# Measure the path to active use

## Keep a metric ledger

For every material number, retain store/report, metric label, value/unit, dates, filters, user/device basis, cohort and comparison period. Record missing or rounded data. Download badges such as 10K+ and 500K+ are thresholds, not exact counts; an Installed badge is not evidence of zero downloads.

Separate impressions, listing visitors, install clicks, completed acquisitions, first opens, installed base and monthly active devices. Use the provider's current definition. A day-7 retained-device count is not a retention percentage; calculating a rate needs the matching eligible cohort. New-user, returning-user and secondary-device counts answer different questions. Do not join mismatched report denominators or dates into a funnel.

Interpret low downloads by locating the measured gap: little reach, weak listing response, acquisition/opening differences or low return use. Reviews and quality signals help choose investigations, not establish causality. Regional/device-weighted ratings can differ from an aggregate console score. Read review text as well as stars and identify small samples.

## Read the relevant dashboards

Checked 2026-10-30. Open current definitions for the selected report; labels and availability evolve.

- **Apple:** Analytics Acquisition/Sources for impressions, product-page views and downloads by source/territory; Engagement/usage and retention for return use, sessions, active devices, deletions and crashes. The standard Conversion Rate uses total downloads and pre-orders divided by unique-device impressions, not product-page views. A separately calculated downloads/page-view ratio needs its own name and a compatible denominator. First-time downloads and redownloads are distinct. See [acquisition](https://developer.apple.com/help/app-store-connect-analytics/acquisition/acquisition) and [metric definitions](https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions).
- **Google:** Grow users/Statistics for acquisitions/activity, listing conversion analysis for visitors and unique button clicks, Android vitals for crashes/ANRs/performance and review analysis for feedback. Different reports can measure different stages. Use [statistics/report definitions](https://support.google.com/googleplay/android-developer/answer/139628) and [listing definitions](https://support.google.com/googleplay/android-developer/answer/9859173). Current Play guidance also exposes additional retention days beyond day 7; inspect the available cohorts rather than limiting the analysis to one day. [Current Play changes](https://google.play/business/whats-new/).
- **Coverage:** Apple usage reflects analytics opt-in; inspect its history before interpreting a trend. Capture suppression, limited-data labels, missing periods, reporting delays and timezone when shown. Do not extrapolate opt-in observations to the full installed population without a defensible method. [Apple usage/coverage](https://developer.apple.com/help/app-store-connect-analytics/engagement/app-usage).
- **Benchmarks:** use a relevant peer group and matching country/context, identify which percentile/comparator is shown, and report differences as percentage points versus relative percent correctly. A peer gap is a lead to investigate, not a universal target or proof of cause. [Google peer groups](https://support.google.com/googleplay/android-developer/answer/10771707).

## Choose an intervention

This is diagnostic guidance, not a promise that a metric proves its cause. Compare within segments; an aggregate decline can come from more low-intent traffic even when each segment is unchanged.

| Observed pattern | Investigate first | Candidate action / measure |
| --- | --- | --- |
| Little discovery; reasonable response among visitors | Source mix, relevant queries, locales and campaign reach | Improve targeting/discoverability; measure qualified visits and downstream acquisitions |
| Visitors arrive but response trails a comparable baseline/peer | Message fit, localized copy, first screenshot and credible feature promise | Focused copy/media hypothesis; measure the relevant platform response rate |
| Click intent and acquisitions/first opens differ | Compatible reporting definitions, install completion, eligibility, device/version issues | Align the reports before diagnosing a technical or onboarding problem |
| Downloads rise but return use weakens | Matched retention cohorts, first experience, quality signals and review themes | Investigate product experience; protect retention/quality while increasing acquisition |
| Usage changes after a release | Version/device/OS segments, opt-in coverage and crash/ANR trends | Investigate a regression or measurement change; do not attribute it to store copy alone |

For an app-behavior question, distinguish “opened/returned/crashed” from “used coloring/saved a drawing/completed a sector”. The latter needs existing events, user testing or another authorized source. Avoid inventing per-feature behavior from store totals. Store sales/proceeds and advertising income are also different sources; inspect the applicable revenue system only within access/scope.

Deliver a short prioritized set of decisions. For each retain: evidence and segment, hypothesis/confidence, exact proposed change, primary metric, guardrail (such as return use or crashes), test/comparison and when to reassess. Low-volume apps may need a longer window or qualitative research instead of several simultaneous variants. Do not set an arbitrary universal conversion/retention threshold.

## Attribute and compare

Use store-supported campaign links or source/campaign dimensions when available. Keep language, country and creative identifiable. A post's views or likes do not prove store visits or downloads. Identify missing click data explicitly. Do not conclude that a channel fails from a handful of installs.

Compare the same report and filters before/after the public change, using equivalent windows and noting release, campaign and seasonal changes. A 28-day window is often useful, not a mandatory rule. With very low traffic, report uncertainty instead of declaring a winning variant. For controlled tests/custom pages, use `store-screenshots` rather than inventing experiment rules. A console recommendation is a hypothesis until measured.

## Proportional scenarios

For a requested estimate, show the arithmetic directly and state the assumptions once. If current downloads are D, monthly active devices A and monthly income R, a proportional scenario at target downloads T is:

- active devices: T × A / D;
- income per active device: R / A;
- monthly income: (T × A / D) × (R / A) = T × R / D.

These are the same extrapolation; introducing active devices does not change the result when their share and monetization are held constant. Label user-provided income, its currency and period separately from verified console metrics. If the period is missing, calculate conditionally and identify the missing period without silently assuming monthly income. Ratios of current activity to lifetime downloads are scenario inputs, not cohort retention rates. Do not infer another app's earnings from its public download badge or authorize ad spend from this estimate.

Additional guidance: [Apple Analytics overview and optimization tools](https://developer.apple.com/app-store-connect/analytics/), [Google listing experiments](https://support.google.com/googleplay/android-developer/answer/12053285). Use the experiment methodology in `store-screenshots` when planning randomized variants; a before/after observation alone does not establish causal lift.
