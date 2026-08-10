# Section: Video Embedding in Slots

## Purpose

Sometimes a Stitch slot needs to show a video instead of a still image (product demo, animated logo, looping background, recorded screen). This document captures the exact pattern that works across browsers and avoids the common pitfalls — content recropping, layout shift, AV1 codec, and aspect-ratio mismatch with the original wrapper.

## The Tag

Use a plain `<video>` element with native `width` and `height` attributes plus inline styling for safe defaults:

```html
<video
  autoplay
  muted
  loop
  playsinline
  width="W"
  height="H"
  preload="metadata"
  style="display:block;width:100%;height:auto;background:#000">
  <source src="../videos/<slug>.mp4" type="video/mp4">
</video>
```

Replace `W` / `H` with the **native** video dimensions and `<slug>` with the screen slug (or whatever filename you used inside `videos/`).

### Why each attribute

| Attribute | Why |
|-----------|-----|
| `autoplay muted loop playsinline` | All four are required for in-app autoplay on iOS and Android. Drop any one and mobile browsers refuse to play without a tap. |
| Native `width` / `height` | Lets the browser compute the aspect ratio from the very first paint — prevents layout shift and CLS regressions. |
| `preload="metadata"` | Loads just enough to know the dimensions and duration; avoids hammering the user's bandwidth when the screen is offscreen. |
| `style="display:block"` | Removes the small descender gap inline videos otherwise get. |
| `style="width:100%;height:auto"` | Scales the video to fit the parent column while keeping its native aspect ratio. **Do NOT use `object-cover`** — it crops the video. |
| `background:#000` | Hides letterboxing during the brief moment before the first frame paints. |

## File Workflow

1. **Download** the source video. For Facebook/Instagram/YouTube/TikTok we recommend `yt-dlp`:

   ```bash
   yt-dlp "https://www.facebook.com/<...>/videos/<id>" -o "videos/<slug>.%(ext)s"
   ```

2. **Re-encode to H.264** if the source comes down as AV1. AV1 doesn't preview in macOS Finder and is rejected by Safari < 17:

   ```bash
   ffmpeg -i in.mp4 \
     -c:v libx264 -preset fast -crf 23 \
     -c:a aac \
     -movflags +faststart \
     videos/<slug>.mp4
   ```

   - `-preset fast`: balanced speed/quality.
   - `-crf 23`: visually-lossless default; lower number = bigger file.
   - `-movflags +faststart`: moves the moov atom to the front so the video can start playing before fully downloaded.

3. **Place** the encoded `.mp4` in a `videos/` folder at the **project level** (the same level as `stitch/` or `showcase/`, not inside `assets/`), so the build keeps it out of the screen-extraction pipeline:

   ```text
   my-project/
   ├── stitch/                 ← Stitch exports (zips)
   ├── videos/                 ← your videos
   │   └── hero.mp4
   └── showcase/               ← generated
       └── assets/
           └── <slug>.html     ← references ../../videos/hero.mp4
   ```

4. **Reference from the screen HTML** with a relative path. From inside `showcase/assets/<slug>.html`, `videos/` is two levels up:

   ```html
   <source src="../../videos/hero.mp4" type="video/mp4">
   ```

## Aspect-Ratio Mismatch

The original Stitch wrapper for a video slot usually carries a fixed aspect ratio (e.g. `aspect-[4/5]`). If your video is a different shape — say 9/16 — keeping the wrapper's aspect locks the video into the wrong box, which then forces a choice:

| Option | Effect |
|--------|--------|
| Keep wrapper's `aspect-*` + `object-cover` | Video crops; logos and edges get chopped. |
| **Remove wrapper's `aspect-*` + `height:auto`** | Video keeps its native aspect; the slot grows or shrinks vertically to fit. ✅ |

The second option is almost always what you want — better to have a slightly taller card than to chop the brand logo out of the frame.

## Quick Sanity Checks

After embedding, open the screen in a browser and confirm:

- The video autoplays without a tap on Chrome, Safari, and Firefox.
- The video loops cleanly (no flash on rewind).
- On mobile (iOS Safari), it autoplays silently inline (not fullscreen).
- The file size is reasonable — re-encode with a higher `-crf` if it's more than ~3-5 MB per 10 seconds.
