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

## Apple and Google workflow counterparts

| Goal | Apple | Google Play |
| --- | --- | --- |
| Audience/campaign landing page | Custom Product Pages | Custom store listings (fichas personalizadas) |
| Find and reuse graphics | Asset Library | Asset Library (biblioteca de recursos) |
| Randomized creative comparison | Product Page Optimization | Store listing experiments |

These are functional counterparts, not interchangeable configurations. Never transfer page limits, targeting, inheritance, approval or experiment rules between stores.

### Custom store listings

Google supports country, URL, ads, keyword and user-segment targeting subject to app eligibility. Listings can customize name, icon, descriptions and graphics; contact details, privacy policy and category are shared. They do not receive automatic translations. Country targeting is not language targeting, and a targeted listing is not an A/B test.

In Grow users → Store presence → Custom store listings, create new, duplicate an existing listing, or create within a group. Duplication copies assets; group membership inherits assets and group updates can affect member listings. Record group/inheritance and individual overrides before editing shared resources. Select targeting, default language/translations, text and graphics; preview and record the review/publication state. Use the console-generated URL with its `listing` parameter, not Apple's CPP identifier.

The user's Spanish console exposes Fichas de Play Store → Crear una ficha de Play Store personalizada. Follow the actual console labels when menus differ from the English guide; this is the same Custom store listings workflow, not a separate asset type.

Source: [Custom store listings and groups](https://support.google.com/googleplay/android-developer/answer/9867158?hl=en).

### Google Asset Library

Add assets in a graphics section opens a side panel for main/custom listings, experiments and events. It supports Upload and Add from Drive, filename/tag search and filters for ratio, language, type and usage. A ratio mismatch can open a crop tool; Save as copy preserves the original. Preserve that derivative's source/crop provenance and inspect text/UI clipping; a crop suggestion is not permission to substitute iOS captures for Android UI. Ready-to-use/crop filters describe asset fit, not Apple-style App Review approval. Do not assume Google's library implements Apple's standalone review or archive lifecycle.

Source: [Manage graphics with Asset Library](https://support.google.com/googleplay/android-developer/answer/16386748?hl=en).

For Google's experiment counterpart, read [google-experiments.md](google-experiments.md): it covers configuration, review, metrics and applying results for default/custom listings. Apple's treatment count, runtime and confidence rules do not apply automatically.

For icons, TV banners, Wear/Automotive/XR, Play Shorts and per-asset AI declarations, read [google-additional-assets.md](google-additional-assets.md). For Promotional Content, use [promotion-and-events.md](promotion-and-events.md). Their rules differ from ordinary phone listing assets, including video orientation and graphic text/alpha requirements. Preview videos should also be localized and captioned where useful; avoid black side bars around portrait video, keep muted-playback copy legible, and check the full official preview guide before final delivery.
