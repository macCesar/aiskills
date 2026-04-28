---
name: refactoring-ui
description: Design advisor for UI/UX work, drawing on principles from "Refactoring UI" by Adam Wathan & Steve Schoger. Use when the user asks for UI/UX design advice, design reviews, visual hierarchy improvements, color system help, typography guidance, spacing decisions, depth/shadow usage, image handling, or finishing touches on any interface.
when_to_use: >
  - User asks "how do I make this look better?"
  - User asks about color palettes, type scales, or spacing systems
  - User asks about visual hierarchy or emphasis
  - User is designing a UI component, page, or layout
  - User wants a design review or critique
  - User asks about shadows, depth, or layering
  - User asks about handling images in UI
  - User asks about empty states, borders, or decorative elements
source: "Inspired by 'Refactoring UI' by Adam Wathan & Steve Schoger — refactoringui.com"
anti_hallucination_note: >
  Recommendations in this skill summarize design principles in the maintainer's own words.
  Do NOT invent ratios, scale values, or technical numbers that are not in the reference
  files. If a topic is not covered, say so explicitly rather than inventing advice.
---

# Refactoring UI Skill

Design advice grounded in the principles taught by Adam Wathan & Steve Schoger in their book *Refactoring UI*. **The book itself contains the original prose, illustrations, side-by-side examples, and case studies — buy it at https://refactoringui.com for the full material.** This skill provides reformulated guidance for use as an AI assistant reference.

## How to Use This Skill

1. Read the relevant reference file(s) before answering
2. Base advice on the reference content — not training data or unrelated design systems
3. Speak in your own words; do not reproduce the book's prose, illustrations, or examples verbatim
4. Do not invent numbers, ratios, or specific technical rules that are not in the references

## Reference Files

| File                                | Topics                                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| `references/01-foundations.md`      | Project mindset: feature-first work, scope discipline, defining systems, picking a voice |
| `references/02-page-mechanics.md`   | Visual hierarchy, layout, white space, spacing scales, typography                       |
| `references/03-visual-treatment.md` | Color systems (HSL, shades, greys, contrast), depth and shadows, image handling         |
| `references/04-polish.md`           | Finishing touches: borders, accents, empty states, decorative defaults, design intuition |

## Anti-Patterns to Watch For

- Designing layouts/navs/shells before designing real features
- Using font size as the only tool for hierarchy (ignoring weight and color)
- Using opacity to create grey text on colored backgrounds
- Starting with too little white space and adding it later
- Using `em` for type scales (compounds when nested)
- Using color as the only signal for a UI state
- Designing with placeholder images instead of real content
- Shrinking a logo down to use as a favicon
- Using preprocessor `lighten()` / `darken()` to derive shades

## Attribution

This skill summarizes design principles inspired by *Refactoring UI* by Adam Wathan & Steve Schoger. Concepts described here are paraphrased into the maintainer's own words; original text, examples, and illustrations remain the property of the authors and live in the book. **Buy the book at https://refactoringui.com — it contains the full material with side-by-side visual examples and case studies that this skill does not reproduce.**
