---
name: session-log
description: 'The convention that decides WHERE a project keeps its working state, and why part of it must not load at startup. Four fixed files under docs/project/ — status (volatile, never imported), requirements, decisions, context (stable, imported) — plus a pointer written into every context file the repo has, so the notes are findable from Claude Code, Codex or Gemini alike. Use this whenever someone closes a working session or picks one up ("ya me voy, déjame anotado dónde quedé", "where did we leave off?"), asks where project notes should live or why they keep ending up scattered, wonders whether progress and dates belong inside CLAUDE.md / AGENTS.md / GEMINI.md, or wants project tracking set up or migrated — even when they never say "notes" or name this skill. Not for: releases and version bumps, commit messages, CHANGELOG entries, build or deploy status, issue trackers, or a spoken recap the user only wants to read.'
---

# Session Log

Work spans sessions; context does not. Notes end up scattered — some in a context
file, some in a README, some in a doc nobody opens — so neither the person nor the
next assistant knows where to look.

This skill fixes that with one fixed convention, installed once per project. After
that, finding the notes no longer depends on this skill at all: any assistant that
reads the repo's context file finds the pointer and knows where everything lives.
That's the point — the convention has to survive being used by tools that never
heard of it.

## The convention

Four files, always the same names, always the same place:

```
docs/project/
  status.md        Where the work stands right now. Half-done things,
                   next step, what's blocked, deployment state.
                   VOLATILE — never loaded at startup.

  requirements.md  What the system must do, and how you'd know it does.
                   The contract. STABLE — loaded at startup.

  decisions.md     What was chosen and why. Append-only, dated.
                   STABLE — loaded at startup.

  context.md       How the project is put together: documentation map,
                   architecture, conventions, the traps that cost a day.
                   STABLE — loaded at startup.
```

The split between `requirements.md` and `status.md` is deliberate and easy to get
wrong. **The contract goes in requirements; the progress goes in status.** What a
feature must do changes when the scope changes — rarely. Whether it's finished
changes constantly. Putting them in one file means the contract gets rewritten
every day, which invalidates the cached prefix behind it: the exact failure this
convention exists to prevent.

Fixed names are the whole point. A convention that adapts per project isn't a
convention — it's the scattered-notes problem with extra steps. Someone opening
any repo should know where to look without reading anything first.

### The client's vocabulary goes in the content, never in the paths

Projects grow words: *modules*, *phases*, *blocks*, *deliverables*, *sprints*.
Those words usually come from a conversation with whoever is paying — someone said
"the work orders module" and it stuck. That's fine as a way to talk. It's a
mistake as a directory structure.

The moment the vocabulary becomes folders, two things happen. The layout stops
being predictable across projects, because the next client uses a different word.
And renaming becomes expensive, so the structure outlives the conversation that
produced it — you end up with `docs/modulos/modulo-3-.../02-implementacion/` in
one repo and `documentacion-importante/backend/` in another, both reasonable when
they were created and neither findable from the outside.

So: the four files are always the four files. Parts of the project are **headings
inside them** — a section per module in `requirements.md`, a line per module in
`status.md`. When the vocabulary changes, you edit a heading instead of moving a
tree.

This also keeps the depth. A project with real modules still gets a detailed
breakdown; it just lives under a heading rather than a path.

### Never put the date in the filename

`status-2026-07-21.md`, `resumen-avances-julio.md`, `progreso-etapa-1.md` — each
one is a session that created a new file instead of updating the existing one.
After a month there are twenty and none of them is *the current one*; finding out
which is means opening several and comparing dates. That's the scattered-notes
problem reappearing inside the folder that was supposed to solve it.

The date goes **inside** `status.md`, at the top, and the file is overwritten.
History is what git is for: `git log docs/project/status.md` gives you every past
state, with its date, for free.

The same applies to anything that sounds like a holding area — `to-review/`,
`pending/`, `notes-temp/`. A file whose location says "somebody should look at
this eventually" gets neither read nor deleted. Either it's current and belongs in
one of the four files, or it's stale and should say so.

### When the project spans more than one repo

A system with a web backend and a mobile client is one project in two
repositories. Very often it's also **one working session**: someone adds an
endpoint on the API side and, without switching context, wires the app that
consumes it. The work is a single thought; only the folders are separate.

