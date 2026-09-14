# Status — 2026-09-14

**Phase:** v1.26.0 shipped and published; nothing unreleased on `main`
**Session by:** Claude Code · Opus 5 (1M context) (`claude-opus-5[1m]`) — review, fixes and both releases. The two rounds of skill work were written in another session whose assistant is not recorded (see "Known pending").
**Deployed:** `@maccesar/aiskills@1.26.0` is `latest` on npm, published by `publish.yml` over OIDC (run 34876990721, green). Tag `v1.26.0`, the GitHub Release and the release commit all point at `08a9163`. v1.25.0 shipped earlier the same day at `9f0d20f`. The maintainer's Claude marketplace cache has **not** been refreshed — see "Next step".
**Branch:** `main`, level with `origin/main` at the release commit, plus this note's own commit.
**Sibling:** `../TiTools` — not touched, and no port is owed. Both releases change AISkills payload only (`laravel-security-sweep`, `release`, `session-log`); no shared CLI CORE behavior moved.

## Where things stand

Two releases today, both about `laravel-security-sweep`.

**v1.25.0** added the skill: a one-agent security review for Laravel 8–13 where `scripts/barrido_laravel.py` does the mechanical part without tokens and the agent reads only the matches. The same release shipped `release` closing its own session note and `session-log` offering to commit `docs/project/`.

**v1.26.0** is the round from a first real run on a second production system (Laravel 12). Its worst issue sat outside every pattern — a server key printed into a public page's JavaScript — so `SECRET-IN-VIEW` now catches that shape, `THROTTLE-SHARED` warns about routes sharing one `throttle:N,1` counter, `SECRET-FALLBACK` no longer flags the stock `AUTH_PASSWORD_BROKER` / `AUTH_PASSWORD_RESET_TOKEN_TABLE` names, and stage 1 has a reads-only rule for live servers. The sweep runs 18 line patterns and 7 project-level checks.

Review of that round before committing found and fixed:

- The stock-name exclusion matched substrings, so `PORT` silently dropped `REPORT_API_KEY` and `PASSPORT_CLIENT_SECRET` (and `STORE` dropped `KEYSTORE_PASSWORD`). It now matches whole underscore-separated segments, pinned by a regression test.
- The round's notes had been written into the already-published `[1.25.0]` CHANGELOG section, changing its counts. That section was restored byte-for-byte to the tag and the notes moved to what became `[1.26.0]`.
- Two `SECRET-IN-VIEW` false positives the catalog did not cover: `window.csrfToken`, and `@js($manualSetupKey)` in the Livewire starter kit's 2FA view (present in at least four local projects).
- The README scope list gained the live-server rule.

## Next step

Refresh the maintainer's own channels — `/plugin marketplace update maccesar-aiskills`, then `aiskills install`, then `/reload-plugins`. Neither channel picks up a release on its own.

## Verified vs. assumed

- **Verified:** 166/166 tests pass locally before the release commit; `publish.yml` passed its tag-vs-both-version-files guard and `npm test`, and logged `+ @maccesar/aiskills@1.26.0`.
- **Verified:** `npm view @maccesar/aiskills dist-tags.latest` returns `1.26.0` (it lagged about four minutes behind the green run).
- **Verified:** the GitHub Release exists at `releases/tag/v1.26.0` with the CHANGELOG section as notes; `git diff v1.25.0 -- CHANGELOG.md` before the promotion showed additions only.
- **Verified:** control run — the fixed script on codigomovil's pre-fix snapshot `785d53e` still flags both `DOWNLOAD_SECRET` fallbacks; current codigomovil, Cronica-Social, cbtis7 and cymez-documentacion sweep with exit 0.
- **Verified against Laravel 13.26.1 source** (`cymez-documentacion/vendor`): `throttle:N,1` keys on user id or `domain|ip` with no route; named limiters prefix the limiter name; `SetRequestForConsole` builds the worker's request from `config('app.url')`.
- **Not checked from here:** the SNAP figures quoted by the authoring session (3 `SECRET-IN-VIEW` lines, 29 `throttle:N,1` uses, `SECRET-FALLBACK` 3 → 0).
- **Verified by the maintainer, not from here:** the skill auto-invoked from "Ahora hay que hacer una auditoría de seguridad del proyecto en Laravel". One prompt, not a trigger measurement; no eval against `audit-codebase` was run.

## Known pending

- **Attribution gap:** the session that wrote both rounds of `laravel-security-sweep` left no transcript under this project's Claude Code directory. `context.md` records it as "Not recorded"; if the maintainer knows which tool wrote it, correct that row.
- Third-party Claude marketplaces do not auto-update unless the maintainer enables it; refresh manually with the sequence above.
