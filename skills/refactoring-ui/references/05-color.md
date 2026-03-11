# Ch5 — Working with Color

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## HSL Color Model

HSL (Hue, Saturation, Lightness) is the right model for UI color work:

- **Hue:** 0°=red, 60°=yellow, 120°=green, 180°=cyan, 240°=blue, 300°=magenta
- **Saturation:** 0%=grey (no color), 100%=fully vivid
- **Lightness:** 0%=black, 50%=pure color, 100%=white

**HSL ≠ HSB (HSV):** Different definitions of "lightness." HSB's "brightness" at 100% still gives a vivid color; HSL's lightness at 100% is always white. They are NOT interchangeable.

## What Colors You Need

A complete UI color system requires:
- **Greys:** 8–10 shades (used for text, backgrounds, borders, UI chrome)
- **Primary color:** 5–10 shades (brand color, main actions)
- **Accent colors:** typically 3–5 colors × 5–10 shades each
  - Red (danger, error, destructive)
  - Yellow (warning, caution)
  - Green (success, positive)
  - Others as needed (blue for info, purple, etc.)

This can mean 10 colors × 10 shades = 100 values. Define them all up front.

## Do NOT Use Preprocessor lighten()/darken()

- `lighten(blue, 20%)` just adds white or removes saturation — produces washed-out results
- `darken(blue, 20%)` adds black — produces muddy, lifeless results
- Define shades up front by hand using HSL — you'll get better results every time

## How to Build a 9-Shade Scale (100–900)

Step-by-step:
1. **Pick your base color** (e.g., 500): should work as a button background
2. **Pick the darkest shade** (e.g., 900): should work as dark text
3. **Pick the lightest shade** (e.g., 100): should work as a tinted background
4. **Fill in 700** next (halfway between 500 and 900)
5. **Fill in 300** next (halfway between 100 and 500)
6. **Fill remaining gaps** (200, 400, 600, 800) by eye

## Saturation Must Increase as Lightness Moves from 50%

- Pure HSL: as you move lightness toward 0% or 100%, the color appears less vivid
- To compensate, **increase saturation** as lightness increases or decreases from 50%
- Very light shades (lightness 90–95%): bump saturation up significantly
- Very dark shades (lightness 15–25%): bump saturation up to maintain richness
- If you don't, light shades look washed-out and dark shades look muddy

## Rotate Hue for Perceptually Better Shades

- Rotating hue slightly while lightening/darkening produces more natural results
- To make a **lighter** shade: rotate hue toward the nearest "bright" color (60°, 180°, 300°)
- To make a **darker** shade: rotate hue toward the nearest "dark" color (0°, 120°, 240°)
- Maximum rotation: **20–30°** — more than that and the color looks completely different
- This mimics how real pigments behave when tinted or shaded

## Cool vs. Warm Greys

- True neutral grey has 0% saturation — often feels clinical and bland
- **Cool greys:** add a small amount of blue saturation (feels modern, professional)
- **Warm greys:** add a small amount of yellow or orange saturation (feels inviting, human)
- Match grey temperature to your overall palette's temperature

## Accessible Contrast (WCAG)

- **Small text (<~18px normal weight, <~14px bold):** minimum 4.5:1 contrast ratio
- **Large text (≥~18px normal or ≥~14px bold):** minimum 3:1 contrast ratio
- Check: dark text on white bg is easier to pass than white on dark colored bg

## Accessibility Alternatives to White-on-Dark

- Instead of white text on a dark colored background, try **dark text on a light tinted background**
- Example: dark navy text on pale blue background — same brand color, much higher contrast
- This "flip" is often more accessible and looks more sophisticated

## Colored Text on Colored Background (Accessible)

- White text on a vivid colored button fails contrast if the color is too bright
- Instead of darkening the background, try **rotating the hue toward a bright anchor**
- A gold/yellow text on a dark orange button is more legible than white because yellow is inherently brighter
- Experiment: rotate hue toward 60° (yellow) for lighter-feeling text that still passes contrast

## Never Use Color as the Only Signal

- Color-blind users (8% of males) cannot distinguish red/green by color alone
- Always pair color with a second signal:
  - Icon (checkmark, warning triangle, X)
  - Shape difference
  - Text label
  - Position or contrast difference
- This applies to: status badges, error states, success messages, alert levels, charts
