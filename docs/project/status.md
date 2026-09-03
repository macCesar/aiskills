# Status — 2026-09-03

**Phase:** v1.23.0 shipped; `technical-demo-videos` is live and maintained
**Session by:** Codex
**Deployed:** `@maccesar/aiskills@1.23.0`, tag `v1.23.0`, GitHub Release, marketplace version on `main`, and the OIDC publish workflow were verified during the release.
**Branch:** `main`; the feature, integration-audit corrections, and release metadata are published.
**Sibling:** `../TiTools` — the shared zero-command diagnostics and command-to-skill migration handling introduced here were ported there and verified in the same session.

## Where things stand

`technical-demo-videos` has been added as the tenth general-purpose skill. It converts a project path and conversational tutorial goal into an approval-gated storyboard, reproducible macOS/VS Code recorder, real event timing, narration and caption sources, a verified delivery master, and optional publishing automation.

The source was generalized from a completed eight-episode workflow. Maintainer-specific paths and product pronunciation rules were removed; disposable-project root and capture display are configurable; workstation geometry is a saved profile; four cross-domain eval specifications cover a Node CLI, a web app, an audio-aligned retake, and safe YouTube channel/playlist targeting.

An independent integration audit corrected the Codex default prompt and plugin catalog description, added the required reference router and citation contract, fixed a test that broke when Python created `__pycache__`, made cue generation respect the actual capture interval, and hardened YouTube normalization and dry-run/resume verification. YouTube publishing now supports read-only account/playlist inspection, requires explicit target choices, verifies the authenticated channel before mutation, and binds execution to the approved dry run. The delivery-master helper selects frame-rate-aware SDR bitrates, emits complete BT.709 metadata, uses YouTube's documented stereo audio settings, and has passed an actual FFmpeg encode/validation cycle.

## In flight

- Nothing. The generalized skill and its hardened production and YouTube workflows are released.

## Requirements

- R1 remains satisfied: only the AISkills payload and catalog documentation changed; shared CLI CORE behavior did not change, so no TiTools port is required.
- `technical-demo-videos` remains approval-gated before UI control, recording, paid voice generation, or external publication.

## Next step

Refresh the maintainer's Claude marketplace cache with `/plugin marketplace update maccesar-aiskills`, run `aiskills install`, then `/reload-plugins`.

## Verified vs. assumed

- Verified: `quick_validate.py` accepts the skill using an isolated PyYAML runtime.
- Verified: all four Python helpers parse; CLI helpers expose `--help`; runtime configuration, cue boundaries, frame-rate-aware bitrate selection, and YouTube dry-run behavior are exercised by regression tests.
- Verified: the delivery-master helper produced and accepted a real H.264/AAC MP4 with complete BT.709 metadata and fast start.
- Verified: ESLint is clean and the full AISkills suite passes 140 tests.
- Verified: `npm pack --dry-run` includes the complete 16-file skill package and excludes Python bytecode.
- Verified during release: `main`, tag `v1.23.0`, GitHub Release, and npm `1.23.0` all resolve to the published release.

## Known pending

- Third-party Claude marketplaces do not auto-update unless enabled; refresh manually with the sequence above when needed.
