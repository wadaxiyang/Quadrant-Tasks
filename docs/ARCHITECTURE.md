# Application architecture

Quadrant-Tasks continues the original Quadrant repository and application. The
directory name does not rename its database, profiles, IPC endpoints, Windows
application identity or shipped GUI. This repository owns eight Cargo crates.

| Crate | Current responsibility | Start reading |
|---|---|---|
| quadrant-domain | Task, quadrant, date, recurrence and Focus rules and values | `crates/quadrant-domain/src/lib.rs` |
| quadrant-application | Use cases, projections, typed intents/events and repository/platform ports | `crates/quadrant-application/src/lib.rs` and `ports.rs` |
| quadrant-storage | SQLite implementations of application repository ports, migrations and backups | `crates/quadrant-storage/src/lib.rs` |
| quadrant-platform | Profile paths/identity, local transport, process launch, tray/hotkey, autostart and notifications | `crates/quadrant-platform/src/lib.rs` |
| quadrant-protocol | Versioned IPC handshake, framing, requests, snapshots and client updates | `crates/quadrant-protocol/src/lib.rs` |
| quadrant-agent | Resident composition root, authoritative state, services, IPC broker and ordered shutdown | `crates/quadrant-agent/src/lib.rs`, `broker.rs`, `lifecycle.rs` |
| quadrant-ui | Generated Slint types, per-window state and Rust presentation adapter | `crates/quadrant-ui/src/lib.rs` and `shell/` |
| quadrant-app | Disposable GUI executable, connection/reconnection and IPC transport for the UI | `crates/quadrant-app/src/main.rs` and `ipc/` |

The Agent opens storage and runs application services. GUI actions become typed
intents sent over local IPC; the Agent processes them and returns snapshots or
updates that the presentation adapter applies to Slint models. The GUI does not
open SQLite or own reminder/Focus schedulers. The Agent has no Kit or Slint edge,
including build/dev reachability. The dependency guard checks the actual resolved
graph as well as manifests; this separation is more than directory naming.

## Process and window ownership

Build both executables before launching the GUI. The GUI locates or starts its
Agent companion; Agent-owned GUI children must not resurrect a stopped parent.
Protocol and profile identity checks distinguish application instances. Keep the
two binaries from the same package together when installing or updating.

Minimize retains the GUI. Main Close with Close to tray enabled releases the GUI
while the Agent remains resident. With that setting disabled, Close requests full
exit. Tray reopen creates/activates the GUI; tray Exit stops the companion
processes. Login startup and native desktop services belong to the Agent.

Quick Add can run without Main, and Main can coexist with it. Quick Add and Task
Editor are created on demand and released on close/confirmed save. Repeated
requests for a visible window preserve its draft. Cancel/Escape follow the
existing close/discard rule; save failure or disconnection preserves the form.
Each independent window initializes Theme, system state and font separately.

The database remains `quadrant-rust.db`. `QUADRANT_DATA_DIR` selects an isolated
development/test profile; it is not a migration to a new production data location.
Backups/restores and their recovery copy remain Agent/storage responsibilities.

## UI ownership and maintenance

Tasks owns `ui/product/`, business components/views, all three window contracts
and the Rust adapter. Generic source components come from the published Kit Git
package at the reviewed revision in Cargo.toml. Kit's separate Gallery is not an
application workspace member. Generated Slint runtime types belong to Tasks.

See [UI architecture](UI_ARCHITECTURE.md) for the presentation layers,
[Kit integration](KIT_INTEGRATION.md) for source/update policy,
[development](DEVELOPMENT.md) for executable commands, and the
[migration ledger](migrations/kit-extraction-v2.md) for acceptance evidence.
