# Kit extraction v2 — migration ledger

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
