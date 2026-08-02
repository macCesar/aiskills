# Status — 2026-08-01

**Phase:** `session-log` built, measured and reviewed; uncommitted
**Deployed:** the GitHub plugin is at v1.15.0, which does **not** include `session-log`
**Branch:** `main`, none of this work pushed

## Where things stand

`skills/session-log/` was built in one session — `commands/session-log.md` was built
alongside it and then deleted the same day (see the review below) — with three A/B
rounds (18 runs) plus two installations on real projects: Logger, and a copy of E&M
Industrial, backend and app. What's missing is César's decision on whether it goes
into the published plugin.

## In flight

- **Uncommitted in two repos.** Here: `skills/session-log/` (now including the
  second-pass fixes below), this `docs/project/`, and changes to `README.md`,
  `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, `lib/config.js`, `plugin.json`,
  `marketplace.json` and `.gitignore`. In Logger: the migration from
  `.claude/memory/` to `docs/project/` with all four files.
- **The version hasn't been bumped.** `session-log` is already in the README and
  the CHANGELOG, but no bump and no tag.
- **Nothing committed on purpose.** César is opening a fresh session on this repo
  to review it before anything lands.

## Review — 2026-08-01, afternoon

The whole skill was reviewed after the automatic-triggering question was settled:

- **The `description` is written to trigger on its own again.** "Invoked
  deliberately, not inferred" is gone, and the natural closing and resuming
  phrases are back ("ya me voy, déjame anotado dónde quedé", "where did we leave
  off?"). 925 characters, in line with `audit-codebase`'s 903 — the only
  description in this repo whose automatic triggering is demonstrated.
- **The body said "Nothing needs to trigger"**, which read as if the skill never
  activates. Rewritten: what doesn't depend on the skill is *finding* the notes
  once the convention is installed — a different claim, and the actual point.
- **`commands/session-log.md` was deleted.** César's call, 2026-08-01: a command
  and a skill doing the same job are two copies of the same logic that drift, and
  the command only works in Claude Code. What lived *only* in the command was
  absorbed into `SKILL.md` first — the up-front repo survey (§ "Which job this
  is", called "Taking stock before writing anything" at the time) and the closing
  checks (§ "Before finishing"). Two
  gaps found while reviewing it were fixed on the way in: it said "create the
  three files" when there are four, and `requirements.md` appeared neither in its
  description nor in its task.
- **`session-log` was missing from `lib/config.js:SKILLS`.** The npm CLI would
  never have installed it — the skill existed in the repo and reached nobody.
  Added. `COMMANDS` now correctly holds only `release`.
- **`CLAUDE.md` still said the repo ships 4 skills**, omitting `audit-codebase`
  and `session-log`. Now 6.
- **The trigger bank was rebalanced**: 5 queries about where notes belong and 5
  about closing or resuming a session, instead of 8 and 2. Still unmeasured.
- **`evals/README.md` was cut down**: a page of self-criticism about the
  instrument was removed. What's left is the fact — the harness doesn't measure,
  the field test did — and what the twenty queries are for.

## Review — 2026-08-01, second pass

A full review of the skill found six defects and ten gaps; all were fixed the same
session. Nothing was run — the changes are content, and the new eval set is written
but unexecuted.

Defects fixed:

- **This file claimed `commands/session-log.md` had been built** while a later
  section of the same file recorded that it was deleted. `ls commands/` shows only
  `release.md`. Corrected above — and it is the exact failure `verification.md`
  exists to prevent, committed in the skill's own dogfood.
- **The description's length was recorded as 978 characters; it is 925.**
- **`decisions.md` was append-only *and* imported at startup**, which contradicts
  the skill's own token argument on any project old enough to matter. It now has
  an archive rule.
- **The central invariant had no check.** "Resolve the import chain" was an
  instruction to look; it is now two greps, with the `grep`-on-a-missing-file trap
  spelled out (exit 2, empty output, reads as clean).
- **The README claimed "files created on a one-commit repo: 2 vs 4"** — no eval
  file backs the 4. Row removed.
- **The A/B rounds were presented as measuring the current convention.** They
  graded `docs/status/current.md`; the four-file layout came later. Both round
  files now carry a historical banner and `evals/README.md` says exactly what
  carries over.

Added: resuming as a first-class job with a drift check against git; the upgrade
path from an earlier install; secrets and language rules; monorepo and
multi-writer layouts; the generated-document row in the documentation map.
`SKILL.md` went 397 → 524 lines, held down by moving the self-contained variants
into `references/file-layout.md` rather than by cutting prose.

Two repo-level defects surfaced by the same review and fixed after:

- **`npm test` ran zero tests and passed.** The script globbed `test/**/*.test.js`,
  and npm runs scripts through `sh`, where `**` collapses to `*` — so it looked in
  `test/<subdir>/` and matched nothing. There was also no `test/` directory, though
  `CLAUDE.md` documented one. Now `test/manifest.test.js`: 23 checks, no new
  dependencies, covering the wiring that has failed here before — a skill on disk
  missing from `SKILLS` (`session-log` itself), an orphaned command, a broken
  `references/` pointer, and `package.json` versus `plugin.json` drift.
  **Verified with positive controls, not just a green run**: an orphan skill
  directory, an orphan command file and a desynced `plugin.json` each made the
  suite fail as intended, and `plugin.json` was restored to an identical md5.
- **`marketplace.json` omitted `audit-codebase`** from both descriptions while
  `plugin.json` listed it. Fixed.

## Next step

Agreed 2026-08-01: **port `/release` to a skill** so it can be used from Codex and
Gemini, not just Claude Code. Today, Claude Code has to be opened for that alone.

What was measured before recording it:

- Of the 417 lines in `commands/release.md`, only **18 depend on Claude Code**:
  fifteen `` !`git …` `` collections and two `$ARGUMENTS`. The rest is portable
  prose — the five steps, the semver criteria, how to group a dirty tree into
  semantic commits, the CHANGELOG format.
- **The auto-trigger risk is low, not high** as first assumed. Step 4 says
  *"Present the plan in ONE block and STOP"* and is marked as a non-negotiable
  gate: even if the skill fires by mistake, it stops before committing, tagging or
  pushing. Worst case is a plan on screen nobody asked for.

Agreed shape: `SKILL.md` as the single source of the logic, with `/release`
reduced to collecting git state and delegating to it. That avoids two copies
drifting apart — which already happened with `release.md` duplicated in
`~/.claude/commands/` and in the plugin (identical today, md5 `8f637561…`, but
they will diverge the moment one is edited).

## Verified vs. assumed

- **Verified:** 3 A/B rounds with adversarial grading; the stable/volatile split
  scored 9 of 9 with the skill against 0 of 9 without; the convention is read
  unprompted at startup (an agent with no skill went straight to `status.md` in
  two files); `node --test` on the E&M app copy, 13/13. Automatic skill triggering
  works: a fresh agent, given only "audita este proyecto completo antes de
  producción", opened `audit-codebase` as its first action with nobody naming it.
- **Assumed:** that the convention works the same in Codex and Gemini. Reasonable
  — it lives in `AGENTS.md` and depends on no assistant — but unmeasured.
- **Not measurable with what's here:** whether `session-log` specifically triggers
  on its own. `skill-creator`'s `run_eval.py` reports 0/10 for this skill and
  **0/5 for `audit-codebase`** — published and in use — fed phrases lifted from its
  own description. A control that fails on a healthy subject measures nothing, so
  neither the 0/10 nor the 10/10 on near-misses says anything.

## Known pending

- **`release.md` is duplicated**: `~/.claude/commands/release.md` and this repo's
  `commands/release.md`. If the plugin is installed, the global copy is redundant.
- **`.skill` packaging doesn't run**: `scripts/package_skill.py` needs `pyyaml` and
  Homebrew's Python blocks loose installs (PEP 668). Not forced. Not needed either
  — distribution is through the GitHub plugin.
- **Nothing has been tested outside Opus 5.** César's criterion is that these
  skills work in Codex and Gemini; that still has no evidence.
