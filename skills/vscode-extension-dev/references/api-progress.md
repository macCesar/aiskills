# withProgress

Show progress for long-running operations.

## Notification Progress

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

## Status Bar Progress

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
