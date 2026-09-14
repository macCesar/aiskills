---
name: laravel-security-sweep
description: 'Low-cost security review of a Laravel 8–13 project. A bundled script runs composer audit and greps for the patterns behind real Laravel breaches (fail-open role middleware, public sign-ups writing into the admin users table, raw SQL with interpolated input, reset links built from the Host header, SSRF, client-controlled uploads, secrets with hard-coded fallbacks); the agent reads only the matching lines to confirm or discard each. One agent, no subagent swarm. Use when the user asks for a security check, audit or vulnerability review of a Laravel or Blade project — "revisa la seguridad de este proyecto", "busca vulnerabilidades", "is this safe to put online" — or wants the same review across several Laravel sites without a large token bill. Laravel 3 and 4 are reported as out of scope. Not for: reviewing only a diff or PR, non-Laravel stacks, performance or style audits, or pentesting a live server.'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, AskUserQuestion
compatibility: Requires Python 3 (standard library only). composer audit needs Composer 2.4+ and network access; the rest runs offline and never executes the project's code.
---

# Laravel Security Sweep

Find the security bugs that actually get Laravel sites broken into, for the price of reading a few dozen lines instead of the whole codebase.

The method splits the work by who is cheap at it. The script does the mechanical part — version detection, dependency advisories, pattern search over `app/`, `routes/`, `config/`, `resources/views/` and `bootstrap/` — and costs no tokens. The agent does the part that needs judgment: open each match, decide whether it is exploitable, and say why. A grep hit is a place to look, never a finding by itself; reporting hits unread is how a sweep turns into noise the owner learns to ignore.

The work has two stages separated by an explicit authorization, for the same reason as any audit: a review that edits while it looks produces a list of things already changed, and takes the decision away from the owner. Stage 1 writes nothing.

Respond in the user's language. This skill is written in English for portability; the report should match whatever language the user is writing in.

## Stage 1 — Sweep and triage, no modifications

1. **Run the script** from the project root:

   ```bash
   python3 <SKILL_DIR>/scripts/barrido_laravel.py /path/to/project
   python3 <SKILL_DIR>/scripts/barrido_laravel.py /path/to/project --sin-composer   # offline
   python3 <SKILL_DIR>/scripts/barrido_laravel.py /path/to/project --json --max 50
   ```

   Replace `<SKILL_DIR>` with the absolute "Base directory for this skill" from the system message that loaded this skill; the working directory is the user's project, so a relative `scripts/…` resolves to nothing.

   If it reports Laravel 3 or 4, stop there and say so: their structure and APIs differ enough that these patterns would produce false confidence, and the honest recommendation for those projects is a migration plan, not a sweep. Laravel 5–7 run through the Laravel 8 rules with a caveat in the report.

2. **Read the version and structure lines first.** `app/Http/Kernel.php` means the Laravel 8–10 layout; `bootstrap/app.php` with `->withMiddleware(` means 11 and later, where middleware, trusted hosts and CSRF exclusions are configured in that file instead. Every fix you propose must match the structure the project actually has — see `references/versions.md`.

3. **Triage every match by reading it, not the whole file.** Open each `file:line` with a window of about 20 lines around it (`Read` with `offset`/`limit`). Follow a variable back only as far as needed to know where it comes from: request input, route parameter, authenticated user, database, or a constant. For each pattern, `references/patterns.md` says what makes a match real, what makes it a false positive, and how to fix it. Read the section for a pattern before judging its matches.

   Group matches that share one root cause into one finding — twenty-two raw queries built the same way are one finding with a list of locations, not twenty-two findings.

4. **Check what the patterns cannot see**, briefly and only where the script pointed: for each `AUTH-ENTRY` and `AUTHZ-MIDDLEWARE` match, decide who can obtain a session and whether the admin route group rejects everyone who should not be there. That combination — a public registration plus a middleware that lets unknown routes through — is the most damaging pattern this sweep exists to catch, and neither half looks wrong on its own.

5. **Report**, in this shape:

   | # | Finding | Severity | Where | Why it is exploitable |
   | --- | --- | --- | --- | --- |
   | 1 | Role middleware allows routes with no section row | High | `app/Http/Middleware/CheckRole.php:37` | Any logged-in account reaches every unlisted admin module |

   Then, separately: matches discarded and the one-line reason for each group (so the owner can see they were read, not skipped); `composer audit` advisories; and a short **Not covered** list (below). Severity is what an attacker gets and how hard it is to get: High is account takeover, data exposure, arbitrary file write or code execution behind at most one real hurdle; Medium is bounded impact or several conditions; Low is limited impact.

6. **Stop.** Present the report and what you would change. Do not start fixing.

## Stage 2 — Authorized fixes

Start only once the user approves, and only for the findings they approved.

1. **Find out how the project deploys before the first edit.** An SFTP upload-on-save watcher or similar makes every saved file live in seconds, including a half-finished one; order edits so nothing reads a column, class or config key before it exists, and say this to the user.
2. **Fix the root cause at the sink**, per `references/patterns.md`, using the project's structure from `references/versions.md`. Sweep the pattern, not only the reported line: when one raw query is wrong, fix all of them.
3. **Check the fix does not lock out legitimate use.** Denying by default in an authorization middleware is right, but before shipping it look at who uses the panel today (roles in the database, not the seeders), so the owner is not the first person it blocks.
4. **Verify.** Run the project's tests; add a test that fails without the fix where the project has a test suite. Re-run the script and expect the fixed matches to disappear or to be explainable by reading. Where behaviour depends on the real database (MySQL full-text search, for instance), test against it rather than trusting SQLite.

## Not covered

Say this in every report, because a clean sweep is otherwise read as a clean bill of health:

- Authorization of individual records (can user A open user B's invoice) beyond the patterns above.
- Business logic, JavaScript front ends, and server configuration (web server, PHP handlers, file permissions).
- Anything outside the swept directories, such as custom packages under `packages/`.
- Vulnerabilities that do not leave a textual pattern. For those, a deeper multi-agent scan or a manual review of the exposed surface is the next step.

## Where to look

| Task involves | Read |
| --- | --- |
| Judging a match: real or false positive, and the fix | `references/patterns.md` |
| Where middleware, trusted hosts, CSRF and casts live in each Laravel version | `references/versions.md` |
