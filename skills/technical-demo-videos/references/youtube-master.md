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
- AAC audio at 48 kHz;
- the moov atom at the front (`faststart`);
- a deliberate delivery bitrate. Use 35 Mbps for 4K30 and 53 Mbps for 4K60
  unless current official YouTube guidance changes.

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
