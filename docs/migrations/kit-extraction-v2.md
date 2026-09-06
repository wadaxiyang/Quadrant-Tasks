# Kit extraction v2 — migration ledger

## Current checkpoint — Phase 6 accepted (2026-09-06)

Gate 6: **PASS**. Both complete repositories now occupy the independent child
roots `Quadrant/Quadrant-Tasks` and `Quadrant/Quadrant-Kit`. Git invariants,
parent ownership, bootstrap, both boundary guards and native Windows role
builds passed after relocation; details are in the final Phase 6 entry below.
Earlier checkpoint statements in this chronological ledger retain their
historical scope. Gate 5's native manual items remain open; overall migration
is **IN_PROGRESS**. Phase 7 has not started.

## Scope and source

- Specification: `Quadrant_Workspace_Extraction_SPEC_v2.md`, version 2.0.
- Phase 0 started on 2026-09-05. This stage establishes a recoverable source and baseline; it does not extract Kit or switch Product consumption.
- Audited and actual baseline source commit: `79632ca3dec2decce7f830879575c517f4e2a29e`.
- Initial branch: `master`. Initial tracked/untracked working tree: clean.
- Source checkout: ordinary, non-shallow Git repository; `.git` and common directory are both `.git`; one registered worktree.
- Migration branch: `codex/kit-extraction-v2`.
- Local safety tag: `pre-kit-extraction-20260905-phase0`, pointing to the baseline source commit. It is not a release tag and was not pushed.
- Actual extraction source commit: `5a2262cd480d639673fa4f5dd406a9c7196361b5`, selected after a clean Phase 1 preflight; implementation bytes match the audited code commit.
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
- Kit remote was empty on the Phase 1 preflight. Kit publication, retained refs, remote CI, smoke consumer, and no-sibling Tasks build: NOT_STARTED.
- Physical layout: LAYOUT_PENDING, intentionally deferred to Phase 6. The active source checkout has not been moved.
- Kit licensing/provenance records, asset hashes, 28-name API reference and compiled probe were created in Phase 1 below. The full machine-checked Kit API baseline/guard and Product API baseline remain later-phase work. Existing Tasks attribution and assets are untouched.

## Phase status and next action

Phase 0 / Gate 0: PASS for local preflight, recoverable source identification, protected local materials, and the explicitly scoped Windows baseline above. Cleanup of the project root is complete through reversible relocation; permanent destruction of the archived upstream checkout remains BLOCKED by automatic approval review. Future P0 checks listed above are not waived.

Phase 1 / Gate 1: PASS, as detailed below. Phases 2–7: NOT_STARTED as gated stages; some local Phase 2 commands were run early to validate the candidate. Overall migration: IN_PROGRESS, not COMPLETE. Physical layout remains LAYOUT_PENDING.

Next planned stage: Phase 2 — finish the versioned Kit boundary/API guard and checker fixtures, API baseline, incremental resource checks, and required platform/CI validation. Tasks continues consuming its embedded Kit. Gate 3 publication and verified remote consumption must pass before any Product cutover.

Recovery: the original `master` branch and source commit remain unchanged. The local safety tag and verified private bundle preserve Git history. Product source, Cargo manifests, and lockfile have not changed in Phase 0. Do not reset new user changes to recover a previous state; inspect status and use the recorded source reference deliberately.

## Phase 1 — independent local Kit candidate (2026-09-06)

Source preflight was clean on `codex/kit-extraction-v2` at `5a2262cd480d639673fa4f5dd406a9c7196361b5`. Changes since the audited implementation were only `.gitignore` and this ledger. The Kit destination did not exist; the target remote still advertised no refs. The candidate was created as a sibling outside this Tasks Git root, not as a nested repository or a replacement Tasks repository.

| Repository | Branch | Phase 1 checkpoint |
|---|---|---|
| Tasks, existing checkout | `codex/kit-extraction-v2` | Original application source, Cargo manifests, lockfile, and embedded Kit/Gallery unchanged; only this ledger updated. |
| Kit, independent checkout | `codex/extraction-candidate` | `008c9b6086f9cddc9ee5dce43bb97a26192c9ff7`; origin `https://github.com/wadaxiyang/Quadrant-Kit.git`; local only, not pushed. |

The Kit checkpoint is a **local candidate SHA**, not an adopted Product dependency, retained remote reference, or published release. Its implementation was validated at `acad992704b75959f1ae2f51304864e919b5a87b`, followed by a documentation-only verification record; the final candidate was also built successfully. No Kit revision was inserted into Tasks.

### Extraction and ownership

- Copied 77 source/asset files from the selected source commit. Kit's `scripts/extraction_manifest.json` records old/new paths, source/extracted SHA-256 hashes, modification status, and newly authored files. All 77 extracted hashes were checked against the actual candidate files.
- Root helper has no dependencies and exports only the library name and build-time facade path. Gallery is the only member application and uses a same-repository path build dependency. Kit has its own Cargo.lock and target directory; Tasks' lockfile was not copied or changed.
- Public facade has 28 names. Branding, InboxItem/InboxPane, TaskRowShell, Q1–Q4, the timer font size, Focus breakpoint, and 11 product icon aliases were excluded. Product files remain in their original locations until Phase 4.
- Retained 32 generic SVGs byte-for-byte with their MIT license. Their property/path/hash/upstream records are in `scripts/asset_manifest.json`. GPL headers and derived-code source comments remain. `.gitattributes` preserves SVG bytes and uses LF for other text files.
- Gallery has eight pages (0–7), neutral samples, a compiled 28-name API probe, explicit per-host theme/font initialization, and a separate never-shown system-theme observer. System preference detection stays in Gallery, not the root helper or a Product platform dependency.
- Snapshot input validation rejects removed/invalid pages, invalid preview/theme, nonfinite/nonpositive dimensions and invalid output paths. Capture tooling builds once per invocation, writes per-scene manifests keyed by source/environment/page/preview/size/theme/scale, and only reuses matching content. Ordinary renderer defaults are unchanged; reproducible snapshot runs explicitly select winit-software.
- Kit now owns AGENTS, README, architecture/API/consumer/Gallery/provenance documentation and candidate change notes. The full boundary/API compatibility guard and baseline are explicitly deferred to Phase 2; the current distribution checker does not pretend to implement them.

### Gate 1 evidence

Environment: native Windows x86_64 MSVC; Rust/Cargo 1.94.1; Python 3.13.15; Slint/slint-build 1.17.1. Kit logs are in its ignored `target/phase1/`; screenshots include source IDs and remain local. Tasks' old-build log is `target/kit-extraction-phase0/tasks-phase1-build.log`. Exact local checkout/backup paths are recorded in local checkpoint metadata, not this public ledger.