**Install from inside each repo, separately.** Open the backend, install; open the
app, install. It's a one-time act per repo and it's worth doing from the right
place: sitting inside the project means its own context file loads, its own MCP
servers connect, and its stack-specific skills detect themselves. Installing a
repo's notes from its sibling means describing a project you're looking at from
outside — and the result reads like it, because the detail that makes `context.md`
useful is exactly what you don't see from across the fence.

Each keeps its own `status.md` — two repos have two branches, two deploy states
and two histories, and one shared file would go stale on whichever side isn't
being edited.

Put the sibling's **path** in the header, not just its name, so whoever reads it
next can actually go there:

```markdown
**Sibling:** `../../Apps/EM Industrial` (Titanium client) — waiting on
`/work-orders/{id}/progress`, not built here yet.
```

**Once both are installed, updating them from one session is fine** — that's the
day-to-day case, and it's different from installing. The files already exist and
carry the project's own vocabulary; you're appending what changed, not inventing
a description of a repo you can't see.

**When a session touched both, close both.** This is the part that gets skipped,
and it's where the two halves drift into separate realities: the mobile notes say
"waiting on the API" for three weeks while the backend's notes never mention that
anything is waiting. If you added the endpoint and consumed it in the same
session, both `status.md` files changed — write both before finishing.

Even then, write the sibling's status from what you did to it, not from what you
assume about it. "Added the client call for `/work-orders/{id}/progress`" is
something you know. "The app is now feature-complete for E5" is something the app
would have to tell you.

If the sibling isn't reachable from where you're working, say so in the handoff
rather than guessing at its state. "Endpoint added here; the app side needs its
status updated, I couldn't reach that repo" is honest and actionable. A confident
claim about a repo you didn't open is neither.

A **monorepo** is the opposite case and takes the opposite answer — one
`docs/project/` at the root, packages as headings — because one repo has one branch,
one deploy and one history to describe. And `status.md` being rewritten whole every
session makes it **conflict-prone the moment a second person or branch touches it**.
Both cases are in `references/file-layout.md`; neither comes up on a project with one
person and one branch, which is most of them.

### Why status.md is not loaded at startup

Context files load at the start of every session, along with everything they
import. Cached context is matched as a **prefix**: byte by byte from the start,
and the first byte that differs invalidates everything after it.

So a status line inside a startup-loaded file means every update to that line
throws away the cache for all the stable content behind it — content that didn't
change. The file you edit most often is the one that must not load at startup.

There's a second reason. Stable context is *instructions*: it shapes how the
assistant works. Status is *data*: it answers a question. Loading data as
instructions every session costs tokens and dilutes the instructions that matter.

`status.md` is read on demand — when someone resumes work and asks where things
stand. That's cheap, and it's when the information is actually wanted.

The same arithmetic catches `decisions.md` eventually. Append-only *and* imported
only works while the file is young; after two years it's a long document loaded in
full every session to answer a question nobody asked. Past roughly two hundred
lines, everything but the current year moves to `decisions-archive.md`, which is not
imported — nothing deleted, still searchable when someone needs it.
`references/file-layout.md` has the mechanics.

## Installing it

Write the same block into **every** context file the repo has. Not one; all of
them. Different people and different tools read different files, and a note only
one assistant can find is a note that disappears the day someone switches.

The usual ones are `CLAUDE.md`, `AGENTS.md` and `GEMINI.md`, but the list keeps
growing: `.github/copilot-instructions.md`, `.cursorrules` or `.cursor/rules/`,
`.windsurfrules`, `CONVENTIONS.md`. Write into the ones that exist rather than
creating new ones — a `GEMINI.md` invented for a repo where nobody uses Gemini is a
file that will rot unread, and the point is to reach the readers who are already
there.

Keep the block short. Duplicated text drifts out of sync — three lines that say
the same thing survive that; three paragraphs don't.

```markdown
## Project state

- `docs/project/requirements.md` — what the system must do
- `docs/project/context.md` — architecture and conventions
- `docs/project/decisions.md` — what was decided and why
- `docs/project/status.md` — where the work stands right now

Read `status.md` when resuming work. Do not import it at startup: it changes
constantly, and loading it invalidates the cached prefix behind it.
```

Import `requirements.md`, `context.md` and `decisions.md` if the tool supports
imports; leave `status.md` out of every import chain. Then create the files with real
content read from the repo, never placeholders — a template nobody filled in is
worse than nothing, because it looks maintained.

**Write the content in the language the project is already documented in.** The
templates here are in English because the skill is; the files are for whoever opens
the repo next. A `status.md` in English in a project whose README, commits and
client conversations are in Spanish is a small tax on every future read, and the
acceptance criteria are the part that suffers most — they're quoting what someone
actually agreed to, and translating that loses the words the agreement was made in.
File and section names stay fixed regardless; that's what makes them findable.

