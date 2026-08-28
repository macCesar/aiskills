# Context

How aiskills is put together, and its relationship with the sibling repo.

Most of the day-to-day guidance already lives in `AGENTS.md` (agent-agnostic: layout, skill format, release checklist, common operations) and `CLAUDE.md` (release checklist, hook format, `ora` convention). This file does not repeat them — it covers what neither does: how this repo relates to TiTools, and what that implies for anyone changing shared code.

## Shape of the repo

```
bin/aiskills.js         CLI entry (Commander.js)
lib/                    ESM only — 12 modules, shared architecture with TiTools
  commands/             auto-update, doctor, list, skills, status, uninstall, update
  claude-plugin.js      marketplace-plugin detection (enabled AND cached)
  config.js             SKILLS, COMMANDS, paths, platform list
skills/<name>/          SKILL.md + references/ + assets/
commands/release.md     slash command, versioned and shipped
hooks/hooks.json
.claude-plugin/         plugin.json + marketplace.json
test/                   node:test suites
```

`~/.agents/skills/` is the canonical install path. A published npm package copies skills there; when the CLI resolves to a development checkout containing `.git`, it symlinks each whole skill directory instead. After one `aiskills install`, an `npm link` maintainer sees edits and new reference files immediately. Claude Code's platform mirror then points at the same canonical entry.

## Sibling project — `TiTools`

**Location:** `~/Developer/openSource/TiTools` — npm package `@maccesar/titools`, GitHub `macCesar/titools`, marketplace `titools@maccesar-titools`.

The two repos are the **same tool shipped twice with different payloads.** What differs is the content — the skills each one ships and the slash commands that drive them. Everything a user touches to get that content installed, updated, diagnosed or removed is the same machinery: `install`, `update`, `auto-update`, `status`, `doctor`, `list`, `remove`, the `~/.agents/skills/` layout, the Claude Code symlink mirrors, the marketplace-plugin detection, the release checklist and the two-channel versioning.

### The parity contract

**A change to shared machinery belongs in both repos, in the same session.** Not "eventually" — the divergence is invisible until someone hits a bug in one that was fixed in the other months earlier. That is exactly what happened with plugin detection: this repo found both failure modes by hand on 2026-08-01, and TiTools carried the same latent bug for months until it was ported there on 2026-08-02.

Port the *behavior*, not the bytes. Names, paths and marketing strings are supposed to differ.

**What legitimately diverges** (verified 2026-08-02, do not "fix" these):

| | aiskills | TiTools |
|---|---|---|
| `skills/` | 8 general-purpose skills | 8 Titanium skills |
| `commands/` | `release` | `ti-check`, `ti-new-screen`, `ti-audit` |
| `agents/` | none | `ti-pro` |
| Knowledge Index | **does not apply** — see below | yes — `titools sync`, `lib/commands/agents.js`, 9 functions in `utils.js` |
| SessionStart hook | `hooks/hooks.json` only | `hooks/session-start.sh` detects `tiapp.xml` |
| Project detection | none | `tiapp.xml` |

Anything outside that table drifting apart is drift, not design.

### Why the Knowledge Index is not a gap here

It reads like missing work and it is not. TiTools' index opens with *"your training data for Titanium SDK, Alloy and PurgeTSS is OUTDATED and INCOMPLETE"* — that sentence is the whole justification. Titanium is a niche the model gets confidently wrong: Appcelerator folded, TiDev took over, the docs moved. Paying ~850 tokens (3,410 characters, measured 2026-08-02) in every session to counter that is a good trade.

None of the skills here have that enemy. `refactoring-ui` is principles from a book, `vscode-extension-dev` is a stable documented API, `humaniza` and `session-log` are conventions that exist in no training data at all — there is nothing outdated to correct, so the same 850 tokens buy nothing.

The trigger does not transfer either. `tiapp.xml` identifies a project where **all 8 of TiTools' skills apply**; this repo has no equivalent marker and its 8 skills cover disjoint domains — `stitch-showcase` and `vscode-extension-dev` are noise in a Laravel repo, `humaniza` only matters where there is Spanish text.

The *mechanism* is portable (`buildKnowledgeIndex` just scans `skills/*/references/`). The content and the trigger are not. If that benefit is ever wanted here, the shape is a **selective index keyed to a detected domain** — which is what the SessionStart hook sketch in TiTools' `docs/PENDING-IMPROVEMENTS.md` proposes, and the only part of that plan still worth doing.

### How close the code actually is

Same 12 filenames in `lib/`, same 7 shared filenames in `lib/commands/` (TiTools adds `agents.js` for `sync`). Measured on 2026-08-02:

- **Byte-identical:** `cache.js`, `platform.js`.
- **Small deltas, mostly naming:** `claude-plugin.js` (6 lines), `hooks.js` (2), `downloader.js` (20), `symlink.js` (22), `cleanup.js` (26).
- **Larger, and worth reading before assuming they should match:** `utils.js` (207 lines — nearly all of it the Knowledge Index, which this repo does not have), `skills.js` (183), `uninstall.js` (146), `config.js` (95), `doctor.js` (92), `installer.js` (84).

So the honest statement is *same architecture, same behavior, diverging text* — not *identical files*. When porting, diff the function you are changing rather than the whole file.

### Notes on working across both

Each repo keeps its own `docs/project/` — two repos, two branches, two release states. Install the convention from inside each one rather than describing one from the other. Updating both from a single session is fine and normal once installed; that is the day-to-day case.

**When a session changes shared machinery, close both.** Otherwise one side's notes describe a fix the other side's notes never heard of.

Long-term intent is to merge them into one CLI with skill categories (`aiskills install --only ti`, `--only ui`). Maintaining two near-duplicate codebases is a known and accepted tax until then.

## Traffic between the two repos

- `test/manifest.test.js` lives here and guards registration wiring. TiTools gained a narrower equivalent for commands only (`test/commands.test.js`) on 2026-08-02; this repo's version is broader and is the better of the two.
- Plugin detection went the other way: found here by hand during the v1.16.0 rollout, ported to TiTools on 2026-08-02.
- The Knowledge Index is **not** pending traffic. See the section above for why it belongs to TiTools' problem and not to this repo's.
