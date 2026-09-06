<p align="center">
  <img src="assets/branding/quadrant-mark.svg" width="96" height="96" alt="Quadrant app icon">
</p>

<h1 align="center">Quadrant</h1>

Quadrant is a local-first, cross-platform four-quadrant task manager built with Rust and Slint.

The Rust application includes Quadrants, Today, Focus, Review, Completed history, reminders, Quick Add, desktop integration, and SQLite-consistent backup/restore.

## Build

Quadrant runs a resident background Agent and a disposable Slint GUI. Build both
companions, then open the GUI; it starts the Agent automatically when needed:

```console
cargo build --locked -p quadrant-agent -p quadrant-app
cargo run --locked -p quadrant-app
```

Minimize keeps the GUI on the taskbar. With **Close to tray** enabled, closing
exits the GUI process while reminders and Focus continue in the Agent. The tray
reopens the interface, and **Exit** stops both processes. Turning Close to tray
off makes window Close request a full exit. Startup preferences apply to the
Agent: **Start in background** means login starts no GUI at all.

Run `quadrant --quick-add` (development: `cargo run -p quadrant-app -- --quick-add`)
to capture a task without creating the main window. The Agent also uses this mode
for the global shortcut when no interface is running. Repeated capture requests
activate an existing capture window and preserve its draft. Main can be opened
separately while a standalone capture is active. Confirmed save, Cancel or Escape
closes the standalone GUI; the Agent continues running.

Quick Add and Task Editor are created only when opened and released on close or
confirmed save. Reopening a visible window keeps its draft; closing it discards
unsaved input. Saves that fail or lose their connection keep the current form.

The GUI communicates only through local IPC and never opens SQLite. Keep both
executables together. Before updating, use tray **Exit** to stop the resident Agent
and all GUI windows, then replace both executables from the same package. This is
required when upgrading from builds with the older profile identity algorithm.
For Agent startup-policy testing, use
`cargo run --locked -p quadrant-agent -- --background`.

For both optimized executables:

```console
cargo build --locked --release -p quadrant-agent -p quadrant-app
```

Shared Fluent controls and the Gallery live in the separate
[Quadrant-Kit repository](https://github.com/wadaxiyang/Quadrant-Kit).
Tasks builds against public Git commit
`838ecfbead2d0a1966907ddd742cb6f34516d3f6` (retained source tag
`candidate/extraction-838ecfbead2d`). Cargo fetches it automatically; no sibling
checkout is required. Static UI resources are embedded into the GUI.

The UI dependency guard is enforced and uses only the Python standard library:

```console
python scripts/check_ui_boundaries.py
python -m unittest discover -s scripts/tests -v
```

It fails on Product API drift, embedded Kit/Gallery copies, invalid imports,
source overrides, forbidden Cargo dependencies, asset/license changes or missing
Slint SPDX headers. See [UI architecture and validation](docs/UI_ARCHITECTURE.md)
for ownership, toolchain requirements and packaging checks.

Windows build outputs are `target/release/quadrant-agent.exe` and
`target/release/quadrant-app.exe`. The scripts under `packaging/windows/`,
`packaging/linux/` and `packaging/macos/` ship both companions together, with the
user-facing GUI named `quadrant` (`quadrant.exe` on Windows). Run the GUI from the
complete extracted package. Executable discovery does not depend on the working
directory. The macOS bundle includes both programs under `Contents/MacOS`.
Linux/macOS packages require their native build/signing hosts.

Quadrant stores its local database as `quadrant-rust.db` in the platform application-data directory. Settings can create validated backups and stage the latest backup for restore on the next Agent startup. Use tray Exit and reopen Quadrant to apply a staged restore; closing only the GUI keeps the Agent running. The previous live database is retained under the adjacent `recovery` directory.

The project is licensed under [GPL-3.0-only](LICENSE). UI primitives are derived from [`owu/wsl-dashboard`](https://github.com/owu/wsl-dashboard), and bundled icons come from [Microsoft Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons). Release notices are maintained in [`packaging/THIRD-PARTY-NOTICES.txt`](packaging/THIRD-PARTY-NOTICES.txt), with the locked Rust package inventory in [`packaging/DEPENDENCY-LICENSES.txt`](packaging/DEPENDENCY-LICENSES.txt).
