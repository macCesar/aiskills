# SecretStorage

Secure credential storage using the OS keychain.

```typescript
class CredentialManager {
  private static readonly TOKEN_KEY = 'myExt.apiToken';

  constructor(private readonly secrets: vscode.SecretStorage) {}

  async getToken(): Promise<string | undefined> {
    return this.secrets.get(CredentialManager.TOKEN_KEY);
  }

  async setToken(token: string): Promise<void> {
    await this.secrets.store(CredentialManager.TOKEN_KEY, token);
  }

  async deleteToken(): Promise<void> {
    await this.secrets.delete(CredentialManager.TOKEN_KEY);
  }

  onDidChange(callback: (e: vscode.SecretStorageChangeEvent) => void): vscode.Disposable {
    return this.secrets.onDidChange(callback);
  }
}

// In activate():
export function activate(context: vscode.ExtensionContext) {
  const credentials = new CredentialManager(context.secrets);

  context.subscriptions.push(
    vscode.commands.registerCommand('myExt.login', async () => {
      const token = await vscode.window.showInputBox({
        prompt: 'Enter your API token',
        password: true,
        ignoreFocusOut: true,
      });
      if (token) {
        await credentials.setToken(token);
        vscode.window.showInformationMessage('Token saved securely.');
      }
    }),

    vscode.commands.registerCommand('myExt.logout', async () => {
      await credentials.deleteToken();
      vscode.window.showInformationMessage('Token removed.');
    }),

    credentials.onDidChange((e) => {
      if (e.key === 'myExt.apiToken') {
        // React to credential change
      }
    }),
  );
}
```
