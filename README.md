# aiskills - AI Skills CLI

<div align="center">

![npm](https://img.shields.io/npm/dm/aiskills)
![npm](https://img.shields.io/npm/v/aiskills)
![NPM](https://img.shields.io/npm/l/aiskills)

</div>

`aiskills` is a CLI for installing curated skills for AI coding assistants. It installs the skill files and links them to Claude Code, Gemini CLI, or Codex CLI.

Each skill is a small knowledge package: a `SKILL.md` file with YAML frontmatter plus a set of reference files. When a prompt matches the skill, the assistant reads those files and answers from the source material.

---

## Quick setup

```bash
# 1) Install the CLI
npm install -g aiskills

# 2) Install skills globally
aiskills install

# 3) Start your AI coding assistant
claude   # or gemini, or codex

# 4) Ask a question that matches a skill
```

Installed files:
- All skills to `~/.agents/skills/`
- Platform symlinks in `~/.claude/skills/`, `~/.gemini/skills/`, or `~/.codex/skills/`

Why install with npm?
- Cross-platform (macOS, Linux, Windows)
- No sudo required
- Simple updates with `aiskills update`

---

## Compatible platforms

| Platform                                                  | Status    | Installation Path   |
| --------------------------------------------------------- | --------- | ------------------- |
| [Claude Code](https://claude.ai/claude-code)              | Supported | `~/.claude/skills/` |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Supported | `~/.gemini/skills/` |
| [Codex CLI](https://developers.openai.com/codex/cli/)     | Supported | `~/.codex/skills/`  |

All three platforms use the same Agent Skills format: a `SKILL.md` file with YAML frontmatter that tells the assistant when to use the skill and what to do.

---

## Available skills

| Skill                | Domain       | Source                               | Reference Files |
| -------------------- | ------------ | ------------------------------------ | --------------- |
| refactoring-ui       | Design       | "Refactoring UI" by Wathan & Schoger | 8 files         |
| humaniza             | Writing (es) | Curated Spanish/es-MX style rules    | 6 files         |
| vscode-extension-dev | VS Code      | VS Code Extension API docs           | 4 files         |
| stitch-showcase      | Design Tools | Google Stitch export workflow        | 14 files        |

Use `aiskills list` to see available skills from the command line. Pull requests are welcome.

---

## How skills work

Skills activate based on what you ask. You can write prompts normally:

```
"How do I create better visual hierarchy in this UI?"
"What's the best way to build a color palette from scratch?"
"This interface feels too dense. How do I fix the spacing?"
```

The assistant reads the skill's `SKILL.md`, checks whether the request fits, and then loads the reference files for that skill. That keeps the answer tied to the source material.

You do not need to name a skill explicitly, though you still can if you want to force a specific one.

---

## Skill details

### refactoring-ui

A design skill based only on *Refactoring UI* by Adam Wathan and Steve Schoger.

When it activates:
- Asking how to improve a UI's appearance
- Building or refining a color system
- Choosing typography scales and line lengths
- Designing layout and spacing systems
- Creating depth with shadows
- Handling images in interfaces
- Adding finishing touches (empty states, borders, icons, backgrounds)
- Design reviews and critiques

Example prompts:
```
"How do I make this dashboard feel less cluttered?"
"What's the right way to build a 9-shade color palette in HSL?"
"My text hierarchy looks flat, how do I fix it without changing font sizes?"
"What's the rule for line-height on large headlines?"
"How do I handle text over a photo background?"
"My empty state looks like a broken page. How should I design it?"
```

Reference files:
| File                    | Topics                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| 01-design-process.md    | Feature-first workflow, low-fidelity, personality, pre-defined systems |
| 02-visual-hierarchy.md  | Weight, color, size hierarchy; labels; icons; button tiers             |
| 03-layout-spacing.md    | White space, spacing scale, columns, law of proximity                  |
| 04-typography.md        | Type scale, line length, alignment, line-height, letter-spacing        |
| 05-color.md             | HSL, shade systems, WCAG contrast, color signals                       |
| 06-depth-shadows.md     | Light source, raised/inset elements, shadow elevation                  |
| 07-images.md            | Stock photos, text over images, icons at scale, favicons               |
| 08-finishing-touches.md | Icons, borders, backgrounds, empty states, leveling up                 |

---

### humaniza

An editor for Spanish text (es-MX). It removes common AI writing patterns and rewrites the text so it sounds natural without changing the meaning.

When it activates:
- User asks to "humanize" a text in Spanish
- User says the text "sounds like AI" or wants it removed
- User wants something to "sound more natural" or "more human"
- Editing emails, documentation, marketing, support, or technical texts in Spanish

Example prompts:
```
"Humaniza este email de bienvenida"
"Este texto suena muy robótico, cámbialo"
"Hazlo sonar más natural, en español de México"
"Quítale el tono de IA a esta documentación"
"Reescríbelo en tono de soporte al cliente"
```

Available modes:
| Mode          | Description                          |
| ------------- | ------------------------------------ |
| Marketing     | Persuasive, direct, no filler        |
| Technical     | Precise, no decoration               |
| Support       | Empathetic, clear, action-oriented   |
| Emails        | Natural tone, appropriate to context |
| Documentation | Clear, scannable, no redundancy      |
| Posts / Essay | Personal voice, varied rhythm        |

Reference files:
| File              | Topics                                                          |
| ----------------- | --------------------------------------------------------------- |
| ai-patterns-es.md | AI writing tics in Spanish: inflated phrases, filler, templates |
| lexicon-es-mx.md  | Preferred es-MX vocabulary vs. Spain Spanish                    |
| modes-es-mx.md    | Rules per mode (marketing, technical, support, etc.)            |
| voice-es-mx.md    | How to add human voice: rhythm, concreteness, variety           |
| checklist.md      | Final QA before delivering the text                             |
| examples.md       | Before/after examples by text type                              |

Scope:
- Preserves meaning, data, and general structure
- Respects the original register (tú/usted) unless asked to change
- Keeps technical terms, brands, code, and proper names intact
- Prefers es-MX: avoids Spain-specific words like "vosotros", "ordenador", "móvil"
- Returns only the final text, no explanation (unless requested)

---

### vscode-extension-dev

A guide for building VS Code extensions from scaffolding to publishing. Based on the official VS Code Extension API docs.

When it activates:
- Creating or scaffolding a new VS Code extension
- Working with VS Code APIs (TreeView, Webview, QuickPick, StatusBar)
- Configuring package.json contributes, activationEvents, or keybindings
- Debugging extension activation, disposables, or memory leaks
- Bundling with esbuild or webpack
- Publishing to the VS Code Marketplace or Open VSX
- Setting up Webview CSP, nonce, or postMessage communication
- Using SecretStorage for credential management
- Writing extension tests with @vscode/test-electron

Example prompts:
```
"Create a VS Code extension with a tree view in the sidebar"
"How do I set up CSP and nonce for a Webview panel?"
"What's the right way to handle disposables in activate()?"
"How do I publish my extension to the Marketplace?"
"Set up esbuild bundling for my VS Code extension"
"How do I use SecretStorage to save API tokens?"
```

Reference files:
| File                   | Topics                                                               |
| ---------------------- | -------------------------------------------------------------------- |
| package-json-schema.md | contributes, activationEvents, engines, scripts, devDependencies     |
| api-patterns.md        | TreeView, Webview, QuickPick, StatusBar, SecretStorage, withProgress |
| architecture.md        | Project structure, layered architecture, testing strategy            |
| publishing.md          | vsce, .vscodeignore, CI/CD, Open VSX, versioning                     |

---

### stitch-showcase

A workflow skill for processing Google Stitch design exports. It handles the full lifecycle: from raw zips to a navigable showcase, component standardization, and a visual component catalog.

When it activates:
- User has Stitch export zips and wants to browse them as a gallery
- User asks to "organize", "build the showcase", or "process" Stitch designs
- User has a folder of `code.html` + `screen.png` pairs from Stitch
- User wants to standardize shared components or extract a component catalog

#### What you can ask it to do

**Build a showcase** — the core feature (instant, ~3 seconds):
```
"Organize my Stitch designs in ~/Downloads/snap-exports"
"Build the showcase from these Stitch zips"
"I have the Stitch zips in /Users/me/designs, generate the index"
"Process this design folder into a showcase"
```
Runs the Python build script directly — no pre-flight questions, no AI pre-processing. Generates a static site with a searchable thumbnail grid, section filter tabs, grid/list toggle, and a per-screen viewer with prev/next navigation, keyboard shortcuts, and fullscreen mode. Supports mobile (phone frame) and web (browser chrome) layouts.

**Enrich titles and descriptions** — optional, on-demand:
```
"Optimize the showcase titles and descriptions"
"Enrich the showcase descriptions"
"Improve the hero section text"
"Fix the mangled screen names in the showcase"
```
After the initial build, you can ask the AI to improve DESIGN.md: de-mangle Stitch slugs into proper titles, write meaningful descriptions from extracted screen text, update the hero section, and verify colors/fonts. Then rebuilds with enriched data.

**Add new screens to an existing showcase:**
```
"Add these new zips to the project"
"I exported 5 more screens from Stitch, add them"
"The client requested a new screen, include it in the showcase"
```
The skill detects which screens are new, adds them to DESIGN.md, and rebuilds the showcase.

**Standardize shared components** — fix Stitch's inconsistencies:
```
"Standardize the navbars across all screens"
"Make all footers the same"
"The bottom tab bar is different in each screen, fix it"
"Use the navbar from the home screen everywhere"
"Unify the navigation across all screens"
```
Google Stitch generates slight variations of navbars, footers, and tabbars across screens in the same session. This feature detects all shared components, shows you the variants with their differences, and lets you choose which version to apply everywhere. You can pick the best one, or mix pieces from different variants.

**Generate a component catalog** — extract reusable UI pieces:
```
"Extract all the components from the designs"
"Make a component catalog"
"Show me all the buttons and cards in the project"
"Generate a visual component library from the designs"
"Extract the atomic components (buttons, inputs, badges)"
"Extract composite components (cards, CTAs, price tables)"
```
Scans all screen HTMLs and extracts:
- **Atomic components**: buttons (with variant detection: primary/secondary/danger), headings, form inputs, badges/pills, standalone links, icons (Material Symbols + SVGs)
- **Composite components**: cards, price tables, CTAs, testimonials, hero sections
- **Design tokens**: colors (sorted by frequency), fonts, border-radius values

Generates a visual catalog page (`components-catalog.html`) with tabs per component type, inline previews, CSS properties, copyable code snippets, dark/light toggle, and search. Also outputs `component_catalog.json` for programmatic use.

#### Output structure

```
showcase/                      ← single output dir with view mode toggle
├── index.html                 ← searchable grid with section tabs + mobile/web view toggle
├── viewer.html                ← per-screen viewer with prev/next + fullscreen + view toggle
├── components-catalog.html    ← visual component catalog (when requested)
├── shared_components.json     ← component standardization data (when requested)
├── component_catalog.json     ← machine-readable catalog (when requested)
├── DESIGN.md
└── assets/
    ├── splash_screen.html
    ├── splash_screen.png
    └── ...
```

---

Anti-patterns `refactoring-ui` guards against:
- Designing shell/nav/layout before the actual feature
- Using font size as the only hierarchy tool
- Using grey text on colored backgrounds by lowering opacity
- Using `em` units for type scales
- Using color as the only way to communicate status
- Using preprocessor `lighten()`/`darken()` to generate color shades

---

## CLI reference

### aiskills list

Lists all available skills with their descriptions.

```bash
aiskills list
```

---

### aiskills install

Installs skills and creates symlinks for supported platforms.

```bash
aiskills install [options]
```

Options:
| Option          | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `-l, --local`   | Install skills locally in the current project (`./.agents/skills/`) |
| `-a, --all`     | Install to all detected platforms without prompting                 |
| `--path <path>` | Install to a custom path (skips symlink setup)                      |

What it does:
- Copies all skills to `~/.agents/skills/` (or a local directory if you use `--local`)
- Detects installed AI platforms such as Claude Code, Gemini CLI, and Codex CLI
- Prompts you to choose which platforms to link
- Creates symlinks from each platform's skills directory to the central install
- Removes legacy artifacts from older versions

### aiskills auto-update

Checks for updates and applies them silently. Designed to run from the Claude Code SessionStart hook, but can also be used manually.

```bash
aiskills auto-update            # Show progress
aiskills auto-update --silent   # No output (for hooks)
```

Options:
| Option        | Description                          |
| ------------- | ------------------------------------ |
| `-s, --silent` | Suppress all output except errors   |

What it does:
1. Checks a local cache (`~/.aiskills/last-check.json`) — if already checked today, exits immediately
2. Queries npm for the latest version
3. If a new version is available, runs `npm update -g aiskills`
4. Syncs skills and refreshes platform symlinks
5. Writes the cache so it won't check again for 24 hours

The hook is installed automatically by `aiskills install` when Claude Code is selected. It runs `aiskills auto-update --silent` at the start of every Claude Code session.

---

### aiskills status

Shows a quick overview of your installation.

```bash
aiskills status
```

Displays: version, skills count, hook status, last update check, and platform symlink status.

---

### aiskills doctor

Diagnoses installation health.

```bash
aiskills doctor
```

Checks: skill directories exist, symlinks are valid (not broken), hook is configured, cache is readable. Reports issues with fix suggestions.

---

### aiskills update

Checks npm for a newer `aiskills` CLI version, then syncs skills from the package you already have installed.

```bash
aiskills update [options]
```

Options:
| Option        | Description                                |
| ------------- | ------------------------------------------ |
| `-l, --local` | Update local skills in the current project |

What it does:
1. Checks npm for the latest CLI version
2. If a newer version exists, shows the update command: `npm update -g aiskills`
3. Exits without changing skills until the CLI is updated
4. If the CLI is current, syncs skills from the installed package (no download needed)
5. Updates platform symlinks only for platforms that already have them

Note: `aiskills update` only syncs the skill files from your installed CLI. To get newer skills, first run `npm update -g aiskills`, then run `aiskills update` again.

### aiskills remove

Removes installed skills and platform symlinks.

```bash
aiskills remove [options]
```

Options:
| Option        | Description                                  |
| ------------- | -------------------------------------------- |
| `-l, --local` | Remove local skills from the current project |

What it does:
- Detects all installed components (skills and symlinks)
- Prompts you to select what to remove:
  - Skills from global (`~/.agents/skills/`) or project directory
  - Platform symlinks from global or project directory

### Verify installation

```bash
aiskills status    # Quick overview of everything
aiskills doctor    # Diagnose any issues
aiskills --version # CLI version only
```

---

## Local vs global installation

By default, skills install globally to `~/.agents/skills/`, and symlinks are created in `~/.claude/skills/` plus any other detected platform. That makes the same skills available across all your projects.

If you want to pin skills to one project, for example to commit them with a repo, use `--local`:

```bash
cd /path/to/your/project
aiskills install --local
```

This installs to `./.agents/skills/` inside your project. Local skills override global skills for that project.

---

## Troubleshooting

### Skill not activating?

If the assistant does not seem to use skill knowledge:
1. Mention the domain explicitly: "Use the refactoring-ui skill"
2. Be more specific about what you're working on
3. Reference the topic area: "I need help with color hierarchy"

### aiskills command not found?

```bash
# Verify installation
npm list -g aiskills

# Re-install
npm install -g aiskills
```

### Skill gives wrong or generic advice?

Each skill only covers what is in its source material. If the topic is missing from the reference files, the answer will stay generic. Check the reference file list to see what the skill actually covers.

---

## Uninstall

```bash
# Remove skills and symlinks
aiskills remove

# Remove the CLI
npm uninstall -g aiskills
```

---

## Contributing

Skills are plain Markdown files. To add a new one:
1. Create a folder under `skills/<skill-name>/`
2. Add a `SKILL.md` with YAML frontmatter
3. Put the reference files under `skills/<skill-name>/references/`

### Skill frontmatter format

```yaml
---
name: skill-name
description: >
  One paragraph describing what this skill does and when to use it.
when_to_use: >
  - Bullet list of trigger conditions
source: "Book title, documentation name, or other authoritative source"
anti_hallucination_note: >
  What the AI should NOT do (invent, supplement, guess).
---
```

### Guidelines
- Every skill must cite a specific source (book, official docs, specification)
- No invented numbers, rules, or advice not found in the source
- Keep `SKILL.md` under 500 lines
- Put detail in reference files, not in `SKILL.md`
- Test with real sessions before submitting

---

## Credits

Created by César Estrada ([@macCesar](https://github.com/macCesar)), who also made [TiTools](https://github.com/macCesar/titools) and [PurgeTSS](https://github.com/macCesar/purgeTSS).

## License

MIT License. Free to use, modify, and distribute.

---

## Resources

- [Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code)
- [Gemini CLI Skills](https://geminicli.com/docs/cli/skills/)
- [Codex CLI Skills](https://developers.openai.com/codex/skills/)
- [Refactoring UI](https://refactoringui.com/)
