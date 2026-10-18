# Google Play Store listing experiments

Verified 2026-10-17 against [Run A/B tests on your store listing](https://support.google.com/googleplay/android-developer/answer/12053285?hl=en). Reopen current console setup before configuring. Experiments work on published default **and custom** listings, unlike Apple's CPP/PPO restriction.

## Select and prepare

| Mode | Audience and editable assets |
| --- | --- |
| Default graphics | Default-language icon, feature graphic and screenshots; viewers with localized graphic assets are excluded |
| Localized | Selected languages; icon, feature graphic, screenshots and descriptions |

The current guide permits one default graphics experiment or up to five localized experiments simultaneously, and up to **two variants** per experiment. Do not import Apple's three treatments, 90-day limit or confidence assumptions. Keep production of assets sequential when the workstation requires it; remote experiment concurrency is a separate concept.

Define a hypothesis, listing/locale, current assets as control, one main changed asset, target metric and decision criteria. Preserve capture authenticity and text/graphics consistency. Use the actual listing's [specifications](google-play.md); experiments do not create new dimensions. Record library IDs and group inheritance so preparing variants cannot overwrite shared defaults.

## Configure, review and run

In Grow users → Store presence → Store listings, choose Set up in the listing's Experiment column (or its Details page). If unavailable, follow the console's readiness requirements rather than assuming eligibility. Enter a reference name (≤50 characters), mode/languages and target metric: unique-user install, open or pre-registration clicks.

Inspect the estimated sample/time calculator. Advanced settings control up to two variants, total experimental audience share, minimum detectable effect and confidence. Prefer defaults unless the task gives a reason to change them. Allocation is divided equally: 40% across two variants gives 20% each and 60% control. Localized assets alter eligible traffic, so do not forecast from total app visits alone.

Next, choose the asset, supply variants, review and Save; submit changes via publishing overview when authorized. Saving/review submission is not proof the experiment is running. Record its observed state, configuration, timestamps and the current control.

Source: [Setup and eligibility](https://support.google.com/googleplay/android-developer/answer/12053285?hl=en).

## Interpret and apply

Use Store listings → Experiments, the listing's Experiment cell or Details page to open results. Record target metric, exposure/sample evidence, interval, minimum detectable effect, elapsed dates and recommended action. More data needed is not a losing variant; Draw is not proof of identical underlying behavior. Keep conversion percentages and relative change distinct. Do not choose a winner from a higher point estimate without the console's result context.

When supported by evidence and authorized, apply the chosen variant or Keep current listing. Record what actually changed. Experiments auto-complete after six months, return traffic to the current listing and do **not** automatically apply a variant. Do not call an expired experiment a published winner.

Source: [Results, metrics and autocompletion](https://support.google.com/googleplay/android-developer/answer/12053285?hl=en).

Google recommends testing one asset at a time and covering at least a week to account for weekday/weekend differences; this is not a guarantee of enough data. Low traffic may require a more focused hypothesis or fewer variants rather than repeated restarts. [Experiment best practices](https://play.google.com/console/about/store-listing-experiments/).

Deliver the brief, variant/control manifest, locale and targeting rationale, configuration, review/running state, actual results and decision. Without console access, prepare the variants and configuration and mark execution/results unverified. Do not fabricate data or automatically launch/apply tests merely because assets are ready.
