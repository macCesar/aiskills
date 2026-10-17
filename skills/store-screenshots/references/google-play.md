# Google Play listing assets

Verified 2026-10-17 against [Google's preview asset requirements and recommendations](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en). Reopen its device-specific sections and the actual Play Console before export.

## Upload requirements versus promotion

| Destination | Requirements |
| --- | --- |
| Feature graphic | Required; 1024 × 500; JPEG or 24-bit PNG without alpha |
| General screenshots | At least 2 across supported device types; up to 8 per type; JPEG or 24-bit PNG without alpha; each dimension 320–3840; longest at most twice shortest |
| Large-screen section (tablet/Chromebook) | Specifies minimum 4 captures; 1080–7680 px; 16:9 landscape or 9:16 portrait; no added text outside the core app experience |

The large-screen section differs from the general limits. Record the precise slot's rules rather than rejecting every image over 3840 or applying 7680 to phones. Google labels additional screenshot conditions for recommendation eligibility: apps need four, games three, at 16:9 ≥1920 × 1080 or 9:16 ≥1080 × 1920. These are distinct from baseline publication requirements.

Play uses feature graphics, screenshots and previews on several surfaces, including search. Its documented listing workflow does not define separate Apple-style Header and Search Results upload slots. Recompose the same brand source for the 1024 × 500 graphic; do not resize/stretch an Apple universal image into it. The feature graphic can serve as the preview-video cover, so review central play-button overlap, edge cropping, and focal-point placement using Google's linked cutoff-zone diagrams. Do not invent fixed safe margins.

Keep Android UI authentic. For phone screenshot overlays, Google's recommendation is ≤20% tagline area. Avoid rankings, promotional claims, store badges, and device imagery; localize overlay text and supply useful alt text (recommended ≤140 characters). Large-screen uploads should use the app experience without added promotional text. Do not extrapolate phone templates to Wear, TV, Automotive or XR; their separate requirements are in the same official page.

Source for the table and content guidance: [Play Console Help](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en). For device frames, see also [Android's device art generator warning](https://developer.android.com/distribute/marketing-tools/device-art-generator): it recommends unframed screenshots for store listings.

## Preview video

The normal listing takes one YouTube video URL (not a channel/playlist, without timecode parameters). Video must be public or unlisted, embeddable, without ads, and not age restricted. A local MP4 alone is not the submitted asset. The feature graphic provides the cover/play surface. Google may autoplay up to the first 30 seconds muted; that is not a 30-second maximum upload duration.

Recommendations: show real use/gameplay within the first 10 seconds, with at least 80% representing the user experience; support silent viewing. Choose the app's orientation, localize when useful, and keep branding intros brief. XR has separate additional video options; consult those only when requested.

Source: [Preview video requirements and recommendations](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en#preview_video).

## Delivery and console review

Use Grow users → Store presence → Main store listing → Graphics for the chosen device type and locale. Keep feature graphic, screenshots and video URL/poster notes as separate manifest entries. Inspect the rendered listing, not only individual files. Record acceptance/review state only when observed. Preparing files does not authorize publishing a listing or uploading a public YouTube video.
