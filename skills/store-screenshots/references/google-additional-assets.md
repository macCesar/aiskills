# Google icons, device-specific assets, Play Shorts and AI provenance

Verified 2026-10-17. These are conditional destinations, not requirements for every phone app. Read the relevant section before producing or reusing files. Keep the normal [listing guidance](google-play.md) separate from event/promotional media.

## Icons, banners and additional device types

| Target | Published requirements / applicability |
| --- | --- |
| Play listing icon | 512 × 512, 32-bit PNG with alpha, ≤1024 KB; separate from the app's launcher/adaptive icon |
| Android TV listing banner | 1280 × 720, JPEG or 24-bit PNG without alpha; required for TV-enabled apps, shown on TV |
| Wear OS | At least one current screenshot, 1:1 and ≥384 × 384; UI only, no frames, extra text/background, transparency or masking |
| Android Automotive | Category-dependent; when supplied, at least two 800 × 1280 portrait and two 1024 × 768 landscape; use generic system/OEM-neutral UI |
| Android XR | 4–8 PNG/JPEG screenshots, ≤8 MB each, 8:5; minimum 1920 × 1200, recommended 3840 × 2400 |

Source: [Google preview asset specifications](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en).

Reopen the actual device section for watch faces, TV screenshots, Automotive categories or XR-specific video/thumbnail options before export. Do not turn the TV banner into a phone Header requirement, apply phone screenshot bounds to XR/large screens, or make an Android screenshot by resizing an iPhone capture. For Wear/watch faces preserve only the actual experience; the listing may need multiple configurations.

For the Play icon use the full square artwork; Google applies its mask and shadow, so do not bake them in. Keep original vectors/layers and review recognition at small size. Consult [icon design specifications](https://developer.android.com/distribute/google-play/resources/icon-design-specifications). The bundled `artwork.py` exports/checks opaque RGB PNGs: **it is not a compliant alpha-preserving Play-icon exporter/validator**. Use an appropriate image tool, inspect actual bit depth/color/alpha, decode the file and check dimensions/bytes without silently flattening it. Native launcher/icon-catalog work needs the app's own build workflow.

## Play Shorts

Current access is limited to selected partners and availability to the US; verify eligibility in the actual console before promising reach. Play Shorts is a direct-video workflow, separate from the normal listing's YouTube URL. From Grow users → Store presence → Play Shorts, upload files, choose audio/subtitle language metadata and finish. New uploads go through Play Console, not Drive; older Drive submissions were migrated.

Track two checks separately: raw-file verification (Processing / Processing failed) and ingestion review (In review / Rejected / Live / Unpublished). A successful upload is not a live Short. Unpublish from its asset entry when authorized; Google notes serving can take 2–3 days to stop. Delete is available for videos never live. Do not invent pixel dimensions, codecs or runtime from YouTube preview rules: inspect the current Short uploader's requirements before encoding and record the evidence.

Source: [Manage Play Shorts](https://support.google.com/googleplay/android-developer/answer/17165227?hl=en).

## AI-generated or edited assets

Google documents an asset-specific self-declaration flow for AI-generated/edited visual assets in listings, promotional content and videos under applicable circumstances. Inspect the current declaration checkbox in creation flows or asset details; declared assets may display an AI label on Google Play and other surfaces. Do not assume one declaration covers the entire app, or silently check/uncheck it on the user's behalf without confirming the asset's actual provenance and applicable instructions.

Record which images/video elements were generated or edited, the source/tool, human edits, rights and observed declaration state. Keep real app captures distinguishable from concept art. The source does not resolve every regulatory edge case; if applicability is unclear, state that specific uncertainty rather than inventing an exemption or blanket claim that every editor operation needs a label. Preparing the record does not authorize submission/publication.

Source: [Declaring AI-generated content in Play Console](https://support.google.com/googleplay/android-developer/answer/17262077?hl=en).
