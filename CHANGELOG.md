# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.17.0] - 2026-08-02

### Added

- **Frontmatter size guard in `test/manifest.test.js`.** The agentskills.io spec caps a skill's YAML frontmatter at 1024 characters, past which an agent may fail to load the skill — and the symptom is the skill silently never triggering, not an error anyone would notice. `vscode-extension-dev` crossed it at 1059 while its description was being widened for better triggering, and was trimmed back to 899. `audit-codebase` sits at 1015, nine characters from the cap.

### Fixed

- **Two README reference-file tables listed files that don't exist.** `refactoring-ui`'s table carried the eight original filenames (`01-design-process.md`, `05-color.md`, …) against seven differently-named files on disk, and `vscode-extension-dev`'s listed a single `api-patterns.md` — a file that was split into seven per-API references — while omitting ten others, `lsp.md`, `notebooks.md`, `debugger.md` and `testing.md` among them. Both tables now match the directories.

### Changed

- **All six skills aligned with the current Anthropic skill-creator guidance.** No behavior changes to the CLI; this is entirely skill content.
  - **Descriptions rewritten for `humaniza`, `refactoring-ui`, `stitch-showcase` and `vscode-extension-dev`.** The frontmatter `description` is the only thing Claude reads when deciding whether to invoke a skill, and the guidance warns that skills are more often *under*-triggered than over-triggered. Each one now covers the phrasings people actually use — including the ones that never name the skill ("esto suena a ChatGPT", "why does this look off", editing `contributes` in a `package.json`) — and closes with what the skill is **not** for, which is what keeps the near-misses from firing. `audit-codebase` and `session-log` already followed this shape and are unchanged.
  - **Removed the `## When to use` sections** from `refactoring-ui` and `vscode-extension-dev`. They restated the description almost verbatim, and body text loads only *after* the invocation decision has been made — it cannot influence triggering, so it was paying context rent for nothing.
  - **Collapsed the duplicated references tables** in the same two skills into the Step 1 routing table, which is the one that does the work. The second copy was 8 and 15 lines respectively, and the two versions had already begun to disagree about what each file covered.
  - **`session-log/SKILL.md` is back under the 500-line budget** (524 → 496). The multi-repo detail — installing from inside each repo, the sibling header format, writing a sibling's status honestly — moved to `references/file-layout.md` under a new "Repos that come in pairs" section. It applies to a minority of projects and was loading in full on every invocation.
  - **Tables of contents** added to the three reference files over 300 lines (`session-log/references/file-layout.md`, `vscode-extension-dev/references/architecture.md` and `references/package-json-schema.md`), so a reader can jump to a section instead of loading the file to find out what's in it.
  - **`refactoring-ui`'s anti-pattern list now covers all seven references.** It cited only `01`–`03`, so polish, motion, dark mode and component patterns contributed reference files that nothing at the top level pointed at — the list read as complete while skipping four topics. Twenty entries added, each drawn from its reference and carrying the `[source:]` citation the skill requires of its own answers.
  - **`vscode-extension-dev`'s anti-pattern list went from 8 entries to 27**, and from 5 references cited to 13 of 14. Publishing, LSP, notebooks, debug adapters and testing each ship a reference file whose failure modes — a VSIX with the TypeScript sources still in it, `innerHTML` from untrusted cell output, a debug session that never sends `terminated` and leaves "Stop" hanging — appeared nowhere at the top level. The list is now grouped by area (manifest, lifecycle, security, publishing, language servers, notebooks and debug adapters, testing) because the domains are far enough apart that 27 flat bullets stop being scannable. `api-statusbar.md` is the one reference still uncited: it documents no failure mode, and inventing one is exactly what the skill's own contract forbids.
  - **Prohibitions now carry their reason.** The `❌`-prefixed "banned behaviors" lists and the shouted `CRITICAL` / `NEVER` / `ALWAYS` in `stitch-showcase` were rewritten to say *why* — that a hand-written `index.html` is erased by the next build, that a plausible-looking `vscode.*` call fails in the extension host where the stack trace helps least. The guidance treats all-caps absolutes as a yellow flag: a model that understands the reason handles the cases the list never anticipated.
- **`CLAUDE.md` § "Documentation-grounded skill template"** records the two omissions above, so the next advisory skill doesn't reintroduce them.

## [1.16.1] - 2026-08-02

### Fixed

- fix(symlink): uninstalling the marketplace plugin left Claude Code with **no skills at all**, and re-running `aiskills install` could not repair it. `isClaudePluginSkillInstalled` decided the plugin provided a skill by checking whether the directory existed in `~/.claude/plugins/cache/`, but Claude Code removes the plugin from `enabledPlugins` in `settings.json` and leaves that cache behind. The CLI read the leftover as proof of installation, skipped every symlink and reported `0/6 skills linked`. Detection now requires the plugin to be **enabled**, not merely cached.
- fix(installer): slash commands never asked whether the plugin already provided them, so `/release` was installed next to the plugin's own copy and appeared twice in the autocomplete. `installCommands` now applies the same rule the symlink step applies to skills, and removes a duplicate left from before the plugin was installed.
- fix(doctor): on a healthy marketplace install, `aiskills doctor` counted every absent mirror as a missing skill — `0/6 skills linked`, six issues, and "run `aiskills install` to fix", which correctly does nothing. Absent mirrors are the *right* state when the plugin serves them. Skills provided by the plugin are now reported as such instead of as failures.
- fix(cli): `✓ Claude Code detected` read as though Gemini and Codex had not been found. Only assistants that need aiskills-managed mirrors are ever listed there; the others read `~/.agents/skills/` directly and need no setup. The header now says so.

### Added

- **"Marketplace plugin" section in `aiskills doctor`**, distinguishing the three states the two channels can produce — enabled (mirrors intentionally absent), not installed (skills reach Claude Code through npm mirrors), and **uninstalled with a cache directory left behind**, which is the state that broke installs on 1.16.0 and now prints the command that clears it.
- **`lib/claude-plugin.js`** — internal module answering "does the installed plugin provide this?", for both skills and commands. It reads `enabledPlugins` from `settings.json` and `settings.local.json`, and fails toward `false`: a wrong `false` costs a duplicate entry, a wrong `true` costs the user every skill they have. No new public surface — no new command, flag or config.
- **16 tests** covering both failures, each run against a throwaway home directory. Verified by restoring each bug and confirming the corresponding tests go red — the stale-cache bug fails 2, the duplicate-command bug fails 1.

## [1.16.0] - 2026-08-01

### Added

- test(manifest): first test suite — `test/manifest.test.js`, 23 checks, no new dependencies. It guards the wiring between what the repo contains and what declares it: a skill directory missing from `lib/config.js:SKILLS` (which is exactly how `session-log` shipped in the repo while the CLI never installed it), an orphaned command file, frontmatter whose `name` disagrees with its directory, a `references/*.md` pointer that resolves to nothing, `SKILLS`/`LEGACY_SKILLS` overlap, bundled eval JSON that no longer parses, and `package.json` drifting from `plugin.json` — the TiTools failure where npm published 2.6.0 while the marketplace announced 3.0.0. Each assertion was verified against a deliberately broken repo state before being trusted: an orphan skill directory, an orphan command file and a desynced version each made the suite fail as intended.

- feat(session-log): new skill. Installs a fixed four-file convention under `docs/project/` — status (never loaded at startup), requirements, decisions and context — and writes a pointer into every context file the repo has, so the notes are findable from Claude Code, Codex or Gemini alike. Keeping volatile status out of the startup chain stops each progress update from invalidating the cached prefix behind it. Skill only, no slash command: commands are Claude Code-only, and a command duplicating the skill's logic is a second copy that drifts.
  - **Resuming is a first-class job, not a side effect of closing.** `SKILL.md` now dispatches on four situations (fresh install, upgrade from an earlier layout, arriving, leaving) instead of two, and the arriving path reads `status.md` and then checks it against git — commits landed since the file was written, whether the branch it names still exists, uncommitted work it never mentioned — before repeating any of it back. `references/verification.md` covers the direction of error in an old record: it rots toward understating what exists and overstating what's blocked.
  - **Safeguards.** These files get committed and often pushed to public repos, so credentials and client details get recorded by location, never verbatim. The notes are written in the language the project is already documented in. The import-chain check at the end of a session is now two greps instead of an instruction to look, with the failure mode spelled out: naming a file that doesn't exist makes `grep` exit non-zero and print nothing, which reads exactly like a clean result.
  - **Layout variants** in `references/file-layout.md` — a monorepo takes one `docs/project/` at the root with a heading per package (one repo, one branch, one deploy); `status.md` is conflict-prone with more than one writer, resolved by merging sections rather than splitting the file; `decisions.md` is append-only *and* imported, so past ~200 lines everything but the current year moves to a `decisions-archive.md` that is not imported; upgrading an earlier install is `git mv` plus a volatility split, not a rewrite.
  - **Evals rewritten and honestly labelled.** The three A/B rounds graded an earlier layout, so `evals.json` was rebuilt against the four-file convention — 9 prompts, including resuming against a stale file, a gitignored `docs/`, an upgrade, an offered credential and a monorepo — each carrying a `fixture_spec`, since the original fixture repos lived in a scratch workspace and are gone. Nothing in the new set has been run and the README says so; the unsupported "files created: 2 vs 4" row was removed from the repo README because no eval file backs it.

