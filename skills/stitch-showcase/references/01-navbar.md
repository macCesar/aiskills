# Section: Navbar

## Purpose

Sticky header that orients the user: project identity, type badge, screen count, and quick-access controls (view toggle, theme toggle, search).

## Data Required (from showcase_context.json)

- `project_name` — display in header
- `type` — "mobile" or "web" badge
- `screen_count` — total screens badge
- `default_theme` — initial light/dark state
- `font_family` — apply as primary font

## Design Requirements

- **Sticky** `top-0 z-50` with subtle backdrop blur and bottom border
- **Left**: project name (truncated on mobile), type badge pill, screen count pill
- **Right**: search input (expandable on mobile), grid/list view toggle, light/dark theme toggle
- Height: 56px desktop, 48px mobile
- Background: translucent white (light) / translucent dark (dark) with `backdrop-filter: blur(12px)`
- Border bottom: `1px solid` with low-opacity color
- Typography: project name in `font-semibold text-sm`, badges in `text-xs`

## Functional Requirements

- **View toggle**: switches gallery between grid and list mode; persists choice in `localStorage('showcase-view')`
- **Theme toggle**: switches `<html>` class `dark`; persists in `localStorage('showcase-theme')`
- **Search**: filters screen cards by title/description; debounced input; shows "No results" empty state
- All buttons: `focus-visible:ring-2` for keyboard accessibility

## Anti-Patterns

- Do NOT use opaque backgrounds — the blur-through effect is essential for depth
- Do NOT put navigation links (there are no pages to navigate to)
- Do NOT use colored/branded backgrounds for the navbar — always neutral

## Structural Pattern

```
<header> sticky top-0 z-50 backdrop-blur
  <div> max-w-7xl mx-auto flex items-center justify-between px-6
    <div> left: project name + badges
    <div> right: search + view toggle + theme toggle
```

## Contract (Required IDs/Classes)

- `id="theme-toggle"` — theme switch button
- `id="view-toggle"` — grid/list toggle button
- `id="search-input"` — search input field
- `.filter-tab` — section filter tab buttons (used by gallery filtering JS)
