# Trusted publishing (OIDC)

The runner proves who it is instead of carrying a secret. GitHub Actions mints a short-lived OIDC credential describing the exact repository, workflow and ref that is running; npm checks that description against the trusted publisher registered for the package and, if it matches, accepts the publish. Nothing is stored anywhere: there is no token to rotate, no secret to leak, no session to keep alive.

Two consequences worth stating up front: **provenance is attached automatically** to a publish made this way — npm links the published version to the exact commit and workflow run — and the registry records the publisher as **GitHub Actions** rather than a person.

## The registration on npmjs.com

Per package, under **Settings → Trusted Publisher → GitHub Actions**:

| Field | Value |
|---|---|
| Organization or user | the GitHub owner, e.g. `macCesar` |
| Repository | the repository name **as GitHub spells it** |
| Workflow filename | the file's basename with extension, e.g. `publish.yml` |
| Environment | empty, unless the job declares `environment:` |

Three ways this goes wrong:

- **The `Repository` field is the canonical repository name, not the local folder name.** A project cloned into `~/Developer/TiTools` can live at `github.com/macCesar/titools`; the OIDC claim carries the canonical one, and a mismatch fails the publish with an authorization error that says nothing about capitalization. Read it from the API rather than from the filesystem — see [verification.md](verification.md).
- **The workflow filename must match exactly**, extension included. Renaming the file later breaks publishing until the registration on npmjs.com is updated, and the break surfaces only on the next release.
- **Registering it requires an interactive 2FA challenge.** Changing the trusted publishing configuration is one of the operations 2FA-bypass tokens lost on 31 July 2026 [source: authentication.md]. This is a step only the package owner can do; it cannot be automated or done on their behalf.

## Order of operations

1. Commit and **push the workflow to the default branch** first. The registration points at a file; the file should exist.
2. Register the publisher on npmjs.com.
3. Push a tag.

Doing 2 before 1 is not fatal, but it leaves a registration pointing at nothing and the first release fails for a reason that looks like the registration is wrong.

## The workflow

The template lives at `assets/publish.yml` in this skill. The parts that matter:

```yaml
permissions:
  contents: read
  id-token: write   # without this there is no OIDC token and npm falls back to token auth
```

`id-token: write` is the whole switch. Omit it and the publish does not error with "you forgot a permission" — it degrades to looking for a token, finds none, and fails as a credentials problem.

```yaml
- uses: actions/setup-node@v7
  with:
    node-version: '24'
    registry-url: 'https://registry.npmjs.org'
```

**Minimums: Node ≥ 22.14.0 and npm ≥ 11.5.1.** Older combinations do not know how to present the OIDC credential and quietly fall back to token auth. `registry-url` is what makes `setup-node` write the `.npmrc` pointing at the public registry.

**Do not set `NODE_AUTH_TOKEN`.** It is the environment variable `setup-node` wires up for token auth; present, it puts the publish back on a secret and gives up provenance. A trusted-publishing workflow has no `env:` block on the publish step and no `secrets.*` reference anywhere.

Pin the actions. `actions/checkout` and `actions/setup-node` are on v7 as of August 2026.

## The version guard

The template compares the pushed tag against every version file in the repo before publishing anything:

```bash
tag="${GITHUB_REF_NAME#v}"
pkg=$(node -p "require('./package.json').version")
[ "$tag" = "$pkg" ] || { echo "::error::tag $tag does not match package.json $pkg"; exit 1; }
```

It exists because a tag and a manifest can disagree and npm will happily publish the manifest's version under a tag that says something else. In a repo that also ships a Claude Code plugin, `.claude-plugin/plugin.json` is a second version file and belongs in the same check — TiTools published 2.6.0 to npm while its `plugin.json` still read 3.0.0, and the marketplace announced a version that did not exist.

Costs one step, removes the whole class of mistake, and fails before `npm ci` so a bad tag never reaches the registry.

## What the release flow looks like afterwards

```
/release  →  creates the tag and pushes it  →  Actions publishes
```

No `npm login`, no two-hour session, no OTP. The human checkpoint does not disappear; it moves to the tag, which is still created deliberately after reviewing the diff.

If a publish fails for any reason, nothing is trapped: `npm login` and a manual `npm publish` remain available as they always were [source: authentication.md].
