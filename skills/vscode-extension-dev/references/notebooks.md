# Notebook Extensions

VS Code supports notebooks (Jupyter-style) through three independent extension points: **serializers** (read/write file format), **controllers** (execute cells), and **renderers** (display rich output). You can implement any combination.

Official guide: https://code.visualstudio.com/api/extension-guides/notebook

## The Three Roles

| Role | What it does | API |
|---|---|---|
| Serializer | Converts file bytes ↔ in-memory `NotebookData` | `NotebookSerializer` |
| Controller | Runs a cell, produces outputs | `NotebookController` |
| Renderer | Webview that displays a specific output mime type | `package.json#contributes.notebookRenderer` |

A `.ipynb`-style extension typically provides serializer + controller. A renderer-only extension can extend ANY notebook (e.g., render a custom plot mime type).

## Notebook Serializer

Used to load and save the notebook file format.

```typescript
import * as vscode from 'vscode';

class MyNotebookSerializer implements vscode.NotebookSerializer {
  async deserializeNotebook(
    content: Uint8Array,
    _token: vscode.CancellationToken,
  ): Promise<vscode.NotebookData> {
    const text = new TextDecoder().decode(content);
    const parsed = JSON.parse(text);

    const cells = parsed.cells.map((c: any) =>
      new vscode.NotebookCellData(
        c.kind === 'code'
          ? vscode.NotebookCellKind.Code
          : vscode.NotebookCellKind.Markup,
        c.source,
        c.language ?? 'plaintext',
      ),
    );

    return new vscode.NotebookData(cells);
  }

  async serializeNotebook(
    data: vscode.NotebookData,
    _token: vscode.CancellationToken,
  ): Promise<Uint8Array> {
    const out = {
      cells: data.cells.map((c) => ({
        kind: c.kind === vscode.NotebookCellKind.Code ? 'code' : 'markdown',
        language: c.languageId,
        source: c.value,
      })),
    };
    return new TextEncoder().encode(JSON.stringify(out, null, 2));
  }
}

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.workspace.registerNotebookSerializer(
      'my-notebook',           // notebook type id (see package.json)
      new MyNotebookSerializer(),
      { transientOutputs: false }, // false = persist outputs in file
    ),
  );
}
```

`package.json`:

```json
"contributes": {
  "notebooks": [
    {
      "type": "my-notebook",
      "displayName": "My Notebook",
      "selector": [{ "filenamePattern": "*.mynb" }]
    }
  ]
}
```

## Notebook Controller

Runs cells and produces outputs.

```typescript
class MyController {
  readonly controllerId = 'my-controller';
  readonly notebookType = 'my-notebook';
  readonly label = 'My Kernel';
  readonly supportedLanguages = ['python', 'plaintext'];

  private readonly _controller: vscode.NotebookController;
  private _executionOrder = 0;

  constructor() {
    this._controller = vscode.notebooks.createNotebookController(
      this.controllerId,
      this.notebookType,
      this.label,
    );
    this._controller.supportedLanguages = this.supportedLanguages;
    this._controller.supportsExecutionOrder = true;
    this._controller.executeHandler = this._execute.bind(this);
  }

  private async _execute(
    cells: vscode.NotebookCell[],
    _notebook: vscode.NotebookDocument,
    _controller: vscode.NotebookController,
  ): Promise<void> {
    for (const cell of cells) {
      const exec = this._controller.createNotebookCellExecution(cell);
      exec.executionOrder = ++this._executionOrder;
      exec.start(Date.now());

      try {
        const result = await this._runCell(cell);
        await exec.replaceOutput([
          new vscode.NotebookCellOutput([
            vscode.NotebookCellOutputItem.text(result, 'text/plain'),
          ]),
        ]);
        exec.end(true, Date.now());
      } catch (err) {
        await exec.replaceOutput([
          new vscode.NotebookCellOutput([
            vscode.NotebookCellOutputItem.error(err as Error),
          ]),
        ]);
        exec.end(false, Date.now());
      }
    }
  }

  private async _runCell(cell: vscode.NotebookCell): Promise<string> {
    // Real kernels: send cell.document.getText() to a backend, await result
    return `Echo: ${cell.document.getText()}`;
  }

  dispose(): void {
    this._controller.dispose();
  }
}
```

Register the controller in `activate()` and push to `context.subscriptions`.

## Output Mime Types

Common mime types VS Code knows how to render natively:

- `text/plain`
- `text/markdown`
- `text/html`
- `image/png`, `image/jpeg`, `image/svg+xml`
- `application/json`
- `application/x.notebook.error` (use `NotebookCellOutputItem.error(err)`)
- `application/vnd.code.notebook.stdout` / `.stderr` (use `.stdout(str)` / `.stderr(str)`)

For anything else, ship a notebook renderer (next section).

## Notebook Renderer

A renderer is a webview that takes a typed output and produces DOM. Declared entirely in `package.json` + a script that exports `activate`:

```json
"contributes": {
  "notebookRenderer": [
    {
      "id": "my-plot-renderer",
      "displayName": "My Plot",
      "entrypoint": "./out/renderer.js",
      "mimeTypes": ["application/x.my-plot+json"]
    }
  ]
}
```

`renderer.ts` — build the DOM with safe APIs, never inject untrusted strings as HTML:

```typescript
import type { ActivationFunction } from 'vscode-notebook-renderer';

export const activate: ActivationFunction = () => ({
  renderOutputItem(outputItem, element) {
    const data = outputItem.json();

    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(data, null, 2);
    element.replaceChildren(pre);
  },
});
```

Renderers run in a separate iframe — they cannot call `vscode.*` directly. Communicate with the controller via the messaging API exposed in `renderer.activate`.

## Anti-Patterns

- ❌ Writing to disk synchronously in the serializer — VS Code calls it on the main thread
- ❌ Forgetting `exec.end(success, endTime)` — the cell stays in "running" state forever
- ❌ Reusing `executionOrder` numbers — must monotonically increase per notebook session
- ❌ Heavy DOM building in the renderer without batching — laggy scroll on large notebooks
- ❌ Bundling a notebook renderer with `vscode` as a dependency — renderers run in an iframe, not the extension host; they have NO `vscode` import
- ❌ Setting `innerHTML` from untrusted output data — XSS in the notebook viewer. Build DOM with `createElement` + `textContent`
