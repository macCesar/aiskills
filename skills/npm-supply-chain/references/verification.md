# Verification

Every claim in this area is checkable in one command, which is the reason none of them should be asserted from memory. This file is the list of those commands and, for each, what a wrong answer looks like.

## The repository's canonical name

The trusted publisher matches the repository as GitHub spells it, which is not necessarily how the folder is spelled on disk:

```bash
gh api repos/<owner>/<repo> --jq .full_name
```

Run it before handing the user any value to type into a form. A folder named `TiTools` whose repository is `macCesar/titools` produces an OIDC claim that never matches a registration typed from the filesystem, and the resulting failure says nothing about capitalization.

This is the general rule for anything the user has to copy by hand: verify the exact string first, then hand it over.

## Credentials, without reading them

```bash
gh secret list --repo <owner>/<repo>          # names and dates only, never values
grep -rl "secrets\." .github/workflows/       # which workflows reference any secret
npm whoami                                    # 401 means the local session or token is dead
```

A secret that appears in `gh secret list` and in no workflow is orphaned. Names and timestamps are enough to establish that; the value is never needed and must never be printed.

## Whether a workflow publishes, and how

```bash
grep -l "npm publish" .github/workflows/*.yml
grep -n "id-token\|NODE_AUTH_TOKEN\|NPM_TOKEN" .github/workflows/*.yml
```

`id-token: write` present and no token reference means OIDC. A `NODE_AUTH_TOKEN` or `NPM_TOKEN` reference means token auth, regardless of what the file is named or what a comment claims.

## The registry, not the CLI cache

```bash
npm view <pkg> version            # ← do not report this as the state of the registry
curl -s https://registry.npmjs.org/<pkg> | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dist-tags'])"
```

**`npm view` is cached and it lies.** Measured on 2026-08-14: minutes after `@maccesar/aiskills` 1.18.1 published successfully, the local `npm view` still answered 1.18.0 while a direct request to the registry already returned 1.18.1. Reporting the cached answer as a failed publish sends someone to debug a release that worked.

For a scoped package the URL encodes the slash: `https://registry.npmjs.org/@maccesar%2Faiskills`.

## Provenance and the publisher

```bash
npm view <pkg> --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('dist',{}).get('attestations'))"
```

The visual signal is stronger and takes one glance: on npmjs.com, the package's version list shows **`GitHub Actions`** in the publisher column where a manually published package shows a username. That is trusted publishing made visible — npm recorded that a workflow identified by OIDC uploaded the package — and it is what backs the provenance badge.

## The workflow run behind a tag

A pushed tag is not a publish. It starts a run, and the run can fail on the version guard, on the tests, or on a publisher that was never registered:

```bash
gh run watch                                  # follow the run started by the tag
gh run list --workflow=publish.yml --limit 5  # after the fact
```

A release is finished when that run is green and the registry confirms the version — not when `git push origin v1.2.3` returns.

## Badges

A shields.io badge asks the registry for a package by name. If the name is wrong the badge renders "package not found" rather than erroring, so a broken badge survives for months:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://registry.npmjs.org/<name-exactly-as-the-badge-spells-it>
```

The failure mode is specific to **scoped packages**: a README badge that says `npm/dm/aiskills` for a package published as `@maccesar/aiskills` looks plausible and reports nothing. It hid a real number here — 568 downloads per month — across three badges for months. An unscoped package cannot have this bug, since the badge name and the package name are the same string.

npmjs.com renders the README of the **published version**, so correcting a badge requires a release, not just a push to the default branch.

## Install-time scripts in the tree

```bash
npm approve-scripts --allow-scripts-pending          # authoritative: what npm itself would ask about
```

Reading each dependency's `scripts` block is the offline approximation and is what the auditor in this skill does; the command above is what npm actually evaluates [source: install-defaults.md].
