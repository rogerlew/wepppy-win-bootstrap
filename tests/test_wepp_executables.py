from pathlib import Path
import os
from unittest.mock import patch
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from wepp_executables import select_executables


class ExecutableSelectionTests(unittest.TestCase):
    def test_platform_defaults_and_provenance(self):
        sources = set()
        for system, suffix in [('Windows', '.exe'), ('Linux', '')]:
            pair = select_executables(system=system, machine='AMD64')
            self.assertEqual([Path(p).name for p in pair],
                             ['wepp_261027'+suffix, 'wepp_261027_hill'+suffix])
            for filename in pair:
                binary = Path(filename).read_bytes()
                metadata = json.loads(Path(filename+'.json').read_text())
                self.assertEqual(hashlib.sha256(binary).hexdigest(), metadata['sha256'])
                self.assertTrue(binary.startswith(b'MZ' if suffix else b'\x7fELF'))
                sources.add(metadata['source_commit'])
        self.assertEqual(len(sources), 1)

    def test_custom_pair_and_single_executable(self):
        with tempfile.TemporaryDirectory(prefix='wepp selection ') as tmp:
            paths = [Path(tmp)/n for n in ('custom', 'hill')]
            for p in paths:
                p.write_bytes(b'fixture'); p.chmod(0o755)
            self.assertEqual(select_executables(str(paths[0]), system='Linux'),
                             (str(paths[0]), str(paths[0])))
            self.assertEqual(select_executables(*map(str, paths), system='Linux'),
                             tuple(map(str, paths)))
            with patch('wepp_executables.BIN', Path(tmp)/'nonexistent-bin'):
                previous = os.getcwd()
                try:
                    os.chdir(tmp)
                    self.assertEqual(select_executables('./custom', system='Linux'),
                                     (str(paths[0]), str(paths[0])))
                finally:
                    os.chdir(previous)
            with self.assertRaises(ValueError):
                select_executables(str(paths[0]), str(Path(tmp)/'missing'), system='Linux')

    def test_unsupported_default_and_missing_release(self):
        with self.assertRaises(ValueError):
            select_executables(system='Linux', machine='aarch64')
        with self.assertRaises(ValueError):
            select_executables('wepp_261026', system='Windows', machine='AMD64')

    def test_missing_selection_does_not_clear_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'wepp'/'output'
            output.mkdir(parents=True)
            sentinel = output/'existing.txt'
            sentinel.write_text('retain me')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/run_project.py'),
                                     tmp, '--wepp_exec', str(Path(tmp)/'missing')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('WEPP executable not found', result.stderr)
            self.assertEqual(sentinel.read_text(), 'retain me')
