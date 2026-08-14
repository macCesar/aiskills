# The images the platforms fetch

Three files do all the work: the share card, the favicon, and the iOS home-screen icon. Each has a constraint that is not obvious and fails silently when you miss it.

---

## `og:image` — the share card

**1200 × 630 px, JPEG.** That is the ratio every platform lays out for; anything else gets cropped by whoever is rendering it, and you do not get to choose where.

**JPEG, not WebP.** Several preview clients still cannot decode WebP and simply show no image. The 30 KB WebP would save are not worth an invisible link. This is the one place in a modern site where JPEG is still the right answer — the page itself can serve WebP.

**Under ~1.5 MB, ideally under 300 KB.** WhatsApp gives up on slow or heavy images and renders the card without a thumbnail.

What goes on it: the logo, a short claim, and one photograph or a solid brand background. It is read at postage-stamp size in a chat list — a full paragraph of text is unreadable there. Do not put anything important in the outer ~60 px, since some clients crop to a squarer ratio.

```bash
# From a source photo: cover-crop to 1200x630, no upscaling beyond what it has
magick source.jpg -resize 1200x630^ -gravity center -extent 1200x630 \
  -quality 82 -strip og-image.jpg
```

`-resize 1200x630^` fills the box (the `^` means "at least"), `-extent` crops the overflow, and `-strip` removes EXIF, which on a phone photo can carry GPS coordinates you did not mean to publish.

If it carries text over a photo, add `-sampling-factor 4:4:4` — the default chroma subsampling smears coloured text at small sizes.

**Verify the file, do not trust the command.** `og:image:width` and `og:image:height` must equal what the file really measures; the audit script reads the dimensions from the file header for exactly this reason.

```bash
magick identify og-image.jpg      # → og-image.jpg JPEG 1200x630 …
```

## Favicon — one SVG

```html
<link rel="icon" type="image/svg+xml" href="/images/logo-symbol.svg">
```

**An SVG has no intrinsic size**, so it draws sharp at 16 px in the tab and at 512 px in a bookmark grid. A `.ico` or a PNG is fixed: the browser asks for it at half a dozen different sizes — tab, bookmarks bar, reading list, home screen — and scales whatever it finds, which is where blurry favicons come from. Safari has supported `rel="icon"` with SVG since version 15 (2021); Chrome and Firefox for longer.

Two things about the SVG file itself:

- **It must declare real dimensions, not `width="100%" height="100%"`.** A percentage-sized SVG has no intrinsic ratio, and a browser using it as an icon does not know what shape to give it. Set `width` and `height` to the `viewBox` values in pixels.
- **Pure vectors.** An SVG with an embedded raster or a non-outlined font is a large file that renders inconsistently. Outline the text.

Add a `favicon.ico` in the document root only if the site must support very old browsers; modern ones stop at the SVG. Do not spend time on a folder of eight PNG sizes — that convention predates SVG favicon support.

## `apple-touch-icon` — 180 × 180 PNG

iOS **ignores the SVG** when the site is added to the home screen. With no PNG it screenshots the page, which at that size is a grey smudge.

```bash
# From the same SVG, at a size that downsamples cleanly
rsvg-convert -w 1480 logo-symbol.svg -o /tmp/symbol.png
magick /tmp/symbol.png -resize 148x148 -background white -alpha remove \
  -gravity center -extent 180x180 -strip apple-touch-icon.png
```

Three decisions inside that command:

- **White background, no alpha.** iOS does not honour the alpha channel on these icons — it fills transparency with black, and a dark logo vanishes into it. `-alpha remove` flattens onto `-background`.
- **The symbol occupies 148 of 180 (~82%).** iOS applies its own rounded mask; a logo that reaches the edge loses its corners to it.
- **Square and unrounded.** iOS draws the corners. Rounding it yourself produces a double-rounded icon with white notches.

180 × 180 is the Retina iPhone size; iOS downscales it for everything else. One file is enough — the `sizes` attribute is a hint, not a requirement to ship every size.

If there is no vector source, render from the largest raster available and accept it; do not upscale a 64 px PNG to 180 and call it done.

## After changing any of them

Facebook and WhatsApp **cache the card for days**. Change the `og:image` and the link keeps showing the old one, which reads exactly like the fix not working. Force the refresh at <https://developers.facebook.com/tools/debug/> by pasting the URL and pressing *Scrape Again*.

If the image filename stays the same and the server sends a long `Cache-Control`, browsers hold the old one too. The discipline that replaces a short cache is **renaming the file when its content changes**.

## Page images, for completeness

Not part of the share card, but the same audit usually finds them:

| Use | Format | Why |
| --- | --- | --- |
| Photographs | WebP, quality ~80 | 15–24× smaller than the equivalent PNG |
| Files meant to be shared or downloaded | JPEG `4:4:4` | they travel through WhatsApp; no chroma subsampling because they carry text |
| Logos and icons | SVG | sharp at any size, and doubles as the favicon |
| `og:image` | JPEG | several preview clients still cannot read WebP |

Below-the-fold images take `loading="lazy"`. Every image takes a descriptive `alt` — it is what a screen reader announces and what Google reads.
