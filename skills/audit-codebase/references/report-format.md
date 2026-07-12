# Deliverable formats

Exact structures for the deliverables of both stages. Always use these templates: a stable format lets audits be compared across projects and guarantees that no finding is left without a disposition.

## Stage 1 deliverable: diagnosis

### 1. Executive summary

- Overall state.
- Overall risk: Low / Medium / High / Critical.
- Top five priorities.
- Existing capabilities that must be preserved.
- What is well implemented.
- What blocks production.
- What could not be verified.

### 2. Findings table

Each finding includes:

- ID (stable, e.g. `F-01`; the matrix and plan reference it).
- Status: Confirmed / Conditional risk / Unverified.
- Severity: Critical / High / Medium / Low / Informational.
- Area (security, DB, files, performance, etc.).
- File and line.
- Problem.
- Evidence.
- Real impact.
- Affected actors and use cases.
- Concrete recommendation.
- Least-restrictive alternative evaluated.
- Compatibility and regression risk.
- Acceptance test.
- Proposed disposition.

With few findings, a wide table works; with many, use a summary table (ID, severity, area, problem, disposition) followed by one card per finding with the remaining fields.

### 3. Special sections

Include separate sections for:

- Security.
- Database.
- Files and storage.
- Performance.
- Code quality.
- Frontend/build/assets.
- Dependencies and compatibility.
- Tests.
- Production and deployment.

If an area doesn't apply to the stack (e.g. database in a pure library), state it in one line instead of omitting the section.

### 4. Decision matrix

Include **all** confirmed findings, regardless of severity. None may be implicitly discarded.

| ID  | Finding | Severity | Proposed disposition | Compatibility | Affected cases | Justification |
| --- | ------- | -------- | -------------------- | ------------- | -------------- | ------------- |

Valid dispositions:

- **Fix now**.
- **Fix in a later phase** — with a reason and a follow-up condition.
- **Consciously accept** — with technical justification.
- **Won't fix** — because it isn't a real problem or the cost/risk outweighs the benefit.

Compatibility column: Compatible / Justified breaking / Avoidable breaking.

### 5. Recommended correction plan

Organize by implementation phase, not just by severity:

1. Immediate protection without breaking legitimate capabilities.
2. Integrity and functional errors.
3. Compatibility, migrations, and dependencies.
4. Performance, caching, and operations.
5. Maintainability and justified refactors.
6. Tests, documentation, rollout, and rollback.

For each phase state:

- Exact changes.
- Files or subsystems.
- Dependencies between changes.
- Risks and mitigations.
- Use cases that must keep working.
- Required tests.
- Acceptance criteria.

Close the diagnosis by stating that no code was modified and that you await the user's decision on the matrix.

## Stage 2 deliverable: implementation report

When the authorized implementation is done, deliver:

### 1. Change summary

- Implemented findings (by ID), with the files touched by each.
- Final compatibility classification of each change (Compatible / Justified breaking) and, for breaking ones, the migration strategy applied.

### 2. Verification

- Verification commands run (tests, lint, static analysis) and their literal output.
- Regression tests added or updated, mapped to the finding they cover.
- Confirmation of the full-diff review: every changed line traces back to an approved finding.

### 3. Pending items

Table of matrix findings that were not implemented:

| ID  | Finding | Approved disposition | Reason left pending | Follow-up condition |
| --- | ------- | -------------------- | ------------------- | ------------------- |

If empty, say so explicitly ("the approved matrix was implemented in full").

### 4. Updated documentation

- List of documents touched (README, CHANGELOG, examples, configuration) and which contract changed each one.
