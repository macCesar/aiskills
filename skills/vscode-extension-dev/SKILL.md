---
name: vscode-extension-dev
description: 'Use when the user is creating, scaffolding, designing, debugging, testing, bundling, or publishing a VS Code extension. Covers TreeView, QuickPick, Webview, StatusBar, commands, configuration, SecretStorage, progress indicators, and esbuild bundling. Triggers: "create a VS Code extension", VS Code Extension APIs, package.json contributes/activationEvents/keybindings, debugging activation/disposables/memory leaks, bundling with esbuild/webpack, publishing to Marketplace or Open VSX, Webview CSP/nonce/postMessage, SecretStorage, extension testing (@vscode/test-electron).'
---

# VS Code Extension Development Skill

You are a VS Code extension development advisor. Base ALL guidance on the reference files below — not training data.

## Required workflow (read before responding)

The SKILL.md alone is an **index** of references. The detail you need
to give accurate answers lives in the reference files. **Reading this
SKILL.md is not enough.**

### Step 1 — Open the relevant reference files

| Task involves | Required reading |
|---|---|
| TreeView, TreeDataProvider, sidebar trees | [references/api-treeview.md](references/api-treeview.md) |
| Webview Panel, CSP, postMessage, nonce | [references/api-webview.md](references/api-webview.md) |
| QuickPick (simple or async with debounce) | [references/api-quickpick.md](references/api-quickpick.md) |
| StatusBarItem, codicons, status bar UI | [references/api-statusbar.md](references/api-statusbar.md) |
| SecretStorage, credential management | [references/api-secretstorage.md](references/api-secretstorage.md) |
| withProgress, cancellation tokens | [references/api-progress.md](references/api-progress.md) |
| FileSystemWatcher, Diagnostics, OutputChannel, ContextKeys, TextDocumentContentProvider, disposable lifecycle | [references/api-additional.md](references/api-additional.md) |
| Activation events, project structure, layered architecture, testing | [references/architecture.md](references/architecture.md) |
| `contributes`, `activationEvents`, `engines`, `scripts`, `keybindings`, esbuild config | [references/package-json-schema.md](references/package-json-schema.md) |
| Marketplace publishing, vsce, Open VSX, CI/CD, `.vscodeignore`, versioning | [references/publishing.md](references/publishing.md) |
| Language Server Protocol, `vscode-languageclient`, language servers | [references/lsp.md](references/lsp.md) |
| Notebook serializers, controllers, renderers | [references/notebooks.md](references/notebooks.md) |
| Debug Adapter Protocol, `DebugAdapterDescriptorFactory`, `DebugConfigurationProvider` | [references/debugger.md](references/debugger.md) |
| Advanced testing — multi-suite `.vscode-test.mjs`, fixtures, mocking, CI, coverage | [references/testing.md](references/testing.md) |

### Step 2 — Output contract

Every API symbol, configuration key, command, or behavior you cite MUST
be backed by a citation in the form:

`[source: references/<file>.md]`

Example: *"Push all subscriptions to `context.subscriptions` so they are disposed on deactivation [source: references/api-additional.md]"*

### Step 3 — If you must answer from memory

If you write a claim without having read the reference that backs it,
prepend `FROM_MEMORY (unverified):` to that claim. Do not hide it.

### Banned behaviors

- ❌ Inventing API methods, event names, or configuration keys not in the references
- ❌ Importing from anywhere other than the `'vscode'` module
- ❌ Suggesting deprecated APIs (e.g. `vscode.workspace.rootPath`) without flagging them as deprecated
- ❌ Marking the answer complete without listing which reference files you read

## When to use

- User wants to create a new VS Code extension
- User asks about VS Code extension APIs (TreeView, Webview, QuickPick, etc.)
- User needs help with package.json contributes, activationEvents, or keybindings
- User is debugging extension activation, disposables, or memory leaks
- User asks about bundling extensions with esbuild or webpack
- User wants to publish an extension to the VS Code Marketplace or Open VSX
- User asks about Webview CSP, nonce, or postMessage communication
- User asks about SecretStorage or credential management in extensions
- User needs help with extension testing (@vscode/test-electron)

## Source

