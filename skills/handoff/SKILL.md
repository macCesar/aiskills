---
name: handoff
description: 'Use only when the user explicitly invokes `$handoff`, `/handoff`, or asks for a HANDOFF.md by name. Writes a disposable HANDOFF.md at the repo root so a fresh session, after `/clear` or in another assistant, resumes the work without the previous conversation: goal and definition of done, state checked against git, files in flight, decisions, failed attempts with the exact error, what the user asked for along the way, and a Resume here block. Never activate on "ya me voy", "cierra la sesión" or "where did we leave off" — persistent project notes are `session-log`.'
---

# Handoff

The user only needs to invoke `/handoff`, `$handoff`, or ask for `HANDOFF.md`. Do not ask them to write a detailed prompt or repeat the session context; gather it from the conversation and inspect the repo yourself.

A long session accumulates two kinds of knowledge. The repo holds one: the diff, the commits, the files. The conversation holds the other: why this approach and not that one, what already failed and with what error, what the user asked for along the way. `/clear` throws the conversation away, and `/compact` keeps a lossy summary of it. `HANDOFF.md` carries the second kind across the reset, so the next session starts from the work instead of rediscovering it.

The file is disposable. It describes one moment, is read once by the next session, and is deleted. That is what separates it from `session-log`'s `status.md`, which is the project's permanent record and gets committed. A `HANDOFF.md` that lingers turns into a stale second copy of the state, so the file itself tells its reader to delete it.

## Before writing

Base the state on the repo, not on recall:

```bash
git status --short --branch
git diff --stat
git diff                      # read the hunks for the files in flight
git log --oneline -10
git rev-parse --short HEAD    # recorded in the file so the reader can detect drift
```

If this is not a git repo, say so in the file and describe the state from what you can inspect directly.

Then look at what the repo already documents. If `docs/project/` exists (the `session-log` convention), or the context file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) already explains the architecture, point at it instead of copying it: the reader loads those files anyway, and a copy made today disagrees with them tomorrow.

**Check whether the conversation was compacted.** If the early part of the session survives only as a summary, write that at the top of the file. Use what the summary states and leave out what it doesn't: a plausible failed attempt nobody made sends the next session chasing it, and a gap marked as a gap costs nothing.

## The file

Write `HANDOFF.md` at the repo root, in the language of the conversation. Overwrite any earlier one; there is only ever the current handoff. Omit a section that would be empty rather than writing "none".

```markdown
# HANDOFF — <YYYY-MM-DD HH:MM> · HEAD <short sha> · branch <name>

> For the session that reads this: check it against the repo before trusting it
> (`git log <sha>..HEAD`, `git status`). Anything that no longer matches, say so.
> Delete this file once you have read it; it is not project documentation.

<If compacted: "The conversation was compacted before this was written; history
before the summary is not available and attempts from that stretch may be missing.">

## Goal
What is being built or fixed, and how we will know it is done: the test that
passes, the screen that shows X, the command that returns Y.

## State
What works (and how that was verified), what is half-done, what is missing.
Whether it builds and whether tests pass, with the command and the result.
Anything not checked by running it is marked [NOT VERIFIED].

## Files in flight
- `path/to/file` — what changed, what is still pending in it.

## Decisions
- Chosen: X, because Y. Rejected: Z, because W.

## Tried and failed
- What was tried, why, what happened. The error verbatim:
  `REQUEST_DENIED: This API project is not authorized to use this API.`

## What the user asked for
Constraints and preferences stated during the session that the code does not
show: "no new dependencies", "don't touch the public API", "Spanish copy only".

## Resume here
1. Open: <files, in order>.
2. Do: <the exact next change — file, function, what it should do>.
3. Run: <the command or test that shows it worked, and the expected result>.
Then, in order:
- [ ] <next task>
- [ ] <next task>
```

Why each section earns its place:

- **Tried and failed** is the one the reader cannot rebuild. A dead end leaves no trace in the diff, so without it the obvious fix gets tried again. The error goes verbatim because a paraphrase can't be searched for or compared against the next failure.
- **What the user asked for** is what `/clear` loses first. Corrections and preferences live only in the conversation, and a fresh session that doesn't know them repeats the mistakes that produced them.
- **Resume here** is specific or it is useless. "Continue implementing the feature" makes the reader rediscover everything; "in `src/app.js`, replace the `TODO` in the `GET /rutas/:id/eta` handler with a haversine distance over `puntos`, then run `node --test test/eta.test.js`" lets it start working.
- **[NOT VERIFIED]** keeps a remembered claim from reading as a checked one. Once written down they look identical; the mark is the only thing that tells the reader which ones to re-check.

Keep it to what a reader absorbs in a couple of minutes. The file exists to be read by someone starting cold; one that runs to fifteen sections is skimmed, and the skimmed part is the part that mattered.

## After writing

`HANDOFF.md` must not be committed. Check whether git would pick it up:

```bash
git check-ignore -q HANDOFF.md && echo ignored || echo "not ignored"
```

If it is not ignored, don't edit `.gitignore` on your own; say in the reply that the file is untracked and should stay out of any commit, since a `git add -A` would sweep it in.

Don't commit, stash, reset or discard anything else either. The uncommitted work is the handoff's subject, and the next session needs it exactly as it is.

Close with the path, a two-line summary of where things stand, and the next step, then tell the user they can `/clear` (or open the next assistant) and start with: *read HANDOFF.md and continue*.
