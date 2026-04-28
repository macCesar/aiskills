---
allowed-tools: Bash(git:*), Bash(gh:*), Bash(npm version:*), Bash(npm pkg:*), Bash(cat:*), Bash(grep:*), Bash(test:*), Read, Edit, Write, Glob, Grep
description: Full release workflow — detect project, infer semver bump, update CHANGELOG+README, commit, push, tag, GitHub release
argument-hint: [patch|minor|major] (optional; inferred from semantic commits if omitted)
---

## Context (read-only — collected automatically)

- Working tree status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Last tag: !`git describe --tags --abbrev=0 2>/dev/null || echo "<no tags>"`
- Commits since last tag: !`git log --pretty=format:"%h %s" $(git describe --tags --abbrev=0 2>/dev/null)..HEAD 2>/dev/null || git log --pretty=format:"%h %s"`
- Remote URL: !`git remote get-url origin 2>/dev/null || echo "<no remote>"`
- Recent commit style: !`git log --pretty=format:"%s" -20`
- Has gh CLI: !`command -v gh >/dev/null 2>&1 && echo "yes" || echo "no"`
- Versioned files present:
  - package.json: !`test -f package.json && echo "yes" || echo "no"`
  - tiapp.xml: !`test -f tiapp.xml && echo "yes" || echo "no"`
  - composer.json: !`test -f composer.json && echo "yes" || echo "no"`
  - Cargo.toml: !`test -f Cargo.toml && echo "yes" || echo "no"`
  - podspec: !`ls *.podspec 2>/dev/null | head -1 || echo "<none>"`
- CHANGELOG.md present: !`test -f CHANGELOG.md && echo "yes" || echo "no"`
- README.md present: !`test -f README.md && echo "yes" || echo "no"`

## Arguments

`$ARGUMENTS` may contain `patch`, `minor`, or `major` to override the inferred bump. If empty, infer from the commits above.

## Your task

Execute the **release workflow** in five strict, ordered steps. **Do not skip Step 4** — it is the user's confirmation gate and is non-negotiable.

### Step 0 — Lock interaction language (do this BEFORE printing anything)

Before you produce any user-facing output, scan the user's last 1–3 messages in this conversation and determine their language. **This file is in English for distribution; that does not mean you respond in English.** Lock that detected language and use it for **every** message you print to the user from this point until the command ends — Step 1 summary, Step 2 inferred bump, Step 4 plan preview, Step 5 progress, errors, final report.

If the user has not yet said anything in this session (rare — `/release` invoked as the very first message), default to the language of the repo's `README.md`. If that is also unclear, default to English.

If the user switches language mid-flow, switch with them on the next message.

This rule is **Axis 1** of the Language policy below and is non-negotiable. **Axis 2** (the language of the artifacts written to disk and pushed to GitHub) is detected separately in Step 1 from the project's README — see the Language policy section. The two axes are independent: you may speak Spanish to the user about a project whose artifacts are in English, or vice versa.

---

### Step 1 — Establish state

From the context above:

1. **Detect version source** in this priority order. The first match wins:
   - `package.json` → npm project (use `npm version --no-git-tag-version`)
   - `tiapp.xml` → Titanium project. Read the **top-level** `<version>X.Y.Z</version>` only — never touch `<module version="...">` entries.
   - `composer.json` → PHP project (edit the `"version"` field if present; many composer projects are versionless and use git tags only)
   - `Cargo.toml` → Rust project (edit `[package] version = "X.Y.Z"`)
   - `*.podspec` → CocoaPods (edit `s.version` line)
   - None of the above → **versionless** mode: commit + push + optional git tag, no file bump.

2. **Detect CHANGELOG strategy:**
   - If `CHANGELOG.md` exists, read it. Look for a `## [Unreleased]` heading (Keep-a-Changelog format).
     - If present → **promote mode**: rename that heading to the new version with today's date and append a fresh empty `## [Unreleased]` on top.
     - If absent → **generate mode**: synthesize the entry from semantic commits since the last tag.
   - If `CHANGELOG.md` does not exist → **skip** changelog updates (do not create one without asking).

3. **Detect README version references:** grep `README.md` for the current version string and for `version`/`v\d+\.\d+` badge patterns. Note any locations that may need updating.

4. **Detect project artifact language** per Axis 2 of the Language policy: read the first ~50 lines of `README.md` (skipping code blocks, badges, shell commands, identifier-only lines), classify the prose, tie-break with `CHANGELOG.md` then `git log`. Lock this language for the rest of the run — it will drive the CHANGELOG entry, the README edits, the commit message, the tag annotation, and the GitHub release (title and body).

