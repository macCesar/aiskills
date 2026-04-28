# AI Skills Maintainer Guide

How to release updates and manage the plugin marketplace.

---

## Distribution Channels

| Channel | Users | Update mechanism |
|---|---|---|
| **Plugin marketplace** | Claude Code users | Auto-update at startup (if enabled) |
| **CLI (`aiskills`)** | Claude Code, Gemini CLI, Codex CLI | `aiskills update` or auto-update hook |

Both channels serve the same `skills/` directory.

---

## Releasing an Update

1. Make changes to skills/references
2. Bump `version` in `.claude-plugin/plugin.json` (plugin channel)
3. Bump `version` in `package.json` (CLI channel)
4. Update CHANGELOG.md
5. Push to `main`
6. Run `npm publish` (for CLI users)

**Plugin users** get the update automatically at next Claude Code startup.
**CLI users** get the update via `aiskills update` or the auto-update hook.

---

## Key Rule: Always Bump Versions

Claude Code caches plugins by version. **If you push changes without bumping `version` in `plugin.json`, users will NOT see your changes.**

---

## Adding a New Skill

1. Create `skills/new-skill/SKILL.md` with YAML frontmatter
2. Add reference files in `skills/new-skill/references/`
3. Update README.md
4. Bump both versions
5. Push and publish

---

## Testing Locally

```bash
/plugin marketplace add --local /path/to/aiskills
/plugin install aiskills@local-marketplace-name
```

---

## Checklist Before Every Release

- [ ] Skills tested with real prompts
- [ ] `plugin.json` version bumped
- [ ] `package.json` version bumped (if CLI changes)
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if new skills)

---

## Setting Up the Marketplace Channel

The marketplace channel requires two files in `.claude-plugin/` at the repo root:

**`.claude-plugin/marketplace.json`** — catalog listing available plugins:

```json
{
  "name": "your-marketplace-id",
  "owner": { "name": "Your Name" },
  "metadata": { "description": "What this marketplace provides" },
  "plugins": [
    {
      "name": "your-plugin-name",
      "source": { "source": "github", "repo": "yourUser/yourRepo" },
      "description": "What this plugin does"
    }
  ]
}
```

**`.claude-plugin/plugin.json`** — plugin metadata:

```json
{
  "name": "your-plugin-name",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": { "name": "Your Name" },
  "homepage": "https://github.com/yourUser/yourRepo",
  "license": "MIT"
}
```

### Naming

`marketplace.json` `"name"` = marketplace ID. `plugin.json` `"name"` = plugin name. Users install with `/plugin install plugin-name@marketplace-id`.

### Discovery

Claude Code walks the plugin directory and discovers skills from any `SKILL.md` inside `skills/` subdirectories. No need to list them in `plugin.json`.

### Verification

```bash
/plugin marketplace add yourUser/yourRepo
/plugin install your-plugin-name@your-marketplace-id
/skills    # Should list your skills
```

For the full guide with hooks, commands, and reference repos, see the [TiTools MAINTAINER-GUIDE](https://github.com/macCesar/titools/blob/main/docs/MAINTAINER-GUIDE.md).