| Check | Result | Evidence |
|---|---|---|
| Tasks `cargo build --locked -p quadrant-agent -p quadrant-app` | PASS, exit 0 | Old consumption remains buildable; source/Cargo/lock diff from Phase 1 input is empty. |
| Kit Gallery build, including API probe | PASS, exit 0 | `build-final-head.log`; all 28 symbols compile. |
| Kit independent clone with own target and no Tasks checkout | PASS, exit 0 | `isolated-build-final.log`; asset hashes also match after Windows checkout. Shared Cargo download cache was allowed; build directories and locks were independent. This is local independence, not remote Git consumption. |
| Kit fmt / clippy all-targets/all-features, warnings denied | PASS, exit 0 | `fmt.log`, `clippy-final.log`. |
| Kit Rust tests | PASS: 5 tests | `tests-final.log`: 1 root helper, 4 configuration tests. |
| Snapshot tool tests | PASS: 2 tests | `python-tests.log`: dirty content identity, stale/mismatched/corrupted scene rejection. |
| Distribution closure and package list | PASS, exit 0 | `distribution-final.log`: 32 SVGs; required Slint, asset, license and provenance files included. |
| `cargo package --locked -p quadrant-kit` | PASS, exit 0 | `package-final.log`: 70 packaged files, verified root helper build. This alone is not Slint runtime verification. |
| Gallery native rendering | PASS for 12 scoped scenes | `native/results.json`: all eight pages plus Dark/System and representative 200%/225% simulated scales. Final icon-tint fix rechecked in Light Controls and Dark Navigation; `native-final/result.json`, `capture-final.log`. |
| Native invalid configuration/output handling | PASS | 8 invalid configurations returned 1; output-directory-as-file returned 2. Local diagnostic UTF-8 logging was corrected and that output-error case rechecked. |
| Public PowerShell capture wrapper and scene reuse | PASS | `capture-final.log`, `capture-reuse.log`; fresh scene capture and matching reuse observed. |
| Kit root normal-dependency tree / workspace metadata | PASS | `helper-dependencies.log`, `cargo-metadata.json`: helper alone; only Kit/Gallery workspace members; no Product packages anywhere in resolved metadata. |

An initial unsupported Palette property was caught by Slint compilation and replaced by the supported separate-instance host approach. Native screenshot review also caught a dark-theme contrast issue in the replacement Gallery header icon; it was fixed by using FluentIcon. Neither issue required changing Tasks or generic component behavior.

**Gate 1 is satisfied:** Tasks still builds using the embedded Kit; the independent Kit checkout builds its own Gallery without Tasks; neither build writes the other's sources. There was no push, release tag, remote CI, Product dependency switch, or physical relocation of the Tasks repository.

Outstanding gates retain their original scope: full API/architecture checker and tests, Rust 1.92 and Linux/macOS checks, CI, incremental token/SVG rebuild tests, remote candidate publication/retention/consumer verification, Product cutover and native regression matrix, and final parent/two-child layout. Real OS theme changes, monitor DPI transitions, keyboard/IME/accessibility interaction, and final source-free package runtime have not been claimed as tested in this phase.

## Phase 2 — Kit boundary/API, baseline and local platform validation (2026-09-06)

Kit local candidate: `2715d01bb2edcb3a62890878517c946b82851352` on `codex/extraction-candidate`. Its implementation was checked at `960373bd30d350699ed29fec667cb69ab3ad77fd`, followed by a documentation-only evidence commit. The final candidate was packaged and its archive rechecked. Neither commit was pushed. Tasks remains on its embedded Kit; Product sources, Cargo manifests, Cargo.lock, existing checker and runtime behavior are unchanged in this phase.

### Contracts and checks delivered

- Kit now owns `scripts/check_ui_boundaries.py`, a shared standard-library lexical scanner, Cargo manifest/resolved-graph checks and positive/negative fixtures. These preserve the original guard's useful import/layer/cycle/API checks and replace its regex/line-counting blind spots. Multiline/alias declarations, comments and escaped strings, balanced delimiters, property directions/types/bindings, callback/function signatures and pure modifiers, struct fields, enums and base types are covered. Unknown public syntax fails explicitly; the Slint 1.17.1 compiled probe supplements semantic validation.
- `scripts/kit_api_v1.json` freezes 28 exports, 217 properties, 13 callbacks and four enums, with signature and default-expression changes reported separately. The four removed Product names, Q1–Q4/timer/Focus tokens and 11 removed icon aliases are documented as the SPEC-authorized initial migration. CI never auto-refreshes this baseline.
- Kit/Gallery import boundaries, same-layer cycles, upward/cross-layer imports, implementation/facade recursion, raw Gallery imports, Product declarations/tokens, static path escapes, asset hashes/licenses and source headers are checked. Generic FocusScope/task text and legal Gallery/internal crate paths have positive fixtures.
- The distribution checker uses the same scanner, validates the live 32-SVG manifest and license material, requires tracked static dependencies, checks package-list inclusion and compares required bytes in the actual `.crate` archive. SVG/UI/Gallery implementation, Cargo.lock and the pinned toolchain have no diff from Phase 1.
- The incremental verifier changes a deep token and referenced SVG separately, requires Gallery build-script reruns and changed binaries, restores exact bytes and rebuilds. Verbose logs identify both deep changed files; it requires exclusive checkout/build access.
- New Kit CI supports push/PR/manual triggers with contents:read: Linux quality/guard/tests/Gallery/package/incremental; Windows native Gallery and screenshot smoke; macOS workspace all-targets/guard; actual Rust 1.92.0 helper+Gallery builds on Windows. This is workflow preparation, not remote CI evidence.
- README, public API, consumer/provenance/Gallery documentation, AGENTS and `docs/VALIDATION.md` describe actual commands, explicit baseline review and remaining limitations. Future Tasks policy fixtures do not activate the final Tasks cutover guard early.

### Gate 2 evidence

Raw evidence is local under Kit `target/phase2/`, `target/incremental-verification/` and source-keyed visual baseline directories. Windows environment: native x86_64 MSVC, Rust/Cargo 1.94.1 and 1.92.0, Python 3.13.15. Linux environment: Ubuntu 24.04 x86_64, WSL2/WSLg, Rust/Cargo 1.94.1, Python 3.12; its target directory is separate from Windows and Tasks.

| Check | Result | Evidence |
|---|---|---|
| Windows fmt / clippy all-targets/all-features with denied warnings / Rust tests | PASS; 5 Rust tests | `fmt.log`, `clippy.log`, `tests.log` |
| Windows boundary/API/assets/resolved dependencies / Python tests | PASS; 31 tests | `boundaries-final.log`, `python-tests-final.log` |
| Windows Gallery + 28-name Slint API probe | PASS | `build-final.log` |
| Actual Rust 1.92.0 helper + Gallery build | PASS; independent MSRV target | `msrv.log` |
| Linux fmt / clippy all-targets/all-features / Rust tests / Gallery + probe | PASS; 5 Rust tests | `linux-fmt.log`, `linux-clippy.log`, `linux-tests.log`, `linux-build.log` |
| Linux boundary/API/assets/resolved dependencies / Python tests | PASS; 31 tests | `linux-boundaries-final.log`, `linux-python-tests-final.log` |
| Independent local Kit Git clone with own target and no Tasks checkout | PASS: guard and Gallery build | `isolated-boundaries.log`, `isolated-build.log` |
| Source package and archive verification | PASS: 72 files packaged, 59 required files byte-checked including 32 SVGs | `package.log`, `distribution.log`; final candidate `package-final-head.log`, `distribution-final-head.log` |
| Deep token / referenced SVG incremental build | PASS: both rerun Gallery build script and change binary; bytes restored | `incremental-verification/result.json` and verbose build logs |
| Windows / Linux WSLg Controls rendering smoke | PASS: Light, page 4, preview 1, 1040×800, 100%, winit-software | `capture-windows.log`, `capture-linux.log`; clean SHA/content identity in PNG manifests |
| macOS native workspace all-targets | NOT_RUN locally; no macOS host/SDK | Mandatory prepared CI job to run in Phase 3 |
| Actual remote CI / retained commit / Git+SHA neutral consumer | NOT_RUN; no publication performed | Phase 3 |

