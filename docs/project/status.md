# Status — 2026-08-01

**Phase:** v1.16.0 shipped on every channel — done
**Deployed:** npm serves `1.16.0` (published 2026-08-02 01:24 UTC, tarball verified to
              contain all nine `session-log` files). Tag and GitHub release are live.
              On César's machine: `~/.agents/skills/session-log` present (this is what
              Gemini CLI and Codex CLI read), marketplace cache at `1.16.0` with the
              skill, and no duplicate symlink at `~/.claude/skills/`.
**Branch:** `main`, pushed, clean at `d13f942`

## Where things stand

`session-log` shipped in v1.16.0 — six commits: the skill itself, the first test
suite, the `npm test` glob fix, the plugin-description sync, this `docs/project/`,
and the release commit. It was built and reviewed across two sessions on 2026-08-01,
with three A/B rounds (18 runs, earlier layout) plus installations on Logger and a
copy of E&M Industrial. `commands/session-log.md` existed briefly and was deleted the
same day (see the first review below).

## In flight

- **Logger still has uncommitted work**: the migration from `.claude/memory/` to
  `docs/project/` with all four files.
- **A second project got the convention installed** the same day — four files in
  Spanish (the project was already documented that way), 9 product requirements,
  6 refactor ones, 15 technical contracts each naming the script that verifies it,
  8 dated decisions reconstructed from git history, and a map of the 36 documents
  already under `docs/`. That install surfaced **~35 uncommitted files dating back
  to 2026-02-14** — the whole Domain → Service migration, including an untracked
  `ARCHITECTURE_GUIDE.md` that exists nowhere else. Six months of finished work on
  a single disk. Not this repo's problem, but it is the finding worth acting on.

## Refresh order, learned the hard way

`npm publish` → **`/plugin marketplace update`** → **`aiskills install`** →
`/reload-plugins`. Done in the other order, `aiskills install` cannot see a plugin
that hasn't updated yet, so it creates a `~/.claude/skills/<skill>` symlink and
Claude Code ends up listing the skill twice — once from the symlink, once from the
plugin. A second `aiskills install` after the marketplace update removes the stale
symlink (`lib/symlink.js:128`). That is exactly what happened with v1.16.0.

The two channels are not alternatives: npm is what Gemini CLI and Codex CLI read
(`getPlatforms()` in `lib/config.js` lists only Claude, so they get no symlinks and
don't need any); the marketplace is Claude Code only but also carries the `/release`
slash command.
- **The skill was exercised once, on the install path only.** `/session-log` was
  invoked explicitly in a repo with no `docs/project/`; it surveyed first, then read
  the existing docs before writing. The resume path and automatic triggering are
  still unexercised — the test for both is to open Logger or E&M and type
  "en qué quedamos aquí?" without naming the skill.

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

Agreed 2026-08-01: **port `/release` to a skill** so it can be used from Codex
and Gemini, not just Claude Code. Today, Claude Code has to be opened for that alone.

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
