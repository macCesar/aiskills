# Motion: Microinteractions, Transitions, Hover

> **Scope note**: motion is **not** covered in *Refactoring UI* by Adam Wathan & Steve Schoger. This file is complementary guidance, written in the same spirit as the book — favor restraint, build from a small fixed system, and avoid effects that exist to draw attention to themselves. It does not paraphrase the book.

---

## The Restraint Principle Carries Over

The book's central idea — "make the right things stand out by quieting the rest" — applies directly to motion. Animation in a UI is for **communicating state changes**, not for entertainment.

- If the user wouldn't notice the animation is gone, it shouldn't be there
- If the animation shows that something happened (state change, success, error), keep it
- "Wow" animations are a tax on every interaction after the first

## Pre-Build a Motion System

Like type/color/spacing scales, define a fixed menu of durations and easings up front. Pick from that menu instead of inventing per-component.

**Sample duration scale (in milliseconds):**

| Token | Duration | Use |
|---|---|---|
| `instant` | 0–80 | Press/active states. Should feel like no delay. |
| `fast` | 100–200 | Hover effects, small state changes (icons, toggles, focus rings) |
| `normal` | 200–400 | Modal/drawer entry, expand/collapse, page-level transitions |
| `slow` | 400–600 | Decorative reveals, onboarding sequences |
| `+1s` | ≥ 1000 | Almost always wrong in a working UI — reserve for very specific moments |

**Sample easing scale:**

| Token | Curve | Use |
|---|---|---|
| `enter` | `cubic-bezier(0, 0, 0.2, 1)` (ease-out) | Elements appearing — fast start, slow finish |
| `exit` | `cubic-bezier(0.4, 0, 1, 1)` (ease-in) | Elements leaving — slow start, fast finish (they "fall away") |
| `standard` | `cubic-bezier(0.4, 0, 0.2, 1)` (ease-in-out) | State changes that aren't directional |
| `linear` | linear | Loaders, progress, anything tied to real time |

## Animate Cheap Properties

Only `transform` and `opacity` are GPU-composited and frame-stable. Animating other properties forces layout/paint per frame and stutters on mid-range hardware.

| Cheap | Expensive |
|---|---|
| `transform: translate(...)`, `scale(...)`, `rotate(...)` | `width`, `height`, `top`, `left`, `margin`, `padding` |
| `opacity` | `box-shadow` (animatable, but slow at large blur) |
| `filter: blur()` (sparingly) | `background-color` on large surfaces |

To slide a panel in: animate `transform: translateX(100%)` → `translateX(0)`, not `right: -400px` → `right: 0`.

## Hover States

The book's principle (use color/weight/contrast for hierarchy, not just one tool) applies to hover too — combine signals subtly.

A solid hover combines two of:

- A small lightness shift on the background (1–2 steps on your shade scale)
- A border or shadow change
- An icon color change

Avoid:

- Scaling up the whole element (1.05×, 1.1×) — chunky and dated
- A bright glow — feels like 2008
- Animating font size on hover — text reflow is jarring

```css
.button {
  background: var(--brand-500);
  transition: background-color 150ms cubic-bezier(0, 0, 0.2, 1);
}
.button:hover {
  background: var(--brand-600);
}
```

## Press / Active States

Visual pressure should feel like the element was pushed *into* the page — the inverse of "raised."

- Shadow shrinks or disappears
- A tiny `transform: translateY(1px)` works for cards
- The hover background usually deepens one more step on press

Press states should feel **instant** — duration `instant` (0–80ms), not `fast`.

## Loading

In order of preference:

1. **Optimistic UI** — assume success, update immediately, roll back on error. No spinner.
2. **Skeleton screen** — placeholder shapes matching the final layout. Communicates structure while content loads.
3. **Inline progress** — a thin progress bar at the top of the affected region, or shimmer on a single field.
4. **Spinner** — only when 1–3 don't fit. Add a "Cancel" if the operation is long.

Skeleton screens beat spinners because they reduce the perceived wait — the layout doesn't shift when content arrives.

If you must use a spinner, **only show it after ~150ms** of waiting. Most operations finish faster than that; a spinner that flashes in and out is worse than no spinner.

## Respect `prefers-reduced-motion`

Some users disable motion at the OS level (motion sickness, vestibular disorders, focus). The browser exposes this preference:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Or, more deliberately, swap motion for an instant state change inside specific components. Never disable a state change entirely (the user still needs to see that something happened) — only the *animation between* states.

## Anti-Patterns

- ❌ Animating layout-affecting properties (`width`, `top`, `margin`) — jank
- ❌ One-off durations per component — kills consistency
- ❌ Easing on a linear curve for entries — feels mechanical
- ❌ Spinners that appear under 150ms — flashy noise
- ❌ Decorative animations that fire on every page load — annoying by the second visit
- ❌ Ignoring `prefers-reduced-motion` — accessibility regression
- ❌ Long durations (>600ms) for state changes — feels sluggish
