# Status — 2026-08-02

**Phase:** v1.16.1 shipped — `session-log` published and the four bugs its rollout
           exposed are fixed
**Deployed:** npm serves `1.16.1`. Tag and GitHub release are live. On César's
              machine: 6 skills in `~/.agents/skills/` (what Gemini CLI and Codex CLI
              read), 6 symlinks in `~/.claude/skills/`, marketplace plugin
              **uninstalled on purpose**, `aiskills doctor` reports no issues.
**Branch:** `main`, pushed, clean at `49036f0`, plus the uncommitted doc changes below

## Changed 2026-08-02 — from a TiTools session, docs only

No code touched here; `npm test` still reports 39 passing, 10 suites.

- **New `docs/project/context.md`** with the parity contract against TiTools: what the two repos share, the table of what legitimately diverges, and a measured per-file comparison of `lib/` as of today. Added to the pointer block in `CLAUDE.md` and `AGENTS.md`.
- **Corrected stale facts** in `CLAUDE.md` and `AGENTS.md`: both listed `ti-create-release` and `ti-module-update` among TiTools' skills. Neither is in its `SKILLS` array or its `skills/` directory — it ships 8, all Titanium docs and patterns.

**What happened on the TiTools side the same day** (v4.2.0, built but not yet released there): the plugin-detection work from this repo's v1.16.0–v1.16.1 was ported over — `lib/claude-plugin.js`, the `skipped` handling in symlinks and command installs, and the doctor changes. TiTools had none of it and had been duplicating every skill for anyone running both channels. Its three slash commands also turned out to be sitting in gitignored `.claude/commands/`, reaching neither channel.

Nothing came back the other way this session.

**The Knowledge Index question is now settled: not porting it.** It had sat in TiTools' `docs/PENDING-IMPROVEMENTS.md` as ALTA PRIORIDAD. Measured on 2026-08-02 it costs ~850 tokens in every session, and its entire justification is that the model's Titanium training data is wrong — an enemy none of the skills here have. There is also no `tiapp.xml`-equivalent trigger, and the 6 skills cover disjoint domains, so a single index would be noise in most repos. That item is marked discarded upstream; the multi-domain SessionStart hook is the part still worth doing. Full reasoning in `context.md` § "Why the Knowledge Index is not a gap here".

## Where things stand

`session-log` shipped in v1.16.0 — six commits: the skill itself, the first test suite, the `npm test` glob fix, the plugin-description sync, this `docs/project/`, and the release commit. It was built and reviewed across two sessions on 2026-08-01, with three A/B rounds (18 runs, earlier layout) plus installations on two real private projects — a Node CLI and a Laravel backend with its Titanium client. `commands/session-log.md` existed briefly and was deleted the same day (see the first review below).

Shipping it exposed four CLI bugs the same evening, fixed in v1.16.1 — see "What shipping v1.16.0 taught" below.

### One channel, not two

César uses Claude Code, Gemini CLI and Codex CLI, so **npm is the channel that serves him** — `aiskills install` covers all three, including the slash commands in `~/.claude/commands/`. The marketplace plugin only reaches Claude Code and adds nothing he doesn't already get, so it was uninstalled. Refresh is now one command:

```
npm update -g @maccesar/aiskills && aiskills install
```

The plugin still matters as a product: it exists for users who only run Claude Code and don't want a global npm install. Worth reinstalling occasionally to test it the way they experience it — but reinstalling brings back the two-channel refresh order.

## In flight

- **The Node CLI project still has uncommitted work**: the migration from `.claude/memory/` to `docs/project/` with all four files.
- **A second private project got the convention installed** the same day, and the install went the way the skill intends: files written in the language the project was already documented in, requirements carrying the script that verifies each one, decisions reconstructed from git history, and a map of the documentation the repo already had. The inventory step also surfaced months of finished work sitting uncommitted — which is the strongest argument for the skill so far, and belongs in *that* project's `status.md`, not here.

