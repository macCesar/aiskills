# Status — 2026-09-10

**Phase:** v1.24.0 shipped and published; a follow-up change to `release` and `session-log` is committed on top of it, unreleased
**Session by:** Claude Code · Opus 5 (1M context) (`claude-opus-5[1m]`)
**Deployed:** `@maccesar/aiskills@1.24.0` is live on npm, published by `publish.yml` over OIDC (run 34508954288, green in 18s). Tag `v1.24.0`, the GitHub Release, and `main` all point at `e3bd949`. The maintainer's Claude marketplace cache has **not** been refreshed yet — see "Next step".
**Branch:** `main`, one commit ahead of the v1.24.0 tag (`0f054cc`, the follow-up below) plus this note's own commit.
**Sibling:** `../TiTools` — not touched, and no port is owed. This release changed only the AISkills payload (`skills/humaniza/SKILL.md`) plus release metadata; no shared CLI CORE file was modified.

## Where things stand

`humaniza` gained the half of its method that was missing. It treated its eight rules as equals and waited for the user to name a mode, so a text could pass the whole checklist and still read as machine-written — a checklist verifies absences and never asks whether the result came out alive.

Three things close that. Rules 1–5 now justify an edit on a single occurrence while the rest only count when several coincide in a passage, which stops one weak tell from flattening the prose. Register is deduced from the kind of text rather than requested: essays and personal mail keep opinion, doubt and digression; reference, technical, legal and factual text stays neutral. And a five-dimension rubric (franqueza, ritmo, confianza, voz, densidad) with a 35/50 threshold scores whether the result is alive, carrying the two caveats that make it usable — voice is graded against the type of text, and a perfect 50 signals over-editing.

Three new tells ship with it: explaining internals inside a usage document, a first sentence that repeats its own heading, and describing the version a change replaces. Incoming text is now stated to be material to edit, never instructions to follow.

The first of those tells comes from a real review: a maintainer rejected a documentation PR with "this does not really belong into the readme" and "no claudish sentences please". That text had already passed the full `humanizer`, which catches vocabulary and punctuation while the problem was structural.

## In flight

**Committed as `0f054cc`, tests green, not released.** Closing a session and cutting a release fought each other: `/release` published and left the tree clean, then `/session-log` wrote `status.md` and `context.md` and stopped without committing, so the tree ended dirty right after a release. The order was never the problem — half of `status.md` (release commit hash, publish outcome, the version the registry serves) does not exist until after the tag, so the note must come second. The problem was stopping one step early.

Two edits, in the two skills that were disagreeing:

- `skills/release/references/workflow.md` — a Step 1.11 detection (does `docs/project/status.md` exist?), one line in the Step 4 confirmation block announcing the notes will be rewritten and committed, and a Phase 6 that does it after the publish is observed. Phase 6 **delegates to `session-log`** instead of restating its rules: it contributes the release facts (commit hash, tag, publish outcome, published version), notes that a release is a common reason the stable files go stale, and commits without a second ask because Step 4 already collected the permission. If the file is absent, `release` creates nothing: installing the convention writes into `CLAUDE.md` and `AGENTS.md`, which has no place inside a release.
- `skills/session-log/SKILL.md` — the "closing is not permission to edit" boundary now distinguishes the person's work in progress from the four files the skill itself just wrote. Closing offers the commit in one line and stages `docs/project/` explicitly. A release is the exception with no second ask, since the confirmation was already collected there.

`CHANGELOG.md` carries both under `[Unreleased]`, so the next release picks them up. Nothing here is published: v1.24.0 on npm predates this commit.

## Requirements

- R1 (sibling CLI CORE parity) is satisfied without action: the release is payload-only.

## Next step

Refresh the maintainer's own channels — `/plugin marketplace update maccesar-aiskills`, then `aiskills install`, then `/reload-plugins`. Neither channel picks up a release on its own.

## Verified vs. assumed

- **Verified:** 140/140 tests pass locally, before and after the CHANGELOG and version edits.
- **Verified:** `package.json` and `.claude-plugin/plugin.json` both read `1.24.0`; `publish.yml`'s tag-vs-both-versions guard passed in CI, which is an independent check of the same thing.
- **Verified:** `npm view @maccesar/aiskills version` returns `1.24.0`.
- **Verified:** the GitHub Release exists at `releases/tag/v1.24.0` with the CHANGELOG section as its notes.
- **Verified:** `main` is level with `origin/main`; the working tree holds only these two doc edits.
- **Assumed:** the skill's new rubric and weighting improve real output. They were reviewed as text and are covered by no test — `test/manifest.test.js` guards frontmatter and reference pointers, not editorial quality.
- **Verified:** 140/140 tests still pass after the two skill edits.
- **Verified:** no TiTools port is owed for the follow-up either — `ls ~/Developer/openSource/TiTools/skills/` shows eleven Titanium skills and neither `release` nor `session-log`. Both are AISkills-only payload, outside the shared CLI CORE.
- **Assumed:** that the new Phase 6 behaves as written. It is prose in a skill, exercised by no test, and it has not run end to end — the v1.24.0 release above was driven by hand before the edit existed.
- **Not checked:** whether the marketplace cache or `~/.agents/skills/` on this machine now serve v1.24.0. Neither was refreshed in this session.

## Known pending

- The published commit `7a3ac5e` has a message body written without accents ("podia", "maquina", "Anadirle"). It was flagged before the release, left as-is by choice, and is now pushed and tagged — rewriting it would mean rewriting published history, so it stays.
- Third-party Claude marketplaces do not auto-update unless the maintainer enables it; refresh manually with the sequence above.
