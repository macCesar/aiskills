# Ch2 — Hierarchy is Everything

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## Visual Hierarchy is the #1 Design Tool

- Every element on a page is either competing for attention or supporting something else
- Good design is not about making everything stand out — it's about making the right things stand out
- If everything is emphasized, nothing is

## Use Weight and Color, Not Just Size

Three tools for hierarchy (in order of subtlety):
1. **Font size** — most obvious, use sparingly for big differences
2. **Font weight** — bold text reads as important; good for same-size emphasis
3. **Color** — use dark/grey/lighter-grey to create a 3-tier system:
   - Primary: near-black for main content
   - Secondary: mid-grey for supporting text
   - Tertiary: lighter grey for placeholder/disabled/least important

**Never use font weights below 400** for UI text — thin/light weights look bad at small sizes on screens.

## Grey Text on Colored Backgrounds

- Don't reduce text opacity to create grey on a colored background — this desaturates and looks muddy
- Instead: hand-pick a color with the same hue as the background, but adjusted lightness/saturation
- Pick a color that feels like a "grey" version within that color family, not an actual grey

## Emphasize by De-Emphasizing Competitors

- When you want one element to stand out, try making everything around it less prominent instead of making it bigger/bolder
- Reduce contrast on secondary elements rather than adding more styling to primary ones
- This is often more effective than adding emphasis — it preserves the visual balance

## Labels: When to Skip, Combine, or Subordinate

**Skip the label when:**
- Format makes it obvious (e.g., an email address, a phone number, a date)
- Context makes it obvious (e.g., a profile page bio doesn't need "Bio:" label)

**Combine label and value:**
- "12 left in stock" instead of "In stock: 12"
- "Bedrooms: 3" → "3 bedrooms"

**Treat label as secondary:**
- When you do need a label, make it smaller/lighter than the value
- The value is what matters; the label is supporting metadata

## HTML Heading Elements ≠ Visual Size

- `<h1>`–`<h6>` are semantic, not visual
- An `<h1>` might visually be smaller than surrounding text if the context calls for it
- An `<h3>` sidebar title might be the same size as body text, just bolder
- Style headings based on visual hierarchy, not element level

## Icons Are Heavy — Reduce Their Contrast

- Icons carry more visual weight than text at the same size
- To balance icons with surrounding text, use a softer/lighter color for the icon
- Don't use the same high-contrast color you use for body text — icons will dominate
- Reduce icon contrast; increase text contrast if needed

## Increase Border Width for Low-Contrast Elements

- When a border is barely visible (low contrast), making it thicker compensates
- A thicker, slightly lighter border can read better than a thin, barely-there one
- This is especially relevant for dividers, table borders, and card edges

## Button Hierarchy

Four tiers of buttons:

| Tier | Style | Use |
|------|-------|-----|
| Primary | Solid + high-contrast fill | The main action on the page |
| Secondary | Outline or low-contrast fill | Supporting actions |
| Tertiary | Link-style (no background/border) | Least important actions |
| Destructive | Secondary style + confirmation step | Delete, remove, revoke |

- A page should rarely have more than one primary button
- Destructive actions should NOT use red as primary — make them secondary, then confirm
- Hierarchy between buttons prevents visual noise and guides users to the right action
