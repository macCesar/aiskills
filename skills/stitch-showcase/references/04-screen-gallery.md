# Section: Screen Gallery

## Purpose

The main browsing area where users explore all screens. Organized by sections with filterable tabs, searchable, and switchable between grid and list views.

## Data Required (from showcase_context.json)

- `sections` — array of `{name, key, screens}` for section grouping and tabs
- `all_screens` — flat list for search/filter
- Each screen: `slug`, `title`, `description`, `html_file`, `png_file`, `detected_type`
- `type` — project-level type for default aspect ratios
- `color_tokens.accent` or `colors.primary` — accent color for hover/active states

## Design Requirements

### Section Tabs

- Horizontal scrollable pill bar below the navbar (or inside gallery header)
- "All" tab + one tab per section with screen count badge
- Active tab: accent color background with white text
- Inactive: ghost pill with hover state
- Tabs scroll horizontally on mobile with `-webkit-overflow-scrolling: touch`

### Screen Cards (Grid Mode)

- **Aspect ratio adapts to screen type**:
  - If `detected_type === "mobile"` → `aspect-ratio: 9/16` (portrait phone)
  - If `detected_type === "web"` → `aspect-ratio: 16/10` (landscape desktop)
  - If `detected_type === "unknown"` → use project-level `type` default
- Thumbnail: `object-cover object-top` for natural cropping
- Card structure: thumbnail on top, title + description below, separated by subtle border
- Hover: slight scale (1.02), accent border, elevated shadow
- Dark/light variant badge: if slug ends with `_oscuro`/`_dark` → dark badge; `_claro`/`_light` → light badge
- Grid: 4 columns for mobile screens, `auto-fill minmax(280px, 1fr)` for web screens
- Gap: 16-20px between cards

### Screen Cards (List Mode)

- Horizontal card: small thumbnail (120px wide) on left, title + full description on right
- No line-clamp on description in list mode
- Compact vertical spacing (8px gap)

### Empty State

- When search yields no results: centered message with muted icon and "No screens match your search" text
- When a section has 0 screens: section is hidden from tabs

### Card Link Behavior

- Each card links to `viewer.html?screen={html_file}&title={title}&desc={description}`
- **Critical**: if `detected_type === "web"`, link to the web viewer. If `detected_type === "mobile"`, link to the mobile viewer.
- Opens in new tab (`target="_blank"`)

## Functional Requirements

- **Section filtering**: clicking a tab shows only that section's cards; "All" shows everything
- **Search**: filters cards by title and description text match (case-insensitive)
- **View toggle**: switches between grid and list layouts; persists in localStorage
- **Smooth transitions**: cards fade/slide when filtering sections
- Cards use `loading="lazy"` on thumbnail images

## Anti-Patterns

- Do NOT use uniform aspect ratios for mixed web+mobile projects — web screens in portrait cards look broken
- Do NOT hide descriptions in grid mode — they provide context for choosing which screen to view
- Do NOT use tiny cards — minimum card width of 200px for mobile, 240px for web
- Do NOT use pagination — show all screens and rely on section tabs + search for navigation

## Structural Pattern

```
<section> gallery: max-w-7xl mx-auto px-6
  <div> gallery-header
    <h2> "Screens" + intro text
    <div> section tabs (pill bar)

  <div> screens-container
    for each section:
      <section> data-section="{key}"
        <h3> section name + count
        <div> screens-grid: grid of cards
          for each screen:
            <a> screen-card → viewer.html?...
              <div> card-thumb: aspect-ratio based on detected_type
                <img> thumbnail
                <span> dark/light badge (conditional)
              <div> card-info
                <p> title
                <p> description
```

## Contract (Required IDs/Classes)

- `.screen-section[data-section="{key}"]` — section wrapper for tab filtering
- `.screen-card` — each card element
- `.screens-grid` — the grid container (JS toggles `.list-mode` class)
- `.filter-tab[data-section="{key}"]` — tab buttons
- `.card-thumb` — thumbnail container
- `.card-info` — text info container
- `.card-desc` — description paragraph
- Viewer URL format: `viewer.html?screen={html_file}&title={encodeURIComponent(title)}&desc={encodeURIComponent(description)}`
