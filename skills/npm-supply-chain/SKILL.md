---
name: npm-supply-chain
description: 'Publishing to npm and installing from it after the 2025–2026 supply-chain changes: why `npm login` now expires after two hours, classic tokens being gone, granular tokens capped at 90 days and losing direct publish around January 2027, and trusted publishing (OIDC) from GitHub Actions — no stored secret, provenance for free. Also the npm v12 install defaults, where lifecycle scripts, git dependencies and remote tarballs stay off until approved. Use when someone asks why npm demands a login on every publish, wants to publish from CI or GitHub Actions, asks about an NPM_TOKEN, a 2FA-bypass banner on npmjs.com, an OTP prompt, provenance, an `npm install` that broke or stopped running postinstall after an upgrade, or a tag that pushed and never published. Not for: choosing the version number, writing the CHANGELOG, or the release flow itself — that is `/release`.'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, AskUserQuestion
compatibility: Requires Python 3 (standard library only). The audit reads more when git and the gh CLI are available, and degrades cleanly without them.
---

# npm Supply Chain

How a package gets onto npm and what happens when one comes off it. Two halves of the same registry, both rewritten between November 2025 and July 2026: the credentials that used to sit in a file forever are gone, and the install that used to run a stranger's code by default no longer does.

Ground every answer in the reference files. This is the area where remembered knowledge is most likely to be a year out of date — the token type you remember may have been revoked, and the flag you remember may now default the other way.

Respond in the user's language. This skill is written in English for portability; the report should match whatever language the user is writing in.

## Required workflow (read before responding)

This SKILL.md is an **index**. The dates, the exact fields, the commands and the failure modes live in the reference files. **Reading this file alone is not enough.**

### Step 1 — Open the relevant reference files

| Task involves | Required reading |
|---|---|
| `npm login` expiring, session-based auth, classic tokens, granular access tokens, the 90-day cap, 2FA-bypass deprecation, the npmjs.com banner, which actions require interactive 2FA | [references/authentication.md](references/authentication.md) |
| Publishing from GitHub Actions, OIDC, the trusted-publisher form, `id-token: write`, Node/npm minimums, provenance, `NODE_AUTH_TOKEN` | [references/trusted-publishing.md](references/trusted-publishing.md) |
| npm v12 install behavior, `allowScripts`, `--allow-git`, `--allow-remote`, `npm approve-scripts`, the committed allowlist, packages that break | [references/install-defaults.md](references/install-defaults.md) |
| Moving a package off token auth: the order of operations, testing the guard, deleting orphaned secrets, cleaning `~/.npmrc` | [references/migration.md](references/migration.md) |
| Proving any of the above instead of assuming it: `gh api`, `gh secret list`, reading provenance, querying the registry directly, what npmjs.com shows when OIDC worked | [references/verification.md](references/verification.md) |

### Step 2 — Output contract

Every date, command, field name, version minimum, or registry behavior you cite carries its citation inline:

`[source: references/<file>.md]`

The citation is what separates a value you read from one that merely sounded right — written down, the two look identical, and the reader has no way to tell them apart. Cite while writing rather than collecting sources at the end, because by then you are reconstructing where something came from instead of recording it.

Example: *"Trusted publishing needs Node ≥ 22.14.0 and npm ≥ 11.5.1 on the runner [source: references/trusted-publishing.md]"*

### Step 3 — If you must answer from memory

If you write a claim without having read the reference that backs it, prepend `FROM_MEMORY (unverified):` to that claim. Do not hide it. Dates in this domain moved three times in eighteen months, and a confidently wrong one sends someone to build a credential that no longer works.

### Banned behaviors

- **Inventing a date, a version minimum, or a CLI flag that is not in the references.** The whole point of a dated reference is that "npm requires…" was true of a different npm; a plausible answer here costs the user a broken release, not a wrong opinion.
- **Recommending a long-lived publish token as the default.** It is the shape the registry is actively retiring, and pointing someone at it builds something they have to dismantle within months.
- **Reading a secret's value, or writing one into a file, a commit or a log.** You may list secret *names* and check whether anything references them; the value is never yours to handle. A token that appears in a transcript is a token that must be revoked.
- **Changing a package's npm settings on the user's behalf.** Registering a trusted publisher, editing token settings and changing package access all require an interactive 2FA challenge by design — hand over the exact steps and let the user do them.
- **Marking the answer complete without listing which reference files you read.** The list is what lets the reader tell a grounded answer from a remembered one.

## Measure the repo before advising it

