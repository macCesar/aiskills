# Ch4 — Designing Text

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## Hand-Crafted Type Scale (Avoid Modular Scales)

- Modular scales (e.g., 1.25× ratio) produce fractional pixel values and limited useful sizes
- Better approach: hand-pick 8-10 sizes that actually work for your use cases
- Example scale: 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72px
- Each value should feel clearly different from adjacent ones — not nearly identical

## Use px or rem — Never em

- `em` units are relative to the parent element's font size
- Nesting elements with `em` compounds the sizing unpredictably
- Use `px` or `rem` (relative to root font size only) for type scale
- `em` is appropriate for things like `margin`/`padding` that should scale with font size, but NOT for defining the type scale itself

## Choosing Fonts from Google Fonts

- Filter by: "10+ styles" — this alone cuts ~85% of sans-serif fonts, leaving fewer than 50
- Quality signal: fonts with many weights/styles are taken seriously by their designers
- For UI: choose a neutral sans-serif (Helvetica-style, not geometric or humanist extremes)
- System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`) is a safe fallback
- Avoid condensed fonts (narrow letterforms) or fonts with very short x-heights for body text — hard to read at small sizes

## Optimal Line Length

- Target: **45–75 characters** per line for comfortable reading
- Equivalent width: approximately **20–35em**
- Limit paragraph width even when placed inside a wider content area
- Too wide: eyes get lost tracking back to the next line
- Too narrow: too many line breaks, disrupts reading flow

## Baseline Alignment for Mixed Font Sizes

- When two elements with different font sizes sit side by side, align them by **baseline** (bottom of text), not by vertical center
- Vertical center alignment of mixed sizes looks off — the smaller text appears too high

## Line-Height Rules

- **Body text (narrow columns):** ~1.5 line-height
- **Wide columns:** up to 2.0 line-height
- **Large headlines:** ~1.0 or slightly below (they need almost no leading)
- Rule: line-height is **inversely proportional** to font size
  - Small text → more line-height (harder to track between lines)
  - Large text → less line-height (already easy to track; extra space feels empty)

## Styling Links

- In **link-heavy UIs** (e.g., sidebars, navigation): use heavier weight or darker color instead of blue color
- Color alone creates too much noise when everything is a link
- **Ancillary links** (e.g., "privacy policy" in footers): only show underline/color on hover
- Reserve high-contrast blue links for inline text where they need to stand out from surrounding prose

## Text Alignment

- **Left-align** for most text — the natural reading direction for LTR languages
- **Center-align** only for short text blocks (max 2–3 lines); never center long paragraphs
- **Right-align** numbers in tables (so decimal points and digits align vertically)
- **Justified text:** hyphenate it — without hyphenation, justified text creates awkward gaps

## Letter-Spacing Adjustments

- **Headlines using wide-spaced body fonts:** tighten letter-spacing slightly (negative tracking)
  - Body fonts are optimized for reading at small sizes; at large sizes they can feel too loose
- **All-caps text:** always increase letter-spacing — all-caps is harder to read, extra spacing compensates
- Never apply tight letter-spacing to body text or all-caps — it reduces legibility
