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

### What this command actually does (read this first)

`/release` is **not** "make a release commit from already-staged work". It is the full janitor: it takes a project that has been worked on without commits (or with mixed work + a release intent) and turns it into a clean, shipped release.

**Working tree dirty is the expected starting state, not an anomaly.** When the user invokes `/release` with 12 modified files since the last tag, what they want is:

1. Read every modified/untracked file, **understand the intent of each change**, and group them into **N semantic commits** (one feat per logical feature, one fix per logical bug, etc.) — NOT one giant "chore(release)" lump.
2. Then bump the version, update CHANGELOG, commit the release metadata, tag, push, and create the GitHub release.

So the plan presented to the user is **N+1 commits**: N semantic commits derived from the working tree, plus 1 release commit at the end (bump + CHANGELOG). Both sets feed the CHANGELOG entry and the GitHub release notes.

If the working tree is **already clean** (everything is already committed since the last tag), skip the semantic-commit pass and just do the release commit (this is the "git tag + bump only" mode).

If the working tree is **completely empty** AND there are zero commits since the last tag → abort, "Nothing to release."

### Verbosity discipline

1. **Steps 1, 2, 3 are silent.** Do all detection, grouping, inference, and composition internally. **Do not print intermediate status, summary tables, or per-step headers.**
2. **Step 4 is the only print before confirmation.** One compact block. No sub-section headers ("Files to modify / Commit message / Tag / Release notes / Push targets"). The N proposed commits go inside this block as a numbered list.
3. **Step 5 runs the actions silently.** Do not narrate each commit as it lands. The final report is **one line plus the URL**.
4. **Genuine anomalies** (branch is not main when expected to be, README/CHANGELOG language disagree, no remote, no `gh`, suspicious files like `.env` or large binaries about to be staged) go as `⚠️` lines **inside** the Step 4 block. A dirty working tree is **not** an anomaly — it is the input.

### Step 0 — Lock interaction language (do this BEFORE printing anything)

Before you produce any user-facing output, scan the user's last 1–3 messages in this conversation and determine their language. **This file is in English for distribution; that does not mean you respond in English.** Lock that detected language and use it for **every** message you print to the user from this point until the command ends — Step 1 summary, Step 2 inferred bump, Step 4 plan preview, Step 5 progress, errors, final report.

If the user has not yet said anything in this session (rare — `/release` invoked as the very first message), default to the language of the repo's `README.md`. If that is also unclear, default to English.

If the user switches language mid-flow, switch with them on the next message.

This rule is **Axis 1** of the Language policy below and is non-negotiable. **Axis 2** (the language of the artifacts written to disk and pushed to GitHub) is detected separately in Step 1 from the project's README — see the Language policy section. The two axes are independent: you may speak Spanish to the user about a project whose artifacts are in English, or vice versa.

---

### Step 1 — Establish state (silent)

Do all of this **internally**. Do not print a status summary or any "Step 1" header. The detected facts feed Step 4.

1. **Detect version source** (first match wins):
   - `package.json` → npm (`npm version --no-git-tag-version`)
   - `tiapp.xml` → Titanium. Edit only the **top-level** `<version>` element; never touch `<module version="...">` entries.
   - `composer.json` → PHP (edit `"version"` if present; many composer projects are versionless)
   - `Cargo.toml` → Rust (edit `[package] version = "X.Y.Z"`)
   - `*.podspec` → CocoaPods (edit `s.version`)
   - None → **versionless** mode (commit + push + optional tag).

2. **Detect CHANGELOG strategy:** if `CHANGELOG.md` exists and has `## [Unreleased]` → **promote mode**; if exists without it → **generate mode**; if missing → **skip CHANGELOG entirely** (do not create one without asking).

3. **Detect README version references:** grep `README.md` for the current version string and `v\d+\.\d+` badge patterns. Note locations that need updating, or note that none exist.