### Check that the location is actually tracked

Before writing anything, confirm the target path isn't ignored:

```bash
git check-ignore -v docs/project/status.md
```

Plenty of repos ignore `docs/` because they generate documentation into it. If
that's the case here, the notes you're about to write will look fine locally and
vanish on clone — the failure is silent, and it surfaces weeks later when someone
else opens the project and finds nothing.

Fixing it needs care: git can't re-include a file whose parent directory is
excluded, so `!docs/project/` under a `docs/` rule does nothing. The pattern has
to exclude the *contents* instead:

```gitignore
docs/*
!docs/project/
```

If the repo ignores `docs/` for a reason you'd rather not touch, put the
convention somewhere tracked and say where — a predictable location that exists
beats a canonical one that doesn't.

### Tracked means published

Being tracked is the point and also the risk: these files get committed, pushed, and
on a public repo indexed. Session notes attract exactly what shouldn't travel — a
token pasted while debugging, a staging URL with credentials in it, a client's phone
number, the reason a particular customer is unhappy.

Write around it. "The API key is in 1Password under *Gym staging*" carries the same
information to the next session and none of the exposure; "blocked on the client's
approval" says what's blocked without narrating a conversation someone would rather
not find on GitHub. Anything that genuinely has to be verbatim belongs wherever the
project already keeps secrets, pointed at from `status.md`. Git makes this expensive
to undo — a secret deleted in a later commit is still in the history — so it's much
cheaper not to write it.

### Map the documentation that already exists

Before writing `context.md`, inventory what the project has documented: everything
under `docs/`, plus `README.md`, `CONTRIBUTING.md`, and any spec or plan sitting
elsewhere. Open each one far enough to say what it's for in a line.

Then put that map in `context.md` as a section — one line per document, saying
what it covers and when someone would need it. Not a file listing; a listing is
what `ls` already does. The value is in "read this before touching X".

This matters more than it looks. A repo usually has more documentation than
anyone remembers, and the parts nobody remembers are functionally lost — the same
scattered-notes problem, just with better-looking files. A doc that exists and
isn't referenced anywhere will be rediscovered by accident or rewritten from
scratch.

Two rules while mapping:

- **Reference, don't absorb.** A plan, a PRD, a numbered checklist has structure
  someone built on purpose. Point at it and say what it's for. Flattening it into
  `context.md` destroys the structure and creates a second copy that will drift.
- **Say when it's stale.** If a document contradicts the code, that's worth a line
  in the map — "describes the v2 schema, superseded by decisions.md 2026-07-31".
  A map that presents rotten docs as current is worse than no map.

Keep it current the same way: when a session adds or invalidates a document,
the map gets a line. That's cheap, and it's what keeps the map trustworthy.

Documents other tools generate belong in the map too, and they go missing fastest —
an audit report, a migration plan, a design review, read once and then the stalest
file in the repo. Map them **with the date they describe**: an audit of the codebase
as it stood three months ago is a historical record, not a to-do list, and whatever
survived from it should already be a line in `status.md` or an entry in
`decisions.md`.

**Migrating a project that already has notes elsewhere.** Move the content into
the four files, then delete the old location and point anything that referenced
it at the new place. Leaving both is how you get scattered notes again. Tell the
person exactly what moved where.

Templates and wiring detail: `references/file-layout.md`.

## Requirements: the denominator

"What's left?" is unanswerable without knowing what finished looks like. That's
what `requirements.md` is for, and it's the one file that lets you say how much
remains without inventing a number.

Most projects already have this somewhere — a PRD, a proposal, a numbered
checklist, an email thread that got pasted into a doc. **Reference it, don't
rewrite it.** `requirements.md` is an index: what the system must do, the
acceptance criterion for each item, and a pointer to wherever the detail lives.
If the project genuinely has nothing written, this is the file you write first —
before any code, and often before there's a repo worth speaking of.

An acceptance criterion is the useful half. "Payments work" isn't checkable;
"charging a member writes a Payment row and the receipt shows the folio" is. When
someone later asks whether a requirement is done, the criterion is what you
verify against — and if you can't write one, the requirement isn't specified yet,
which is itself worth recording.

### When there is no code yet

