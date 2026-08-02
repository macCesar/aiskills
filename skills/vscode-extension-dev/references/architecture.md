# Extension Architecture

Layered architecture, project structure, and testing strategy for VS Code extensions.

<!-- TOC-START -->
## Contents

- [Directory Structure](#directory-structure)
- [Layered Architecture](#layered-architecture)
- [Debug Configuration](#debug-configuration)
- [Testing Strategy](#testing-strategy)
- [Extension Entry Point Pattern](#extension-entry-point-pattern)
- [Extension Host Runtime](#extension-host-runtime)
- [Workspace Folders (`rootPath` is deprecated)](#workspace-folders-rootpath-is-deprecated)

<!-- TOC-END -->

## Directory Structure

```
my-extension/
├── .vscode/
│   ├── extensions.json        # Recommended extensions for contributors
│   ├── launch.json            # Debug configurations
│   ├── settings.json          # Workspace settings
│   └── tasks.json             # Build tasks
├── src/
│   ├── extension.ts           # Entry point: activate() and deactivate()
│   ├── commands/              # Command handlers
│   │   ├── index.ts           # Re-exports all commands
│   │   └── runAnalysis.ts     # Individual command
│   ├── providers/             # VS Code API providers
│   │   ├── treeProvider.ts    # TreeDataProvider
│   │   ├── webviewProvider.ts # Webview panel manager
│   │   └── contentProvider.ts # TextDocumentContentProvider
│   ├── services/              # Business logic (no vscode imports)
│   │   ├── apiClient.ts       # External API communication
│   │   └── dataProcessor.ts   # Data transformation
│   ├── models/                # TypeScript interfaces and types
│   │   └── types.ts
│   └── utils/                 # Shared utilities
│       └── logger.ts
├── media/                     # Webview assets
│   ├── style.css
│   └── main.js
├── resources/                 # Icons and images
│   ├── dark/
│   │   └── icon.svg
│   └── light/
│       └── icon.svg
├── test/
│   ├── unit/                  # Unit tests (no VS Code dependency)
│   │   └── dataProcessor.test.ts
│   └── integration/           # Integration tests (require VS Code)
│       └── extension.test.ts
├── .vscodeignore              # Files to exclude from VSIX package
├── esbuild.js                 # Bundler configuration
├── package.json
├── tsconfig.json
├── CHANGELOG.md
└── README.md
```

## Layered Architecture

```
┌─────────────────────────────────────────────┐
│             VS Code Layer                    │
│  extension.ts, commands/, providers/         │
│  Imports from 'vscode'. Registers commands,  │
│  creates UI, manages disposables.            │
├─────────────────────────────────────────────┤
│          Business Logic Layer                │
│  services/                                   │
│  Pure TypeScript. NO 'vscode' imports.       │
│  Testable without VS Code runtime.           │
├─────────────────────────────────────────────┤
│            Data / API Layer                  │
│  services/apiClient.ts, models/              │
│  HTTP clients, data models, storage.         │
│  Also pure TypeScript.                       │
└─────────────────────────────────────────────┘
```

### Why This Layering Matters

- **Business logic** in `services/` has zero `vscode` imports — it can be unit tested with plain Mocha/Jest, no Extension Host needed
- **VS Code layer** is thin — it wires providers/commands to services
- **Data layer** is injectable — swap real API for mock in tests

### Example: Keeping Layers Separate

```typescript
// services/dataProcessor.ts — NO vscode imports
export interface ProcessResult {
  total: number;
  errors: string[];
}

export function processData(items: string[]): ProcessResult {
  const errors: string[] = [];
  for (const item of items) {
    if (!item.trim()) {
      errors.push('Empty item found');
    }
  }
  return { total: items.length, errors };
}
```

```typescript
// commands/runAnalysis.ts — thin VS Code wrapper
import * as vscode from 'vscode';
import { processData } from '../services/dataProcessor';

export async function runAnalysis(): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('No active editor');
    return;
  }

  const text = editor.document.getText();
  const lines = text.split('\n');
  const result = processData(lines);

  if (result.errors.length > 0) {
    vscode.window.showWarningMessage(`Found ${result.errors.length} issues`);
  } else {
    vscode.window.showInformationMessage(`Processed ${result.total} lines`);
  }
}
```

## Debug Configuration

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Extension",
      "type": "extensionHost",
      "request": "launch",
      "args": ["--extensionDevelopmentPath=${workspaceFolder}"],
      "outFiles": ["${workspaceFolder}/dist/**/*.js"],
      "preLaunchTask": "npm: compile"
    },
    {
      "name": "Extension Tests",
      "type": "extensionHost",
      "request": "launch",
      "args": [
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionTestsPath=${workspaceFolder}/out/test/integration"
      ],
      "outFiles": ["${workspaceFolder}/out/**/*.js"],
      "preLaunchTask": "npm: compile"
    }
  ]
}
```

## Testing Strategy

### Unit Tests (Business Logic)

Test `services/` with plain Mocha — no VS Code runtime needed.

```typescript
// test/unit/dataProcessor.test.ts
import * as assert from 'assert';
import { processData } from '../../src/services/dataProcessor';

suite('dataProcessor', () => {
  test('counts items correctly', () => {
    const result = processData(['a', 'b', 'c']);
    assert.strictEqual(result.total, 3);
    assert.strictEqual(result.errors.length, 0);
  });

  test('reports empty items', () => {
    const result = processData(['a', '', 'c']);
    assert.strictEqual(result.errors.length, 1);
  });

  test('handles empty input', () => {
    const result = processData([]);
    assert.strictEqual(result.total, 0);
  });
});
```

### Integration Tests (VS Code API)

Test commands, providers, and UI interactions with `@vscode/test-electron`.

```typescript
// test/integration/extension.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Integration', () => {
  suiteSetup(async () => {
    // Wait for extension to activate
    const ext = vscode.extensions.getExtension('publisher.my-extension');
    await ext?.activate();
  });

  test('extension activates', () => {
    const ext = vscode.extensions.getExtension('publisher.my-extension');
    assert.ok(ext?.isActive);
  });

  test('command registers successfully', async () => {
    const commands = await vscode.commands.getCommands(true);
    assert.ok(commands.includes('myExt.run'));
  });

  test('command executes without error', async () => {
    // Open a test document first
    const doc = await vscode.workspace.openTextDocument({
      content: 'line1\nline2\nline3',
      language: 'plaintext',
    });
    await vscode.window.showTextDocument(doc);

    // Execute command — should not throw
    await vscode.commands.executeCommand('myExt.run');
  });
});
```

### Test Runner Configuration

`.vscode-test.mjs`:

```javascript
import { defineConfig } from '@vscode/test-cli';

export default defineConfig({
  files: 'out/test/integration/**/*.test.js',
  mocha: {
    timeout: 20000,
    ui: 'tdd',
  },
});
```

`tsconfig.json` for tests (if separate):

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2022",
    "lib": ["ES2022"],
    "outDir": "out",
    "rootDir": ".",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "test/**/*.ts"]
}
```

## Extension Entry Point Pattern

```typescript
// src/extension.ts
import * as vscode from 'vscode';
import { runAnalysis } from './commands/runAnalysis';
import { MyTreeProvider } from './providers/treeProvider';

export function activate(context: vscode.ExtensionContext) {
  const output = vscode.window.createOutputChannel('My Extension', { log: true });
  output.info('Activating...');

  // Initialize providers
  const treeProvider = new MyTreeProvider();

  // Register everything and push to subscriptions
  context.subscriptions.push(
    output,
    vscode.window.createTreeView('myTreeView', { treeDataProvider: treeProvider }),
    vscode.commands.registerCommand('myExt.run', runAnalysis),
    vscode.commands.registerCommand('myExt.refresh', () => treeProvider.refresh()),
  );

  output.info('Activated');
}

export function deactivate(): void {
  // Only for async cleanup (network connections, child processes)
  // Disposables in context.subscriptions are auto-disposed
}
```

## Extension Host Runtime

The extension host is a **single Node.js process shared by every extension** in the window. Two consequences shape the code you write:

- **Synchronous file I/O blocks the UI.** Calls like `fs.readFileSync` or `fs.writeFileSync` stall the host event loop, which freezes responses from every extension AND the editor's command handling. Always prefer async APIs:
  - Node: `import { readFile } from 'node:fs/promises'` — `await readFile(path, 'utf8')`
  - VS Code abstraction: `await vscode.workspace.fs.readFile(uri)` — works across remote, virtual, and local file systems
- **CPU-heavy work in the host blocks too.** For long parsing/analysis, move work to a worker thread (`node:worker_threads`) or a language server (LSP), not a tight loop on the host.
- The Webview runs in a separate process; messaging is async by construction. Don't try to "call" the host synchronously from the webview.

```typescript
// BAD — blocks the extension host
import * as fs from 'node:fs';
const text = fs.readFileSync('/tmp/big-file.txt', 'utf8');

// GOOD — async, yields back to the event loop
import { readFile } from 'node:fs/promises';
const text = await readFile('/tmp/big-file.txt', 'utf8');

// GOOD — workspace-aware (preferred when reading user files)
const uri = vscode.Uri.file('/tmp/big-file.txt');
const bytes = await vscode.workspace.fs.readFile(uri);
const text2 = new TextDecoder('utf-8').decode(bytes);
```

## Workspace Folders (`rootPath` is deprecated)

`vscode.workspace.rootPath` is **deprecated** and returns only the *first* folder in multi-root workspaces, silently dropping the rest. Use `vscode.workspace.workspaceFolders` instead — it returns `readonly WorkspaceFolder[] | undefined`.

```typescript
// BAD — deprecated, fails silently in multi-root workspaces
const root = vscode.workspace.rootPath;

// GOOD — iterate all workspace folders
const folders = vscode.workspace.workspaceFolders;
if (!folders || folders.length === 0) {
  vscode.window.showWarningMessage('Open a folder first.');
  return;
}
for (const folder of folders) {
  // folder.uri.fsPath is the absolute path
  // folder.name is the display name
  // folder.index is its position in the list
}

// GOOD — find the folder that owns a given file
const fileUri = vscode.window.activeTextEditor?.document.uri;
if (fileUri) {
  const owner = vscode.workspace.getWorkspaceFolder(fileUri);
  // owner is the WorkspaceFolder containing the file, or undefined
}

// GOOD — react to folders being added or removed
context.subscriptions.push(
  vscode.workspace.onDidChangeWorkspaceFolders((event) => {
    for (const added of event.added) {
      // ...
    }
    for (const removed of event.removed) {
      // ...
    }
  }),
);
```

Relative paths in extension code should resolve against a specific `WorkspaceFolder`, never against `process.cwd()` (which is unrelated to the user's workspace).
