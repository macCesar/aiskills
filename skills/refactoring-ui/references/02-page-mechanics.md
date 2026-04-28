# Page Mechanics: Hierarchy, Spacing, Typography

Inspired by principles from *Refactoring UI* by Adam Wathan & Steve Schoger. Paraphrased into the maintainer's own words; the original prose, illustrations, and examples are in the book — refactoringui.com.

---

## Hierarchy Is the Most Important Tool

- Every element on a page is either competing for attention or supporting something else
- Good design isn't making everything stand out — it's making the *right* things stand out
- If everything is emphasized, nothing is

## Use Weight and Color, Not Just Size

Three tools for hierarchy, in order from heaviest hammer to most subtle:

1. **Font size** — most obvious. Use sparingly for big differences.
2. **Font weight** — bold reads as important; great for same-size emphasis.
3. **Color contrast** — use a 3-tier system:
   - Primary: near-black for main content
   - Secondary: mid-grey for supporting text
   - Tertiary: lighter grey for placeholder/disabled/least important

**Avoid font weights below 400 in UI** — thin/light weights look bad at small sizes on screens.

## Tinted Greys for Colored Surfaces

- Don't reduce text opacity to fake grey on a colored background — desaturates and looks muddy
- Hand-pick a color with the same hue as the background, but adjusted lightness/saturation
- The result reads as "grey within that color family" rather than as actual grey

## Reduce the Competition Instead of Boosting the Star

- When you want one thing to pop, often the right move is to push down everything around it — not push the primary up further
- Reducing contrast on secondary elements preserves the visual balance and makes the primary read clearly
- Cheaper than adding more weight/size/color to the primary

## Labels: Skip, Combine, or Subordinate

**Skip the label when context already tells you:**
- An email address, a phone number, a date — format alone makes it obvious
- A profile bio doesn't need "Bio:"

**Fold label and value into a phrase:**
- "12 left in stock" beats "In stock: 12"
- "3 bedrooms" beats "Bedrooms: 3"

**Make the label secondary when you do need it:**
- Smaller and lighter than the value
- The value is the content; the label is metadata

## Semantics Are Not the Same as Visual Size

- `<h1>`–`<h6>` carry document semantics, not visual rules
- An `<h1>` may visually be smaller than surrounding body text in the right context
- An `<h3>` sidebar title might be the same size as body, just bolder
- Style by visual hierarchy, not by element level

## Icons Are Visually Heavier Than Text

- An icon at the same size as text reads as heavier
- Use a softer color for icons next to text — don't reach for the same near-black as body text
- Increase the text contrast and dim the icon, rather than the reverse

## Borders Get Thicker as Their Contrast Drops

- A barely-visible border becomes more readable when made slightly thicker
- A thicker low-contrast border often beats a thin high-contrast one
- Applies to dividers, table edges, card outlines

## Button Tiers

| Tier | Style | Use |
|---|---|---|
| Primary | Solid + high-contrast fill | The main action on the page |
| Secondary | Outline or low-contrast fill | Supporting actions |
| Tertiary | Link-style (no background or border) | Minor or repeating actions |
| Destructive | Secondary style + confirm step | Delete, remove, revoke |

- One primary action per page is the rule of thumb
- Don't make destructive the primary — render as secondary, then confirm the action

---

## Generous Spacing as the Default

- Default to *more* white space than feels right; trim it later if needed
- Most UIs suffer from too little spacing, not too much
- Dense feels noisy; generous feels organized

## A Spacing Scale, Not Arbitrary Pixels

- Define a non-linear spacing scale up front; pick from it
- Anchor near 16px (a common base unit)
- Adjacent values should differ by at least ~25% — otherwise they look almost identical
- Sample non-linear scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 640, 768

## Don't Stretch by Default

- A short form does not need full-width inputs
- If an element is naturally 200px wide, let it be 200px — don't reflow to 600px
- Full-width is a deliberate choice, not a fallback

## Design at the Real Size

