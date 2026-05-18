---
name: refactoring-ui
description: 'Use when the user asks for UI/UX design advice, design reviews, visual hierarchy improvements, color system help, typography guidance, spacing decisions, depth/shadow usage, image handling, or finishing touches on any interface. Inspired by "Refactoring UI" by Adam Wathan & Steve Schoger. Triggers: "how do I make this look better?", color palettes, type scales, spacing systems, visual hierarchy, design reviews, shadows/depth, image handling, empty states, borders.'
---

# Refactoring UI Skill

Design advice grounded in the principles taught by Adam Wathan & Steve Schoger in their book *Refactoring UI*. **The book itself contains the original prose, illustrations, side-by-side examples, and case studies — buy it at https://refactoringui.com for the full material.** This skill provides reformulated guidance for use as an AI assistant reference.

## Required workflow (read before responding)

The SKILL.md alone is an **index** of references. The detail you need
to give accurate answers lives in the reference files. **Reading this
SKILL.md is not enough.**

### Step 1 — Open the relevant reference files

| Task involves | Required reading |
|---|---|
| Color systems, typography, spacing scales — defining the system | [references/01-foundations.md](references/01-foundations.md) |
| Layout, white space, visual hierarchy, page-level structure | [references/02-page-mechanics.md](references/02-page-mechanics.md) |
| Color usage, HSL, greys, contrast, shadows, depth, images | [references/03-visual-treatment.md](references/03-visual-treatment.md) |
| Empty states, borders, accents, finishing touches | [references/04-polish.md](references/04-polish.md) |
| Motion, microinteractions, transitions, hover/press states, loading | [references/05-motion.md](references/05-motion.md) |
| Dark mode, multi-theme color tokens, theme toggle, contrast strategy | [references/06-dark-mode.md](references/06-dark-mode.md) |
| Modals, forms, tables — component-specific layout and behavior patterns | [references/07-component-patterns.md](references/07-component-patterns.md) |

### Step 2 — Output contract

Every design recommendation, ratio, value, or rule you cite MUST be
backed by a citation in the form:

`[source: references/<file>.md]`

Example: *"Use weight and color, not just font size, to establish hierarchy [source: references/02-page-mechanics.md]"*

### Step 3 — If you must answer from memory

If you write a claim without having read the reference that backs it,
prepend `FROM_MEMORY (unverified):` to that claim. Do not hide it.

### Banned behaviors

- ❌ Inventing ratios, scale values, contrast numbers, or rules not in the references
- ❌ Reproducing the book's prose, illustrations, or examples verbatim — paraphrase only
- ❌ Mixing in advice from unrelated design systems (Material, HIG, Tailwind defaults) as if it were *Refactoring UI* doctrine
- ❌ Marking the answer complete without listing which reference files you read

## When to use

- User asks "how do I make this look better?"
- User asks about color palettes, type scales, or spacing systems
- User asks about visual hierarchy or emphasis
- User is designing a UI component, page, or layout
- User wants a design review or critique
- User asks about shadows, depth, or layering
- User asks about handling images in UI
- User asks about empty states, borders, or decorative elements

## Source

Inspired by 'Refactoring UI' by Adam Wathan & Steve Schoger — refactoringui.com

## Reference Files

| File                                | Topics                                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| `references/01-foundations.md`      | Project mindset: feature-first work, scope discipline, defining systems, picking a voice |
| `references/02-page-mechanics.md`   | Visual hierarchy, layout, white space, spacing scales, typography                       |
| `references/03-visual-treatment.md` | Color systems (HSL, shades, greys, contrast), depth and shadows, image handling         |
| `references/04-polish.md`           | Finishing touches: borders, accents, empty states, decorative defaults, design intuition |
| `references/05-motion.md`           | Motion system (durations, easings), hover/press states, loading patterns, prefers-reduced-motion — **complementary** (not from RUI) |
| `references/06-dark-mode.md`        | Dark mode color tokens, text contrast, shadow handling, images, theme toggle — **complementary** (extrapolates RUI's HSL principles) |
| `references/07-component-patterns.md` | Modals (focus, layout), forms (labels, validation), tables (density, alignment) — **complementary** (extends RUI principles to specific components) |

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

## Attribution

This skill summarizes design principles inspired by *Refactoring UI* by Adam Wathan & Steve Schoger. Concepts described here are paraphrased into the maintainer's own words; original text, examples, and illustrations remain the property of the authors and live in the book. **Buy the book at https://refactoringui.com — it contains the full material with side-by-side visual examples and case studies that this skill does not reproduce.**
