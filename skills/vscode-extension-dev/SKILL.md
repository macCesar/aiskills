---
name: vscode-extension-dev
description: 'VS Code extension development grounded in the official Extension API docs. Use this whenever someone is creating, scaffolding, debugging, testing, bundling or publishing a VS Code extension — TreeView, QuickPick, Webview, StatusBar, SecretStorage, Language Server Protocol, Debug Adapter Protocol, notebooks — and also when they never say "extension" but the work clearly is one: editing `package.json` `contributes` / `activationEvents` / `keybindings`, an `activate(context)` function, importing from `vscode`, leaking disposables, `yo code`, `vsce`, `.vscodeignore`, bundling with esbuild, publishing to the Marketplace or Open VSX, Webview CSP/nonce/postMessage, or testing with @vscode/test-electron. Not for: configuring your own editor, Claude Code plugins or MCP servers, or general TypeScript/Node questions with no extension host involved.'
---

# VS Code Extension Development Skill

You are a VS Code extension development advisor. Ground every answer in the reference files below rather than in training data: the Extension API moves fast, deprecates surfaces, and adds new ones every release, so a remembered signature is often a signature that used to be right.

## Required workflow (read before responding)

The SKILL.md alone is an **index** of references. The detail you need to give accurate answers lives in the reference files. **Reading this SKILL.md is not enough.**

### Step 1 — Open the relevant reference files

| Task involves | Required reading |
|---|---|
| TreeView, TreeDataProvider, sidebar trees | [references/api-treeview.md](references/api-treeview.md) |
| Webview Panel, CSP, postMessage, nonce, `asWebviewUri` | [references/api-webview.md](references/api-webview.md) |
| QuickPick (simple or async with debounce) | [references/api-quickpick.md](references/api-quickpick.md) |
| StatusBarItem, codicons, status bar UI | [references/api-statusbar.md](references/api-statusbar.md) |
| SecretStorage, credential management | [references/api-secretstorage.md](references/api-secretstorage.md) |
| withProgress, cancellation tokens | [references/api-progress.md](references/api-progress.md) |
| FileSystemWatcher, Diagnostics, OutputChannel, ContextKeys, TextDocumentContentProvider, disposable lifecycle | [references/api-additional.md](references/api-additional.md) |
| Activation events, project structure, layered architecture, testing | [references/architecture.md](references/architecture.md) |
| `contributes`, `activationEvents`, `engines`, `scripts`, `keybindings`, esbuild config | [references/package-json-schema.md](references/package-json-schema.md) |
| Marketplace publishing, vsce, Open VSX, CI/CD, `.vscodeignore`, versioning | [references/publishing.md](references/publishing.md) |
| Language Server Protocol, `vscode-languageclient`, server lifecycle, capabilities, diagnostics | [references/lsp.md](references/lsp.md) |
| Notebook serializers, controllers, renderers, output mime types | [references/notebooks.md](references/notebooks.md) |
| Debug Adapter Protocol, `DebugAdapterDescriptorFactory`, `DebugConfigurationProvider` | [references/debugger.md](references/debugger.md) |
| Advanced testing — multi-suite `.vscode-test.mjs`, fixtures, mocking, CI, coverage | [references/testing.md](references/testing.md) |

### Step 2 — Output contract

Every API symbol, configuration key, command, or behavior you cite MUST be backed by a citation in the form:

`[source: references/<file>.md]`

Example: *"Push all subscriptions to `context.subscriptions` so they are disposed on deactivation [source: references/api-additional.md]"*

### Step 3 — If you must answer from memory

If you write a claim without having read the reference that backs it, prepend `FROM_MEMORY (unverified):` to that claim. Do not hide it.

### Banned behaviors

These four are where extension advice usually goes wrong, so they're worth naming:

- Inventing API methods, event names, or configuration keys not in the references. A plausible-looking `vscode.*` call fails at runtime, in the extension host, where the stack trace is least helpful.
- Sourcing editor APIs from anywhere other than the `'vscode'` module. That module is injected by the host at runtime rather than installed, which is why it's marked `external` in the bundler config — ordinary npm dependencies are fine and get bundled normally.
- Suggesting deprecated APIs (`vscode.workspace.rootPath` and friends) without flagging them. They still work today, which is exactly why they get copied into new code.
- Marking the answer complete without listing which reference files you read. The list is what lets the reader tell a grounded answer from a remembered one.

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

## Anti-Patterns to Avoid

**Manifest and activation**

- Using `*` activation event in production (activates on every VS Code start) [source: references/package-json-schema.md]
- Registering commands without corresponding `contributes.commands` entries [source: references/package-json-schema.md]
- Bundling `node_modules` instead of using esbuild/webpack [source: references/package-json-schema.md]

**Lifecycle and runtime**

- Forgetting to dispose subscriptions (causes memory leaks) [source: references/api-additional.md]
- Using synchronous file I/O in the extension host (blocks the UI) [source: references/architecture.md]
- Hardcoding `vscode.workspace.rootPath` (deprecated — use `workspaceFolders`) [source: references/architecture.md]
- Recreating a TreeView to refresh it instead of firing `onDidChangeTreeData` [source: references/api-treeview.md]
- Declaring `cancellable: true` and never checking `token.isCancellationRequested` — the Cancel button appears and does nothing [source: references/api-progress.md]
- Querying on every keystroke in a QuickPick without debouncing, and leaving the in-flight request running when the picker hides [source: references/api-quickpick.md]

**Security**

- Missing CSP in Webviews (security vulnerability) [source: references/api-webview.md]
- Storing secrets in `configuration` instead of `SecretStorage` [source: references/api-secretstorage.md]
- Setting `innerHTML` from untrusted cell output in a notebook renderer — XSS in the notebook viewer [source: references/notebooks.md]

**Publishing**

- Shipping `.ts` sources or `node_modules/` inside the VSIX instead of only the bundled output [source: references/publishing.md]
- Publishing without a `README.md` — it *is* the Marketplace listing page, and the publish fails without one [source: references/publishing.md]
- A `publisher` field that doesn't match the Marketplace publisher exactly [source: references/publishing.md]

**Language servers**

- Re-parsing the whole document on every keystroke instead of using `TextDocumentSyncKind.Incremental` [source: references/lsp.md]
- Heavy work inside `onInitialize` — it blocks editor startup; do it lazily on first request [source: references/lsp.md]
- Not awaiting `client.stop()` in `deactivate()` — leaves the server process alive [source: references/lsp.md]

**Notebooks and debug adapters**

- Forgetting `exec.end(...)` — the cell stays in "running" state forever [source: references/notebooks.md]
- Bundling a notebook renderer with `vscode` as a dependency — renderers run in an iframe and have no `vscode` import [source: references/notebooks.md]
- Forgetting to send `terminated` — the debug session never closes and "Stop" hangs [source: references/debugger.md]
- Long-running synchronous work in `DebugAdapterInlineImplementation` — blocks the extension host [source: references/debugger.md]

**Testing**

- Keeping editor-independent business logic in `extension.ts` — forces every test to spin up Electron [source: references/testing.md]
- `setTimeout` / sleep to "wait for activation" instead of `await ext.activate()` [source: references/testing.md]
- Running `xvfb-run` on macOS or Windows — it's only needed on Linux [source: references/testing.md]
