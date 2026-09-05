# Kit extraction v2 — migration ledger

## Scope and source

- Specification: `Quadrant_Workspace_Extraction_SPEC_v2.md`, version 2.0.
- Phase 0 started on 2026-09-05. This stage establishes a recoverable source and baseline; it does not extract Kit or switch Product consumption.
- Audited and actual baseline source commit: `79632ca3dec2decce7f830879575c517f4e2a29e`.
- Initial branch: `master`. Initial tracked/untracked working tree: clean.
- Source checkout: ordinary, non-shallow Git repository; `.git` and common directory are both `.git`; one registered worktree.
- Migration branch: `codex/kit-extraction-v2`.
- Local safety tag: `pre-kit-extraction-20260905-phase0`, pointing to the baseline source commit. It is not a release tag and was not pushed.
- Actual extraction source commit: not selected yet; recheck source changes before Phase 1.
- Tasks pre-cutover commit: not selected yet.

The user confirmed that the existing repository and its history belong to the future `Quadrant-Tasks` directory. Its existing remote is already named `Quadrant-Tasks` and points to `https://github.com/wadaxiyang/Quadrant-Tasks.git`. This differs from the historical application URL in the SPEC. Preserve this actual configuration; do not rename the remote or initialize a replacement repository.

The user supplied `https://github.com/wadaxiyang/Quadrant-Kit.git`. GitHub repository metadata confirmed owner/name `wadaxiyang/Quadrant-Kit`, public visibility, and ADMIN permission for the connected account. `git ls-remote` succeeded but returned no refs; GitHub reported no default branch name. The repository is currently empty. No adopted Kit SHA, retained candidate ref, remote CI result, or remote consumer verification exists yet. Product must keep the embedded Kit until Gate 3 passes.

## Protection and cleanup

A complete local `git bundle --all` was created outside the source checkout and successfully checked with `git bundle verify`. The ignored SPEC and root third-party notice were copied alongside it; SHA-256 records are stored with those copies. The bundle includes local Git refs and remains private. It is not intended for publication.

The initial ignored inventory contained the SPEC, root third-party notice, empty `docs/`, `.tmp-wsl-dashboard/`, `legacy/`, and `target/`. No root AGENTS file was present. Historical visual baselines and build outputs are retained in place; they are not part of the Git bundle and must be protected before any later physical relocation. The upstream temporary checkout and legacy source were subsequently relocated to the external private backup as recorded below. No old docs or agent instructions were used as architectural references.

The app's task inventory showed no other active Codex task on this checkout at preflight time; other tasks on it were idle or unloaded. No existing Cargo, rustc, Product, Agent, or Gallery process was found in the initial process check. This is a point-in-time observation and must be rechecked before later mutations.

| Item | Result | Evidence / decision |
|---|---|---|
| `.tmp-wsl-dashboard` | RELOCATED; deletion BLOCKED | User authorized deletion. Checkout was clean at `948589a255a4bd8a3ff9c3de49e2e13109378fcd`; no references found in current crates, UI, scripts, packaging, Cargo manifest, or workflows. Resolved paths were checked; no root/nested reparse points. Automatic approval review rejected permanent recursive deletion with `blocked by policy`. A reversible relocation instead retained all 616 files / 44,019,332 bytes in the external private backup. The initial move left an empty hidden `.git` directory; this empty shell was separately relocated with `-Force`, without overwriting the retained checkout. The source temporary directory is now absent. No file contents were deleted. |
| `legacy/dotnet-reference` | RELOCATED; deletion BLOCKED | On 2026-09-06 the user explicitly authorized deletion. The verified `legacy` directory contained 227 untracked, ignored files / 959,204 bytes and no reparse points. Automatic approval review rejected permanent recursive deletion with `blocked by policy`. The entire directory was instead moved to `legacy-retained` in the external private backup. All 227 file SHA-256 hashes matched after relocation; `legacy/` is absent from the source checkout. No file contents were deleted. |
| `target/` | RETAINED | Contains useful build cache and historical QA results; no broad cleanup. |
| Private root Markdown / docs | PROTECTED | Ignore rules remain restrictive. Only this new migration ledger is allowlisted. No private files are staged. |

## Local validation

Execution directory for all Cargo/Python checks: source repository root. Platform: native Windows x86_64 MSVC. Toolchain: Rust/Cargo 1.94.1, as already pinned by `rust-toolchain.toml`; Python 3.13.15. The workspace declares `rust-version = "1.92"`. Rust 1.92 is not installed and has not been tested. No toolchain or dependency versions were changed.

`cargo metadata --offline --locked --format-version 1` succeeded and resolved both Slint and slint-build to 1.17.1. No resolved package declares a Rust version above 1.92; this metadata observation is not an MSRV build result.

Local evidence root: `target/kit-extraction-phase0/`. This ignored directory contains command logs, JSON results, preflight inventory, and native diagnostic artifacts. A separate backup copy is retained outside the repository; the exact machine path is in local `preflight.json`, not this public ledger.

