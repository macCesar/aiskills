# Children and age

## Applicability and official sources

Sources consulted 2026-10-22; reopen at use time:

- [Current COPPA Rule, 16 CFR Part 312](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312), especially §§312.2–312.5, 312.8 and 312.10: assess child-directed or mixed-audience services, actual knowledge, personal information, consent, security and retention. Do not treat a general-audience service as child-directed merely because children could visit it.
- [FTC COPPA FAQs](https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions), especially general-audience/teen services and third-party collection. The page warns that the rule was amended in 2025; use the current rule over outdated FAQ wording. Check current compliance dates and enforcement statements rather than reusing historical deadlines.
- [ICO Children's code](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/): assess the UK's separate likely-to-be-accessed-by-children scope. US age thresholds are not universal; consult the relevant local law for other markets.

First establish the intended and actual audience, markets, features, data collected and any knowledge of underage users. No registration does not mean no personal-data collection. Do not prescribe birth-date collection, identity documents or an account ban before evaluating necessity, proportionality and the applicable rule. Age assurance itself can introduce additional data processing.

## Inspection and corrections

- Trace the first launch/page load through analytics, advertising, crash reporting, replay, push, location, cookies, identifiers, IP/access logs, uploads and backend events. Inspect vendor settings and transitive SDKs before any age/consent UI appears.
- Examine neutral age screening if appropriate, parental notice and verifiable consent where required, server enforcement, parent access/deletion, retention schedules and processor deletion. A checkbox saying “I am 13” is not evidence of parental consent.
- Prefer existing privacy-preserving modes, minimal age bands and delayed nonessential collection where these satisfy the verified requirements. Preserve public/general-audience access unless a supported restriction is needed. Do not silently repurpose a user's profile birthday as permission for unrelated processing.

## Technical verification

Use fresh storage/install and synthetic identities. Capture outbound requests and storage before interaction, after an applicable age/consent decision, after refusal and after deletion. Exercise direct API calls, deep links and background startup, not only the onboarding view. Confirm restricted identifiers never reach vendors prematurely; test consent/access/deletion paths and document any unavailable vendor evidence. For a general-audience site without accounts, report the audience/data-flow evidence and remaining unknowns before proposing any age gate.
