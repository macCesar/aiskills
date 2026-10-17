# Apple Custom Product Pages (CPP)

Verified 2026-10-17. Use CPP for an audience, feature or campaign destination with its own URL. Use [Product Page Optimization](apple-product-page-optimization.md) for randomized tests of the default page; CPP performance comparisons alone do not establish a causal conversion lift.

## Capabilities and eligibility

Apple currently allows up to 70 additional pages for iPhone/iPad. Pages support localized screenshots, previews, promotional text and keyword assignments; creative assets can also be used. CPP works on iOS/iPadOS 15+, with optional app deep links on 18+. Keep creative OS availability and pixel requirements in [apple-creative-assets.md](apple-creative-assets.md), and screenshot/video targets in [apple-media.md](apple-media.md); CPP does not define a new image size.

Source: [Custom product pages overview](https://developer.apple.com/app-store/custom-product-pages/), [creative asset usage](https://developer.apple.com/app-store/asset-best-practices/).

## Prepare and configure

1. Record audience, acquisition channel, specific benefit, locales, asset sequence and destination inside the app. Keep campaign copy and the first screenshot consistent with the referring message. Reuse existing real captures when they demonstrate the benefit; do not invent app functionality.
2. In Apps → app → Custom Product Pages → Create Custom Product Page (or +), name the page and start blank or copy an existing page. The setup guide requires Ready for Distribution in at least one region. Account Holder, Admin, App Manager or Marketing can configure it; inspect actual eligibility if preparing a pre-order page.
3. Add the localized assets and promotional text. Browse Assets reuses approved compatible resources from [Asset Library](apple-asset-library.md). Preview the correct page/device/locale; select Header/Search creative in that page's context rather than assuming default-page changes propagate.
4. Record the automatically generated URL and page identifier. For organic search, assign keywords from the latest approved version per localization, with a unique relevant set per page. Searchability requires approval and visibility; keyword publication is a separate action from saving a draft.
5. If requested, set and test the app deep link. Universal links or custom URLs are supported; the deep link must be reviewed. Do not promise deferred navigation after a fresh installation merely because tapping Open can deep-link an installed app.

Source: [Configure multiple product page versions](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions/).

## Review, lifecycle and measurement

Submit CPP metadata for review independently of an app update when authorized. Editing an approved page creates a new version, keeps its URL, and publishes the replacement automatically after approval. Disabling/deleting redirects its URL to the default page; deletion is permanent. Record these consequences before carrying out an authorized change. Sources: [configuration and lifecycle](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions/), [independent review and analytics](https://developer.apple.com/app-store/custom-product-pages/).

Deliver a page brief, locale-to-asset map, approved-copy sources, URL/deep-link notes, observed status and QA results. Measure impressions, downloads and conversion in Analytics; CPP metrics appear after five first-time downloads. Compare matching periods and acquisition sources; different audience intent can explain differences. Never report projected gains as observed results. [Source: configuration guide](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions/).
