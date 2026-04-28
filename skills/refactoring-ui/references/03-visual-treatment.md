# Visual Treatment: Color, Depth, Images

Inspired by principles from *Refactoring UI* by Adam Wathan & Steve Schoger. Paraphrased into the maintainer's own words; the original prose, illustrations, and examples are in the book — refactoringui.com.

---

## HSL Is the Right Model for UI Color

HSL (Hue, Saturation, Lightness) gives intuitive control:

- **Hue:** 0°=red, 60°=yellow, 120°=green, 180°=cyan, 240°=blue, 300°=magenta
- **Saturation:** 0%=grey (no color), 100%=fully vivid
- **Lightness:** 0%=black, 50%=pure color, 100%=white

**HSL ≠ HSB (HSV).** HSB's "brightness" at 100% still gives a vivid color; HSL's lightness at 100% is always white. Don't conflate them.

## Building a Complete Palette

Plan for more colors than you'd guess:

- **Greys:** 8–10 shades (text, backgrounds, borders, UI chrome)
- **Primary brand color:** 5–10 shades
- **Accent set:** typically 3–5 named colors × 5–10 shades each
  - Red (danger, error, destructive)
  - Yellow (warning, caution)
  - Green (success, positive)
  - Others as needed (blue for info, purple, etc.)

That can mean ~10 colors × ~10 shades = 100 values. Define them all once, up front.

## Skip Preprocessor `lighten()` / `darken()`

- `lighten(blue, 20%)` mixes white into the color — produces washed-out results
- `darken(blue, 20%)` mixes black — produces muddy, lifeless results
- Hand-pick shades using HSL — better results every time

## Building a 9-Step Shade Scale (100–900)

Step by step:

1. **Pick the base** (500): should work as a button background
2. **Pick the darkest** (900): should work as text on light bg
3. **Pick the lightest** (100): should work as a tinted background
4. **Fill in 700:** roughly halfway between 500 and 900
5. **Fill in 300:** roughly halfway between 100 and 500
6. **Fill the gaps** (200, 400, 600, 800) by eye — adjusting until the steps feel even

## Bump Saturation as Lightness Moves Away from 50%

- Moving lightness toward 0% or 100% in pure HSL drains apparent vividness
- Counter it: increase saturation as you push lightness up or down
- Very light shades (lightness 90–95%): bump saturation noticeably
- Very dark shades (lightness 15–25%): bump saturation to keep richness
- Without this, light shades look washed out and dark shades look muddy

## Rotate Hue Slightly When Lightening or Darkening

- Pure-hue lightening/darkening looks artificial; shifting hue a bit produces more natural shades
- Toward lighter: rotate toward the nearest "bright anchor" (60°, 180°, 300°)
- Toward darker: rotate toward the nearest "dark anchor" (0°, 120°, 240°)
- Cap the rotation at ~20–30° — beyond that the color reads as a different one entirely
- Mimics how real pigments behave when tinted or shaded

## Greys Don't Need to Be Pure Grey

- Pure 0%-saturation grey often feels clinical and bland
- **Cool greys:** small amount of blue saturation → modern, professional
- **Warm greys:** small amount of yellow/orange saturation → inviting, human
- Match the temperature of your greys to the rest of your palette

## Accessible Contrast (WCAG)

- **Small text (<~18px normal weight, <~14px bold):** at least 4.5:1
- **Large text (≥~18px normal, ≥~14px bold):** at least 3:1
- Dark text on white passes more easily than white text on a colored bg

## When White-on-Colored Fails Contrast

- Try dark text on a *light tinted* version of the same brand color
- Example: dark navy text on pale blue — same brand, much higher contrast
- Often more sophisticated visually than white-on-saturated

## Colored Text on Colored Backgrounds

- White text on a vivid bright button often fails contrast
- Instead of darkening the background, shift the *text* hue toward a bright anchor (rotate toward yellow/60°)
- Yellow text on a dark orange button can read more clearly than white because yellow is inherently brighter

## Color Cannot Be the Only Signal

- ~8% of males cannot distinguish red/green by color alone
- Always pair color with a second signal:
  - Icon (checkmark, warning triangle, X)
  - Shape difference
  - Text label
  - Position or strong contrast difference
- Applies to: status badges, error states, success messages, alert levels, charts

---

## Light Source Convention

- Simulated depth in a UI assumes the light source sits **above** the screen
- Users naturally look at screens from a slightly downward angle
- Every shadow, edge, and inset should respect that single "sun"

## Raised Elements

To make an element appear lifted off the page:

- **Lighter top edge:** a top border or top inset shadow in a lighter shade
- **Small dark shadow below:** the element's cast shadow on the surface
- Hand-pick the lighter color — semi-transparent white (`rgba(255,255,255,0.x)`) desaturates the underlying color and looks fake

