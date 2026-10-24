# Requirements

Source: this file. Product behavior is documented in `README.md`; the architectural boundary with TiTools is documented in `docs/project/context.md` § "Sibling project".

## Engineering

### R1 — The shared CLI CORE stays synchronized with TiTools

`@maccesar/titools` is the same CLI engine shipped with a different payload. The shared CORE covers CLI entry behavior, common `lib/` and `lib/commands/` behavior, installation and symlink handling, marketplace-plugin detection, non-product-specific hooks, shared tests, manifest wiring, and release mechanics.

**Accepted when:** every shared-CORE change is ported to TiTools in the same working session, both repos are verified independently, and any intentional difference is already listed in `context.md` § "Sibling project" or recorded as a decision before the session ends. Titanium-specific pieces — the Knowledge Index, `tiapp.xml` detection, the `ti-pro` agent, Titanium skills and TiTools-only commands — remain legitimate product differences.

Parity acceptance requires per-behavior evidence in BOTH status files: the
corresponding implementation/test paths, independently executed focused checks
and their results, plus a technical justification for each product exception.
An already equivalent implementation must be inspected and verified; a prior
note is insufficient. Shared test-only and release/documentation changes count.
An unavailable sibling, unported regression or failed check leaves the shared
change incomplete and blocks completion/publication of the affected release.
Product-specific payloads, independent release authorization and existing
private-file boundaries must be preserved. See AGENTS.md's mandatory parity gate.
