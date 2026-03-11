# Ch3 — Layout and Spacing

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## Start with Too Much White Space

- Default to more white space, then remove it — don't add white space after the fact
- Most UIs suffer from too little spacing, not too much
- Dense UIs feel busy and hard to scan; generous spacing feels calm and organized

## Spacing Scale

- Use a defined, non-linear spacing scale — not arbitrary pixel values
- Base value: **16px** is a natural anchor point
- Adjacent values on the scale should differ by at least 25%
- Example scale (non-linear): 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 640, 768
- The non-linearity matters: you want clearly distinct values, not ones that look nearly the same

## Use Only the Space You Need

- Don't stretch elements to fill the full container by default
- Short forms don't need full-width inputs
- If an element's natural width is 200px, let it be 200px — don't stretch to 600px
- Full-width is a choice, not a default

## Shrink Your Canvas for Small Interfaces

- When designing small components (modals, cards, widgets), shrink the canvas
- Working at ~400px forces you to think about the actual scale
- Zooming out on a 1440px canvas to see a card is deceptive — elements feel more generous than they are
- Mobile-first approach: design at 320-400px first, then expand

## Split into Columns Instead of Stretching

- When content is too wide or elements feel stretched, introduce columns
- A two-column layout for a settings page beats stretching form fields across the full width
- Use columns to create denser, more structured layouts without sacrificing usability

## Fixed Widths for Sidebars

- Sidebars should use fixed pixel widths, not percentages
- A sidebar at `240px` stays consistent; at `20%` it becomes tiny or huge at different breakpoints
- Use `max-width` constraints for content columns rather than percentage-based grid columns
- Percentage widths work for responsive images and grid cells — not for UI chrome

## Responsive Scaling: Large Elements Shrink Faster

- Large headline that is 45px on desktop → should be 20-24px on mobile
- The ratio of reduction is not 1:1 — large elements shrink proportionally more
- Button padding does not scale proportionally with font size:
  - A button with 16px font and 12px vertical padding looks right
  - Increasing font to 24px doesn't mean padding should become 18px
  - Often keep padding roughly the same while increasing font

## Spacing Within Groups vs. Between Groups

- More space should appear **around** a group than **within** it (Law of Proximity)
- Elements close together are perceived as related
- A form section header should have more space above it (separating from previous section) than below it (connecting to its fields)
- Labels should be closer to their own input than to the input above or below

## Law of Proximity Checklist

- [ ] Does the spacing clearly show which elements belong together?
- [ ] Is there more space between groups than within groups?
- [ ] Is the label closer to its own input than to adjacent inputs?
- [ ] Does the layout communicate grouping without relying on borders or backgrounds?
