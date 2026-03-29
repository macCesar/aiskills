# Section: Quality Standards & Anti-Patterns

## Purpose

Guardrails that prevent the AI from generating generic, flat, "obviously AI-made" showcase HTML. This document defines the visual quality bar and common failure modes to avoid.

## Required Skills

Before generating ANY showcase HTML, the AI MUST invoke these skills:
- **`frontend-design`** — for creative, distinctive HTML generation that avoids generic AI patterns
- **`refactoring-ui`** — for visual hierarchy, depth, spacing, and typography decisions
- **`ui-ux-pro-max`** — for color system best practices, component patterns, and interaction design

These skills contain specific techniques for achieving professional-grade output.

## Visual Quality Bar

The generated showcase should feel like it was designed by a product designer at **Linear, Raycast, Stripe, or Vercel** — not by a template engine. Specific qualities:

### Depth & Layering
- Use subtle shadows at multiple levels (not just `shadow-lg` on everything)
- Cards should feel lifted off the surface with layered borders + shadows
- Background should have subtle texture or gradient (not flat solid color)
- Ghost borders (`border: 1px solid rgba(255,255,255,0.06)`) add refinement in dark mode

### Typography
- Use the project's font family with a clear **type scale** (not everything the same size)
- Tracking adjustments: `-0.02em` on headings, normal on body
- Font weight hierarchy: Bold (700) for headings, Semibold (600) for labels, Regular (400) for body
- Line height: tight (1.2) on headings, relaxed (1.6) on body text

### Color Usage
- Accent color used sparingly: tab highlights, hover borders, interactive elements
- **NEVER** as large surface backgrounds
- Neutral surfaces with slight warmth or coolness (not pure gray)
- Sufficient contrast ratios (WCAG AA minimum: 4.5:1 for text)

### Spacing & Rhythm
- Consistent spacing scale: 4px base (4, 8, 12, 16, 24, 32, 48, 64)
- Generous whitespace between sections (48-96px)
- Tighter spacing within components (8-16px)
- Asymmetric padding creates visual interest (more top than bottom, more left than right for headers)

### Micro-interactions
- Hover states on ALL interactive elements (cards, buttons, tabs)
- Scale transforms on card hover: `scale(1.02)` — subtle, not bouncy
- Color transitions: `transition-colors duration-200`
- Focus-visible rings for keyboard navigation accessibility

### Responsive Behavior
- Mobile-first: single column, then expand to grid
- No horizontal scroll on any viewport
- Touch-friendly tap targets (minimum 44×44px)
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)

## Banned Patterns (The "Generic AI" Checklist)

If you see yourself doing ANY of these, STOP and redesign:

| Banned Pattern | Why It's Bad | What To Do Instead |
|---|---|---|
| Flat gray (#f3f4f6) background everywhere | Lifeless, no personality | Use near-white/near-black with subtle warmth |
| All cards exactly the same size and spacing | Monotonous grid | Vary card sizes for DS section vs gallery cards |
| Color swatches as small circles | Minimizes the design system | Large blocks showing relationships |
| "Aa" as the only type specimen | Tells nothing about the typeface | Full type scale with real project text |
| Generic sans-serif (system-ui) when font exists | Ignores project identity | Always load and apply the project's font |
| Bright colored header/hero backgrounds | Clashes with thumbnails | Neutral backgrounds, accent as detail only |
| No hover states | Feels static, dead | Every clickable element needs hover feedback |
| Same border-radius everywhere | Boring uniformity | Vary: 8px for cards, 12px for modals, full for pills |
| Centered everything | Template feel | Left-align text, asymmetric layouts |
| "Welcome to..." copy | AI copywriting smell | Jump straight to project stats and content |
| Rainbow gradients | Unprofessional | Monochrome or two-tone gradients from project palette |
| Icon soup (decorative icons everywhere) | Visual noise | Icons only for functional purposes (toggle, nav) |

## Technical Standards

### Self-Contained HTML
- Single HTML file with all CSS inline (in `<style>` or Tailwind classes)
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Google Fonts via CDN link
- No external JS libraries beyond Tailwind
- No build step required — just open in browser

### Performance
- Images use `loading="lazy"`
- Minimal DOM nesting (avoid wrapper div soup)
- CSS transitions, not JS animations
- No layout shift on theme toggle

### Accessibility
- Semantic HTML: `<header>`, `<main>`, `<section>`, `<nav>`
- All images have `alt` text
- Focus-visible styles on interactive elements
- Keyboard navigable: Tab through cards, Enter to open
- `role="button"` on non-button clickable elements

### URL Contract
- Index links to viewer via: `viewer.html?screen={path}&title={title}&desc={desc}`
- Viewer reads URL params and renders accordingly
- Prev/next updates URL without reload (history.replaceState)

## Inspiration References

Study these products for visual quality benchmarks:
- **Linear** — dark mode, subtle gradients, layered cards, excellent typography
- **Raycast** — clean hierarchy, bold headings, muted descriptions, pill badges
- **Stripe Docs** — structured sections, code blocks, clear information hierarchy
- **Vercel Dashboard** — minimal, high contrast, excellent use of whitespace
- **Apple Human Interface Guidelines** — phone frame styling, device showcasing

## Verification Checklist

Before declaring the showcase complete, verify:

- [ ] Project font is loaded and applied (not falling back to system-ui)
- [ ] Accent color from project is used (hover, active tab, not generic indigo)
- [ ] Dark/light mode works and persists across pages
- [ ] Design system section shows color RELATIONSHIPS, not just swatches
- [ ] Typography specimen shows multiple sizes and weights
- [ ] Gallery cards have correct aspect ratios (portrait for mobile, landscape for web)
- [ ] Web screens open in full-width viewer, mobile screens in phone frame
- [ ] Search filters cards
- [ ] Section tabs filter correctly
- [ ] Prev/next works in viewer with keyboard shortcuts
- [ ] No horizontal scroll on mobile viewport
- [ ] All hover states are present and smooth
