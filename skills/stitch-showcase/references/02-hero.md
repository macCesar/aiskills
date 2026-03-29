# Section: Hero

## Purpose

First impression section that introduces the project with visual impact. Establishes the design's identity and communicates scope at a glance.

## Data Required (from showcase_context.json)

- `project_name` — headline
- `type` — "Mobile App" or "Web App"
- `screen_count` — stat
- `sections` — count and names for description
- `font_family` — use for typographic emphasis
- `color_tokens` or `colors` — accent color for subtle decorative elements

## Design Requirements

- **Typographic hierarchy**: large project name (text-4xl to text-6xl depending on length), smaller subtitle describing scope
- **Visual rhythm**: generous vertical padding (py-16 to py-24), breathing room
- **Subtle accent**: use the project's primary/accent color for a decorative element (gradient line, dot, underline) — NOT as background
- **Stats row**: screen count, section count, type — displayed as a minimal horizontal row with dividers
- **Personality**: the hero should reflect the project's character. A fitness app feels different from a banking app. Use the project name and section names to infer tone.
- Background: inherits page background (no separate hero background color)

## Functional Requirements

- Static section — no interactive elements beyond scroll
- Smooth entrance: consider CSS-only fade-in with `@keyframes` (no JS animation library)
- Responsive: stack stats vertically on small screens

## Anti-Patterns

- Do NOT use generic stock-photo-style hero imagery
- Do NOT use full-width colored backgrounds or gradients as hero background
- Do NOT center everything — left-aligned text with asymmetric layout creates sophistication
- Do NOT use "Welcome to..." or "Introducing..." copywriting patterns

## Structural Pattern

```
<section> hero: max-w-7xl mx-auto px-6 py-20
  <div> text content
    <h1> project name — large, bold, tracking-tight
    <p> auto-generated description from sections data
  <div> stats row
    <span> N screens
    <span> divider
    <span> N sections
    <span> divider
    <span> Mobile App / Web App
```

## Contract

- No required IDs (hero is static)
- Should be the first `<section>` after `<header>`