- For small components (modals, cards, widgets), shrink the canvas
- Working at ~400px forces honest decisions about scale
- Zooming out on a 1440px canvas makes elements feel more generous than they actually are
- Mobile-first: design at 320–400px first, expand from there

## Columns Beat Stretched Rows

- When content gets too wide and elements feel diluted, introduce columns
- A two-column settings page reads better than a settings page where every form field stretches edge-to-edge

## Sidebars Use Fixed Widths

- Sidebars in pixels (e.g., 240px) — not percentages
- 20% sidebars become tiny on small screens and huge on large ones
- Use `max-width` on content columns, not percentage grid columns
- Percentages are for responsive *images* and grid cells, not UI chrome

## Big Things Shrink More Than Small Things

- A 45px headline on desktop should drop to roughly 20–24px on mobile, not just half
- Shrink larger elements proportionally more
- Button padding does *not* scale linearly with font:
  - 16px font + 12px vertical padding looks balanced
  - Bumping font to 24px doesn't mean padding becomes 18px — often padding stays close to original

## Group With Space, Not Boxes

- More space *around* a group than *within* it (Law of Proximity)
- A form section header should have more room above it than below it
- Labels should be closer to their own input than to the input above or below

## Spacing Sanity Checklist

- [ ] Does the spacing show what belongs together?
- [ ] Is there more space between groups than within groups?
- [ ] Is the label closer to its own input than to the next input?
- [ ] Does the layout communicate grouping without borders or backgrounds?

---

## Hand-Pick Your Type Scale (Don't Use Modular Ratios)

- Modular scales (e.g., 1.25× ratio) produce fractional pixels and useless intermediate sizes
- Hand-pick ~8–10 sizes that actually serve real use cases
- Sample scale: 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72px
- Each size should feel clearly different from its neighbors

## Use px or rem — Avoid em for Type

- `em` is relative to the parent's font size; nesting compounds unpredictably
- `px` or `rem` (relative to root) keep type sizes predictable
- `em` is fine for things like padding/margin that should scale with font, but not for the type scale itself

## Shopping for a Body Font

- On Google Fonts, filter by "10+ styles" — drops the bottom ~85% in one move
- Multiple weights/styles signal a font designed seriously
- For UI, prefer neutral sans-serif (Helvetica-style) over geometric or humanist extremes
- A system stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`) is a safe fallback
- Avoid condensed fonts and fonts with very short x-heights for body text

## Comfortable Line Length

- Target: ~45–75 characters per line
- Equivalent: ~20–35em of width
- Constrain paragraph width even inside a wider container
- Too wide → eyes lose track of the next line; too narrow → too many breaks

## Align Mixed Sizes by Baseline

- When two elements with different font sizes sit side by side, align by baseline (bottom of text)
- Vertical centering of mixed sizes makes the smaller text look too high

## Line-Height Inversely Tracks Size

- Body text in narrow columns: ~1.5
- Wider columns: closer to 2.0
- Large headlines: ~1.0 or slightly tighter
- Smaller text needs more space between lines; larger text needs less

## Link Styling Depends on Density

- In link-heavy contexts (sidebar navs, lists), drop the colored underline — use heavier weight or darker shade instead
- Color on every link reads as noise when most things are links
- Footer-style "ancillary" links: color/underline only on hover
- Save the high-contrast blue for inline body links that need to stand out

## Text Alignment by Use

- **Left:** the default for most text in LTR languages
- **Center:** only short blocks (≤2–3 lines) — never a paragraph
- **Right:** numbers in tables (so digits and decimals line up)
- **Justified:** only with hyphenation enabled — without it, big awkward gaps

## Letter-Spacing

- **Body fonts at headline sizes:** tighten letter-spacing slightly (negative tracking) — body fonts are tuned for small sizes, look loose at large sizes
- **All-caps text:** always loosen letter-spacing — caps are harder to read, extra space helps
- Never tighten body text or all-caps — kills legibility
