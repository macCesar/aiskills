# Status — 2026-10-24

**Phase:** v1.28.1 published and verified; shared engine parity complete.
**Session:** Codex / GPT-6. **Branch:** main.

## Release

- a9924cb — fix(cli): correct cache namespace and removal scopes.
- e75bf04 — test(cli): port shared engine regression coverage.
- 09ac2c0 — docs(engine): enforce bidirectional parity completion gate.
- 56d89d0 — chore(release): v1.28.1.

Release commit: 56d89d0e0a85988122a548deb48f51dcf856c525. Annotated tag v1.28.1 and main targets were
verified on origin. Package, root lockfile/lockfile package entry and plugin
versions are synchronized at 1.28.1.

- GitHub release: https://github.com/macCesar/aiskills/releases/tag/v1.28.1
- Successful OIDC publishing run: https://github.com/macCesar/aiskills/actions/runs/40131025241
- Public main plugin.json version independently verified as 1.28.1.
- Direct registry metadata confirms @maccesar/aiskills@1.28.1 and latest=1.28.1;
  registry publication time 2026-10-24T20:44:32.932Z. Initial CLI/direct queries lagged
  behind the successful workflow; verification continued until they converged.
- Downloaded the registry tarball and verified its advertised integrity, package
  version and shipped core corrections. It contains 166 entries and no private
  assistant/session paths. Public guides are present where applicable.

## Verification

Local mandatory release suite: 213 passed, zero failures. CI: 213 discovered,
212 passed, zero failures, one pre-existing SVG-export test skipped. That SVG
case passed locally; it is outside the shared core. Focused parity checks and
changed-code lint had already passed and were not repeated for session closure.

The shared gate and mirrored regression cases were compared across both repos;
relative instruction links, balanced fences, version synchronization, whitespace
and recursive absence of status.md imports were checked. No force push, tag
replacement, manual npm publish or native-module release occurred.

## Session and next step

Existing AISkills tracking of AGENTS.md, CLAUDE.md and docs/project/ is
preserved. New instruction paths use sibling-relative locations; TiTools private
files were not imported. This publication record is committed after the release
tag under the existing session convention. Actual registry payload excludes all
docs/project/ files, so the note does not alter the published package. Stable
requirements/context already carry the strengthened parity rule; no additional
stable change was needed after publication.

Both requested releases are complete. No release blocker or known uncommitted
product correction remains. Future engine changes must satisfy the same
bidirectional implementation/test evidence gate before completion or publication.
The maintainer uses npm-link/symlink checkouts; no marketplace refresh is needed.

## Parity evidence for the current engine correction

Parity status: **verified** for the corrected behaviors below. Both implementations and their regression coverage are committed and shipped
in the independently authorized releases TiTools 5.2.2 and AISkills 1.28.1.

| Behavior | TiTools implementation / tests | AISkills implementation / tests | Evidence |
| --- | --- | --- | --- |
| Cache TTL and deterministic auto-update | lib/cache.js; test/cache.test.js; test/auto-update.test.js | lib/cache.js; test/cache.test.js; test/auto-update.test.js | TiTools cache/auto-update/CLI subset 17 passed; AISkills ported subset 21 passed; AISkills TTL regression failed before correction |
| Install/update and canonical mirrors | lib/installer.js; lib/symlink.js; lib/commands/update.js; test/cli.test.js | lib/installer.js; lib/symlink.js; lib/commands/update.js; test/cli.test.js | Independent temporary-home CLI cases included in 17/21 results above |
| Hook preservation | lib/hooks.js; test/hooks.test.js | lib/hooks.js; test/hooks.test.js | Implementation comparison equivalent after command-name adaptation; AISkills ported hook cases included in 21-pass subset; TiTools hooks unchanged |
| Selection/foreign-skill cleanup | lib/cleanup.js; test/core-cleanup.test.js | lib/cleanup.js; test/core-cleanup.test.js | 2 passed independently in each repo |
| Removal scope and defaults | lib/commands/uninstall.js; test/uninstall.test.js | lib/commands/uninstall.js; test/uninstall.test.js | Reproduced failures; final real-CLI subprocess checks 3 passed independently in each repo |
| Manifest JSON guard | test/manifest.test.js | test/manifest.test.js | AISkills filtered bundled JSON checks 8 passed; TiTools existing guard inspected |
| Description helper default exports | lib/utils.js | lib/utils.js | TiTools export identity assertions passed; AISkills equivalent default exports inspected |

Changed-code lint and git diff --check passed in each repo. Product exceptions:
Titanium detection/agent/index paths, asset dependencies and catalog-specific
fixtures; private instruction tracking differs by repository. No successful core
suite was repeated for the subsequent instruction-only edits.

Instruction mapping: TiTools and AISkills each use AGENTS.md (mandatory gate),
CLAUDE.md (entry-point and release pointer), docs/project/requirements.md
(acceptance) and docs/project/context.md (contract). Static validation compares
the two gate blocks exactly, checks their pointers and local targets, preserves
existing ignored paths and confirms no status import was introduced. TiTools'
public CONTRIBUTING.md carries the corresponding neutral contributor rule.
