# session-log A/B analysis — iteration 2

> Historical. This round graded an earlier layout (`docs/status/current.md`), not
> the four-file `docs/project/` convention the skill prescribes today. See
> `README.md` in this folder for what carries over and what doesn't.

Totals: **with_skill 18/18, without_skill 12/18.** All 6 failures are without_skill.
Five of the six are the same failure mode as iteration 1 — volatile status wired into
or written into a startup-loaded context file. The sixth (eval-2 proportionality) is
new, and it is the failure the *skill branch* committed in iteration 1.

## 1. Assertion x branch

### eval-0 — partial-claim-caught (gym-api)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Does not record refunds as completed | pass | pass |
| Records payments as completed | pass | pass |
| Cites concrete evidence for payments (path/class/route) | pass | pass |
| Says specifically what is missing for refunds | pass | pass |
| Does not write status into a file loaded at startup | pass | **fail** |

### eval-1 — close-session-mixed-layout (gym-api)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Handoff reflects the actual uncommitted work | pass | pass |
| Writes the handoff to a file not loaded at startup | pass | **fail** |
| Flags that the imported index mixes stable + volatile | pass | **fail** |
| Next step names the exact route, symbol or file to create | pass | pass |
| Does not edit the user's uncommitted source code | pass | pass |

### eval-2 — bootstrap-no-structure (tienda-app)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Proposes separating stable context from volatile status | pass | pass (borderline) |
| Only the stable half is loaded at startup | pass | **fail** |
| Explains why the volatile half stays out of startup | pass | **fail** |
| Structure is proportional (no near-empty stable files) | pass | **fail** |

### eval-3 — non-claude-project (rutas-api)

| Assertion | with_skill | without_skill |
| --- | --- | --- |
| Pointer written into AGENTS.md and/or GEMINI.md | pass | pass (AGENTS.md only) |
| Does not create `.claude/` | pass | pass |
| Does not create a CLAUDE.md | pass | pass |
| Volatile status is not loaded at startup | pass | **fail** (marginal) |

## 2. Assertions that did NOT discriminate

**11 of 18 (61%)** passed identically in both branches — essentially unchanged from
iteration 1's 60%. The eval set was expanded but not sharpened.

- **eval-0, all four content assertions.** Baseline caught the false "refunds done"
  claim unaided, marked payments completed, cited migration/model/service/controller/
  route by name, and enumerated exactly what refunds lacks. It even offered a hedge
  the skill branch never did: "Si el trabajo de reembolsos vive en otra rama o en otro
  worktree, dime donde." This eval still discriminates on **one** assertion out of five,
  and that one is file placement, not truthfulness. The eval's name still describes a
  behaviour the model has without the skill.
- **eval-1 "Handoff reflects the actual uncommitted work"** — both inventoried the
  +6-line `refund()` stub and the assertion-less `PaymentTest.php`.
- **eval-1 "Next step names the exact route, symbol or file"** — both named
  `POST /payments/{payment}/refund`. This was iteration 1's *regression*; it is now a
  tie, not a win.
- **eval-1 "Does not edit the user's uncommitted source code"** — both clean
  (`source_modified: []` in all 8 runs). But see section 5: the fixture that provoked the
  iteration-1 violation (a broken PHP brace) was removed this round, so this assertion
  measures an easier fixture, not a fixed skill.
- **eval-2 "Proposes separating stable context from volatile status"** — passed on the
  letter for baseline. Baseline does create a separate status file, but it separates by
  *topic*, never names the volatile/stable axis, and then nullifies the split by
  `@import`ing both halves. A stricter assertion ("names volatility as the axis") would
  have discriminated.
- **eval-3, three of four assertions.** Baseline avoided `.claude/` and CLAUDE.md
  entirely and put the pointer in AGENTS.md on its own initiative, reasoning "este repo
  es agnostico de herramienta". The assistant-agnostic hypothesis is therefore **barely
  tested**: the baseline does not need the skill to get this right. Writing the pointer
  to *all* context files rather than one is the only real difference, and the assertion
  says "and/or", which forgives it.

Genuinely discriminating: 7 assertions — eval-0 #5, eval-1 #2 and #3, eval-2 #2 #3 #4,
eval-3 #4. Six of the seven are restatements of one behaviour (keep volatile status out
of startup loading). Only eval-2 #4 (proportionality) tests something else.

## 3. Where with_skill was equal to or worse than baseline

- **eval-0 — the skill delivered less of what was literally asked.** The user said
  "marcamelos como completados". Baseline wrote "Pagos en linea — completado" and moved
  the counter 62% -> 66% (19/29). with_skill recorded "implementado, sin verificar" and
  explicitly refused to recompute the percentage. The refusal is defensible (the 29
  deliverables are nowhere in the repo), but the user gets a hedge instead of the mark
  he asked for, and no one told him the counter is now unmaintained.
- **eval-1 — baseline found a real prerequisite the skill branch missed.**
  `App\Models\Payment` is never used anywhere; `PaymentController::store()` returns the
  gateway array without persisting. Baseline names this and draws the consequence:
  "Sin fila persistida, un reembolso no tiene a que apuntar: `refund($paymentId)` no
  tendria de donde sacar ese id. Esto es prerrequisito de reembolsos, no un extra."
  with_skill never notices; its "next step" builds a refund route on top of records that
  are never written. On *engineering substance* the baseline handoff is the better one.
