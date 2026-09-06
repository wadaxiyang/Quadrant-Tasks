# Local migration status

Generated checkpoint; verify current refs before resuming work.

- Workspace: `{{WORKSPACE_ROOT}}`
- Tasks HEAD: `{{TASKS_HEAD}}`
- Tasks branch: `{{TASKS_BRANCH}}`
- Kit HEAD: `{{KIT_HEAD}}`
- Kit branch: `{{KIT_BRANCH}}`
- Layout: child Git roots verified by bootstrap.
- Gate 6: IN_PROGRESS until Git invariants and builds from the new paths pass.
- Overall migration: IN_PROGRESS; bootstrap does not establish any acceptance gate.

Carry forward all open checks from the public migration ledger. In particular,
directory relocation does not close Phase 5 native manual verification items.
Record local commands, outcomes, evidence locations and any exact recovery steps
here after execution. This file is not the only copy of architectural rules.
