# Apple listing text

Checked 2026-10-30. Recheck official rules and the selected app state before applying.

| Field | Limit / behavior |
| --- | --- |
| Name / subtitle | 30 characters each; changes depend on version state |
| Promotional text | 170 characters; editable without a new app version; appears above the description |
| Description | 4,000 characters; plain text; update with a new version |
| Keywords | 100 bytes in the App Store Connect reference; check UTF-8 length and console validation |

Promotional text does not influence App Store search ranking. Use it to explain a current benefit, not as a keyword list. Keywords should describe the app; avoid duplicating its name, irrelevant terms and competitor names. Do not transfer Google's short-description field to Apple as though it were identical.

Check both locale content and whether the actual field is editable. An approved version and its next draft are different records. Saving promotional text does not update the full description. Record the save and verify public propagation separately.

Sources:

- [Apple product-page guidance](https://developer.apple.com/app-store/product-page/): name, subtitle, description, promotional text and search.
- [Platform version information](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information/): field limits, keyword bytes and localized version properties.
- [Editable properties](https://developer.apple.com/help/app-store-connect/reference/app-information/required-localizable-and-editable-properties/): editability by property/state.

## Choose the page tool

| Tool | Use when | Decision/evidence to carry forward |
| --- | --- | --- |
| Custom Product Pages | Different audiences, features or campaigns need different presentations | Audience/message, locales, destination URL and source-matched outcomes; different audiences alone do not make a randomized test |
| Product Page Optimization | A hypothesis about the default page needs a controlled comparison | Baseline/treatment, eligible assets/locales, expected traffic and meaningful result criteria |
| Asset Library | Existing approved resources can be reused or organized | Compatible resource, intended placement and observed review/public state; uploading a resource does not publish a page |

Read `store-screenshots` and its corresponding Apple CPP, PPO or Asset Library reference before configuration. Check live eligibility and testable fields; do not assume that text, keywords or every creative slot can be randomized. Choose these tools from the diagnosed problem, not a “New” label. With very low traffic, first estimate whether a test can answer the question.

Current official starting points: [Custom Product Pages](https://developer.apple.com/app-store/custom-product-pages/), [Product Page Optimization](https://developer.apple.com/app-store/product-page-optimization/), [Asset Library](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets).