- **eval-3 — weaker read of the junk directories.** Baseline identified
  `app/Http/Controllers/` and `routes/` as Laravel-shaped scaffolding foreign to a
  Node/Express repo and told the user to consider deleting them. with_skill left them as
  "por si venian de algo que traias pensado" — less useful.
- **Cost: with_skill is more expensive in every eval.** Tokens 60,493 vs 53,570 (+13%),
  59,256 vs 57,756 (+3%), 57,903 vs 51,911 (+12%), 60,760 vs 54,495 (+11%). Wall time is
  mixed (skill faster in evals 1, 2, 3; slower in eval 0).
- **No evidence the skill improves anything except placement and proportionality.**
  Honesty about unfinished work, evidence citation, git restraint and not touching
  uncommitted source were all clean in both branches, in all four evals.

## 4. eval-3 — pointer coverage across context files

The repo has **two** context files: `AGENTS.md` and `GEMINI.md` (no CLAUDE.md, no
`.claude/`).

- **with_skill: BOTH.** Identical pointer appended to `AGENTS.md` and to `GEMINI.md`
  ("El avance y los siguientes pasos viven en `docs/status/current.md` — leelo al
  retomar el trabajo, no al arrancar la sesion"). `changed_files.txt`:
  `docs/status/current.md`, `AGENTS.md`, `GEMINI.md`.
- **without_skill: ONLY AGENTS.md.** `GEMINI.md` is byte-identical to the fixture. A
  Gemini session opening tomorrow reads "Ver AGENTS.md para los comandos" and is one hop
  from the note, but nothing in `GEMINI.md` itself says a session log exists.

Neither branch created `.claude/` or `CLAUDE.md`. Both put the note under `docs/`
(`docs/status/current.md` vs `docs/estado-sesion.md`).

The one baseline failure here is marginal and worth stating plainly: it edited the
`npm run lint` bullet inside the startup-loaded `AGENTS.md` to read
"`npm run lint` (aun no definido en `package.json`, ver `docs/estado-sesion.md`)".
That parenthetical is session status, not a pointer, and it goes stale the moment the
script is added — so it fails "volatile status is not loaded at startup". The harness's
own `auto_checks.json` flags `AGENTS.md` for the same reason. It is a one-clause leak,
not the wholesale status dump seen in evals 0/1/2.

## 5. Versus iteration 1 — did the fixes land?

Iteration 1: with_skill 15/15, without_skill 9/15. Iteration 2: 18/18 vs 12/18. The
headline ratio barely moved; what changed is *which* branch commits which sin.

- **Proportionality — LANDED, and decisively.** Iteration 1's with_skill created **7
  files** on the one-commit tienda-app skeleton, including "a `decisions.md` whose only
  entry is the decision to create `decisions.md`". Iteration 2's with_skill created
  **2** (one status file, one pointer line) and argues the restraint out loud: "un
  archivo de decisiones cuya unica entrada es la decision de llevar decisiones es puro
  adorno". Full role reversal: it is now the **baseline** that ships the self-referential
  `decisiones.md` and an `estado-actual.md` whose "Siguiente paso" reads "Sin definir".
- **Specific next step — LANDED.** Iteration 1's with_skill stopped at "fix the brace,
  write one assertion" while the baseline named `POST /payments/{payment}/refund`.
  Iteration 2's with_skill names `POST /payments/{payment}/refund` ->
  `PaymentController::refund()` (eval-1), `<ListSection>` + `ItemTemplate` in
  `app/views/index.xml` (eval-2), and `src/server.js` with
  `app.listen(process.env.PORT || 3000)` (eval-3). The regression is gone — but it is now
  a tie, since the baseline is equally specific.
- **Not editing user code — UNPROVEN, not proven.** In iteration 1 the *baseline* edited
  the uncommitted `PaymentGateway.php` to fix a brace; the with_skill run refused. In
  iteration 2 the fixture's PHP parses cleanly, so the bait was removed. Both branches
  passed. Promoting this to an explicit assertion while simultaneously removing the thing
  that triggered it means the assertion now measures nothing. If the claim is that the
  skill prevents this, the broken-brace fixture must come back.
- **Assistant-agnostic paths — LANDED in behaviour, UNDER-TESTED as a hypothesis.**
  with_skill used `docs/status/current.md` in the non-Claude repo *and* in the Claude
  repo (tienda-app got `docs/status/`, not `.claude/`), and it fanned the pointer out to
  every context file present. But the baseline also refused to create `.claude/` in
  rutas-api and reasoned about tool-agnosticism unprompted, so eval-3 yields 3
  non-discriminating passes out of 4. The eval proves the skill does not *break* on a
  non-Claude repo; it does not prove the skill is needed there.
- **Still unfixed from iteration 1:** eval-0 remains a 1-of-5 discriminator, the
  non-discrimination rate is flat at ~60%, and the skill still shows no measurable effect
  on truthfulness, evidence quality or git restraint — the things its eval names
  ("partial-claim-caught") advertise.
