# Status — 2026-10-17

**Phase:** store-screenshots coverage expansion implemented, verified and committed; not released.
**Session by:** Codex — audited official Apple/Google asset documentation, expanded the skill, and completed semantic commits and session notes at the user's request.
**Branch:** `main`.

## Where things stand

- `17b3204` — `feat(store-screenshots): complete asset review and production workflows`. Closes the latest identified gaps: Apple asset statuses and screenshot/preview content rules; store-video production; Google listing experiments; icons/device-specific banners; events/promotions; Play Shorts; per-asset AI provenance/declarations. The skill now has 13 reference guides and one unchanged PNG helper.
- Earlier implementation commits: `60b8b02` (Apple/Google asset specifications), `f0b6030` (CPP/library/PPO and Google counterparts), `4871cf1` (sequential heavy work on constrained machines), and `192a644` (native capture versus Header-video delivery). Their session documentation is also committed.
- Spanish console terminology is recorded: Fichas de Play Store → Crear una ficha de Play Store personalizada. Google experiments cover default and custom listings; Apple PPO does not test CPP.
- README, Codex metadata and CHANGELOG reflect the expanded scope. Changes remain under Unreleased; package, lockfile and plugin versions remain at `1.27.1`.
- No shared CLI machinery changed, so no TiTools port is required. Session notes and the audit report are committed separately from the latest skill changes.

## Verification

- Fresh `npm test`: 179 passed, 0 failed, 0 skipped. `git diff --check` passed.
- Skill Creator validator passed using PyYAML in a temporary environment; no project dependencies changed.
- All 58 relative skill-reference links resolve. npm pack dry run includes all 13 reference guides.
- FFmpeg 9.0.2 smoke test executed the documented recipes sequentially with a temporary synthetic 1920 × 1080 source: cropped and contained Headers both 3840 × 1646, 12 seconds, 30 fps/H.264; App Preview 1920 × 886, 15 seconds, 30 fps/H.264 High Level 4.0 plus AAC stereo/48 kHz. Probe assertions and full decoding passed, including the documented probe/decode commands.
- Earlier PNG export/check smoke tests passed for Header, Search, universal and Play feature-graphic sizes. The PNG helper was not changed by the later documentation expansion.
- See [audit evidence and limits](store-screenshots-audit.md) for sources and the exact scope of verification. Startup context files do not import status.md.

## Availability and publication

- The maintainer's npm link / skill-directory symlinks use the edited source immediately.
- Latest publication verified in a previous session: v1.27.1, release commit `65e05ee`, successful [publish workflow](https://github.com/macCesar/aiskills/actions/runs/36489047822). Registry state was not rechecked in this session.
- No push, tag, version bump, npm release or marketplace release was requested or performed.

## Next step and remaining limits

- If a release is requested, synchronize package/plugin versions, finalize CHANGELOG, verify, tag and publish through the documented GitHub Actions workflow.
- Synthetic encoding checks do not prove gameplay quality or store acceptance. No app recording, live console mutation, review submission, Lottie production, AI declaration or public upload was performed. Feature eligibility and current destination rules must be checked when used.
- Numeric Apple safe-area geometry still requires opening the current template; actual crop/placement behavior needs console Preview. Apple operational/Analytics PPO documentation conflicts remain explicitly documented.
- The 16 GB sequential policy and temporary indexer pause/restoration instructions are implemented; no workstation performance benchmark or live process-control experiment was performed here.
- Real-session validation of handoff and fresh simulator/emulator captures remain outside this session's verification. No known blocker to the completed skill/documentation work.
