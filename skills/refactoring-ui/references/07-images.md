# Ch7 — Working with Images

Source: "Refactoring UI" by Adam Wathan & Steve Schoger

---

## Use Real Images From Day One

- Never design with placeholder images (grey boxes, lorem ipsum images)
- Placeholder images lie about how real content will look — especially for products, people, and covers
- Hire a photographer or use quality stock photo services (e.g., Unsplash)
- The visual design must work with actual images, not idealized placeholders

## Text Over Images

Option 1: **Semi-transparent overlay**
- Add a dark overlay (black) for light-colored text on top of a photo
- Add a light overlay (white) for dark-colored text on top of a photo
- Overlay controls how much of the image shows through

Option 2: **Lower image contrast + adjust brightness**
- Reduce contrast on the image itself so text has a more uniform background
- Brighten or darken the whole image to create a consistently light/dark canvas for text

Option 3: **Colorize the image**
- Desaturate the image (remove color)
- Apply a solid fill layer using "multiply" blend mode in your design tool
- Result: a single-color tone that text can sit on top of

Option 4: **Text shadow**
- Use a large blur, no offset text-shadow behind the text
- Creates a soft halo that separates text from the image background
- Best for small amounts of text (headlines, labels)

## Icons at Scale

- Icons designed at 16–24px look chunky and blurry when scaled to 3–4×
- At large sizes, use a **shaped container** with a background color instead of a raw oversized icon
- Put the icon inside a circle, rounded square, or other shape
- Scale the container to the needed size; keep the icon at its native size (or slightly larger)
- This prevents the "blown up icon" problem while adding visual polish

## Screenshots

Three problems with using screenshots at full scale:
- At 70% scale, 16px font becomes ~11px — unreadable
- At 50% scale, 16px font becomes 8px — completely illegible

Solutions:
1. **Use a tablet/narrow layout screenshot** instead of a full desktop one — content scales better
2. **Take a partial screenshot** — crop to just the relevant portion
3. **Draw a simplified version** — remove most UI, keep only what illustrates the point
4. Never rely on the viewer being able to read or understand text in a thumbnail screenshot

## Favicons

- A 128px logo shrunk to 16px is unrecognizable — too much detail is lost
- **Redraw the favicon at target size** from scratch (16×16, 32×32)
- Keep it to 1–2 elements; use just the icon mark, not the full wordmark
- Test it at 1× actual size while designing — what looks good at 128px often looks like noise at 16px

## User-Uploaded Images

Two problems: aspect ratio and background bleed.

**Aspect ratio:** User uploads won't match your layout's expected proportions.
- Use fixed containers (set width and height)
- Apply `background-size: cover` (or the equivalent `object-fit: cover`)
- Let the browser/engine center and crop to fill the container

**Background bleed:** Images with white or light backgrounds bleed into light-colored page backgrounds.
- Don't use a visible border — it creates a box outline that looks heavy
- Instead, add a subtle **inner box-shadow** (inset): `box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1)`
- This creates a soft inner ring that defines the edge without a harsh border
- Works across all image background colors since it sits on top of the image
