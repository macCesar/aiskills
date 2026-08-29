# Status — 2026-08-29

**Phase:** v1.22.0 shipped; live and maintained
**Session by:** Codex
**Deployed:** `@maccesar/aiskills@1.22.0`, tag `v1.22.0`, GitHub Release, marketplace version on `main`, and the OIDC publish workflow were verified during the release.
**Branch:** `main`; the sibling-parity requirement, release-skill migration, and release metadata are published.
**Sibling:** `../TiTools` — the shared zero-command diagnostics and command-to-skill migration handling introduced here were ported there and verified in the same session.

## Where things stand

The former Claude-only `commands/release.md` is now the cross-agent `skills/release/` package. Codex carries a native explicit-only invocation policy; Claude and Gemini use the portable body's mandatory name gate because Claude's proprietary frontmatter extension makes Codex reject the skill. Gemini CLI successfully discovers the standard skill. The workflow stops at its confirmation plan before any external mutation.

The CLI catalog installs nine skills and marks the old `release` command as legacy so the next install/update removes stale Claude copies. README, marketplace copy, maintainer documentation, CHANGELOG, tests, and the actual npm tarball surface all reflect the migration.

## In flight

- Nothing. The migration and both shared-CORE safeguards are released.

## Requirements

- R1 remains satisfied: the zero-active-commands branch and same-name command-to-skill migration handling exist in both sibling repos with matching regression coverage.
- `release` remains explicit-only and requires a second confirmation after the plan before commit, tag, push, publication, merge, or pull request.

## Next step

Refresh the maintainer's Claude marketplace cache with `/plugin marketplace update maccesar-aiskills`, run `aiskills install`, then `/reload-plugins` so the old command-to-skill handoff completes locally.

## Verified vs. assumed

- Verified: AISkills tests pass 121/121 and lint is clean; the focused manifest suite passes 57/57; `git diff --check` is clean; `npm pack --dry-run` includes all three `skills/release/` files and excludes `commands/release.md`; Gemini CLI 0.56.0 discovers the skill; Codex 0.151 rejects the Claude-only frontmatter extension and accepts the standards-only entry point; an isolated `doctor` run reports the zero-command state correctly.
- Verified: TiTools tests pass 346/346 and lint is clean after the shared CORE port.
- Verified during release: `main`, tag `v1.22.0`, GitHub Release, and npm `1.22.0` all resolve to the published release.

## Known pending

- TiTools: carry its small diagnostics/symlink parity patch in the next appropriate release; it does not change current behavior while TiTools has active, non-overlapping slash commands.
