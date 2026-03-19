# VS Code API Patterns

Working TypeScript implementations for common VS Code extension patterns.

## TreeDataProvider

Provides data for a TreeView in the sidebar or panel.

```typescript
import * as vscode from 'vscode';

interface TreeItem {
  id: string;
  label: string;
  children?: TreeItem[];
}

class MyTreeProvider implements vscode.TreeDataProvider<TreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<TreeItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private items: TreeItem[] = [];

  refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: TreeItem): vscode.TreeItem {
    const treeItem = new vscode.TreeItem(
      element.label,
      element.children?.length
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None
    );
    treeItem.id = element.id;
    treeItem.contextValue = element.children ? 'parent' : 'leaf';
    treeItem.iconPath = new vscode.ThemeIcon('symbol-file');
    // Make leaf items clickable
    if (!element.children) {
      treeItem.command = {
        command: 'myExt.openItem',
        title: 'Open Item',
        arguments: [element],
      };
    }
    return treeItem;
  }

  getChildren(element?: TreeItem): TreeItem[] {
    if (!element) {
      return this.items;
    }
    return element.children ?? [];
  }

  setItems(items: TreeItem[]): void {
    this.items = items;
    this.refresh();
  }
}
```

### Registering the TreeView

```typescript
export function activate(context: vscode.ExtensionContext) {
  const treeProvider = new MyTreeProvider();

  const treeView = vscode.window.createTreeView('myTreeView', {
    treeDataProvider: treeProvider,
    showCollapseAll: true,
  });

  context.subscriptions.push(
    treeView,
    vscode.commands.registerCommand('myExt.refresh', () => treeProvider.refresh()),
    vscode.commands.registerCommand('myExt.openItem', (item: TreeItem) => {
      vscode.window.showInformationMessage(`Opened: ${item.label}`);
    }),
  );
}
```

## Webview Panel

Full HTML rendering with CSP and bidirectional messaging.

```typescript
import * as vscode from 'vscode';

class MyWebviewPanel {
  public static readonly viewType = 'myExt.webview';
  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];

  public static create(extensionUri: vscode.Uri): MyWebviewPanel {
    const panel = vscode.window.createWebviewPanel(
      MyWebviewPanel.viewType,
      'My Panel',
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: false, // saves memory; set true if state is expensive
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')],
      },
    );

    return new MyWebviewPanel(panel, extensionUri);
  }

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._extensionUri = extensionUri;

    this._panel.webview.html = this._getHtml(this._panel.webview);

    // Handle messages FROM the webview
    this._panel.webview.onDidReceiveMessage(
      (message: { command: string; data?: unknown }) => {
        switch (message.command) {
          case 'save':
            this._handleSave(message.data);
            return;
          case 'requestData':
            this._sendData();
            return;
        }
      },
      null,
      this._disposables,
    );

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  /** Send data TO the webview */
  public sendMessage(command: string, data: unknown): void {
    this._panel.webview.postMessage({ command, data });
  }

  private _handleSave(data: unknown): void {
    vscode.window.showInformationMessage('Data saved!');
  }

  private _sendData(): void {
    this.sendMessage('loadData', { items: ['a', 'b', 'c'] });
  }

  private _getHtml(webview: vscode.Webview): string {
    const styleUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'media', 'style.css'),
    );
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js'),
    );
    const nonce = getNonce();

    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy"
    content="default-src 'none';
      style-src ${webview.cspSource};
      script-src 'nonce-${nonce}';
      img-src ${webview.cspSource} https:;
      font-src ${webview.cspSource};">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="${styleUri}" rel="stylesheet">
  <title>My Panel</title>
</head>
<body>
  <div id="app"></div>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
  }

  public dispose(): void {
    this._panel.dispose();
    while (this._disposables.length) {
      const d = this._disposables.pop();
      d?.dispose();
    }
  }
}

function getNonce(): string {
  let text = '';
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 32; i++) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return text;
}
```

### Webview Script (media/main.js)

```javascript
// Inside the webview — communicates with the extension via postMessage
(function () {
  // @ts-ignore
  const vscode = acquireVsCodeApi();

  // Send message TO the extension
  function save(data) {
    vscode.postMessage({ command: 'save', data });
  }

  // Receive messages FROM the extension
  window.addEventListener('message', (event) => {
    const message = event.data;
    switch (message.command) {
      case 'loadData':
        renderData(message.data);
        break;
    }
  });

  function renderData(data) {
    const app = document.getElementById('app');
    if (app) {
      app.textContent = JSON.stringify(data, null, 2);
    }
  }

  // Request initial data
  vscode.postMessage({ command: 'requestData' });
})();
```

## QuickPick

Modal list with filtering, multi-select, and async items.

### Simple QuickPick

