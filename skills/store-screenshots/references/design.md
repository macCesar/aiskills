# Art direction and editorial selection

## Read the app before decorating it

Inventory actual screenshots and brand files. Extract the app's primary and surface colors, type families/weights, icon language, logo variants, density, tone, and main user benefit. Prefer official vector logos or original app-icon artwork. Do not substitute a generic glyph or redraw the logo. If the logo is a font glyph, resolve its actual character map and export its outline; retain the font's license.

Separate observed brand facts from proposed campaign choices. A logo's primary color need not fill every background: test separation from the app's bottom bar, dark panels, and edge-to-edge photos. A subtle border, quieter surface, or different brand tint may keep the screenshot readable.

Offer directions that change hierarchy and mood, not just hue. Examples to adapt, not category rules:

| App character | Possible direction | What the screenshot must prove |
| --- | --- | --- |
| News, radio, community | Editorial typography, restrained brand surfaces, strong headline | Current content and useful local services |
| Children, creative learning | Playful geometry, warm accents, expressive type used sparingly | Actual activity and age-appropriate interactions |
| Productivity, business | Calm surfaces, precise spacing, benefit-led copy | A task completed with little friction |
| Wellness, lifestyle | Spacious composition, gentle palette, authentic imagery | The actual tracking, guidance, or routine |
| Games, media | Gameplay/content dominant, energetic framing | Real gameplay or catalog; artwork does not replace it |

Landscape apps stay landscape where their destination supports it. Apps with mixed orientation need explicit per-screen/destination decisions. Do not rotate a portrait capture and call it a landscape UI.

## Select a story

Honor mandatory screens and their order. Lead with the most distinctive, understandable benefit, then cover major use cases. Settings/about/privacy rarely deserve a standalone sales slide unless requested or central to the product. Do not fill every available slot merely because it exists.

When there are too many sections, combine related screens under one benefit. Use `07.1` and `07.2` for two source captures on final slide `07`; the number of source files is not the number of uploads. Avoid shrinking several unrelated screens into an unreadable collage. Keep platform correspondence when features exist on both, but do not invent parity.

Write one concrete headline per slide in the user's locale, usually one or two short lines, with optional supporting copy. Verify every claim against the current build. Avoid outdated features, unsupported superlatives, ratings, prices, and calls to action prohibited by the destination. Check line breaks using the actual font metrics; do not truncate copy with ellipses.

## Build a visual system without a rigid template

Choose a small type palette from existing brand fonts or properly licensed alternatives with locale coverage. Confirm accented letters and punctuation. Keep font files, weights, internal family names, and license provenance together. Never assume a fallback looks close enough.

Define canvas-relative margins, type sizes, background, logo position, and screenshot treatment. Use these consistently while allowing a hero slide, a single-screen slide, and a paired-screen slide. A frame is optional; if used, match the platform and do not obscure content. Avoid decorative mockups that make the real interface too small.

For a screenshot of size `sw × sh` inside a box `bw × bh`, use `s = min(bw/sw, bh/sh)` and place it at `sw*s × sh*s`. SVG `preserveAspectRatio="xMidYMid meet"` provides containment. Do not stretch or crop meaningful UI to make a ratio fit. Full screenshots are the default; a deliberate detail crop needs context and accurate representation.

Evaluate the sample as both a full-size image and a storefront thumbnail: headline hierarchy, app legibility, recognizable branding, and separation of screenshot edges from the background. For a new series, exercise the difficult layout too (paired screens, long translation, or tablet). Carry corrections into shared tokens/generator parameters rather than individually patching every PNG.
