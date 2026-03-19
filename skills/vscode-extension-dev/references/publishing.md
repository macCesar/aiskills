# Publishing VS Code Extensions

Complete workflow from local build to Marketplace.

## Prerequisites

```bash
# Install vsce (Visual Studio Code Extensions CLI)
npm install -g @vscode/vsce

# Verify installation
vsce --version
```

## Personal Access Token (PAT)

1. Go to https://dev.azure.com → User Settings → Personal Access Tokens
2. Create new token:
   - **Organization**: All accessible organizations
   - **Scopes**: Marketplace → Manage
   - **Expiration**: Set a reasonable duration
3. Save the token securely — it's shown only once

```bash
# Login with your publisher
vsce login your-publisher-id
# Paste token when prompted
```

## Publisher Setup

1. Go to https://marketplace.visualstudio.com/manage
2. Create a publisher if you don't have one
3. Your `publisher` field in `package.json` must match exactly

## .vscodeignore

Controls what goes into the VSIX package. Keep it small.

```
.vscode/**
.vscode-test/**
src/**
test/**
out/**
node_modules/**
.gitignore
.eslintrc*
tsconfig.json
esbuild.js
**/*.ts
**/*.map
.github/**
```

**Key rules:**
- Source `.ts` files should be excluded — only ship bundled `dist/`
- `node_modules/` excluded when using esbuild bundling
- Keep `README.md`, `CHANGELOG.md`, `LICENSE`, and `media/` (icons, images)

## Pre-Publish Checklist

Before running `vsce publish`:

1. **README.md** — Must exist and be non-empty (Marketplace listing page)
2. **CHANGELOG.md** — Document what changed in this version
3. **Icon** — Add `"icon": "resources/icon.png"` to `package.json` (128x128 PNG)
4. **Repository** — Add `"repository"` field to `package.json`
5. **License** — Add `"license"` field and include a LICENSE file
6. **Version** — Bump version in `package.json`
7. **Build** — Run `npm run package` to verify bundling works
8. **Test** — Run `npm test` to verify all tests pass
9. **Package** — Run `vsce package` to create VSIX locally and verify contents

```bash
# Create VSIX for local testing
vsce package

# Install locally to verify
code --install-extension my-extension-0.0.1.vsix

# Check package size
ls -la *.vsix
```

## Publishing

### Manual Publish

```bash
# Bump version and publish
vsce publish patch  # 0.0.1 → 0.0.2
vsce publish minor  # 0.0.2 → 0.1.0
vsce publish major  # 0.1.0 → 1.0.0

# Or publish current version
vsce publish
```

### Publish with Specific Version

```bash
vsce publish 1.2.3
```

## GitHub Actions CI/CD

### Test on Every Push

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - run: npm ci
      - run: npm run compile
      - run: xvfb-run -a npm test
        if: runner.os == 'Linux'
      - run: npm test
        if: runner.os != 'Linux'
```

### Publish on Tag

```yaml
# .github/workflows/publish.yml
name: Publish

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - run: npm ci
      - run: npm run compile
      - run: xvfb-run -a npm test

      # Publish to VS Code Marketplace
      - run: npx @vscode/vsce publish
        env:
          VSCE_PAT: ${{ secrets.VSCE_PAT }}

      # Publish to Open VSX (optional)
      - run: npx ovsx publish -p ${{ secrets.OVSX_PAT }}
        if: env.OVSX_PAT != ''
        env:
          OVSX_PAT: ${{ secrets.OVSX_PAT }}
```

**Required secrets:**
- `VSCE_PAT`: Your Azure DevOps Personal Access Token
- `OVSX_PAT` (optional): Open VSX Registry access token

## Open VSX Registry

For VS Code forks (VSCodium, Gitpod, etc.) that don't use the Microsoft Marketplace.

```bash
# Install ovsx CLI
npm install -g ovsx

# Publish
ovsx publish -p YOUR_OPENVSX_TOKEN

# Or publish an existing VSIX
ovsx publish my-extension-0.0.1.vsix -p YOUR_OPENVSX_TOKEN
```

Get your token at https://open-vsx.org.

## Version Bumping Strategies

### Semantic Versioning

- **Patch** (0.0.x): Bug fixes, docs updates
- **Minor** (0.x.0): New features, backward-compatible
- **Major** (x.0.0): Breaking changes

### Recommended Workflow

```bash
# 1. Update CHANGELOG.md with changes
# 2. Bump version
npm version patch -m "Release %s"
# This updates package.json and creates a git tag

# 3. Push with tags
git push origin main --tags
# CI/CD picks up the tag and publishes
```

### Pre-release Versions

```bash
# Publish as pre-release
vsce publish --pre-release

# In package.json, use pre-release versions:
# "version": "1.0.0-beta.1"
```

Pre-release extensions show a "Pre-release" badge in the Marketplace and users can opt in/out.

## Verifying Your Published Extension

After publishing:

1. Check https://marketplace.visualstudio.com/items?itemName=publisher.extension-name
2. Verify README renders correctly
3. Install from the Marketplace in VS Code
4. Test that all features work in a clean VS Code instance

## Common Publishing Errors

| Error | Fix |
| ----- | --- |
| `Missing publisher name` | Add `"publisher"` to `package.json` |
| `A '+0.0.0' version is not valid` | Use valid semver in `"version"` |
| `README.md not found` | Create a README.md in the root |
| `VSIX too large` | Check `.vscodeignore`, exclude `node_modules/` |
| `401 Unauthorized` | Regenerate PAT, ensure Marketplace scope |
| `Extension already exists` | Your `publisher.name` combo is taken |