5. **Print a one-screen summary** to the user (in the user's language, per Axis 1) with: project type, current version (or `<versionless>`), last tag, count of commits since last tag, CHANGELOG strategy, README references found, gh availability, current branch, **detected project artifact language** (and that the user can override it before confirming in Step 4).

---

### Step 2 — Infer the bump

Parse commit subjects since the last tag using Conventional Commits:

- Any commit with `BREAKING CHANGE:` in the body **or** `!:` after the type (e.g. `feat!:`) → **major**
- Any `feat:` (and no breaking) → **minor**
- Otherwise (`fix:`, `chore:`, `docs:`, `refactor:`, `perf:`, `test:`, `style:`, `ci:`, `build:`, or non-conventional) → **patch**

If `$ARGUMENTS` contains `patch`, `minor`, or `major`, that **overrides** the inference.

Compute the proposed next version. Show:

```
Last tag: vX.Y.Z
Inferred bump: <patch|minor|major>  (overridden by argument: <yes|no>)
Next version: vX.Y.(Z+1)   ← format depends on bump
Reason: N feat, M fix, K chore (or: argument override)
```

If there are **zero commits** since the last tag, abort with: "No commits since the last tag. Nothing to release."

---

### Step 3 — Compose the CHANGELOG entry

If **promote mode**: take the existing `[Unreleased]` body verbatim. Replace its heading with `## [X.Y.Z] - YYYY-MM-DD`. Insert a fresh empty `## [Unreleased]` block above it.

If **generate mode**: group commits by Conventional Commit type into Keep-a-Changelog sections:

```
## [X.Y.Z] - YYYY-MM-DD

### Added
- <feat: subjects, with the `feat:` prefix stripped>

### Fixed
- <fix: subjects, prefix stripped>

### Changed
- <refactor:, perf:, style: subjects>

### Removed
- <only if explicitly mentioned in commit messages>
```

Skip empty sections. Use today's date in `YYYY-MM-DD` format.

---

### Language policy (applies to Steps 1–5)

There are **two independent language axes**. Do not mix them.

#### Axis 1 — Interaction language (your conversation with the user)

**Always match the user's language.** Detect from the user's last 1–3 messages in this conversation — not from this command file (which is in English for distribution), and not from the project files. If the user has been speaking Spanish, every status summary, plan preview, confirmation prompt, error message, and final report you print **must be in Spanish**. If the user switches mid-flow, switch with them.

This is about what the user **reads on screen**. It does **not** affect what gets written to disk or to GitHub.

#### Axis 2 — Project artifact language (everything that gets written or pushed)

**Detect the project's audience language from `README.md`. That single decision drives every artifact.** The README is the canonical signal because it defines who the project is for: a Spanish README means a Spanish-speaking audience (typical for private / local projects), an English README means an international audience (typical for open source). Match that language across the board.

**Detection procedure** (Step 1 must do this):

1. Read the first ~50 lines of `README.md`, skipping code blocks, badges, shell commands, and identifier-only lines.
2. Classify the prose: Spanish, English, or other.
3. Tie-break with `CHANGELOG.md` (recent entries) if README is too short or ambiguous.
4. Final tie-break: the recent `git log` subjects.
5. If everything is ambiguous, default to English and tell the user in the Step 1 summary so they can correct you before Step 4.

The detected language applies to **all** of the following:

| Artifact | Language |
| --- | --- |
| New `CHANGELOG.md` entry | Project language |
| `README.md` edits (badges, version snippets) | Project language |
| Commit message (subject + body) | Project language |
| Tag annotation (`-m "..."`) | Project language |
| GitHub release title | Project language |
| GitHub release body / notes | Project language |

**No mixed-language releases.** If the README is in Spanish, the commit, tag, release title, and release body are all in Spanish. If the README is in English, all of them in English. The CHANGELOG entry being shipped also matches.

**Why this works:** the README is the project's "front door" and reflects the audience the maintainer chose. Aligning every public artifact (commits, tags, releases) to that same audience avoids the awkward private-project-with-English-commits or open-source-with-Spanish-tags split. Open source in English keeps coverage broad; private/local in Spanish keeps the team comfortable.

#### Spanish content rule (whenever writing Spanish, on either axis)

Preserve correct accents and eñes: sesión, electrónico, también, código, configuración, después, año, español, versión, añadir, corrección, contraseña. Do not strip or mangle tildes. The user has a standing rule about this and will catch it.

#### Overrides

If the user explicitly tells you to use a specific language for the artifacts (e.g. "haz los commits en inglés aunque el README esté en español"), that overrides Axis 2 detection for this run only.

---

### Step 4 — Present the full plan and STOP

Print, in this exact order:

1. **Files to modify** — explicit list with the type of edit (e.g. "package.json: bump 1.2.3 → 1.3.0", "CHANGELOG.md: promote [Unreleased] to [1.3.0]", "README.md: update version badge in line N").
2. **Commit message** — match the project **style** (Conventional Commits or whatever the recent log uses) and the **project artifact language** detected in Step 1 (Axis 2).
   - Conventional default: `chore(release): vX.Y.Z`.
3. **Tag name** — `vX.Y.Z`. The tag annotation message uses the project artifact language.
4. **Release notes preview** — the body that will be sent to `gh release create --notes`, in the project artifact language. If the CHANGELOG is in the same language (the normal case after Axis 2 alignment), the release notes can be the CHANGELOG section verbatim or a slight rewording; either way, no translation across languages.
5. **Push targets** — branch and tag refs that will be pushed.

Remember the two axes: the **plan preview** itself is shown to the user in the **user's** language (Axis 1). The **artifacts listed inside** follow the project language (Axis 2). These can differ — for example, you summarize the plan to a Spanish-speaking user about a project with an English README; the on-screen prose is Spanish, the proposed commit/tag/release is English.

Then **stop and wait** for explicit confirmation. Do **not** run any `git add`, `git commit`, `git push`, `git tag`, `gh release`, `npm version`, `Edit`, or `Write` calls in this step.

Acceptable confirmations from the user: `yes`, `sí`, `commitea`, `adelante`, `proceed`, `go`, `ship it`. Anything else (including silence, partial yes, "let me check", questions) means **do not proceed**.

---

### Step 5 — Execute (only after explicit confirmation)

Run in this order. Stop and report any failure; do **not** attempt destructive recovery.

1. **Bump the version file:**
   - npm: `npm version <patch|minor|major> --no-git-tag-version`
   - tiapp.xml: use `Edit` to change **only** the top-level `<version>` element. Verify there are no `<module version=...>` matches in your edit.
   - composer.json: use `npm pkg`-style or `Edit` on the `"version"` field. If absent and the project is git-tag-versioned, skip.
   - Cargo.toml: `Edit` the `[package] version = "X.Y.Z"` line.
   - podspec: `Edit` the `s.version = "X.Y.Z"` line.
   - Versionless: skip.

2. **Update CHANGELOG.md** with the entry composed in Step 3 (using `Edit` with sufficient context to disambiguate). Promote `[Unreleased]` or insert a new section right under the title/intro.

3. **Update README.md** if it has a version badge or install snippet referencing the old version. Use `Edit` per location identified in Step 1. Skip if there are no such references.

4. **Stage everything dirty:** `git add -A`. Per the user's standing rule, every dirty file is staged at release time, not just files touched in this command run. If anything looks unrelated or sensitive (`.env`, credentials, large binaries), pause and surface it before committing.

5. **Commit:** `git commit -m "<message from Step 4>"`. Use a HEREDOC for multi-line messages. **Never** pass `--no-verify`. If a pre-commit hook fails, surface the failure, fix the underlying issue, re-stage, and create a **new** commit (do not `--amend`).

6. **Push the branch:** `git push origin <current-branch>`.

7. **Tag and release** (only if remote exists and a version was bumped, or the user explicitly opted into a versionless tag). Per Axis 2 of the Language policy: tag annotation, release title, and release notes body all use the **project artifact language** locked in Step 1. Since the CHANGELOG is also in that language, the release notes can mirror or lightly rewrite the CHANGELOG section.
   - `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
   - `git push origin vX.Y.Z`
   - If `gh` is available and remote is GitHub: `gh release create vX.Y.Z --title "vX.Y.Z" --notes "<release notes in project language>"` (use HEREDOC for the notes).

8. **Report back** with the release URL (from `gh release create` stdout) and a one-line summary of what shipped.

---

## Hard restrictions (never violate)

- **Never** `git push --force` or `git push -f`.
- **Never** `git commit --amend` on commits that may already be pushed.
- **Never** `--no-verify`, `--no-gpg-sign`, or any hook-skipping flag unless the user explicitly asks.
- **Never** delete tags or branches.
- **Never** proceed past Step 4 without explicit confirmation. The slash command itself is consent to **invoke**, not consent to commit and push.
- If the working tree has merge conflicts or rebase-in-progress markers → **abort** with a diagnosis and let the user resolve manually.
- If currently on `main` / `master` and the repo has **no prior tag**, ask the user explicitly before creating the first tag (this is a meaningful one-way action).
- If the repo has no remote → run Steps 5.1–5.5 only; skip push, tag, and release. Tell the user.
- If the repo has a remote but `gh` is not available → run through 5.7's tag step but skip the GitHub release; tell the user how to create the release manually if they want to.