Proposal, requirements gathering, design — the work is real and it's exactly where
people forget where they left off, but there's no diff to verify against. Adapt
rather than skip: `requirements.md` and `decisions.md` carry the weight, `status.md`
records what the client agreed and what's still open, and verification runs against
the artifacts that do exist — a requirement that says "as agreed in the proposal"
can be checked against the proposal. Don't create empty files waiting for a phase
that hasn't arrived; `references/file-layout.md` covers how to size this down.

## Which job this is

Three jobs share this skill — install the convention, resume work, close a session —
and the first has a variant worth catching before you write anything. Which one it
is depends on the repo and on whether the person is arriving or leaving, not on how
the request was phrased. Look before deciding:

```bash
ls docs/project/                                    # installed already?
ls CLAUDE.md AGENTS.md GEMINI.md CONVENTIONS.md \
   .cursorrules .github/copilot-instructions.md     # which context files exist
ls -d .claude/memory .codex .gemini .cursor/rules   # notes living somewhere else
find docs -name "*.md" -not -path "docs/project/*"; ls README.md CONTRIBUTING.md
```

Read the output, not the exit status. These lines report "No such file" for whatever
is absent, and that *is* the answer — but a command that failed on a missing path
looks a lot like one that found nothing, and mistaking the two here is how you end
up installing on top of a setup that already existed.

**Nothing under `docs/project/`** — install the convention. Create the files that
have content, fill them from what you actually read in the repo, add the pointer
block to every context file found. If the third line turned something up, migrate
it in and delete the old location; two places is the problem this solves. Say
exactly what moved where, so the person can audit it.

**Something that is almost this convention** — a single `docs/status/current.md`, or
three of the four files under names someone chose by hand. That's an upgrade, not a
fresh install: rename into the fixed names, fold the content into the right file,
and update the pointer blocks that referenced the old paths. Treat the existing
content as correct until the repo says otherwise — it was written by someone who was
there.

**Already there and the person is arriving** — resume. That's the next section, and
it writes nothing unless they ask.

**Already there and the person is leaving** — close the session: update `status.md`,
and touch the other three only if something stable changed. That's "Closing a
session", below.

## Resuming work

"Where did we leave off?" is a read, and it's the moment `status.md` was written
for. It's also where the file is most likely to lie — it's a snapshot of the day it
was written, and nothing keeps it honest in between. Work landed, a branch got
merged, someone deployed. Check it against the repo before repeating it back:

```bash
git log -1 --format='%cd' --date=short -- docs/project/status.md   # when it was last committed
BASE=$(git log -1 --format=%H -- docs/project/status.md)
git log --oneline "$BASE"..HEAD                                    # what landed since
git branch --show-current                                          # versus the branch it names
git status --short                                                 # what's uncommitted now
```

If `BASE` comes back empty the file has never been committed, so the date at the top
of it is all you have — worth saying out loud, because an uncommitted `status.md`
also means it exists on exactly one machine.

Three kinds of drift are worth naming, because each one changes what to do next:

- **Commits landed after it was written.** The "next step" may already be done.
  Say how many and from when instead of reading a stale plan as current.
- **The branch moved.** A status naming `feature/payments` while HEAD is on `main`
  describes work that was merged, abandoned, or is sitting in a worktree — three
  very different situations, and the file can't tell you which.
- **The tree is dirty in ways the file never mentions.** Uncommitted work from a
  session that ended without closing, which is the usual reason someone can't
  remember where they were.

Then answer what was asked: where things stand, what's in flight, the next step, and
which parts of the file you couldn't confirm. Keep it to what someone reads in
fifteen seconds — they asked to be caught up, not to be handed the file back.

If the drift is bad enough that the file misleads, say so and offer to rewrite it.
Rewriting is a separate act and it's their call; arriving at a project shouldn't
silently overwrite the record of how it was left.

## Closing a session

The evidence comes first. Base what you write on this, not on recall of the
conversation:

```bash
git status --short          # what's still uncommitted
git log --oneline <base>..  # what landed
git diff --stat             # the shape of it
```

Write: **what changed** as outcomes, not a file list; **what's half-done**, naming
which half works; **the next step**; and **what was verified versus assumed** — if
tests ran, the numbers; if they never ran, say so, because an unqualified "done"
that turns out to be untested costs the next session an afternoon.

Three more things belong in `status.md` and are routinely left out:

- **What's deployed, and since when.** Shipped and committed are different states,
  and on projects that deploy by file sync rather than by git they drift apart
  constantly — a file can be live on the server and uncommitted, or committed and
  never uploaded. Never infer one from the other. Record what you actually know,
  and say when you don't know.
