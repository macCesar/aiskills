# Section: Type Detection & Routing

## Purpose

Intelligent per-screen type detection that ensures web designs open in the web viewer (full-width) and mobile designs open in the mobile viewer (phone frame). Solves the critical bug where web designs were displayed inside a phone frame.

## Data Required (from showcase_context.json)

- `type` — project-level type ("mobile" or "web")
- Each screen's `detected_type` — per-screen type ("mobile", "web", or "unknown")

## How Detection Works (in build_showcase.py)

Each screen's HTML is analyzed for these signals:

| Signal | Points | Type |
|--------|--------|------|
| `user-scalable=no` in viewport meta | +2 | mobile |
| `maximum-scale=1` in viewport meta | +1 | mobile |
| Fixed widths 375-430px in CSS | +2 | mobile |
| Desktop breakpoints (768px+) in media queries | +2 | web |
| Sidebar/nav-rail/drawer patterns | +1 | web |
| Wide fixed widths (900px+) | +1 | web |

If mobile score > web score → mobile. If web > mobile → web. Tie → "unknown".

## Routing Rules

### In index.html (Gallery Cards)

When generating card links, the AI must use the correct viewer:

```
if screen.detected_type === "web":
    link → viewer-web.html?screen=...
elif screen.detected_type === "mobile":
    link → viewer-mobile.html?screen=...
elif screen.detected_type === "unknown":
    link → viewer based on project-level type
```

### Single vs Dual Viewer Strategy

**Option A — Two separate viewer files** (simpler):
- `viewer-web.html` — always renders full-width with browser chrome
- `viewer-mobile.html` — always renders in phone frame
- Cards link to the appropriate one

**Option B — Single viewer.html with mode parameter** (DRYer):
- `viewer.html?screen=...&mode=web` or `mode=mobile`
- Viewer reads mode param and adjusts layout accordingly
- Prev/next must respect mode of each screen

**Recommended**: Option B for mixed-type projects, Option A when all screens are the same type.

### Gallery Card Aspect Ratios

Cards in the gallery should adapt their thumbnail aspect ratio:
- Mobile screens: `aspect-ratio: 9/16` (tall portrait)
- Web screens: `aspect-ratio: 16/10` (wide landscape)
- This provides visual differentiation even before clicking

### Mixed-Type Badges

For projects with both web and mobile screens, add a small badge on cards:
- Mobile screens: phone icon or "Mobile" pill
- Web screens: monitor icon or "Web" pill
- Only show these badges in mixed-type projects (when both types exist)

## Anti-Patterns

- **NEVER** route all screens to the same viewer regardless of type — this is the bug being fixed
- Do NOT ignore `detected_type` and only use project-level `type`
- Do NOT show web designs in a phone frame under any circumstance
- Do NOT show mobile designs in a full-width iframe (they'll be tiny and lost)

## Contract

- Viewer URL must include type/mode information
- `detected_type` field must be present on every screen in the context JSON
- Gallery cards must use adaptive aspect ratios based on detected_type
