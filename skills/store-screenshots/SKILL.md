---
name: store-screenshots
description: Use when creating, selecting, capturing, redesigning, or exporting App Store or Google Play screenshots and editable SVG templates. Covers real Android/iOS captures and store artwork tailored to an app's branding. Also triggers on “capturas para las tiendas”, “pantallas de Play Store”, or “plantillas de screenshots”. Not for app UI implementation, video previews, or unrelated slide decks.
---

# Store screenshots

Produce a coherent store series from real app screens, with editable SVG masters and reproducible PNG exports. Work with ordinary files and command-line tools so Claude Code, Codex, and other agents can use the same sources. An image-generation service is optional for decorative artwork; never require one or use it to redraw the app UI.

## Establish the deliverable

Inspect existing artwork, app UI, brand assets, project instructions, and the requested release before choosing a direction. Reuse an accepted direction and existing generators when appropriate. Discover similar skills before replacing an established workflow.

Resolve platform, upload slot/device class, locale, app orientation, mandatory sections, and whether the request is selection, one sample, or the complete series. Infer what the project makes clear; ask only for missing decisions that block the work. A request for one sample is not authorization to regenerate all designs.

Read [design.md](references/design.md) for selection, messaging, typography, and composition. Propose a small set of meaningfully different directions if none is established, recommend one, and produce a representative sample. If no user approval is required, inspect the sample and continue within the authorized scope. Honor explicit review checkpoints.

Read [delivery.md](references/delivery.md) before setting canvas dimensions. Verify current official requirements for the actual destination; do not confuse native capture resolution, accepted upload sizes, and featuring recommendations. Use the real app's orientation, never an orientation inherited from another project.

## Capture and compose

Read [capture.md](references/capture.md) when obtaining new screenshots. Capture each platform's real UI. An iPhone capture does not become Android artwork by changing its dimensions or frame. Tablets need the actual tablet layout.

Number final slides in reading order. Name captures sharing a slide with subnumbers (`06`, `07.1`, `07.2`). Keep required screens; group related benefits only when both remain legible. Store a mapping of slide → source captures → copy, including exclusions and the reason for them.

Build SVGs with explicit pixel dimensions and a matching viewBox. Keep text editable, logos authentic, and screenshot pixels intact. Use proportional placement, embedded screenshots, and licensed local fonts. Adapt composition to each form factor rather than stretching a phone design to a tablet.

Use the bundled helper where useful:

```bash
python3 scripts/artwork.py export slide.svg slide.png
python3 scripts/artwork.py check --size 1080x1920 slide.png
```

Paths above are relative to this skill. The size is an example, not a store requirement. Read [delivery.md](references/delivery.md) for dependencies, portable font handling, packaging, validation, and helper limits.

## Finish criteria

- All requested sections and platforms accounted for; no unreviewed loading, blank, clipped, stale, or incorrect screens passed off as final.
- Each final matches its recorded destination dimensions, format, count, and content rules.
- Open rendered PNGs: inspect the entire contact sheet, each slide at useful size, and suspect details at 100%. XML validity and matching dimensions do not prove visual quality.
- Export commands, fonts/licenses, sources, capture provenance, and final sequence are reproducible from the delivered package.
- Report actual validation and missing access separately. Do not claim store acceptance or successful device capture unless observed. Store upload, publication, and unrelated app fixes need their own authorization.
