# DESIGN.md & showcase.json Format

Configuration formats that drive the showcase build: project metadata, screen grouping, and description fallbacks.

## DESIGN.md Format

```markdown
# Project Name

## Type
mobile  ← or "web"

## Screens
### Onboarding
- splash_screen
- login

### Home
- home_dashboard

## Colors
- Primary: #FDD900
- Background: #0A0A0A

## Typography
- **Inter**
```

The parser also accepts:

- Free-form bullets/numbered lists under `## Screens`
- Markdown table format: `| slug | title | description |`
- Color tokens in Stitch format: `` `primary-container` (#FDD900) `` or bare `surface (#0B1326)`
  - Token named `primary-*` → accent color for tabs and hover
  - Token named `surface` or `background` → used to compute smart showcase theme
- Optional `## Lang` section to override `<html lang>` (e.g. `es`, `en`, `pt-BR`). Auto-detected from content if absent. See [`13-language-detection.md`](13-language-detection.md).

The `--init` flag auto-generates a skeleton DESIGN.md from detected slugs.

## Screen Grouping

Screens are grouped into sections in this priority order:

1. **`DESIGN.md` sections** (best result) — explicit `### Section Name` blocks under `## Screens`
2. **Auto-grouping** (fallback) — keyword overlap between slugs; screens sharing a meaningful word are grouped together

When auto-grouping applies, offer to improve it:

- List the detected screen names for the user
- Suggest logical section groupings based on the app domain
- Write the sections to `DESIGN.md` in the source folder
- Re-run the script to apply them

### DESIGN.md section format for explicit grouping

```markdown
## Screens
### Onboarding
- splash_screen
- welcome

### Login & Registration
- login
- signup
- forgot_password

### Home
- home
- home_oscuro
```

The script merges DESIGN.md sections with slug auto-detection — slugs not listed in any section appear in an "Other screens" group at the end.

## Description Sources (priority)

When building cards, the script picks the description from these sources, in order:

1. `DESIGN.md` — screen list with descriptions
2. Individual `{num}-{name}.md` in source folder (per-screen prompt files)
3. `<meta name="description">` or `<meta property="og:description">` inside the HTML
4. First `<h1>` or `<h2>` visible text in the HTML body
5. `<title>` tag (skipped if generic: "Untitled", "index", "screen", etc.)
6. First meaningful visible text phrase found in the HTML body (strips scripts/styles/SVGs)
7. Formatted slug fallback ("splash_screen" → "Splash Screen")

Stitch-exported HTML rarely has `<title>` or meta descriptions — steps 4 and 6 are the most useful for those files.

## showcase.json

Optional config file in the project root. Tells the script where to find screens, the project type, and name — so you can point the script at any folder in the project.

```json
{
  "source": "stitch",
  "type": "mobile",
  "name": "SNAP Gym"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `source` | yes | Relative path from the JSON file to the folder with screens |
| `type` | no | `"mobile"` or `"web"` (overridden by `--type` CLI flag) |
| `name` | no | Project name (overridden by `--name` CLI flag or DESIGN.md) |
| `lang` | no | BCP-47 code for `<html lang>` (e.g. `"es"`, `"pt-BR"`). Overrides DESIGN.md auto-detect. See [`13-language-detection.md`](13-language-detection.md). |

The `--init` flag generates this file automatically alongside DESIGN.md.
