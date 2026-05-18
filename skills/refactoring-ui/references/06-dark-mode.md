# Dark Mode

> **Scope note**: *Refactoring UI* was written before dark mode was an industry default and does not address it explicitly. **However**, the book's HSL chapter (in `03-visual-treatment.md`) — handpicking shades by hue/saturation/lightness, not deriving them via `lighten()`/`darken()` — is exactly the foundation dark mode needs. This file extends those principles to a second color mode.

---

## Don't Invert — Rebuild

Inverting a light theme produces a "negative" image: muddy colors, weird text contrast, accents that lose punch. Dark mode is its own design pass.

The bookkeeping change: every color token now has a **mode pair**. Plan for it from the start, even if you only ship light first.

```css
:root {
  --bg-canvas: hsl(220 14% 96%);
  --bg-surface: hsl(0 0% 100%);
  --text-primary: hsl(220 13% 18%);
  --text-secondary: hsl(220 9% 46%);
  --border: hsl(220 13% 91%);
  --brand-500: hsl(217 91% 60%);
}

:root[data-theme='dark'] {
  --bg-canvas: hsl(220 13% 10%);
  --bg-surface: hsl(220 13% 14%);
  --text-primary: hsl(220 14% 96%);
  --text-secondary: hsl(220 9% 65%);
  --border: hsl(220 13% 22%);
  --brand-500: hsl(217 91% 65%);   /* nudged lighter for dark bg */
}
```

## Dark Backgrounds Aren't Black

Pure `#000` reads as a hole in the screen. Pull the lightness up to ~8–12%, keep a small amount of saturation, and lean slightly warm or cool depending on your brand.

| Backdrop | Lightness | Notes |
|---|---|---|
| App canvas (outermost) | 8–12% | Lowest layer — slightly tinted, not pure black |
| Surface (cards, panels) | 12–16% | One step above canvas — implies "raised" without a shadow |
| Elevated surface (modals, popovers) | 16–22% | Highest layer — even lighter |

The trick: in dark mode, **lighter = closer to the viewer**, the opposite of light mode. A higher elevation doesn't get a darker shadow — it gets a lighter surface.

## Text Contrast in Dark Mode

Pure white text on a near-black background is *too much* contrast — the text vibrates and reading becomes tiring at length.

- Primary text: ~96% lightness (slightly off-white) — e.g., `hsl(220 14% 96%)`
- Secondary text: ~65% lightness — significantly muted compared to light mode's secondary
- Tertiary / placeholder: ~45–50%

WCAG ratios still apply (4.5:1 small text, 3:1 large), and slightly off-white still passes against a near-black canvas with room to spare.

## Accent Colors Usually Need a Lightness Bump

A brand color tuned for white backgrounds often looks too dark and dim against a dark canvas. Most palettes need the accent **lightness raised 5–10%** for the dark variant.

Test against both backgrounds. If the brand color fails contrast in dark mode, derive a lighter variant rather than swapping for an unrelated color — keeps brand identity coherent.

## Shadows: Mostly Gone, Sometimes Inverted

Shadows are made of light obstruction. On a dark canvas, the absence of light is the canvas itself — a dark shadow on dark background is invisible.

Options:

1. **Skip shadows entirely**: use lighter surfaces and tinted borders to communicate elevation
2. **Top highlight**: an inset top border (lighter color) to show that the element catches the imagined light source, with no shadow below
3. **Very soft dark shadow**: works only when the element is on a lighter surface (e.g., a dropdown over the canvas) — large blur, low opacity

A `box-shadow: 0 2px 4px rgba(0,0,0,0.3)` that was crisp in light mode is invisible on a `hsl(220 13% 10%)` canvas. Recheck every shadow when adding dark mode.

## Images and Photos in Dark Mode

Photos with bright backgrounds (typically light themes) "blow out" against a dark canvas — they pop too hard. Two tactics:

- **Lower image brightness slightly** in dark mode (e.g., `filter: brightness(0.9)`) — only for decorative/hero images, never for content the user is reading
- **Frame with a subtle border** — separates the bright rectangle from the dark canvas without dimming the photo

Same principle for video posters and avatar images.

## SVG Icons and Logos

Single-color icons should be currentColor-driven so they pick up the mode's text color:

```html
<svg fill="currentColor" ...>
```

Multi-color logos need a dark variant. Don't fake it with `filter: invert()` — colors land in the wrong hue and brand recognition suffers.

## Theme Toggle: Three Defaults

1. **Match system preference** (`prefers-color-scheme`) — best first-paint experience
2. **Respect explicit user override** — store in `localStorage`; persists across sessions
3. **Apply before first paint** — set the theme class on `<html>` from a tiny inline script in `<head>` BEFORE any rendering, to avoid a flash of the wrong theme

```html
<script>
  (function () {
    var stored = localStorage.getItem('theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = stored || (prefersDark ? 'dark' : 'light');
    document.documentElement.dataset.theme = theme;
  })();
</script>
```

## Anti-Patterns

- ❌ Pure black (`#000`) for the canvas — feels like a void, hurts at length
- ❌ Pure white text — vibrates against dark bg, tiring to read
- ❌ `filter: invert(1)` to "do" dark mode — produces wrong hues, breaks images
- ❌ Same brand color in both modes without checking contrast — fails WCAG silently
- ❌ Keeping every shadow from light mode unchanged — invisible against dark bg
- ❌ Theme toggle applied AFTER first paint — flash of opposite theme on every load
- ❌ Inverting photos and screenshots — colors shift unnaturally, recognition suffers
