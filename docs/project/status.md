# Status — 2026-10-17

**Phase:** store-screenshots audit and page/library workflow expansion implemented, verified and committed; not released.
**Session by:** Codex — researched official Apple/Google asset requirements, updated the skill, and completed the requested semantic commits and session documentation.
**Branch:** `main`.

## Where things stand

- `60b8b02` — `feat(store-screenshots): cover Apple creative assets and Play listing requirements`. Adds three platform references, required reference routing/citations, creative artwork versus real-UI capture guidance, and distinct image/video delivery requirements.
- `f0b6030` — `feat(store-screenshots): add page workflows and asset library guidance`. Adds Apple CPP, Asset Library and PPO references, plus Google custom listings/groups/library guidance and a cross-store comparison. The skill now has nine reference guides.
- Covers Apple Header, Search Results and universal images, safe-area templates, current screenshot targets, App Preview specifications, Google Play feature graphics, large screens and YouTube previews.
- README, Codex sidecar and CHANGELOG reflect the expanded scope. Changes remain under Unreleased; package, lockfile and plugin versions remain at `1.27.1`.
- Session documentation is committed separately (`67dd547` for the first audit, plus the workflow follow-up). The audit report records evidence and limits; context maps it and records authorship.
- No shared CLI machinery changed; no TiTools port is required.

## Verification

- Fresh `npm test` before committing: 179 passed, 0 failed, 0 skipped.
- Skill Creator validator passed using PyYAML in a temporary environment; no project dependencies changed.
- Export/check passed for 3840 × 1646, 3840 × 2560, 5244 × 2950 and 1024 × 500 RGB PNGs.
- Follow-up verification: all 29 relative skill-reference links resolve; npm pack dry run includes all nine reference guides; `git diff --check` passed. Fresh tests and Skill Creator validation also passed after the workflow expansion.
- Context files point to status on demand and contain no startup imports of it.
- See [audit evidence and limits](store-screenshots-audit.md) for sources and the exact scope of verification.

## Availability and publication

- The maintainer's `npm link` / skill-directory symlinks use the edited skill immediately.
- Latest publication verified in the previous session: v1.27.1, release commit `65e05ee`, successful [publish workflow](https://github.com/macCesar/aiskills/actions/runs/36489047822). Registry state was not rechecked this session.
- This session creates commits only. No push, tag, version bump or new npm/marketplace release was requested or performed.

## Next step and remaining limits

- When a new release is requested, follow the release checklist: synchronize package/plugin versions, update CHANGELOG, verify, tag and publish through GitHub Actions.
- Numeric safe-area geometry and actual app cropping still require opening Apple's current templates and reviewing App Store Connect Preview. No live console upload, store approval, full video production or new device capture was performed.
- Google Store listing experiments is identified and linked as the PPO counterpart; a full operational Google experiment guide is not included. Apple operational/Analytics documentation conflicts are recorded in the PPO reference; verify live console capabilities before promising exceptions.
- Real-session validation of `handoff` and new simulator/emulator captures for `store-screenshots` remain outside this session's verification. No known blocker to the completed documentation/skill changes.
