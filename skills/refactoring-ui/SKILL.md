---
name: refactoring-ui
description: 'Use when redesigning or visually refactoring an interface, including an entire app, dashboard, or admin panel, or when a UI feels cramped, generic, or needs polish. Applies across web and mobile stacks to layout, hierarchy, typography, spacing, color, shadows, images, empty states, borders, dark mode, motion, hover states, forms, tables, and modals. Also applies when implementing UI with Tailwind CSS or diagnosing a missing Tailwind class. Excludes copywriting, brand identity, user research, and unrelated isolated CSS rendering bugs.'
---

# Refactoring UI Skill

Design advice grounded in the principles taught by Adam Wathan & Steve Schoger in their book *Refactoring UI*. **The book itself contains the original prose, illustrations, side-by-side examples, and case studies — buy it at https://refactoringui.com for the full material.** This skill provides reformulated guidance for use as an AI assistant reference.

## Required workflow (read before responding)

The SKILL.md alone is an **index** of references. The detail you need to give accurate answers lives in the reference files. **Reading this SKILL.md is not enough.**

### Step 1 — Open the relevant reference files

| Task involves | Required reading |
|---|---|
| Project mindset: feature-first work, scope discipline, defining systems, picking a voice | [references/01-foundations.md](references/01-foundations.md) |
| Visual hierarchy, layout, white space, spacing scales, typography | [references/02-page-mechanics.md](references/02-page-mechanics.md) |
| Color systems (HSL, shades, greys, contrast), depth and shadows, image handling | [references/03-visual-treatment.md](references/03-visual-treatment.md) |
| Empty states, borders, accents, decorative defaults, finishing touches, and studying design decisions | [references/04-polish.md](references/04-polish.md) |
| Motion, microinteractions, transitions, hover/press states, loading, `prefers-reduced-motion` — *complementary, not from the book* | [references/05-motion.md](references/05-motion.md) |
| Dark mode, multi-theme color tokens, theme toggle, contrast strategy — *complementary, extrapolates the book's HSL principles* | [references/06-dark-mode.md](references/06-dark-mode.md) |
| Modals (focus, layout), forms (labels, validation), tables (density, alignment) — *complementary, extends the book's principles* | [references/07-component-patterns.md](references/07-component-patterns.md) |
| Refactoring a whole app, panel, or interface area with several modules — *AISkills implementation workflow* | [references/08-integral-refactoring.md](references/08-integral-refactoring.md) |
| Implementing or refactoring UI in a project that uses Tailwind CSS, or diagnosing a missing Tailwind class | [references/09-tailwind-v4.md](references/09-tailwind-v4.md) |
| Implementing semantic HTML components with Tailwind, including panels, tables, filters, forms, selects, disclosures, dialogs, and Alpine.js in Blade | [references/10-native-components.md](references/10-native-components.md) |

When the request covers a whole interface, use the integral refactoring workflow before editing and at handoff. A set of example screens guides the design. The requested scope determines which screens to review.

When the project uses Tailwind or the request names it, confirm the installed version, build pipeline, and browser targets before applying version-specific advice. Use the implementation reference for v4 and follow its source-detection checklist for missing classes. For a whole Laravel panel on v4, combine the integral workflow, the applicable visual references, and both Tailwind references. Use semantic HTML and follow the project’s approach to interaction. When a Blade project uses Alpine.js or the request calls for it, follow the Alpine integration and examples in the component reference. For a visual review in a project without Tailwind, start with the relevant visual and component references.

### Step 2 — Output contract

Every design recommendation, ratio, value, or rule you cite carries its citation inline:

`[source: references/<file>.md]`

The citation is what separates a value you read from one that merely sounded right — written down, the two look identical, and the reader has no way to tell them apart. Cite while writing rather than collecting sources at the end, because by then you are reconstructing where something came from instead of recording it.

Example: *"Use weight and color, not just font size, to establish hierarchy [source: references/02-page-mechanics.md]"*

### Step 3 — If you must answer from memory

