# CLAUDE.md — aiskills

Project-specific instructions for Claude Code sessions working on this repo. These rules travel with the repo via git, unlike machine-local `~/.claude/projects/` memory which is lost when the repo is cloned elsewhere.

## Project state

- `docs/project/status.md` — where the work stands right now

Read it when resuming work. Do not import it at startup: it changes constantly,
and loading it invalidates the cached prefix behind it.

## What aiskills is

- An npm CLI (`@maccesar/aiskills`) + Claude Code plugin marketplace that ships 6 general-purpose AI coding assistant skills (audit-codebase, humaniza, refactoring-ui, session-log, stitch-showcase, vscode-extension-dev) and 1 slash command (`release`).
- Distribution channels:
  - **npm**: `npm install -g @maccesar/aiskills` then `aiskills install` (works with Claude Code, Gemini CLI, Codex CLI).
  - **Claude Code plugin marketplace**: `/plugin marketplace add macCesar/aiskills` then `/plugin install aiskills@maccesar-aiskills` (Claude Code only).
- Architecture: ESM modules under `lib/`, commands in `lib/commands/`, CLI entry in `bin/aiskills.js`, skills live in `skills/<name>/SKILL.md` with optional `references/`, `assets/`, `scripts/`. Slash commands live in `commands/<name>.md`.

## Release checklist (mandatory)

Every release that ships code or skill changes must bump **BOTH** version files and keep them in sync:

1. Code + tests green.
2. Update `CHANGELOG.md` with the new version entry.
3. Bump `package.json` → `"version"`.
4. Bump `.claude-plugin/plugin.json` → `"version"` to the **same number**.
5. Single commit including both bumps.
6. Tag `vX.Y.Z` pointing at that commit.
7. Push `main` + push the tag.
8. `npm publish --access public`.

The bundled `/release` slash command automates 2–7 end-to-end. Step 8 (the npm publish) is intentionally manual so the maintainer can confirm the diff before publishing.

### Why both bumps matter

Claude Code caches marketplace-installed plugins in `~/.claude/plugins/cache/`. It compares the `version` field in `plugin.json` to decide whether to invalidate the cache. **If the code changes but `plugin.json` version does not, marketplace users keep the stale cached code** even after you push to GitHub.

Anthropic's exact wording: *"If you change your plugin's code but don't bump the version in `plugin.json`, your plugin's existing users won't see your changes due to caching."*

### Precedent (do not repeat)

The sibling repo TiTools shipped v2.6.0 with `plugin.json` frozen at `3.0.0` (pre-existing value from a feature branch). npm published 2.6.0 but the marketplace announced 3.0.0. Had to sync manually and amend the release. Both repos share the same `lib/` and the same release mechanics, so the rule applies identically here: **always sync before the release commit**.

### How a release propagates to each install channel (verified 2026-07-13, v1.15.0)

`npm publish` is **not** the whole story. A release reaches users through two independent channels, and `npm publish` only feeds one of them. Confirmed empirically when shipping `audit-codebase`:

- **npm channel** (`~/.agents/skills/`) — used by Gemini CLI, Codex CLI, and Claude Code via symlink. Updated by `npm update -g @maccesar/aiskills` (for end users) then **one** of `aiskills update` / `aiskills install` (not both — `update` already re-syncs skills). The maintainer's own CLI is `npm link`-ed to this repo, so on the maintainer's machine `aiskills install` reads straight from the dev repo — `npm publish` is only for *other* npm users, not to refresh the maintainer's own box.
- **Marketplace channel** (`~/.claude/plugins/cache/maccesar-aiskills/`) — used by Claude Code plugin installs (`aiskills:<skill>` prefix). **`npm publish` does nothing here.** It updates only inside Claude Code.

