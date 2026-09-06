# Consume and update Quadrant Kit

The dependency selection lives in root `Cargo.toml` under
`workspace.dependencies.quadrant-kit`; `Cargo.lock` records the resolved source.
The guard's `KIT_URL`/`KIT_REV` and `scripts/kit_source_v1.json` deliberately assert
that reviewed selection. They are validation baselines, not a second update
channel. Read those files for the currently adopted revision instead of editing
a revision copied into this guide.

Only `crates/quadrant-ui/Cargo.toml` inherits Kit, as a build dependency.
`crates/quadrant-ui/build.rs` maps `quadrant_kit::SLINT_LIBRARY_NAME` to the facade
file returned by `slint_library_path()`, compiles `ui/app.slint` with Fluent style
and embeds static resources using EmbedFiles. Product imports use
`from "@quadrant-kit"`. The helper's path is build-time input, never a runtime
resource path. Generated window/global/model types stay in quadrant-ui.

The Agent cannot reach Kit/Slint, and the GUI has no storage/SQLite dependency.
Kit is never a sibling path dependency, copied implementation, patch/replace,
symlink/submodule, local Cargo source replacement or build-time download.
Gallery's own same-repository path dependency is a separate legitimate case.

## Deliberate upgrade

1. Finish a scoped change and its checks in Kit. Review API/defaults, probe,
   assets/licenses, changelog and any compatibility implications. Publish an
   authorized candidate; obtain its real full SHA, retained ref/peeled commit,
   same-SHA CI and independent remote-consumer report.
2. In a clean Tasks integration branch, change the manifest revision to that
   verified SHA. Review `cargo update -p quadrant-kit` and the complete lockfile
   diff. Do not accept unrelated dependency churn without explanation.
3. Adapt Product where required. Explicitly review/update the guard's adopted
   revision and source fingerprint baseline against that published candidate;
   review any Product API baseline change separately. Never copy a new baseline
   just to silence a failure or point the guard at an unpublished local Kit.
4. Run the guard, Python fixtures and the development check matrix; build Agent
   and GUI together. Validate a fresh checkout without sibling access, complete
   native packages and affected business/window behavior. Record exact tested
   SHAs, failures and runtime limits in the migration/change record.
5. Commit Tasks independently. Preserve the adopted Kit reference. A later Kit
   documentation commit does not automatically change Tasks' pinned source.

Keep Slint/MSRV/backend changes in a separate compatibility review. Breaking
pre-1.0 API/behavior changes require the next minor and migration notes; a patch
must not conceal a breaking change. Fixed SHA plus lockfile controls inputs,
without promising byte-identical binaries across different systems.

## Local editor mapping

First run `python scripts/check_ui_boundaries.py`. Its result includes
`kit_manifest`, verified from full, target-filtered
`cargo metadata --locked --format-version 1`. The resolver checks package IDs
and actual build edges, so Cargo dependency aliases do not change ownership.
Resolve `ui/kit.slint` relative to that manifest's directory and confirm it exists.
In private `.vscode/settings.json`/JSONC, map `slint.libraryPaths` → `quadrant-kit`
to that facade file. Preserve existing comments/settings and keep absolute paths
out of Git. Do not map Tasks to the adjacent Kit you are editing.

There is no automatic settings writer in this repository. The existing guard
prints a verified source location; using `cargo metadata --no-deps` would omit
the external package needed here. Fetch explicitly with `cargo fetch --locked`
if the selected package is not available yet. Parent workspace generation is
described in [WORKSPACE.md](WORKSPACE.md).