```typescript
const items: vscode.QuickPickItem[] = [
  { label: 'Item 1', description: 'First item', detail: 'Additional details' },
  { label: 'Item 2', description: 'Second item', picked: true },
  { label: 'Item 3', description: 'Third item' },
];

const selected = await vscode.window.showQuickPick(items, {
  placeHolder: 'Select an item',
  canPickMany: false,
  matchOnDescription: true,
  matchOnDetail: true,
});

if (selected) {
  vscode.window.showInformationMessage(`Selected: ${selected.label}`);
}
```

### QuickPick with Async Loading

```typescript
async function showAsyncQuickPick(): Promise<void> {
  const qp = vscode.window.createQuickPick<vscode.QuickPickItem>();
  qp.placeholder = 'Search items...';
  qp.matchOnDescription = true;

  // Debounced search
  let searchTimer: ReturnType<typeof setTimeout> | undefined;
  const controller = new AbortController();

  qp.onDidChangeValue((value) => {
    if (searchTimer) {
      clearTimeout(searchTimer);
    }
    searchTimer = setTimeout(async () => {
      qp.busy = true;
      try {
        const results = await fetchItems(value, controller.signal);
        qp.items = results.map((r) => ({
          label: r.name,
          description: r.description,
        }));
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          vscode.window.showErrorMessage(`Search failed: ${err.message}`);
        }
      } finally {
        qp.busy = false;
      }
    }, 300);
  });

  qp.onDidAccept(() => {
    const selected = qp.selectedItems[0];
    if (selected) {
      vscode.window.showInformationMessage(`Selected: ${selected.label}`);
    }
    qp.dispose();
  });

  qp.onDidHide(() => {
    controller.abort();
    qp.dispose();
  });

  qp.show();
}
```

## StatusBarItem

Persistent info in the status bar with click action.

```typescript
export function activate(context: vscode.ExtensionContext) {
  const statusBar = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100, // priority — higher = more to the left
  );

  statusBar.text = '$(sync) My Extension';
  statusBar.tooltip = 'Click to refresh';
  statusBar.command = 'myExt.refresh';
  statusBar.backgroundColor = undefined; // use new vscode.ThemeColor('statusBarItem.warningBackground') for warnings
  statusBar.show();

  context.subscriptions.push(statusBar);

  // Update dynamically
  function updateStatus(count: number): void {
    statusBar.text = `$(check) ${count} items`;
    statusBar.tooltip = `${count} items synced`;
  }
}
```

### Codicon Icons in StatusBar

Use `$(icon-name)` syntax. Common icons:
- `$(sync~spin)` — spinning sync (loading)
- `$(check)` — checkmark
- `$(warning)` — warning triangle
- `$(error)` — error circle
- `$(info)` — info circle
- `$(cloud-upload)` — upload
- Full list: https://code.visualstudio.com/api/references/icons-in-labels

## SecretStorage

Secure credential storage using the OS keychain.

```typescript
class CredentialManager {
  private static readonly TOKEN_KEY = 'myExt.apiToken';

  constructor(private readonly secrets: vscode.SecretStorage) {}

  async getToken(): Promise<string | undefined> {
    return this.secrets.get(CredentialManager.TOKEN_KEY);
  }

  async setToken(token: string): Promise<void> {
    await this.secrets.store(CredentialManager.TOKEN_KEY, token);
  }

  async deleteToken(): Promise<void> {
    await this.secrets.delete(CredentialManager.TOKEN_KEY);
  }

  onDidChange(callback: (e: vscode.SecretStorageChangeEvent) => void): vscode.Disposable {
    return this.secrets.onDidChange(callback);
  }
}

// In activate():
export function activate(context: vscode.ExtensionContext) {
  const credentials = new CredentialManager(context.secrets);

  context.subscriptions.push(
    vscode.commands.registerCommand('myExt.login', async () => {
      const token = await vscode.window.showInputBox({
        prompt: 'Enter your API token',
        password: true,
        ignoreFocusOut: true,
      });
      if (token) {
        await credentials.setToken(token);
        vscode.window.showInformationMessage('Token saved securely.');
      }
    }),

    vscode.commands.registerCommand('myExt.logout', async () => {
      await credentials.deleteToken();
      vscode.window.showInformationMessage('Token removed.');
    }),

    credentials.onDidChange((e) => {
      if (e.key === 'myExt.apiToken') {
        // React to credential change
      }
    }),
  );
}
```

## withProgress

Show progress for long-running operations.

### Notification Progress

```typescript
async function longRunningTask(): Promise<void> {
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Processing items',
      cancellable: true,
    },
    async (progress, token) => {
      const items = await getItems();
      const total = items.length;

      for (let i = 0; i < total; i++) {
        // Check for cancellation
        if (token.isCancellationRequested) {
          vscode.window.showWarningMessage('Operation cancelled.');
          return;
        }

        progress.report({
          increment: 100 / total,
          message: `(${i + 1}/${total}) ${items[i].name}`,
        });

        await processItem(items[i]);
      }

      vscode.window.showInformationMessage(`Processed ${total} items.`);
    },
  );
}
```

### Status Bar Progress

