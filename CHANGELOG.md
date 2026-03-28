# Changelog

All notable changes to this project will be documented in this file.

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
