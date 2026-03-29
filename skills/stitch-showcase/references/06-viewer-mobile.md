# Section: Viewer — Mobile

## Purpose

Viewer for mobile app designs. Displays the screen's HTML inside a realistic phone frame (390×844), centered on the page, with device-like bezel styling.

## Data Required (from URL parameters)

- `screen` — path to the HTML file (e.g., `assets/login.html`)
- `title` — screen title for the header
- `desc` — screen description

## Data Required (from showcase_context.json — embedded in viewer)

- `all_screens` — flat ordered list for prev/next navigation
- `font_family` — consistent typography
- `default_theme` — initial theme
- `project_name` — page title

## Design Requirements

### Phone Frame

- **Dimensions**: 390×844px (iPhone 14/15 logical resolution)
- **Bezel**: 8px solid border with rounded corners (40px border-radius)
- **Notch/Dynamic Island**: optional decorative element at the top (a small pill shape)
- **Shadow**: deep box-shadow to lift the device off the background: `0 20px 60px rgba(0,0,0,0.4)`
- **Background behind frame**: dark neutral (#0d0d0d dark mode, #f0f0f0 light mode)

### Responsive Scaling

- On viewports narrower than ~450px, scale the phone frame down using `transform: scale()` to fit
- Calculate scale factor: `min(1, (viewportWidth - 40) / 390)`
- Also scale vertically if viewport height is limited: `min(1, (viewportHeight - headerHeight - 40) / 844)`
- Use `transform-origin: top center`

### Header Bar

- Same compact header pattern as web viewer:
  - Back button → `window.close()`
  - Screen title (truncated)
  - Description (hidden on mobile)
  - Prev/Next arrows
  - Fullscreen toggle

### Iframe Inside Frame

- `width: 390px; height: 844px` — matches the frame interior
- `border: none`
- Overflow handled by the iframe's own content

## Functional Requirements

- **URL-driven**: reads `?screen=...&title=...&desc=...` params
- **Prev/Next**: cycles through all_screens; updates URL via history.replaceState
- **Keyboard shortcuts**: Left/Right arrows, Escape, F for fullscreen
- **Fullscreen**: expands the phone frame container (not just the iframe)
- **Theme**: respects localStorage theme from index.html
- **Scaling recalculates on window resize**

## Anti-Patterns

- **NEVER** display web designs in this viewer — they will be crushed to 390px
- Do NOT remove the phone frame border/bezel — it provides essential context
- Do NOT use fixed positioning that breaks on mobile browsers
- Do NOT let the phone frame overflow the viewport without scaling

## Structural Pattern

```
<html>
  <head> title, theme setup, Tailwind CDN, font
  <body> flex flex-col h-screen bg-neutral
    <header> compact bar
      <button> back
      <span> title
      <span> description (desktop only)
      <div> prev / next / fullscreen buttons

    <main> flex-1 flex items-center justify-center
      <div> phone-wrap: 390x844, border, border-radius, shadow
        <iframe> src={screen} 390x844

    <script>
      - Parse URL params
      - Responsive scaling logic
      - Prev/next from embedded SCREENS_DATA
      - Keyboard shortcuts
      - Fullscreen toggle
      - Theme management
      - Window resize handler for scale recalculation
```

## Contract

- `id="phone-wrap"` — the phone frame container
- `id="viewer-frame"` — the iframe element
- `id="screen-title"` — title display
- `id="screen-desc"` — description display
- `id="btn-back"` — back/close button
- `id="btn-prev"` / `id="btn-next"` — navigation buttons
- `id="btn-fullscreen"` — fullscreen toggle
- Phone dimensions: exactly 390×844px (CSS), scaled via transform
- `SCREENS_DATA` — embedded JSON array of all screens
