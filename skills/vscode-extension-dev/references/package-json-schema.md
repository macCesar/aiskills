# package.json Schema Reference

Complete reference for VS Code extension `package.json` configuration.

## Minimal Valid Extension

```json
{
  "name": "my-extension",
  "displayName": "My Extension",
  "description": "What it does",
  "version": "0.0.1",
  "publisher": "your-publisher-id",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Other"],
  "main": "./dist/extension.js",
  "activationEvents": [],
  "contributes": {
    "commands": [
      {
        "command": "myExtension.helloWorld",
        "title": "Hello World",
        "category": "My Extension"
      }
    ]
  }
}
```

## engines.vscode

Specifies the minimum VS Code version your extension supports.

```json
"engines": {
  "vscode": "^1.85.0"
}
```

- Use `^` prefix for "this version or newer"
- Check API availability at https://code.visualstudio.com/api/references/vscode-api
- Common milestones: 1.74 (implicit activation), 1.82 (SecretStorage improvements)

## activationEvents

Controls **when** your extension loads. Less is better — lazy activation improves startup.

```json
"activationEvents": [
  "onLanguage:python",
  "onCommand:myExtension.doSomething",
  "onView:myTreeView",
  "onUri",
  "onFileSystem:myScheme",
  "onWebviewPanel:myPanel",
  "workspaceContains:**/tsconfig.json",
  "onStartupFinished",
  "*"
]
```

### Implicit Activation (VS Code 1.74+)
Commands declared in `contributes.commands` **automatically** generate `onCommand:` activation events. You do NOT need to list them in `activationEvents`.

```json
// This is enough — no activationEvents entry needed for this command
"contributes": {
  "commands": [
    { "command": "myExt.run", "title": "Run" }
  ]
}
```

### Event Reference

| Event                        | Fires when                                  |
| ---------------------------- | ------------------------------------------- |
| `onLanguage:langId`          | File of that language is opened             |
| `onCommand:commandId`        | Command is invoked (implicit since 1.74)    |
| `onView:viewId`              | TreeView with that ID is expanded           |
| `onUri`                      | Extension URI is opened (deep linking)      |
| `onFileSystem:scheme`        | File from that scheme is read               |
| `onWebviewPanel:type`        | Webview panel of that type is restored      |
| `workspaceContains:pattern`  | Workspace contains matching file            |
| `onStartupFinished`          | VS Code has fully started                   |
| `*`                          | On VS Code start — **avoid in production**  |

## contributes

### commands

```json
"contributes": {
  "commands": [
    {
      "command": "myExt.refresh",
      "title": "Refresh",
      "category": "My Extension",
      "icon": {
        "light": "resources/light/refresh.svg",
        "dark": "resources/dark/refresh.svg"
      },
      "enablement": "myExt.isConnected"
    }
  ]
}
```

- `category` groups commands in the Command Palette: "My Extension: Refresh"
- `icon` is used when the command appears in menus/toolbars
- `enablement` uses when-clause context for conditional availability

### menus

```json
"contributes": {
  "menus": {
    "view/title": [
      {
        "command": "myExt.refresh",
        "when": "view == myTreeView",
        "group": "navigation"
      }
    ],
    "view/item/context": [
      {
        "command": "myExt.deleteItem",
        "when": "view == myTreeView && viewItem == deletable",
        "group": "inline"
      }
    ],
    "editor/context": [
      {
        "command": "myExt.formatSelection",
        "when": "editorHasSelection",
        "group": "1_modification"
      }
    ],
    "commandPalette": [
      {
        "command": "myExt.deleteItem",
        "when": "false"
      }
    ]
  }
}
```

### Menu locations

| Location              | Where it appears                        |
| --------------------- | --------------------------------------- |
| `commandPalette`      | Command Palette (Ctrl+Shift+P)          |
| `editor/context`      | Editor right-click menu                 |
| `editor/title`        | Editor title bar                        |
| `view/title`          | View title bar (tree view header)       |
| `view/item/context`   | Tree view item right-click              |
| `explorer/context`    | File explorer right-click               |
| `scm/title`           | Source control title bar                |