Linux initially lacked fontconfig development files and the X11 xkbcommon runtime. Both failures were resolved using Ubuntu packages extracted into a private user-owned validation sysroot, with command-scoped pkg-config/runtime paths. Stale apt-index download 404s were resolved with a private refreshed index. No system package replacement or repository build override was committed. Both platform screenshots were reviewed; font/render differences are recorded, not asserted pixel-identical.

**Gate 2 local requirements are satisfied.** Kit is independently reviewable, buildable, testable and packageable, with the intended Product-free API and licensing material. This does not mark all platform gates or the full migration complete: macOS, actual remote CI and retained Git consumption are still mandatory. Real OS theme transitions, monitor DPI transitions, keyboard/IME and complete accessibility/focus behavior remain unverified; ModalManager focus containment/restoration remains a documented P1 gap.

The next phase is Phase 3 publication and same-SHA remote verification. No Tasks dependency switch, Git remote push, release tag or parent/child directory relocation occurred in Phase 2.

## Phase 3 — Published candidate and real remote consumption (2026-09-06)

**Gate 3: PASS.** The qualified, remotely available Kit commit is **`838ecfbead2d0a1966907ddd742cb6f34516d3f6`**. It has passed actual remote CI and independent Git+SHA consumer verification. This is the candidate eligible for Phase 4; Tasks has not adopted it yet.

### Publication and retention

