# Language Server Protocol (LSP)

Build a language extension by running an out-of-process **language server** and connecting it to VS Code via the `vscode-languageclient` npm package. The server can be written in any language; only the client lives inside the extension.

Official guide: https://code.visualstudio.com/api/language-extensions/language-server-extension-guide
Protocol spec: https://microsoft.github.io/language-server-protocol/

## When to Use LSP vs Direct API

| Need | Use |
|---|---|
| Diagnostics, completion, hover for ONE editor (VS Code only) | Direct API (`vscode.languages.register*Provider`) |
| Same language features in VS Code + other LSP clients (Neovim, Sublime, etc.) | LSP |
| Heavy parsing/analysis you want isolated from the extension host | LSP (server runs in its own process) |
| Sharing logic with a CLI or CI tool | LSP (server is reusable) |

**Rule of thumb**: write LSP if the features are non-trivial OR you want portability. Use direct API for a one-off completion provider in a single language.

## Project Structure

```
my-language-ext/
├── client/
│   ├── src/extension.ts          # The VS Code extension (the client)
│   └── tsconfig.json
├── server/
│   ├── src/server.ts             # Language server (Node-based example)
│   └── tsconfig.json
├── package.json                  # Extension manifest (covers both)
└── tsconfig.json                 # Root, with project references
```

The extension's `package.json` lists `vscode-languageclient` as a runtime dependency and uses `activationEvents: ["onLanguage:<langId>"]`.

## Client (extension side)

```typescript
import * as path from 'node:path';
import * as vscode from 'vscode';
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from 'vscode-languageclient/node';

let client: LanguageClient | undefined;

export function activate(context: vscode.ExtensionContext) {
  const serverModule = context.asAbsolutePath(
    path.join('server', 'out', 'server.js'),
  );

  const serverOptions: ServerOptions = {
    run: { module: serverModule, transport: TransportKind.ipc },
    debug: {
      module: serverModule,
      transport: TransportKind.ipc,
      options: { execArgv: ['--nolazy', '--inspect=6009'] },
    },
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: 'file', language: 'myLang' }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher('**/.myLangConfig'),
    },
  };

  client = new LanguageClient(
    'myLangServer',
    'My Language Server',
    serverOptions,
    clientOptions,
  );

  client.start();
}

export async function deactivate(): Promise<void> {
  if (client) {
    await client.stop();
  }
}
```

`TransportKind.ipc` is the recommended transport for Node-based servers (process IPC). For non-Node servers, spawn with `TransportKind.stdio` or `TransportKind.socket`.

## Server (minimal Node example)

```typescript
import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  TextDocumentSyncKind,
  CompletionItem,
  CompletionItemKind,
} from 'vscode-languageserver/node';
import { TextDocument } from 'vscode-languageserver-textdocument';

const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);

connection.onInitialize((_params: InitializeParams) => ({
  capabilities: {
    textDocumentSync: TextDocumentSyncKind.Incremental,
    completionProvider: { resolveProvider: false, triggerCharacters: ['.'] },
    hoverProvider: true,
  },
}));

connection.onCompletion((_params): CompletionItem[] => [
  { label: 'hello', kind: CompletionItemKind.Keyword },
]);

connection.onHover((params) => {
  const doc = documents.get(params.textDocument.uri);
  if (!doc) return null;
  return { contents: { kind: 'markdown', value: 'Hover content' } };
});

documents.listen(connection);
connection.listen();
```

## Capabilities You Typically Register

| Capability | Server method | Client receives |
|---|---|---|
| Completion | `onCompletion` | items shown in IntelliSense |
| Hover | `onHover` | tooltip on hover |
| Diagnostics | `connection.sendDiagnostics({ uri, diagnostics })` | Problems panel + squiggles |
| Definition | `onDefinition` | "Go to Definition" target |
| References | `onReferences` | "Find All References" results |
| Document symbols | `onDocumentSymbol` | breadcrumbs + outline |
| Formatting | `onDocumentFormatting` | "Format Document" |
| Code actions | `onCodeAction` | quick fixes / refactors |
| Rename | `onRenameRequest` | symbol rename |

Each capability must be declared in the `InitializeResult.capabilities` AND have a matching server handler. Mismatch = silent failure.

## Diagnostics (Push Model)

Send diagnostics whenever a document changes:

```typescript
documents.onDidChangeContent((event) => {
  const diagnostics = validate(event.document);
  connection.sendDiagnostics({
    uri: event.document.uri,
    diagnostics,
  });
});
```

Diagnostic structure:

```typescript
{
  severity: DiagnosticSeverity.Error, // Error | Warning | Information | Hint
  range: { start: { line: 0, character: 0 }, end: { line: 0, character: 10 } },
  message: 'Unexpected token',
  source: 'my-lang',
}
```

## Anti-Patterns

- ❌ Re-parsing the whole document on every keystroke — use `TextDocumentSyncKind.Incremental` and process deltas
- ❌ Heavy work inside `onInitialize` — it blocks editor startup; do it lazily on first request
- ❌ Forgetting to `await client.stop()` in `deactivate()` — leaves the server process alive
- ❌ Hardcoding paths in `serverModule` — always go through `context.asAbsolutePath`
- ❌ Mixing client and server types — `vscode-languageclient/node` is for the client, `vscode-languageserver/node` is for the server
