# Status — 2026-10-22

**Phase:** v1.28.0 published to npm and GitHub; publication verified and session documented.
**Session by:** Codex — used Skill Creator, checked official sources, ran an independent isolated forward-test, created semantic commits and published v1.28.0 after explicit release-plan confirmation.
**Branch:** `main`.

## Publication — v1.28.0

- Release commit `3fe5f9d6cb0404a66b2cbb991801b9d76953c886`; annotated tag `v1.28.0` resolves to that commit. Both are pushed to origin; GitHub Release is public, not a draft or prerelease: [v1.28.0](https://github.com/macCesar/aiskills/releases/tag/v1.28.0).
- `package.json`, root/package entry in `package-lock.json`, and `.claude-plugin/plugin.json` are synchronized at `1.28.0`. Confirmed the remote plugin manifest at the release tag. README already covers the shipped features; CHANGELOG Unreleased content was promoted to `1.28.0` dated 2026-10-22.
- Trusted-publishing workflow [39793177366](https://github.com/macCesar/aiskills/actions/runs/39793177366), job `119874014457`: all steps completed successfully, including version guard, npm ci, npm test and npm publish. GitHub's overall run metadata still reports `in_progress` with no conclusion despite the completed successful job; this is recorded separately from the verified registry publication.
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
- No known implementation or registry-publication blocker remains. The only outstanding observation is GitHub's delayed overall run conclusion; the publish job and actual npm artifact are verified independently. Future releases must follow the same confirmation and synchronized-version workflow.
