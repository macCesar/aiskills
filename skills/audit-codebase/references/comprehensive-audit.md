# Comprehensive technical audit — full method

Detailed guidance for stage 1 (audit) and the rules that govern both stages. The exact deliverable formats live in `report-format.md`.

## Objective

Detect real, verifiable problems in:

1. Implementation and functional logic.
2. Architecture and separation of responsibilities.
3. Security, authentication, and authorization.
4. Input validation and trust boundaries.
5. Database, integrity, and performance.
6. Files, uploads, paths, and storage.
7. Error handling, logs, and sensitive data.
8. Dependencies, configuration, and deployment.
9. Frontend, mobile client, or external integrations.
10. Tests, compatibility, and maintainability.

The result must let the user decide what to fix, what to keep, what to consciously postpone, and how to implement the changes without breaking valid use cases.

## Mandatory principles

### 1. Evidence before patterns

- Don't invent problems.
- Don't flag something as vulnerable just because it resembles a known pattern.
- Every finding must include concrete evidence: file, line, configuration, dependency, reproducible behavior, or tool output.
- If it can't be verified, mark it **Unverified**.
- Distinguish clearly between:
  - **Confirmed**: demonstrated in code or execution.
  - **Conditional risk**: depends on specific configuration or infrastructure.
  - **Unverified**: not enough data to conclude.

### 2. Proportional security, not absolute security

- "Secure by default" does not mean "forbid by default" without analyzing the product.
- Before recommending authentication, strict authorization, allowlists, tokens, route blocking, or removing compatibility, identify the current use cases that could break.
- Explicitly consider public, anonymous, multi-user, admin, API, temporary, and embedded flows when they exist in the project or its documentation.
- Don't impose registration/login if the product legitimately supports anonymous visitors.
- Prefer controls at the real boundary: signatures, opaque tokens, anonymous sessions, rate limiting, ownership, expiration, scopes, and context validation.
- Don't duplicate controls without justifying the benefit. If a signature already guarantees integrity, don't also add a mandatory manual record unless it mitigates a distinct, demonstrated risk.
- Every restrictive recommendation must include:
  1. The concrete risk it mitigates.
  2. The affected use cases.
  3. The least-restrictive alternative evaluated.
  4. A safe opt-in/opt-out mechanism, if applicable.
  5. The migration and compatibility impact.

### 3. Compatibility and existing behavior

- Review README, CHANGELOG, configuration, tests, examples, and recent history to identify public contracts and intentional behaviors.
- Build a list of existing capabilities before recommending changes.
- Don't silently remove or change a documented capability.
- Classify each change as:
  - Compatible.
  - Justified breaking change.
  - Avoidable breaking change.
- If a fix could break consumers, include a transition strategy, configuration, deprecation, or migration guide.
- Verify the real support matrix of the language, framework, database, and runtime versions.

### 4. Severity is not scope

- Severity indicates risk; it does not automatically decide whether something is implemented or ignored.
- Every confirmed finding — mediums and lows included — must receive an explicit disposition:
  - **Fix now**.
  - **Fix in a later phase**, with a reason and a follow-up condition.
  - **Consciously accept**, with technical justification.
  - **Won't fix**, because it isn't a real problem or the cost/risk outweighs the benefit.
- Don't use "optional", "tech debt", or "medium improvement" as a synonym for "won't be done".
- If the user asks to implement the full plan, include every finding whose fix is appropriate and proportionate, not just criticals and highs.
- Refactors are evaluated by benefit, risk, and available coverage; they are neither done automatically nor discarded automatically.

### 5. Minimal, complete, verifiable changes

- Prioritize small, safe changes, but don't leave a functional fix half done.
- Don't propose full rewrites without a demonstrated need.
- Don't add features unrelated to the problems found.
- Don't introduce abstractions without a concrete problem they solve.
- Don't do cosmetic cleanup during the fix phase unless it's needed to implement or verify the change.
- Every recommendation must state how to check that it works and that it caused no regressions.

## Technical scope

Review at minimum:

1. General architecture and folder structure.
2. Separation of responsibilities and coupling.
3. Modern framework conventions.
4. Main configuration and default values.
5. Direct, transitive, outdated, or vulnerable dependencies.
6. Public, private, web, API, and callback routes.
7. Authentication, sessions, tokens, and expiration.
8. Authorization, ownership, roles, policies, gates, and isolation between users.
9. Input validation, coercion, limits, and error messages.
10. Models, mass assignment, casts, relations, and events.
11. Migrations, indexes, cascades, constraints, and referential integrity.
12. Queries, N+1, transactions, concurrency, and partial operations.
13. Controllers, services, jobs, commands, and middleware.
14. Uploads, MIME, extensions, names, paths, disks, permissions, and cleanup.
15. Image/document processing and CPU/memory consumption.
16. Sensitive data in responses, logs, exceptions, and caches.
17. CSRF, CORS, rate limiting, headers, and signed URLs.
18. Frontend, CDN dependencies, CSP, integrity, and client-side error handling.
19. Build scripts, published assets, and install/update commands.
20. Production configuration and behavior behind proxies/CDNs.
21. Existing tests, practical coverage, and compatibility matrix.
22. Outdated documentation, examples, and public contracts.
23. Duplicated code, dead code, and accidental complexity.
24. Deployment, upgrade, and rollback risks.

