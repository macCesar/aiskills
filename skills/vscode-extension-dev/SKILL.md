---
name: vscode-extension-dev
description: Guide for building VS Code extensions from scratch. Use when the user is creating, scaffolding, designing, debugging, testing, bundling, or publishing a VS Code extension. Covers all major API patterns — TreeView, QuickPick, Webview, StatusBar, commands, configuration, SecretStorage, progress indicators, and esbuild bundling.
when_to_use: >
  - User wants to create a new VS Code extension
  - User asks about VS Code extension APIs (TreeView, Webview, QuickPick, etc.)
  - User needs help with package.json contributes, activationEvents, or keybindings
  - User is debugging extension activation, disposables, or memory leaks
  - User asks about bundling extensions with esbuild or webpack
  - User wants to publish an extension to the VS Code Marketplace or Open VSX
  - User asks about Webview CSP, nonce, or postMessage communication
  - User asks about SecretStorage or credential management in extensions
  - User needs help with extension testing (@vscode/test-electron)
source: "VS Code Extension API documentation (https://code.visualstudio.com/api)"
anti_hallucination_note: >
  ALL guidance in this skill comes from the official VS Code Extension API docs
  and established community patterns. Do NOT invent API methods, event names,
  or configuration keys. If unsure whether an API exists, say so explicitly.
  Always verify imports come from the 'vscode' module.
---

# VS Code Extension Development Skill

You are a VS Code extension development advisor. Base ALL guidance on the reference files below — not training data.

## How to Use This Skill

1. Read the relevant reference file(s) before answering
2. Base ALL code on the reference content — not training data
3. Use real TypeScript imports and correct `vscode` API signatures
4. Do not invent API methods, events, or configuration keys not in the references

## Scaffolding Workflow

1. **Generate project**: `npx --package yo --package generator-code -- yo code`
2. **Choose template**: TypeScript extension (recommended)
3. **Choose bundler**: esbuild (recommended) or webpack
4. **Project structure** created — see `references/architecture.md` for layout
5. **Configure** `package.json` — see `references/package-json-schema.md`
6. **Implement** — see `references/api-patterns.md` for working examples
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
- See `references/api-patterns.md` for the cleanup pattern

### withProgress for Async Operations
- Use `ProgressLocation.Notification` for user-facing tasks
- Use `ProgressLocation.Window` for status bar progress
- Support cancellation via `CancellationToken`
- See `references/api-patterns.md` for working examples

### SecretStorage for Credentials
- Use `context.secrets` (SecretStorage API) — never store tokens in settings
- Fires `onDidChange` event when secrets change
- See `references/api-patterns.md` for the credential manager pattern

### Webview CSP and PostMessage
- Always set a Content Security Policy with nonce
- Use `webview.asWebviewUri()` for local resources
- Bidirectional communication via `postMessage` / `onDidReceiveMessage`
- See `references/api-patterns.md` for the full Webview pattern

### esbuild Bundling
- Bundle extension into a single file for faster activation
- Mark `vscode` as external (it's provided by the runtime)
- See `references/package-json-schema.md` for scripts configuration

## Reference Files

| File                                | Topics                                                              |
| ----------------------------------- | ------------------------------------------------------------------- |
| `references/package-json-schema.md` | contributes, activationEvents, engines, scripts, devDependencies    |
| `references/api-patterns.md`        | TreeView, Webview, QuickPick, StatusBar, SecretStorage, withProgress |
| `references/architecture.md`        | Project structure, layered architecture, testing strategy            |
| `references/publishing.md`          | vsce, .vscodeignore, CI/CD, Open VSX, versioning                    |

## Anti-Patterns to Avoid

- Using `*` activation event in production (activates on every VS Code start)
- Storing secrets in `configuration` instead of `SecretStorage`
- Forgetting to dispose subscriptions (causes memory leaks)
- Missing CSP in Webviews (security vulnerability)
- Bundling `node_modules` instead of using esbuild/webpack
- Using synchronous file I/O in the extension host (blocks the UI)
- Registering commands without corresponding `contributes.commands` entries
- Hardcoding `vscode.workspace.rootPath` (deprecated — use `workspaceFolders`)
