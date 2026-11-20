# Status — 2026-11-20

**Phase:** v1.30.1 published and verified. **Session by:** Codex · GPT-6. **Branch:** main.

## Result

- `89b73a3` updates `session-log` so Codex creates a root `AGENTS.md` with links to the session docs when setting them up or reconnecting them. The instructions cover projects with preliminary files, docs already present, and an existing `AGENTS.md` whose other instructions must be preserved. `status.md` remains a reference for resuming work.
- The README and layout reference document the same behavior. The maintainer's development symlink resolves to the updated skill and reference.

## Publication

- The annotated `v1.30.1` tag points to `d17f3de1229ca88e24f6699389b3da2ab4662599`. The public GitHub release title and notes match the approved text. https://github.com/macCesar/aiskills/releases/tag/v1.30.1
- GitHub Actions verified the versions and passed `npm ci`, `npm test`, and `npm publish` through trusted publishing. https://github.com/macCesar/aiskills/actions/runs/44835147961
- npm serves `@maccesar/aiskills@1.30.1` as `latest` with registry timestamp `2026-11-20T23:15:06.082Z`. The registry metadata matches the tagged commit and the package SHA-1 logged by the workflow. Once the public archive became available, its SHA-512 integrity, package version, README, and both updated skill files matched the release. The archive excludes `docs/project/`.
- The marketplace manifest on `main` reports `1.30.1`, matching both npm manifests and the tag.

## Verification and scope

- `npm test`: 222 tests passed. `git diff --check` passed. A fresh Codex session has yet to exercise creation of `AGENTS.md` end to end.
- Shared engine parity: **product-specific exception**. The change is confined to the AISkills `session-log` skill and its documentation. The TiTools skill catalog has no `session-log` counterpart.

## Next step

Release verification is complete.
