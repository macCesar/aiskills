# Status — 2026-09-26

**Phase:** 1.27.0 committed on `main`, not tagged, not pushed, not published. npm `latest` is still 1.26.1.
**Session by:** Claude Code · Opus 5.5 (`claude-opus-5-5`) for `handoff` and the commits; `store-screenshots` was written by an earlier session (2026-09-16, notes below).
**Branch:** `main`, 6 commits ahead of `origin/main` (`dffb004`..this note).

## What 1.27.0 carries

- `store-screenshots` (`0bdc45e`): app-specific store artwork, real Android/iOS captures, editable SVG masters, `scripts/artwork.py` for RGB PNG export and checks. Verified by its session: skill-creator validator, targeted ESLint, a real NotiGAPE SVG export at 1284 × 2778. Not yet used on a real project; new simulator/emulator captures were never run.
- `handoff` (`67f1a4a`): explicit-only skill that writes a disposable `HANDOFF.md` before a `/clear`. One eval round in a scratch workspace, one run per case against a no-skill baseline: 21/21 assertions with the skill, 16/21 without; the difference is the reader header (resuming session deleted the file only when the header told it to). Not yet used in a real session.
- `session-log` was changed and then reverted in the same session: its `status.md` stays short and permanent; failed attempts belong in `HANDOFF.md`.
- Also committed: the `@.claude/memory/index.md` import in `CLAUDE.md` (`dffb004`), both version fields at 1.27.0 (`04a7145`), and root screenshots ignored (`07f5f70`).

## Next step

César uses `/handoff` and `store-screenshots` on real work, then runs `/release` for 1.27.0, which tags, pushes and lets `publish.yml` publish. Run `aiskills update` first so `handoff` gets its symlink.

## Verified vs. assumed

- Verified 2026-09-26: `npm test` 179/179; `git status` clean except this file before its commit; `git log @{u}..HEAD` shows 5 commits.
- Open: `.claude/` is in `.gitignore`, so the `@.claude/memory/index.md` import in `CLAUDE.md` resolves only on this machine; a clone gets a dangling import.

## Previous published state

# Status — 2026-09-14

**Phase:** v1.26.1 shipped and published; nothing unreleased on `main`
**Session by:** Claude Code · Opus 5 (1M context) (`claude-opus-5[1m]`) — review, fixes and the three releases. The skill work was written by another Claude Code · Opus 5 session (`e5b2d76f`) run from the `LM - La Baraja` directory, which is why its transcript is not under this project.
**Deployed:** `@maccesar/aiskills@1.26.1` is `latest` on npm, published by `publish.yml` over OIDC (run 34893977418, green). Tag `v1.26.1`, the GitHub Release and the release commit all point at `8f78ff7`. Earlier the same day: v1.25.0 at `9f0d20f`, v1.26.0 at `08a9163`.
**Branch:** `main`, level with `origin/main`; the release is followed by two `docs(project)` commits, the second of which carries this file.
**Sibling:** `../TiTools` — one local commit, `2e7e98b`, carries the same `CLAUDE.md` correction about the maintainer's `npm link` setup; it is **not pushed**. No port is owed for the releases: they change AISkills payload only.

## Where things stand

Three releases today, all about `laravel-security-sweep`.

**v1.25.0** added the skill: a one-agent security review for Laravel 8–13 where `scripts/barrido_laravel.py` does the mechanical part without tokens and the agent reads only the matches. The same release shipped `release` closing its own session note and `session-log` offering to commit `docs/project/`.

**v1.26.0** is the round from a first real run on a second production system (Laravel 12). Its worst issue sat outside every pattern — a server key printed into a public page's JavaScript — so `SECRET-IN-VIEW` catches that shape, `THROTTLE-SHARED` warns about routes sharing one `throttle:N,1` counter, `SECRET-FALLBACK` no longer flags the stock `AUTH_PASSWORD_BROKER` / `AUTH_PASSWORD_RESET_TOKEN_TABLE` names, and stage 1 has a reads-only rule for live servers. The sweep runs 18 line patterns and 7 project-level checks. Review before committing fixed a substring exclusion that dropped `REPORT_API_KEY` and `PASSPORT_CLIENT_SECRET`, added two `SECRET-IN-VIEW` discards (`window.csrfToken`, the Livewire starter kit's 2FA setup key), and moved notes out of the published `[1.25.0]` CHANGELOG section.

**v1.26.1** fixes the catalog's own `SSRF` advice: validating the resolved IP is not enough when the HTTP client resolves the host again (DNS rebinding). The section now pins the validated address with `CURLOPT_RESOLVE` (IPv6 in brackets), replaces the `on_redirect` advice — which had the same gap — with disabling redirects or following them by hand, and explains why a reused connection makes a pin look broken in a test. Its notes had also been written into a published section (`[1.26.0]`) and were moved out before release.

Also on `main` since v1.26.0: `CLAUDE.md` now says the maintainer runs `npm link` and has no marketplace plugin, so post-release advice must not tell him to refresh the marketplace; and `context.md` attributes the skill to its real session and says to search every project's transcripts before writing "not recorded".

## Next step

Push TiTools' `2e7e98b` if the maintainer wants it upstream. Nothing to refresh on this machine: the CLI is `npm link`-ed and the skills are symlinks into the checkout.

## Verified vs. assumed

- **Verified:** 166/166 tests pass locally before each release commit; `publish.yml` passed its tag-vs-both-version-files guard and `npm test`, and logged `+ @maccesar/aiskills@1.26.1`.
- **Verified:** `npm view @maccesar/aiskills dist-tags.latest` returns `1.26.1` (about four minutes behind the green run, as with v1.26.0).
- **Verified:** the GitHub Release exists at `releases/tag/v1.26.1` with the CHANGELOG section as notes; before each promotion today, `git diff <previous tag> -- CHANGELOG.md` showed additions only.
- **Verified:** control run — the v1.26.0 script on codigomovil's pre-fix snapshot `785d53e` still flags both `DOWNLOAD_SECRET` fallbacks; current codigomovil, Cronica-Social, cbtis7 and cymez-documentacion sweep with exit 0.
- **Verified against Laravel 13.26.1 source** (`cymez-documentacion/vendor`): `throttle:N,1` keys on user id or `domain|ip` with no route; named limiters prefix the limiter name; `SetRequestForConsole` builds the worker's request from `config('app.url')`.
- **Verified against `man curl`:** the `host:port:addr` format of `--resolve` / `CURLOPT_RESOLVE`, and bracketed addresses from curl 7.57.0.
- **Verified:** attribution — among today's transcripts, the phrases the skill rounds introduced occur only in this session and in `~/.claude/projects/-Users-cesar-Developer-Apps-LM---La-Baraja/e5b2d76f…`, whose `Write` calls created the skill files; model `claude-opus-5`.
- **Not checked from here:** the SNAP figures quoted by the authoring session (3 `SECRET-IN-VIEW` lines, 29 `throttle:N,1` uses, `SECRET-FALLBACK` 3 → 0), and the Guzzle 7.9 pinning test the `SSRF` section cites.
- **Verified by the maintainer, not from here:** the skill auto-invoked from "Ahora hay que hacer una auditoría de seguridad del proyecto en Laravel". One prompt, not a trigger measurement; no eval against `audit-codebase` was run.