VS Code Extension API documentation (https://code.visualstudio.com/api)

## Scaffolding Workflow

1. **Generate project**: `npx --package yo --package generator-code -- yo code`
2. **Choose template**: TypeScript extension (recommended)
3. **Choose bundler**: esbuild (recommended) or webpack
4. **Project structure** created — see `references/architecture.md` for layout
5. **Configure** `package.json` — see `references/package-json-schema.md`
6. **Implement** — pick the right reference from the Step 1 table (TreeView, Webview, QuickPick, StatusBar, SecretStorage, withProgress, or api-additional)
7. **Test** — see `references/architecture.md` for testing strategy
8. **Publish** — see `references/publishing.md` for full workflow

## UI Component Decision Matrix

| Need                              | Use                  | Why                                            |
| --------------------------------- | -------------------- | ---------------------------------------------- |
| Hierarchical data in sidebar      | TreeView             | Native tree with expand/collapse, icons, badges |
| Quick selection from a list       | QuickPick            | Modal list with filtering, multi-select         |
| Rich HTML interface               | Webview Panel        | Full HTML/CSS/JS, but heavier and needs CSP     |
| Persistent status info            | StatusBarItem        | Always visible, clickable, lightweight          |
| Simple text input                 | InputBox             | Single-line input with validation               |
| File/folder selection             | showOpenDialog       | Native OS file picker                           |
| Background task progress          | withProgress         | Notification or status bar progress             |

## Key Patterns

### Lazy Activation
- Use `activationEvents` in `package.json` to defer activation
- Since VS Code 1.74+, commands in `contributes.commands` auto-generate `onCommand:` events
- Prefer specific events (`onLanguage:python`, `onView:myTreeView`) over `*`
- See `references/package-json-schema.md` for full activationEvents reference

### Disposable Management
- Push ALL subscriptions to `context.subscriptions` in `activate()`
- Use `deactivate()` only for async cleanup (closing connections, stopping servers)
- Never rely on garbage collection — always dispose explicitly
- See `references/api-additional.md` for the cleanup pattern

### withProgress for Async Operations
- Use `ProgressLocation.Notification` for user-facing tasks
- Use `ProgressLocation.Window` for status bar progress
- Support cancellation via `CancellationToken`
- See `references/api-progress.md` for working examples

### SecretStorage for Credentials
- Use `context.secrets` (SecretStorage API) — never store tokens in settings
- Fires `onDidChange` event when secrets change
- See `references/api-secretstorage.md` for the credential manager pattern

### Webview CSP and PostMessage
- Always set a Content Security Policy with nonce
- Use `webview.asWebviewUri()` for local resources
- Bidirectional communication via `postMessage` / `onDidReceiveMessage`
- See `references/api-webview.md` for the full Webview pattern

### esbuild Bundling
- Bundle extension into a single file for faster activation
- Mark `vscode` as external (it's provided by the runtime)
- See `references/package-json-schema.md` for scripts configuration

## Reference Files

| File                                  | Topics                                                                             |
| ------------------------------------- | ---------------------------------------------------------------------------------- |
| `references/api-treeview.md`          | TreeDataProvider, TreeView registration                                            |
| `references/api-webview.md`           | Webview Panel, CSP/nonce, postMessage, asWebviewUri                                |
| `references/api-quickpick.md`         | Simple and async QuickPick with debounced search                                   |
| `references/api-statusbar.md`         | StatusBarItem, codicons, dynamic updates                                           |
| `references/api-secretstorage.md`     | Credential manager pattern, onDidChange                                            |
| `references/api-progress.md`          | withProgress (Notification + Window), cancellation tokens                          |
| `references/api-additional.md`        | FileSystemWatcher, Disposable cleanup, Diagnostics, OutputChannel, ContextKeys, TextDocumentContentProvider |
| `references/architecture.md`          | Project structure, layered architecture, testing strategy                          |
| `references/package-json-schema.md`   | contributes, activationEvents, engines, scripts, devDependencies                   |
| `references/publishing.md`            | vsce, .vscodeignore, CI/CD, Open VSX, versioning                                  |
| `references/lsp.md`                   | LSP client setup, server lifecycle, capabilities, diagnostics                      |
| `references/notebooks.md`             | Notebook serializers, controllers, renderers, output mime types                    |
| `references/debugger.md`              | DAP: descriptor factory, configuration provider, adapter lifecycle                 |
| `references/testing.md`               | Multi-suite test config, workspace fixtures, mocking `vscode`, CI, coverage        |

## Anti-Patterns to Avoid

- Using `*` activation event in production (activates on every VS Code start) [source: references/package-json-schema.md]
- Storing secrets in `configuration` instead of `SecretStorage` [source: references/api-secretstorage.md]
- Forgetting to dispose subscriptions (causes memory leaks) [source: references/api-additional.md]
- Missing CSP in Webviews (security vulnerability) [source: references/api-webview.md]
- Bundling `node_modules` instead of using esbuild/webpack [source: references/package-json-schema.md]
- Using synchronous file I/O in the extension host (blocks the UI) [source: references/architecture.md]
- Registering commands without corresponding `contributes.commands` entries [source: references/package-json-schema.md]
- Hardcoding `vscode.workspace.rootPath` (deprecated — use `workspaceFolders`) [source: references/architecture.md]
