# SPDX-License-Identifier: GPL-3.0-only
"""Exercise the real filesystem and Git roots without moving either repository."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "workspace_bootstrap", Path(__file__).resolve().parents[1] / "bootstrap_workspace.py"
)
BOOTSTRAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOTSTRAP)


class WorkspaceBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "Quadrant"
        self.root.mkdir()
        for role in ("Tasks", "Kit"):
            child = self.root / f"Quadrant-{role}"
            child.mkdir()
            self.git(child, "init", "--quiet")
            (child / "source.txt").write_text(role)
            self.git(child, "add", "source.txt")
            self.git(child, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "fixture")

    def git(self, root, *args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                       stderr=subprocess.PIPE).strip()

    def snapshots(self):
        return [(self.git(child, "rev-parse", "HEAD"), self.git(child, "status", "--porcelain"))
                for child in sorted(self.root.glob("Quadrant-*")) if child.is_dir()]

    def test_default_dry_run_has_no_writes(self):
        before = self.snapshots()
        result = BOOTSTRAP.bootstrap(self.root)
        self.assertEqual(4, len(result))
        self.assertTrue(all(item["action"] == "CREATE" for item in result))
        self.assertFalse((self.root / "docs").exists())
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertEqual(before, self.snapshots())

    def test_apply_creates_only_parent_files(self):
        before = self.snapshots()
        BOOTSTRAP.bootstrap(self.root, apply=True)
        self.assertIn(str(self.root.resolve()), (self.root / "docs/WORKSPACE.md").read_text())
        self.assertNotIn("{{", (self.root / "docs/MIGRATION_STATUS.md").read_text())
        self.assertFalse((self.root / ".git").exists())
        self.assertFalse((self.root / "Cargo.toml").exists())
        self.assertEqual(before, self.snapshots())

    def test_existing_user_notes_are_never_overwritten(self):
        BOOTSTRAP.bootstrap(self.root, apply=True)
        notes = self.root / "docs/MIGRATION_STATUS.md"
        notes.write_bytes(b"private notes\r\n")
        result = BOOTSTRAP.bootstrap(self.root, apply=True)
        self.assertTrue(all(item["action"] == "KEEP" for item in result))
        self.assertEqual(b"private notes\r\n", notes.read_bytes())

    def test_missing_child_fails_before_creating_files(self):
        (self.root / "Quadrant-Kit").rename(self.root / "Kit-elsewhere")
        with self.assertRaisesRegex(ValueError, "missing independent"):
            BOOTSTRAP.bootstrap(self.root, apply=True)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_parent_git_or_cargo_workspace_is_rejected(self):
        for marker in (".git", "Cargo.toml"):
            with self.subTest(marker=marker):
                path = self.root.parent / marker
                path.write_text("external ownership")
                try:
                    with self.assertRaisesRegex(ValueError, "Git/Cargo ancestor"):
                        BOOTSTRAP.bootstrap(self.root, apply=True)
                finally:
                    path.unlink()
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_directory_in_output_path_fails_before_any_write(self):
        (self.root / "docs/WORKSPACE.md").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            BOOTSTRAP.bootstrap(self.root, apply=True)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_file_in_output_parent_fails_before_any_write(self):
        (self.root / "docs").write_text("keep me")
        with self.assertRaisesRegex(ValueError, "not a directory"):
            BOOTSTRAP.bootstrap(self.root, apply=True)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_linked_output_is_rejected(self):
        target = self.root.parent / "private.txt"
        target.write_text("private")
        try:
            (self.root / "AGENTS.md").symlink_to(target)
        except OSError as error:
            self.skipTest(f"host cannot create symbolic links: {error}")
        with self.assertRaisesRegex(ValueError, "linked coordination path"):
            BOOTSTRAP.bootstrap(self.root, apply=True)
        self.assertEqual("private", target.read_text())

    def test_ancestor_alias_uses_verified_canonical_directory(self):
        alias = self.root.parent / "alias"
        try:
            alias.symlink_to(self.root.parent, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"host cannot create symbolic links: {error}")
        result = BOOTSTRAP.bootstrap(alias / "Quadrant")
        self.assertTrue(all(Path(item["path"]).is_relative_to(self.root.resolve())
                            for item in result))
        self.assertFalse((self.root / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
