# Testing Extensions (Advanced)

Beyond the basic Mocha setup covered in `architecture.md`: configuring `.vscode-test.mjs` for multiple suites, isolating unit tests from the VS Code runtime, mocking the `vscode` module, running tests in CI, and measuring coverage.

Official guide: https://code.visualstudio.com/api/working-with-extensions/testing-extension

## Two Test Layers

| Layer | Runs in | Imports `vscode`? | Speed |
|---|---|---|---|
| Unit | Plain Node (Mocha/Vitest) | No — only `services/`, pure logic | Fast |
| Integration | VS Code Extension Host (Electron) via `@vscode/test-electron` | Yes | Slow |

Keep `services/` free of `vscode` imports so unit tests don't need the Electron runtime. Integration tests cover wiring (commands registered, providers connected, activation works).

## `.vscode-test.mjs` (Multi-Suite)

The default file in `architecture.md` runs one suite. For real extensions, split by concern:

```javascript
import { defineConfig } from '@vscode/test-cli';

export default defineConfig([
  {
    label: 'integration',
    files: 'out/test/integration/**/*.test.js',
    workspaceFolder: './test/fixtures/workspace-basic',
    mocha: { timeout: 20000, ui: 'tdd' },
  },
  {
    label: 'multi-root',
    files: 'out/test/multi-root/**/*.test.js',
    workspaceFolder: './test/fixtures/workspace-multi.code-workspace',
    mocha: { timeout: 30000, ui: 'tdd' },
  },
  {
    label: 'insiders',
    version: 'insiders',
    files: 'out/test/integration/**/*.test.js',
    workspaceFolder: './test/fixtures/workspace-basic',
  },
]);
```

Run a specific suite: `vscode-test --label integration`.

## Workspace Fixtures

Integration tests need a real folder on disk because the editor expects a workspace:

```
test/fixtures/
├── workspace-basic/
│   ├── .vscode/
│   │   └── settings.json
│   ├── src/
│   │   └── sample.txt
│   └── package.json
└── workspace-multi.code-workspace
```

```json
// workspace-multi.code-workspace
{
  "folders": [
    { "path": "workspace-basic" },
    { "path": "workspace-secondary" }
  ]
}
```

Mutating fixtures in a test? Copy to a temp dir in `suiteSetup` and point the test there — leaving committed fixtures dirty between runs causes flakes.

## Mocking the `vscode` Module (Unit Tests)

`vscode` is provided by the Electron host — it has no npm package. Unit tests outside the host can't `import 'vscode'` directly. Two ways around this:

**1. Dependency injection** (preferred): never import `vscode` in `services/`. Pass the bits you need as parameters.

```typescript
// services/processor.ts — pure, no vscode import
export interface FileReader {
  read(path: string): Promise<string>;
}

export async function process(reader: FileReader, path: string): Promise<number> {
  const text = await reader.read(path);
  return text.split('\n').length;
}
```

Test it with a fake reader. The VS Code layer adapts `vscode.workspace.fs` to the `FileReader` interface.

**2. Module aliasing** (when DI isn't feasible): map `vscode` to a stub via the test runner.

```javascript
// vitest.config.ts (or jest moduleNameMapper)
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    alias: {
      vscode: new URL('./test/stubs/vscode.ts', import.meta.url).pathname,
    },
  },
});
```

```typescript
// test/stubs/vscode.ts — just enough surface to compile
export const window = {
  showInformationMessage: (..._args: unknown[]) => Promise.resolve(undefined),
  showErrorMessage: (..._args: unknown[]) => Promise.resolve(undefined),
  activeTextEditor: undefined,
};
export const workspace = {
  workspaceFolders: undefined as readonly unknown[] | undefined,
  getConfiguration: () => ({ get: () => undefined }),
};
export const Uri = { file: (p: string) => ({ fsPath: p }) };
// add more as needed
```

Aliasing is brittle — keep the stub minimal and prefer DI for non-trivial logic.

## CI: GitHub Actions

VS Code tests need a display. On Linux runners, wrap with `xvfb`:

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run compile
      - name: Run tests (Linux)
        if: runner.os == 'Linux'
        run: xvfb-run -a npm test
      - name: Run tests (non-Linux)
        if: runner.os != 'Linux'
        run: npm test
```

## Coverage

`@vscode/test-electron` runs in a real Electron process, so traditional Istanbul instrumentation can't simply wrap `node`. Use `c8` against the compiled output:

```json
// package.json
"scripts": {
  "test:coverage": "c8 --reporter=text --reporter=lcov vscode-test"
}
```

`c8` reads V8's native coverage and produces an `lcov.info` you can upload to Codecov/Coveralls. Coverage of integration-test execution paths only — unit tests should be measured separately and merged.

## Stable Test Patterns

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Activation', () => {
  suiteSetup(async () => {
    const ext = vscode.extensions.getExtension('publisher.my-extension');
    assert.ok(ext, 'Extension not found — check publisher and name in package.json');
    await ext!.activate();
  });

  test('registers expected commands', async () => {
    const commands = await vscode.commands.getCommands(true);
    for (const id of ['myExt.run', 'myExt.refresh']) {
      assert.ok(commands.includes(id), `Missing command: ${id}`);
    }
  });

  test('respects user setting', async () => {
    const config = vscode.workspace.getConfiguration('myExt');
    await config.update('mode', 'strict', vscode.ConfigurationTarget.Workspace);

    // ...exercise the feature

    await config.update('mode', undefined, vscode.ConfigurationTarget.Workspace);
  });
});
```

Always restore mutated settings/state in `teardown` or `suiteTeardown` — workspace state persists across test files.

## Anti-Patterns

- ❌ Putting business logic that doesn't touch the editor inside `extension.ts` — forces every test to spin up Electron
- ❌ Sharing state between tests via module-level variables — order-dependent failures
- ❌ `setTimeout`/`sleep` to "wait for activation" — use `await ext.activate()` and the `onDidStartDebugSession` (or similar) events
- ❌ Hardcoding absolute paths in fixtures — breaks on CI runners
- ❌ Running `xvfb-run` on macOS/Windows — only needed on Linux
- ❌ Trusting that a fresh test instance is clean — clear workspace state and SecretStorage explicitly when behavior depends on them
