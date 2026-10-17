# Apple Product Page Optimization (PPO)

Verified 2026-10-17. PPO compares randomized treatments of the default product page. It is not available for [Custom Product Pages](apple-custom-product-pages.md), Apple Watch or iMessage product pages. It does not introduce new image dimensions.

## Choose the experiment

Record a concrete hypothesis, baseline assets, one main creative change, locales, primary conversion metric, treatment count, traffic allocation and decision rule. Prefer one treatment for low traffic instead of automatically filling three. Label these as experiment-design choices, not Apple requirements.

Apple's overview allows one active test, up to three treatments, and up to 90 days. The original receives traffic outside the experiment; treatment traffic is divided equally. Example: 40% allocated to two treatments means 20% each and 60% original, not 40% per treatment. Selected locales define eligibility. Users see the same treatment throughout the test on supported iOS/iPadOS 15+.

Sources: [PPO overview](https://developer.apple.com/app-store/product-page-optimization/), [Create a test](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/create-a-test/).

## Prepare and configure

In Apps → app → Product Page Optimization → Create Test (+ for another draft), name it, select treatments, traffic and locales, inspect Estimate Your Test Duration, then Create Test. The setup guide requires a live app with Ready for Distribution or Pre-Order Ready for Distribution status and Account Holder/Admin/App Manager/Marketing access. The duration estimate is guidance, not a promise of a conclusive result.

Source: [Create a test](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/create-a-test/).

Treatments inherit unchanged baseline items, including missing device-size screenshot/preview overrides. Name each treatment and configure App Icon, Header and Search Results, or App Previews and Screenshots. Reuse approved compatible assets through Browse Assets. Alternate icons must already be in the currently distributed app binary; uploading a PNG alone is insufficient. New metadata needs approval; reordering already approved screenshots/previews does not require resubmission.

Source: [Configure treatments](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/configure-test-treatments/).

## Run, measure and apply

Start Test launches an approved test or prompts review for pending metadata. Record the observed status; do not call review submission a running experiment. Stop Test cannot be resumed; a new test is needed. Results become available after five first-time downloads, which is a reporting threshold, not evidence of a winner. Source: [Run a test](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/run-a-test).

In Analytics → Acquisition → Product Pages → test, record date range, baseline, unique impressions, conversion, relative lift, confidence and status. At ≥90% confidence Apple can label Performing Better/Worse. Collecting Data and Likely to be Inconclusive do not establish equivalence. Report absolute conversion and relative lift separately. Source: [PPO Analytics](https://developer.apple.com/help/app-store-connect-analytics/acquisition/product-page-optimization).

Apply Treatment to Current Product Page changes selected versions and stops a running test; one treatment can be applied and the action cannot be undone. The application guide explicitly describes transferring screenshots/previews and requires a future app version to make an icon default. It does not explain Header/Search transfer despite those tabs being testable: inspect the current confirmation and verify resulting placements before claiming creative assets were applied. Source: [Apply a treatment](https://developer.apple.com/help/app-store-connect/create-product-page-optimization-tests/apply-a-test-treatment-to-your-product-page/).

**Documentation conflict:** the Analytics FAQ mentions simultaneous tests, descriptions and possible extension beyond 90 days, whereas the operational overview/setup documents one test and a 90-day limit. Follow the documented operational setup for planning, verify live console capability before promising exceptions, and disclose unresolved differences. Do not silently turn either page's FAQ into a capability guarantee.

Deliver the hypothesis/configuration, treatment-to-asset manifest, baseline snapshot, QA and review state, observed metrics and decision. Starting/stopping tests and applying treatments require authorization covering those actions; preparing assets alone does not provide it.
