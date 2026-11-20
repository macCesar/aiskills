# Status — 2026-11-20

**Phase:** v1.30.0 published and verified. **Session by:** Codex · GPT-6. **Branch:** main.

## Result

- Released `articulos-de-blog` with five editorial references for planning, research, writing, and review. The title guidance keeps titles easy to scan, preserves details that help readers recognize their problem, and reserves claims about tests for work the article documents.
- The skill saves Markdown articles by language and a companion publication file with the suggested blog section, keywords, tags, and cover prompts. It routes Spanish and English review to Humaniza and Humanizer and uses ImageGen for the cover in Codex.

## Commits and publication

- `5108ab7` — feat(blog): add article writing skill.
- `1fc209b8d185bb4885b2c0524da7ecf2e9ebfb4e` — chore(release): v1.30.0. The annotated tag points to this commit.
- GitHub release: https://github.com/macCesar/aiskills/releases/tag/v1.30.0. Verified the approved title and notes against the public release.
- OIDC workflow: https://github.com/macCesar/aiskills/actions/runs/44801173273. The version guard, install, tests, and npm publish passed.
- npm serves `@maccesar/aiskills@1.30.0` with `latest=1.30.0`. Registry publication timestamp: 2026-11-20T19:23:42.993Z. The downloadable archive became available after the metadata. Its SHA-512 integrity and all six skill Markdown files, including the final title criteria, match the release.
- The public `.claude-plugin/plugin.json` on main reports version 1.30.0. Both root lockfile version entries and the npm manifest match it.

## Verification and scope

- Local release suite: 222 tests passed with zero failures or skips. ESLint on `lib/config.js` and `git diff --check` passed.
- Shared engine parity: **product-specific exception**. The `lib/config.js` change registers one AISkills catalog entry. The skill, its README entry, and the synchronized release versions require no corresponding TiTools change.
- The maintainer's development symlink resolves to `skills/articulos-de-blog/`. The published npm archive excludes `docs/project/`.

## Next step

Release verification is complete.
