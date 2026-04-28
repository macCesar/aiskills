# Changelog

All notable changes to this project will be documented in this file.

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
