# TreeDataProvider

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

## Registering the TreeView

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
