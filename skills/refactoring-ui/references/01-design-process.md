# Ch1 — Starting from Scratch

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## Feature-First Design

- Design actual features, not shells, navbars, or layouts first
- Pick one real feature and design it end-to-end before thinking about navigation
- The shell and layout emerge naturally from the features — don't force it first
- Resist the urge to design "the app" — design what people will actually use

## Low-Fidelity First (Thick Sharpie Trick)

- Start with low-fidelity mockups — details don't matter at this stage
- Use a thick Sharpie (or similar): makes it physically impossible to add fine details
- Sketch ideas, not pixels — get the general layout and content blocks right
- Avoid wireframing tools that tempt you into making polished designs too early
- Don't move to high-fidelity until the concept is locked

## Work in Cycles, Be a Pessimist

- Only design what you're ready to build right now
- Work in short design-then-build cycles, not one giant design phase
- Be a pessimist: cut features before building, not after
- A simple, complete experience beats a complex, half-built one
- Add features to the next version; ship the core first

## Choose a Personality

Design decisions that define personality:

**Font choice:**
- Serif → classic, elegant, literary (e.g., law firms, newspapers)
- Rounded sans-serif → playful, friendly, approachable
- Neutral sans-serif → plain, professional, clean

**Color:**
- Blue → safe, familiar, trustworthy
- Gold/yellow → luxurious, sophisticated
- Pink → fun, not-too-serious

**Border radius:**
- Small or none → formal, serious
- Large → playful, friendly

**Language register:**
- "An error occurred" → formal
- "Uh oh, something broke!" → casual and approachable

Every choice should reinforce the same personality — be consistent.

## Pre-Define Systems Before Designing

Define your system up front; make decisions once instead of every time:

- **Font sizes:** 8-10 values (type scale)
- **Font weights:** usually 2 (normal 400, bold 600/700)
- **Colors:** 8-10 shades per color, plus primary, greys, accents
- **Spacing:** 10-15 values on a non-linear scale
- **Box shadows:** 5 options (small, medium, large, extra-large, inner)
- **Border radius:** 3-5 options (none, small, medium, large, full)
- **Border widths:** 2-3 options

**Benefit:** When you need to make a decision, you're choosing from a small set, not from infinity. Eliminates decision fatigue.

## Process of Elimination

- Don't try to "find the perfect value" — start from a set and eliminate
- Too big? Try the next smaller option. Too close to white? Try the next shade darker.
- Systems make design systematic, not artistic guesswork
