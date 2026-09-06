# Quadrant Workspace

This is local coordination, not a Git repository or a Cargo workspace.

- Use Quadrant-Kit for generic Slint controls, tokens, assets and Gallery.
- Use Quadrant-Tasks for business pages, domain, storage, IPC, Agent and GUI hosts.
- Read the affected child repository's AGENTS.md before editing. Each child must
  work independently; do not assume parent instructions load from a child Git root.
- Tasks consumes the published Kit Git URL at a reviewed full SHA. Never introduce
  sibling path consumption, local patches, copied Kit code or a parent Cargo workspace.
- Kit Gallery's path dependency inside its own repository is allowed.
- Inspect HEAD, branch, status and remotes separately; keep one writer per checkout.
- Commit separately, preserve user work and published history, and keep machine
  paths and private notes out of both repositories.
- Canonical contracts and build rules live in the child repositories. Report
  missing verification explicitly; never equate directory relocation with full acceptance.
