"""Fetch a verified manifest, then run aria2c without hiding HTTP failures."""
import argparse
from http.client import HTTPException
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.error import URLError
from urllib.parse import quote, urlsplit

from download_http import DownloadError, open_download

BASE_URL = 'https://wepp.cloud'


def manifest_urls(text):
    urls = []
    for line in text.splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        if line[0].isspace():
            if not urls:
                raise DownloadError('Server did not return a valid aria2c manifest; download stopped.')
            continue
        # aria2c's saved session ends URI lines with a TAB delimiter.
        parts = [url for url in line.split('\t') if url]
        if any(urlsplit(url).scheme not in ('http', 'https') for url in parts):
            raise DownloadError('Server did not return a valid aria2c manifest; download stopped.')
        urls.extend(parts)
    return urls


def download(run_id, destination, *, base_url=BASE_URL, executable=None):
    token_path = Path.home() / '.weppcloud_jwt'
    token = token_path.read_text().strip() if token_path.exists() else ''
    print('using JWT authentication' if token else 'downloading without authentication')
    url = f'{base_url}/weppcloud/runs/{quote(run_id, safe="")}/cfg/aria2c.spec'
    with open_download(url, token) as response:
        manifest = response.read().decode('utf-8')
    urls = manifest_urls(manifest)
    # Preserve the established inspectable inventory artifact. aria2c consumes
    # only this request's private copy below, never a stale inventory on disk.
    Path(f'{run_id}_aria2c.spec').write_text(manifest, encoding='utf-8')
    # aria2c percent-encodes spaces and Unicode when writing failed sessions.
    normalized_urls = {quote(u, safe=":/?#[]@!$&'()*+,;=%") for u in urls}
    if not urls:
        print('The server returned an empty project manifest (HTTP 200); no files to download.')
        return 0
    if executable is None:
        executable = str(Path(__file__).with_name('aria2c.exe')) if os.name == 'nt' else 'aria2c'
    # A failed request cannot overwrite or accidentally reuse an earlier manifest.
    with tempfile.TemporaryDirectory(prefix='wepp-download-') as scratch:
        spec = Path(scratch) / 'manifest.spec'
        failed = Path(scratch) / 'failed.spec'
        spec.write_text(manifest, encoding='utf-8')
        args = [executable, '-j', '10', '--allow-overwrite=true', '-d', destination,
                '--input-file=' + str(spec), '--save-session=' + str(failed)]
        if token:
            args.append('--header=Authorization: Bearer ' + token)
        result = subprocess.run(args, check=False)
        if result.returncode:
            print(f'File transfer failed (aria2c exit {result.returncode}).', file=sys.stderr)
            # aria2c does not print HTTP bodies. Recheck failed URLs with a bounded
            # range request to surface the server explanation; never retry whole files.
            if failed.exists():
                failed_urls = manifest_urls(failed.read_text(encoding='utf-8'))
                for failed_url in failed_urls[:10]:
                    if quote(failed_url, safe=":/?#[]@!$&'()*+,;=%") not in normalized_urls:
                        continue
                    try:
                        with open_download(failed_url, token, headers={'Range': 'bytes=0-0'}, timeout=10):
                            print('A failed file now responds; original transfer still failed.', file=sys.stderr)
                    except DownloadError as error:
                        print(str(error), file=sys.stderr)
                    except (OSError, URLError, HTTPException) as error:
                        print(f'Failed-file diagnostic request could not complete: {error.reason if isinstance(error, URLError) else type(error).__name__}', file=sys.stderr)
                if len(failed_urls) > 10:
                    print('Additional failed-file diagnostics omitted (limit 10).', file=sys.stderr)
            return result.returncode if result.returncode > 0 else 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id')
    parser.add_argument('destination')
    args = parser.parse_args()
    try:
        return download(args.run_id, args.destination)
    except DownloadError as error:
        print(f'Download failed: {error}', file=sys.stderr)
    except (OSError, URLError, UnicodeError, HTTPException) as error:
        print(f'Download failed: {error.reason if isinstance(error, URLError) else type(error).__name__}. Check connectivity and local file access.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
