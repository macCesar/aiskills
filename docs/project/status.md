# Status — 2026-09-26

**Phase:** v1.27.0 shipped and published; nothing unreleased on `main`
**Session by:** Claude Code · Opus 5.5 (`claude-opus-5-5`) — `handoff`, the commits for the pending tree, and the release. `store-screenshots` came from a Codex session (see `context.md`).
**Deployed:** `@maccesar/aiskills@1.27.0` is `latest` on npm (checked against registry.npmjs.org), published by `publish.yml` over OIDC with provenance (run 36287165067, green). Tag `v1.27.0`, the GitHub Release and the release commit all point at `5b13794`.
**Branch:** `main`, level with `origin/main` (`39f432c` and this note pushed together).

## Where things stand

v1.27.0 adds two skills:

- `store-screenshots`: app-specific store artwork, real Android/iOS captures, editable SVG masters, and `scripts/artwork.py` for opaque RGB PNG export and checks.
- `handoff`: explicit-only; writes a disposable `HANDOFF.md` before a `/clear`, with a reader header (HEAD sha, check it against the repo, delete it after reading). `session-log` keeps the permanent record; a change that would have put failed attempts into `status.md` was tried and reverted in the same session.

The same release ignores screenshots at the repo root. After it, `39f432c` removed the `@.claude/memory/index.md` import from `CLAUDE.md`: `.claude/` is gitignored and the memory it loaded was stale (manual `npm publish` with 2FA, an April marketplace branch). The local memory was deleted; the one rule still current (don't suggest a new session on low context) now lives in the maintainer's global instructions.

## Next step

César uses `/handoff` and `store-screenshots` on real work; findings from that use are the next round for both skills. Run `aiskills update` so `handoff` gets its symlink under `~/.agents/skills/`.

## Verified vs. assumed

- Verified 2026-09-26: `npm test` 179/179 before the release commit; `publish.yml` run green and its log shows `+ @maccesar/aiskills@1.27.0`; registry `latest` is 1.27.0 (it lagged about 90 s behind the run).
- `handoff`: one eval round in a scratch workspace, 21/21 assertions with the skill vs 16/21 without, one run per case. Not yet used in a real session.
- `store-screenshots`: verified by its session with a real NotiGAPE SVG export; new simulator/emulator captures never ran.

## Known pending

- `store-screenshots` has a row in the README table but no section of its own, unlike the other skills.
