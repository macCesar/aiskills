# Marketing email

## Applicability and official sources

Sources consulted 2026-10-22; reopen at use time:

- [FTC CAN-SPAM business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): assess the primary purpose of commercial versus transactional messages, including mixed content and B2B email. Where applicable, verify truthful headers/subjects, ad identification, a real valid physical postal address and accessible opt-out. The guide specifies keeping the mechanism working for at least 30 days after sending and honoring requests within 10 business days; prefer immediate suppression technically. It recognizes qualifying postal/private mailboxes as well as street addresses.
- [ICO electronic mail marketing rules](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/how-do-we-comply-with-the-pecr-electronic-mail-marketing-rules/): assess subscriber type, solicited/unsolicited messages, consent or a fully satisfied soft opt-in. This differs from the US framework; do not apply CAN-SPAM as a worldwide permission to send. Consult local official sources for other recipient markets.

Classify real templates and sending purposes before editing. Password resets, receipts and security alerts need separate treatment from promotional campaigns; adding a promotion can change the analysis. An account signup is not automatic evidence of marketing permission.

## Inspection and corrections

- Trace every sender: app jobs, scheduled campaigns, ESP automations, CRM, imports and manual exports. Inspect actual HTML/plain-text templates, From/Reply-To, footer, preference pages and subscription records.
- Reuse the project's verified legal identity and mailing address. If absent, request the real eligible address immediately. Prepare a configurable footer and validation in the campaign path so incomplete campaigns cannot be sent; do not publish an invented address or stop essential transactional messages unnecessarily.
- Make opt-out usable without login, payment or needless personal data. Protect preference endpoints from enumeration and unauthorized changes using appropriate opaque tokens. Distinguish safe link inspection from an intentional unsubscribe; implement provider-required one-click mechanisms according to current official provider docs.
- Persist suppression and apply it at the actual delivery boundary, not just in UI preferences. Reconcile ESP lists, queues, retries, automations and reimports. Keep minimal suppression evidence so a deletion or import does not silently re-subscribe someone. Re-subscription requires the relevant verified basis.

## Technical verification

Render representative HTML/plain-text messages. With sandbox recipients/provider mocks, unsubscribe and attempt subsequent campaigns through all senders, including already queued messages, retry and import paths. Confirm suppression survives restart and duplicate events, unauthorized tokens fail, and necessary transactional sends still work. Without ESP access, complete app-side protections and report the outstanding provider reconciliation explicitly. Do not send real campaigns to prove a fix.
