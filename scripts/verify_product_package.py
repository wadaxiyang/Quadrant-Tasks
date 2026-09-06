# SPDX-License-Identifier: GPL-3.0-only
"""Verify the actual native archive, executable pair and original license bytes.

This is distribution-closure evidence, not a substitute for native GUI execution.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import tarfile
import zipfile


def archive_files(archive):
    """Read regular files only; fail closed on unsafe names and special entries."""
    files = {}
    def add(name, data):
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
            raise ValueError(f"unsafe archive path: {name}")
        key = path.as_posix()
        if key in files:
            raise ValueError(f"duplicate archive file: {name}")
        files[key] = data
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as handle:
            for item in handle.infolist():
                if (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("archive symlinks are not supported")
                if not item.is_dir():
                    add(item.filename, handle.read(item))
    else:
        with tarfile.open(archive, "r:gz") as handle:
            for item in handle.getmembers():
                if item.isdir():
                    continue
                if not item.isfile():
                    raise ValueError(f"non-regular archive member: {item.name}")
                add(item.name, handle.extractfile(item).read())
                if "/bin/" in item.name or "/MacOS/" in item.name:
                    if not item.mode & 0o111:
                        raise ValueError(f"executable permission missing: {item.name}")
    return files


def verify(archive, target, repository):
    files = archive_files(archive)
    if target == "windows":
        base, binaries, licenses = "", ("quadrant.exe", "quadrant-agent.exe"), ""
        magic = (b"MZ",)
    else:
        roots = {name.split("/")[0] for name in files}
        if len(roots) != 1:
            raise ValueError("archive must contain one product root")
        base = next(iter(roots)) + "/"
        if target == "linux":
            binaries, licenses = ("bin/quadrant", "bin/quadrant-agent"), "share/licenses/quadrant/"
            magic = (b"\x7fELF",)
            assert base + "share/applications/quadrant.desktop" in files
            for size in (16, 20, 24, 32, 40, 48, 64, 128, 256, 512):
                assert base + f"share/icons/hicolor/{size}x{size}/apps/quadrant.png" in files
        else:
            assert base == "Quadrant.app/"
            binaries = ("Contents/MacOS/quadrant", "Contents/MacOS/quadrant-agent")
            licenses = "Contents/Resources/"
            magic = (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe")
            assert base + "Contents/Info.plist" in files
            assert base + "Contents/Resources/Quadrant.icns" in files
    for binary in binaries:
        if not files[base + binary].startswith(magic):
            raise ValueError(f"wrong native executable format: {binary}")
    for filename, source in {
        "LICENSE": "LICENSE",
        "LICENSE-Fluent-Icons.txt": "assets/icons/LICENSE-MIT",
        "THIRD-PARTY-NOTICES.txt": "packaging/THIRD-PARTY-NOTICES.txt",
        "DEPENDENCY-LICENSES.txt": "packaging/DEPENDENCY-LICENSES.txt",
    }.items():
        if files[base + licenses + filename] != (repository / source).read_bytes():
            raise ValueError(f"missing or altered license: {filename}")
    forbidden = (".slint", ".rs", ".db", ".db-wal", ".db-shm")
    if any(name.endswith(forbidden) or ".git/" in name for name in files):
        raise ValueError("source or profile data leaked into native archive")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sidecar = Path(str(archive) + ".sha256").read_text(encoding="utf-8-sig").split()[0]
    if sidecar.lower() != digest:
        raise ValueError("archive checksum sidecar does not match")
    return {"platform": target, "archive": archive.name, "sha256": digest,
            "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
            "native_execution": "Separate native runtime evidence required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--platform", required=True, choices=("windows", "linux", "macos"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    report = verify(args.archive, args.platform, repository)
    report.update(source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository, text=True).strip(),
                  host=platform.platform(), toolchain=subprocess.check_output(["rustc", "-Vv"], text=True).strip())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {args.platform} archive, both native executables and original licenses ({len(report['files'])} files)")


if __name__ == "__main__":
    main()