### Fixed

- fix(test): `npm test` ran zero tests and passed. The script was `node --test test/**/*.test.js`, and npm runs scripts through `sh`, where `**` collapses to a single `*` — so the pattern looked in `test/<subdir>/` and matched nothing, reporting `1..0` as success. Now `node --test test/*.test.js`, with test files kept flat.
- fix(marketplace): `marketplace.json` described four skills and omitted `audit-codebase`, which `plugin.json` already listed. Both descriptions now name every shipped skill.


## [1.15.0] - 2026-07-12

### Skill: audit-codebase

#### Added
- **New skill `audit-codebase`** — comprehensive software audit covering architecture, security, compatibility, performance, maintainability, and tests. Two-stage workflow: a read-only audit that delivers an evidence-based diagnosis, decision matrix, and phased correction plan, followed by an authorized implementation of the approved matrix. Core principles: evidence before patterns (Confirmed / Conditional risk / Unverified), proportional security (every restrictive recommendation must name affected use cases and the less-restrictive alternative evaluated), severity ≠ scope (every confirmed finding gets an explicit disposition), and minimal, complete, verifiable changes. Written in English for global reach; the audit report is produced in the user's language.
- **`references/comprehensive-audit.md`** — mandatory principles, 24-area technical scope, 5-phase working method, severity classification, and recommendation/communication rules.
- **`references/report-format.md`** — exact deliverable formats: executive summary, findings table, special sections, decision matrix, phased correction plan, and stage-2 implementation report.
- **`agents/openai.yaml`** — Codex interface metadata (display name, short description, default prompt).

## [1.14.0] - 2026-05-22

### CLI

#### Added
- **Interactive skill selection during `aiskills install`** — the install command now presents a checkbox prompt listing all skills with their descriptions so users can deselect the ones they don't want. Previously, every install was an all-or-nothing operation. `--all` and `--path` modes skip the prompt (CI/automation). Unselected skills are cleaned up from `~/.agents/skills/` and any platform symlinks. New utilities `readSkillDescription` and `shortenSkillDescription` in `lib/utils.js` drive the checkbox labels — they parse YAML frontmatter and compress descriptions to a one-line hint.
- **`removeUnselectedSkills` / `removeUnselectedSymlinks` in `lib/cleanup.js`** — when the user de-selects skills during a partial install, stale directories and symlinks are swept so on-disk state matches the selection.
- **Gemini redundant symlink detection and removal** — previous aiskills versions created symlinks at `~/.gemini/skills/`, but Gemini CLI auto-discovers skills from `~/.agents/skills/` per the agentskills.io standard. The duplicate symlinks caused "Skill conflict detected" warnings on Gemini startup. `cleanupLegacyArtifacts` now removes Gemini symlinks during `install`/`update`, and `con cleanup` / `aiskills install` also trigger the removal for existing installations.

#### Changed
- **Gemini CLI removed from platform auto-detection** — `getPlatforms()` in `lib/config.js` no longer includes a Gemini entry. Gemini discovers skills from `~/.agents/skills/` natively; aiskills no longer creates or updates platform symlinks for it. The column count in the install output decreased by one with no loss of functionality.
- **`aiskills install` output now shows install path prominently** — before the platform selection prompt, the command prints where skills are going (`~/.agents/skills/`) and which agents read from there, making the "did it actually work?" confirmation explicit.
- **`installSkills()` accepts a `skillsToInstall` subset** — `lib/installer.js` now supports installing a filtered skill list, used by the new interactive selector.

### Skill: humaniza

#### Added
- **8 new core rules** adapted from Stop Slop for Spanish prose: corta los abridores, rompe estructuras formulaicas, usa voz activa, sé concreto, pon al lector en la escena, varía el ritmo, confía en el lector, corta lo citable.
- **`references/structures-es.md`** — new reference covering 9 structural patterns to avoid in Spanish: contrastes binarios, listado negativo, fragmentación dramática, setups retóricos, agencia falsa, narrador desde la distancia, voz pasiva, inicios de oración a evitar, patrones de ritmo. Each category includes specific Spanish examples and replacements.
- **Quick Checks section** in `SKILL.md` — 12 pre-delivery checks mirroring Stop Slop's approach, adapted for Spanish: adverbs -mente, passive voice, false agency, wh- openers, throat-clearing, sentence length rhythm, paragraph endings, em dashes, vague declaratives, meta-commentary, false contrasts, LinkedIn-style quotables.

#### Changed
- **`references/ai-patterns-es.md`** — added 8 new patterns: abridores (throat-clearing), muletas de énfasis, agencia falsa, narrador desde la distancia, comentario meta, vagos declarativos, adverbiomanía, falsa intimidad.
- **`references/lexicon-es-mx.md`** — added 6 new sections: abridores, muletas de énfasis, adverbios -mente inflados, comentario meta, agencia falsa, vagos declarativos.
- **`references/checklist.md`** — expanded from 7 to 16 checks, covering all new Stop Slop-inspired patterns.
- **`references/examples.md`** — added 5 new before/after examples demonstrating abridor+falso contraste, énfasis vacío+fragmentación, agencia falsa, and abridor vago.

## [1.13.0] - 2026-05-16

### CLI

#### Changed
- **`aiskills install`/`update` no longer creates duplicate Claude symlinks when the marketplace plugin is installed** — users who installed the CLI before the `maccesar-aiskills` Claude marketplace plugin existed accumulated two copies of each skill: the symlink at `~/.claude/skills/<skill>` (created by the CLI) and the plugin payload at `~/.claude/plugins/cache/maccesar-aiskills/aiskills/<version>/skills/<skill>/`. Claude Code scans both locations and lists the skill twice in the slash-command autocomplete. `createSkillSymlinks` (`lib/symlink.js`) now detects the marketplace plugin via the new `isClaudePluginSkillInstalled(skill, baseDir)` helper and, when present, skips the Claude symlink for that skill **and removes any stale symlink left from previous CLI installs**. Gemini and the canonical `~/.agents/skills/` install path are untouched — Gemini still needs its symlink, and Codex still auto-discovers from `~/.agents/skills/`. The `results` object returned by `createSkillSymlinks` now also exposes a `skipped` array alongside the existing `linked` / `failed` arrays so callers can report the new behavior.
- **`lib/config.js`** — added `CLAUDE_PLUGIN_MARKETPLACE`, `CLAUDE_PLUGIN_NAME`, and `getClaudePluginSkillsPath(baseDir)` constants/helper so the marketplace location lives in one place. These are public exports for any future tooling that needs to reason about the plugin install.

#### Fixed
- **`.claude-plugin/plugin.json` version restored to sync with `package.json`** — `HEAD` had `plugin.json` frozen at `2.0.0` from a prior feature branch while `package.json` shipped at `1.12.0`. This is exactly the failure mode CLAUDE.md "Why both bumps matter" warns about (Claude Code caches plugins by `plugin.json` version). Both files now bump to `1.13.0` in lockstep.

### /release Command

#### Added
- **First-ever tag and first-ever GitHub release detection on public repos** — Step 1.8 surfaces a `first-tag` flag (`git tag --list | head -1` empty) and a `first-release` flag (`gh release list --limit 1` empty, requires `gh` available + GitHub remote). Each missing milestone appears as its own ⚠️ line in the Step 4 plan so the user can opt out in the same confirmation round-trip — no separate prompt. Private repos remain unaffected because tag and GitHub release are skipped there by default.

