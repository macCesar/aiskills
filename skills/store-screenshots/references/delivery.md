# Store specifications, SVG export, and delivery

## Verify the destination before designing

Open the current official documentation for every requested store and record the URL, verification date, device/upload slot, locale, accepted dimensions, format, count, and applicable content restrictions:

- [Apple creative assets](apple-creative-assets.md) for Header, Search Results, universal artwork, safe areas and review.
- [Apple media](apple-media.md) for screenshots and App Preview video requirements.
- [Custom Product Pages](apple-custom-product-pages.md), [Asset Library](apple-asset-library.md) and [Product Page Optimization](apple-product-page-optimization.md) for page, reuse and experiment workflows.
- [Google Play](google-play.md) for feature graphics, screenshots, large screens and YouTube previews.

Do not apply a rule for one asset type or device class to another. Use the dated platform references and reopen their official sources. A newer simulator's native screenshot is not necessarily accepted by a different slot. Distinguish baseline upload constraints from recommendation and large-screen guidance. Do not bake dated requirements into a generator without explicit target/version metadata.

If live verification is unavailable, use the user's actual console error/requirements, state the limitation, and do not promise acceptance. A ratio-only check is not a complete store validator. Tablet destinations may require real fullscreen UI without promotional copy: keep such uploads separate from designed alternatives. Check the current rule before applying phone templates to tablets.

## Portable package

Follow the project's naming conventions; a default is:

```text
docs/store-assets/
  README.md                     # index, decisions, store spec links/date
  app-store/
    captures/{iphone,ipad}/     # untouched selected native captures
    source/
      series.json              # slide order, copy, grouping, placement, provenance
      generate.py              # project-specific layout generation, if needed
      export.py                # bundled artwork.py copy, if used
      assets/                  # logos, fonts, licenses
      {iphone,ipad}/           # editable SVG masters
    final/{iphone,ipad}/       # ONLY selected screenshot upload PNGs
    final/creative/            # header/search/universal images, when requested
    final/previews/            # videos, when requested
    review/                    # contact sheets and visual QA notes
    alternatives/              # experiments, not upload candidates
  play-store/
    captures/{phone,tablet}/
    source/
    final/{phone,tablet}/      # screenshots
    final/feature-graphic/     # separate feature graphic, when requested
    review/
    alternatives/
```

Create only requested platforms and useful folders. Prefer each store's source package to be self-contained. Use relative paths anchored to the generator's location, never a developer's home directory or temporary venv. Bundle the exporter if regeneration depends on it; document dependency versions and an exact command runnable from another directory. Do not leave copied captures mislabeled as final designs.

A simple series manifest should identify each final's ID, destination, canvas pixels, headline/body, ordered capture paths and hashes, placements, font files/families/weights, logo source, output SVG/PNG, app build, and relevant spec reference/date. Keep machine-specific device IDs and navigation recipes in capture provenance. Record excluded screens with reasons. Do not store credentials.

For creative assets also record placement type, universal versus dedicated, original artwork source/license, template URL/date and safe-area review. Capture paths can be empty for illustration-only creative art. Keep storefront mockups and template overlays in review, never upload folders. For video record duration, codec, frame rate, audio, poster timestamp, probe result and editable project; for Play record the intended YouTube URL/visibility when available. Keep locale and review/publication state explicit.

For CPP/PPO deliveries, group sources and finals by stable page/test/treatment identifier and locale so variants cannot overwrite the default set. Record inherited assets, ordered overrides, library IDs/hashes and compatibility. CPP needs audience/channel, URL, keyword and deep-link notes; PPO needs hypothesis, baseline snapshot, allocation, selected locales, decision criteria and measured results when available. Library management needs usage and processing/review/archive state. Create only the records required by the requested workflow; do not force screenshots or exports into a configuration-only task.

## SVG and typography

Declare integer `width`, `height` (unitless or `px`), and `viewBox="0 0 W H"`. Embed screenshots as base64 data images so SVGs don't break when moved. Preserve full image aspect ratio. Use real logo vectors, adequate padding, and correct stacking order. Keep master text editable and escape XML text/attributes.

Bundled font files alone do not make librsvg use them. Resolve/install the chosen fonts in the rendering environment (or configure Fontconfig), check exact family/weight matching, and render accented sample text. Browser support for embedded `@font-face` does not guarantee equivalent librsvg behavior. For reliable distribution, retain editable masters and optionally provide an outlined export copy, with the original fonts/licenses retained where redistribution is permitted. Do not silently swap typefaces.

Generate each canvas at its final pixel dimensions. For new dimensions, reflow the vector layout and proportionally place original screenshots; do not stretch a rendered PNG. SVG improves edges/text, but cannot add detail missing from a low-resolution capture. Pixel dimensions matter for upload; arbitrary DPI metadata does not increase quality.

## Included helper

`scripts/artwork.py` requires Python 3, `rsvg-convert` (librsvg), and ImageMagick 7 (`magick`) on PATH. On macOS these are commonly supplied by Homebrew's `librsvg` and `imagemagick`; use the environment's package manager only within installation permissions. Python uses its standard library. No AI image service or paid design application is required.

```bash
python3 artwork.py export source/phone/01.svg final/phone/01.png
python3 artwork.py check --size 1080x1920 final/phone/*.png
```

Export checks explicit SVG canvas dimensions/viewBox, renders at native canvas size, flattens on white by default (`--background '#112233'` to change), converts to 8-bit sRGB RGB PNG without alpha, validates full decoding and PNG structure, and emits JSON dimensions/SHA-256. Existing outputs require `--force`; failed rendering does not replace an existing output. `check` accepts only RGB 8-bit PNGs, checks optional exact dimensions, and never modifies them. The helper does not enforce store counts/policies, font identity, layout, provenance, or visual quality; the agent checks those against the recorded target.

The helper also handles creative PNG canvases, including Apple's universal size, when passed their exact dimensions. It does not select an upload slot, verify safe areas, validate JPEG or video, or prove store acceptance. Use a video probe plus playback review for videos; consult the platform reference before assigning a target.

For capture-only tablet deliveries, make a derivative with ImageMagick to normalize RGB/sRGB without resizing; retain the original under captures. Review every derivative too.

## QA and handoff

1. Verify every requested final exists, sequence matches the manifest, count fits its specific destination, and no alternatives or contact sheets are mixed in.
2. Run the helper against each device group's recorded dimensions. Check hashes preserve the originals and paths/assets resolve after moving the package or running from a different working directory.
3. Build contact sheets with a local tool such as ImageMagick montage; open them. Open each PNG at useful size and inspect suspicious details at 100%: missing glyphs, font fallback, clipped text, real UI, image sharpness, logo shape, borders, and loading/error states.
4. Compare paired slides and form factors for visual consistency without assuming identical layout. Review representative long copy and every distinct layout after shared changes. For creative artwork, inspect template safe areas and the actual console previews across placements, device classes and orientations. Record unavailable console access as unverified crop/placement behavior.
5. Deliver links to final directories, the editable source, and a preview. Summarize what was actually checked. Local checks do not prove a store has accepted uploads; state acceptance only after observing it. Upload/publish only when authorized.
