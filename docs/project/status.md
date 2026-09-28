# Status — 2026-09-28

**Phase:** v1.27.1 release published; npm download verification is blocked by a registry 404.
**Session by:** Codex · GPT-6 — applied the supplied handoff patch, committed it, and executed the confirmed release.
**Publication:** GitHub Release and annotated tag `v1.27.1` point at release commit `65e05ee`. `publish.yml` run [36489047822](https://github.com/macCesar/aiskills/actions/runs/36489047822) succeeded and reported `+ @maccesar/aiskills@1.27.1` with provenance. npm now reports `latest` as `1.27.1`, but repeated tarball downloads, including `npm pack`, returned HTTP 404 after publication. Installation from npm is not verified.
**Branch:** `main`; the release commit is on origin. This note is committed and pushed after the tag.

## Where things stand

- `handoff` explicitly accepts `/handoff`, `$handoff`, or a request for `HANDOFF.md` without asking the user to repeat the context. README and the evaluation prompt match. Change commit: `783e19b`.
- The release also includes removal of the stale machine-local memory import from `CLAUDE.md`.
- `package.json`, `package-lock.json`, and `.claude-plugin/plugin.json` are synchronized at `1.27.1`. The plugin manifest served from GitHub main was verified at that version.
- No shared CLI machinery changed, so no TiTools port was required.

## Next step

Retry `npm pack @maccesar/aiskills@1.27.1 --pack-destination /tmp --registry=https://registry.npmjs.org` to confirm the registry tarball is downloadable. If the 404 persists, investigate npm publication availability; do not reuse or replace the existing tag.

## Verified vs. assumed

- `npm test`: 179/179 passed after the version bump; release diff passed `git diff --check`.
- GitHub Release is public, not a draft or prerelease; remote tag resolves to `65e05ee`.
- npm metadata reports `1.27.1` and preserves `bin.aiskills = bin/aiskills.js`, despite the publish log's bin normalization warning. The downloaded tarball could not be inspected because the registry returned 404.
- Local `npm pack --dry-run --json` excludes `docs/`; this session note does not change the package contents.
- The revised minimal-invocation evaluation was not rerun with an assistant. Prior handoff evaluation results describe the earlier prompt.
- The optional skill validator could not run because the local Python lacks PyYAML.

## Known pending

- `store-screenshots` has a README table row but no dedicated section.
- Real-session validation of `handoff` and new simulator/emulator captures for `store-screenshots` remain outside this release's verification.
