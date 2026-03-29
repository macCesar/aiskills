# Section: Viewer — Web

## Purpose

Full-screen viewer for web (desktop/dashboard) designs. Displays the screen's HTML in an iframe that fills the available viewport width, mimicking a real browser window with chrome decoration.

## Data Required (from URL parameters)

- `screen` — path to the HTML file (e.g., `assets/dashboard.html`)
- `title` — screen title for the header
- `desc` — screen description

## Data Required (from showcase_context.json — embedded in viewer)

- `all_screens` — flat ordered list for prev/next navigation
- `font_family` — consistent typography
- `default_theme` — initial theme
- `project_name` — page title

## Design Requirements

### Browser Chrome Bar

- A decorative bar at the top of the iframe area simulating a browser window:
  - Three dots (red/yellow/green) on the left
  - URL bar in the center showing the screen slug (non-functional, decorative)
  - Subtle rounded corners on the chrome bar
- The chrome bar is purely decorative — it frames the web design to feel like viewing a real website

### Iframe Container

- **Full viewport width** within content area (no phone frame!)
- `width: 100%` with natural height based on content, or `height: calc(100vh - header - chrome)`
- No artificial width constraints — web designs must breathe
- Border: subtle `1px solid` border around the iframe area
- Background: neutral dark (matches iframe loading state)

### Header Bar

- Compact header (48-56px) with:
  - Back button (← or X) that calls `window.close()` or navigates back
  - Screen title (truncated)
  - Screen description (right-aligned, muted, hidden on mobile)
  - Prev/Next navigation arrows
  - Fullscreen toggle button

### Navigation

- **Prev/Next**: arrow buttons cycle through `all_screens` in order
- **Keyboard shortcuts**: Left/Right arrow keys for prev/next, Escape to go back, F for fullscreen
- Wrap around: after last screen, next goes to first

## Functional Requirements

- **URL-driven**: reads `?screen=...&title=...&desc=...` params on load
- **Prev/Next updates URL** without page reload (history.replaceState)
- **Fullscreen**: Fullscreen API on the iframe container (not the whole page)
- **Theme**: respects localStorage theme setting from index.html
- **Responsive**: on very small screens, hide the chrome bar and description, keep core functionality

## Anti-Patterns

- **NEVER** use a phone frame for web designs — this is the critical bug being fixed
- **NEVER** constrain the iframe to a fixed narrow width (like 390px)
- Do NOT add scrollbars around the iframe — let the iframe content handle its own scroll
- Do NOT use a heavy header that competes with the design being viewed

## Structural Pattern

```
<html>
  <head> title, theme setup, Tailwind CDN, font
  <body> flex flex-col h-screen
    <header> compact bar
      <button> back
      <span> title
      <span> description (desktop only)
      <div> prev / next / fullscreen buttons

    <main> flex-1 overflow-hidden
      <div> browser-chrome-bar
        <div> three dots
        <div> fake URL bar
      <div> iframe-container
        <iframe> src={screen param} width=100% height=100%

    <script>
      - Parse URL params
      - Load all_screens from embedded JSON
      - Prev/next navigation
      - Keyboard shortcuts
      - Fullscreen toggle
      - Theme management
```

## Contract

- `id="viewer-frame"` — the iframe element
- `id="screen-title"` — title display
- `id="screen-desc"` — description display
- `id="btn-back"` — back/close button
- `id="btn-prev"` / `id="btn-next"` — navigation buttons
- `id="btn-fullscreen"` — fullscreen toggle
- URL format: `viewer.html?screen={path}&title={title}&desc={desc}`
- `SCREENS_DATA` — embedded JSON array of all screens (for prev/next)
