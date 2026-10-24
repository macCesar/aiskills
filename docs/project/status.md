# Engine parity instructions strengthened — 2026-10-24

Added the same mandatory parity gate to AGENTS.md in both projects, a direct
CLAUDE.md pointer and release prerequisite, and matching requirements/context
acceptance criteria. The rule covers shared behavior AND regression coverage,
independent verification in each repo, corresponding implementation/test paths,
explicit exceptions and incomplete/blocker reporting. Unverified shared changes
cannot be closed or included in an affected release. No automatic commit or
publication authority is added; existing privacy boundaries remain intact.

This instruction-only follow-up uses static consistency/link/privacy checks;
previous successful core tests were not repeated. Earlier core audit changes
remain uncommitted. No commit, tag, push or publication in this follow-up.


## Parity evidence for the current engine correction

Parity status: **verified** for the corrected behaviors below. Changes remain
uncommitted and each product release remains separately authorized.

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

---

# Shared CLI parity correction — 2026-10-24

**Phase:** Shared behavior corrected and focused validation passed; uncommitted.
**Session:** Codex / GPT-6. **Branch:** main. Manifests remain 1.28.0.

Compared the shared CLI to TiTools, including prior core commits. Earlier
plugin/migration/dev-link/catalog corrections were already present. Ported
missing cache, auto-update, hook and CLI install/update regressions. Added the
same selection/mirror cleanup and removal-scope cases to both repos. Manifest
JSON parsing now includes package, plugin, marketplace and hook metadata while
preserving existing skill evaluation checks.

Fixed AISkills cache TTL override to read AISKILLS_CACHE_TTL_MS. Both uninstallers
now resolve home mirrors independently of --local. AISkills no longer preselects
mirror removal and tolerates noncritical cache cleanup failures like TiTools.
TiTools adopts AISkills' separate command scopes, scoped reinstall guidance and
description-helper default exports. Product catalogs, ti-pro, project detection,
Knowledge Index and asset CI requirements remain separate.

Verification: ported cache/hooks/auto-update/CLI 21/21, cleanup 2/2, removal CLI
3/3 and filtered bundled JSON checks 8/8. The cache and removal scope regressions
failed before the fixes. Fixtures use temporary HOME/USERPROFILE and deterministic
npm versions; only the interactive prompt is substituted in removal subprocesses.
TiTools counterpart checks passed (17+2+3); changed JavaScript lint and whitespace
checks pass in both repositories. No complete product suite was needed.

README, Unreleased changelog and context parity ledger updated. Existing session
tracking policy is preserved; no history or privacy migration was performed.
No commit, push, version bump or publication was performed for this follow-up.
Next step: review/commit and explicitly release each package when requested.

Previous public release facts and skill verification remain below.

---

# Status — 2026-10-22

**Phase:** v1.28.0 published to npm and GitHub; publication verified and session documented.
**Session by:** Codex — used Skill Creator, checked official sources, ran an independent isolated forward-test, created semantic commits and published v1.28.0 after explicit release-plan confirmation.
**Branch:** `main`.

## Publication — v1.28.0

