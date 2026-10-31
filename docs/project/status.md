# Status — 2026-10-30

**Phase:** v1.29.0 published and verified. **Session:** Codex · GPT-6. **Branch:** main. The new store-listing skill and session documentation are committed; publication was explicitly confirmed by César.

## Verified release — v1.29.0

- 5954382 — feat(store): add evidence-based listing optimization skill.
- 501a244 — docs(project): record store optimization workflow and validation.
- 6feddf7d5e9c2f22411d1d6edc84a854fff98d30 — chore(release): v1.29.0.
- GitHub release: https://github.com/macCesar/aiskills/releases/tag/v1.29.0. Annotated tag and main pushed without force.
- OIDC publication workflow succeeded: https://github.com/macCesar/aiskills/actions/runs/41159349131. Local mandatory release suite: 218 passed, zero failures. CI install, tests, version guard and publish all succeeded.
- Registry verified @maccesar/aiskills@1.29.0 and latest=1.29.0; publication time 2026-10-31T02:20:30.427Z (2026-10-30 in the session timezone). Registry initially lagged the successful workflow; verification continued until it served the new version.
- Downloaded registry tarball: SHA-512 integrity verified, package version 1.29.0, all seven new skill files present, docs/project/ excluded. Public main plugin.json independently verified at 1.29.0; package, lockfile and plugin versions agree.
- This session note is committed after the tag as announced in the approved release plan. Stable context/requirements were checked; the feature documentation and product-specific parity exception already cover this release, so no additional stable change was needed.

## Current result

- Added `store-listing-optimization` with four dated official-source references, automatic UI metadata and six synthetic evaluation cases; registered in `lib/config.js`/README and the 1.29.0 changelog. English copy uses Humanizer; Spanish uses Humaniza and its scanner. Saved/submitted/public states, locale parity, supported product claims and metric windows are explicit.
- Kept `store-screenshots` focused on media and experiment/page configuration; added its routing link to the new skill. New skill linked from the existing universal/Claude development install paths.
- Removed the two redundant Skill Creator variants at César's explicit request, using official plugin uninstallers for Anthropic and removing imported synchronized folders. The OpenAI integrated creator remains. Source/version comparison, exact removal verification, design decision and test evidence: [review](skill-creator-review.md).
- Focused manifest checks: 11/11; changed-config ESLint passed; official creator validation passed with isolated PyYAML via uv. Four independent simulation cases found no substantive workflow failure; they exercised both language editors and corrected an over-limit draft before delivery. Evaluation JSON parse: 1/1 additional focused check. npm dry run includes all seven skill files and excludes private notes/bytecode. Session links/imports and whitespace checks passed.
- Shared engine parity: **product-specific exception**. Only the skill catalog entry changes in config; no common CLI behavior/test changes. TiTools' Titanium catalog does not need this skill.

## Expansion after the first review

César requested stronger statistics-led decisions, inspection of the full Apple/Google toolset and explicit reuse of the screenshot specialist. The skill now has a full-presence inventory, source/locale/version/cohort and coverage analysis, intervention-to-measurement decisions, Apple CPP/PPO/Asset Library routing and Google custom listings/experiments/promotion/attribution opportunities. A dedicated early companion section invokes `store-screenshots` before visual/page production and prevents reimplementing its generators/specifications.

Current official Apple Analytics/usage/acquisition and Google statistics/peer/growth/change guidance were checked. The fifth independent simulation correctly separated Apple impression-based conversion, traffic mix and opt-in coverage; its minor recommendation-only closing ambiguity was corrected. The sixth independent case passed: it covered full-presence scope with incomplete account access, retained unknown tool states and handed a concrete brief to the screenshot specialist without duplicating production. Updated focused manifest checks: 5/5; creator validator, all seven packaged skill files/private exclusions and references passed. No shared-engine code or live-store configuration changed in this expansion.

## Next step

The release is complete. Use the published skill on authorized listing tasks and record outcomes in each app project. Console mutations during the synthetic forward-test were prohibited and none occurred. The maintainer uses development symlinks; no marketplace refresh is needed.

## Previous release record — 2026-10-24

The following describes the already published 1.28.1 release and its earlier parity evidence, not publication of the new skill.

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
