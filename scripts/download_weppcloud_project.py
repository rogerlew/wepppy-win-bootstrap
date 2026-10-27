import sys
from http.client import HTTPException
import zipfile
import argparse
import os
from os.path import exists, expanduser
from os.path import join as _join
from urllib.error import URLError
from download_http import DownloadError, open_download

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', type=str,
                        help='run_id of weppcloud project')
    parser.add_argument('destination', type=str,
                        help='directory to download to')
    parser.add_argument('-n', '--no_extract',
                        help='do not extract', action='store_true', default=False)
    parser.add_argument('-r', '--remove',
                        help='remove zipfile after extracting', action='store_true', default=False)
    args = parser.parse_args()

    wd = args.run_id
    destination = args.destination
    assert exists(destination)

    no_extract = args.no_extract
    remove = args.remove

    url_template = 'https://wepp.cloud/weppcloud/runs/{wd}/0/archive/'

    # Read JWT token from ~/.weppcloud_jwt if it exists
    jwt_path = expanduser('~/.weppcloud_jwt')
    jwt_token = ''
    if exists(jwt_path):
        with open(jwt_path) as f:
            jwt_token = f.read().strip()
        if jwt_token:
            print('using JWT authentication')

    fname = _join(destination, "{wd}.zip".format(wd=wd))
    print("attempting to download", wd)

    url = url_template.format(wd=wd)
    try:
        with open_download(url, jwt_token) as response:
            data = response.read()
    except DownloadError as error:
        print(f'Download failed: {error}', file=sys.stderr)
        sys.exit(1)
    except (OSError, URLError, HTTPException) as error:
        print(f'Download failed: {type(error).__name__}. Check connectivity and local file access.', file=sys.stderr)
        sys.exit(1)
    print('download complete')

    print('saving archive')
    if exists(fname):
        os.remove(fname)

    # Write data to file
    file_ = open(fname, 'wb')
    file_.write(data)
    file_.close()

    if not no_extract:
        print('extracting archive')
        zip_ref = zipfile.ZipFile(fname, 'r')
        zip_ref.extractall(_join(destination, wd))
        zip_ref.close()

    if remove:
        os.remove(fname)