- Release commit `3fe5f9d6cb0404a66b2cbb991801b9d76953c886`; annotated tag `v1.28.0` resolves to that commit. Both are pushed to origin; GitHub Release is public, not a draft or prerelease: [v1.28.0](https://github.com/macCesar/aiskills/releases/tag/v1.28.0).
- `package.json`, root/package entry in `package-lock.json`, and `.claude-plugin/plugin.json` are synchronized at `1.28.0`. Confirmed the remote plugin manifest at the release tag. README already covers the shipped features; CHANGELOG Unreleased content was promoted to `1.28.0` dated 2026-10-22.
- Trusted-publishing workflow [39793177366](https://github.com/macCesar/aiskills/actions/runs/39793177366), job `119874014457`: all steps completed successfully, including version guard, npm ci, npm test and npm publish. The overall workflow is now `completed` / `success`; `gh run watch --exit-status` also exited successfully. GitHub briefly lagged behind the successful job and live registry, then converged. Publish logs confirm a signed provenance statement and `+ @maccesar/aiskills@1.28.0`.
- Live npm queries confirm `@maccesar/aiskills@1.28.0` and `dist-tags.latest = 1.28.0`. Downloaded the actual registry tarball and verified its advertised SHA-512 integrity, package version, all eight `app-compliance` files and the new store/video references. No `docs/` files occur in the tarball, so the session-note commit does not change the distributed payload.
- Fresh pre-release `npm test`: **183 passed, zero failures**. `git diff --check` and explicit three-manifest version assertions passed. No additional suite rerun for the release-metadata or session-note edits; the publishing job also passed its test step.

## Where things stand

- `4df4b5f` — `feat(app-compliance): add evidence-based controls and catalog integration`. Session state and attribution are recorded in a separate `docs(project)` commit.
- Added `skills/app-compliance/SKILL.md`, six topic references and `agents/openai.yaml` with normal implicit discovery. All skill content is English; responses follow the user's language.
- Scope: children/age, external fonts, session recording, marketing email, subscriptions and user content/DMCA. Requires current official sources, applicability evidence and findings before edits; review mode remains read-only, implementation continues within existing authorization without a generic second approval.
- Requires completion of authorized technical work, precise blockers requested when detected, and continuation of independent work. No invented identities, addresses, agents or business policies. Actual provider/data-flow verification is distinguished from source checks and mocks.
- Registered the skill in `lib/config.js`; added README entry/example, CHANGELOG Unreleased entry and conditional routing in `audit-codebase`. Updated current catalog counts in CLAUDE.md and context.md to 14.
- CLI engine, dependencies and TiTools are unchanged: this is AISkills-specific catalog content. Release-specific version, tag, push and publication facts are recorded above. No external compliance filing was performed.
- Previous `store-screenshots` work ships in v1.28.0; its latest implementation commit is `17b3204`. See [its audit evidence](store-screenshots-audit.md) for verification and limits.

## Verification

- `node --test test/manifest.test.js test/list.test.js`: 96 passed, zero failures.
- ESLint on `lib/config.js` and `git diff --check` passed.
- Skill Creator `quick_validate.py` passed. PyYAML was installed only in a temporary validation environment; no repository dependency changed. Universal frontmatter and Codex UI metadata were also parsed and checked, including enabled implicit invocation.
- Six relative reference links resolve. `npm pack --dry-run --json` includes all eight new skill files: entry point, six references and Codex metadata. `aiskills list` renders the new catalog entry.
- Independent agent used a copied skill and synthetic app in a temporary directory, with no real services or external mutations. Actual corrections and seven behavior tests covered replay refusal/acceptance/revocation, marketing guards and persistent suppression, transactional-message preservation, provider-confirmed period-end cancellation, provider failures and unconfirmed state. The primary agent inspected the artifacts and independently reran those seven tests: all passed.

## Forward-test cases and observed decisions

| Case | Observed result |
| --- | --- |
| General audience, no accounts or actual knowledge of children | No unnecessary age gate or birth-date collection; applicability based on product facts. |
| SDK collects before consent | Deferred collection until opt-in and stopped on revocation; verified fake SDK state/events. |
| Marketing email without a known address | Requested real address in the evaluation report; prepared campaign guard, opt-out and persistent suppression while preserving security sends. |
| Cancellation changes only local state | Called fake billing authority, checked provider confirmation and retained access through the paid period; tested failure paths. |
| DMCA preparation without agent details | Prepared an internal draft and identified missing identity, contacts, policy decision and filing authority; no invented agent or filing. |

The evaluator identified ambiguous scope when future subsystems do not yet exist. The final skill now explicitly distinguishes future plans from existing features, avoids unrequested subsystem construction and requires completing necessary authorized wiring when architecture/authority are available. This wording clarification received static review, not a second independent behavioral run.

## Session close

- Reviewed and committed only the implementation and documentation from this session using explicit paths. The implementation-close dirty tree consisted of these already reviewed changes; the release started from a clean tree.
- Updated `context.md` attribution and catalog count, and this status with commit/verification evidence. The release ran the full required suite once; existing focused/forward-test evidence is retained above without repeating it for session notes.
- Confirmed the existing AGENTS.md/CLAUDE.md pointers do not import `status.md`; session notes remain tracked and read on demand.

## Limits and next steps

- Official sources were consulted on 2026-10-22. CNIL session-replay material consulted was a draft; the references require checking for a final version. California §17602 retrieval returned HTTP 403 and is explicitly marked Pending verification rather than used to assert deadlines.
- The ROSCA official URL returned Page Not Found on direct fetch; official search returned the statute text. The final reference links that official result and still requires checking current statutory scope at use time. The evaluator independently marked its failed statute fetch unverified and relied on the fixture's explicit cancellation policy for the technical correction.
- Forward-testing used local fake providers and synthetic data, not browser/network capture, live replay masking, real campaign delivery, billing renewals or a real DMCA procedure. Missing HTTP/authentication, uploads and provider dashboards in the fixture were reported as concrete integration limits. The evaluation instruction substituted recorded questions for actual user interaction.
- No known implementation or release blocker remains. GitHub's delayed overall conclusion resolved to success. Future releases must follow the same confirmation and synchronized-version workflow.