Adapt the list to the real stack: a CLI has no CSRF, a library has no routes. Explicitly mark the areas that don't apply instead of silently omitting them, so the reader knows they were considered.

## Working method

### Phase 1: discovery

1. Identify the stack and real versions.
2. Review the repository instructions and Git state.
3. Inventory entrypoints, routes, models, migrations, services, views, and commands.
4. Read configuration, README, CHANGELOG, and examples to understand intent and compatibility.
5. Identify real actors and flows:
   - Anonymous visitor.
   - Authenticated user.
   - Resource owner.
   - Administrator.
   - API client or external service.
   - Internal processes and CLI.
6. Trace the critical flows end to end.

### Phase 2: verification

1. Run available tests, lint, static analysis, and audits.
2. Use dependency tools to verify real advisories.
3. Reproduce important bugs when it's safe.
4. Verify authorization with at least two users/tenants when it applies.
5. Verify positive and negative paths.
6. Review concurrency, rollback, and cleanup in operations that touch DB + filesystem.
7. Check every claim against evidence before reporting it.

### Phase 3: diagnosis, no modifications

- The first deliverable is diagnosis and plan only.
- Don't modify the project tree during this phase — not just source files, but any generated artifact (compiled bytecode/`__pycache__`, caches, `node_modules`, lockfiles, coverage output). Verification tools that write into the tree as a side effect (`py_compile`, test runners, bundlers, `npm install`) must be run with their output redirected outside the project, or skipped and recorded as unverified with the reason.
- If a critical finding needs immediate attention, report it first, but continue the full audit.
- Don't stop the analysis after finding critical problems.

### Phase 4: decide before implementing

Before modifying code, present a **decision matrix** with all confirmed findings (format in `report-format.md`).

Don't start changes until the decisions are clear for anything that alters public behavior, authentication, compatibility, schema, dependencies, or API.

Ask only about product decisions that can't be inferred from the repository. Don't ask for data that can be investigated locally.

### Phase 5: authorized implementation

When the user authorizes implementation:

1. Implement the full approved matrix, not just the highest-severity findings.
2. If a contradiction with an existing use case appears, stop and present it before applying a restriction.
3. Keep or add regression tests for every affected behavior.
4. Update configuration, documentation, examples, and CHANGELOG when a contract changes.
5. Run all verifications again.
6. Review the full diff and confirm there are no out-of-scope changes.
7. Explicitly list any finding not implemented and the approved reason for leaving it pending.

## Severity classification

### Critical

- Provable unauthorized access, modification, or deletion.
- Direct exposure of secrets or highly sensitive data.
- Code execution, server or database compromise.
- Data loss or breakage of an essential flow.

### High

- Serious permissions, validation, integrity, or logic problem.
- Can cause partial data loss, inconsistencies, or major failures.
- Vulnerable dependency exploitable in the project's real context.
- Must be resolved before production unless explicitly and justifiably accepted.

### Medium

- Real performance, maintainability, compatibility, or incomplete-validation problem.
- Faulty build, migration, cache, or operational process with a workaround available.
- Must receive an explicit decision and is normally included in stabilization.

### Low

- Confirmed minor inconsistency or defect.
- Its fix is small or can be grouped with related work.
- Must not be ignored automatically; weigh cost against benefit.

### Informational

- Verified correct behavior.
- Unconfirmed risk or preventive recommendation with no current defect.
- Requires no change unless a conscious decision is made.

## Rules for recommendations

- Be actionable and specific.
- Include the file and the suggested change when possible.
- Recommend one concrete option, but explain the real tradeoffs.
- Don't present a restrictive policy as the only solution if a safer, more flexible alternative exists.
- Don't turn product decisions into technical assumptions.
- Don't recommend allowlists, mandatory authentication, or endpoint removal without demonstrating why signatures, scopes, tokens, ownership, or rate limiting aren't enough.
- If a fix is breaking, include migration and compatibility.
- If you decide not to fix something, justify why and what future signal would force a reconsideration.

## Communication rules

- Be direct, no filler.
- Don't explain basic framework concepts.
- Don't list irrelevant theoretical possibilities.
- Separate facts, inferences, and decisions.
- Acknowledge uncertainty and contradictions.
- Don't declare the audit or implementation "complete" if any findings lack an explicit disposition.
