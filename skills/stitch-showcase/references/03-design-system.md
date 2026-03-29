# Section: Design System (Manual de Identidad)

## Purpose

A rich, visual Manual de Identidad that showcases the project's design language — not just tokens, but **relationships between tokens**, typographic hierarchy in action, and surface layering. This is the most impactful section of the showcase.

## Data Required (from showcase_context.json)

- `color_tokens` — semantic color tokens with hex values (primary, secondary, surface, on-primary, etc.)
- `colors` — named color pairs from DESIGN.md
- `font_family` — primary typeface name
- `default_theme` — informs which surface colors to demonstrate first
- `design_system_screen` — if present, link to the dedicated design system screen in viewer
- `design_md_raw` — raw DESIGN.md text; may contain design philosophy, component descriptions, usage rules that the AI should interpret and visualize

## Design Requirements

### Color Palette (NOT just flat swatches)

- **Large color blocks** arranged horizontally, showing name + hex + semantic role
- **Relationship demonstrations**: show primary color ON surface, show on-primary text ON primary background, show secondary as accent alongside primary
- **Tonal layering**: if surface tokens exist (surface, surface-variant, background), show stacked/overlapping cards at different elevations to demonstrate the tonal hierarchy
- **Contrast pairs**: explicitly show which text colors work on which backgrounds (e.g., "on-primary" text on "primary" background)
- Minimum block height: 80px per color. No tiny circles or dots.

### Typography Specimen

- Show the font at **multiple sizes**: Display (48px), Heading (32px), Subheading (24px), Body (16px), Caption (12px)
- Show at **multiple weights** if available: Regular (400), Medium (500), Semibold (600), Bold (700)
- Use **real text from the project** (project name, section names) — not "The quick brown fox"
- Show a **type scale** visualization: a vertical stack where each level is progressively smaller
- Include the font name, source (Google Fonts), and fallback stack

### Surface Hierarchy (if color_tokens has surface data)

- Visualize 2-3 elevation layers: background → surface → surface-variant
- Use nested cards or overlapping panels to show depth
- If the project uses glassmorphism or ghost borders (check design_md_raw), demonstrate them

### Design System Screen Link

- If `design_system_screen` exists, show a prominent card linking to the full design system viewer
- Include the thumbnail (png_file) as a visual preview

### Component Showcase (if design_md_raw describes components)

- Parse design_md_raw for component mentions (buttons, cards, inputs, etc.)
- If found, render sample components using the project's color tokens and typography
- These are illustrative — they don't need to be interactive

## Functional Requirements

- Static section — no interactivity beyond hover states
- Color blocks should show hex on hover or always-visible
- If glassmorphism tokens exist, demonstrate with `backdrop-filter: blur()` and semi-transparent backgrounds
- Responsive: color blocks wrap to 2-column on mobile, type specimen stacks naturally

## Anti-Patterns

- **NEVER** render only flat square swatches as the entire "design system" — this is the #1 failure mode
- **NEVER** show just a font name with "Aa" — that's a placeholder, not a specimen
- **NEVER** use gray backgrounds when the project has specific surface tokens
- **NEVER** ignore the design_md_raw content — it contains the designer's intent and philosophy
- **NEVER** list colors without showing how they relate to each other
- Do NOT use a generic grid of circles for colors (this is the "boring AI" pattern)

## Structural Pattern

```
<section> design-system: max-w-7xl mx-auto px-6 py-12
  <h2> "Design System" or "Manual de Identidad"

  <div> color-palette
    <div> large horizontal blocks with name + hex + role
    <div> relationship demos: text-on-background pairs

  <div> typography-specimen
    <div> type scale: Display → Heading → Body → Caption
    <div> weight showcase: Regular / Medium / Semibold / Bold
    <p> font metadata: name, source, fallback

  <div> surface-hierarchy (conditional)
    <div> nested cards showing tonal layering

  <div> ds-screen-link (conditional)
    <a> card linking to viewer.html?screen=design_system

  <div> components (conditional, from design_md_raw parsing)
    rendered sample components
```

## Contract

- Section must have `id="design-system"`
- Color blocks: each with `data-token="token-name"` attribute
- If design_system_screen exists, link format: `viewer.html?screen={html_file}&title={title}&desc={description}`

## Skills to Invoke

When generating this section, the AI MUST invoke:
- `refactoring-ui` — for visual hierarchy, depth, and spacing decisions
- `ui-ux-pro-max` — for color palette presentation and typography best practices