| Command | Exit | Result | Evidence |
|---|---:|---|---|
| `cargo fmt --all --check` | 0 | PASS | `fmt.log` |
| `python scripts/check_ui_boundaries.py` | 0 | PASS | `ui-boundaries.log`; existing checker only, not the future stronger guard |
| `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings` | 0 | PASS | `clippy.log` |
| `cargo test --workspace --locked` | 0 | PASS | `tests.log`; 125 passed, 0 failed, 1 ignored native Windows notification test |
| `cargo check --workspace --all-targets --locked` | 0 | PASS | `all-targets.log` |
| `cargo build --locked -p quadrant-agent -p quadrant-app -p quadrant-ui-gallery` | 0 | PASS | `build.log` |
| `cargo build --locked -p quadrant-ui --examples` | 0 | PASS | `examples.log` |

Existing tests exercise isolated IPC/storage and a custom headless Slint window adapter. They do not establish native tray, monitor DPI, IME, accessibility, or full packaged application behavior.

Normal-dependency reachability checks over the locked metadata passed: Agent does not reach Slint, its implementation crates, quadrant-ui, or Kit; GUI does not reach quadrant-storage or rusqlite. The local `dependency-baseline.json` records the reachable names. These preflight checks do not replace the new versioned guards required during extraction.

Native baseline capture: PASS for the following limited smoke scenarios. Only existing Gallery and synthetic `task_editor_preview` / `restore_probe` examples were used, from an output directory outside the source root working directory. They do not connect to Agent or open the user's database. All six diagnostic processes exited 0 with empty stderr logs; no diagnostic processes remained afterward.

| Scenario | Result / evidence |
|---|---|
| Gallery Controls page 4, preview 1, Light and Dark, 1040 × 800 | PNGs captured and visually inspected; controls, text, and icons render in both themes. |
| Gallery Inbox page 8, preview 1, Light, 1040 × 800 | PNG captured and visually inspected as the existing Product specimen baseline. |
| Task Editor preview, Light and Dark | PNGs captured and visually inspected; form, labels, icons, and footer render. This does not validate field interaction or scrolling. |
| Synthetic MainWindow minimize / restore | Existing `restore_probe` ran at `scale=1`; `collapsed=false` throughout. Two initial restore samples were blank: 5002 ms (`36x0`) and 5050 ms (`36x680`); visible samples resumed at 5082 ms and remained visible through 5781 ms. A subsequent strict all-samples-visible assertion therefore FAILED. Capture succeeded, but uninterrupted visible frames are not established. This is a recorded pre-existing rendering observation, not a migration regression or full Product lifecycle pass. |

The `native/manifest.json` records scenarios, source SHA, image hashes, and default backend/renderer selection. The exact dynamically selected backend/renderer was not instrumented; these images are local diagnostic evidence, not portable pixel-equality baselines. Native scale in the restore probe was 1; real 200%/225% and cross-monitor tests remain NOT_RUN. The full Product startup and business workflow matrix also remains NOT_RUN.

## Known baseline gaps and required later checks

- Existing UI API checker passes but still has the parsing and boundary gaps described by SPEC section 9; it has not yet been upgraded or given checker fixtures.
- Embedded Kit still exports 32 names and includes Product semantics. Gallery still has pages 0–8 and the old permissive environment parsing. These are Phase 1/4 work, not completed extraction.
- MSRV 1.92 build, Linux/macOS checks, release/package runs, real cross-monitor DPI tests, full native business/lifecycle checks, and accessibility interactions: NOT_RUN.
- The native notification test is intentionally ignored by the existing suite; no claim of notification delivery validation.
- Native restore observation: first two post-restore samples were blank, recovering approximately 80 ms after the restore request; severity/visual perceptibility has not been classified. Preserve this evidence for later regression comparison; do not claim a no-blank-frame baseline or modify lifecycle code during this preflight.
- Kit remote is empty. Kit publication, retained refs, remote CI, smoke consumer, and no-sibling Tasks build: NOT_STARTED.
- Physical layout: LAYOUT_PENDING, intentionally deferred to Phase 6. The active source checkout has not been moved.
- Licensing, asset hash/provenance manifests, 28-symbol Kit baseline/probe, and Product API baseline: NOT_STARTED. Existing attribution and assets are untouched.

## Phase status and next action

Phase 0 / Gate 0: PASS for local preflight, recoverable source identification, protected local materials, and the explicitly scoped Windows baseline above. Cleanup of the project root is complete through reversible relocation; permanent destruction of the archived upstream checkout remains BLOCKED by automatic approval review. Future P0 checks listed above are not waived.

Phases 1–7: NOT_STARTED. Overall migration: NOT_STARTED beyond preflight; not COMPLETE.

Next planned stage: create the independent Kit candidate outside the current source Git root, extract from a rechecked source commit, and keep Tasks consuming its existing embedded Kit. Before that stage, inspect the intended destination and recheck the empty remote to avoid overwriting concurrent work.

Recovery: the original `master` branch and source commit remain unchanged. The local safety tag and verified private bundle preserve Git history. Product source, Cargo manifests, and lockfile have not changed in Phase 0. Do not reset new user changes to recover a previous state; inspect status and use the recorded source reference deliberately.
