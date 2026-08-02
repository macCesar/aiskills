# The four files

Read this when installing the convention in a project or migrating one that keeps
its notes somewhere else.

<!-- TOC-START -->
## Contents

- [Layout](#layout)
- [The pointer block](#the-pointer-block)
- [Two variants](#two-variants)
- [Repos that come in pairs](#repos-that-come-in-pairs)
- [Templates](#templates)
- [Migrating an existing project](#migrating-an-existing-project)
- [Sizing](#sizing)

<!-- TOC-END -->

## Layout

```
docs/project/
  status.md        VOLATILE — never imported, read on demand
  requirements.md  STABLE   — imported at startup
  decisions.md     STABLE   — imported at startup
  context.md       STABLE   — imported at startup

CLAUDE.md   ┐
AGENTS.md   ├─ each gets the same short pointer block
GEMINI.md   ┘

CHANGELOG.md   untouched — that's the release record, not the session record
```

Same names in every project. That's what makes them findable without asking.

## The pointer block

Identical in every context file. Keep it this short — duplicated prose drifts,
three lines don't.

```markdown
## Project state

- `docs/project/requirements.md` — what the system must do
- `docs/project/context.md` — architecture and conventions
- `docs/project/decisions.md` — what was decided and why
- `docs/project/status.md` — where the work stands right now

Read `status.md` when resuming work. Do not import it at startup: it changes
constantly, and loading it invalidates the cached prefix behind it.
```

Where the tool supports imports, import the three stable files:

```markdown
@docs/project/requirements.md
@docs/project/context.md
@docs/project/decisions.md
```

Never `@docs/project/status.md`. That single line is the difference between a
cache that survives and one that gets thrown away on every update.

## Two variants

### One repo, several packages

A monorepo takes the opposite answer from two sibling repos: **one `docs/project/`
at the root**, with a heading per package.

```
docs/project/
  status.md        ## apps/api   ## apps/web   ## packages/ui
  requirements.md  same headings
```

Sibling repos get their own files because each has its own branch, its own deploy
state and its own history — three things that go stale independently. A monorepo has
one of each. Splitting the notes per package there would invent a boundary git
doesn't have, and the cross-package work — the half that actually goes wrong, the
API change that breaks the web build — would have no obvious home.

The vocabulary rule is unchanged: `apps/api` is a heading, not a directory of notes.

### More than one person writing

`status.md` is rewritten whole, by whoever is working, every session. Two people or
two live branches means merge conflicts in it, reliably. That's a fact to plan for
rather than a flaw to design around, because both obvious fixes are worse:

| Tempting fix | What it costs |
| --- | --- |
| A file per person (`status-cesar.md`) | Scattered notes again, with extra steps |
| `.gitignore` it | The notes never reach the person they were written for |
| Only the lead updates it | It goes stale the first week the lead is busy |

Resolve conflicts by **keeping both sides and merging by section** — two people's
"In flight" entries are both true, and whichever loses a conflict is information
nobody gets back. If the friction is constant rather than occasional, the team wants
a heading per workstream inside the file. Still one file.

## Repos that come in pairs

A web backend and the mobile client that consumes it. The mechanics of installing
and closing both are in the skill; what follows is the detail that didn't need to
load every session.

**Install from inside each repo, separately.** Open the backend, install; open the
app, install. It's a one-time act per repo and it's worth doing from the right
place: sitting inside the project means its own context file loads, its own MCP
servers connect, and its stack-specific skills detect themselves. Installing a
repo's notes from its sibling means describing a project you're looking at from
outside — and the result reads like it, because the detail that makes `context.md`
useful is exactly what you don't see from across the fence.

Put the sibling's **path** in the header of `status.md`, not just its name, so
whoever reads it next can actually go there:

```markdown
**Sibling:** `../../Apps/EM Industrial` (Titanium client) — waiting on
`/work-orders/{id}/progress`, not built here yet.
```

**Once both are installed, updating them from one session is fine** — that's the
day-to-day case, and it's different from installing. The files already exist and
carry the project's own vocabulary; you're appending what changed, not inventing a
description of a repo you can't see.

Write the sibling's status from what you did to it, not from what you assume about
it. "Added the client call for `/work-orders/{id}/progress`" is something you know.
"The app is now feature-complete for E5" is something the app would have to tell
you. And if the sibling isn't reachable from where you're working, say so in the
handoff rather than guessing: "endpoint added here; the app side needs its status
updated, I couldn't reach that repo" is honest and actionable. A confident claim
about a repo you didn't open is neither.

## Templates

### `docs/project/status.md`

The only file that changes every session. Keep it short enough that someone
actually reads it.

```markdown
# Status — <YYYY-MM-DD>

**Phase:** <proposal · requirements · design · build · testing · live>
**Deployed:** <what's in production and since when — or "nothing yet">
**Branch:** <branch, and whether it's pushed>
**Sibling:** <other repo of this same project, and what it's waiting on — omit
              when the project is a single repo>

## Where things stand
<Two or three sentences. Outcomes, not a file list.>

## In flight
- <What's half-done, and which half works.>

## Blocked by others
- <Waiting on a client, a store review, a provider. Who, on what, since when.>
  <Omit this section entirely when nothing is blocked.>

## Requirements
<One line per requirement with its state, referencing requirements.md by number.
 This is where "how much is left" gets answered.>

## Next step
<The exact route, symbol or file to create or change — not an area.>

## Verified vs. assumed
- Verified: <what actually ran, with the result>
- Assumed: <what was not checked>

## Known pending
- <Things spotted but not started. Delete them as they get picked up.>
```

Absolute dates, never "yesterday" — the file outlives the session that wrote it.

The three header lines exist because they're the questions asked first and
answered worst. **Deployed is not the same as committed**: on a project that
deploys by file sync, a change can be live and uncommitted, or committed and never
uploaded. Write what you know and mark what you don't; a confident wrong answer
here sends someone debugging the wrong copy of the code.

### `docs/project/requirements.md`

The contract: what the system must do and how you'd know it does. Stable — it
changes when scope changes, not when work happens. **Progress lives in
`status.md`**, not here.

```markdown
# Requirements

Source: <path to the PRD, proposal or checklist this indexes — or "this file"
if nothing else exists>

## <Area — module, phase, whatever this project calls its parts>

| # | Must do | Accepted when |
| --- | --- | --- |
| 1 | <capability, in the client's terms> | <a checkable condition> |
| 2 | <…> | <…> |

## <Next area>

| # | Must do | Accepted when |
| --- | --- | --- |
| 3 | <…> | <…> |

## Invariants
- <A property that must not break, and what breaking it would look like.>

## Out of scope
- <What was explicitly agreed as not included. Prevents the argument later.>

## Unspecified
- <Things known to be needed but not yet pinned down. A requirement with no
  acceptance criterion belongs here, not in the table above.>
```

**Invariants** are for projects where the risk isn't forgetting a feature — it's
breaking a property while improving something else. Offline-first, no polling, a
storage schema other code depends on, a latency budget. They read like
conventions but they're stronger: a convention is how the team writes code, an
invariant is a promise the system makes. Write what breaking it would look like,
not just the rule, so it's recognizable when someone is about to do it.

Not every project has them. Skip the section when the honest answer is that
nothing here is that load-bearing.

**When the requirements live in another repo**, this file is an index pointing
outward rather than a self-contained contract — half its rows may reference
`../other-repo/…`. That's correct: copying the spec across creates a second copy
that drifts. Say plainly at the top which repo owns the contract.

Write acceptance criteria you could hand to someone else to check. "Payments
work" is not one; "charging a member writes a Payment row and the receipt shows
the folio" is. If you can't write one, the requirement isn't specified — say so
in **Unspecified** rather than pretending the table is complete.

The **Out of scope** section earns its place on client work: it's the cheapest
insurance against a disagreement six weeks later about what was included.

### `docs/project/decisions.md`

Append-only. Old entries stay even when superseded; a decision that was reversed
is more informative than one that was deleted.

```markdown
## <YYYY-MM-DD> — <the decision in one line>

**Chose:** <what>
**Over:** <the alternatives considered>
**Because:** <the reasoning, including the constraints that mattered>
**Reverses:** <link to an earlier entry, when applicable>
```

**When the date isn't knowable**, don't invent one. A repo with a single commit,
or everything still under `[Unreleased]`, has real decisions with no traceable
date — and stamping them with the commit date is a fabrication that later reads
as fact. Put them in a separate section that says why:

```markdown
## Decisions without a traceable date

These predate any usable history (single commit / nothing released yet). The
reasoning is recovered from the code and the docs; the dates are not known.

### <the decision in one line>
**Chose / Over / Because:** <as above>
```

These are usually the most valuable entries in the file, because they're the ones
that explain why the code doesn't match the spec. Losing them to keep the template
tidy is the wrong trade.

**Archiving.** Append-only and imported-at-startup is a combination with a shelf
life: every session pays for the whole file, and most of what it's paying for is a
decision from two years ago that nobody is about to revisit.

Past roughly two hundred lines, split it:

```
docs/project/decisions.md          current year — imported
docs/project/decisions-archive.md  everything older — NOT imported
```

Move entries oldest-first, keep them verbatim, and leave a line at the top of
`decisions.md` saying where the rest went. Then check the import chain again — the
archive must not be pulled in by any `@` line, or the split bought nothing.

Two rules keep the archive honest. A superseded entry stays with its reverser, even
if that means keeping an old entry in the current file — a reversal that outlives
the decision it reversed reads as if the original never happened. And an entry the
project still argues about is current by definition, whatever its date.

Two hundred lines is a prompt to look, not a threshold to enforce. A project with
twelve decisions in four years never needs this.

### `docs/project/context.md`

How the project is put together, and what a newcomer would get wrong on day one.
Anything derivable from reading the code doesn't belong here — this is for what
the code *doesn't* say.

```markdown
# Context

## Documentation map
| Document | What it covers | When you need it |
| --- | --- | --- |
| `docs/<file>.md` | <one line> | <before doing X> |

## Architecture
<How the pieces fit. Where things go and why.>

## Conventions
- <Rule.> — <why it exists; a rule without a reason gets ignored>

## Traps
- <The thing that cost someone a day, and how to avoid it.>
```

The map goes first because it's what someone new needs first: knowing what exists
saves them from rewriting it. List every document you found, including the ones
that turned out to be stale — marked as stale. A document omitted from the map is
a document nobody will open again.

## Migrating an existing project

Projects that already keep notes somewhere — `.claude/memory/`, a roadmap under
`docs/`, a planning doc — get migrated rather than duplicated. Two locations is
the problem this convention exists to solve.

1. **Read what's there** and sort it: is this line status, a decision, or context?
   Most existing notes are a mix, and that's exactly why they're hard to use.
2. **Split it into the four files.** Status goes to `status.md` even if it was
   living in an imported file — especially then.
3. **Delete the old location** and update anything that referenced it, including
   `@import` lines in context files.
4. **Add the pointer block** to every context file.
5. **Tell the person what moved where**, concretely. They need to be able to check
   that nothing was lost, and a migration they can't audit is one they won't trust.

If the project has a planning doc with real structure — a numbered checklist, a
PRD — don't flatten it into `status.md`. Leave it where it is and reference it
from `status.md`. The convention is about knowing where to look, not about
destroying work that already has a shape.

### Upgrading an earlier version of this convention

Repos installed before the four-file layout settled look almost right and aren't:
a lone `docs/status/current.md`, a `docs/project/` holding three files named by
hand, an `estado-actual.md` next to a `decisiones.md`. This is an upgrade, not a
migration, and the difference matters — the content was written by someone who was
there, so it's correct until the repo contradicts it.

1. **`git mv` into the fixed names**, so the history follows the file. Copying and
   deleting loses the one thing that made the old file trustworthy.
2. **Split by volatility, not by topic.** The usual finding is a single file mixing
   a stable architecture description with three lines of "where I left off". The
   stable half goes to `context.md` or `requirements.md`; only the volatile half
   ends up in `status.md`.
3. **Update every pointer**, including `@import` lines and any reference from
   `README.md` or a sibling repo's header. A pointer to the old path is worse than
   no pointer: it resolves to nothing and looks maintained.
4. **Say what moved where**, path by path. An upgrade someone can't audit is one
   they won't trust, and this one moves files they wrote.

## Sizing

A repo with one commit doesn't need four files with nothing in them. Start with
whichever ones have content — often `requirements.md` and `status.md` early on,
`context.md` and `decisions.md` once the thing exists — and add the rest when
there's something real to put in them. A `decisions.md` whose only entry is the decision to keep decisions is a
file that exists to look organized.

**The pointer block lists the files that exist.** Listing all four from the start is
tempting — it shows the shape — but three of the four lines then point at nothing,
and a pointer that resolves to a missing file trains the next reader to distrust the
block. Add the line when the file arrives; it's one line, at the moment it becomes
true.
