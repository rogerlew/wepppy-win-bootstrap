from pathlib import Path
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

    def test_missing_or_replaced_pair_member_is_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('wepp_261027.exe', 'wepp_261027_hill.exe'):
                shutil.copy2(ROOT/'bin'/name, root/name)
            with patch('wepp_executables.BIN', root):
                select_executables(system='Windows', machine='AMD64')
                hill = root/'wepp_261027_hill.exe'
                hill.write_bytes((root/'wepp_261027.exe').read_bytes())
                with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                    select_executables(system='Windows', machine='AMD64')
                hill.unlink()
                with self.assertRaisesRegex(ValueError, 'incomplete'):
                    select_executables(system='Windows', machine='AMD64')

    def test_only_registered_platform_releases_are_accepted(self):
        for name in ('/tmp/custom', './wepp_261027', 'wepp_261026', 'wepp_261027_hill', 'wepp_261027.exe'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                select_executables(name, system='Linux', machine='x86_64')
        with self.assertRaises(ValueError):
            select_executables(system='Linux', machine='aarch64')
        with self.assertRaises(ValueError):
            select_executables('wepp_reveg', system='Linux', machine='x86_64')
        pair = select_executables('wepp_reveg', system='Windows', machine='AMD64')
        self.assertEqual(pair[0], pair[1])

    def test_invalid_selection_does_not_clear_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'wepp'/'output'
            output.mkdir(parents=True)
            sentinel = output/'existing.txt'
            sentinel.write_text('retain me')
            for options in (['--wepp_exec', str(Path(tmp)/'custom')],
                            ['--wepp_hill_exec', 'wepp_261027_hill'],
                            ['--wepp-hill-exec', 'wepp_261027_hill']):
                result = subprocess.run([sys.executable, str(ROOT/'scripts/run_project.py'),
                                         tmp, *options], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(sentinel.read_text(), 'retain me')
