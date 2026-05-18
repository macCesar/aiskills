# Debugger Extensions (Debug Adapter Protocol)

Add a new debugger by implementing the **Debug Adapter Protocol** (DAP). The debug adapter is a separate process that translates between VS Code's generic debug UI and the language/runtime's actual debugging facilities.

Official guide: https://code.visualstudio.com/api/extension-guides/debugger-extension
Protocol spec: https://microsoft.github.io/debug-adapter-protocol/

## Three Components

| Component | Job | Where |
|---|---|---|
| Debug adapter | Speaks DAP over stdio/socket, drives the underlying debugger | Separate process (any language) |
| `DebugAdapterDescriptorFactory` | Tells VS Code how to launch the adapter | In the extension |
| `DebugConfigurationProvider` | Resolves/validates `launch.json` entries | In the extension |

Plus declarations in `package.json` under `contributes.debuggers`.

## package.json Manifest

```json
"contributes": {
  "debuggers": [
    {
      "type": "mydebug",
      "label": "My Debugger",
      "languages": ["mylang"],
      "configurationAttributes": {
        "launch": {
          "required": ["program"],
          "properties": {
            "program": {
              "type": "string",
              "description": "Path to program to debug"
            },
            "stopOnEntry": {
              "type": "boolean",
              "default": true
            }
          }
        }
      },
      "initialConfigurations": [
        {
          "type": "mydebug",
          "request": "launch",
          "name": "Launch program",
          "program": "${workspaceFolder}/main.mylang",
          "stopOnEntry": true
        }
      ]
    }
  ]
}
```

- `type` is the debugger identifier — referenced in user `launch.json`
- `configurationAttributes` powers IntelliSense inside `launch.json`
- `initialConfigurations` is what "Add Configuration" inserts

## Descriptor Factory

Tells VS Code how to start the adapter process for a debug session.

```typescript
import * as vscode from 'vscode';

class MyDebugAdapterDescriptorFactory
  implements vscode.DebugAdapterDescriptorFactory {

  createDebugAdapterDescriptor(
    _session: vscode.DebugSession,
    _executable: vscode.DebugAdapterExecutable | undefined,
  ): vscode.ProviderResult<vscode.DebugAdapterDescriptor> {
    // Option 1: launch a separate Node executable
    return new vscode.DebugAdapterExecutable('node', [
      this._extensionPath + '/dist/debug-adapter.js',
    ]);

    // Option 2: run the adapter inline in the extension host
    // return new vscode.DebugAdapterInlineImplementation(new MyDebugSession());

    // Option 3: connect to a server on a TCP port (for development)
    // return new vscode.DebugAdapterServer(4711);
  }

  constructor(private readonly _extensionPath: string) {}
}

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.debug.registerDebugAdapterDescriptorFactory(
      'mydebug',
      new MyDebugAdapterDescriptorFactory(context.extensionPath),
    ),
  );
}
```

**Choose the right form**:

- `DebugAdapterExecutable` — production. Adapter is a separate Node script.
- `DebugAdapterInlineImplementation` — testing, or very simple debuggers. Runs in extension host (so it shares the event loop — beware blocking).
- `DebugAdapterServer` — development convenience. Run the adapter in a debugger yourself, point VS Code at the port.

## Configuration Provider

Resolves user `launch.json` BEFORE the session starts. Useful for filling in defaults, validating, or generating configs dynamically.

```typescript
class MyDebugConfigurationProvider
  implements vscode.DebugConfigurationProvider {

  resolveDebugConfiguration(
    folder: vscode.WorkspaceFolder | undefined,
    config: vscode.DebugConfiguration,
    _token?: vscode.CancellationToken,
  ): vscode.ProviderResult<vscode.DebugConfiguration> {
    // Called when "Debug" is hit with no launch.json — supply a default
    if (!config.type && !config.request && !config.name) {
      const editor = vscode.window.activeTextEditor;
      if (editor && editor.document.languageId === 'mylang') {
        config.type = 'mydebug';
        config.request = 'launch';
        config.name = 'Launch';
        config.program = '${file}';
      }
    }

    if (!config.program) {
      return vscode.window
        .showInformationMessage('Cannot find a program to debug')
        .then(() => undefined);
    }
    return config;
  }
}

context.subscriptions.push(
  vscode.debug.registerDebugConfigurationProvider(
    'mydebug',
    new MyDebugConfigurationProvider(),
  ),
);
```

## DAP — What the Adapter Has to Implement

Minimum lifecycle:

| Request | Response | When |
|---|---|---|
| `initialize` | capabilities (e.g., `supportsConfigurationDoneRequest`) | Session start |
| `launch` or `attach` | empty success | After initialize |
| `setBreakpoints` | array of verified breakpoints | When breakpoints change |
| `configurationDone` | empty success | After initial setup |
| `threads` | list of thread ids/names | UI refresh |
| `stackTrace` | call frames | Thread is stopped |
| `scopes` | scopes per frame | Frame selected |
| `variables` | variables in a scope | Scope expanded |
| `continue` / `next` / `stepIn` / `stepOut` | empty success | User clicks step button |
| `disconnect` | empty success | Session ends |

Events the adapter must SEND to the UI:

- `initialized` (after responding to `initialize`)
- `stopped` (with reason: `breakpoint`, `step`, `exception`, etc.)
- `terminated` (debugging finished)
- `output` (console output for the Debug Console)
- `thread` (thread started/exited)

Use the `vscode-debugadapter` npm package to handle the protocol plumbing — implement just the verbs you support.

## Anti-Patterns

- ❌ Sending `stopped` without a previous `initialized` event — UI shows nothing
- ❌ Returning ad-hoc thread/frame ids — must be stable integers within the session
- ❌ Sending `output` events without a `category` (`stdout` | `stderr` | `console` | `important`)
- ❌ Long-running synchronous work in `DebugAdapterInlineImplementation` — blocks the extension host
- ❌ Forgetting to send `terminated` — session never closes and "Stop" hangs
