# QuickPick

Modal list with filtering, multi-select, and async items.

## Simple QuickPick

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

## QuickPick with Async Loading

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