4. **Detect project artifact language** (Axis 2): scan the first ~50 lines of `README.md` (skip code blocks, badges, identifier-only lines), classify the prose; tie-break with `CHANGELOG.md` then `git log`. Lock this language for the run.

5. **Group the working tree into semantic commits** (the core janitor pass — do this carefully):

   For each modified, deleted, and untracked file, read enough of the diff or content to understand the **intent** of the change. Then group the files by intent into a list of proposed commits, in the order they should land.

   **Grouping heuristics:**
   - Files in the same module that implement a single feature → one `feat(scope):` commit.
   - Files that implement a single bug fix → one `fix(scope):` commit.
   - Refactors that don't change behavior → `refactor(scope):` (or `chore` if mechanical).
   - Renames, lint cleanups, formatting passes → `chore(scope):` or `style(scope):`.
   - Documentation-only changes (README, CHANGELOG, docs/) → `docs(scope):`. **Exception:** the release-commit's CHANGELOG/README/version bumps stay in the final release commit, not in a docs commit.
   - Test-only changes → `test(scope):`.
   - Build/CI config → `build(scope):` or `ci(scope):`.
   - Lockfiles (`package-lock.json`, `yarn.lock`, `Gemfile.lock`, `Cargo.lock`, `composer.lock`) follow whichever commit changed the corresponding manifest. If only the lockfile is dirty without a manifest change, group it into the release commit.
   - Mixed-intent files: if a single file legitimately covers two unrelated changes, propose one combined commit and flag it in Step 4 so the user can split it manually if they want — do not silently mis-attribute.

   **Files to exclude by default** (do not stage, mention them in Step 4 as "excluded"):
   - Screenshots in repo root (`*.png`, `*.jpg`, `*.jpeg`, `Screenshot*.png`, `Captura*.png`) unless they live inside an `assets/`, `docs/`, or similarly-blessed directory.
   - Editor scratch files: `*.swp`, `*.tmp`, `.DS_Store`, `Thumbs.db`.
   - Local-only env files: `.env`, `.env.local`, `*.local.json` if the project's `.gitignore` already excludes them but they appear because of `git add -A`.
   - Credentials, secret keys, large binaries that look unrelated to the project.
   When in doubt, **list the file in the Step 4 plan as "excluded — confirm?"** instead of silently dropping or silently including it.

   **Output of this step (held internally for Step 4):** an ordered list `[ {type, scope, subject, files[], body?}, ... ]` representing the N semantic commits, plus an "excluded" list.

