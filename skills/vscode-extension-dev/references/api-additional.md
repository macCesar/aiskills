# Additional API Patterns

Lower-frequency patterns that complement the core UI components.

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
