import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from hill_pass import HillPass


class WindowsReleaseTests(unittest.TestCase):
    def test_packaged_pair_and_alias(self):
        metadata = []
        for name in ('wepp_261027.exe', 'wepp_261027_hill.exe', 'wepppy-win-bootstrap.exe'):
            binary = (ROOT / 'bin' / name).read_bytes()
            sidecar = json.loads((ROOT / 'bin' / (name + '.json')).read_text())
            self.assertEqual(hashlib.sha256(binary).hexdigest(), sidecar['sha256'])
            self.assertEqual(sidecar['binary_name'], name)
            self.assertEqual(binary[:2], b'MZ')
            pe = struct.unpack_from('<I', binary, 60)[0]
            self.assertEqual(binary[pe:pe+6], b'PE\0\0\x64\x86')
            metadata.append(sidecar)
        self.assertEqual(len({m['source_commit'] for m in metadata}), 1)
        self.assertEqual({m['release_tag'] for m in metadata}, {'261027'})
        self.assertEqual(metadata[0]['sha256'], metadata[2]['sha256'])

    def test_pass_v3_preserves_legacy_daily_totals(self):
        # Synthetic daily records, including EVENT continuation and SRC3 metadata.
        legacy = ('p1.cli\n1 2020\n10000\n5 1 2 3 4 5\n0 0 0 0\n'
                  'NO EVENT 2020 1 0 0\n'
                  'EVENT      2020 2 60 1 1 .001 10 0 0 0 0 1 2 3 1 0 0 0 0\n'
                  '0 0 0\n')
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp) / 'old.pass'; new = Path(tmp) / 'new.pass'
            old.write_text(legacy)
            new.write_text('WEPP_PASS_COMPONENTS 3\n' + legacy + 'SRC3 2020 2 0\n')
            a, b = HillPass(str(old)), HillPass(str(new))
            self.assertTrue(a.sed_df.equals(b.sed_df))
            self.assertEqual(b.sed_df['Sed Del (kg)'].tolist(), [0, 10])
            self.assertEqual(b.sed_df['Julian'].tolist(), [1, 2])
            new.write_text('WEPP_PASS_COMPONENTS 4\n' + legacy)
            with self.assertRaises(ValueError):
                HillPass(str(new))
