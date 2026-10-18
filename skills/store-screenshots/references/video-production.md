# Store video production and verification

Read the actual slot's dated requirements first: [Apple creative video](apple-creative-assets.md), [App Previews](apple-media.md), [Google preview video](google-play.md), or [event media](promotion-and-events.md). This is a file-based production workflow, not authorization to record, submit or publish. Capture and encode sequentially on constrained machines.

## Prepare and capture

1. Identify placement, locale, intended duration, orientation, app build, demo state, feature/access claims, soundtrack rights and final dimensions. Keep a brief shot list with a clear opening, real functionality and ending/loop. Do not fill an App Preview with rendered concept art or use a generic trailer for an event-specific asset.
2. Record native app footage using the available platform capture workflow. Inspect a short sample first. For an iOS Simulator, inspect `xcrun simctl io UDID recordVideo --help`; start its recorder and stop it with its supported interrupt so the movie is finalized. Other platforms need their actual recorder/tool, not a renamed screenshot. Preserve the native file unchanged. Do not start recording without authorization covering it.
3. Inspect metadata, rotation, sample aspect ratio, timing, audio and sharpness. Select complete action, no debug/loading overlays, notifications or private information. Retain original captures and an edit list of in/out points; an editor project or exact commands must reproduce the cut.
4. Compose for the upload target: crop only when all important content survives, otherwise contain on a designed background. Check HUD/menus and text in every shot. Keep square-pixel output, but normalize anamorphic/HDR sources deliberately instead of merely relabeling them. Native resolution, composition size and export size are separate. Upscaling cannot restore missing detail.

## Reproducible FFmpeg examples

Requires installed `ffmpeg`/`ffprobe` with `libx264`. These recipes assume a square-pixel SDR source named `capture.mov`, already in the correct orientation and at least 15 seconds long. They are starting points, not universal store presets. Check encoder availability/help before use. `-n` protects existing outputs. Thread limits keep the examples suitable for the sequential workflow; run one command at a time.

**Silent Header, center crop, 12 seconds.** H.264/CRF/preset here are production choices; Apple's creative-video table specifies dimensions, fps, duration and extensions, not an App Preview bitrate/profile requirement.

```bash
ffmpeg -hide_banner -n -threads 1 -filter_threads 1 -i capture.mov -t 12 -map 0:v:0 -vf "scale=3840:1646:force_original_aspect_ratio=increase:force_divisible_by=2,crop=3840:1646,setsar=1,fps=30" -an -c:v libx264 -threads 1 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart header.mp4
```

To preserve the entire source instead, use this filter in the same command and choose a different output filename. The color is a review placeholder; choose appropriate branded composition after visual inspection, not automatic black bars:

```text
scale=3840:1646:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=3840:1646:(ow-iw)/2:(oh-ih)/2:color=0x102030,setsar=1,fps=30
```

**Landscape modern-iPhone App Preview, 15 seconds.** This uses that slot's 1920 × 886 target, H.264 High Level 4.0 and an 11 Mbps target bitrate. Optional source audio is encoded as AAC stereo 256 kbps/48 kHz. Check rights and actual audio content first. This is a separate output from Header, not a way to upload Header video as a preview.

```bash
ffmpeg -hide_banner -n -threads 1 -filter_threads 1 -i capture.mov -t 15 -map 0:v:0 -map '0:a:0?' -vf "scale=1920:886:force_original_aspect_ratio=increase:force_divisible_by=2,crop=1920:886,setsar=1,fps=30" -c:v libx264 -threads 1 -preset medium -profile:v high -level:v 4.0 -b:v 11M -maxrate 12M -bufsize 24M -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart app-preview.mp4
```

For other targets recompose from original captures and select the matching specifications; do not stretch this export. For Google, also verify the published YouTube video/URL and cover surface. A local encode or YouTube autoplay duration does not establish listing compliance.

Filter semantics: [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) (`scale`, `crop`, `pad`, `setsar`, `fps`), also discoverable using `ffmpeg -h filter=NAME`. Encoder behavior is inspectable with `ffmpeg -h encoder=libx264`. The commands were smoke-tested locally; live store review remains separate.

## Technical and visual QA

Probe every final, not just the original:

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,profile,level,width,height,sample_aspect_ratio,avg_frame_rate,pix_fmt,sample_rate,channels,bit_rate -of json header.mp4
ffmpeg -hide_banner -v error -xerror -threads 1 -i header.mp4 -f null -
```

Repeat for the preview. Compare actual duration (short input truncates `-t`), codec/profile/level, pixel dimensions, square-pixel display, fps, byte size and audio to the recorded slot. A nominal fps conversion can duplicate/drop frames; it does not improve native motion. Decode success does not validate policy, content, crop or poster.

Watch every final with sound and muted: inspect motion, sharpness, clipping, readable/localized overlays, claims, unexpected black frames, soundtrack transitions and the join between loop iterations. A normal cut does not automatically make a seamless loop. If the join is distracting, select a better interval or edit an appropriate transition and recheck; do not conceal missing functionality with fabricated footage. Choose the representative poster in the console where supported, then inspect the actual storefront Preview.

Deliver raw captures, edit list/project, exact commands/tool versions, output hashes, probe/decode results, rights/provenance, poster timestamp and visual QA. Keep publication state separate from local verification. Do not claim full production capability when a necessary recorder/editor/encoder is unavailable; finish the brief and available preparation, then identify the specific blocker.