If you write a claim without having read the reference that backs it, prepend `FROM_MEMORY (unverified):` to that claim. Do not hide it.

### Banned behaviors

These four are where advice like this usually goes wrong, so they're worth naming:

- Inventing ratios, scale values, contrast numbers, or rules not in the references. A made-up number is indistinguishable from a real one once it's in someone's stylesheet.
- Reproducing the book's prose, illustrations, or examples verbatim. The references paraphrase on purpose — the original material belongs to its authors and is worth buying.
- Presenting advice from unrelated design systems (Material, HIG, Tailwind defaults) as *Refactoring UI* doctrine. Those systems are fine; attributing them here makes the citation meaningless.
- Marking the answer complete without listing which reference files you read. The list is what lets the reader tell a grounded answer from a plausible one.

## Source

References 01–04 cover the book’s design principles and identify the relevant pages in the reviewed PDF edition. [Refactoring UI by Adam Wathan and Steve Schoger](https://refactoringui.com/)

## Anti-Patterns to Watch For

- Designing layouts/navs/shells before designing real features [source: references/01-foundations.md]
- Using font size as the only tool for hierarchy (ignoring weight and color) [source: references/02-page-mechanics.md]
- Using opacity to create grey text on colored backgrounds [source: references/02-page-mechanics.md]
- Starting with too little white space and adding it later [source: references/02-page-mechanics.md]
- Using `em` for type scales (compounds when nested) [source: references/02-page-mechanics.md]
- Using color as the only signal for a UI state [source: references/03-visual-treatment.md]
- Designing with placeholder images instead of real content [source: references/03-visual-treatment.md]
- Shrinking a logo down to use as a favicon [source: references/03-visual-treatment.md]
- Using preprocessor `lighten()` / `darken()` to derive shades [source: references/03-visual-treatment.md]
- Leaving an empty state as a bare "No data" rectangle — it's often the first thing a new user sees [source: references/04-polish.md]
- Rendering tabs, filters or pagination that have nothing to operate on (reads as broken) [source: references/04-polish.md]
- Reaching for a border when a shadow, a second background color, or more space separates better [source: references/04-polish.md]
- Replacing native checkboxes or radios without preserving their behavior and keyboard focus [source: references/04-polish.md]
- Animating layout properties (`width`, `top`, `margin`) instead of `transform` / `opacity` [source: references/05-motion.md]
- Inventing a duration per component instead of picking from a fixed motion scale [source: references/05-motion.md]
- Scaling a whole element up on hover (1.05×), or animating font size [source: references/05-motion.md]
- Showing a spinner before ~150ms of waiting [source: references/05-motion.md]
- Ignoring `prefers-reduced-motion` [source: references/05-motion.md]
- Pure `#000` for the canvas, or pure white for text [source: references/06-dark-mode.md]
- Producing dark mode with `filter: invert(1)` [source: references/06-dark-mode.md]
- Reusing the light-mode brand color in dark mode without rechecking contrast [source: references/06-dark-mode.md]
- Applying the theme after first paint (flash of the wrong theme on every load) [source: references/06-dark-mode.md]
- Keeping every light-mode shadow unchanged on a dark canvas, where it's invisible [source: references/06-dark-mode.md]
- Using a placeholder as the only label [source: references/07-component-patterns.md]
- Validating a field on every keystroke instead of on blur [source: references/07-component-patterns.md]
- A modal that leaks focus to the background or leaves the user without a logical focus target on close [source: references/07-component-patterns.md]
- Left-aligning numeric columns, which hides magnitude [source: references/07-component-patterns.md]
- A translucent sticky table header, with rows showing through it [source: references/07-component-patterns.md]

## Attribution

This skill summarizes design principles inspired by *Refactoring UI* by Adam Wathan & Steve Schoger. Concepts described here are paraphrased into the maintainer's own words; original text, examples, and illustrations remain the property of the authors and live in the book. **Buy the book at https://refactoringui.com — it contains the full material with side-by-side visual examples and case studies that this skill does not reproduce.**