### Skill: refactoring-ui

#### Added
- **`references/05-motion.md`** — motion system (durations, easings), hover/press states, loading patterns, prefers-reduced-motion. Complementary, not from the book.
- **`references/06-dark-mode.md`** — dark mode color tokens, text contrast, shadow handling, images, theme toggle. Complementary, extrapolated from the book's HSL principles.
- **`references/07-component-patterns.md`** — modals (focus, layout), forms (labels, validation), tables (density, alignment). Complementary, extends RUI principles to specific components.

#### Changed
- **SKILL.md restructured around the documentation-grounded skill template** (now shared with `vscode-extension-dev`): Step 1 routing table per task, Step 2 output contract (every cited rule/ratio carries `[source: references/<file>.md]`), Step 3 `FROM_MEMORY (unverified):` fallback, banned behaviors block, anti-patterns block with source citations.

### Skill: vscode-extension-dev

#### Changed
- **`references/api-patterns.md` (625 lines) split into seven focused files** so each query loads only the reference it needs: `api-treeview.md`, `api-webview.md`, `api-quickpick.md`, `api-statusbar.md`, `api-secretstorage.md`, `api-progress.md`, `api-additional.md` (FileSystemWatcher, Diagnostics, OutputChannel, ContextKeys, TextDocumentContentProvider, disposable lifecycle).
- **SKILL.md restructured around the documentation-grounded skill template** (same contract as `refactoring-ui`): Step 1 routing table covering all 14 references, Step 2 citation contract, Step 3 FROM_MEMORY fallback, banned behaviors (deprecated APIs like `vscode.workspace.rootPath` are named explicitly).

#### Added
- **`references/lsp.md`** — Language Server Protocol, `vscode-languageclient`, language servers.
- **`references/debugger.md`** — Debug Adapter Protocol, `DebugAdapterDescriptorFactory`, `DebugConfigurationProvider`.
- **`references/testing.md`** — multi-suite `.vscode-test.mjs`, fixtures, mocking, CI, coverage.
- **`references/notebooks.md`** — notebook serializers, controllers, renderers.
- **`references/architecture.md`** gains two sections: "Extension Host Runtime" (single Node.js process shared by every extension, sync I/O hazards like `fs.readFileSync`, async alternatives via `node:fs/promises` and `vscode.workspace.fs`) and "Workspace Folders" (`vscode.workspace.rootPath` is deprecated; use `workspaceFolders`, `getWorkspaceFolder(uri)`, and `onDidChangeWorkspaceFolders`; relative paths must resolve against a `WorkspaceFolder`, never against `process.cwd()`).

### Skill: humaniza

#### Added
- **`scripts/check_ai_patterns.py`** — deterministic scanner that reads `references/lexicon-es-mx.md` and reports each AI-tic hit with line, column, category, and suggestion (when one exists). Reads from a path argument or stdin.

#### Changed
- **SKILL.md workflow step 7** now requires running the scanner before the visual QA checklist. A new "Verificación con script" section documents the `<SKILL_DIR>` placeholder (so the instructions work for both plugin and standalone installs), what to do per hit (correct + rescan, or annotate as a legitimate quote/mark/example), and the fact that the scanner does not replace the visual checklist — it removes only the mechanical lexical-search phase.
- **`allowed-tools`** in the frontmatter now includes `Bash` so the AI can invoke the scanner from the conversation.

### Skill: stitch-showcase

#### Added
- **Three-tier title resolution: DESIGN.md override → `<title>` HTML → demangler** — `_enrich_screens` previously tried `design.get("title") or slug_to_title(slug)`, which skipped the rich data already in every Stitch export. There is now a middle step: `_read_html_title_tag(html_path)` reads the `<title>` element from each `code.html`, decodes entities, skips generics (`Untitled`, `index`, numeric-only…), and strips a leading `"Brand - "` / `" | "` / `": "` prefix so `"Lumiere Dining - Rústico & Artesanal"` becomes `"Rústico & Artesanal"`. Real-world impact on a 5-screen Stitch menu zip: 3 of 5 titles went from `"Men R Stico Artesanal"`-style garbage to `"Menú Dark Mode Premium"` / `"Elegante & Minimalista"` / `"Rústico & Artesanal"` without touching the demangler or invoking an LLM. The remaining slugs whose HTML has no `<title>` still fall to the demangler — those are the ones Mode 2 (Enrich) is now responsible for.
- **YAML frontmatter parser for Stitch's native DESIGN.md format** — Stitch exports a `DESIGN.md` whose first block is YAML (`name: Culinary Framework`, `colors:` mapping with `surface` / `primary` / etc., `typography:` with `fontFamily` per role). The previous parser ignored that entire block and fell back to inferring everything from the filename. New `_parse_yaml_frontmatter(text)` in `parse_design_md.py` extracts `name`, `colors` (as a flat hex dict), and the first `fontFamily` (as `font_family`). `parse()` now uses those as defaults for `project_name`, `colors`, `color_tokens` (via the new `_semantic_tokens_from_dict` helper that mirrors `_extract_color_tokens`'s `accent` / `surface` rules), and `font_family` whenever the corresponding Markdown body sections are absent. Concrete effect on the Stitch menu zip: `project_name` is now `"Culinary Framework"` (the value in the frontmatter) instead of the filename-derived `"Stitch Responsive Digital Menu Designs"`.
- **Mode 2 (Enrich) is now the LLM-driven recovery path for broken titles, not just descriptions** — `SKILL.md` Mode 2 spelled out the title resolution chain in Mode 1 (`Title|Description` override → `<title>` HTML → demangler) and made it explicit that when the demangler falls back to gibberish like `"Men Colorido Din Mico"` (because the slug has un-dictionaried accents AND the HTML has no `<title>` tag), the **correct** response is not to grow the demangler's dictionary indefinitely — it is to invoke Mode 2, read the HTML content + the project description, and write a `Title | Description` override in DESIGN.md so the next build picks it up. The demangler stays as the deterministic Mode 1 floor; the LLM stays out of Mode 1 by design but takes over in Mode 2.
- **Automatic `<html lang>` detection with explicit overrides** — `references/index.html` and `references/viewer.html` previously hard-coded a single `lang` value, which made Chrome's content-language detector misfire whenever the showcase content disagreed with the template's locale. The build now resolves `lang` through this priority chain: `"lang"` field in `showcase.json` → `## Lang` section in `DESIGN.md` → heuristic auto-detect over the DESIGN.md text (Spanish accented characters and stopword count) → `"en"` default. Both templates carry a `{{HTML_LANG}}` placeholder that `_generate_viewer` and `_generate_index` substitute. The resolved value is normalized to BCP-47 form (`pt-br` → `pt-BR`). See `references/13-language-detection.md`.
- **Deterministic slug de-mangling** — `scripts/slug_demangle.py` is a new sibling script with a 90-entry dictionary of common Spanish words that Stitch mangles when stripping accents from filenames (`configuraci_n` → `"Configuración"`, `membres_as` → `"Membresías"`, `men_m_s` → `"Menú Más"`, `esc_ner` → `"Escáner"`, …). `parse_design_md._slug_to_title` and `build_showcase._slug_to_title` both delegate to `demangle_to_title`, so every code path that derives a display title from a slug (section auto-grouping, viewer SCREENS JSON, card titles, `--init`-generated DESIGN.md skeletons) now produces the accented form without AI assistance or manual `Title | Description` overrides. The override format is still supported for slugs that fall outside the dictionary.
- **Post-build validation pass** — `_validate_showcase()` runs at the end of `build()` (after catalog generation) and checks three things: the `var SCREENS = […]` JSON embedded in `viewer.html` parses cleanly, each screen has both an `assets/<slug>.html` and `assets/<slug>.png` file, and every local `src=` reference inside the screen HTMLs (img, video, source — http/https/data: URLs are skipped) resolves on disk. Reports `✅ N/N screens válidos` on success or a capped list of warnings on failure. The build never aborts — this is a sanity check, not a gate.
- **Five new reference guides**: `references/12-video-embedding.md` (autoplay attributes, native `width`/`height`, AV1 → H.264 with ffmpeg, aspect-ratio mismatch), `references/13-language-detection.md` (resolution order + when to override), `references/14-troubleshooting-known-issues.md` (catalog stuck loading, Chrome translate banner, AV1 codec, plugin-vs-CLI duplicate install, brand-color background pitfall, accent stripping), `references/15-build-flags.md` (full build script reference — flags, output structure, source discovery, supported input layouts), `references/16-design-md-format.md` (DESIGN.md and showcase.json formats — project metadata, screen grouping, description sources priority).

