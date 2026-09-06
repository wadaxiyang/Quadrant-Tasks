# Two-repository workspace

The local parent `Quadrant/` contains the independent `Quadrant-Tasks/` and
`Quadrant-Kit/` repositories. It has no Git repository or Cargo workspace of its
own. Tasks is the original application's continued repository, including history,
tags and remotes; relocating it does not rename the shipped product or data paths.

Open Kit for reusable Slint controls and Gallery, Tasks for product and Agent work.
Tasks always consumes the reviewed remote Kit revision through Cargo, never its
sibling checkout. Each repository remains independently buildable.

After moving both complete repositories safely, run from Tasks:

```console
python scripts/bootstrap_workspace.py
python scripts/bootstrap_workspace.py --apply
```

The first command is a dry-run. The second creates only missing parent AGENTS,
workspace/status notes and a relative-path VS Code multi-root workspace file.
Existing files are retained. Invalid Git roots, linked output paths and ancestor
Git/Cargo workspaces are rejected. It never moves repositories, initializes Git,
overwrites user settings or commits. Templates have `.template.md` names so they
are not active nested instructions. Parent files are local coordination; this
document and the child repositories hold versioned contracts.

Before relocating an ordinary checkout, commit the intended checkpoint and
record HEAD, branch, remotes, refs, complete history and status. Check destination
conflicts, free space and open processes. Run moves from outside both repositories,
retaining the entire `.git` directory and ignored local files. A linked worktree
requires Git worktree operations instead. If an active session holds the old
path, record `LAYOUT_PENDING` and exact recovery instructions; do not force it.

After relocation, compare the Git snapshot, run the boundary guards and build
Tasks' Agent/GUI and Kit's Gallery from their respective new roots. Keep any open
native acceptance items in the migration ledger; moving folders does not waive them.

Machine-specific editor settings stay private. The generated workspace uses
relative child paths. Any Tasks Slint library mapping must point to the package
resolved by `cargo metadata --locked --format-version 1`, not to sibling Kit.
