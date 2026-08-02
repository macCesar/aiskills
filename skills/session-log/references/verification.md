# Verifying that work actually exists

Read this before marking anything as done. The goal is narrow: turn "I finished
X" into "I found the artifacts X would have produced."

## What "done" is allowed to mean

Be careful with the word — these are different claims, and a record that collapses
them into one checkmark loses the distinction exactly when someone needs it:

| Claim | What it means |
| --- | --- |
| Implemented | The code exists — you found it |
| Verified | Tests or a build passed, and you saw the output |
| Reviewed | A human looked at it |
| Shipped | It's deployed or released |

Use the distinction to be *more* precise, not to avoid answering. "Implemented,
not yet verified — no test covers it" is a useful record. Marking nothing at all
because verification was impossible is not.

## Three ways records go bad

**Percentages the repo can't support.** A percentage needs a fixed denominator —
a checklist with a known number of items. Without one, any number is invented.
Count what's enumerable or describe status in words.

**Duplicating what the repo already records.** Git history, the CHANGELOG and the
code are better sources than a note paraphrasing them. Record what they *can't*
say: why an approach was abandoned, what failed, what looks wrong but is deliberate.

**Padding.** A handoff nobody reads is a handoff that failed. Three specific lines
beat a page of headers. Length is not thoroughness.

## The method

Someone's claim is about behavior. The repo holds artifacts. Verification is
translating between the two:

1. **Name the artifacts before searching.** "Finished the payments module" should
   produce a concrete list first — a service class, a route, a migration, a test.
   Writing that list before you look is what stops you from accepting whatever
   you happen to find as sufficient.
2. **Search for those specific things**, not for the feature name. Grepping for
   "payment" finds comments, TODOs, and unrelated strings. Grepping for the route
   registration or the class definition finds the thing itself.
3. **Distinguish existence from completeness.** A file that exists but contains a
   stub is not the feature. Open what you find when the claim is substantial.
4. **Report the gap, not just the verdict.** "Found the service and the routes;
   no tests and no migration" is useful. "Not done" is not.

## What to search for, by stack

The artifact names differ; the reasoning doesn't. Use the closest row and adapt.

### Laravel / PHP

| Claim involves | Look for |
| --- | --- |
| Web route | Registration in `routes/web.php` |
| API endpoint | Registration in `routes/api.php` |
| Controller | `app/Http/Controllers/**/*.php` |
| Livewire component | `app/Livewire/**/*.php` plus its Blade view under `resources/views/livewire/` |
| Model | `app/Models/*.php` |
| Migration | `database/migrations/*.php` — and whether it has been run |
| Service / action | `app/Services/`, `app/Actions/` |
| Job / queue work | `app/Jobs/` |
| Test | `tests/Feature/`, `tests/Unit/` |

A Livewire feature that has a class but no Blade view is not done. Check both.

### Titanium SDK / Alloy

| Claim involves | Look for |
| --- | --- |
| Screen | Matching files in `app/controllers/` **and** `app/views/` |
| Styling | `app/styles/` — note `app.tss` is generated, so hand edits there mean nothing |
| Business logic | `app/lib/` — helpers, services, repositories |
| Localized text | Matching keys in every `app/i18n/*/strings.xml`, not just one |
| Native module | Declared in `tiapp.xml` under `<modules>` **and** present in `modules/` |
| Platform config | `tiapp.xml` |

A controller without its view compiles to nothing usable. A string added to one
locale and not the others ships as a raw key in the missing language.

### Node / TypeScript

| Claim involves | Look for |
| --- | --- |
| Endpoint | Route registration — framework-specific, follow the app entry point |
| Module | The file plus its export from the package or barrel index |
| Type / interface | `*.d.ts` or the declaring source file |
| Test | `*.test.ts`, `*.spec.ts`, or the configured test directory |
| Dependency | `package.json` **and** the lockfile |

### Python

| Claim involves | Look for |
| --- | --- |
| Module | The `.py` file plus its import from wherever it's used |
| Endpoint | Router or URL configuration — framework-specific |
| Model / schema | The declaring class, plus a migration if the project has them |
| Test | `test_*.py` or `*_test.py` |
| Dependency | `pyproject.toml`, `requirements.txt`, or the lockfile |

### Rails

| Claim involves | Look for |
| --- | --- |
| Route | `config/routes.rb` |
| Controller / model | `app/controllers/`, `app/models/` |
| Migration | `db/migrate/` — and whether `schema.rb` reflects it |
| Job | `app/jobs/` |
| Test / spec | `test/`, `spec/` |

### Go

| Claim involves | Look for |
| --- | --- |
| Handler | The handler function plus its route registration |
| Package | The directory plus its import path in use |
| Test | `*_test.go` |
| Dependency | `go.mod` **and** `go.sum` |

## Claims in a status file you didn't write

Resuming work means reading claims written weeks ago by someone — possibly you —
who is no longer available to ask. The method above applies unchanged, with one
addition: an old record has a **direction of error**. It says what was true when it
was written, so its claims rot toward being *understated* about what exists and
*overstated* about what's blocked.

- "Not started" from three weeks ago may well be finished. Check the artifacts
  before repeating it — this is the most common way a resumed session redoes work.
- "Blocked on the client" has a date attached to a person who has probably answered
  since. Flag it as needing a human check rather than carrying it forward as fact.
- "Next step: X" may be stale in a way the file cannot know. If X is already in the
  code, say so instead of proposing it again.

The safe form is attribution: "the file says the payments module was left half-done
on 2026-07-14; the routes and the service exist now, so part of that landed after it
was written". That gives the person both the record and the correction.

## Claims that can't be verified from the repo

Some are legitimate and simply live elsewhere: work in another repository, a
deploy, a conversation with a client, a design decision.

Record them. Label them. The pattern that keeps the log trustworthy is:

```markdown
- Payments service implemented — verified: `app/Services/PaymentGateway.php`,
  routes `payments.store` and `payments.show`
- Staging deploy completed — unverified, reported by the user
```

The distinction costs one word and preserves the whole point of the record.

## Deployment is not git state

A change can be live on a server without being committed, and committed without
being live. Repos with file-sync deployment (SFTP-on-save watchers, rsync hooks)
break the assumption that git reflects production entirely.

Never infer deployment state from git. When it matters, check the deployment
configuration in the repo, or ask.

## Tests: the output is the evidence

"Tests pass" is a claim like any other. If you ran them, quote the count and the
result. If you didn't, say so. A log that records passing tests nobody ran is
worse than one that records nothing, because it stops the next session from
running them.