#### Changed
- **`_slug_to_title` deduplicated** — the two near-identical copies in `parse_design_md.py` and `build_showcase.py` are gone. A single canonical `slug_to_title(slug)` now lives in `scripts/slug_demangle.py` alongside `demangle_to_title`; both former callers import it. Side effect: `parse_design_md` now also strips a leading numeric ordering prefix (`01_splash_screen` → `Splash Screen`), matching what `build_showcase` already did. If a user listed slugs like `01_pantalla` in DESIGN.md expecting the `01` to appear in the title, the title now drops the digits. Consistent across the pipeline either way. The plan's broader "extract ~150 duplicated lines to `lib_shared.py`" item was scoped down to what was actually duplicated — `_extract_buttons` / `_extract_inputs` exist in both `extract_text.py` and `extract_catalog.py` but have different signatures and serve different pipelines (text summary vs component catalog), so they were left alone.
- **`SKILL.md` — Mode 2 (Enrich) no longer instructs manual de-mangling** — the previous text walked the AI through reconstructing accented titles by hand and required the `Title | Description` override for every mangled slug. Both the prose and the worked example block are now replaced with a short note explaining that `slug_demangle.py` handles the common cases automatically and the override format is reserved for slugs the demangler can't infer. The new reference guides and `slug_demangle.py` are listed in the Scripts and Reference Guides tables, and `showcase.json` / DESIGN.md format docs now describe the `lang` field and `## Lang` section.
- **Templates now ship in Spanish UI chrome** — `references/index.html` and `references/viewer.html` shipped with mixed-language UI chrome (Spanish hero copy, English UI affordances). The hardcoded UI strings are now Spanish to match the rest of the templates: header `"5 screens"` → `"5 pantallas"`, hero counter `"Screens"` → `"Pantallas"`, search placeholder `"Search screens..."` → `"Buscar pantallas..."`, empty-state `"No screens match your search."` → `"Ninguna pantalla coincide con tu búsqueda."`, view-mode badge `'Mobile' | 'WEB'` → `'Móvil' | 'Web'`. In `scripts/build_showcase.py`: the project type label `{"mobile": "Mobile App", "web": "Web App"}` → `{"mobile": "App Móvil", "web": "App Web"}` and the typography hint `"Primary typeface"` → `"Tipografía principal"`. In `references/viewer.html`: the Back button label/aria + every `title` tooltip (Previous/Next screen, Toggle light/dark, Toggle mobile/web, Fullscreen) translated. The `<html lang>` attribute is no longer hard-coded — see the new "Automatic `<html lang>` detection with explicit overrides" entry above.
- **Showcase gallery is now responsive on real mobile viewports** — `references/index.html` previously forced `repeat(4, 1fr)` for the mobile-view grid regardless of screen width, so opening the showcase on a phone produced 4 cramped columns where titles wrapped one word per line. The grid is now mobile-first: 2 columns by default, 3 at `≥640px`, 4 at `≥768px`. List-mode thumbnails also scale down — `140px` wide on phones, `240px` from `640px` up — leaving room for titles and descriptions to breathe on small screens.
- **Index header collapses cleanly on phones** — the chips next to the project title (`view-badge`, `"N screens"`, and the "Catalog" label) used to claim `shrink-0` and pushed the project name into a single-letter ellipsis on narrow viewports. The badge and screen count now hide below `640px`, the Catalog link keeps only its icon (with `aria-label="Catalog"`), and the outer container drops to `gap-2 px-3` so the project name has room to render.
- **Viewer navbar fits in one row on phones** — `references/viewer.html` carried seven controls that overflowed the viewport on phones, clipping the fullscreen button off-screen. On `<640px`: the Back label, vertical separator, position counter (`N / M`) and fullscreen button are hidden; the screen title switches from `shrink-0` to `min-w-0 truncate` so it yields to the spacer instead of pushing siblings out. Prev/next/theme/view-mode stay visible. Padding tightens to `gap-2 px-3` on mobile and restores to `gap-3 px-5` from `sm:` up.
- **Simulator chrome auto-hides on real mobile viewports** — when the showcase is opened on a phone, the phone-frame border/radius/shadow around the mobile iframe (and the browser chrome bar around the web iframe) became visual noise: a simulated phone framed inside a real phone, eating ~60–80px of vertical space and recropping content already designed for the device. A `@media (max-width: 639px)` block in `references/viewer.html` now zeros out `#phone-wrap` border / border-radius / box-shadow, drops `#mobile-frame` padding-top, cancels the JS-applied `transform: scale(...)` on `#phone-container` (the iframe already fits natively at this width), and hides `#browser-chrome` plus its surrounding border for the web view. From `640px` up the simulator chrome returns untouched.
- **Viewer prev/next order now matches the index gallery** — `_generate_viewer` was passing `screens` straight to the SCREENS_JSON in alphabetical order (the order returned by `iterdir()` sorting), while `_generate_index` was already grouping by DESIGN.md sections. Result: clicking "Moderno Visual" — the first card in the gallery — opened the viewer at position `4 / 5`, and prev/next walked an unrelated alphabetical sequence. The viewer now reorders `screens` to follow the DESIGN.md section order (slugs appearing in sections come first in declared order; unlisted slugs are appended at the end), mirroring the same logic `_build_sections_html` already uses for the gallery.
- **Existing reference guides expanded**: `references/07-theme-system.md` adds a "Showcase Color Strategy" section with the rule "do NOT use brand colors as large showcase surfaces" plus the matching anti-pattern; `references/08-type-detection.md` adds a "Project-Level Detection (from DESIGN.md)" section that runs before per-screen detection; `references/10-component-standardization.md` documents the "Workflow (Mode 4: Standardize Components)" detect → present → choose → apply → rebuild loop.

#### Removed
- **Catalog link removed from the index header** — the `references/index.html` template no longer includes the "Catalog" chip that pointed to `catalog.html`. The viewer reported the catalog page hanging on "loading" for projects with dense / heterogeneous screen HTMLs, and rather than ship a broken affordance the link is gone. The component extraction pipeline (`extract_catalog.py`, `component_utils.py`, `catalog-template.html`, the structural/atomic/composite detection logic, and the `catalog.html` output file itself) is **untouched** — `build_showcase.py` still generates `catalog.html` alongside `index.html` and `viewer.html`. Anyone who needs the catalog can still open it directly at `<showcase>/catalog.html`; we'll restore the chip once the loading issue is diagnosed and fixed.

### Project

#### Added
- **`AGENTS.md`** — agent-agnostic guidance for any LLM-driven coding assistant (Claude Code, Gemini CLI, Codex CLI, Copilot CLI, …) working inside this repo. Describes the dual distribution (npm CLI + Claude Code plugin marketplace), the layout, the sibling `@maccesar/titools` project, and the release contract.
- **`CLAUDE.md`** — Claude Code-specific notes that travel with the repo via git: the release checklist requiring both `package.json` and `.claude-plugin/plugin.json` to be bumped in lockstep (with the precedent of TiTools shipping 2.6.0 while `plugin.json` was frozen at 3.0.0), hooks format in `settings.json` (nested, not flat), the `ora` + `execFile` async pattern, the documentation-grounded skill template contract shared by `refactoring-ui` and `vscode-extension-dev`, and parallel-project coordination notes for TiTools.

#### Changed
- **`.gitignore`** — ignore local maintainer-only directories (`.claude/`, `docs/`) so machine-specific Claude Code state and draft docs don't end up tracked.

