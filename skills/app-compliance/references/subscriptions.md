# Subscriptions

## Applicability and official sources

Sources consulted 2026-10-22; reopen at use time:

- [FTC negative-option rulemaking notice, March 2026](https://www.ftc.gov/news-events/news/press-releases/2026/03/ftc-seeks-public-comment-response-advance-notice-proposed-rulemaking-regarding-negative-option): describes the vacated 2024 rule and a new rulemaking. Do not cite the old “click-to-cancel” announcement as a current nationwide obligation. Verify the current rule, ROSCA and relevant state/local laws separately.
- [ROSCA, 15 USC §8403](https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title15-section8403): for covered Internet negative-option transactions, inspect material disclosures before obtaining billing information, express informed consent before charging and simple mechanisms to stop recurring charges. A complaint or press release is not a substitute for checking this statutory scope and current text.
- [California Business and Professions Code §17602](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17602.&lawCode=BPC): source for a California applicability check, not a universal checklist. Retrieval returned HTTP 403 during preparation; its current text and notice deadlines remain **Pending verification**. Obtain an accessible official legislative copy before applying specific requirements.
- Read current official billing-provider/store docs for the installed integration, including hosted cancellation portals, lifecycle events and test clocks where supported.

Determine operator/customer jurisdictions, consumer/business context, enrollment channel, contract dates, trials, renewal and billing model. Map applicable disclosure, acceptance, acknowledgment, renewal/trial/price-change notice and cancellation rules. Do not invent a notice schedule, refund policy or commercial terms from a generic checklist.

## Inspection and corrections

- Trace price/interval/currency, trial conversion, renewal, minimum commitment and cancellation terms from checkout through provider configuration and confirmation. Preserve evidence of the actual version accepted and when; avoid preselected or bundled acceptance where inappropriate.
- Verify confirmations and any applicable notices against actual renewal dates/time zones, trial end, price changes and scheduled jobs. Check delivery failures and idempotent scheduling; a template without a sender is incomplete.
- Trace cancellation from UI/API authentication and subscription ownership to the billing provider. Record whether it is immediate or at period end and the effective date. A local `canceled` flag, account deletion or hidden button does not stop provider charges.
- Handle multiple subscriptions, provider errors, retries, signed webhooks, duplicate/out-of-order events and reconciliation. Show success only after provider-confirmed cancellation or clearly label a pending request. Keep appropriate paid-period entitlements; do not turn a cancellation fix into an unrequested immediate cutoff.
- Reuse store/provider-managed subscription management when appropriate. Verify that it addresses the relevant subscription and actual customer ability to cancel.

## Technical verification

Use a sandbox and synthetic customers. Exercise enrollment, acceptance evidence, confirmation, applicable notices, cancellation and the next simulated renewal. Assert provider state and absence of future renewal charges, alongside access through the promised date. Test failures, retry, duplicate webhook, wrong-owner requests and already-canceled subscriptions. If provider access is unavailable, implement and test the integration against mocks, state that real provider cancellation is unverified and request the exact sandbox access needed.
