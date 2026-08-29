# Status — 2026-08-28

**Phase:** live and maintained
**Session by:** Codex
**Deployed:** `@maccesar/aiskills@1.21.1` is published; tag `v1.21.1`, GitHub Release, marketplace version on `main`, and the OIDC publish workflow were verified.
**Branch:** `main`; this documentation handoff is to be committed locally and left unpushed for the next update.
**Sibling:** `../TiTools` — the same shared-CORE invariant is recorded there in the same session.

## Where things stand

The live `npm link` installer behavior, marketplace diagnostics, shared public API alignment, and Python-bytecode tarball exclusion are already released as 1.21.1. This session changed no executable code: it installed `requirements.md` and converted sibling synchronization from guidance into a permanent, testable engineering requirement.

## In flight

- Nothing. The documentation commit is intentionally being held for the next AISkills update rather than triggering another patch release.

## Requirements

- R1 requires every shared-CORE change to be ported to TiTools in the same working session, with both repos verified independently. Intentional differences must already be listed in `context.md` or recorded as a decision.

## Next step

Include this local documentation commit in the next AISkills update. Before changing shared CLI machinery, inspect the equivalent TiTools implementation and finish the session with both repos synchronized.

## Verified vs. assumed

- Verified: v1.21.1 release and npm publication succeeded; the current full suite passed 115/115 with lint clean; `aiskills doctor` reported no issues; all 8 canonical and Claude skill links resolved to this checkout; the documentation diff passes `git diff --check`.
- Assumed: none for this documentation-only handoff.

## Known pending

- Push and release this documentation commit as part of the next AISkills update; do not create a standalone version, tag, or release for it.