- **What's blocked by someone else.** A client who hasn't sent the copy, a store
  review, a provider whose sandbox is down. These read like pending work but
  can't be unblocked by working, so mixing them into the technical list makes the
  list lie about what's actionable.
- **Which phase the project is in** — proposal, requirements, design, build,
  testing, live. One line. It tells whoever arrives which of these files matters
  today.

Update `requirements.md`, `decisions.md` or `context.md` only when something
genuinely stable changed: scope moved, a choice was made, a new document appeared.
Most sessions change nothing there, and that's normal.

**When `status.md` grows, the cause is usually stable content that drifted in.**
The test is simple: would this text be the same next week? A test checklist, an
acceptance walkthrough, a list of platform-specific gotchas — those don't change
between sessions, so they belong in `requirements.md` or `context.md` even though
you're using them right now. Being *currently relevant* is not the same as being
*volatile*, and confusing the two is how the volatile file ends up carrying half
the project.

The next step points at them: "run the acceptance walkthrough for requirements
13–18" is a next step. Pasting the walkthrough into `status.md` means rewriting it
every session, which is both noise and the same cache problem in miniature.

### Follow the chain, not the checklist

This is where a skill like this one can make things worse. A procedure followed
carefully still produces a tidy record of a misunderstanding, and the failure
looks like competence: correct format, specific file names, confident next step —
resting on something that isn't there.

Before writing a next step, follow what it depends on. A plan to add a refund
route is worthless if nothing in the codebase ever persists a payment, and that
gap is invisible if you're working down a list instead of reading the code. Ask
what has to be true for the next step to be possible, then check that it is.

When the code and the plan disagree, the code wins and the note says so. "The
refund route can't be built yet — nothing writes a Payment record, so there's no
id to refund against" beats a well-formatted plan built on sand.

### Recording finished work

Check the claim before writing it down. Name the artifacts it implies, look for
those specific things, record what you found, and report the evidence with the
verdict — "found `PaymentGateway.php` and the `payments.*` routes" lets the person
catch a wrong conclusion; a bare "✅" doesn't.

Then **answer what was asked.** Someone asking you to mark work complete wants it
marked, not a lecture on epistemics. Record the part that checks out and note the
rest as open. Hedging everything into "implemented but unverified" and leaving the
file untouched is refusing the request while appearing thorough.

Per-stack specifics — Laravel, Titanium, Node, Python, Rails, Go — are in
`references/verification.md`.

### Closing is not permission to edit

You'll find real problems while taking inventory. Write them down and leave them.
The uncommitted tree is the person's work in progress; a fix applied while they
weren't looking is a fix they didn't review, landing in a diff they'll read
tomorrow as their own.

Same for publishing: don't commit, tag or push. Releasing assumes the work is
finished, which is the opposite of why this exists. A log entry says "auth is
half-wired, the form is missing"; a release note never says that. If the project
has a release path — a `/release` command, a documented procedure — name it and
stop there; deciding that this is the moment to run it is the person's call.

The same boundary holds in the other direction. `status.md` records that an audit
found twelve issues and where the report lives; it isn't the place to fix them, and
a session that quietly repaired three on the way past leaves a record that no longer
matches either the report or the diff.

## Before finishing

Resolve the import chain from each context file and confirm `status.md` isn't in
it. This is worth checking every time rather than assuming, because it breaks
quietly: someone adds an `@` line meaning well, and from then on every progress
update throws away the cached prefix behind it — the one failure this convention
exists to prevent.

Check it, don't eyeball it — and check the files the inventory actually found, not
a fixed list:

```bash
grep -n 'status\.md' CLAUDE.md AGENTS.md   # add whichever others exist
grep -rn '^@' CLAUDE.md AGENTS.md          # every import, including nested ones
```

A mention of `status.md` in the pointer block is correct and expected; an `@` line
pulling it in is the failure. Follow each `@` to its target and grep that file too —
the break usually happens one level down, where someone imported an index that
imports everything.

Naming a file that doesn't exist makes `grep` exit non-zero and print nothing, which
looks exactly like a clean result. If you list `GEMINI.md` on a repo that has no
`GEMINI.md`, you get silence and a failed command, and reading that as "no imports
found" is how a broken chain ships as verified.

Then close with a short summary in the person's language: where things stand,
what's half-done, the next step, and the paths you wrote. Fifteen seconds of
reading — the files hold the detail, and a handoff nobody reads is a handoff that
failed.
