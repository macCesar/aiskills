# Status — 2026-09-14

**Phase:** v1.25.0 shipped and published; nothing unreleased on `main`
**Session by:** Claude Code · Opus 5 (1M context) (`claude-opus-5[1m]`) — registration review and release. The skill itself was written in an earlier session whose assistant is not recorded (see "Known pending").
**Deployed:** `@maccesar/aiskills@1.25.0` is `latest` on npm, published by `publish.yml` over OIDC with provenance (run 34872333300, green in 17s). Tag `v1.25.0`, the GitHub Release and the release commit all point at `9f0d20f`. The maintainer's Claude marketplace cache has **not** been refreshed — see "Next step".
**Branch:** `main`, level with `origin/main` at the release commit, plus this note's own commit.
**Sibling:** `../TiTools` — not touched, and no port is owed. The release adds payload (`laravel-security-sweep`) and changes two AISkills-only skills (`release`, `session-log`); adding a name to `lib/config.js:SKILLS` is this repo's own manifest, not shared CORE behavior.

## Where things stand

v1.25.0 ships two things that sat under `[Unreleased]`.

`laravel-security-sweep` is a one-agent security review for Laravel 8–13. `scripts/barrido_laravel.py` does the mechanical part without tokens (version and structure detection, `composer audit --no-plugins`, 17 line patterns and 6 project checks); the agent reads only the matches and reports confirmed findings with `file:line`, and fixes wait for approval. Its `allowed-tools` excludes `Agent`, and a test guards that.

`release` now closes its own session note (Step 1.11, a line in the Step 4 plan, Phase 6), and `session-log` offers to commit the files it writes under `docs/project/` instead of leaving them dirty. This note is the first one written by that Phase 6.

Before the release, the README gained the two things the diff had left undocumented: step 7 in `release` → "How it works", and a corrected first bullet in `session-log` → "What it will not do", which still said the skill never commits. The "Available skills" table was realigned for the longer skill name.

## Next step

Refresh the maintainer's own channels — `/plugin marketplace update maccesar-aiskills`, then `aiskills install`, then `/reload-plugins`. Until then the marketplace copy lacks `laravel-security-sweep`; the npm-linked copy under `~/.claude/skills/` already has it.

## Verified vs. assumed

- **Verified:** 162/162 tests pass locally before the release commit; `publish.yml` ran `npm test` again and its tag-vs-both-version-files guard passed.
- **Verified:** `npm view @maccesar/aiskills dist-tags.latest` returns `1.25.0` (it lagged about a minute behind the green run).
- **Verified:** the GitHub Release exists at `releases/tag/v1.25.0` with the CHANGELOG section as notes.
- **Verified:** `aiskills list` shows `laravel-security-sweep`; `aiskills --help` enumerates no skills, so it needed no change.
- **Verified by the maintainer, not from here:** the skill auto-invoked from "Ahora hay que hacer una auditoría de seguridad del proyecto en Laravel" and loaded `references/patterns.md`. One prompt, not a trigger measurement.
- **Not checked:** whether that run produced a full report that includes the script output — the transcript shown ended at the reference read.
- **Assumed:** no conflict with `audit-codebase`, whose description also matches "security review". The single prompt above picked the sweep; no eval was run.

## Known pending

- **Attribution gap:** `context.md` records the release row, but the session that wrote `laravel-security-sweep` left no trace here — no Claude Code transcript under this project contains its authoring, and the commit `b98658e` carries this session's trailer only because this session committed it. If the maintainer knows which tool wrote it, add it to the table.
- Third-party Claude marketplaces do not auto-update unless the maintainer enables it; refresh manually with the sequence above.