### keybindings

```json
"contributes": {
  "keybindings": [
    {
      "command": "myExt.run",
      "key": "ctrl+shift+r",
      "mac": "cmd+shift+r",
      "when": "editorTextFocus && editorLangId == typescript"
    }
  ]
}
```

### configuration

```json
"contributes": {
  "configuration": {
    "title": "My Extension",
    "properties": {
      "myExt.apiUrl": {
        "type": "string",
        "default": "https://api.example.com",
        "description": "API endpoint URL",
        "format": "uri"
      },
      "myExt.maxResults": {
        "type": "number",
        "default": 50,
        "minimum": 1,
        "maximum": 500,
        "description": "Maximum number of results to display"
      },
      "myExt.logLevel": {
        "type": "string",
        "default": "info",
        "enum": ["debug", "info", "warn", "error"],
        "enumDescriptions": [
          "Verbose debug logging",
          "Standard information",
          "Warnings only",
          "Errors only"
        ],
        "description": "Logging verbosity level"
      },
      "myExt.features.autoRefresh": {
        "type": "boolean",
        "default": true,
        "description": "Automatically refresh data on file save"
      }
    }
  }
}
```

Reading configuration in TypeScript:

```typescript
const config = vscode.workspace.getConfiguration('myExt');
const apiUrl = config.get<string>('apiUrl', 'https://api.example.com');
const maxResults = config.get<number>('maxResults', 50);

// Listen for changes
vscode.workspace.onDidChangeConfiguration(e => {
  if (e.affectsConfiguration('myExt.apiUrl')) {
    // Re-initialize API client
  }
});
```

### views and viewsContainers

```json
"contributes": {
  "viewsContainers": {
    "activitybar": [
      {
        "id": "myExtExplorer",
        "title": "My Extension",
        "icon": "resources/icon.svg"
      }
    ]
  },
  "views": {
    "myExtExplorer": [
      {
        "id": "myTreeView",
        "name": "Items",
        "icon": "resources/items.svg",
        "contextualTitle": "My Extension Items"
      },
      {
        "id": "myFavoritesView",
        "name": "Favorites",
        "visibility": "collapsed"
      }
    ]
  },
  "viewsWelcome": [
    {
      "view": "myTreeView",
      "contents": "No items found.\n[Add Item](command:myExt.addItem)"
    }
  ]
}
```

## scripts (esbuild)

```json
"scripts": {
  "vscode:prepublish": "npm run package",
  "compile": "npm run check-types && node esbuild.js",
  "check-types": "tsc --noEmit",
  "watch": "node esbuild.js --watch",
  "package": "npm run check-types && node esbuild.js --production",
  "lint": "eslint src",
  "test": "vscode-test",
  "deploy": "vsce publish"
}
```

### esbuild.js

```javascript
const esbuild = require('esbuild');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

async function main() {
  const ctx = await esbuild.context({
    entryPoints: ['src/extension.ts'],
    bundle: true,
    format: 'cjs',
    minify: production,
    sourcemap: !production,
    sourcesContent: false,
    platform: 'node',
    outfile: 'dist/extension.js',
    external: ['vscode'],
    logLevel: 'silent',
    plugins: [
      /* add esbuild problem matcher plugin if needed */
    ],
  });

  if (watch) {
    await ctx.watch();
  } else {
    await ctx.rebuild();
    await ctx.dispose();
  }
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
```

## devDependencies

```json
"devDependencies": {
  "@types/vscode": "^1.85.0",
  "@types/mocha": "^10.0.6",
  "@types/node": "20.x",
  "@vscode/test-cli": "^0.0.6",
  "@vscode/test-electron": "^2.3.8",
  "esbuild": "^0.20.0",
  "eslint": "^8.56.0",
  "@typescript-eslint/eslint-plugin": "^7.0.0",
  "@typescript-eslint/parser": "^7.0.0",
  "typescript": "^5.3.0"
}
```

- `@types/vscode` version must match your `engines.vscode` range
- `@vscode/test-cli` provides the `vscode-test` command
- `@vscode/test-electron` downloads and launches VS Code for integration tests
