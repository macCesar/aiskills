# Evals

Three things live here, and they are in three different states. The states matter more than the numbers, so they come first.

| File | What it is | State |
| --- | --- | --- |
| `ab-ronda-1.md`, `ab-ronda-2.md` | A/B grading of an **earlier layout** | Run, graded, historical |
| `defecto-experimento.md` | A flaw found in round 3's fixture design | The only surviving record of round 3 |
| `evals.json` | Task prompts for the **current** four-file convention | Written, **never run** |
| `trigger-eval.json` | Twenty queries for automatic triggering | Written, **never measured** |

## What the A/B rounds actually measured

Three rounds, 18 runs, same prompt with and without the skill on purpose-built fixture repos, graded adversarially by an independent agent. Headline: volatile status kept out of the startup chain **9/9 with the skill, 0/9 without**. Token cost 3–13% higher. In round 3, with a deliberately broken uncommitted file planted in the fixture, the skill left it alone and reported it while the baseline silently fixed it.

Each run was inspected directly — files on disk, import chains resolved, `php -l` and `node --test` executed. The numbers are real.

**They describe a layout this skill no longer prescribes.** Rounds 1 and 2 graded `docs/status/current.md` against `.claude/memory/index.md`; the four-file `docs/project/` convention came later. What carried over is the finding those rounds were built to test — keeping volatile status out of the startup chain is not behaviour the model has on its own — and that finding is about the split, not about the filenames. Everything specific to the current layout (requirements as a separate file, the upgrade path, resuming, monorepos) is untested.

Two more limits worth stating plainly:

- **Round 3 has no write-up.** It is counted in the 18 runs and in the 9/9, and the only file from it is `defecto-experimento.md`, which documents a fixture that contaminated one eval. Treat round 3's numbers as less reviewable than 1 and 2.
- **The fixture repos are not in this repo.** They were built in a scratch workspace and are gone. `evals.json` now carries a `fixture_spec` per eval so they can be rebuilt; the rounds above cannot be re-run as they were.

## `evals.json` — the current set

Nine task prompts against the four-file convention: the three that survive from the old set (rewritten), the non-Claude repo case from round 2, and five new ones covering paths nothing has ever tested — resuming against a stale file, a repo that gitignores `docs/`, upgrading an earlier install, a credential offered for the notes, and a monorepo.

Nothing here has been run. Saying so is the point: an eval file that looks like results is worse than no eval file.

## `trigger-eval.json` — when the skill gets consulted

Twenty queries: ten that should reach the skill — five about where notes belong, five about closing or resuming a session — and ten near-misses that should not.

**Not measured. The harness these were written for does not work.**

`skill-creator`'s `run_eval.py` reports 0/10 for this skill — and **0/5 for `audit-codebase`**, a published skill in this same repo, fed phrases lifted verbatim from its own description. A control that fails on a healthy subject is not measuring the subject.

A field test settled what the harness could not. A fresh agent, given only *"audita este proyecto completo antes de producción, quiero saber qué está realmente roto"* and no mention of any skill, opened `audit-codebase` as its first action. **Automatic triggering works; the harness does not detect it.** The near-misses scoring 10/10 is equally uninformative — a harness that never reports a trigger is trivially correct at "don't trigger".

So these twenty queries are written and unused. If you have a working way to measure skill triggering, that's what they're for.

The description is written for automatic triggering, and there is no slash command to fall back on — that was deliberate, since a command duplicating this logic would drift from it and would only work in Claude Code. So the wording of the description is the whole mechanism, which is exactly why it would be worth measuring properly.
