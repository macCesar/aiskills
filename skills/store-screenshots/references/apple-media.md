# Apple screenshots and App Previews

Verified 2026-10-17. Read the live tables for the requested display target; this is a focused iPhone/iPad reference, not a replacement for all platform tables.

## Screenshots

Apple accepts 1–10 screenshots per device size, JPEG/JPG/PNG, without transparency or alpha. Current required sizes are iPhone with Dynamic Island (medium display), and iPad 13-inch if the app supports iPadOS. Do not carry forward the old assumption that the largest iPhone slot alone is always sufficient. The live table also retains some older fallback requirements: verify the actual console when fallback behavior and required slots are unclear.

| Target | Accepted portrait width × height | Landscape |
| --- | --- | --- |
| Dynamic Island, medium | 1179 × 2556; 1206 × 2622 | Reverse width/height |
| Dynamic Island, large | 1260 × 2736; 1290 × 2796; 1320 × 2868 | Reverse width/height |
| Face ID, large | 1284 × 2778; 1242 × 2688 | Reverse width/height |
| iPad 13-inch | 2064 × 2752; 2048 × 2732 | Reverse width/height |

These are accepted choices, not a mandate to export every listed size. Capture the correct device UI; use scaling only where Apple permits it and the UI matches. Native simulator pixels, screenshot upload pixels, and video upload pixels are different concepts. For other displays/platforms and upcoming device requirements, consult the full table rather than inventing a universal preset.

Source: [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications).

Screenshots must show the app in use. Creative artwork belongs to its own slot; it must not replace all screenshot content. Keep the real UI legible when composing captions. App Previews use captured app footage; do not present concept art or generated animation as real gameplay.

Sources: [Creating your product page](https://developer.apple.com/app-store/product-page/), [App Previews guidance](https://developer.apple.com/app-store/app-previews/).

## App Preview video requirements

Optional, up to three per supported device size and language. Duration 15–30 seconds; maximum 500 MB; maximum 30 fps. H.264: MOV/M4V/MP4, progressive, up to High Profile Level 4.0, target 10–12 Mbps. ProRes 422 HQ: MOV, progressive, approximately 220 Mbps VBR. For H.264 audio use stereo AAC 256 kbps, 44.1 or 48 kHz; inspect the official table for ProRes audio and track layout. These are App Preview specs, not Header/Search creative-video specs.

| Target | Accepted portrait | Accepted landscape |
| --- | --- | --- |
| Modern Face ID / Dynamic Island iPhone | 886 × 1920 | 1920 × 886 |
| iPad 13-inch | 1200 × 1600 | 1600 × 1200 |

Other targets have their own entries. A native-resolution screenshot is not a video encoding preset. Choose a representative poster frame; default is second 5. Processing can take up to 24 hours. Previews precede screenshots; a different aspect ratio moves a preview to “A Closer Look”.

Source: [App preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications).

## Validate video independently

For an existing file, inspect it with an available media probe, for example:

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,avg_frame_rate,pix_fmt,sample_rate,channels,bit_rate -of json preview.mp4
```

Compare dimensions, duration, frame rate, codec/profile, byte size, and audio to the actual slot. Watch the whole file, inspect the chosen poster, and check muted playback. Probe metadata alone cannot establish content compliance or a clean loop. The PNG helper does not encode or validate video. Keep the editable video project and original captures when producing videos; use an available recording/editing workflow rather than pretending an SVG export creates a preview.
