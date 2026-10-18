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
- Initial pass: all 13 relative Markdown reference links resolved. `npm pack --dry-run --json` included the three initial platform references. `git diff --check` passed.
- Existing exporter inspected through the knowledge graph; no implementation defect requiring a code change was identified within this task. No shared CLI machinery changed, so no TiTools port is needed.
- No new app captures, full video production, live console upload, store review, or independent assistant evaluation was performed. Safe-area placement still requires opening the current template and reviewing the actual app in console Preview.
- Changes are recorded under Unreleased and committed as `60b8b02` (`feat(store-screenshots): cover Apple creative assets and Play listing requirements`); session documentation is committed separately at the user's request. No tag, push, npm release or marketplace version change was requested or performed.

## Follow-up: page workflows and Google equivalents

The user identified missing Apple CPP/PPO workflows and partial Asset Library coverage, then asked how they compare with Google custom listings and its resource library. Implemented as `f0b6030` (`feat(store-screenshots): add page workflows and asset library guidance`).

- Added three focused Apple references for audience/campaign pages, library reuse/review/lifecycle, and randomized default-page testing. Required routing, triggers, delivery manifests, README and Codex metadata now cover them.
- Added Google custom listings, group inheritance, library search/filter/crop/reuse and an Apple/Google counterpart table. Google's Store listing experiments is identified and linked, not presented as a complete operational guide.
- Clarified that CPP is not a PPO treatment, five downloads is a reporting threshold rather than proof of a winner, approval is separate from placement, and copying a listing differs from inheriting group assets.
- Recorded conflicts between Apple's operational PPO instructions and its Analytics FAQ. The skill does not promise simultaneous tests, duration extensions, description tests or automatic Header/Search treatment transfer without checking actual capability.

Sources verified on 2026-10-17:

- [Apple CPP setup/lifecycle](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions/) and [CPP overview](https://developer.apple.com/app-store/custom-product-pages/).
- [Apple asset management](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets) and [standalone submission constraints](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-assets-from-asset-library).
- [PPO creation](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/create-a-test/), [treatments](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/configure-test-treatments/), [run/stop](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/run-a-test), [Analytics](https://developer.apple.com/help/app-store-connect-analytics/acquisition/product-page-optimization), and [application limits](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/apply-a-test-treatment-to-your-product-page/).
- [Google custom listings/groups](https://support.google.com/googleplay/android-developer/answer/9867158?hl=en), [Asset Library](https://support.google.com/googleplay/android-developer/answer/16386748?hl=en), and [Store listing experiments](https://play.google.com/console/about/store-listing-experiments/). The canonical library request failed once; its indexed English regional URL returned the official full article.

Follow-up checks: 179 tests passed, none failed/skipped; Skill Creator validator passed; all 29 relative links resolve; npm pack dry run includes all nine reference guides. This is reference/configuration guidance: no live page, library, group or experiment was changed, and no statistical outcome or independent assistant evaluation is claimed.

## Follow-up: constrained capture workstations

The user reported that a project indexer processing large SVGs consumed more than three CPU cores while iPad control stalled, and requested sequential execution on machines such as an M1 with 16 GB RAM. The entry point now requires one virtual device total and one heavy job at a time on constrained machines, with serial device transitions, SVG generation, PNG export and contact sheets. Capture/export references carry the same policy. Temporary project-indexing pauses preserve their prior state, cover the heavy pipeline, and are restored at completion/interrupted handoff without persistent configuration changes. This is a workflow rule, not a claim that a specific chip cannot handle parallel work.

Verification: existing 179 tests pass; no code/helper changed. No local performance benchmark or process-control experiment was performed; the operational incident is user-provided evidence.

## Follow-up: remaining asset coverage implemented

`17b3204` closes the gaps identified in the subsequent documentation review. Four references were added: video-production, google-experiments, promotion-and-events, and google-additional-assets. The entry point routes all four; README/metadata and delivery guidance match. No shared CLI/helper implementation changed.

- Apple: explicit status/action table, Accepted versus Approved, configurable unreviewed assets, screenshot majority per device/localization, App Preview rights/access disclosures and additional-platform routing.
- Video: native capture/edit/export/QA workflow, separate Header/App Preview recipes, cover/contain composition and reproducible probe/decode commands. Commands were verified against installed FFmpeg help, then executed with FFmpeg 9.0.2.
- Google: full default/custom listing experiment setup/results/application; icon versus launcher artwork and alpha handling; TV/Wear/Automotive/XR asset requirements; Spanish console labels; conditional Play Shorts eligibility, upload/status/unpublish behavior; per-asset AI provenance/declaration handling.
- Events: Apple card/details media and event configuration; Google Promotional Content images/Lottie/video, differing safe areas, eligibility, copy and schedule constraints. Conditional features are not claimed available to every app.

New primary sources include [Apple asset statuses](https://developer.apple.com/help/app-store-connect/reference/app-information/app-store-asset-statuses), [screenshot review guidance](https://developer.apple.com/help/app-review/guideline-reference/2-3-3-screenshots/), [App Preview creative guidance](https://developer.apple.com/app-store/app-previews/), [event media/audio](https://developer.apple.com/help/app-store-connect/reference/in-app-events/in-app-event-media-and-audio-specifications), [Google experiment setup](https://support.google.com/googleplay/android-developer/answer/12053285?hl=en), [promotional content](https://support.google.com/googleplay/android-developer/answer/12929944?hl=en), [Play Shorts](https://support.google.com/googleplay/android-developer/answer/17165227?hl=en) and [AI declarations](https://support.google.com/googleplay/android-developer/answer/17262077?hl=en). Each reference carries its own source links and verification date.

Verification: 179 tests passed, 0 failed/skipped; Skill Creator validator passed; all 58 relative links resolve; npm pack includes all 13 references. Sequential smoke tests used temporary synthetic footage: Header crop and contain outputs at 3840 × 1646/12 seconds/30 fps/H.264, and App Preview at 1920 × 886/15 seconds/30 fps/H.264 High Level 4.0 with AAC stereo/48 kHz. Dimension, duration, fps, codec/profile/audio assertions and full decode passed. No real app capture, visual-quality verdict on gameplay, store acceptance, live console operation or independent assistant evaluation is claimed.
