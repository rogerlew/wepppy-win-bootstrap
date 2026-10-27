import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import subprocess
import shutil
import os
import sys
import tempfile
import threading
import unittest
import zipfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from download_http import DownloadError, open_download, describe_http_error
from urllib.error import HTTPError
from download_with_aria2c import download, manifest_urls


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.mode = 'error'
        self.file_name = 'file.txt'
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as zipped:
            zipped.writestr('data.txt', b'exact-archive-bytes')
        self.archive = archive.getvalue()
        self.requests = []
        self.auth_headers = []
        self.redirect_target = None
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                outer.requests.append(self.path)
                outer.auth_headers.append(self.headers.get('Authorization'))
                if self.path == '/redirect':
                    self.send_response(302)
                    self.send_header('Location', outer.redirect_target)
                    self.end_headers()
                    return
                is_manifest = self.path.endswith('aria2c.spec')
                if outer.mode == 'error' or (outer.mode == 'file_error' and not is_manifest):
                    body = json.dumps({'error': {'message': 'Server configuration error: SECRET_KEY is not configured. Contact operator.',
                                                'code': 'server_configuration_error'},
                                       'request_id': 'fixture-request-id'}).encode()
                    self.send_response(500)
                    self.send_header('X-Request-Id', 'fixture-request-id')
                elif outer.mode == 'archive':
                    body = outer.archive
                    self.send_response(200)
                elif outer.mode == 'truncated':
                    self.send_response(200)
                    self.send_header('Content-Length', '1000')
                    self.end_headers()
                    self.wfile.write(b'partial')
                    self.close_connection = True
                    return
                elif outer.mode == 'html':
                    body = b'<html>Login</html>'
                    self.send_response(200)
                elif outer.mode == 'plain':
                    body = b'upstream unavailable'
                    self.send_response(502)
                elif outer.mode == 'large':
                    body = b'x' * 10000
                    self.send_response(503)
                elif is_manifest:
                    body = (outer.base + '/' + outer.file_name + '\n  out=' + outer.file_name + '\n').encode()
                    self.send_response(200)
                else:
                    body = b'exact-success-bytes'
                    self.send_response(200)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.temp = tempfile.TemporaryDirectory()
        self.original_cwd = Path.cwd()
        os.chdir(self.temp.name)
        self.child_env = dict(os.environ, HOME=self.temp.name, USERPROFILE=self.temp.name)
        self.home = patch('pathlib.Path.home', return_value=Path(self.temp.name))
        self.home.start()

    def tearDown(self):
        self.home.stop()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        os.chdir(self.original_cwd)
        self.temp.cleanup()

    def test_manifest_error_stops_before_aria_and_preserves_diagnostic(self):
        inventory = Path('project_aria2c.spec')
        inventory.write_text('previous inventory')
        with patch('download_with_aria2c.subprocess.run') as aria:
            with self.assertRaises(DownloadError) as failure:
                download('project', self.temp.name, base_url=self.base)
            aria.assert_not_called()
        self.assertEqual(inventory.read_text(), 'previous inventory')
        self.assertIn('SECRET_KEY', str(failure.exception))
        self.assertIn('fixture-request-id', str(failure.exception))
        self.assertIn('HTTP 500', str(failure.exception))

    def test_false_success_html_manifest_rejected(self):
        self.mode = 'html'
        with patch('download_with_aria2c.subprocess.run') as aria:
            with self.assertRaises(DownloadError):
                download('project', self.temp.name, base_url=self.base)
            aria.assert_not_called()

    def test_successful_bytes_and_aria_exit(self):
        self.mode = 'success'
        with open_download(self.base + '/file.txt') as response:
            self.assertEqual(response.read(), b'exact-success-bytes')
        def aria(args, **kwargs):
            spec = next(a.split('=', 1)[1] for a in args if a.startswith('--input-file='))
            self.assertIn(self.base + '/file.txt', Path(spec).read_text())
            self.assertIn(self.temp.name, args)
            return subprocess.CompletedProcess(args, 0)
        with patch('download_with_aria2c.subprocess.run', side_effect=aria):
            self.assertEqual(download('project', self.temp.name, base_url=self.base), 0)
        self.assertIn(self.base + '/file.txt', Path('project_aria2c.spec').read_text())

    def test_failed_file_body_reported_and_nonzero(self):
        self.mode = 'file_error'
        def aria(args, **kwargs):
            failed = next(a.split('=', 1)[1] for a in args if a.startswith('--save-session='))
            Path(failed).write_text(self.base + '/file.txt\t\n')
            return subprocess.CompletedProcess(args, 22)
        output = io.StringIO()
        with patch('download_with_aria2c.subprocess.run', side_effect=aria), contextlib.redirect_stderr(output):
            self.assertEqual(download('project', self.temp.name, base_url=self.base), 22)
        self.assertIn('SECRET_KEY', output.getvalue())
        self.assertIn('fixture-request-id', output.getvalue())

    def test_indented_error_and_orphan_option_rejected(self):
        for text in ['  <html>Login</html>\n', '  {"error": "failed"}\n', ' out=orphan.txt\n']:
            with self.assertRaises(DownloadError):
                manifest_urls(text)
        self.assertEqual(manifest_urls('\n# Empty project\n'), [])

    def test_legacy_archive_reports_http_and_truncated_errors_without_writing(self):
        scripts = Path(__file__).resolve().parents[1] / 'scripts'
        for mode in ['error', 'truncated']:
            self.mode = mode
            code = ('import sys,runpy; sys.path.insert(0,sys.argv.pop(1)); '
                    'import download_http as h; original=h.open_download; '
                    f'h.open_download=lambda u,t: original({self.base!r}+"/archive",t); '
                    f'runpy.run_path({str(scripts / "download_weppcloud_project.py")!r},run_name="__main__")')
            result = subprocess.run([sys.executable, '-c', code, str(scripts), 'project', self.temp.name],
                                    capture_output=True, text=True, env=self.child_env)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse((Path(self.temp.name) / 'project.zip').exists())
            if mode == 'error':
                self.assertIn('fixture-request-id', result.stderr)
                self.assertIn('SECRET_KEY', result.stderr)
            else:
                self.assertIn('IncompleteRead', result.stderr)

    def test_error_redaction_happens_after_control_sanitization(self):
        token = 'synthetic-private-token'
        body = b'{"error":{"message":"synthetic-\\u001bprivate-token"}}'
        error = HTTPError('http://localhost/file', 500, 'Failure', {}, io.BytesIO(body))
        text = describe_http_error(error, token)
        self.assertNotIn(token, text)
        self.assertIn('[redacted]', text)

    def test_real_aria_success_and_file_error(self):
        bundled = Path(__file__).resolve().parents[1] / 'scripts' / 'aria2c.exe'
        executable = str(bundled) if os.name == 'nt' and bundled.exists() else shutil.which('aria2c')
        if not executable:
            self.skipTest('aria2c not installed')
        for name in ['file.txt', 'file name.txt', 'fílè.txt']:
            self.file_name = name
            self.mode = 'success'
            self.assertEqual(download('project', self.temp.name, base_url=self.base, executable=executable), 0)
            self.assertEqual((Path(self.temp.name) / name).read_bytes(), b'exact-success-bytes')
            (Path(self.temp.name) / name).unlink()
            self.mode = 'file_error'
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = download('project', self.temp.name, base_url=self.base, executable=executable)
            self.assertNotEqual(result, 0)
            self.assertIn('fixture-request-id', output.getvalue())
            self.assertIn('SECRET_KEY', output.getvalue())

    @unittest.skipUnless(os.name == 'nt', 'native Windows wrapper')
    def test_windows_batch_exit_propagation(self):
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'wget_download_weppcloud_project_noprep.bat'
        env = dict(os.environ)
        env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
        result = subprocess.run(['cmd', '/c', str(script)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('destination', result.stderr)

    @unittest.skipUnless(os.name == 'nt', 'native Windows wrapper')
    def test_windows_batch_http_failure_and_success(self):
        scripts = Path(__file__).resolve().parents[1] / 'scripts'
        # Redirect only the fixed service origin to a disposable HTTP fixture;
        # run the unchanged .bat, Python client and bundled transfer executable.
        redirect = Path(self.temp.name) / 'sitecustomize.py'
        redirect.write_text(
            'import urllib.request\n'
            'original = urllib.request.OpenerDirector.open\n'
            'def local_open(self, request, *args, **kwargs):\n'
            '    if isinstance(request, urllib.request.Request) and request.full_url.startswith("https://wepp.cloud/"):\n'
            f'        request.full_url = {self.base!r} + request.full_url[len("https://wepp.cloud"):]\n'
            '    return original(self, request, *args, **kwargs)\n'
            'urllib.request.OpenerDirector.open = local_open\n')
        env = dict(os.environ)
        env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
        env['PYTHONPATH'] = self.temp.name
        env['USERPROFILE'] = self.temp.name
        env['HOME'] = self.temp.name
        destination = Path(self.temp.name) / 'destination with spaces'
        for mode, expected in [('error', 1), ('file_error', 22), ('success', 0)]:
            self.mode = mode
            result = subprocess.run(['cmd', '/c', str(scripts / 'wget_download_weppcloud_project_noprep.bat'),
                                     'project', str(destination)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            if mode != 'success':
                self.assertIn('fixture-request-id', result.stderr)
                self.assertIn('SECRET_KEY', result.stderr)
            else:
                self.assertEqual((destination / 'file.txt').read_bytes(), b'exact-success-bytes')

    def test_legacy_archive_success_preserves_archive_and_extracts_bytes(self):
        self.mode = 'archive'
        scripts = Path(__file__).resolve().parents[1] / 'scripts'
        code = ('import sys,runpy; sys.path.insert(0,sys.argv.pop(1)); '
                'import download_http as h; original=h.open_download; '
                f'h.open_download=lambda u,t: original({self.base!r}+"/archive",t); '
                f'runpy.run_path({str(scripts / "download_weppcloud_project.py")!r},run_name="__main__")')
        result = subprocess.run([sys.executable, '-c', code, str(scripts), 'project', self.temp.name],
                                capture_output=True, text=True, env=self.child_env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((Path(self.temp.name) / 'project.zip').read_bytes(), self.archive)
        self.assertEqual((Path(self.temp.name) / 'project' / 'data.txt').read_bytes(), b'exact-archive-bytes')

    def test_redirect_auth_scope_and_successful_bytes(self):
        self.mode = 'success'
        other = ThreadingHTTPServer(('127.0.0.1', 0), self.server.RequestHandlerClass)
        thread = threading.Thread(target=other.serve_forever, daemon=True)
        thread.start()
        try:
            for target, expected in [(self.base, 'Bearer synthetic-token'),
                                     (f'http://127.0.0.1:{other.server_port}', None)]:
                self.redirect_target = target + '/file.txt'
                self.auth_headers.clear()
                with open_download(self.base + '/redirect', 'synthetic-token') as response:
                    self.assertEqual(response.read(), b'exact-success-bytes')
                self.assertEqual(self.auth_headers, ['Bearer synthetic-token', expected])
        finally:
            other.shutdown()
            other.server_close()
            thread.join()

    def test_plain_and_large_errors(self):
        for mode, expected in [('plain', 'upstream unavailable'), ('large', 'truncated')]:
            self.mode = mode
            with self.assertRaises(DownloadError) as failure:
                open_download(self.base + '/file')
            self.assertIn(expected, str(failure.exception))
            self.assertLess(len(str(failure.exception)), 8500)

    def test_cli_prints_server_message_and_exits_nonzero(self):
        scripts = str(Path(__file__).resolve().parents[1] / 'scripts')
        code = ('import sys; sys.path.insert(0, sys.argv.pop(1)); '
                'import download_with_aria2c as d; original=d.download; '
                f'd.download=lambda r,p: original(r,p,base_url={self.base!r}); '
                'sys.exit(d.main())')
        result = subprocess.run([sys.executable, '-c', code, scripts, 'project', self.temp.name],
                                capture_output=True, text=True, env=self.child_env)
        self.assertEqual(result.returncode, 1)
        self.assertIn('SECRET_KEY', result.stderr)
        self.assertIn('fixture-request-id', result.stderr)


if __name__ == '__main__':
    unittest.main()
