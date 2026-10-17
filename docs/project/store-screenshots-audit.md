# Store screenshots audit — 2026-10-17

Scope: skill entry point, all three original references, exporter, existing tests, Codex sidecar, README discovery, and current Apple/Google requirements. User-supplied storefront previews motivated crop review; they were not treated as original upload files or evidence of source-image dimensions.

## Findings and corrections

| Finding | Impact | Correction |
| --- | --- | --- |
| Header/Search/universal creative assets absent | Wrong dimensions or rejection of legitimate illustration artwork | New `apple-creative-assets.md`: exact upload sizes/formats, templates, distinct video requirements, review/placement workflow |
| Entry point excluded all video previews | Requests for specifications could fail to activate the skill | Trigger now covers video specification/checking; production remains an appropriate recording/editing workflow |
| Screenshots and artwork treated as one deliverable | Real-UI constraints could be applied to optional creative illustrations | Explicit asset-type selection, separate capture/art provenance and output folders |
| No concrete Apple media reference | Remembered device sizes could substitute for actual accepted slots | New `apple-media.md`: current required slots, selected accepted sizes, preview encodings and poster/probe checks |
| Play feature graphic missing | A required listing asset could be omitted | New `google-play.md`: 1024 × 500 graphic, cutoff diagrams, video cover usage |
| Play publication and promotion criteria not enumerated | Agents could confuse 2 required captures with 3/4 promotion criteria or apply phone limits to tablets | Separate baseline, recommendation eligibility and large-screen sections; flag differing published bounds |
| Optional device-frame advice applied broadly | Android listing artwork could conflict with Google's recommendations | Qualify frame advice by destination; prefer unframed Android captures |
| No required reference/output contract | Unsupported recalled values could look verified | Routing table, source citations, verification dates and explicit unverified fallback |
| Helper capabilities easy to overstate | RGB/dimension checks could be mistaken for store approval or video validation | Keep helper unchanged; explicitly document JPEG/video/safe-area/console limitations |

## Evidence

- [Apple creative specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications): dedicated Header 3840 × 1646; Search 1920 × 1280–3840 × 2560; universal image 5244 × 2950 PNG; no alpha. Creative video allows 5–30 seconds at 30/60 fps.
- [Apple best practices](https://developer.apple.com/app-store/asset-best-practices/): placement-specific creative guidance and downloadable safe-area templates. Read PSD headers through the page's official Photoshop download links: Header 3840 × 1646, Search 3840 × 2560, universal 5244 × 2950. Did not infer numeric safe areas from the screenshots or extract PSD layer geometry.
- [Manage assets](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets): optional creative placements on iOS/iPadOS 27+, universal reuse, console Preview, standalone review, and approved-asset updates to live versions.
- [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications) and [App Preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications): separate upload tables and video constraints. The screenshot page has both a current required-device summary and older fallback notes; the skill now calls out the need to inspect the actual slot when ambiguous.
- [Google preview assets](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en): feature graphic, screenshots, device-specific exceptions, promotion recommendations and YouTube video requirements. [Android device art guidance](https://developer.android.com/distribute/marketing-tools/device-art-generator) recommends screenshots without framing for listings.

## Verification and limits

- `npm test`: 179 passed, 0 failed, 0 skipped; includes real SVG rendering, RGB/no-alpha checks, dimension mismatch, corrupt-image rejection and overwrite protection.
- Skill Creator `quick_validate.py`: passed using a temporary venv with PyYAML; no project dependencies changed.
- Export/check smoke run passed with temporary plain-color SVGs at 3840 × 1646, 3840 × 2560, 5244 × 2950, and 1024 × 500; each decoded as RGB at its exact size. This verifies exporter compatibility, not actual artwork quality or store acceptance.
- All 13 relative Markdown reference links resolve. `npm pack --dry-run --json` includes all three new platform references. `git diff --check` passed.
- Existing exporter inspected through the knowledge graph; no implementation defect requiring a code change was identified within this task. No shared CLI machinery changed, so no TiTools port is needed.
- No new app captures, full video production, live console upload, store review, or independent assistant evaluation was performed. Safe-area placement still requires opening the current template and reviewing the actual app in console Preview.
- Changes are recorded under Unreleased and committed as `60b8b02` (`feat(store-screenshots): cover Apple creative assets and Play listing requirements`); session documentation is committed separately at the user's request. No tag, push, npm release or marketplace version change was requested or performed.