Marketplace channel facts (not in Anthropic's docs — confirmed by inspecting the cache):

- **Third-party marketplaces do NOT auto-update by default** (only official Anthropic ones do). So a release does *not* appear "tomorrow" on its own. Enable auto-update once via `/plugin` → Marketplaces → `maccesar-aiskills` → Enable auto-update, or refresh manually every release.
- The refresh command is **`/plugin marketplace update maccesar-aiskills`** (does the `git pull`), then **`/reload-plugins`** to apply in the live session. There is **no** `/plugin update <plugin>` command.
- The `source` in `marketplace.json` is `{github, repo}` with **no pinned version**, so the update tracks the **default-branch HEAD**, not the latest git tag. It moves to whatever `plugin.json` says at HEAD and **ignores the numeric version of the stale cache** — e.g. a leftover `2.0.0/` cache did not block moving to `1.15.0/`. (This is why the `plugin.json` bump still matters for *end users* whose cache compares versions, but the maintainer's `/plugin marketplace update` always jumps to HEAD.)
- **Duplicate-symlink cleanup:** while a new skill exists only on npm (not yet in the marketplace cache), `aiskills install` creates a `~/.claude/skills/<skill>` symlink so Claude Code sees it. Once the marketplace cache catches up (after `/plugin marketplace update`) and the user re-runs `aiskills install`, the CLI detects the marketplace now provides it and **removes that symlink** to avoid the "skill conflict" duplicate — leaving it marketplace-only, like the other skills.

**Full post-release sequence to refresh every channel on the maintainer's machine:** `/release` → `npm publish` (manual, 2FA) → `/plugin marketplace update maccesar-aiskills` → `aiskills install` → `/reload-plugins`.

## Code conventions

### Claude Code hooks format in `settings.json`

If a hook is added in the future, hooks must use the nested format:

```json
{
  "hooks": [
    { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh" }
  ]
}
```

NOT the flat `{ "command": "...", "timeout": 30000 }` format. The flat form causes a settings validation error on session start (caused TiTools's v2.4.0 → v2.4.1 hotfix; same `lib/`, same rule).

### `ora` spinner + child processes

When wrapping a shell command with `ora`, always use the async form:

```js
import { promisify } from 'node:util';
import { execFile } from 'node:child_process';
const run = promisify(execFile);
await run('npm', ['update', '-g', ...]);
```

Never `execFileSync` — it blocks the Node.js event loop, freezing the spinner animation (static dot instead of spinning). Same root cause as TiTools's v2.4.2 hotfix.

## Skill patterns

### Documentation-grounded skill template

`refactoring-ui` and `vscode-extension-dev` follow the same structural template — both are advisory skills that ground their answers in a body of external documentation (a book, an API reference). When adding a new skill of this kind, copy the structure below instead of reinventing it. If you change the contract here, update both existing skills to match.

The template, in `SKILL.md`:

1. **Step 1 — Open the relevant reference files**: a `| Task involves | Required reading |` table that routes each topic to a specific `references/<file>.md`. Keep one topic per row, granular enough that a typical question loads one reference, not the whole set.
2. **Step 2 — Output contract**: every cited rule, value, API, or behavior must include `[source: references/<file>.md]`. Show one literal example.
3. **Step 3 — FROM_MEMORY fallback**: if the model answers without having read the reference that backs the claim, it must prepend `FROM_MEMORY (unverified):` to that claim. Do not hide it.
4. **Banned behaviors**: a short bullet list of things the skill must never do (invent values not in references, reproduce source prose verbatim, mix in unrelated doctrines, mark answer complete without listing read references).
5. **Anti-Patterns**: a table or bullet list of common mistakes in the domain. **Each anti-pattern should cite `[source: references/<file>.md]`** — same contract Step 2 enforces on responses.

Existing instances:

- `skills/refactoring-ui/SKILL.md` — grounded in *Refactoring UI* by Adam Wathan & Steve Schoger
- `skills/vscode-extension-dev/SKILL.md` — grounded in https://code.visualstudio.com/api

If a third advisory skill arrives, copy from one of these and keep the contract identical so users get the same answer shape across skills.

## Parallel project: `TiTools`

`@maccesar/titools` lives at `~/Developer/openSource/TiTools` and shares **identical** `lib/` infrastructure (Commander.js, ora, chalk, ESM, same install paths, same symlink pattern). Only the `skills/` contents differ — TiTools ships Titanium SDK-specific skills (purgetss, ti-expert, ti-ui, ti-api, ti-howtos, alloy-guides, alloy-howtos, ti-create-release, ti-module-update) plus a `ti-pro` agent and a SessionStart hook that injects a Titanium Knowledge Index. aiskills ships general-purpose skills.

**When implementing features in aiskills, consider porting the equivalent to TiTools in the same session** — adapted to add Titanium-specific pieces (Knowledge Index, `tiapp.xml` detection, SessionStart hook) if they apply.

### Long-term direction

User intends to eventually merge TiTools + aiskills into a single CLI with skill categories (e.g. `aiskills install --only ti`, `--only ui`). Maintaining two near-duplicate codebases is a known tax. When that consolidation happens, the marketplace would either become one plugin with all skills or multiple plugins under one marketplace manifest.

## Testing

Tests live under `test/` using Node's built-in test runner (`node:test`):

```bash
npm test                        # all suites
node --test test/list.test.js   # single file
```

Add tests whenever a new command or skill-scripted behavior ships. Skills that include executable scripts should have tests covering: frontmatter validity, CLI help output, argument validation, shell syntax of any bash scripts.

## Files worth knowing

- `lib/config.js:SKILLS` — hardcoded list of which skills to install. Keep in sync when adding/removing a skill.
- `lib/config.js:LEGACY_SKILLS` — skills to actively remove during updates/uninstall. Use this when deprecating a skill so existing users get it cleaned up on their next `aiskills update`.
- `lib/config.js:COMMANDS` — slash commands installed to `~/.claude/commands/` (Claude Code only). Keep in sync when adding/removing a command file in `commands/`.
- `lib/config.js:LEGACY_COMMANDS` — commands to actively remove on update/uninstall.
- `lib/utils.js` — shared helpers used by every command in `lib/commands/`.