#### Added
- **Three-tier title resolution: DESIGN.md override → `<title>` HTML → demangler** — `_enrich_screens` previously tried `design.get("title") or slug_to_title(slug)`, which skipped the rich data already in every Stitch export. There is now a middle step: `_read_html_title_tag(html_path)` reads the `<title>` element from each `code.html`, decodes entities, skips generics (`Untitled`, `index`, numeric-only…), and strips a leading `"Brand - "` / `" | "` / `": "` prefix so `"Lumiere Dining - Rústico & Artesanal"` becomes `"Rústico & Artesanal"`. Real-world impact on a 5-screen Stitch menu zip: 3 of 5 titles went from `"Men R Stico Artesanal"`-style garbage to `"Menú Dark Mode Premium"` / `"Elegante & Minimalista"` / `"Rústico & Artesanal"` without touching the demangler or invoking an LLM. The remaining slugs whose HTML has no `<title>` still fall to the demangler — those are the ones Mode 2 (Enrich) is now responsible for.
- **YAML frontmatter parser for Stitch's native DESIGN.md format** — Stitch exports a `DESIGN.md` whose first block is YAML (`name: Culinary Framework`, `colors:` mapping with `surface` / `primary` / etc., `typography:` with `fontFamily` per role). The previous parser ignored that entire block and fell back to inferring everything from the filename. New `_parse_yaml_frontmatter(text)` in `parse_design_md.py` extracts `name`, `colors` (as a flat hex dict), and the first `fontFamily` (as `font_family`). `parse()` now uses those as defaults for `project_name`, `colors`, `color_tokens` (via the new `_semantic_tokens_from_dict` helper that mirrors `_extract_color_tokens`'s `accent` / `surface` rules), and `font_family` whenever the corresponding Markdown body sections are absent. Concrete effect on the Stitch menu zip: `project_name` is now `"Culinary Framework"` (the value in the frontmatter) instead of the filename-derived `"Stitch Responsive Digital Menu Designs"`.
- **Mode 2 (Enrich) is now the LLM-driven recovery path for broken titles, not just descriptions** — `SKILL.md` Mode 2 spelled out the title resolution chain in Mode 1 (`Title|Description` override → `<title>` HTML → demangler) and made it explicit that when the demangler falls back to gibberish like `"Men Colorido Din Mico"` (because the slug has un-dictionaried accents AND the HTML has no `<title>` tag), the **correct** response is not to grow the demangler's dictionary indefinitely — it is to invoke Mode 2, read the HTML content + the project description, and write a `Title | Description` override in DESIGN.md so the next build picks it up. The demangler stays as the deterministic Mode 1 floor; the LLM stays out of Mode 1 by design but takes over in Mode 2.
- **Automatic `<html lang>` detection with explicit overrides** — `references/index.html` and `references/viewer.html` previously hard-coded a single `lang` value, which made Chrome's content-language detector misfire whenever the showcase content disagreed with the template's locale. The build now resolves `lang` through this priority chain: `"lang"` field in `showcase.json` → `## Lang` section in `DESIGN.md` → heuristic auto-detect over the DESIGN.md text (Spanish accented characters and stopword count) → `"en"` default. Both templates carry a `{{HTML_LANG}}` placeholder that `_generate_viewer` and `_generate_index` substitute. The resolved value is normalized to BCP-47 form (`pt-br` → `pt-BR`). See `references/13-language-detection.md`.
- **Deterministic slug de-mangling** — `scripts/slug_demangle.py` is a new sibling script with a 90-entry dictionary of common Spanish words that Stitch mangles when stripping accents from filenames (`configuraci_n` → `"Configuración"`, `membres_as` → `"Membresías"`, `men_m_s` → `"Menú Más"`, `esc_ner` → `"Escáner"`, …). `parse_design_md._slug_to_title` and `build_showcase._slug_to_title` both delegate to `demangle_to_title`, so every code path that derives a display title from a slug (section auto-grouping, viewer SCREENS JSON, card titles, `--init`-generated DESIGN.md skeletons) now produces the accented form without AI assistance or manual `Title | Description` overrides. The override format is still supported for slugs that fall outside the dictionary.
- **Post-build validation pass** — `_validate_showcase()` runs at the end of `build()` (after catalog generation) and checks three things: the `var SCREENS = […]` JSON embedded in `viewer.html` parses cleanly, each screen has both an `assets/<slug>.html` and `assets/<slug>.png` file, and every local `src=` reference inside the screen HTMLs (img, video, source — http/https/data: URLs are skipped) resolves on disk. Reports `✅ N/N screens válidos` on success or a capped list of warnings on failure. The build never aborts — this is a sanity check, not a gate.
- **Three new reference guides**: `references/12-video-embedding.md` (autoplay attributes, native `width`/`height`, AV1 → H.264 with ffmpeg, aspect-ratio mismatch), `references/13-language-detection.md` (resolution order + when to override), `references/14-troubleshooting-known-issues.md` (catalog stuck loading, Chrome translate banner, AV1 codec, plugin-vs-CLI duplicate install, brand-color background pitfall, accent stripping).

#### Changed
- **`_slug_to_title` deduplicated** — the two near-identical copies in `parse_design_md.py` and `build_showcase.py` are gone. A single canonical `slug_to_title(slug)` now lives in `scripts/slug_demangle.py` alongside `demangle_to_title`; both former callers import it. Side effect: `parse_design_md` now also strips a leading numeric ordering prefix (`01_splash_screen` → `Splash Screen`), matching what `build_showcase` already did. If a user listed slugs like `01_pantalla` in DESIGN.md expecting the `01` to appear in the title, the title now drops the digits. Consistent across the pipeline either way. The plan's broader "extract ~150 duplicated lines to `lib_shared.py`" item was scoped down to what was actually duplicated — `_extract_buttons` / `_extract_inputs` exist in both `extract_text.py` and `extract_catalog.py` but have different signatures and serve different pipelines (text summary vs component catalog), so they were left alone.
- **`SKILL.md` — Mode 2 (Enrich) no longer instructs manual de-mangling** — the previous text walked the AI through reconstructing accented titles by hand and required the `Title | Description` override for every mangled slug. Both the prose and the worked example block are now replaced with a short note explaining that `slug_demangle.py` handles the common cases automatically and the override format is reserved for slugs the demangler can't infer. The new reference guides and `slug_demangle.py` are listed in the Scripts and Reference Guides tables, and `showcase.json` / DESIGN.md format docs now describe the `lang` field and `## Lang` section.
- **Templates now ship in Spanish UI chrome** — `references/index.html` and `references/viewer.html` shipped with mixed-language UI chrome (Spanish hero copy, English UI affordances). The hardcoded UI strings are now Spanish to match the rest of the templates: header `"5 screens"` → `"5 pantallas"`, hero counter `"Screens"` → `"Pantallas"`, search placeholder `"Search screens..."` → `"Buscar pantallas..."`, empty-state `"No screens match your search."` → `"Ninguna pantalla coincide con tu búsqueda."`, view-mode badge `'Mobile' | 'WEB'` → `'Móvil' | 'Web'`. In `scripts/build_showcase.py`: the project type label `{"mobile": "Mobile App", "web": "Web App"}` → `{"mobile": "App Móvil", "web": "App Web"}` and the typography hint `"Primary typeface"` → `"Tipografía principal"`. In `references/viewer.html`: the Back button label/aria + every `title` tooltip (Previous/Next screen, Toggle light/dark, Toggle mobile/web, Fullscreen) translated. The `<html lang>` attribute is no longer hard-coded — see the new "Automatic `<html lang>` detection with explicit overrides" entry above.

#### Removed
- **Catalog link removed from the index header** — the `references/index.html` template no longer includes the "Catalog" chip that pointed to `catalog.html`. The viewer reported the catalog page hanging on "loading" for projects with dense / heterogeneous screen HTMLs, and rather than ship a broken affordance the link is gone. The component extraction pipeline (`extract_catalog.py`, `component_utils.py`, `catalog-template.html`, the structural/atomic/composite detection logic, and the `catalog.html` output file itself) is **untouched** — `build_showcase.py` still generates `catalog.html` alongside `index.html` and `viewer.html`. Anyone who needs the catalog can still open it directly at `<showcase>/catalog.html`; we'll restore the chip once the loading issue is diagnosed and fixed.

