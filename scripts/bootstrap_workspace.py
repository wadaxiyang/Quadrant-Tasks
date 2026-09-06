# SPDX-License-Identifier: GPL-3.0-only
"""Preview/create local coordination files after both repositories are relocated.

Never moves repositories, initializes Git, commits, or overwrites existing files.
"""
import argparse
import json
from pathlib import Path
import subprocess


TEMPLATES = Path(__file__).with_name("workspace_templates")
FILES = {
    "AGENTS.md": "AGENTS.template.md",
    "docs/WORKSPACE.md": "WORKSPACE.template.md",
    "docs/MIGRATION_STATUS.md": "MIGRATION_STATUS.template.md",
}


def reject_links(path, *, ancestors=True):
    for item in ((path, *path.parents) if ancestors else (path,)):
        if item.is_symlink() or (hasattr(item, "is_junction") and item.is_junction()):
            raise ValueError(f"linked coordination path is not supported: {item}")


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def prepare(workspace):
    workspace = Path(workspace).absolute()
    # Canonicalize platform ancestor aliases (/var on macOS, short Windows names)
    # before checking ownership; the chosen root itself must not be a link.
    reject_links(workspace, ancestors=False)
    workspace = workspace.resolve(strict=True)
    for ancestor in (workspace, *workspace.parents):
        if (ancestor / ".git").exists() or (ancestor / "Cargo.toml").exists():
            raise ValueError(f"coordination directory has a Git/Cargo ancestor: {ancestor}")
    facts = {"WORKSPACE_ROOT": str(workspace)}
    for role in ("Tasks", "Kit"):
        child = workspace / f"Quadrant-{role}"
        reject_links(child)
        if not child.is_dir() or not (child / ".git").exists():
            raise ValueError(f"missing independent repository: {child}")
        if Path(git(child, "rev-parse", "--show-toplevel")).resolve() != child.resolve():
            raise ValueError(f"not a repository root: {child}")
        facts[f"{role.upper()}_HEAD"] = git(child, "rev-parse", "HEAD")
        facts[f"{role.upper()}_BRANCH"] = git(child, "branch", "--show-current") or "(detached)"
    planned = []
    for relative, template in FILES.items():
        content = (TEMPLATES / template).read_text(encoding="utf-8")
        for key, value in facts.items():
            content = content.replace("{{" + key + "}}", value)
        planned.append((workspace / relative, content))
    planned.append((workspace / "Quadrant.code-workspace", json.dumps({
        "folders": [{"path": "Quadrant-Tasks"}, {"path": "Quadrant-Kit"}],
    }, indent=2) + "\n"))
    # Preflight all outputs before writing any of them. Existing local notes are
    # intentionally preserved even when repository HEADs have subsequently changed.
    for destination, _ in planned:
        reject_links(destination)
        if destination.exists() and not destination.is_file():
            raise ValueError(f"output is not a regular file: {destination}")
        for ancestor in destination.parents:
            if ancestor == workspace:
                break
            if ancestor.exists() and not ancestor.is_dir():
                raise ValueError(f"output parent is not a directory: {ancestor}")
    return planned


def bootstrap(workspace, apply=False):
    result = []
    for destination, content in prepare(workspace):
        action = "KEEP" if destination.exists() else "CREATE"
        if apply and action == "CREATE":
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation also preserves a file created after preflight.
            with destination.open("x", encoding="utf-8", newline="\n") as output:
                output.write(content)
        result.append({"action": action, "path": str(destination)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--apply", action="store_true", help="create missing files only")
    args = parser.parse_args()
    try:
        print(json.dumps({"mode": "apply" if args.apply else "dry-run",
                          "files": bootstrap(args.workspace_root, args.apply)}, indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Workspace bootstrap refused: {error}\n")


if __name__ == "__main__":
    main()
