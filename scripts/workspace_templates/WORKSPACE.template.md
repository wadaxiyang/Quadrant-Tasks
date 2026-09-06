# Local Quadrant workspace

Location: `{{WORKSPACE_ROOT}}`

| Work | Open | Versioned instructions |
|---|---|---|
| Reusable UI and Gallery | `Quadrant-Kit` | `AGENTS.md`, `docs/CONSUMER_GUIDE.md`, `docs/GALLERY.md` |
| Product and Agent | `Quadrant-Tasks` | `AGENTS.md`, `docs/WORKSPACE.md`, `docs/UI_ARCHITECTURE.md` |

Open the relevant child for ordinary work, or `Quadrant.code-workspace` for
coordination. Each child owns its own Git history and Cargo workspace. This
parent must not acquire `.git` or `Cargo.toml`.

Tasks consumes the pinned remote Git package, regardless of what is edited in
the local Kit checkout. Publish and verify a Kit candidate before deliberately
updating Tasks' revision and lockfile. LSP mappings must also use the resolved
Cargo package, not the sibling checkout.

Regenerate missing parent files by running `python scripts/bootstrap_workspace.py`
from Tasks, reviewing its dry-run, then adding `--apply`. Existing local files
are kept. The script does not move repositories, initialize Git or commit.

Current local progress belongs in `docs/MIGRATION_STATUS.md`; reviewed migration
evidence belongs in Tasks' `docs/migrations/kit-extraction-v2.md`.
