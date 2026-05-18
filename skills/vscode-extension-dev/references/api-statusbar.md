# StatusBarItem

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

## Codicon Icons in StatusBar

Use `$(icon-name)` syntax. Common icons:

- `$(sync~spin)` — spinning sync (loading)
- `$(check)` — checkmark
- `$(warning)` — warning triangle
- `$(error)` — error circle
- `$(info)` — info circle
- `$(cloud-upload)` — upload
- Full list: https://code.visualstudio.com/api/references/icons-in-labels
