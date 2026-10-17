# Status — 2026-10-17

**Phase:** store-screenshots audit implemented, verified and committed; not released.
**Session by:** Codex — researched official Apple/Google asset requirements, updated the skill, and completed the requested semantic commits and session documentation.
**Branch:** `main`.

## Where things stand

- `60b8b02` — `feat(store-screenshots): cover Apple creative assets and Play listing requirements`. Adds three platform references, required reference routing/citations, creative artwork versus real-UI capture guidance, and distinct image/video delivery requirements.
- Covers Apple Header, Search Results and universal images, safe-area templates, current screenshot targets, App Preview specifications, Google Play feature graphics, large screens and YouTube previews.
- README, Codex sidecar and CHANGELOG reflect the expanded scope. Changes remain under Unreleased; package, lockfile and plugin versions remain at `1.27.1`.
- Session documentation is committed separately as `docs(project): close store screenshots audit session`. The audit report records evidence and limits; context maps it and records authorship.
- No shared CLI machinery changed; no TiTools port is required.

## Verification

- Fresh `npm test` before committing: 179 passed, 0 failed, 0 skipped.
- Skill Creator validator passed using PyYAML in a temporary environment; no project dependencies changed.
- Export/check passed for 3840 × 1646, 3840 × 2560, 5244 × 2950 and 1024 × 500 RGB PNGs.
- All 13 relative skill-reference links resolve; npm pack dry run includes all three new platform references; `git diff --check` passed.
- Context files point to status on demand and contain no startup imports of it.
- See [audit evidence and limits](store-screenshots-audit.md) for sources and the exact scope of verification.

## Availability and publication

- The maintainer's `npm link` / skill-directory symlinks use the edited skill immediately.
- Latest publication verified in the previous session: v1.27.1, release commit `65e05ee`, successful [publish workflow](https://github.com/macCesar/aiskills/actions/runs/36489047822). Registry state was not rechecked this session.
- This session creates commits only. No push, tag, version bump or new npm/marketplace release was requested or performed.

## Next step and remaining limits

- When a new release is requested, follow the release checklist: synchronize package/plugin versions, update CHANGELOG, verify, tag and publish through GitHub Actions.
- Numeric safe-area geometry and actual app cropping still require opening Apple's current templates and reviewing App Store Connect Preview. No live console upload, store approval, full video production or new device capture was performed.
- Real-session validation of `handoff` and new simulator/emulator captures for `store-screenshots` remain outside this session's verification. No known blocker to the completed documentation/skill changes.
