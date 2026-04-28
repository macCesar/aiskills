# Polish: Finishing Touches and Sharpening Intuition

Inspired by principles from *Refactoring UI* by Adam Wathan & Steve Schoger. Paraphrased into the maintainer's own words; the original prose, illustrations, and examples are in the book — refactoringui.com.

---

## Replace Default Bullets with Meaningful Icons

- Default disc bullets feel generic and low-effort
- Swap for icons that match the content:
  - Checkmarks for feature lists or completed items
  - Arrows for sequential or directional lists
  - Content-specific icons (lock for "secure", globe for "worldwide")
- Adds visual interest *and* reinforces meaning at the same time

## Big Quotation Marks as Decorative Elements

- For testimonials and pull quotes, quotation marks can become design elements rather than punctuation
- Make them large, colorful (accent color), positioned prominently
- The quote mark is now part of the visual design

## Style Links With Intention

Two paths depending on context:

1. **Color + weight:** brand-colored link with a slightly heavier weight than surrounding text
2. **Thick colorful underline:** a 2–4px border-bottom in an accent color that overlaps the lower portion of the text — clearly a link, visually distinctive

## Custom Checkbox and Radio Styling

- Browser default inputs look generic and break brand identity
- Build custom-styled checkboxes/radios using your brand color for the checked state
- Common pattern: custom checkbox = colored fill + checkmark SVG
- Worth the extra markup — defaults feel like 1996 every time

## Color Accents on Edges

A short, thick accent-color stripe is a high-impact, low-effort touch. Common placements:

- **Top of a card** — a colored bar at the top edge
- **Left side of an active nav item** — communicates "you are here"
- **Left side of an alert message** — color-codes the alert type (red=danger, yellow=warning, green=success)
- **Under a headline** — a short thick underline in brand color
- **Top of the entire page** — a thin strip of color across the very top

These add brand identity without adding complexity.

## Going Beyond a Plain Background

Options when "white" feels boring:

1. **Solid color shift:** switch from white to a brand-tinted neutral
2. **Gradient:** between two hues no more than 30° apart on the color wheel — close = natural, far = jarring
3. **Low-contrast repeating pattern:** subtle dots, lines, or hatching at low opacity
4. **Geometric shapes / blobs:** abstract colored shapes at low opacity behind content

Gradient rule of thumb: keep the two hues within ~30° of each other for a natural blend.

## Empty States Deserve Real Design

- Empty UIs look broken or confusing — and they're often the *first* thing new users see
- Design the empty state as deliberately as the populated one

A good empty state has:

- A contextually relevant illustration or icon
- A short, friendly explanation of what belongs here
- A clear next-step CTA (e.g., "Add your first project")

Companion rule: **hide UI that has nothing to operate on**

- Tabs with no content, filters with no items, pagination with one page — all read as broken
- Don't render those elements until there's content to make them useful

## Alternatives to Borders

Borders are overused. Try:

1. **Box shadow:** `box-shadow: 0 1px 3px rgba(0,0,0,0.1)` — separates without a hard line
2. **Two background colors:** alternating backgrounds communicate sections without lines
3. **More space:** sometimes the right answer is just more white space

## Beyond the Generic Pattern

Don't reach for the standard widget when something more engaging fits:

- **Enriched dropdowns:** add icons, sections, descriptions, two-column layouts inside dropdowns
- **Hierarchy inside table cells:** instead of equal-weight columns, give each cell its own primary/secondary tier (large dark for the main value, small grey for secondary)
- **Selectable cards instead of radios:** for option groups, replace radio buttons with styled card options that highlight on selection — easier to scan, more inviting

## Sharpening Design Intuition Over Time

Two practices that compound:

1. **Study the unintuitive choices in good UIs.** Find polished products you admire and ask *"why did they do that?"* — focus on choices you wouldn't have made yourself. Those are the ones worth learning from.
2. **Rebuild interfaces without DevTools.** Pick a UI you admire and recreate it from scratch — no inspecting the original. Forces real decisions instead of copying values.
