---
name: audit-codebase
description: 'Audit a whole codebase, app, backend, or API as one unit and prepare or (once approved) implement an evidence-based correction plan, preserving legitimate use cases and avoiding disproportionate security controls. One sweep across security, production-readiness, architecture, dependencies, compatibility, performance, maintainability, and tests, in any language. Use even when the user just says "audit this project", "go through the whole app end to end", "is it safe to ship to prod / run on the public internet?", "do a real security review of my API", "find real problems before we launch", "what''s actually broken vs. just ugly?", "audit it and implement the fixes", or "implement the audit plan / decision matrix we already approved". Do NOT use for narrow work — a single bug, one regex or snippet, a small PR/diff, or tests for one module — nor for non-code audits like cloud bills or resumes.'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, AskUserQuestion
---

# Audit Codebase

Act as a senior software, security, and architecture auditor. Review the whole project end to end before drawing any conclusions.

The work has two stages separated by an explicit user authorization. The separation exists because the value of an audit depends on a neutral diagnosis: if you edit while you audit, you contaminate the evidence and take away the user's decision about what to change. The first deliverable is always diagnosis and plan; code is only touched after the user approves the decision matrix.

Respond in the user's language. This skill is written in English for portability, but the audit report should match whatever language the user is writing in.

## How the user invokes this

- **Audit only** ("audit this", "is it production-ready?", "security review") — run stage 1 and stop at the decision matrix + plan. Don't touch code.
- **Audit and fix** ("audit and implement the fixes", "find problems and fix them", "clean this up before we ship") — run stage 1, then present the decision matrix and stop for a single go/no-go before stage 2. Even when the user asks up front to fix everything, show the matrix first: it takes seconds to approve and it's the checkpoint that lets you change code on their own repo without guessing which product tradeoffs are acceptable. Once they approve (a plain "yes, go" is enough), implement the full matrix.
- **Implement a prior plan** ("implement the audit plan we approved") — skip discovery, go straight to stage 2 against the approved matrix.

If the user explicitly says to skip the checkpoint ("just fix everything, don't ask"), honor it — but still surface any finding whose fix would break a documented use case before applying that specific change, because that's a product decision you can't infer.

## Before you start

Read `references/comprehensive-audit.md`. It holds the mandatory principles, the full technical scope (24 areas), the phased method, the severity classification, and the recommendation rules. Don't audit from memory: the file exists so the review is systematic and doesn't depend on which areas you happen to recall in the moment.

Before writing any deliverable (diagnosis, decision matrix, or implementation report), read `references/report-format.md` and use those exact structures. A stable format lets audits be compared across projects and guarantees that no finding is left without a disposition.

## Stage 1 — Audit (no modifications)

Do not modify the project during this stage. This covers the whole project tree, not just source files: don't leave build output, compiled bytecode (`__pycache__`, `.pyc`), caches, lockfiles, `node_modules`, coverage reports, or any generated artifact behind. Verification tools often write into the tree as a side effect — `python -m py_compile` drops `__pycache__`, test runners and bundlers create caches, `npm install` writes `node_modules`. When you need to run such a tool, run it so its output lands outside the project (e.g. set `PYTHONPYCACHEPREFIX` to a temp dir, use a flag that disables writes, or copy the file elsewhere first); if you can't, skip it and record the check as unverified with the reason. A clean read-only pass is what lets the user trust that the diagnosis changed nothing.

If a critical finding needs immediate attention, report it first, but continue the full audit — don't stop at the first serious problem.

1. **Discovery** — Identify the stack and real versions. Inventory entrypoints, routes, models, migrations, services, and commands. Read README, CHANGELOG, configuration, tests, and examples to understand the project's intent.
2. **Existing use cases** — Build the list of real capabilities and actors (anonymous visitor, authenticated user, resource owner, admin, API client, internal processes) **before** recommending any change. This list is the yardstick every restrictive recommendation is measured against.
3. **Evidence** — Run available tests, lint, static analysis, and dependency audits. Verify authorization with at least two users/tenants when it applies. Confirm every claim before reporting it.
4. **Findings** — Document each problem with concrete evidence (file, line, configuration, reproducible behavior) and a status: **Confirmed**, **Conditional risk**, or **Unverified**.
5. **Decision matrix** — Every confirmed finding, medium and low included, gets an explicit proposed disposition. None is silently discarded.
6. **Correction plan** — Organized by implementation phase, with compatibility, tests, and rollback. Stop here and wait for the user's approval.

### Stage 1 critical rules

- **Evidence before patterns.** Don't flag something as vulnerable just because it resembles a known pattern. A finding without evidence is noise that erodes trust in the real findings.
- **Proportional security, not absolute.** Before recommending mandatory auth, allowlists, or route blocking, identify which legitimate use cases would break and evaluate the least-restrictive alternative (signatures, opaque tokens, ownership, rate limiting, expiration).
- **Severity is not scope.** Severity signals risk; the disposition (fix now, later phase, accept, won't fix) is a separate decision that every finding must receive explicitly.
- **Don't turn product decisions into technical assumptions.** Ask only what cannot be inferred from the repository.

## Stage 2 — Authorized implementation

Start only when the user approves the decision matrix.

1. Implement the **full** approved matrix, not just the critical and high findings.
2. If a change contradicts an existing use case discovered in stage 1, stop and present it before applying the restriction.
3. Keep or add regression tests for every affected behavior.
4. Update configuration, documentation, examples, and CHANGELOG when a public contract changes.
5. Re-run all verifications and review the full diff: every changed line must trace back to an approved finding. No cosmetic cleanup, no unrelated features.
6. Explicitly list any finding you did not implement and the approved reason it was left pending.

## Closing condition

The audit or implementation is complete only when:

1. Every finding has evidence and a status.
2. Every confirmed finding has an explicit disposition.
3. Existing capabilities and legitimate use cases are documented.
4. The plan (or final report) includes compatibility, tests, and rollback.
5. In stage 1, no code was modified.

Do not declare the work "complete" if any finding is left without an explicit disposition.
