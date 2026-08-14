# Authentication

What proves to npm that a publish is yours. Every long-lived option in this space was removed or put on a clock between November 2025 and January 2027, so the answer to "how do I stop typing my password" is different from what it was a year ago.

## The timeline

| When | What changed |
|---|---|
| November 2025 | Classic tokens removed from npm |
| December 2025 | Classic tokens revoked; `npm login` starts issuing a **two-hour session** instead of a token; CLI token management lands |
| 8 July 2026 | npm v12 goes GA with the install-time defaults, and the 2FA-bypass GAT deprecation is announced |
| 31 July 2026 | **Phase 1 applied**: 2FA-bypass tokens lose account, package and organization management |
| ~January 2027 | **Phase 2 expected**: 2FA-bypass tokens lose the ability to publish directly |

Sources: [npm classic tokens revoked, session-based auth and CLI token management](https://github.blog/changelog/2025-12-09-npm-classic-tokens-revoked-session-based-auth-and-cli-token-management-now-available/), [npm install-time security and GAT bypass2fa deprecation](https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation/), [Restricting npm bypass-2FA granular access tokens](https://github.blog/changelog/2026-07-31-restricting-npm-bypass-2fa-granular-access-tokens/).

## Why `npm login` keeps coming back

Since December 2025 `npm login` does not write a durable token. It opens a **session that lasts two hours**. Publish inside that window or authenticate again. This is not a token expiring early and there is no setting that extends it — it is the mechanism that replaced classic tokens.

The common symptom is a `401 Unauthorized` from `npm whoami` on a machine that "was logged in", because `~/.npmrc` still holds an `_authToken` line from the old regime that the registry no longer honors. `npm logout` clears it; the stale line is otherwise harmless and only produces confusing errors.

## The three token types, and which are alive

- **Classic tokens** — the long-lived, non-expiring strings people pasted into `.npmrc` and forgot. **Removed November 2025, revoked December 2025.** No flag, option or command brings them back.
- **Granular access tokens (GATs)** — the only token type still issued. Scoped to specific packages or organizations, with an expiry. **Tokens with write access cap at 90 days**, so a publish token has to be rotated four times a year.
- **GATs configured to bypass 2FA** — the subset built for unattended CI publishing. These are the ones being retired in two phases (below).

## The 2FA-bypass retirement, in two phases

**Phase 1 — already in effect since 31 July 2026.** A 2FA-bypass GAT can no longer perform sensitive account, package and organization management. Concretely: creating or deleting tokens; generating recovery codes; changing your password, email, profile or 2FA configuration; changing package access, maintainers, or **the trusted publishing configuration**; managing organization and team membership or their package grants. All of those now require an interactive 2FA challenge.

**Phase 2 — expected around January 2027.** The same tokens lose the ability to publish directly. Their publishing surface shrinks to reading private packages and *staging* a publish, where the package only becomes public after a human approves it with 2FA.

**What this does not touch:** GitHub personal access tokens, GitHub App tokens, and the `GITHUB_TOKEN` that Actions injects. The restriction is specific to npm granular access tokens. This clarification came with the 31 July post and was not in the 8 July announcement.

## The banner on npmjs.com

The 2FA-bypass notice shown when you log into npmjs.com is a **site-wide campaign banner**, not a diagnosis of the account looking at it. It appears whether or not you own a single bypass token.

To answer whether it applies: npmjs.com → avatar → **Access Tokens**, and read the **Bypass 2FA** column. An empty list, or a list where that column is blank on every row, means the deprecation does not touch the account at all. Expired tokens still show in that list and are worth deleting — a token that expired months ago is noise, and noise is what hides the one that matters.

## The three remaining paths

| Option | Friction per release | Lifetime |
|---|---|---|
| **A. Interactive** — `npm login`, then publish | one login (plus an OTP per publish) | indefinite |
| **B. GAT with 2FA bypass** in `~/.npmrc` | none | **90 days max**, and direct publish dies ~January 2027 |
| **C. Trusted publishing (OIDC)** from Actions | none | indefinite; the registry's own recommendation |

**B is the option the deprecation exists to discourage**: a long-lived secret on disk, renewable four times a year, with a known end date. Building it now means dismantling it within months.

**C is the only one that returns zero friction without an expiry.** See [trusted-publishing.md](trusted-publishing.md). A is a perfectly good fallback and stays available forever — if OIDC fails for any reason, `npm login` and a manual publish still work.

## Package-level hardening

npm can mark a package **"Require two-factor authentication and disallow tokens"**, which rejects any token regardless of its own configuration. On a package published by hand (option A) this is free protection. Its interaction with OIDC publishing is **not established here** — do not enable it on a package that publishes through trusted publishing without confirming the two coexist.
