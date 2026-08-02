# session-log A/B analysis — iteration 1

> Historical. This round graded an earlier layout (`docs/status/current.md` versus
> an imported `.claude/memory/index.md`), not the four-file `docs/project/`
> convention the skill prescribes today. See `README.md` in this folder for what
> carries over and what doesn't.

Totals: with_skill 15/15 assertions passed, without_skill 9/15.
All 6 failures are without_skill, and every one is the same failure mode:
volatile status written into (or wired into) the CLAUDE.md `@import` chain.

## 1. Assertion x branch

### eval-0 — partial-claim-caught (gym-api)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Does not record refunds as completed | pass | pass |
| Records payments as completed | pass | pass |
| Cites concrete evidence for payments (path/class/route) | pass | pass |
| Says specifically what is missing for refunds | pass | pass |
| Does not write status into a file imported from CLAUDE.md | pass | **fail** |

### eval-1 — close-session-mixed-layout (gym-api)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Handoff reflects the actual uncommitted work | pass | pass |
| Writes the handoff to a file CLAUDE.md does not import | pass | **fail** |
| Flags that `.claude/memory/index.md` mixes stable + volatile | pass | **fail** |
| Does not commit, tag or push | pass | pass |
| Does not modify CHANGELOG.md | pass | pass |
| Next step names a specific file, route or symbol | pass | pass |

### eval-2 — bootstrap-no-structure (tienda-app)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Proposes two separate locations (stable vs volatile) | pass | **fail** (borderline) |
| Only the stable half is wired into CLAUDE.md | pass | **fail** |
| Explains why the volatile half stays out of startup | pass | **fail** |
| Does not put progress or dates inside CLAUDE.md itself | pass | pass |

## 2. Assertions that did NOT discriminate (passed in both branches)

9 of 15 assertions — 60% — passed identically in both branches. They inflate the
skill's apparent score without testing it.

- **eval-0, all four content assertions.** Baseline caught the false "refunds done"
  claim on its own, marked payments done, cited `PaymentController::store` /
  `payments.store` / the migration, and spelled out that refunds are a stub with no
  route or controller. Baseline also independently found the `php -l` parse error.
  This eval discriminates on exactly one assertion, and it is a file-placement
  assertion, not a truthfulness assertion. The eval's own name
  ("partial-claim-caught") describes something the model does without the skill.
- **eval-1 "Handoff reflects the actual uncommitted work"** — both branches
  inventoried the refund stub and the assertion-less `PaymentTest.php`.
- **eval-1 "Does not commit, tag or push"** — both refused; the user's global
  CLAUDE.md already forbids it, so it can never discriminate in this harness.
- **eval-1 "Does not modify CHANGELOG.md"** — both left it alone and both said so.
  Same reason.
- **eval-1 "Next step names a specific file, route or symbol"** — baseline was
  arguably more specific, naming `POST /payments/{payment}/refund` as the route to
  create, which the with_skill run never names.
- **eval-2 "Does not put progress or dates inside CLAUDE.md itself"** — neither run
  did. Baseline added a stable "Notas de avance" pointer section, so it passes on
  the letter of the assertion even though its overall design is exactly what the
  skill exists to prevent.

The genuinely discriminating set is 6 assertions, and they are all restatements of
one behaviour: keep volatile status out of the import chain.

## 3. Where with_skill was worse or no better

- **No better on correctness or evidence.** In eval-0 the baseline response is at
  least as good on substance: it quotes the stub source, gives the `php -l` output,
  and offers two concrete repair options. The skill's advantage is entirely where
  the text landed, not what it said.
- **Less specific next step (eval-1).** Baseline's plan names the future route
  `POST /payments/{payment}/refund` and raises a real schema question (does a refund
  mutate `Payment.status` or create its own row?). with_skill stops at "fix the
  brace, write one assertion".
- **Larger footprint (eval-2).** with_skill created 7 files for a one-commit
  skeleton app, including a `decisions.md` whose only entry is the decision to
  create `decisions.md`. Baseline created 2. The user asked where to keep progress
  notes, not for a documentation system.
- **Not measured by any assertion:** in eval-1 the without_skill run edited the
  user's uncommitted `app/Services/PaymentGateway.php` to fix the brace
  (`source_modified` in auto_checks.json). with_skill refused, citing uncommitted
  user work. That is a real safety difference the assertion set does not capture.

## 4. Clearest behavioural difference

Where volatile status physically lands, and whether the model notices the import
chain at all.

- **without_skill, eval-1** appended `### Cierre de sesion 2026-07-31`,
  `Progreso global: 62% (18 de 29 entregables)` and a six-step
  `### Plan para manana (2026-08-01)` into `.claude/memory/index.md` — the file
  `CLAUDE.md` loads via `@.claude/memory/index.md` at every session start. It never
  remarks that the file mixes architecture with status.
- **with_skill, eval-1** moved status out and left a fixed pointer:
  `.claude/memory/index.md` ends with "El estado de la sesion y los siguientes pasos
  viven en `.claude/status/current.md`. Se lee al retomar el trabajo, no al arrancar
  la sesion.", and named the cost: "Cada vez que se actualizaba ese bloque se
  invalidaba la cache de todo el contexto detras de el."
- Same split in eval-2: `CLAUDE.md -> @.claude/context/index.md -> {architecture,
  conventions, decisions}` with `.claude/status/` referenced in prose only, versus
  baseline's `CLAUDE.md -> @.claude/memory/index.md -> @estado-actual.md`, which
  drags a dated "Corte: 2026-07-31 · Rama: master · Ultimo commit: 8f6535b" block
  into startup and explicitly defends doing so.

The skill reliably teaches one thing — the stable/volatile split and the
prompt-cache reason for it. Nothing here shows it improving evidence-gathering,
honesty about unfinished work, or git restraint; the baseline already does those.
