---
name: app-compliance
description: 'Use when reviewing or fixing app controls for children and age, external fonts, session recording, marketing email, recurring subscriptions, or user content and DMCA notices. Applies across web, mobile, and backend stacks; does not provide a complete legal audit.'
---

# App Compliance

Identify and correct technical controls in the six areas below. Respond in the user's language. This is a scoped engineering workflow, not a certification of legal compliance or an exhaustive audit of a jurisdiction.

## Required workflow

Open only the references relevant to the request or discovered behavior before reporting findings or editing:

| Topic or evidence | Reference |
| --- | --- |
| Children, age checks, parental consent, SDK collection | [Children and age](references/children-and-age.md) |
| External font stylesheets, files, themes or embeds | [Fonts and third parties](references/fonts-and-third-parties.md) |
| Session replay, heatmaps, interaction recording | [Session recording](references/session-recording.md) |
| Campaigns, newsletters, unsubscribe, sender identity | [Marketing email](references/marketing-email.md) |
| Trials, recurring charges, renewal, cancellation | [Subscriptions](references/subscriptions.md) |
| User uploads, copyright notices, DMCA agent | [User content and DMCA](references/user-content-dmca.md) |

1. **Discover existing behavior.** Inspect the stack, entry points, providers, configuration, policies and tests. Follow indirect integrations, tag managers, native SDK startup, background jobs and provider dashboards where accessible. Reuse existing controls. Distinguish existing features from future plans; do not build an unrequested subsystem just to satisfy a checklist. Complete new wiring needed by an authorized correction when the architecture and authority are available; otherwise identify the exact missing dependency. Ask only for facts that the project and available tools cannot establish.
2. **Establish applicability.** Record operator and user jurisdictions, audience, activity, data flows and the relevant effective dates. Open current official laws/regulations, regulator guidance and provider documentation for the actual integration/version. The dated links in references are starting points, not evergreen authority. Distinguish binding rules, guidance, drafts, contractual provider rules and engineering recommendations. Check amendments, enforcement policies, court decisions and territorial reach before asserting an obligation. Do not infer jurisdiction from a language, domain or hosting region alone. If a source cannot be checked, mark the legal claim **Pending verification**; continue work supported by independent evidence and existing authorization.
3. **Show findings before editing.** For each finding provide `file:line` where available (otherwise the dashboard/configuration location), observed evidence, applicability and its factual basis, current official source URL/section and access date, proposed correction, effect on legitimate use cases and planned verification. Classify it as **Confirmed**, **Conditional**, **Pending verification**, or **Not applicable**. Cite the consulted local guide as `[source: references/<file>.md]` as well as the official source supporting legal/provider claims. Use `FROM_MEMORY (unverified):` for an unconsulted claim; it cannot establish an obligation.
4. **Follow the requested mode.** For review-only requests, deliver the diagnosis and proposed actions without modifications. For requests to fix or implement, present the findings as a progress update and continue within existing authorization; do not impose a second generic approval checkpoint. Ask only for an unresolved product choice, missing fact/access or an external action requiring authority not already granted. A request for technical fixes is not itself permission to submit a registration or spend money.
5. **Implement and verify.** Complete all authorized corrections, preserving legitimate product functions. Verify actual data flow and provider state, not just UI text. Use focused regression tests and runtime/network checks proportional to the change. Never use real sensitive data in recordings, send real campaigns, charge customers or file real notices as a test. Report source-only checks separately from sandbox and live verification.

## Completion and blockers

Do not invent legal identities, postal addresses, designated agents, jurisdictions, consent, commercial terms or business policies. Drafts with unresolved values must remain clearly marked and outside active sends, checkout disclosures and public legal pages. Do not hide a missing control behind reassuring copy.

When blocked, ask for the precise missing datum, access, decision or authorization as soon as it is detected. Explain why it is needed and what is prepared. Continue independent authorized work while waiting. Do not stop at recommendations when implementation was requested; complete accessible provider configuration and external procedures too when tools, access and authorization suffice. Bound retries: after two failed attempts at the same external mutation, stop retrying that operation, capture the error without secrets and continue independent work.

Deliver changes by file (or findings only in review mode), checks executed and results, applicability still unverified, and each concrete blocker with the prepared work and next required input. Never claim full compliance from these six checks or mark untested provider behavior as fixed.
