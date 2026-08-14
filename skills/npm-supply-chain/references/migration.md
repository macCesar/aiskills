# Migrating a package to trusted publishing

Done once per package. The order matters, because two of the steps can only be done by the package owner with an interactive 2FA challenge, and one of them is easy to test cheaply before it can cost a bad publish.

## 1. Audit what is there

Before changing anything, establish the starting state — this is what `scripts/auditar_npm.py` reports, and each finding maps to a step below:

- **Tokens on disk**: `~/.npmrc` and any project `.npmrc`. An `_authToken` line from before December 2025 is dead weight producing confusing 401s [source: authentication.md].
- **Actions secrets**: anything named like an npm credential (`NPM_TOKEN` and variants). A secret no workflow references is orphaned — a live credential with nothing watching it.
- **Existing workflows**: which ones publish, and whether they authenticate with a token or with OIDC.
- **Version files**: `package.json`, and `.claude-plugin/plugin.json` if the repo also ships a Claude Code plugin. They feed the guard in step 2.
- **Install-time scripts** in the dependency tree, which is a different question but the same audit [source: install-defaults.md].

## 2. Add the workflow and push it

Copy `assets/publish.yml`, adjust the version files in the guard to match the repo, commit, push to the default branch. Details of each line are in [trusted-publishing.md](trusted-publishing.md).

The file must be on GitHub before the registration points at it, and before any tag is pushed.

## 3. Register the trusted publisher

npmjs.com → the package → **Settings → Trusted Publisher → GitHub Actions**, with the four fields from [trusted-publishing.md](trusted-publishing.md). Read the repository name from the GitHub API rather than from the local folder name — see [verification.md](verification.md) for the command.

**Only the package owner can do this**, interactively, with 2FA. It is one of the operations 2FA-bypass tokens lost in July 2026 [source: authentication.md]. Hand over the exact field values; do not attempt it on their behalf.

If the package is configured as *"Require two-factor authentication and disallow tokens"*, leave that setting alone. Whether it coexists with OIDC publishing is not established here.

## 4. Test the guard before trusting it

The version guard is the one part of the workflow that can be verified without publishing anything. Run its logic locally against a tag that should pass and one that should fail:

```bash
tag="1.18.1"; node -p "require('./package.json').version"     # expect a match
tag="9.9.9";  node -p "require('./package.json').version"     # expect a mismatch → the job must exit 1
```

A guard that passes everything is not a guard. Confirm both directions before relying on it — the same discipline as running a positive control on any measuring instrument.

## 5. First real release

Push a tag and watch the run rather than assuming it. The verification commands are in [verification.md](verification.md). Three things distinguish a real success from a plausible one: the workflow run is green, the registry (not the local CLI cache) reports the new version, and npmjs.com lists the publisher as **GitHub Actions** rather than a username.

If it fails, nothing is lost: `npm login` plus a manual publish is still the fallback, and it stays available permanently [source: authentication.md].

## 6. Clean up what the old flow left behind

- **Orphaned Actions secrets.** `gh secret delete NPM_TOKEN --repo <owner>/<repo>` once nothing references it. An unused publish credential is strictly a liability.
- **Dead `_authToken` in `~/.npmrc`.** `npm logout` removes it. Not dangerous, but it is what makes `npm whoami` answer 401 on a machine that looks logged in.
- **Empty workflow directories** left by a removed CI file, and any documentation that still tells the reader to run `npm publish` by hand or to set a token.
- **Expired tokens on npmjs.com.** They do nothing, and they hide the one entry that matters in the list.

Delete secrets only with the user's agreement, and never print a secret's value — listing names is enough to reason about orphans.

## What the release flow becomes

`/release` still does everything it did: semantic commits, version bump, CHANGELOG, tag, push. The publish is what moved — it now happens because the tag landed, not because someone typed `npm publish`. Nothing needs to run by hand, and the release is not finished until that workflow run is green.
