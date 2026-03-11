# Ch6 — Creating Depth

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## Light Source Convention

- Light source is always **above** the interface
- Users look at screens from a slightly downward angle
- This is the physical convention all simulated depth should honor

## Raised Elements

To make an element appear raised off the page:
- **Lighter top edge:** use a top border or top-side inset box-shadow in a lighter color
- **Small dark box-shadow below:** simulates the shadow cast downward by the raised element
- Pick the lighter edge color by hand — do NOT use semi-transparent white (`rgba(255,255,255,0.x)`) because it desaturates the underlying color and looks fake

## Inset Elements

To make an element appear pressed into the page:
- **Lighter bottom edge:** use a bottom border or bottom-side inset box-shadow in a lighter color
- **Small dark inset shadow at top:** simulates the shadow falling into the well
- Same rule: hand-pick the lighter color instead of using semi-transparent white

## 5-Level Shadow Elevation System

Define 5 shadow levels (like Material Design's elevation system):
- **Level 1 (almost flat):** very small blur, tiny offset — element is barely raised
- **Level 2:** slightly larger blur and offset
- **Level 3:** medium blur, medium offset — default "card" shadow
- **Level 4:** large blur, larger offset — modals, dropdowns
- **Level 5 (closest to user):** very large blur, biggest offset — tooltips, popovers in foreground

Rule: small blur = slightly raised; large blur = close to the user/floating.

## Shadow Response to Interaction

- **On drag (element is "picked up"):** shadow grows — blur and offset increase as if the element moved closer to the user
- **On click/press (element is pressed in):** shadow shrinks and may disappear — simulates the element being pushed into the surface
- This gives tactile feedback without animation

## Two-Part Shadow for Realism

Real objects cast two kinds of shadow:
1. **Direct light shadow** (umbra): large, soft, with big offset and big blur — from the primary light source
2. **Ambient light shadow** (penumbra): tight, dark, with small offset and small blur — from scattered ambient light

For UI shadows:
- Shadow 1: large blur, large offset, low opacity (direct light)
- Shadow 2: small blur, small offset, higher opacity (ambient)

At higher elevations (closer to user), the ambient shadow (Shadow 2) becomes more subtle relative to Shadow 1.

## Flat Design Depth Alternatives

When shadows are not appropriate (flat aesthetic):
- **Lighter = closer, darker = further** — opposite of intuition with real light, but works visually
- Use solid, no-blur shadows: `box-shadow: 4px 4px 0 #000` for a retro/flat look
- These shadows define edges without implying light source

## Overlap Elements for Layering

- Overlapping one element across a background boundary creates a strong sense of layers
- Example: a card that straddles a dark hero and a white content area feels layered
- Example: an avatar that overlaps the edge of a card creates depth without shadows

## Overlapping Images: Invisible Border

- When images overlap each other or a background, edges can clash
- Add a border that matches the **background color** — an "invisible" border
- This creates separation between elements without a visible border color
- Also called a "halo" — a same-color buffer that prevents visual clashing
