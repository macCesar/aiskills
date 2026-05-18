# Webview Panel

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

## Webview Script (media/main.js)

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