6. **Detect README documentation gaps** (do NOT skip this — README maintenance is part of the release, not optional):

   For each proposed semantic commit (Step 1.5) and each existing commit since the last tag, ask: *does this change the project's user-visible surface?* Concretely, flag any of:

   - A new slash command (`commands/*.md` added).
   - A new CLI subcommand or flag (`bin/*` or `lib/commands/*` added/changed).
   - A new public API export, hook, MCP tool, or skill.
   - A new env var the user must set, a new config file the user must create.
   - A new install path, distribution channel, or compatibility platform.
   - A breaking change in any of the above.

   For each surface change found, **grep `README.md`** for the new symbol/name/path. If it is **not** mentioned in README:
   - Compose the documentation patch needed (a new row in an existing table, a new section under an existing heading, an updated bullet, etc.).
   - Hold this patch internally for Step 4 — it becomes part of the release commit (along with the version bump and CHANGELOG insert), NOT a separate semantic commit. README updates that document this release ship with the release.

   For surface changes that *are* already mentioned in README, do nothing.

   For non-surface changes (internal refactors, fixes that don't change behavior, dependency bumps), do nothing.

   **Also still update README** for: version badges, install snippets, or any reference to the old version that needs to bump to the new one.

7. **Detect main-alignment state.** Capture: the name of the project's primary branch (`main` or `master` — check `git symbolic-ref refs/remotes/origin/HEAD` or fall back to `main` then `master`), whether the current branch matches it, and whether `main` (locally and on origin) is reachable. This drives the optional merge prompt in Step 4.

8. **Note genuine anomalies** for Step 4: no remote, no `gh`, README/CHANGELOG languages disagree, an excluded file is borderline. **Do not** flag a dirty working tree itself — that's expected. **Do not** flag "branch is not main" as an anomaly either — handle it via the dedicated merge prompt below.

---

### Step 2 — Infer the bump (silent)

Look at **both** sources of changes and take the highest level:

- Existing commits since the last tag (from `git log`).
- The N **proposed** semantic commits from Step 1.5.

Apply Conventional Commits rules across that combined set:

- Any `BREAKING CHANGE:` or `!:` → **major**
- Any `feat:` (no breaking) → **minor**
- Otherwise → **patch**

`$ARGUMENTS` (`patch` / `minor` / `major`) overrides the inference.

If there are zero existing commits AND zero proposed commits AND the working tree is clean → abort: "Nothing to release."

---

### Step 3 — Compose the CHANGELOG entry (silent)

The CHANGELOG entry covers **everything that will ship** — both the existing commits since the last tag and the N proposed semantic commits from Step 1.5.

**Promote mode**: take the existing `[Unreleased]` body, **append** any new bullets derived from the proposed commits that aren't already represented, then rename the heading to `## [X.Y.Z] - YYYY-MM-DD`. Insert a fresh empty `## [Unreleased]` above.

**Generate mode**: build the entry from the union of (existing commits since tag) + (proposed semantic commits), grouped by type, in the project artifact language detected in Step 1:

```
## [X.Y.Z] - YYYY-MM-DD

### Added
- <feat: subjects from both sources, prefix stripped>

### Fixed
- <fix: subjects from both sources>

### Changed
- <refactor:, perf:, style: subjects>

### Removed
- <only when explicitly mentioned>
```

Skip empty sections. Use today's date. Don't double-count when an existing commit and a proposed commit describe the same work — pick the clearer wording.

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

### Step 4 — Present the plan in ONE block and STOP

This is your **only** print to the user before confirmation. One block. Compact. No tables, no per-section sub-headers. The block is shown in the user's language (Axis 1); the artifacts quoted inside use the project language (Axis 2).

The block has three parts (in this order, in one continuous block):

**Part A — header line + anomalies**
```
**Release plan: vA.B.C → vX.Y.Z** (<bump> — <project type>, artifacts en <language>, branch <name>)

⚠️ <one line per genuine anomaly>   ← only if any; do NOT flag dirty working tree
```

**Part B — semantic commits from the working tree** (omit this part entirely if the working tree was already clean)
```
N commits semánticos antes del release:

1. <type>(<scope>): <subject>
   • <files>
2. ...
N. ...

Excluded: <files the user should confirm or none>
```

**Part C — release commit + tag + push**
```
CHANGELOG entry:

## [X.Y.Z] - YYYY-MM-DD
### Added
- ...
### Fixed
- ...

README updates (gaps found): <one-line per gap, e.g. "add /release row to Available commands table + new section">  ← omit this line if no gaps
Release commit: bumps <version-file> A.B.C→X.Y.Z, inserts CHANGELOG section, applies README updates. Subject: `<exact line>`.
Tag + push: vX.Y.Z to <branch> + tag.
GitHub release: notes = CHANGELOG section above.

Branch <branch> → <main-branch>? (default: no; responde "merge" para fast-forward, "PR" para pull request)   ← include ONLY when current branch ≠ main/master; localize to user's language

¿Procedo?  ← in the user's language
```

**Rules for this block:**

- The CHANGELOG entry is shown **once**. Don't paste it again under "Release notes" — say "notes = CHANGELOG section above".
- The N semantic commits are listed compactly: type + scope + subject on one line, files on the next. No separate body text per commit unless a commit truly needs one.
- "Excluded" lists files you decided not to stage (screenshots in root, scratch files, suspicious binaries) so the user can override your decision before confirming.
- A single bold "Release plan: ..." is the only header. No "Step 4 — Plan" preamble.
- The closing question is in the user's language: `¿Procedo?` (Spanish), `Proceed?` (English), etc.
- If there is something genuinely ambiguous (a file that could be either feat or fix, a possibly-sensitive file, a branch-vs-main question), put it in `⚠️` and ask the user to clarify in the same message — do not block on a separate round-trip if you can present the question alongside the plan.

Then **stop and wait**. Do **not** run any `git add`, `git commit`, `git push`, `git tag`, `gh release`, `npm version`, `Edit`, or `Write` calls in this step.

Acceptable confirmations:

- **Without merge** (default): `yes`, `sí`, `commitea`, `adelante`, `proceed`, `go`, `ship it`. → execute Phases 1–3 of Step 5 only.
- **With fast-forward merge** to main/master: `merge`, `sí merge`, `proceed and merge`, `merge yes`, `ship and merge`. → execute Phases 1–3, then Phase 4 with `mode=merge`.
- **With PR**: `pr`, `PR`, `abrir PR`, `proceed PR`, `release and PR`. → execute Phases 1–3, then Phase 4 with `mode=pr`. Requires `gh` available.

Anything else (silence, partial yes, "let me check", questions) means **do not proceed**. If the user proposes changes (e.g. "merge commits 2 and 3", "split commit 5", "skip commit 7", "different subject for #4"), apply them and re-present a refreshed Step 4 block before executing. The merge-mode confirmation can also be revised — e.g. user says "yes but no merge" → mode=none; "merge actually" after an initial plain yes → re-confirm before doing it.

---

### Step 5 — Execute (silent until done)

Run the actions below **without** narrating each one. No "committing 1/7...", "staging files...", "pushing tag..." progress messages. The user sees one final report at the end.

If any step fails, **stop** and surface the failure with a diagnosis — do not attempt destructive recovery and do not skip ahead.

**Phase 1 — Land the N semantic commits from the working tree (skip if working tree was already clean).**

For each commit `i` in the proposed list, in order:

1. `git add <exact files for commit i>` (use explicit paths — do **not** `git add -A` here; that would mix unrelated files into a single commit).
2. `git commit -m "<type>(<scope>): <subject>"`. Use a HEREDOC if there's a multi-line body. **Never** `--no-verify`. If a pre-commit hook fails, fix the root cause, re-stage the same files, and retry the same commit (do not silently skip and do not `--amend`).

After Phase 1, the working tree should be clean except for files explicitly listed as "Excluded" in Step 4.

**Phase 2 — Release commit.**

1. **Bump the version file:**
   - npm: `npm version <patch|minor|major> --no-git-tag-version`
   - tiapp.xml: `Edit` only the **top-level** `<version>` element. Verify no `<module version=...>` matches in your edit.
   - composer.json: `Edit` `"version"` if present; skip if absent.
   - Cargo.toml: `Edit` `[package] version = "X.Y.Z"`.
   - podspec: `Edit` `s.version`.
   - Versionless: skip.

2. **Update `CHANGELOG.md`** with the Step 3 entry. Promote `[Unreleased]` or insert above the most recent version section.

3. **Update `README.md`** with everything identified in Step 1.6:
   - The documentation gap patches (new command rows, new sections, updated tables) so the README reflects the user-visible surface being shipped in this release.
   - Plus any version badge / install snippet that referenced the old version.
   Apply with `Edit` per location. Skip only if Step 1.6 found nothing.

4. **Stage exactly the release-commit files** (the bumped version file + lockfile if `npm version` updated it + `CHANGELOG.md` + `README.md` if changed). Use explicit `git add <paths>`, not `git add -A`.

5. **Commit:** `git commit -m "chore(release): vX.Y.Z"` (or the project's release-commit convention).

**Phase 3 — Push, tag, GitHub release.**

1. `git push origin <current-branch>`.
2. Tag (only if remote exists and a version was bumped, or user opted into a versionless tag):
   - `git tag -a vX.Y.Z -m "Release vX.Y.Z"`  ← annotation in project language
   - `git push origin vX.Y.Z`
3. If `gh` is available and remote is GitHub: `gh release create vX.Y.Z --title "vX.Y.Z" --notes "<CHANGELOG section>"` (HEREDOC for notes).

**Phase 4 — Optional main alignment** (only if user confirmed `merge` or `PR`).

For `mode=merge` (fast-forward only):

1. `git fetch origin` to make sure local `main` knows about origin.
2. `git checkout <main-branch>`.
3. `git pull --ff-only origin <main-branch>` — bring local main up to date.
4. `git merge --ff-only <feature-branch>` — must be fast-forward. If main has diverged (someone else merged in the meantime), this fails cleanly. **Do not** retry with `--no-ff` or any other strategy: abort, leave the user on `<main-branch>`, and tell them to resolve manually. The release on the feature branch is intact regardless.
5. `git push origin <main-branch>`.
6. **Stay on `<main-branch>`.** Do NOT `git checkout` back to the feature branch. Confirming `merge` is the user's signal that the feature branch is done — landing them on main matches that intent and avoids a silent branch-switch after a "ship it" action. The feature branch still exists locally; the user can `git branch -d <feature-branch>` when ready. (PR mode is different — see below — because the branch is still live.)

For `mode=pr` (open a PR via `gh`):

1. Compose the PR title from the release: `Release vX.Y.Z` (in project artifact language).
2. Compose the PR body from the CHANGELOG entry (the `## [X.Y.Z]` section).
3. `gh pr create --base <main-branch> --head <feature-branch> --title "..." --body "..."` (HEREDOC for body).
4. Capture the PR URL from `gh` stdout.

If `mode=none` (default), skip this phase entirely.

If a Phase 4 step fails, the release itself is already shipped (Phases 1–3 succeeded). Surface the merge/PR failure as a non-fatal note in the final report — do not unwind the release.

**Phase 5 — Final report (one line plus URL).**

```
✓ vX.Y.Z → <release URL>
   N+1 commits on <feature-branch>, latest <short hash>  ·  <optional one-line note>
```

The "optional note" only appears if something was non-routine — examples:
- `merged to main; now on <main-branch>` (when Phase 4 ran successfully with mode=merge; include the new main HEAD short hash)
- `PR opened: <pr-url>` (when Phase 4 ran with mode=pr)
- `merge to main aborted: main has diverged — resolve manually`
- `tag is on feature branch; main not aligned`
- `GitHub release skipped (no gh)`
- `excluded file left in working tree: screenshot.png`

If everything was routine and no merge was requested, the second line is just the commit summary.

---

## Hard restrictions (never violate)

- **Never** `git push --force` or `git push -f`.
- **Never** `git commit --amend` on commits that may already be pushed.
- **Never** `--no-verify`, `--no-gpg-sign`, or any hook-skipping flag unless the user explicitly asks.
- **Never** delete tags or branches.
- **Never** merge to main with anything other than `--ff-only`. If fast-forward is not possible, abort and let the user resolve. Do not fall back to `--no-ff`, `-X theirs`, `-X ours`, or any rebase strategy.
- **Never** proceed past Step 4 without explicit confirmation. The slash command itself is consent to **invoke**, not consent to commit and push.
- If the working tree has merge conflicts or rebase-in-progress markers → **abort** with a diagnosis and let the user resolve manually.
- If currently on `main` / `master` and the repo has **no prior tag**, ask the user explicitly before creating the first tag (this is a meaningful one-way action).
- If the repo has no remote → run Steps 5.1–5.5 only; skip push, tag, and release. Tell the user.
- If the repo has a remote but `gh` is not available → run through 5.7's tag step but skip the GitHub release; tell the user how to create the release manually if they want to.