#### Changed
- **Showcase gallery is now responsive on real mobile viewports** — `references/index.html` previously forced `repeat(4, 1fr)` for the mobile-view grid regardless of screen width, so opening the showcase on a phone produced 4 cramped columns where titles wrapped one word per line. The grid is now mobile-first: 2 columns by default, 3 at `≥640px`, 4 at `≥768px`. List-mode thumbnails also scale down — `140px` wide on phones, `240px` from `640px` up — leaving room for titles and descriptions to breathe on small screens.
- **Index header collapses cleanly on phones** — the chips next to the project title (`view-badge`, `"N screens"`, and the "Catalog" label) used to claim `shrink-0` and pushed the project name into a single-letter ellipsis on narrow viewports. The badge and screen count now hide below `640px`, the Catalog link keeps only its icon (with `aria-label="Catalog"`), and the outer container drops to `gap-2 px-3` so the project name has room to render.
- **Viewer navbar fits in one row on phones** — `references/viewer.html` carried seven controls that overflowed the viewport on phones, clipping the fullscreen button off-screen. On `<640px`: the Back label, vertical separator, position counter (`N / M`) and fullscreen button are hidden; the screen title switches from `shrink-0` to `min-w-0 truncate` so it yields to the spacer instead of pushing siblings out. Prev/next/theme/view-mode stay visible. Padding tightens to `gap-2 px-3` on mobile and restores to `gap-3 px-5` from `sm:` up.
- **Simulator chrome auto-hides on real mobile viewports** — when the showcase is opened on a phone, the phone-frame border/radius/shadow around the mobile iframe (and the browser chrome bar around the web iframe) became visual noise: a simulated phone framed inside a real phone, eating ~60–80px of vertical space and recropping content already designed for the device. A `@media (max-width: 639px)` block in `references/viewer.html` now zeros out `#phone-wrap` border / border-radius / box-shadow, drops `#mobile-frame` padding-top, cancels the JS-applied `transform: scale(...)` on `#phone-container` (the iframe already fits natively at this width), and hides `#browser-chrome` plus its surrounding border for the web view. From `640px` up the simulator chrome returns untouched.
- **Viewer prev/next order now matches the index gallery** — `_generate_viewer` was passing `screens` straight to the SCREENS_JSON in alphabetical order (the order returned by `iterdir()` sorting), while `_generate_index` was already grouping by DESIGN.md sections. Result: clicking "Moderno Visual" — the first card in the gallery — opened the viewer at position `4 / 5`, and prev/next walked an unrelated alphabetical sequence. The viewer now reorders `screens` to follow the DESIGN.md section order (slugs appearing in sections come first in declared order; unlisted slugs are appended at the end), mirroring the same logic `_build_sections_html` already uses for the gallery.

## [1.12.0] - 2026-05-11

### Changed — Codex CLI no longer gets a redundant platform symlink

