# Quadrant-Tasks

This is the original Quadrant application's continued Git repository. A directory
rename does not rename its binaries, database, profiles, IPC or application identity.

- Agent owns persistent state, SQLite and resident services. The GUI is disposable;
  quadrant-ui owns the Slint adapter. Preserve all three window lifecycle contracts.
- Product branding, Q1-Q4 semantics, Inbox, TaskRowShell, ProductIcons and business
  views belong here. Generic controls and Gallery belong in Quadrant-Kit.
- Import the Kit public facade through `@quadrant-kit`. Its only production edge
  is quadrant-ui's build dependency on the reviewed public Git URL and full SHA.
- No sibling path dependency, patch/replace, copied Kit source, submodule, symlink
  or unpublished override. Normal intra-repository crate paths remain allowed.
- Keep Cargo.lock reviewed; do not refresh API baselines merely to silence guards.
- Build/package Agent and GUI together. Test with isolated data, never destructive
  operations against a user's real profile. Preserve source attribution and licenses.
- Keep one writer per checkout. Preserve user changes and published history.
- Parent coordination is optional. See docs/WORKSPACE.md for the two-repository
  workflow, docs/ARCHITECTURE.md for process ownership, docs/UI_ARCHITECTURE.md
  for Product contracts, docs/KIT_INTEGRATION.md for upgrades and editor mapping,
  and docs/DEVELOPMENT.md for native development and packaging.

Relevant checks, scaled to the change:

```console
python -m unittest discover -s scripts/tests -v
python scripts/check_ui_boundaries.py
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --locked
cargo build --locked -p quadrant-agent -p quadrant-app
```

Use the native packaging entry point under `packaging/<platform>/` and validate
its archive with `scripts/verify_product_package.py`. Record native execution
separately from compilation and synthetic screenshots. Explicitly report any
unrun checks and retain open migration gates in docs/migrations/kit-extraction-v2.md.