Run the auditor rather than asking the user what their setup is — most of what matters is readable from disk and from `gh`:

```bash
python3 <SKILL_DIR>/scripts/auditar_npm.py            # the repo in the current directory
python3 <SKILL_DIR>/scripts/auditar_npm.py ~/code/foo # somewhere else
python3 <SKILL_DIR>/scripts/auditar_npm.py --no-network
```

Replace `<SKILL_DIR>` with the absolute "Base directory for this skill" from the system message that loaded this skill — the working directory here is the user's project, not this one, so a relative `scripts/…` resolves to nothing. The path also differs by install type (`~/.claude/plugins/cache/<plugin>/<version>/skills/npm-supply-chain` for a plugin install, `~/.agents/skills/npm-supply-chain` standalone), so read it rather than assuming it.

It reports: whether `~/.npmrc` and the project `.npmrc` carry a token and whether the registry still accepts it, Actions secrets that look like npm credentials and whether any workflow uses them, which workflows publish and how they authenticate, whether `package.json` and `.claude-plugin/plugin.json` agree on a version, shields.io badges pointing at a package name that does not exist, dependencies with install-time scripts, and the local npm version against v12.

It writes nothing. Everything it finds is a proposal for the user to approve, the same separation `seo-launch` keeps between auditing and installing.

## The shape of the answer

1. **Report what is actually there** — the auditor's output, not a generic checklist.
2. **Name the deadline that applies**, with its date and source. "This stops working" is only actionable with a when.
3. **Propose one path**, not a menu. For automated publishing the path is trusted publishing; say so and give the reason rather than laying out three options of which two are dead ends [source: references/authentication.md].
4. **Split the work by who can do it.** Everything in the repo is yours; everything on npmjs.com needs the user's interactive 2FA [source: references/migration.md].
5. **Verify afterwards against the registry**, not against the local CLI, and say which command proved it [source: references/verification.md].

## Anti-Patterns

**Credentials**

- Storing a publish token in `~/.npmrc` and treating it as permanent — classic tokens were removed in November 2025 and revoked in December, so the file usually holds a dead string that produces a confusing 401 long before any 2FA prompt [source: references/authentication.md]
- Reaching for a 2FA-bypass granular token to "stop the login prompts" — it caps at 90 days, it already lost account and package management in July 2026, and it loses direct publish around January 2027 [source: references/authentication.md]
- Leaving an `NPM_TOKEN` secret in a repo whose workflow no longer uses it. It is a live credential with nothing watching it [source: references/migration.md]
- Assuming the npmjs.com 2FA-bypass banner is about your account. It is a site-wide campaign notice; the Access Tokens page is what answers whether it applies to you [source: references/authentication.md]

**Trusted publishing**

- Omitting `permissions: id-token: write`. Without it there is no OIDC token to mint, `npm publish` falls back to token auth, and the failure reads like a credentials problem rather than a missing permission [source: references/trusted-publishing.md]
- Typing the local folder name into the publisher's `Repository` field. The claim is matched against the repository's canonical name on GitHub, which is not always how the folder is spelled on disk [source: references/trusted-publishing.md]
- Registering the publisher before the workflow file exists on the default branch, or renaming the workflow afterwards. The registration names the file, so the rename breaks publishing until npmjs.com is updated to match [source: references/trusted-publishing.md]
- Setting `NODE_AUTH_TOKEN` alongside OIDC "just in case". It puts the publish back on token auth and silently gives up provenance [source: references/trusted-publishing.md]
- Running the publish job on a Node old enough that the npm shipped with it cannot do OIDC — it degrades to token auth instead of erroring clearly [source: references/trusted-publishing.md]

**Installing**

- Upgrading to npm v12 and reading the missing `postinstall` as a broken package. The scripts are off by default now; `npm approve-scripts` is what turns the intended ones back on [source: references/install-defaults.md]
- Approving every script the prompt lists to make CI green. The allowlist is a security decision that gets committed and inherited by the whole team [source: references/install-defaults.md]
- Assuming a clean local install means a clean CI install when `ignore-scripts=true` sits in a personal `~/.npmrc`. The machine has been running v12 behavior for years and CI has not [source: references/install-defaults.md]

**Verifying**

- Reporting `npm view <pkg> version` as the state of the registry. The CLI caches it, and it will happily report the previous version minutes after a successful publish [source: references/verification.md]
- Calling a release published because the tag pushed. The tag starts a workflow; the workflow is what publishes, and it can fail on the version guard, on tests, or on a publisher that was never registered [source: references/verification.md]