Codex CLI auto-discovers skills from the canonical `~/.agents/skills/` per the agentskills.io standard, so the symlinks aiskills was creating at `~/.codex/skills/<skill>` were redundant — Codex never actually read from there. Verified against the [official Codex CLI skills documentation](https://developers.openai.com/codex/skills/), which lists `$HOME/.agents/skills` (not `~/.codex/skills/`) as the user-scope location.

Codex remains fully supported by aiskills; users simply don't need a platform-specific symlink.

### Removed

- Codex entry in `getPlatforms()` (`lib/config.js`). The platform detector and install/sync flow no longer treat Codex as a symlink target.
- README references implying Codex needs `~/.codex/skills/` symlinks.

### Migration for existing users

`aiskills update` now removes any stale `~/.codex/skills/<skill>` symlinks that aiskills created in earlier versions (active and legacy skill names alike). The cleanup is scoped to aiskills-managed skill names, so symlinks placed there by other tools (for example `npx skills add`) are left alone.

No action is required from users — the next `aiskills update` cleans up automatically.

## [1.11.0] - 2026-05-01

### Stitch Showcase

#### Added
- **Auto-copy of shared asset folders** in `build_showcase.py` — after extracting screens, the script now detects `images/`, `fonts/`, `css/`, `js/` folders in the source dir or its parent (project root) and copies them to `showcase/assets/`. Eliminates the manual `cp images/ showcase/assets/images/` step needed every rebuild for projects whose HTMLs reference shared assets via relative paths (e.g., a logo at `images/logo.png`).

#### Changed
- **Scrollbar-hiding CSS moved from per-HTML injection to viewer level** — `extract_zips.py:_copy_html()` previously mutated each copied HTML by inserting `<style>*::-webkit-scrollbar{display:none}...</style>` before `</head>`. Now `_copy_html()` is a thin wrapper around `shutil.copy2()` and the CSS is injected dynamically into the iframe by `viewer.html` after `load`. Result: HTMLs in `showcase/assets/` are byte-identical to their source in `{source}/{slug}/code.html`, so the templates stay clean for downstream handoff (e.g., Laravel Blade conversion). Detect divergence between source and output via `md5`/`diff` if either is ever modified out of band.
- **View-mode toggle icon now reflects the current state** instead of the destination — previously the icon swapped to show "where clicking takes you" (Mobile mode → monitor icon, Web mode → phone icon), which conflicted with the badge text and confused users familiar with language switchers / segmented controls. Now the icon matches the badge: Mobile mode shows the phone icon, Web mode shows the monitor icon. Applied to both `references/index.html` and `references/viewer.html`.

#### Internal
- `extract_zips.py`: removed the `_NO_SCROLLBAR_CSS` constant and the in-place HTML mutation. `_copy_html()` is now a 3-line `shutil.copy2()` wrapper kept for symmetry with the `_process_zip` / `_process_dir` paths.

## [1.10.0] - 2026-04-30

### Added
- **`/release` — private-repo handling** — when the GitHub repo is private, the workflow now skips both the git tag and the GitHub release by default (tags/releases are distribution artifacts the maintainer typically doesn't need on a private repo). Public/internal repos behave as before. Append `con tag` / `with tag` to the confirmation to force-create the tag on a private repo (the GitHub release stays skipped). Detection uses `gh repo view --json visibility`; falls back to public-mode behavior if `gh` is unavailable or the remote isn't GitHub.

### Fixed
- **stitch-showcase: hardcoded script paths broke plugin installs** — `SKILL.md` instructed the AI to run `python ~/.claude/skills/stitch-showcase/scripts/build_showcase.py`, but plugin installs live at `~/.claude/plugins/cache/<plugin>/<version>/skills/stitch-showcase/`, so the first run failed with `[Errno 2] No such file or directory`. All 9 invocations of `build_showcase.py` and `apply_canonical.py` now use a `<SKILL_DIR>/scripts/...` placeholder, and a new "Script paths" section at the top of `SKILL.md` instructs the AI to substitute the absolute path provided in the "Base directory for this skill" system message — which works for both plugin and standalone installs.

## [1.9.3] - 2026-04-28

### Changed
- **`refactoring-ui` skill restructured** — consolidated from 8 chapter-mirror reference files (one per book chapter) to 4 thematic files (`foundations`, `page-mechanics`, `visual-treatment`, `polish`). All 69 sections preserved; section titles that paralleled the book's table of contents reworded to reduce structural similarity with the source material.
- **`refactoring-ui` attribution strengthened** — `SKILL.md` and each reference file now explicitly note the principles are paraphrased from *Refactoring UI* by Adam Wathan & Steve Schoger, with a pointer to refactoringui.com to buy the original book.

## [1.9.2] - 2026-04-28

### Changed
- **README install snippet uses lowercase marketplace slug** — `/plugin marketplace add maccesar/aiskills` instead of `macCesar/aiskills`, to avoid Claude Code's `ENOENT` rename bug on macOS APFS case-insensitive filesystems when the GitHub URL has uppercase characters.
- **`aiskills status` clarifies "Last check" label** — renamed to `Last npm check` so users don't confuse it with marketplace or other update sources.

## [1.9.1] - 2026-04-28

### Fixed
- **`/release` no longer silently switches back to the feature branch after `mode=merge`.** Phase 4 step 6 used to run `git checkout <feature-branch>` after the fast-forward merge to "return the user to where they started" — but if you confirmed `merge`, you signaled that the feature branch is done, so landing back on it created a confusing post-state. Now stays on `main`. PR mode is unchanged (the branch is still live, so staying on it is correct). Final report note updated to `merged to main; now on <main-branch>`.

## [1.9.0] - 2026-04-28

### Changed
- **`/release` rewritten as full janitor** — handles the common case where the working tree has uncommitted work plus a release intent. Reads each modified/untracked file's diff, infers intent, and groups files into N proposed semantic commits before the release commit. Plan preview shows N+1 commits in one compact block; the user can ask to merge, split, or skip any of the N before confirming.
- **`/release` — optional main alignment** — when run from a feature branch, the plan now offers fast-forward merge to main or PR creation via `gh`. Confirmation tokens: `proceed` (release only), `merge` (release + ff-merge), `PR` (release + pull request).
- **`/release` — README gap detection** — Step 1 scans for new user-visible surface (commands, flags, APIs) and updates the README as part of the release commit when documentation is missing.
- **`/release` — verbosity discipline** — Steps 1–3 silent (no per-step headers), Step 4 prints one compact plan block, Step 5 executes silently with a single-line final report.

## [1.8.0] - 2026-04-28

### Added
- **Slash commands sync** — `aiskills install/update` now copies `commands/*.md` to `~/.claude/commands/` (or `<project>/.claude/commands/` in local mode). `aiskills uninstall` removes them. New `COMMANDS` array in `lib/config.js` controls what gets synced.
- **`/release` slash command** — project-agnostic release workflow: detects project type (npm, Titanium, Composer, Cargo, CocoaPods, versionless), infers semver bump from Conventional Commits, updates CHANGELOG and README, commits, pushes, tags, and creates the GitHub release via `gh`.
- **Scope selection in `aiskills update`** — when both global and local skills exist, prompts the user to choose Global / Local / Both.
- **`downloader.js` helpers** — `fetchLatestRelease()`, `fetchLatestVersion()`, `downloadRawFile()`, plus `AISKILLS_TEST_NPM_LATEST_VERSION` env override for tests.
- **Plugin Marketplace integration** — `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` for Claude Code plugin distribution.
- **`docs/MAINTAINER-GUIDE.md`** and **`hooks/`** directory.

### Changed
- **`aiskills list`** — reads each skill's `SKILL.md` directly from the installed location (`~/.agents/skills/`), shows ✓/✗ install status per skill, and prints footer pointers to `aiskills status` and `aiskills doctor`.
- **SKILL.md descriptions normalized** — `refactoring-ui`, `stitch-showcase`, and `vscode-extension-dev` converted from YAML folded scalar (`description: >`) to single-line format, matching `humaniza` and Anthropic's canonical skill style.

### Fixed
- **`aiskills update` false-positive on home directory** — when run from `~/`, the command no longer asks "Both local and global skills detected" because both paths resolve to the same `.agents/skills/` directory. Now skips local detection when `cwd === os.homedir()`.

## [1.7.0] - 2026-04-08

### Added
- **`aiskills auto-update`** — Full update pipeline: checks npm once per day, updates CLI, syncs skills, refreshes symlinks. Supports `--silent` flag for hook usage.
- **Claude Code SessionStart hook** — Installed by `aiskills install`, runs `aiskills auto-update --silent` at session start. Removed by `aiskills remove`.
- **Update cache** (`~/.aiskills/last-check.json`) — Prevents hitting npm registry on every invocation. Checks at most once every 24 hours.
- **Dev mode detection** — Skips npm update when running from source (`npm link`).
- **`aiskills status`** — Quick overview of installation: version, skills count, hook, last update check, and platform symlinks.
- **`aiskills doctor`** — Diagnoses installation health: verifies each skill directory, validates symlinks (detects broken ones), reports issues with fix suggestions.

## [1.6.0] - 2026-03-28

### Changed
- **stitch-showcase: fast build + optional AI enrichment** — restructured the SKILL workflow into 4 distinct modes instead of a linear pipeline. Mode 1 (Build) runs the Python script instantly (~3 seconds) with zero AI pre-processing — no pre-flight questions, no DESIGN.md enrichment, no `--extract-text`. Mode 2 (Enrich) is on-demand when the user asks to optimize — improves titles, descriptions, and hero text in DESIGN.md without re-grouping sections, then rebuilds. Mode 3 (Update) and Mode 4 (Standardize) remain unchanged.

### Fixed
- **stitch-showcase: view mode leaking between projects** — localStorage key for view mode (mobile/web) was global (`showcase-view-mode`), so opening a web showcase and then a mobile one would show mobile screens in web layout. Now scoped per project (`showcase-view-mode-{project-slug}`).
- **stitch-showcase: catalog loading overlay stuck under Live Server** — added safety timeout and `.catch()` handler so the loading overlay always resolves, even when `srcdoc` iframes don't fire `load` events (common with VS Code Live Server and strict CSP environments). Worst case the overlay hides after 15 seconds instead of hanging forever.
- **stitch-showcase: type detection now reads `## Type` section** — `parse_design_md` now checks the explicit `## Type` section first (authoritative) before falling back to keyword scoring. Previously it only used keyword scoring, which could miss or contradict an explicit `## Type\nweb` declaration.
- **stitch-showcase: screen-based type detection fallback** — when no DESIGN.md type or `showcase.json` type is available, the build script now analyzes all screen HTMLs (viewport meta, fixed widths, media queries, sidebar patterns) and uses majority vote instead of blindly defaulting to "mobile".

### Removed
- **stitch-showcase: pre-flight questions before build** — the build no longer blocks on Q1/Q2/Q3 (source, type, name). The script handles smart defaults; `--type` and `--name` are only needed if the script fails or the user explicitly overrides.
- **stitch-showcase: mandatory AI enrichment before build** — Step 2b (Suggest Sections) is no longer required before running the build script. AI enrichment is now opt-in via Mode 2.
- **stitch-showcase: linear workflow graph** — replaced with a 4-mode branching flow diagram.

## [1.5.0] - 2026-03-28

### Added
- **stitch-showcase: integrated component catalog** — catalog.html is now generated automatically as part of every build (no `--catalog` or `--components` flags needed). The showcase always produces 3 pages: index.html, viewer.html, and catalog.html.
- **stitch-showcase: faithful component previews** — catalog previews now render with the original Tailwind CDN + config extracted from screen HTMLs, showing components with their actual colors, fonts, and spacing instead of unstyled HTML.
- **stitch-showcase: comparison view** — catalog.html displays component variants side-by-side in cluster groups. Each card shows a styled preview, canonical badge (★), similarity score, screen count, and difference description. Structural components (navbars, footers) and atomic components (buttons, inputs) are organized by type with context-aware clustering.
- **stitch-showcase: "Already Unified" section** — components that have only one variant across all screens are grouped in a collapsible section, showing at a glance which parts of the design are already standardized.
- **stitch-showcase: similarity clustering for atomics** — atomic components (buttons, headings, inputs, badges, links, icons) are now clustered by structural similarity (85% threshold) within semantic context (form buttons separate from CTA buttons). Each cluster auto-selects a canonical version.
- **stitch-showcase: `apply_canonical.py`** — new script to replace component variants with a chosen canonical version across screen HTMLs. Supports both structural components (via semantic block replacement) and atomic components (via cluster-based snippet replacement). Usage: `python apply_canonical.py /path/to/assets/ navbar home_screen`.
- **stitch-showcase: catalog link in index.html** — the gallery navbar now includes a "Catalog" link to catalog.html for easy navigation between pages.

### Removed
- **stitch-showcase: `--catalog` and `--components` CLI flags** — catalog generation is now automatic. These flags are no longer needed.

### Changed
- **stitch-showcase: catalog output renamed** — `components-catalog.html` → `catalog.html` for cleaner URLs.

## [1.4.0] - 2026-03-28

### Changed
- **stitch-showcase: unified mobile/web into single showcase with view toggle** — merged 4 separate templates (`index-mobile.html`, `index-web.html`, `viewer-mobile.html`, `viewer-web.html`) into 2 unified templates (`index.html`, `viewer.html`). A view mode toggle button lets users switch between mobile (portrait phone cards, phone frame viewer) and web (landscape browser cards, browser chrome viewer) at any time. The `--type` flag now sets the **default view**, not the template or output directory.
- **stitch-showcase: single output directory** — all builds now output to `showcase/` instead of `showcase-mobile/` or `showcase-web/`. View mode is controlled via CSS classes and persisted in localStorage.
- **stitch-showcase: viewer description placement** — screen description now displays inline after the title instead of right-aligned with `ml-auto`, improving readability.
- **stitch-showcase: card aspect ratios driven by CSS** — card thumbnails no longer use inline `aspect-ratio` styles. Instead, `.view-mobile` and `.view-web` classes on `<html>` control the aspect ratio via CSS, enabling instant switching without page reload.

## [1.3.1] - 2026-03-28

### Added
- **stitch-showcase: `showcase.json` support** — optional config file in the project root that tells the build script where to find screens, the project type, and name. Eliminates the need to pass the exact source folder path.
- **stitch-showcase: source auto-discovery** — when the given path has no screens, the script searches for `showcase.json` (in the path or its parent), then auto-scans subdirectories one level deep. Skips `showcase-*` output dirs. Clear error messages with suggestions when nothing is found.
- **stitch-showcase: `--init` generates `showcase.json`** — alongside DESIGN.md, `--init` now creates a `showcase.json` in the project root pointing to the detected source folder.

### Fixed
- **stitch-showcase: search bar moved out of navbar** — search input relocated from the fixed navbar to below the section tabs, giving the navbar a cleaner look and the search more room.
- **stitch-showcase: list view spacing** — added 16px gap between thumbnail and text, plus top padding on the info block for better vertical alignment.
- **stitch-showcase: list view square thumbnails** — mobile list view now uses 140px square thumbnails (`aspect-ratio: 1/1`) instead of tall phone-shaped previews, saving vertical space.

## [1.3.0] - 2026-03-28

### Added
- **stitch-showcase: `--components` flag** — new `detect_components.py` script detects shared components (navbar, footer, tabbar, sidebar, header) across screen HTMLs, groups variants by similarity (DOM structure 50% + CSS classes 30% + text 20%), and recommends a canonical version. Outputs `shared_components.json`.
- **stitch-showcase: `--catalog` flag** — new `extract_catalog.py` script extracts atomic components (buttons, headings, inputs, badges, links, icons) and composite components (cards, price tables, CTAs, testimonials, heroes) from all screens. Deduplicates by normalized HTML hash. Outputs `component_catalog.json` + visual `components-catalog.html`.
- **stitch-showcase: `component_utils.py`** — shared HTML parsing utilities using stdlib `html.parser` and `difflib`. Provides DOM tree parsing, semantic block extraction, similarity scoring, and normalization helpers.
- **stitch-showcase: `catalog-template.html`** — visual component catalog template with tabbed navigation, inline previews, CSS property display, copyable code snippets, dark/light toggle, and search.
- **stitch-showcase: SKILL.md Step 6** — "Standardize Shared Components" workflow: detect → present variants → user chooses → apply canonical → rebuild.
- **stitch-showcase: SKILL.md Step 7** — "Generate Component Catalog" workflow: extract → visual muestrario → browse/copy components.
- **stitch-showcase: reference docs** — `10-component-standardization.md` (detection strategy, similarity scoring, canonical selection) and `11-component-catalog.md` (atomic/composite extraction, deduplication, design tokens).
- **stitch-showcase: `skill_version` in context JSON** — `showcase_context.json` now includes `skill_version` field to track which version of the skill generated the output.

### Fixed
- **stitch-showcase: list-mode thumbnails too small** — increased list-mode thumbnails from `120×80px` to `180px` wide with proper aspect ratio (9:19.5 for mobile, 16:10 for web) and rounded corners.
- **stitch-showcase: `--catalog` now includes shared component detection** — running `--catalog` automatically detects shared components (navbars, footers, tabbars) via `detect_components` and integrates them as a "Shared Components" section in the visual catalog. No need to run `--components` separately.
- **stitch-showcase: shared components integrated in catalog** — `shared_components.json` data now renders inside `components-catalog.html` with canonical versions highlighted (accent border + "Canonical" badge), variant similarity bars, and difference descriptions.
- **stitch-showcase: skill version badge in catalog** — `components-catalog.html` header now shows the skill version (`v1.3.0`) via `{{SKILL_VERSION}}` placeholder for traceability.

### Changed
- **stitch-showcase: architecture — always use templates** — SKILL.md now explicitly instructs the AI to NEVER generate index.html or viewer.html manually. The build script always generates HTMLs from pre-built templates (seconds, not minutes). The AI's role is enriching DESIGN.md before the build, not writing HTML after it. The `--context` flag is marked as debug-only.

## [1.2.0] - 2026-03-28

### Added
- **stitch-showcase: `--extract-text` flag** — new `extract_text.py` script extracts visible text (headings, paragraphs, buttons, lists, inputs, colors, fonts) from screen HTML files and writes a compact `screen_summaries.txt`. Reduces LLM token consumption by ~96% compared to reading full HTML files (149 lines vs 4000+ for 19 screens).
- **stitch-showcase: `extract_text.py` script** — standalone module for extracting visible text from Stitch HTML exports. Strips scripts, styles, SVGs, and comments. Outputs structured summaries suitable for LLM consumption.

### Fixed
- **stitch-showcase: web card backgrounds** — changed thumbnail background from `bg-black` to `bg-white dark:bg-[#1a1a1a]` for web type cards, preventing dark background bleed on light web screenshots
- **stitch-showcase: viewer-web browser chrome** — wrapped browser chrome bar and iframe in `max-w-[1440px]` container with padding and rounded bottom corners, preventing full-bleed layout

### Changed
- **stitch-showcase: SKILL.md Step 2b** — updated workflow to use `--extract-text` flag and read `screen_summaries.txt` instead of reading each HTML file individually

## [1.1.1] - 2026-03-27

### Added
- **stitch-showcase: `--update` flag** — detects screens not yet in any DESIGN.md section and appends them under `### Por Clasificar`; existing sections and descriptions are untouched. Workflow step 0 added to SKILL.md.

## [1.1.0] - 2026-03-27

### Added
- **stitch-showcase** — Converts Google Stitch exports (zips with `code.html` + `screen.png`) into a navigable showcase with `index.html` + `viewer.html`. Supports mobile (phone frame) and web (browser chrome). Includes 3 Python scripts and 4 HTML reference templates. (7 files)

#### Viewer (viewer-mobile.html, viewer-web.html)
- Prev/Next navigation — arrow buttons + keyboard shortcuts (← / →); position badge shows `N / total`
- Fullscreen mode — `F` key or button hides the header; phone scales to fill the viewport
- Smart default theme — opens light or dark based on app surface color luminance (dark app → light showcase)
- Google Fonts injection — font extracted from `## Typography` in DESIGN.md and applied to the showcase UI

#### Index (index-mobile.html, index-web.html)
- Searchable thumbnail grid — mobile 9:19.5, web 16:10 aspect ratios
- Section filter tabs — pill buttons per section with screen count; shown only when 2+ sections exist
- Grid / List toggle — compact horizontal list view (thumbnail + full title + description)
- Same smart default theme and Google Fonts injection as the viewer

#### Build script (build_showcase.py)
- Screen count per section label — `Section Name (N)`
- Dark/light variant badge — slugs ending in `_oscuro`/`_dark` get a dark pill; `_claro`/`_light` get a light pill
- `--watch` flag — polls source folder every 2 s and auto-rebuilds on changes (Ctrl+C to stop)
- `--init` flag — generates a `DESIGN.md` skeleton with auto-grouped slugs; backs up existing file
- Color token extraction — parses `` `token-name` (#XXXXXX) `` format; maps `primary-*` → accent, `surface` → theme source
- Accepts individual zip folder, pre-extracted folders, or a single mega-zip directly

#### Parser (parse_design_md.py)
- `_extract_color_tokens()` — backtick-wrapped and bare token formats; semantic `accent` and `surface` keys
- `_surface_default_theme()` — luminance formula (0.299R + 0.587G + 0.114B) → `"light"` or `"dark"`
- `_extract_typography()` — finds font name in `## Typography` (bold text, 1–3 words); falls back to `font-family:` in doc

#### Extractor (extract_zips.py)
- Incremental builds — skips extraction when output `.html` is newer than source zip/folder; prints `↩ slug (unchanged)`

#### Workflow (SKILL.md)
- Step 2b: AI section suggestion — uses `--init` to scaffold DESIGN.md, then AI suggests logical groupings
- Step 5b: AI description enrichment — AI reads `assets/{slug}.png` and generates 1-sentence descriptions for slug-only cards

## [1.0.0] - 2026-03-18

### Added
- CLI tool (`aiskills`) with `install`, `update`, and `remove` commands
- Multi-platform support: Claude Code, Gemini CLI, Codex CLI
- Global and local (`--local`) installation modes
- Custom path installation (`--path`)
- Automatic platform detection and symlink management
- `aiskills list` command to show available skills with descriptions
- Skills shown when invoking `aiskills list` from the command line

### Skills
- **refactoring-ui** - Design advisor based on "Refactoring UI" by Adam Wathan & Steve Schoger (8 reference files)
- **humaniza** - Spanish text editor (es-MX) that removes AI writing patterns (6 reference files)
- **vscode-extension-dev** - VS Code extension development guide covering TreeView, Webview, QuickPick, StatusBar, SecretStorage, esbuild bundling, and publishing (4 reference files)
