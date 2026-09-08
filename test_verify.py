import shutil
import tempfile
import unittest
from pathlib import Path
import verify


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'catalog'
        shutil.copytree(Path(__file__).parent, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def test_original_bytes(self):
        verify.verify(self.root, ['b3sum'])

    def test_same_size_corruption(self):
        path = self.root / 'intel/ivpu/vpu_40xx_v1.bin'
        data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            verify.verify(self.root, ['b3sum'])

    def test_missing_license(self):
        (self.root / 'LICENSES/intel-xe.txt').unlink()
        with self.assertRaisesRegex(ValueError, 'missing catalog file'):
            verify.verify(self.root, ['b3sum'])

    def test_modified_license(self):
        (self.root / 'LICENSES/intel-xe.txt').write_text('not the upstream notice')
        with self.assertRaisesRegex(ValueError, 'license digest mismatch'):
            verify.verify(self.root, ['b3sum'])

    def test_path_escape(self):
        path = self.root / 'manifest.toml'
        path.write_text(path.read_text().replace('intel/ivpu/vpu_40xx_v1.bin', '../outside.bin'))
        with self.assertRaisesRegex(ValueError, 'path escapes catalog'):
            verify.verify(self.root, ['b3sum'])


if __name__ == '__main__':
    unittest.main()
