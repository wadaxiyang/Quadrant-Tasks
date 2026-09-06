# Develop and validate Tasks

Open this repository itself. No parent coordination file or sibling Kit checkout
is needed. Cargo fetches the reviewed public Kit package automatically; use an
ordinary trusted Cargo/Git environment without source overrides.

The development toolchain is pinned to Rust 1.94.1 with rustfmt/clippy. The
declared baseline is Rust 1.92, edition 2024, with exact Slint/slint-build 1.17.1.
Python 3.11+ is used for standard-library developer scripts. Windows needs the
MSVC build tools/SDK; macOS needs its native Xcode command-line environment.
On Ubuntu the current CI installs libfontconfig1-dev, libx11-xcb-dev, xinput,
libxcursor-dev, libxkbcommon-x11-dev and libx11-dev. Native display access is
separate from these compilation prerequisites.

## Run

From the Tasks Git root:

```console
cargo build --locked -p quadrant-agent -p quadrant-app
cargo run --locked -p quadrant-app
cargo run --locked -p quadrant-app -- --quick-add
```

The first command creates both companions. Use the second for Main or the third
for standalone capture. The GUI starts its Agent if needed. For destructive or
behavioral testing set `QUADRANT_DATA_DIR` to a fresh, task-owned directory before
starting either executable, and keep that setting consistent for both. Exit the
test Agent using its own tray before changing profiles. Do not point tests at a
real user's data. Normal startup-policy testing can use
`cargo run --locked -p quadrant-agent -- --background`.

## Checks

```console
python -m unittest discover -s scripts/tests -v
python scripts/check_ui_boundaries.py
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --locked
cargo check --workspace --all-targets --locked
cargo build --locked -p quadrant-agent -p quadrant-app
cargo +1.92.0 build --locked -p quadrant-agent -p quadrant-app
```

Install Rust 1.92.0 before the last command. On macOS run tests with a short
temporary root (`TMPDIR=/tmp cargo test --workspace --locked`); long Darwin
temporary paths can exceed Unix socket address capacity. Tests create their own
unique profile directories. Python symlink fixtures may skip on local Windows
without creation privileges; record skips separately from hosted execution.

The guard covers Product API/defaults, Rust facade/shell headers, imports,
resource/license ownership, build mapping and resolved dependency boundaries.
It does not prove every event, native IME, accessibility path or all Rust syntax.
Never refresh baselines merely to make the guard pass.

## Native packages

```console
cargo build --locked --release -p quadrant-agent -p quadrant-app
```

Use the matching host's packaging entry point from this root:

| Host | Entry | Output directory |
|---|---|---|
| Windows, PowerShell 7 | `pwsh -NoProfile -File packaging/windows/package.ps1` | `target/package/windows/` |
| Linux | `bash packaging/linux/package.sh` | `target/package/linux/` |
| macOS | `bash packaging/macos/package.sh` | `target/package/macos/` |

These scripts build both release binaries with a distribution channel, run the
guard and include resources and notices. `-SkipBuild` / `--skip-build` is only for
matching channel-specific prebuilt companions. Inspect
`python scripts/verify_product_package.py --help` for archive/report arguments;
package-validation CI demonstrates them on each native host. macOS produces an
unsigned bundle, not a signed/notarized distribution. Windows PowerShell 5.1
compatibility of private relocation tooling is not a promise about every script.

Validate an extracted complete package away from source and Cargo caches using
an isolated profile. Check icons, Main/capture/editor, save errors, lifecycle,
tray, reminders and real DPI/cross-display behavior. Synthetic native probes
and simulated Slint scale factors have their own narrower scope.

CI runs quality, native Windows/macOS and actual MSRV builds on push/PR/manual
dispatch. Package validation is separate; releases keep the existing `v*` tag
policy and require source_ref to match the version tag. Migration does not
automatically publish a release or replace existing release attachments.

See [architecture](ARCHITECTURE.md), [Kit integration](KIT_INTEGRATION.md),
[workspace workflow](WORKSPACE.md) and the [ledger](migrations/kit-extraction-v2.md).
