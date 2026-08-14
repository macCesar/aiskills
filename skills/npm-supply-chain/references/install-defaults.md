# Install defaults in npm v12

npm v12 went generally available and became `latest` on 8 July 2026. It turns on the install-time security defaults announced in June: three things that used to happen automatically during `npm install` are now opt-in.

Source: [npm install-time security and GAT bypass2fa deprecation](https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation/).

## What changed

| Before | npm v12 |
|---|---|
| Dependency lifecycle scripts (`preinstall`, `install`, `postinstall`) and implicit node-gyp builds ran automatically | **Do not run** unless explicitly allowed (`allowScripts` defaults to off) |
| Git dependencies (`github:user/repo`), direct or transitive, resolved | **Not resolved** unless allowed (`--allow-git` defaults to none) |
| Dependencies from remote URLs (an `https://` tarball) resolved | **Not resolved** unless allowed (`--allow-remote` defaults to none) |

The reason is the ecosystem's most exploited vector: a compromised package put its payload in a `postinstall` and ran it on your machine as a side effect of `npm install`. That code is now inert until someone approves it.

All three were available behind warnings from **npm 11.16.0**, so a project can be rehearsed against the new behavior before upgrading the major.

## The migration flow

```bash
npm approve-scripts --allow-scripts-pending
```

It lists the packages asking to run install scripts. Approve the ones you trust, and **commit the resulting allowlist in `package.json`** so the team and CI inherit the same decision rather than each machine answering the prompt differently.

Two things about that allowlist: it is a security decision, not a build chore — approving everything the prompt offers to make CI green defeats the change entirely — and it is inherited, so whoever commits it is deciding for everyone.

## What actually breaks

Nothing in a dependency tree of pure JavaScript. The packages that notice are the ones that **download or compile a binary during install**: `sharp`, `puppeteer`, native CLI wrappers, anything using node-gyp. In a Laravel or Vite project the symptom shows up one step removed — assets that stop compiling after a clean `npm ci`.

The way to know without guessing is to run `npm approve-scripts --allow-scripts-pending` in each repo and read the list. A package whose `package.json` declares no `preinstall` / `install` / `postinstall` and pulls no node-gyp dependency has nothing to approve, and its users see no prompt at all.

## The trap: a personal `ignore-scripts`

A developer with `ignore-scripts=true` in `~/.npmrc` has been living with the main v12 behavior for years and will not notice the upgrade at all. Their CI, running with the default configuration, has not — so "it installs fine on my machine" is not evidence about the pipeline, in either direction.

Check both: the personal `~/.npmrc`, the project `.npmrc`, and what the CI job actually runs. Only the last one describes what users and the pipeline experience.

## As a package author

The question is what your *dependents* see. If none of your dependencies declares an install script, a user on npm v12 installs your package without a single approval prompt. This is worth measuring before publishing rather than after an issue arrives: the auditor in this skill reports it, and so does reading the `scripts` block of every installed `package.json`.
