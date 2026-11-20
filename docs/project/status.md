# Status — 2026-11-20

**Phase:** Preparing v1.30.1. **Session by:** Codex · GPT-6. **Branch:** main.

## Result

- `89b73a3` updates `session-log` so Codex creates a root `AGENTS.md` with links to the session docs when setting them up or reconnecting them. The instructions cover projects with preliminary files, docs already present, and an existing `AGENTS.md` whose other instructions must be preserved. `status.md` remains a reference for resuming work.
- The README and layout reference document the same behavior. The maintainer's development symlink resolves to the updated skill and reference.

## Publication

- The previous release, `v1.30.0`, shipped `articulos-de-blog`. Its verified publication is recorded in `4c2c747`.
- The `v1.30.1` release plan and notes are pending approval.

## Verification and scope

- `npm test`: 222 tests passed. `git diff --check` passed. A fresh Codex session has yet to exercise creation of `AGENTS.md` end to end.
- Shared engine parity: **product-specific exception**. The change is confined to the AISkills `session-log` skill and its documentation. The TiTools skill catalog has no `session-log` counterpart.

## Next step

After approval, publish `v1.30.1`, verify GitHub, npm and the marketplace manifest, and record the results here.
