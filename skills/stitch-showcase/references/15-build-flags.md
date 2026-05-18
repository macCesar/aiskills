# Build Script Reference

Detailed reference for `scripts/build_showcase.py` — flags, output structure, source discovery, and supported input layouts.

## Running the build

```bash
# Point to the project root — the script discovers the source automatically
python <SKILL_DIR>/scripts/build_showcase.py /path/to/project

# Or point directly to the folder with zips/screens
python <SKILL_DIR>/scripts/build_showcase.py /path/to/project/stitch

# Single mega-zip (zip containing all screens as subfolders)
python <SKILL_DIR>/scripts/build_showcase.py /path/to/export.zip
```

## Flags

| Flag | Description |
|------|-------------|
| `--type mobile\|web` | Set default view mode instead of auto-detecting |
| `--name "Title"` | Set project name when no DESIGN.md is present |
| `--init` | Generate a DESIGN.md skeleton from detected screen slugs |
| `--update` | Detect new screens not yet in DESIGN.md and append under `### Por Clasificar` |
| `--extract-text` | Extract visible text from screen HTMLs → `screen_summaries.txt` (for LLM consumption) |
| `--context` | (Debug only) Generate showcase_context.json without building HTML — do NOT use for normal builds |
| `--watch` | Auto-rebuild on file changes (Ctrl+C to stop) |

Component detection and catalog generation are automatic — no `--catalog` or `--components` flags needed. Every build produces `catalog.html` alongside `index.html` and `viewer.html`.

## Output structure

The script creates a single `showcase/` directory next to the source folder:

```
showcase/                         ← single output dir (view mode toggle inside)
├── index.html                    ← open this in browser (gallery + design system)
├── viewer.html                   ← individual screen viewer
├── catalog.html                  ← component catalog with comparison view
├── component_catalog.json        ← atomic + composite + cluster data
├── shared_components.json        ← structural component variants
├── DESIGN.md                     ← copy from source
└── assets/
    ├── splash_screen.html
    ├── splash_screen.png
    ├── login.html
    ├── login.png
    └── ...
```

Source folder with original zips is **never touched**.

## Source discovery

The script accepts **any folder in the project** — it doesn't need to be the exact folder with screens. Discovery order:

1. If the given path has screens (zips or `code.html` folders) → use it directly
2. If `showcase.json` exists in the given path or its parent → follow its `source` field
3. Auto-discover: scan one level of subdirectories for screens (skips `showcase`, `showcase-mobile`, `showcase-web` output dirs)
4. Clear error with a suggestion to create `showcase.json`

## Supported input structures

| Structure | Example |
|-----------|---------|
| Project root with `showcase.json` | `project/showcase.json` → `{"source": "stitch"}` |
| Folder of individual zips | `folder/login.zip`, `folder/home.zip` |
| Folder of pre-extracted screen folders | `folder/login/code.html`, `folder/home/code.html` |
| Single mega-zip (Stitch "Export all") | `export.zip → stitch/screen1/code.html, stitch/screen2/code.html` |
| Single screen zip | `screen.zip → code.html + screen.png` |
