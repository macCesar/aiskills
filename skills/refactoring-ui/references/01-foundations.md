# Foundations: Mindset and Systems

Inspired by principles from *Refactoring UI* by Adam Wathan & Steve Schoger. Paraphrased into the maintainer's own words; the original prose, illustrations, and examples are in the book — refactoringui.com.

---

## Build Real Features Before Designing the App

- Don't open the design tool with "the app" in mind — start with a single feature you can actually ship
- Navbars, sidebars, and shells should emerge from the features, not be picked first
- "Designing the app" usually means picking a layout shell with no real content, which leads to dead ends

## Sketch Rough Before Going Polished

- Start with low-fidelity drawings — pencil, marker, or rough boxes in any tool
- Use a tool that physically prevents fine detail (a thick pen, a low-resolution canvas) to lock yourself out of polish too early
- Move to high-fidelity only when the rough concept is settled
- Wireframing tools that already look like polished UI tend to stall this process

## Cycle Between Designing and Building

- Design only what you're going to build right now; don't draft the whole app at once
- Short cycles — design a feature, build it, ship it, decide what's next
- When in doubt, cut features; a complete simple version beats a half-built complex one
- Save scope expansions for the next version

## Defining a Project's Voice

A project's "feel" is the sum of small consistent choices. Decide these together so they reinforce each other:

**Type choice signals tone:**
- Serif → editorial, traditional, considered
- Geometric / rounded sans-serif → friendly, casual
- Neutral sans-serif → quiet, professional, modern

**Color signals associations:**
- Cool blues → reliability, calm
- Warm yellows / golds → warmth, premium feel
- Pinks → playful, less serious

**Border radius signals formality:**
- Sharp / no radius → serious, technical
- Pronounced rounding → soft, friendly

**Copy register signals personality:**
- "An error occurred" reads as formal
- "Something broke on our end" reads as casual

Every project decision should reinforce the same tone — consistency is what makes a project feel intentional rather than thrown together.

## Decide Once: Pre-Build Your Systems

Before picking values per-screen, define a small fixed menu of options to choose from. This eliminates per-decision fatigue and produces consistency by default.

Suggested coverage:

- **Type sizes:** ~8–10 hand-picked values
- **Type weights:** typically 2 (a regular and a bold)
- **Colors:** primary, neutrals (8–10 shades each), and 3–5 accent colors with shades
- **Spacing:** ~10–15 values on a non-linear scale
- **Shadows:** ~5 levels (from barely raised to floating)
- **Border radius:** 3–5 options (none → fully rounded)
- **Border widths:** 2–3 options

## Choose by Elimination, Not by Search

- Don't try to find "the perfect value" — start from the system and work by elimination
- Too big? Try the next smaller. Too pale? Step darker. Too close to white? Step toward the next shade
- A system makes design feel like a multiple-choice exam instead of an open-ended search
