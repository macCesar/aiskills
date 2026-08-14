/**
 * npm-supply-chain ships an executable and a workflow template, so it has two
 * ways to fail that a documentation-only skill does not: the script breaks in
 * front of the user mid-audit, and the template is copied into someone's repo
 * where a typo becomes a failed release rather than a wrong sentence.
 *
 * The auditor's own suite runs it against two fixtures instead of asserting on
 * its source. A tool that reports the same verdict for a healthy repo and a
 * broken one is not measuring anything, and the only way to know it tells them
 * apart is to feed it one of each. The positive fixture is the shipped template
 * itself, which is also how the template gets checked for the mistake it exists
 * to prevent.
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILL_DIR = path.join(ROOT, 'skills', 'npm-supply-chain');
const SCRIPT = path.join(SKILL_DIR, 'scripts', 'auditar_npm.py');
const TEMPLATE = path.join(SKILL_DIR, 'assets', 'publish.yml');

/** Runs python3 and returns { status, stdout, stderr } without throwing on a non-zero exit. */
const run = (args, options = {}) => {
  try {
    const stdout = execFileSync('python3', args, { encoding: 'utf8', stdio: 'pipe', ...options });
    return { status: 0, stdout, stderr: '' };
  } catch (error) {
    return { status: error.status ?? 1, stdout: error.stdout ?? '', stderr: error.stderr ?? '' };
  }
};

describe('npm-supply-chain frontmatter', () => {
  const body = readFileSync(path.join(SKILL_DIR, 'SKILL.md'), 'utf8');
  const block = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(body)?.[1] ?? '';

  test('declares the tools the workflow needs', () => {
    // The skill reads a repo, runs the auditor, and writes a workflow file once
    // the user approves. Without Bash it cannot measure, and without Write it
    // can only describe the file it was asked to create.
    const declared = /^allowed-tools:\s*(.+)$/m.exec(block)?.[1] ?? '';
    for (const tool of ['Read', 'Grep', 'Glob', 'Bash', 'Edit', 'Write']) {
      assert.ok(declared.includes(tool), `allowed-tools is missing ${tool}: "${declared}"`);
    }
  });

  test('points at the audit script by its real path', () => {
    assert.ok(existsSync(SCRIPT), 'skills/npm-supply-chain/scripts/auditar_npm.py is missing');
    assert.ok(
      body.includes('scripts/auditar_npm.py'),
      'SKILL.md never names the script, so nothing tells the agent to run it',
    );
  });

  test('every assets/ template the body names exists', () => {
    const referenced = new Set(body.match(/assets\/[A-Za-z0-9._-]+/g) ?? []);
    for (const asset of referenced) {
      assert.ok(existsSync(path.join(SKILL_DIR, asset)), `SKILL.md points at ${asset}, which does not exist`);
    }
  });
});

describe('the audit script', () => {
  test('compiles', () => {
    // PYTHONPYCACHEPREFIX keeps __pycache__ out of the repo: py_compile writes
    // bytecode next to the source unless told otherwise.
    const cache = mkdtempSync(path.join(tmpdir(), 'npm-supply-chain-'));
    try {
      const result = run(['-m', 'py_compile', SCRIPT], { env: { ...process.env, PYTHONPYCACHEPREFIX: cache } });
      assert.equal(result.status, 0, `py_compile failed:\n${result.stderr}`);
    } finally {
      rmSync(cache, { recursive: true, force: true });
    }
  });

  test('--help answers and documents the flag', () => {
    const result = run([SCRIPT, '--help']);
    assert.equal(result.status, 0, `--help exited ${result.status}:\n${result.stderr}`);
    assert.match(result.stdout, /--no-network/);
  });

  test('a directory that does not exist is an error, not a traceback', () => {
    const result = run([SCRIPT, path.join(tmpdir(), 'no-such-project-here')]);
    assert.equal(result.status, 2, 'argparse should exit 2 when the path is not a directory');
    assert.match(result.stderr, /not a directory/i);
  });

  test('an unknown flag is rejected', () => {
    const result = run([SCRIPT, '--publish-everything']);
    assert.equal(result.status, 2);
  });

  test('it never prints the value of a credential', () => {
    // Listing secret names is enough to reason about orphans. Reading a value
    // would put a live token in a transcript, which is how a token becomes one
    // that has to be revoked.
    const source = readFileSync(SCRIPT, 'utf8');
    assert.doesNotMatch(source, /gh\W+secret\W+(view|get)/, 'the script must not read a secret value');
  });
});

