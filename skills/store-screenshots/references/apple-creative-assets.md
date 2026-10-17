# Apple Header and Search Results creative assets

Verified 2026-10-17. Recheck the linked documentation and the app's actual console before production. These are optional creative placements for iOS/iPadOS 27 and later, separate from screenshots, App Previews, paid ads, and editorial artwork. They do not remove screenshot requirements.

## Image upload targets

| Destination | Apple's ratio label | Width × height | Formats |
| --- | --- | --- | --- |
| Dedicated product page Header | 21:9 | 3840 × 1646 | JPEG/JPG/PNG |
| Dedicated Search Results | 3:2 | 1920 × 1280 minimum; 3840 × 2560 maximum | JPEG/JPG/PNG |
| Universal image, usable in both | 16:9 | 5244 × 2950 | PNG only |

No alpha channels or transparency. Use the literal pixel sizes: the labeled 21:9 and universal 16:9 ratios have rounding, so do not reject these official dimensions with an exact ratio test. For dedicated search artwork, 3840 × 2560 is a useful production choice at the published maximum, not an extra requirement. The universal file is a distinct upload option; an arbitrary 16:9 image is not equivalent.

Source: [Creative assets specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications).

## Compose for real placements

Use an illustration, photo, branded composition, or authentic app content relevant to what the app offers. Header can establish mood; search should make the experience understandable immediately. Keep a clear focal point and avoid dense detail. Keep key subjects centrally composed, localize text, and avoid prices, URLs, other-store logos, unsupported awards, and Apple editorial recognitions. Assets must be suitable for a 4+ audience. If search creative is omitted, Apple uses In-App Events, App Previews, and screenshots.

Source: [Asset best practices](https://developer.apple.com/app-store/asset-best-practices/).

Use Apple's current safe-area layers, not a guessed percentage or a crop measured from someone else's phone preview:

| Template | Official link |
| --- | --- |
| Header Photoshop | [Header template](https://developer.apple.com/go/?id=photoshop-product-page-header-template) |
| Search Photoshop | [Search template](https://developer.apple.com/go/?id=photoshop-search-results-template) |
| Universal Photoshop | [Universal template](https://developer.apple.com/go/?id=photoshop-universal-asset-template) |

Figma, Pixelmator, and Sketch options are linked on the best-practices page. On the verification date, the downloaded PSD headers confirmed 3840 × 1646, 3840 × 2560, and 5244 × 2950 respectively. Safe-area geometry was not extracted in this reference; open the template for the chosen destination before making numeric safe-area claims. Keep guides in a review layer, exclude them from final exports, and retain the template URL/date in provenance. Link to Apple's templates instead of redistributing their files without checking terms.

For universal art, test both placements. Inspect the actual App Store Connect Preview for iPhone and iPad, both orientations, and each supplied language. Check subject recognition, text, navigation overlays and cropping. A standalone 16:9 thumbnail does not prove the Header is composed correctly. If the image cannot survive both placements, use dedicated compositions. For a scene with a player ship and a large enemy, position the essential silhouettes inside the template's safe area and allow scenery to bleed; do not infer that both subjects remain visible from a wide desktop preview alone. This is composition advice, not an Apple pixel-margin specification.

## Video is a separate deliverable

Dedicated Header video: 3840 × 1646. Search video: 3:2, from 1920 × 1280 to 3840 × 2560. Both allow 5–30 seconds, 30 or 60 fps, MOV/M4V/MP4. They loop; search audio cannot be unmuted, while Header audio can. The published video table does not list the 5244 × 2950 universal-image option: do not assume universal video support or apply App Preview encodings automatically. The creative-image/video tables do not specify a byte-size cap for these placements; do not borrow the In-App Event or App Preview cap. Check the actual uploader/API if needed.

Source: [Creative assets specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications).

## Console workflow and verification

In the app version, open Product Page Information → Header and Search Results → choose placement → drag in an asset or Browse Assets → Save. Only universal assets offer **Use header asset in search results**. Preview both destinations before submission.

[Asset Library](apple-asset-library.md) supports standalone review once an approved app version exists; first-release assets must accompany the first app submission. Approval alone does not select a placement. For a live version, choose an approved asset with Browse Assets → Next → Publish; a new app version is not required for this path. For a new version, creative assets go live with its approved release. Perform upload, submission, and publishing only within the user's authorization; document observed review/placement state separately from local file validation.

Source: [Manage your App Store assets](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets).

For audience-specific creative, read [Custom Product Pages](apple-custom-product-pages.md); for controlled tests of the default page, read [Product Page Optimization](apple-product-page-optimization.md). Configure assets in the correct page/treatment context and inspect its Preview; library reuse does not make every page identical.
