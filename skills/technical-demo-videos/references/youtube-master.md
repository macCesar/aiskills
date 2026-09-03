# YouTube master quality gate

Read this before promoting an approved edit to `<slug>-final.mp4` or creating
its YouTube upload manifest.

An MP4 can report 3840×2160 and still be a poor delivery master. Do not treat
resolution or successful muxing as sufficient. A stream-copied synchronization
preview remains a preview.

For horizontal 4K screen demonstrations using an approved capture profile, create
the final upload master with:

- MP4, H.264 High Profile, progressive, yuv420p;
- 3840×2160 with no baked-in letterboxing;
- constant 30 FPS unless the approved content genuinely needs its native 60 FPS;
- BT.709 primaries, transfer, and matrix metadata;
- AAC stereo audio at 48 kHz and 384 kbps;
- the moov atom at the front (`faststart`);
- a deliberate variable bitrate. The bundled helper uses the lower edge of
  YouTube's current SDR upload ranges: 35 Mbps for 4K at 24–30 FPS and 53 Mbps
  for 4K at 48–60 FPS. It also selects the documented standard/high-frame-rate
  defaults for 1440p, 1080p, and 720p.

These bitrate and codec recommendations can change. Before creating a delivery
master, verify them against YouTube's current official
[recommended upload encoding settings](https://support.google.com/youtube/answer/1722171).
If the published range changed, pass its lower bound with `--video-bitrate` and
record the source and chosen value in the production plan.

Run:

```bash
python3 scripts/normalize_youtube_master.py APPROVED_EDIT.mp4 FINAL.mp4
```

The tool refuses to overwrite the output and verifies resolution, CFR, codec,
profile, pixel format, BT.709, audio, container, and bitrate before completing.
Do not create an upload manifest when this gate fails.

After upload, keep the video private until the intended high-resolution
representations are actually available. YouTube chooses the playback codecs;
the upload API cannot request AVC, VP9, or AV1 and offers no reprocess action.