- Rechecked `wadaxiyang/Quadrant-Kit`: PUBLIC, expected URL `https://github.com/wadaxiyang/Quadrant-Kit.git`, ADMIN access, initially no remote refs. Reviewed tracked source/documentation/license files and credential/machine-path indicators before publication. Only the Kit repository was pushed.
- Added remote mode to `scripts/verify_distribution.py` and its isolated verification module/fixtures. Local boundary/package/archive checks and all 35 Python tests passed before commit and push. The consumer guide documents parameters, isolation, retained evidence and baseline/retention discipline.
- Pushed `codex/extraction-candidate` at the full SHA above. After its CI passed, created annotated tag **`candidate/extraction-838ecfbead2d`** and pushed only that explicit tag. Its tag object is `aa736b6873652d0c8dd8ea55df6d16bb5cec9f39`; its peeled commit is the qualified SHA, not the tag object SHA.
- Created `main` at the same verified commit and set it as the repository default branch. Existing candidate history was preserved; no force push, tag movement or stable `v0.1.0` release occurred.
- Repository ruleset **22363188**, [Retain extraction candidate commits](https://github.com/wadaxiyang/Quadrant-Kit/rules/22363188), is active for `refs/tags/candidate/extraction-*`. Update and deletion are prohibited, there are no bypass actors, and the API reports the current user cannot bypass it. Future fixes must use new commits and new candidate tags. Retained candidate tags are not formal stable releases.

### Same-SHA CI evidence

Every run below has `headSha = 838ecfbead2d0a1966907ddd742cb6f34516d3f6`, status completed and conclusion success. All four jobs passed in each run.

| Trigger/reference | Run | Result |
|---|---|---|
| Candidate branch, before retention tag creation | [34003620362](https://github.com/wadaxiyang/Quadrant-Kit/actions/runs/34003620362) | PASS |
| Retained candidate tag | [34004051391](https://github.com/wadaxiyang/Quadrant-Kit/actions/runs/34004051391) | PASS |
| Default `main` branch | [34004053852](https://github.com/wadaxiyang/Quadrant-Kit/actions/runs/34004053852) | PASS |

Jobs cover Linux fmt/clippy/tests, boundary/API/assets/resolved graph, 35 Python fixtures, Gallery/probe, package/archive and incremental token/SVG invalidation; Windows all-targets/guard/tests/native Gallery and screenshot; macOS native workspace all-targets/guard/tests; and actual Windows Rust 1.92.0 helper+Gallery builds. The previously unrun macOS gate now has real hosted-runner evidence. The candidate-run Windows Controls PNG/manifest artifact was downloaded and visually reviewed.

### Independent anonymous fetch and neutral consumer

The verification command used the exact public URL, full SHA and `refs/tags/candidate/extraction-838ecfbead2d`, plus GUI smoke and a report output path. It created a fresh temporary working directory, Cargo home and target outside both project checkouts. No sibling Kit path, copied implementation, personal Cargo cache/config, URL rewrite, patch or source replacement was used. Personal/system Git configuration and credential helpers were disabled; the Kit fetch was anonymous.

| Verification | Result |
|---|---|
| Fetch explicit retained ref, then `FETCH_HEAD^{commit}` | PASS; exactly the qualified 40-character SHA |
| Deliberate initial consumer lockfile generation | PASS; 597 packages resolved with the declared Rust 1.92 compatibility policy |
| Actual metadata source | `git+https://github.com/wadaxiyang/Quadrant-Kit.git?rev=838ecfbead2d0a1966907ddd742cb6f34516d3f6#838ecfbead2d0a1966907ddd742cb6f34516d3f6` |
| Actual manifest location | Inside the new CARGO_HOME's `git/checkouts/quadrant-kit-66b2a2b03347928c/838ecfb/Cargo.toml`; canonical path checked, no sibling checkout |
| Slint and slint-build | Exactly 1.17.1; metadata contains no Product packages |
| `cargo build --locked` | PASS, exit 0; native Windows MSVC Rust/Cargo 1.94.1; fresh target |
| Lockfile integrity | Unchanged by locked build; SHA-256 `d48930e4e83ad97abd5fe9742bf468a27697a5f9475ab926e45942adbb0ae2f7` |
| Light and Dark native consumer rendering | PASS, exit 0 each; winit-software at 100%, two 640×440 PNGs visually reviewed |

The generated consumer compiles Theme/ThemeMode, FluentButton, FluentIcon/FluentIcons, ModalManager/ModalKind and ToastHost/ToastKind through the file-mapped `@quadrant-kit` facade with EmbedFiles. It contains no Product crate, DTO or asset. Runtime smoke launches a copied binary from a separate directory without source/asset files. The build cache still exists elsewhere; this evidence is not described as a source-cache-deletion test or as validation of the final Tasks runtime package. Modal is compiled; complete modal interaction/accessibility is not claimed.

An initial isolated attempt fetched and peeled the tag successfully but then failed to connect during Cargo's Git fetch because the existing Git-configured proxy was intentionally excluded with personal Git configuration. The failed attempt/report/logs were retained. A second **new** work/cache/target directory explicitly received that existing network proxy through HTTP_PROXY/HTTPS_PROXY, while all source rewrites and credential configuration remained disabled. It passed fetch, metadata, locked build and both runtime scenes. TLS verification was never disabled, and no local-path fallback or fake revision was used.

Local Kit evidence is under ignored `target/phase3/`: the initial and successful remote reports/logs, CI JSON and full candidate-run log, Windows CI artifact, retained-ref listing and ruleset responses. The successful consumer's generated source, Cargo.lock, step logs, result and PNGs remain in its isolated directory and are copied into the private phase checkpoint. No cache, machine configuration or private raw log was added to either Git repository.

### Handoff

Kit `main` and `codex/extraction-candidate` point to the qualified commit; the protected annotated tag retains it. Tasks still uses its original embedded Kit/Gallery, manifests, lockfile and guard. Phase 3 changed only this Tasks ledger. No Product switch, embedded source deletion, stable release or final parent/two-child directory relocation was performed. Phase 4 can now use the actual verified Git+SHA dependency and proceed with its own controlled cutover/regression gates.

## Phase 4 — Controlled Product cutover (2026-09-06)

The complete integration is on `codex/kit-product-cutover`. The pre-cutover
Tasks commit is `d2b423d4b7f557116f6fe655dcc67aac60db2d7f`, retained locally by
`pre-kit-cutover-20260906`. Kit remains unchanged at the Gate 3 qualified commit
`838ecfbead2d0a1966907ddd742cb6f34516d3f6` and its protected candidate tag.

### Atomic source and contract changes

- Migrated Branding, InboxItem, InboxPane and TaskRowShell into Product before
  deleting the old embedded Kit/Gallery trees, Gallery crate and capture script.
  Tasks now has eight workspace crates. No generic Slint implementation is copied
  into another Tasks directory.
- Added Product quadrant colors, timer typography, Focus breakpoint and eleven
  icon aliases. They retain original values/asset bytes; quadrant colors use the
  same imported Theme.dark_mode. Thirty-two Kit-owned icon copies were removed;
  Product icons, native branding and the original MIT text remain.
- quadrant-ui alone has the public Git+full-SHA Kit build dependency. build.rs
  maps the returned facade file to @quadrant-kit and embeds resources with
  EmbedFiles. Window/model Rust types are still generated inside quadrant-ui.
- Compared all 23 original Product exports before deletion against the new
  scanner: signatures and defaults match except Branding's relocated relative
  image path, which resolves to the same unchanged SVG. Four Product semantic
  globals are added. GuiShell/UiShell Rust implementations and public interfaces,
  Agent/business/storage code, profile identity and protocol are unchanged.
- Reviewed Cargo.lock: only adds quadrant-kit 0.1.0 at the qualified source,
  adds its UI build edge and removes quadrant-ui-gallery. No registry package
  version changed. The workspace png dependency remains required by UI probes.
- Replaced the old mixed baseline with reviewed Product API, Kit source/copy
  fingerprints and Product asset manifests. The guard retains import/cycle/API/
  attribution checks and verifies source overrides, actual Git storage/source,
  exclusive UI build ownership, Agent build/dev/transitive isolation and GUI
  normal dependency isolation. Sixteen Python fixtures cover failure cases.
- Updated README and public UI architecture guidance, three packaging scripts
  and third-party notices. Packages include the original Fluent MIT text.
  CI runs on push/PR with pinned toolchains, target-filtered source checks,
  Windows/macOS native builds and an actual Windows Rust 1.92 build. Release
  verification compares the existing tag's peeled commit to the selected source
  and passes that exact SHA to every packaging job. No release was triggered.

### Local integration evidence before CI

Windows MSVC Rust/Cargo 1.94.1: locked workspace/all-targets check, fmt, clippy
all-targets/all-features with warnings denied, the synthetic three-window probe
and the repeated full workspace test run pass. The full run reports **125
passed, 0 failed, 1 ignored** (the existing real Windows notification smoke).
Main/Quick Add/Task Editor were captured and visually reviewed in Light and Dark
with winit-software; all six images contain the expected controls and assets.
These probes never start Agent or access a database.

The first full test run terminated the IPC integration binary with Windows
STATUS_HEAP_CORRUPTION after seven tests. A targeted 12-test rerun, five repeats
of the exact original test binary and the subsequent entire workspace run all
pass. No test was disabled or serialized. This intermittent failure is retained
as an unresolved diagnostic for Phase 5 stress regression, not attributed to
Kit: Agent sources and its resolved dependencies were not changed.

Private command logs, pre-cutover contracts, lock review and native screenshots
are under ignored target/phase4. Final optimized build and same-commit hosted CI
results will be recorded below before declaring Gate 4. Phase 5 package/business
regression and Phase 6 directory relocation have not been performed.

### Hosted checkout correction

The first candidate `f439d964302965b3313f3d4808b95366e7f67301` exposed a real
Windows checkout difference in run 34005112838: core.autocrlf changed the original
SVG bytes, so the Product asset hash guard correctly failed. Added repository
attributes that preserve upstream SVG/MIT bytes and keep shell entry points LF.
The asset hashes were not weakened or regenerated. A real temporary Git index
and checkout with core.autocrlf=true now verifies byte-for-byte preservation;
all **17 Python tests pass**. Linux/macOS had already passed the source guard.

Local locked debug and optimized release builds of both quadrant-agent and
quadrant-app also pass, along with the final all-targets check. Packaging scripts
pass PowerShell parsing and native shell syntax checks using their committed
bytes. This verifies packaging entry points, not Phase 5 package execution.

### Strict platform lint corrections

Linux CI exposed seven pre-existing non-Windows lint errors in quadrant-platform.
The narrow corrections remove unnecessary mutability/result wrapping in private
fallback code, compile Windows notification helpers only on Windows or in their
tests, and add the missing Unix cleanup semicolon. AgentStream::close keeps its
portable async signature: Windows awaits a native drain, so only that method has
a reasoned non-Windows unused_async expectation. No global lint is disabled and
no business behavior or public signature changes. Windows Platform/Agent tests
pass after the corrections. Linux all-workspace/all-targets/all-features Clippy
with -D warnings also passes locally using the existing private Phase 2 SDK.

Review also closed an import-scanner exclusion gap: Product imports cannot point
into target, __pycache__ or .tmp-* directories. The regression fixture confirms
that such sources cannot evade scanning. All **18 Python tests pass**.

macOS all-targets compilation passed, then its newly enabled native tests exposed
Darwin's long runner TMPDIR: the UUID test profile plus socket name exceeded
sockaddr_un capacity. CI now sets TMPDIR=/tmp only for the macOS workspace-test
step; all existing tests remain enabled and retain their unique isolated profile
directories. The matching local command is documented. This changes neither
production profile discovery nor socket identity. Linux's complete workspace
test run passes locally after the lint corrections.

The short-root macOS rerun then reached the transport and exposed a production
compatibility defect: interprocess 2.4.3's mode(0600) uses pre-bind descriptor
fchmod, unsupported on Darwin. The macOS branch now binds inside the already
verified owner-only 0700 directory, then applies 0600 to the filesystem socket
before returning the listener. Other users cannot traverse that directory during
the operation; peer UID authentication remains required. Linux keeps its existing
pre-bind mode. No process-global umask change, unrestricted fallback, protocol
change or profile-identity change was introduced.

Three Unix native regression tests verify directory/socket ownership and modes
with an authenticated ping/pong, rejection of permissive existing directories,
and preservation of non-socket files at the endpoint path. They and the Agent
tests pass on Linux, with strict platform/Agent Clippy. Native CI now runs this
transport/Agent preflight before compiling the large Product UI, so transport
failures are reported early. The final macOS result remains a required gate.

The Darwin preflight now passes Agent startup and all 12 real IPC integration
tests. One new permission fixture initially collided with another fixture's
timestamp-based directory name on the runner's coarse clock. Added a process-local
atomic sequence to the short fixture name; runtime endpoint naming is untouched.

### Gate 4 acceptance

**Gate 4: PASS.** The tested implementation commit is
`dc5497433a8ccfc7db9603dfadebdd54637c9995`, on `codex/kit-product-cutover`.
[CI run 34006175012](https://github.com/wadaxiyang/Quadrant-Tasks/actions/runs/34006175012)
completed successfully at exactly that SHA; all four jobs passed. This acceptance
entry is a subsequent documentation-only commit, not a change to the tested code.

| Check | Result |
|---|---|
| Product contracts, owned assets, actual Git source and dependency graph | PASS on Windows, Linux and macOS; 27 Product exports, 12 static Product assets, one UI build-only Kit edge |
| Python scanner/guard/checkout fixtures | PASS; 18 tests on each platform |
| Linux quality | PASS: fmt, Clippy all-targets/all-features with -D warnings, workspace tests and both native binaries |
| Windows native | PASS: Agent/transport preflight, all-targets check, workspace tests, both binaries and Light/Dark three-window smoke |
| macOS native | PASS: Agent/transport preflight including socket permissions and authenticated roundtrip, all-targets check, workspace tests and both binaries |
| Declared Rust minimum | PASS: actual Windows Rust 1.92.0 build of quadrant-agent and quadrant-app |
| Local Windows final code | PASS: 125 tests, 0 failures, 1 existing notification smoke ignored; strict Clippy, all-targets and debug/release dual-binary builds |
| Local Linux final code | PASS: 123 tests, 0 failures, 0 ignored; includes the three added Unix permission regressions |
| Native UI assets | PASS: six final-commit Windows CI PNGs downloaded, hashed and byte-identical to the reviewed earlier CI images; local Light/Dark probes also reviewed |
| Locked dependency review | PASS: approved Kit Git entry and UI build edge added, old Gallery removed; registry versions unchanged |

The final CI JSON/full log, test summaries, native artifact manifest and PNGs are
retained with the local phase checkpoint. Subsequent acceptance-ledger commits
contain only this record; the final delivery identifies the actual final HEAD.
Kit remains at `838ecfbead2d0a1966907ddd742cb6f34516d3f6` with its protected retained
candidate tag. No source override or local Kit fallback was introduced.

The initial Windows IPC heap-corruption event remains recorded above. It did not
recur in targeted runs, five exact-binary repetitions, subsequent full local
tests or successful hosted Windows tests; preserve it for Phase 5 stress checks.
Phase 4 acceptance is not a claim that the Phase 5 package/dual-process/native
business matrix or Phase 6 physical workspace relocation has been completed.

## Phase 5 — independent builds, packages and native regression (2026-09-06)

**Gate 5: INCOMPLETE — native manual acceptance remains open.** Build, source
independence and distribution checks pass. The observed Windows startup crash
is fixed and stress-tested. Actual system-tray reopen/Exit and physical DPI /
cross-monitor transitions have not been verified; notification delivery while
the GUI is closed also remains unobserved. These are not replaced by unit tests
or synthetic screenshots. Phase 6 has not started.

The first tested implementation is `22fb670835299902e4a3c7d4fb34c0790ed11541` on
`codex/kit-product-cutover`. Kit remains unchanged at
`838ecfbead2d0a1966907ddd742cb6f34516d3f6`. This entry is a subsequent
documentation-only commit; package hashes and native results refer to the
implementation SHA, not to an untested rebuilt package.

### Independent checkout and command evidence

Both repositories were cloned from their actual GitHub remotes into separate
temporary parents, each with a new, separate `CARGO_HOME`. Neither checkout had
a sibling repository, source override, shared target directory or copied build
cache. Tasks resolved Kit from the pinned remote Git source. The first clean
Tasks release build used the Phase 4 commit, then the same independent checkout
was fast-forwarded to the Phase 5 fix and rebuilt/retested. This distinction is
retained in the logs.

Private evidence paths below are relative to ignored `target/phase5`. Local
builds used Windows 11 build 26200, Rust 1.94.1, x86_64-pc-windows-msvc. Successful
commands in this table exited 0. Hosted jobs record their own working directory,
toolchain and platform in the linked full logs.

| Check / command | Execution directory | Result and evidence |
|---|---|---|
| `git -c credential.helper= clone --branch codex/kit-product-cutover --single-branch https://github.com/wadaxiyang/Quadrant-Tasks.git repo` | Isolated Tasks verification parent (exact private path in command logs) | Independent remote checkout; Kit resolved below this parent's new `cargo-home`, as recorded by `tasks-clean-package.log` and `tasks-clean-package-fixed.log` |
| `git -c credential.helper= clone https://github.com/wadaxiyang/Quadrant-Kit.git repo`, checkout approved full SHA | Separate isolated Kit verification parent | Clean approved Kit checkout; independent `cargo-home` |
| `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`; `cargo test --workspace --locked` | Fresh Kit `repo` | PASS; 5 Rust tests; `kit-clean-gates.log` |
| `python scripts/check_ui_boundaries.py`; `python -m unittest discover -s scripts/tests -p test_*.py` | Fresh Kit `repo` | PASS; 35 Python tests; `kit-clean-gates.log` |
| `cargo build --locked -p quadrant-kit-gallery` | Fresh Kit `repo` | PASS; `kit-clean-build.log` |
| `cargo package --locked -p quadrant-kit --list`; `cargo package --locked -p quadrant-kit` | Fresh Kit `repo` | PASS, including Cargo package verification; 72 files, public `ui/kit.slint`, assets and licenses; `kit-clean-gates.log`, `kit-crate-files.json` |
| `pwsh -NoProfile -File packaging/windows/package.ps1` | Fresh Tasks `repo` | PASS; original entry point builds the optimized executable pair and archive; `tasks-clean-package-fixed.log` |
| `python scripts/verify_product_package.py target/package/windows/Quadrant-0.1.1-windows-x86_64.zip --platform windows --output <evidence>/windows-clean-package-fixed.json` | Fresh Tasks `repo` | PASS; native executable signatures, licenses and archive checksum |
| `cargo check --workspace --all-targets --locked`; `cargo test --workspace --locked` | Fresh Tasks `repo` | PASS; 126 tests, 0 failures, 1 existing notification smoke ignored; `tasks-clean-all-targets.log`, `tasks-clean-tests.log` |
| `cargo test --locked -p quadrant-platform -p quadrant-agent`; strict platform/Agent Clippy | Original Tasks checkout | PASS; `identity-fix-tests.log`, `identity-fix-clippy.log` |
| `python -m unittest discover -s scripts/tests -v`; `python scripts/check_ui_boundaries.py` | Original Tasks checkout and all three native CI platforms | PASS; 25 Python tests, including 7 new package fixtures; `python-package-tests.log`, `guard-identity-fix.log`, hosted logs |

For runtime isolation, the fresh Tasks source and Cargo cache were subsequently
renamed to `repo-offline` and `cargo-home-offline`, within their temporary parent.
Their original compiled absolute paths no longer existed. The extracted release
pair ran from a separate runtime parent's `package` directory, with an empty
working directory and an empty runtime `CARGO_HOME`. All runtime test data used
that parent's isolated `profile` via `QUADRANT_DATA_DIR`. See
`build-paths-offline.json`, `runtime-binaries.json` and `native-interaction`.

The local runtime ZIP SHA-256 is
`5db8ded01f8ddff6cc4b481ee085c9e46dd5464386c3c6469bd013adc1841e65`.
Both executables were extracted from that same archive. The verifier compares
license bytes against the checkout that produced the archive: an initial attempt
using the original working tree encountered its differing LICENSE line endings;
the producer-checkout verification passed without weakening the byte comparison.

### Native CI and distribution closure

[Code CI 34008329629](https://github.com/wadaxiyang/Quadrant-Tasks/actions/runs/34008329629)
passed all four jobs at exactly the implementation SHA:

| Platform / job | Verified result |
|---|---|
| Linux, Rust 1.94.1 | fmt, strict all-targets/all-features Clippy, boundary/API/asset guard, 25 Python tests, 123 Rust tests and both native binaries |
| Windows, Rust 1.94.1 | Agent/transport preflight, all-targets check, 126 Rust tests with 1 existing notification smoke ignored, both binaries and native three-window probes |
| macOS, Rust 1.94.1 | Agent/transport preflight, all-targets check, 123 Rust tests, both binaries; existing short test TMPDIR retained |
| Windows MSRV | Actual Rust 1.92.0 locked build of both binaries |

[Package CI 34008329538](https://github.com/wadaxiyang/Quadrant-Tasks/actions/runs/34008329538)
passed Windows, Linux and macOS native packaging at that same SHA. The new
workflow invokes the original `packaging/windows/package.ps1`,
`packaging/linux/package.sh` and `packaging/macos/package.sh`. It uploads test
archives and verification reports; it does not publish a release. macOS remains
explicitly unsigned.

`scripts/verify_product_package.py` checks the actual archive, executable pair
and platform format, original license bytes, checksum sidecar and platform
resources. It rejects source/profile leakage and unsafe archive entries.
The seven fixtures cover a complete pair and failures for a missing Agent,
wrong binary format, altered MIT license, bad checksum, leaked source/profile
and unsafe path. Real Linux/macOS archives additionally exercise their platform
resource checks. This is archive verification, not a claim that those two
platforms received the interactive Windows business regression.

All three CI archives were downloaded and their hashes rechecked against both
the reports and sidecars; each report identifies the exact implementation SHA.
`evidence-summary.json` records their platform/toolchain and hashes;
`code-ci-final.{json,log}`, `package-ci-final.{json,log}` and `ci-packages/` retain
the full results. Workspace test totals exclude separately repeated preflight
steps.

### Windows concurrent startup crash: resolved

The Phase 4 heap-corruption observation recurred on the fifth Phase 5 IPC stress
round as `0xc0000005`. Native debugger reproduction captured `0xc0000374` with
the symbolized path `SetCurrentProcessExplicitAppUserModelID -> LocalFree ->
RtlFreeHeap`, entered by concurrent `Agent::open` calls. The fault was in repeated
concurrent process identity initialization; no evidence implicated Kit imports
or named-pipe shutdown.

`initialize_application_identity` now caches the Windows initialization result
in a process-wide `OnceLock`. The AUMID remains `Quadrant.Tasks`; profile, IPC,
database and application identity values are unchanged. A fresh-child Windows
regression synchronizes 32 threads at a barrier, each making 64 calls, including
first-call contention. Existing tests remain parallel and enabled.

After the fix, **30 complete IPC rounds passed: 360 tests, 0 failures**.
`ipc-stress.log` preserves the original failure; `debug-symbols/ipc-debug-fault.json`
preserves the symbolized fault; `ipc-stress-fixed.log` and
`ipc-stress-summary.json` record the successful rerun. Final local full workspace
tests, hosted Windows tests and packaged runtime interaction also passed.

### Native Windows business observations

The actual optimized package was launched with `SLINT_BACKEND=winit-software`,
no scale override, from the empty runtime working directory described above.
GUI input used selected native windows. Screenshot/accessibility records are in
`native-interaction/`; process snapshots and PID records are in the evidence
root. Interactive actions have observed outcomes rather than shell exit codes.

| Spec scenario | Observed result / evidence |
|---|---|
| Main / companion startup away from source cwd | PASS; standalone Quick Add bootstrapped Agent, Main later connected; Main also rendered after original build source/cache paths were unavailable; `package-source-cache-offline-main` |
| Minimize and restore | PASS; same Main window and layout restored; `main-restored-same-layout` |
| Close to tray ON | PASS for GUI release and resident Focus: only Agent remained, reopening Main by CLI showed the same running task at 05:53; `close-to-tray-processes.json`, `focus-survives-gui-close`. Actual reminder notification delivery was not observed |
| Close to tray OFF | PASS; settings persisted, native Close ended both GUI and Agent without a process kill; `close-to-tray-disabled`, `full-exit-processes.json` (0 remaining processes) |
| Actual tray reopen / Exit | NOT VERIFIED; native automation could not target the Windows system tray. Manual assistance was requested but no result received. CLI reopening above is not tray-click evidence |
| Standalone / repeated Quick Add | PASS; no forced Main, second CLI request exited 0 and activated the same window with its draft; `quick-add-repeat.log`, `quick-add-processes.json` |
| Main and standalone Quick Add together | PASS; both displayed and interacted; Dark theme reached the existing draft window; `main-quickadd-coexist`, `quickadd-dark-draft-retained` |
| Editor creation / release / reopen | PASS; created on demand, Escape released it, reopening discarded unsaved notes; `editor-created-dark`, `editor-unsaved-notes`, `editor-reopened-cancel-discards` |
| Save / Cancel / Escape | PASS; Enter captured once into Inbox; Editor Save closed and updated the planned date; Quick Add Escape discarded its draft, reopened empty, Cancel released it; `quickadd-saved-inbox`, `today-planned-task`, `quickadd-reopened-empty` |
| Failed save / disconnect | PASS; temporary write lock in the isolated database produced visible save error with draft retained; stopping only the isolated Agent produced a visible disconnected error and disabled Save; `editor-save-failed-retains-form`, `editor-disconnected-retains-form` |
| Unconfirmed edits | PASS; after bounded reconnect attempts expired, UI instructed explicit reopen; failed Q2 change was not replayed automatically. Reopened task was still in Inbox; `reconnect-exhausted-no-replay` |
| Business views | PASS; Inbox capture, Q2 classification, Today planning, Focus start/finish, Review session history, Completed and Restore were exercised through the real Agent. Follow-up Move actions traversed Q1, Q3 and Q4 with counts updated and the same task retained; `task-moved-q1`, `task-moved-q3`, `task-moved-q4` |
| Light / Dark / System | PASS for observed switching/new windows, existing Quick Add draft and native date picker; `main-light`, `main-dark`, `std-datepicker-dark`, `system-theme-settings` |
| Package static resources | PASS for visible Main/sidebar/task/date-picker icons while original source/cache paths were unavailable |
| Data and identity | Isolated profile used the original `quadrant-rust.db` name and current IPC derivation. Identity constants and product contracts are unchanged; no real user profile was modified |

An additional visual observation in the Focus view was that its right-side
settings fields extended beyond the visible content area at the tested window
size (`focus-started`). Commit `6db63abeb2a0ecca24762e0cc270948441ad8c38` replaces
the forced 320px panel width with a preferred width and zero horizontal stretch,
allowing the layout's actual minimum width to contain both input columns. No
timer, settings, model or callback semantics changed. The native probe now
accepts an optional third `focus` argument; Windows CI captures this view in
both themes. Package validation also runs for Product UI changes.

The corrected native Focus capture (`focus-layout-candidate/main.png`) and
Light/Dark captures at simulated 200% / 225% (`focus-scale-*/main.png`) were
visually inspected: all four settings fields and Save remain inside the card.
These captures use `product_windows_probe.exe <output> <light|dark> focus` from
the Tasks root, Windows Rust 1.94.1, winit/software, exit 0. The four scaled runs
set `SLINT_SCALE_FACTOR=2` or `2.25`; they are not physical DPI tests.

### Scaling evidence and remaining native acceptance

The original Kit native smoke entry point produced an approved-SHA Controls
capture at 1040x800 / 100%. Gallery native keyboard Tab focus and Space theme
activation were also exercised. `kit-native-smoke.log` and `kit-native/` retain
the deterministic capture and metadata.

`python target/phase5/capture_scale_probes.py` ran eight native winit/software
processes with `SLINT_SCALE_FACTOR=2` or `2.25`: Light/Dark Gallery plus Product
Main, Quick Add and Task Editor. All exited 0. All **16 PNGs were visually
inspected**, along with the original Kit smoke PNG. Captured regions have
readable text/icons, aligned controls and coherent colors; Gallery and Editor
use their expected scroll areas. `scale-probes/manifest.json` records commands,
working directories, scale type, binary/image hashes and physical pixel sizes;
`visual-review.json` records the review scope. These synthetic Product probes
do not use Agent/IPC and are separate from the real package business tests.

These are **programmatic scale simulations**, not physical display DPI evidence.
The current Windows desktop exposes one usable 1920x1080 display
(`display-layout.json`). Cross-screen movement could not be run. System display
settings were not changed.

To close Gate 5, use the preserved isolated package/profile and record:

1. Enable Close to tray, close Main, click the actual tray icon to reopen Main,
   then choose actual tray Exit and confirm both package processes terminate.
   The earlier test processes have now fully exited; the previous pending
   manual tray prompt no longer describes a running test instance.
2. Verify a scheduled reminder while Main is released, including visible native
   delivery. The normally ignored notification smoke was separately executed
   with `cargo test --locked -p quadrant-platform native_windows_notification_smoke_test -- --ignored --exact notifications::tests::native_windows_notification_smoke_test`
   from the Tasks root on Windows/Rust 1.94.1: exit 0, one test passed
   (`notification-smoke.log`). The notification API accepted the submission;
   no notification window was available to the native window observer. This
   does not establish visible scheduled delivery while the GUI is closed.
3. Use real 200% / 225% display settings and move Main, Quick Add and Editor
   across displays; capture the display configuration and before/after views.

No master merge, release publication or physical workspace relocation is part
of this Phase 5 checkpoint.

### Final implementation checkpoint

Final code is `6db63abeb2a0ecca24762e0cc270948441ad8c38`; its only production
difference from the fully exercised `22fb670` package is the Focus panel layout
correction above. The fresh remote Tasks checkout was fast-forwarded to this
SHA, rebuilt with the original Windows packaging entry point, and the new
archive passed verification. The rebuilt local ZIP SHA-256 is
`c44819185a01240a608307b08db12b560cc9243b75b24b64c78734c86fd8b095`.

Both new executables were extracted together, the build checkout/cache paths
were again made unavailable, and the actual package bootstrapped Agent from the
empty working directory. Focus's four input fields fit within the card; clicking
Save displayed `Pomodoro settings saved.` Closing Main with Close to tray OFF
again ended both processes. Evidence: `tasks-clean-package-focus.log`,
`windows-clean-package-focus.json`, `final-runtime.json`,
`native-interaction/final-package-*` and `focus-visual-review.json`. The prior
runtime executable pair is retained separately for diagnostic comparison.

[Final package CI 34009907575](https://github.com/wadaxiyang/Quadrant-Tasks/actions/runs/34009907575)
passed all three native platforms at this exact SHA. All three downloaded
archives match their report and sidecar checksums; records are in
`package-ci-focus.{json,log}`, `ci-packages-6db63ab/` and
`final-package-downloads.json`.

[Final code CI 34009907582](https://github.com/wadaxiyang/Quadrant-Tasks/actions/runs/34009907582)
also passed all four jobs at exactly `6db63ab`: Linux quality, native Windows,
native macOS and actual Windows Rust 1.92.0. Both native workspace test runs,
all-targets checks, debug binaries and the additional Windows Focus captures
completed successfully. Full results are retained in `code-ci-focus.{json,log}`
and `ci-native-6db63ab/`. Subsequent ledger commits contain only this record.

The remaining Gate 5 native manual items listed above are still open; neither
this corrective checkpoint nor the passing package jobs marks Gate 5 complete.

## Phase 6 — physical workspace preparation (2026-09-06)

The user requested physical workspace organization while the recorded Phase 5
manual items remain open. Those items are carried forward; Phase 6 is not an
override of final migration acceptance.

Added `scripts/bootstrap_workspace.py`, versioned non-active templates,
`docs/WORKSPACE.md` and reviewed Tasks `AGENTS.md`. The bootstrap defaults to
dry-run and only creates missing parent coordination files with exclusive file
creation. Existing notes/settings are preserved. It validates both independent
Git roots, rejects linked output paths and ancestor Git/Cargo workspaces, and
does not move repositories, initialize Git or commit. The generated editor
workspace contains relative child paths. Public migration records now use role
labels instead of private absolute verification paths; exact paths remain in
private command evidence.

Local Windows verification: `python -m unittest discover -s scripts/tests -v`
ran 33 tests, 32 passed and one symbolic-link fixture skipped because the host
lacks symlink creation privilege. `python scripts/check_ui_boundaries.py` and
`git diff --check` pass. The eight new filesystem/Git fixtures cover dry-run,
creation without repository mutation, preservation of existing notes, missing
repositories, forbidden ancestors, conflicting output directories/parents and
linked output rejection. Native Unix CI supplies the symlink-capable execution.

The pre-move checkpoint records each repository's HEAD, branch, remotes, tags,
history, Git metadata form and status, plus target conflicts, available space
and observed running binaries. Both are ordinary checkouts with `.git`
directories. Full-repository movement will run from their external parent;
an active-session lock must produce `LAYOUT_PENDING`, not a forced copy or
reinitialized repository. Final movement/build results are recorded separately
after execution; preparation alone does not establish Gate 6.

### Bootstrap platform corrections

The first hosted run exposed two real platform path differences: macOS's
standard `/var` ancestor alias and Windows's short temporary-directory name.
Bootstrap now canonicalizes ancestor aliases before checking repository and
ancestor ownership, while still rejecting a linked workspace root, child root
or output path. The Windows fixture compares against the canonical path rather
than its short spelling. A ninth bootstrap fixture verifies an ancestor alias
resolves to the intended, verified directory without writing in dry-run mode.

At `da4d6741f4ea965491f6e25326391ecce410997f`, local Windows Python validation
runs 34 tests: 32 passed, two actual symlink fixtures skipped for host privilege.
The normal Git/ownership checks are retained; no platform-wide safety bypass was
introduced. Exact logs are in private `target/phase6/`.

### Initial physical relocation attempt (superseded below)

**Gate 6: LAYOUT_PENDING.** Windows rejected the first complete-directory move
before any path changed. After external editors/terminal handles were released,
a second attempt from the external parent was also rejected. Read-only native
handle inspection found remaining old-root directory handles in Codex's Node
helpers. Resetting the two REPL kernels did not release those process-level
handles. No application was forcibly terminated and no remote handle was closed.

Both original repository paths remain intact, including their `.git` directories;
neither the unique temporary path nor the final child paths exists. No partial
copy, replacement Git repository, parent Git/Cargo workspace or dependency
override was created. There is consequently **no claim of builds from the new
paths** and no claim that the final physical layout or parent bootstrap ran.

Private evidence retains the first attempt and updated preflight snapshots,
failure stage/path state, read-only handle inspection, and verified full-history
bundles for both repositories. The local `PHASE6_RESUME.md` gives exact paths and
commands. The reviewed `complete-phase6.ps1` defaults to a preflight preview;
with explicit `-Apply`, it invokes the complete-directory mover, compares Git
invariants, runs bootstrap preview/apply, then each repository's boundary guard
and role build. It checks every native exit code and leaves the Phase 5 manual
items open. It never commits or pushes.

To resume, save and exit sessions that hold the old directory (including the
Codex session's helpers), then run that local script from an external PowerShell.
Do not rerun blindly after a partial move: inspect the recorded stage and follow
the stage-specific recovery instructions. After successful relocation, open the
generated relative-path `Quadrant.code-workspace` or the intended child Git root.
The saved parent project path becomes coordination, not the Tasks Git root.

[Phase 6 tool checkpoint CI 34011358631](https://github.com/wadaxiyang/Quadrant-Tasks/actions/runs/34011358631)
passed all four jobs at exactly `da4d6741f4ea965491f6e25326391ecce410997f`:
Linux quality, native Windows, native macOS and actual Rust 1.92.0. All three
platforms ran the 34 Python tests successfully, including real symbolic-link
fixtures on the hosted runners. This validates the committed bootstrap/tooling;
it does not substitute for the blocked new-path builds. The final delivery
checkpoint adds only this evidence and the layout status record. Kit's checkout
remains clean and unchanged at `838ecfbead2d0a1966907ddd742cb6f34516d3f6` on
`codex/extraction-candidate`.

### Completed relocation and new-path acceptance

The user ran the reviewed mover from an external PowerShell after releasing
the old directory handles. It moved both entire repositories, including Git
metadata and ignored evidence, into the final child roots. No replacement
repository, copied source tree or dependency override was created. The parent
has no `.git` or `Cargo.toml`, its ancestors have no Git/Cargo ownership, and
the old Kit and unique intermediate paths are absent.

The initial completion script then stopped on Cargo's ordinary `Compiling`
stderr output: Windows PowerShell 5.1 promoted redirected native stderr into
`NativeCommandError` under `ErrorActionPreference=Stop`. This was a script
failure, not a Rust compiler failure. The private runner now captures native
stdout/stderr directly through Python's subprocess API and checks the actual
exit code. A `-ValidateOnly` entry verifies the recorded complete relocation
and current Git identity before running checks, without invoking any move.
PowerShell 5.1 regression cases pass for stderr with exit 0, captured streams,
paths/arguments with spaces, rejection of exit 7, and a missing executable.

The resumed Gallery build exposed a separate stale-cache failure: the moved
Kit rlibs embedded the former `CARGO_MANIFEST_DIR`, and Gallery reported
`Kit facade is missing`. The old root was confirmed in the cached libraries.
Targeted `cargo clean -p quadrant-kit -p quadrant-kit-gallery` removed those
packages' generated artifacts, then the locked Gallery build passed. Kit
source, dependency cache and historical QA evidence were preserved. Both
initial failures and their logs are retained in private relocation evidence.

The acceptance checks ran at these exact revisions before this ledger-only
record was added:

| Repository | HEAD | Branch |
|---|---|---|
| Tasks | `d9b8b57a66271e2dc1db9b9a215c8cc1c5962456` | `codex/kit-product-cutover` |
| Kit | `838ecfbead2d0a1966907ddd742cb6f34516d3f6` | `codex/extraction-candidate` |

| New-root check | Result |
|---|---|
| Before/after/current HEAD, branch, remotes, refs/tags, history, status and shallow state, independently for both repositories | PASS, exact match before and after builds; both clean |
| True independent Git roots; no parent/ancestor Git or Cargo workspace | PASS |
| Tasks bootstrap preview and apply | PASS; four existing coordination files kept, editor paths relative |
| Tasks `python scripts/check_ui_boundaries.py` | PASS; resolved Kit is the pinned public Git package |
| Tasks `cargo build --locked -p quadrant-agent -p quadrant-app` | PASS |
| Kit `python scripts/check_ui_boundaries.py` | PASS |
| Kit `cargo build --locked -p quadrant-kit-gallery` | PASS after targeted cache cleanup |

**Gate 6: PASS.** Private `phase6-layout/` retains the move snapshots,
`validated-git.json`, per-command logs, native-runner regression results and
`completion.json`; local coordination notes and recovery instructions were
updated. Exact machine paths and recovery scripts stay outside both public
repositories. The bootstrap/tooling CI result above remains tied to `da4d674`;
this follow-up does not claim a new full platform run or new native GUI tests.

Gate 5 remains open for actual system-tray reopen/Exit, visibly delivered
scheduled reminders while the GUI is closed, and physical 200%/225% DPI plus
cross-display movement. Overall migration remains **IN_PROGRESS**, and Phase 7
is **NOT_STARTED**. The physical move and passing builds do not waive these
remaining acceptance items.