```typescript
await vscode.window.withProgress(
  {
    location: vscode.ProgressLocation.Window,
    title: 'Indexing files...',
  },
  async (progress) => {
    progress.report({ message: 'scanning...' });
    await scanFiles();
    progress.report({ message: 'building index...' });
    await buildIndex();
  },
);
```

## FileSystemWatcher

React to file changes in the workspace.

```typescript
export function activate(context: vscode.ExtensionContext) {
  const watcher = vscode.workspace.createFileSystemWatcher(
    '**/*.json',     // glob pattern
    false,           // ignoreCreateEvents
    false,           // ignoreChangeEvents
    false,           // ignoreDeleteEvents
  );

  context.subscriptions.push(
    watcher,
    watcher.onDidCreate((uri) => {
      console.log(`Created: ${uri.fsPath}`);
    }),
    watcher.onDidChange((uri) => {
      console.log(`Changed: ${uri.fsPath}`);
    }),
    watcher.onDidDelete((uri) => {
      console.log(`Deleted: ${uri.fsPath}`);
    }),
  );
}
```

## Disposable Cleanup Pattern

The standard pattern for managing extension lifecycle.

```typescript
import * as vscode from 'vscode';

let outputChannel: vscode.OutputChannel | undefined;

export function activate(context: vscode.ExtensionContext) {
  // Output channel for logging
  outputChannel = vscode.window.createOutputChannel('My Extension');
  context.subscriptions.push(outputChannel);

  // All registrations go into context.subscriptions
  context.subscriptions.push(
    vscode.commands.registerCommand('myExt.run', run),
    vscode.workspace.onDidSaveTextDocument(onDocSaved),
    vscode.window.onDidChangeActiveTextEditor(onEditorChanged),
  );

  outputChannel.appendLine('Extension activated');
}

export function deactivate(): void {
  // Only needed for async cleanup like:
  // - Closing network connections
  // - Stopping child processes
  // - Flushing buffers
  // Disposables in context.subscriptions are auto-disposed.
}

function run(): void {
  outputChannel?.appendLine('Command executed');
}

function onDocSaved(doc: vscode.TextDocument): void {
  outputChannel?.appendLine(`Saved: ${doc.fileName}`);
}

function onEditorChanged(editor: vscode.TextEditor | undefined): void {
  outputChannel?.appendLine(`Active editor: ${editor?.document.fileName ?? 'none'}`);
}
```

## Diagnostic Collection

Report problems (errors, warnings) in the Problems panel.

```typescript
const diagnostics = vscode.languages.createDiagnosticCollection('myExt');
context.subscriptions.push(diagnostics);

function validateDocument(doc: vscode.TextDocument): void {
  const issues: vscode.Diagnostic[] = [];

  for (let i = 0; i < doc.lineCount; i++) {
    const line = doc.lineAt(i);
    if (line.text.includes('TODO')) {
      issues.push(
        new vscode.Diagnostic(
          line.range,
          'TODO comment found',
          vscode.DiagnosticSeverity.Warning,
        ),
      );
    }
  }

  diagnostics.set(doc.uri, issues);
}
```

## Output Channel and Logging

```typescript
// Simple output channel
const output = vscode.window.createOutputChannel('My Extension');
output.appendLine('Info message');
output.show(true); // true = preserve focus

// Log output channel (structured, with log levels — VS Code 1.74+)
const log = vscode.window.createOutputChannel('My Extension', { log: true });
log.info('Started');
log.warn('Something looks off');
log.error('Something failed', new Error('details'));
log.debug('Debug data', { key: 'value' });
```

## Context Keys (When Clauses)

Set custom context keys to control menu/command visibility.

```typescript
// Set a context key
vscode.commands.executeCommand('setContext', 'myExt.isConnected', true);

// Use in package.json when clauses:
// "when": "myExt.isConnected"
// "when": "myExt.isConnected && editorLangId == typescript"

// Clear it
vscode.commands.executeCommand('setContext', 'myExt.isConnected', false);
```

## TextDocumentContentProvider

Provide virtual read-only documents.

```typescript
class MyContentProvider implements vscode.TextDocumentContentProvider {
  private _onDidChange = new vscode.EventEmitter<vscode.Uri>();
  readonly onDidChange = this._onDidChange.event;

  provideTextDocumentContent(uri: vscode.Uri): string {
    const query = new URLSearchParams(uri.query);
    const id = query.get('id') ?? 'unknown';
    return `Content for: ${id}\nGenerated at: ${new Date().toISOString()}`;
  }

  refresh(uri: vscode.Uri): void {
    this._onDidChange.fire(uri);
  }
}

// Register
const provider = new MyContentProvider();
context.subscriptions.push(
  vscode.workspace.registerTextDocumentContentProvider('myScheme', provider),
);

// Open a virtual document
const uri = vscode.Uri.parse('myScheme:item?id=123');
const doc = await vscode.workspace.openTextDocument(uri);
await vscode.window.showTextDocument(doc);
```
