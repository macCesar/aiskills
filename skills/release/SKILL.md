---
name: release
description: 'Use only when the user explicitly invokes `$release`, `/release`, or asks to use the release skill by name. Never activate merely because work appears ready or the user discusses releases. Handles the full repository release workflow: semantic commits, semver, CHANGELOG and README updates, confirmation, push, tag, GitHub release, and publication verification.'
---

# Release

Publish a repository only through an explicit, reviewable authorization sequence.

## Invocation boundary

This is an explicit-only skill.

- Proceed only when the user's current request names `$release`, `/release`, or the `release` skill itself.
- A generic request that merely discusses releases, versions, tags, publishing, or a repository that looks ready is not an invocation. Stop and tell the user how to invoke the skill.
- Invoking the skill authorizes read-only analysis and a release plan. It does not authorize commits, tags, pushes, package publication, GitHub releases, merges, or pull requests.
- Accept an optional `patch`, `minor`, or `major` override from the invocation. Otherwise infer the bump from the repository changes.

## Required workflow

1. Read [references/workflow.md](references/workflow.md) completely before running repository checks.
2. Follow its Steps 0–4 in order and present the single confirmation block.
3. Stop. Do not perform any mutation until the user explicitly confirms that exact plan.
4. After confirmation, follow Step 5 exactly and verify every publication channel triggered by the release.

Repository instructions remain authoritative. If they impose stricter release checks or extra synchronized version files, include those requirements in the plan and execution.