- **The skill was exercised once, on the install path only.** `/session-log` was invoked explicitly in a repo with no `docs/project/`; it surveyed first, then read the existing docs before writing. The resume path and automatic triggering are still unexercised — the test for both is to open one of the projects that already has the convention and type "en qué quedamos aquí?" without naming the skill.

## What shipping v1.16.0 taught, and cost

Rolling out `session-log` across both channels exposed four bugs in a single evening, all fixed in v1.16.1. They are recorded here because each one was found by asking "is this right?" rather than by a test:

- **A leftover plugin cache is not an installed plugin.** Uninstalling the marketplace plugin leaves `~/.claude/plugins/cache/` behind. The CLI read that as proof of installation, skipped every symlink, reported `0/6 skills linked`, and left Claude Code with no skills that `aiskills install` could restore.
- **`aiskills doctor` was useless in exactly the configuration that breaks.** With the plugin enabled it counted the (correctly) absent mirrors as six failures and recommended a command that does nothing.
- **Slash commands never asked about the plugin**, so `/release` appeared twice.
- **`✓ Claude Code detected`** read as though Gemini and Codex had not been found.

**Refresh order, if the plugin is ever reinstalled:** `npm publish` → `/plugin marketplace update` → `aiskills install` → `/reload-plugins`. In any other order the install cannot see a plugin that has not updated yet, creates a symlink, and the skill is listed twice. This no longer applies while the plugin stays uninstalled.

## Review — 2026-08-01, afternoon

The whole skill was reviewed after the automatic-triggering question was settled:

- **The `description` is written to trigger on its own again.** "Invoked deliberately, not inferred" is gone, and the natural closing and resuming phrases are back ("ya me voy, déjame anotado dónde quedé", "where did we leave off?"). 925 characters, in line with `audit-codebase`'s 903 — the only description in this repo whose automatic triggering is demonstrated.
- **The body said "Nothing needs to trigger"**, which read as if the skill never activates. Rewritten: what doesn't depend on the skill is *finding* the notes once the convention is installed — a different claim, and the actual point.
- **`commands/session-log.md` was deleted.** César's call, 2026-08-01: a command and a skill doing the same job are two copies of the same logic that drift, and the command only works in Claude Code. What lived *only* in the command was absorbed into `SKILL.md` first — the up-front repo survey (§ "Which job this is", called "Taking stock before writing anything" at the time) and the closing checks (§ "Before finishing"). Two gaps found while reviewing it were fixed on the way in: it said "create the three files" when there are four, and `requirements.md` appeared neither in its description nor in its task.
- **`session-log` was missing from `lib/config.js:SKILLS`.** The npm CLI would never have installed it — the skill existed in the repo and reached nobody. Added. `COMMANDS` now correctly holds only `release`.
- **`CLAUDE.md` still said the repo ships 4 skills**, omitting `audit-codebase` and `session-log`. Now 6.
- **The trigger bank was rebalanced**: 5 queries about where notes belong and 5 about closing or resuming a session, instead of 8 and 2. Still unmeasured.
- **`evals/README.md` was cut down**: a page of self-criticism about the instrument was removed. What's left is the fact — the harness doesn't measure, the field test did — and what the twenty queries are for.

## Review — 2026-08-01, second pass

A full review of the skill found six defects and ten gaps; all were fixed the same session. Nothing was run — the changes are content, and the new eval set is written but unexecuted.

Defects fixed:

- **This file claimed `commands/session-log.md` had been built** while a later section of the same file recorded that it was deleted. `ls commands/` shows only `release.md`. Corrected above — and it is the exact failure `verification.md` exists to prevent, committed in the skill's own dogfood.
- **The description's length was recorded as 978 characters; it is 925.**
- **`decisions.md` was append-only *and* imported at startup**, which contradicts the skill's own token argument on any project old enough to matter. It now has an archive rule.
- **The central invariant had no check.** "Resolve the import chain" was an instruction to look; it is now two greps, with the `grep`-on-a-missing-file trap spelled out (exit 2, empty output, reads as clean).
- **The README claimed "files created on a one-commit repo: 2 vs 4"** — no eval file backs the 4. Row removed.
- **The A/B rounds were presented as measuring the current convention.** They graded `docs/status/current.md`; the four-file layout came later. Both round files now carry a historical banner and `evals/README.md` says exactly what carries over.

