# Session recording

## Applicability and official sources

Sources consulted 2026-10-22; reopen at use time:

- [ICO cookies and similar technologies](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/cookies-and-similar-technologies/): assess device storage/access, applicable consent and exceptions using the current detailed guidance linked there. “Analytics” is not evidence of an exemption.
- [CNIL session replay consultation](https://www.cnil.fr/en/session-replay-cnil-launches-public-consultation-its-draft-recommendation): the consulted page describes a draft and a consultation closed on 22 April 2026. Check whether a final recommendation has superseded it; do not present the draft as binding law.
- Open the actual vendor's official SDK, privacy/masking, consent, stop/reset, retention and deletion documentation for the installed version. Provider defaults and a marketing claim of anonymization do not establish the legal basis.

Identify applicable jurisdictions, recording purpose, data types, lawful basis, device-access rules and any distinct interception/communications-consent rules. Do not assert that one banner resolves every jurisdiction. Treat data minimization as an engineering objective while distinguishing it from verified legal duties.

## Inspection and corrections

- Trace initialization via application startup, tag managers, plugins, remote configuration and error-triggered replay. Determine whether “disabled” prevents collection, buffering and transmission or only hides playback in the dashboard.
- When prior consent is applicable, block collection before consent, including pre-consent buffers and server forwarding; do not merely postpone upload of already captured interactions. Integrate with existing consent state and revoke promptly across tabs/routes/background states. Handle stale consent and SDK startup races.
- Inspect organization/project settings as well as code: sampling, retention, region, access roles, exports, integrations and deletion. Mask/exclude authentication, payment, health, private messages and other sensitive views by default. Cover text nodes, inputs, dynamically inserted DOM/native views, URLs, query strings, network bodies, console logs and custom events. Keep useful non-sensitive diagnostics working.
- Do not assume `stop()` deletes existing sessions or clears every buffer. Verify the provider's distinct stop, reset and deletion semantics; ask for missing dashboard access while completing accessible code changes.

## Technical verification

Use synthetic sentinel values, never real secrets. Inspect storage, requests and accessible replay payloads during fresh launch, refusal, acceptance, navigation, revocation and reload. Test dynamic fields, error-triggered sessions and background resume. Confirm excluded content never leaves the device and revoked sessions do not resume through another loader. Where authorized, inspect sandbox playback/export and deletion. If payload encryption or dashboard access prevents inspection, state the precise verification limit rather than claiming masking succeeded.
