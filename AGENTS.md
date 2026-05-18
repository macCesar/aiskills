# AGENTS.md

Guidance for AI agents — **Claude Code, Gemini CLI, Codex / OpenAI Codex CLI, GitHub Copilot CLI, and any other LLM-driven coding assistant** — working **inside** this repository.

If you are an agent invoked by a user to *use* a skill (e.g. "humanize this text", "review my UI"), read the relevant `skills/<name>/SKILL.md` directly and follow it — not this file.

## What this repo is

aiskills ships two things from a single source:

1. **An npm CLI** (`@maccesar/aiskills`) that installs and updates general-purpose AI coding assistant skills into `~/.agents/skills/` (universal) plus per-agent symlinks for Claude Code and Gemini CLI. Codex CLI auto-discovers `~/.agents/skills/` directly, so no Codex symlink is created.
2. **A Claude Code plugin marketplace** (`aiskills@maccesar-aiskills`) that exposes the same content plus slash commands as a plugin via `/plugin marketplace add macCesar/aiskills`.

Skills conform to the [agentskills.io specification](https://agentskills.io/specification) so any compatible agent can load them. The CLI itself is ESM Node.js with Commander.js and `ora` spinners.

Sibling project: **`@maccesar/titools`** at `~/Developer/openSource/TiTools` shares the same `lib/` infrastructure but ships Titanium SDK-specific skills (purgetss, ti-expert, ti-ui, ti-api, ti-howtos, alloy-guides, alloy-howtos, ti-create-release, ti-module-update) plus a `ti-pro` agent and a SessionStart hook. When you change `lib/`, consider porting the change there too — see [CLAUDE.md](CLAUDE.md) § "Parallel project: TiTools".

## Layout

```
.
├── README.md             # human-facing index
├── AGENTS.md             # this file (agent-agnostic guidance)
├── CLAUDE.md             # Claude Code-specific notes (release checklist, code conventions)
├── CHANGELOG.md
├── package.json          # npm publish manifest
├── .claude-plugin/
│   └── plugin.json       # Claude Code plugin manifest (version must match package.json)
├── bin/
│   └── aiskills.js       # CLI entry point
├── lib/                  # CLI source (ESM)
│   ├── commands/         # one file per CLI subcommand
│   ├── config.js         # SKILLS, COMMANDS lists, paths, platforms
│   ├── cleanup.js        # legacy artifact removal on update/uninstall
│   ├── utils.js          # helpers
│   └── platform.js
├── commands/
│   └── <name>.md         # slash commands shipped to Claude Code (~/.claude/commands/)
└── skills/
    └── <skill-name>/
        ├── SKILL.md      # required: skill entry point
        ├── references/   # optional: deep references
        └── assets/       # optional: scripts, templates
```

One skill per folder under `skills/`. The folder name **must** equal the `name:` field in the skill's YAML frontmatter (kebab-case, letters/digits/hyphens only).

## Skill format

Every `SKILL.md` starts with YAML frontmatter:

```markdown
---
name: <kebab-case-name>
description: Use when <triggering conditions, symptoms, file markers>. ~500 chars or less.
---

# <Skill title>

## Overview
What it is. Core principle in 1-2 sentences.

## When to use
Bullet triggers + when NOT to use.

## Workflow / Steps
...
```

Rules:

- **Frontmatter total ≤ 1024 chars.** See [agentskills.io/specification](https://agentskills.io/specification).
- `description` describes **when to use** the skill — concrete triggers, error messages, user requests — *not* a summary of the workflow. Future agents read the description to decide whether to load the full skill; a workflow summary may cause them to follow the summary instead of the skill.
- Start the description with `Use when…` (third person). For Spanish-targeted skills, `Úsalo cuando…` is the equivalent form.
- If the description contains `:` characters, wrap it in single or double quotes so YAML strict parsers don't interpret mid-line colons as nested mappings.
- Set `metadata.internal: true` on skills meant for maintainers only — that hides them from public skill-installer menus.

### Required workflow pattern (recommended for non-trivial skills)

For skills with multiple reference files, add an explicit "Required workflow" section near the top of `SKILL.md` so the agent must:

1. **Open the relevant reference files** before responding — provide a task → reference table.
2. **Cite sources** in every claim using `[source: references/<file>.md]` format.
3. **Flag unverified claims** with `FROM_MEMORY (unverified):` prefix when the agent answers without consulting a reference.

This output contract makes non-compliance visible in the agent's response and is the strongest mitigation against agents answering from training data instead of from the skill. See `skills/refactoring-ui/SKILL.md` and `skills/vscode-extension-dev/SKILL.md` for concrete examples.

## Design principles for skills

- **Concrete file paths, commands, and API names.** Reference real files (`package.json`, `tsconfig.json`, `.vscodeignore`), real CLI invocations (`vsce publish`, `npx yo code`), and real API symbols (`vscode.window.createTreeView`, `context.secrets`). Avoid pseudo-code that the agent will need to invent details for.
- **Tool / SDK neutral within scope.** Skills target a domain broadly (UI design, VS Code extensions, text humanization) — avoid hard-coding one third-party library or vendor inside triggers and examples unless the skill is explicitly about that library.
- **Verify before claiming success.** A green build / passing test / rendered output is the proof, not the agent's assertion.
- **Define explicit hand-back conditions.** State when the agent should stop and ask the human (e.g. *"after 2-3 failed bundle attempts"*, *"when the user needs to make a subjective tone call"*).
- **No backwards-compat noise.** Move version history out of `SKILL.md` into `references/version-history.md` or `CHANGELOG.md` so the entry point stays focused on current behavior.

## CLI code conventions

### ESM modules

All `lib/` files are ESM. No CommonJS. Imports use `import { foo } from './bar.js'` with the `.js` extension explicit.

### Spinners + child processes

When wrapping a shell command with `ora`, **always use the async form** of `execFile`:

```js
import { promisify } from 'node:util';
import { execFile } from 'node:child_process';
const run = promisify(execFile);
await run('npm', ['update', '-g', '@maccesar/aiskills']);
```

Never `execFileSync` — it blocks the Node.js event loop, freezing the spinner animation. This is the same lesson TiTools learned in its v2.4.2 hotfix; since both repos share the same `lib/` infrastructure, the rule applies identically here.

### Claude Code hook format

If a hook is added in the future, in `settings.json` it must use the nested form:

```json
{
  "hooks": [
    { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh" }
  ]
}
```

NOT the flat `{ "command": "...", "timeout": 30000 }` form. The flat form triggers a settings validation error on session start.

### Files worth knowing

- `lib/config.js:SKILLS` — hardcoded list of which skills to install. Update when adding/removing a skill.
- `lib/config.js:LEGACY_SKILLS` — skills to actively remove during `update`/`uninstall`. Use when deprecating a skill so existing users get a clean migration.
- `lib/config.js:COMMANDS` — slash commands copied to `~/.claude/commands/` on install (Claude Code only). Update when adding/removing a slash command.
- `lib/config.js:LEGACY_COMMANDS` — commands to actively remove during `update`/`uninstall`.

## Tests

Tests live under `test/` using Node's built-in test runner (`node:test`):

```bash
npm test                        # all suites
node --test test/list.test.js   # single file
```

Add tests whenever a new command or skill-scripted behavior ships. Skills with executable scripts should have tests covering: frontmatter validity, CLI help output, argument validation, shell syntax of any bash scripts.

## Release checklist (mandatory)

Every release that ships code or skill changes must bump **BOTH** version files and keep them in sync. Anthropic's marketplace caches plugins by `version` in `plugin.json`; if code changes without the bump, marketplace users keep stale code.

1. Code + tests green (`npm test`).
2. Update `CHANGELOG.md` with the new version entry.
3. Bump `package.json` → `"version"`.
4. Bump `.claude-plugin/plugin.json` → `"version"` to the **same number**.
5. Single commit including both bumps.
6. Tag `vX.Y.Z` pointing at that commit.
7. Push `main` + push the tag.
8. `npm publish --access public`.

The bundled `release` slash command automates steps 2–7 end-to-end (semver bump inference, CHANGELOG update, commit, tag, GitHub release). Use it when releasing from a Claude Code session.

### Precedent (do not repeat)

This exact mismatch happened in the sibling repo TiTools: v2.6.0 shipped with `plugin.json` frozen at `3.0.0` (a stale value from a prior feature branch). npm published 2.6.0 but the marketplace announced 3.0.0. Had to sync manually and amend the release. **Always sync before the release commit** — applies here identically.

### npm 2FA and publishing

With 2FA enabled, each `npm publish` invocation needs a fresh OTP — even if a prior publish in the same session succeeded. Pass it via `--otp=XXXXXX` or respond to the prompt.

## Common operations

### Add a new skill

1. Pick a kebab-case `<skill-name>`.
2. Create `skills/<skill-name>/SKILL.md` with frontmatter ≤ 1024 chars.
3. Add the skill to `lib/config.js:SKILLS`.
4. Add a row in the README skills table.
5. If the skill has scripts, add tests under `test/`.
6. Bump version per the Release checklist.

### Deprecate a skill

1. Move the skill name from `SKILLS` to `LEGACY_SKILLS` in `lib/config.js`. This makes `aiskills update` remove it from existing user installs.
2. Delete the `skills/<name>/` folder.
3. Bump version + CHANGELOG entry explaining the deprecation.

### Edit a skill's frontmatter

1. Keep total chars ≤ 1024.
2. If the `description` semantics change meaningfully, update the README row.
3. Don't add fields the spec doesn't define (`name`, `description`, optional `metadata.*`, `argument-hint`, `allowed-tools` for Claude Code skills).

### Don't

- ❌ Skip the `plugin.json` version bump when shipping code changes. Marketplace users will get stale cache.
- ❌ Use `execFileSync` inside an `ora` wrapper. Freezes the spinner.
- ❌ Use the flat hook format in `settings.json`. Validation fails.
- ❌ Add a feature to aiskills without considering whether the equivalent belongs in TiTools.
- ❌ Commit without explicit user authorization. See `CLAUDE.md` § "Git Safety Protocol" in the user's global instructions.

## Resources

- Skill spec (cross-agent): <https://agentskills.io/specification>
- Claude Code skills: <https://docs.claude.com/en/docs/claude-code/skills>
- Codex CLI: <https://github.com/openai/codex>
- Gemini CLI: <https://github.com/google-gemini/gemini-cli>
- GitHub Copilot CLI: <https://docs.github.com/en/copilot/github-copilot-in-the-cli>
- Sibling repo (`@maccesar/titools`): <https://github.com/macCesar/titools>