/**
 * Two fixture repos, identical except for how the workflow authenticates: one
 * carries the shipped template, the other a token-auth publish. Both run with
 * --no-network so the suite never depends on the registry, gh, or a login.
 */
const fixture = (workflowSource) => {
  const dir = mkdtempSync(path.join(tmpdir(), 'npm-audit-fixture-'));
  mkdirSync(path.join(dir, '.github', 'workflows'), { recursive: true });
  writeFileSync(path.join(dir, 'package.json'), JSON.stringify({ name: '@acme/widget', version: '2.0.0' }));
  workflowSource(path.join(dir, '.github', 'workflows', 'publish.yml'));
  return dir;
};

describe('the auditor tells a healthy repo from a broken one', () => {
  test('the shipped template is reported as OIDC, not as token auth', () => {
    // The regression this pins: the template's own comments say "no NPM_TOKEN",
    // and a scan that reads comments as configuration reports the correct file
    // as the broken one.
    const dir = fixture((dest) => copyFileSync(TEMPLATE, dest));
    try {
      const result = run([SCRIPT, dir, '--no-network']);
      assert.equal(result.status, 0, `a healthy repo should exit 0:\n${result.stdout}`);
      assert.match(result.stdout, /publish\.yml: OIDC/);
      assert.doesNotMatch(result.stdout, /token auth/);
      assert.match(result.stdout, /runs on a pushed tag/);
      assert.doesNotMatch(result.stdout, /no version guard/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('a token-auth workflow is reported as a finding', () => {
    const dir = fixture((dest) =>
      writeFileSync(
        dest,
        ['on:', '  push:', '    branches: [main]', 'jobs:', '  publish:', '    runs-on: ubuntu-latest', '    steps:', '      - run: npm publish', '        env:', '          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}', ''].join('\n'),
      ),
    );
    try {
      const result = run([SCRIPT, dir, '--no-network']);
      assert.equal(result.status, 1, 'a repo publishing with a stored token should exit non-zero');
      assert.match(result.stdout, /token auth/);
      assert.doesNotMatch(result.stdout, /publish\.yml: OIDC/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('version files that disagree are caught', () => {
    const dir = fixture((dest) => copyFileSync(TEMPLATE, dest));
    try {
      mkdirSync(path.join(dir, '.claude-plugin'));
      writeFileSync(path.join(dir, '.claude-plugin', 'plugin.json'), JSON.stringify({ name: 'widget', version: '1.0.0' }));
      const result = run([SCRIPT, dir, '--no-network']);
      assert.equal(result.status, 1);
      assert.match(result.stdout, /plugin\.json is out of sync/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

const ruby = (() => {
  try {
    execFileSync('ruby', ['--version'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
})();

describe('the workflow template', () => {
  test('parses as YAML', { skip: ruby ? false : 'ruby is not installed here' }, () => {
    // A template that does not parse fails inside GitHub Actions, on a tag the
    // user already pushed, after the release commit has landed.
    try {
      execFileSync('ruby', ['-ryaml', '-e', `YAML.load_file(${JSON.stringify(TEMPLATE)})`], { stdio: 'pipe' });
    } catch (error) {
      assert.fail(`ruby rejected publish.yml:\n${error.stdout ?? ''}${error.stderr ?? ''}`);
    }
  });

  test('grants id-token and stores no credential', () => {
    const source = readFileSync(TEMPLATE, 'utf8');
    const uncommented = source.replace(/^\s*#.*$/gm, '').replace(/\s#.*$/gm, '');
    assert.match(uncommented, /id-token:\s*write/, 'without id-token: write there is no OIDC token to mint');
    assert.doesNotMatch(uncommented, /NODE_AUTH_TOKEN|secrets\./, 'a token reference drops the publish back to token auth');
  });
});
