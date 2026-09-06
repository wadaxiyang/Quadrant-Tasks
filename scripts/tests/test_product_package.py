# SPDX-License-Identifier: GPL-3.0-only
"""Distribution regressions: reject incomplete or altered release archives."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

MODULE = Path(__file__).resolve().parents[1] / "verify_product_package.py"
SPEC = importlib.util.spec_from_file_location("product_package", MODULE)
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class ProductPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive = self.root / "product.zip"
        self.files = {"quadrant.exe": b"MZgui", "quadrant-agent.exe": b"MZagent"}
        for name, source in {
            "LICENSE": "LICENSE", "LICENSE-Fluent-Icons.txt": "assets/icons/LICENSE-MIT",
            "THIRD-PARTY-NOTICES.txt": "packaging/THIRD-PARTY-NOTICES.txt",
            "DEPENDENCY-LICENSES.txt": "packaging/DEPENDENCY-LICENSES.txt",
        }.items():
            data = (name + " original bytes\n").encode()
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            self.files[name] = data

    def write_archive(self):
        with zipfile.ZipFile(self.archive, "w") as handle:
            for name, data in self.files.items():
                handle.writestr(name, data)
        Path(str(self.archive) + ".sha256").write_text(hashlib.sha256(self.archive.read_bytes()).hexdigest())

    def verify(self):
        return PACKAGE.verify(self.archive, "windows", self.root)

    def test_complete_pair_and_original_notices(self):
        self.write_archive()
        self.assertEqual(len(self.verify()["files"]), 6)

    def test_missing_agent(self):
        del self.files["quadrant-agent.exe"]
        self.write_archive()
        with self.assertRaises(KeyError):
            self.verify()

    def test_wrong_native_format(self):
        self.files["quadrant-agent.exe"] = b"\x7fELF"
        self.write_archive()
        with self.assertRaisesRegex(ValueError, "format"):
            self.verify()

    def test_modified_mit_notice(self):
        self.files["LICENSE-Fluent-Icons.txt"] = b"replaced license"
        self.write_archive()
        with self.assertRaisesRegex(ValueError, "license"):
            self.verify()

    def test_checksum_mismatch(self):
        self.write_archive()
        Path(str(self.archive) + ".sha256").write_text("0" * 64)
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.verify()

    def test_source_or_profile_leak(self):
        for filename in ("ui/kit/base.slint", "quadrant-rust.db", ".git/config"):
            with self.subTest(filename=filename):
                self.files[filename] = b"unexpected"
                self.write_archive()
                with self.assertRaisesRegex(ValueError, "leaked"):
                    self.verify()
                del self.files[filename]

    def test_unsafe_archive_path(self):
        self.files["../outside"] = b"unsafe"
        self.write_archive()
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