## Inset Elements

To make an element appear pressed into the page:

- **Lighter bottom edge:** bottom border or bottom inset shadow in a lighter shade
- **Small dark inset shadow at top:** simulates shadow falling into the well
- Same rule: hand-pick the light color rather than using transparent white

## Five-Level Shadow System

Define ~5 shadow levels (similar to Material Design's elevation):

- **Level 1 — barely raised:** very small blur, tiny offset
- **Level 2 — slightly higher:** modest blur and offset
- **Level 3 — default card:** medium blur, medium offset
- **Level 4 — modal / dropdown:** large blur, larger offset
- **Level 5 — closest to viewer:** very large blur, biggest offset (tooltips, popovers)

Rule of thumb: small blur reads as slightly raised, large blur reads as floating close to the viewer.

## Shadows React to Interaction

- **On drag (element "picked up"):** shadow grows (blur and offset increase) — feels like the element moved closer to the user
- **On click/press (element pressed in):** shadow shrinks or disappears — feels pushed into the surface
- Tactile feedback without animation

## Compound Shadows: Direct + Ambient Light

Real objects cast two shadow layers:

1. **Direct light shadow** (umbra): large, soft, big offset, big blur — from the primary light source
2. **Ambient light shadow** (penumbra): tight, dark, small offset, small blur — from scattered ambient light

For UI:

- Shadow 1: large blur, large offset, low opacity (direct)
- Shadow 2: small blur, small offset, higher opacity (ambient)

At higher elevations, the ambient shadow becomes more subtle relative to the direct shadow.

## Depth Without Shadows (Flat Aesthetic)

When shadows aren't appropriate:

- **Lighter = closer, darker = further** — opposite of real-world intuition, but works visually
- Solid no-blur "shadows": `box-shadow: 4px 4px 0 #000` for a retro/flat look
- These define edges without implying a light source

## Layering Through Element Overlap

- Overlap one element across the boundary of another to create a clear sense of layers
- Example: a card straddling a dark hero and a white content area below
- Example: an avatar that overlaps the edge of a card — depth without shadow

## Halo Borders to Separate Adjacent Images

- When images touch each other or a busy background, edges clash
- Add a border in the **same color as the background** behind the image
- That "invisible" border (sometimes called a halo) creates separation without a visible line color

---

## Use Real Content From the Start

- Never design with placeholder images — grey boxes lie about how the layout actually feels
- Real photos differ in aspect, brightness, and busyness — design must work with reality
- Hire a photographer or use quality stock services (e.g., Unsplash)

## Putting Text on Top of an Image

Four reliable techniques:

**1. Semi-transparent overlay**
- Dark overlay for light-colored text
- Light overlay for dark-colored text
- Tune the overlay opacity until contrast is comfortable

**2. Reduce image contrast / shift brightness**
- Lower contrast on the image so text has a more uniform background
- Brighten or darken globally to give a consistent canvas

**3. Recolor the image**
- Desaturate, then apply a solid color via "multiply" blend mode
- Result: a single-tone image that text reads cleanly on top of

**4. Soft halo behind the text**
- Big blur, no offset text-shadow behind the text
- Best for short text (headlines, labels), not paragraphs

## Don't Just Scale Tiny Icons Up

- Icons drawn at 16–24px look chunky and blurry when stretched 3–4×
- At larger sizes, put the icon inside a **shaped container** (circle, rounded square)
- Scale the container up; keep the icon at native size (or only slightly larger)
- Adds polish, avoids the "blown-up icon" problem

## Screenshots in Marketing/Documentation

The problem: scaling shrinks text below readability.

- At 70% scale, 16px font ≈ 11px — already getting unreadable
- At 50% scale, 16px font = 8px — illegible

What works:

1. Use a tablet/narrow-layout screenshot — scales better than a full desktop one
2. Take a partial screenshot — crop to the relevant area
3. Draw a simplified version — strip most UI, keep what matters
4. Don't depend on the viewer being able to read the text in a thumbnail

## Favicons Need to Be Redrawn, Not Shrunk

- A 128px logo shrunk to 16px loses too much detail
- Redraw at the target size (16×16, 32×32) from scratch
- 1–2 elements only; usually just the icon mark, not the wordmark
- Test at 1× actual size while designing — what reads at 128px is often noise at 16px

## User-Uploaded Images: Two Problems

**Aspect ratio:** uploads won't match your layout's expected proportions.
- Fixed-size container
- `background-size: cover` (or CSS `object-fit: cover`)
- Let the engine center and crop

**Background bleed:** white-bg images dissolve into white page bgs.
- Don't use a hard border — too heavy
- Instead, an inset box-shadow: `box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1)`
- Soft inner ring that defines the edge without a visible border color