Added: resuming as a first-class job with a drift check against git; the upgrade path from an earlier install; secrets and language rules; monorepo and multi-writer layouts; the generated-document row in the documentation map. `SKILL.md` went 397 → 524 lines, held down by moving the self-contained variants into `references/file-layout.md` rather than by cutting prose.

Two repo-level defects surfaced by the same review and fixed after:

- **`npm test` ran zero tests and passed.** The script globbed `test/**/*.test.js`, and npm runs scripts through `sh`, where `**` collapses to `*` — so it looked in `test/<subdir>/` and matched nothing. There was also no `test/` directory, though `CLAUDE.md` documented one. Now `test/manifest.test.js`: 23 checks, no new dependencies, covering the wiring that has failed here before — a skill on disk missing from `SKILLS` (`session-log` itself), an orphaned command, a broken `references/` pointer, and `package.json` versus `plugin.json` drift. **Verified with positive controls, not just a green run**: an orphan skill directory, an orphan command file and a desynced `plugin.json` each made the suite fail as intended, and `plugin.json` was restored to an identical md5.
- **`marketplace.json` omitted `audit-codebase`** from both descriptions while `plugin.json` listed it. Fixed.

## Next step

Agreed 2026-08-01: **port `/release` to a skill** so it can be used from Codex and Gemini, not just Claude Code. Today, Claude Code has to be opened for that alone.

What was measured before recording it:

- Of the 417 lines in `commands/release.md`, only **18 depend on Claude Code**: fifteen `` !`git …` `` collections and two `$ARGUMENTS`. The rest is portable prose — the five steps, the semver criteria, how to group a dirty tree into semantic commits, the CHANGELOG format.
- **The auto-trigger risk is low, not high** as first assumed. Step 4 says *"Present the plan in ONE block and STOP"* and is marked as a non-negotiable gate: even if the skill fires by mistake, it stops before committing, tagging or pushing. Worst case is a plan on screen nobody asked for.

Agreed shape: `SKILL.md` as the single source of the logic, with `/release` reduced to collecting git state and delegating to it. That avoids two copies drifting apart — which already happened with `release.md` duplicated in `~/.claude/commands/` and in the plugin (identical today, md5 `8f637561…`, but they will diverge the moment one is edited).

## Verified vs. assumed

- **Verified:** 3 A/B rounds with adversarial grading; the stable/volatile split scored 9 of 9 with the skill against 0 of 9 without; the convention is read unprompted at startup (an agent with no skill went straight to `status.md` in two files); `node --test` on the Titanium client copy, 13/13. Automatic skill triggering works: a fresh agent, given only "audita este proyecto completo antes de producción", opened `audit-codebase` as its first action with nobody naming it.
- **Assumed:** that the convention works the same in Codex and Gemini. Reasonable — it lives in `AGENTS.md` and depends on no assistant — but unmeasured.
- **Not measurable with what's here:** whether `session-log` specifically triggers on its own. `skill-creator`'s `run_eval.py` reports 0/10 for this skill and **0/5 for `audit-codebase`** — published and in use — fed phrases lifted from its own description. A control that fails on a healthy subject measures nothing, so neither the 0/10 nor the 10/10 on near-misses says anything.

## Known pending

- **`release.md` is duplicated**: `~/.claude/commands/release.md` and this repo's `commands/release.md`. If the plugin is installed, the global copy is redundant.
- **`.skill` packaging doesn't run**: `scripts/package_skill.py` needs `pyyaml` and Homebrew's Python blocks loose installs (PEP 668). Not forced. Not needed either — distribution is through the GitHub plugin.
- **Nothing has been tested outside Opus 5.** César's criterion is that these skills work in Codex and Gemini; that still has no evidence.
