# Status — 2026-09-03

**Phase:** `technical-demo-videos` generalized and validated; awaiting a separately authorized release
**Session by:** Codex
**Deployed:** `@maccesar/aiskills@1.22.0` remains the latest release. The new skill is not yet published.
**Branch:** `main`; feature implementation is committed separately from any future release.
**Sibling:** `../TiTools` — the shared zero-command diagnostics and command-to-skill migration handling introduced here were ported there and verified in the same session.

## Where things stand

`technical-demo-videos` has been added as the tenth general-purpose skill. It converts a project path and conversational tutorial goal into an approval-gated storyboard, reproducible macOS/VS Code recorder, real event timing, narration and caption sources, a verified delivery master, and optional publishing automation.

The source was generalized from a completed eight-episode workflow. Maintainer-specific paths and product pronunciation rules were removed; disposable-project root and capture display are configurable; workstation geometry is a saved profile; three cross-domain eval specifications cover a Node CLI, a web app, and an audio-aligned retake.

## In flight

- No implementation work remains. Publishing the skill requires a separate explicit `release` invocation and confirmation.

## Requirements

- R1 remains satisfied: only the AISkills payload and catalog documentation changed; shared CLI CORE behavior did not change, so no TiTools port is required.
- `technical-demo-videos` remains approval-gated before UI control, recording, paid voice generation, or external publication.

## Next step

Invoke the explicit `release` skill when this addition should be versioned, tagged, pushed, and published to npm and the Claude marketplace.

## Verified vs. assumed

- Verified: `quick_validate.py` accepts the skill using an isolated PyYAML runtime.
- Verified: all four Python helpers parse; CLI helpers expose `--help`; runtime configuration is exercised by regression tests.
- Verified: ESLint is clean and the full AISkills suite passes 132 tests.
- Verified: `npm pack --dry-run` includes the complete 16-file skill package and excludes Python bytecode.

## Known pending

- Release and install `technical-demo-videos` only when explicitly requested; the current installed workstation copy remains independent until then.
