/**
 * laravel-security-sweep ships an executable, so it gets the same treatment as
 * seo-launch: a broken script fails in front of the user mid-review, while a
 * broken reference only degrades an answer.
 *
 * The fixture tests are the ones that matter. A pattern search is an instrument,
 * and an instrument that reports the same thing for everything measures nothing;
 * each fixture therefore pairs a vulnerable line with a safe one written the way
 * the fix looks, and asserts the script tells them apart. They also pin the two
 * promises the SKILL.md makes about side effects: Laravel 3 projects are refused
 * rather than swept, and no value from `.env` is ever printed.
 */

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILL_DIR = path.join(ROOT, 'skills', 'laravel-security-sweep');
const SCRIPT = path.join(SKILL_DIR, 'scripts', 'barrido_laravel.py');

/** Runs python3 and returns { status, stdout, stderr } without throwing on a non-zero exit. */
const run = (args, options = {}) => {
  try {
    const stdout = execFileSync('python3', args, { encoding: 'utf8', stdio: 'pipe', ...options });
    return { status: 0, stdout, stderr: '' };
  } catch (error) {
    return { status: error.status ?? 1, stdout: error.stdout ?? '', stderr: error.stderr ?? '' };
  }
};

/** Writes a file inside a fixture, creating its directories. */
const put = (base, relative, content) => {
  const full = path.join(base, relative);
  mkdirSync(path.dirname(full), { recursive: true });
  writeFileSync(full, content);
};

const lock = (version) => JSON.stringify({ packages: [{ name: 'laravel/framework', version }] });

describe('laravel-security-sweep frontmatter', () => {
  const body = readFileSync(path.join(SKILL_DIR, 'SKILL.md'), 'utf8');
  const block = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(body)?.[1] ?? '';

  test('declares the tools both stages need', () => {
    // Stage 2 edits the project; without Edit and Write the skill can diagnose
    // and then not apply the fixes the user approved.
    const declared = /^allowed-tools:\s*(.+)$/m.exec(block)?.[1] ?? '';
    for (const tool of ['Read', 'Grep', 'Glob', 'Bash', 'Edit', 'Write']) {
      assert.ok(declared.includes(tool), `allowed-tools is missing ${tool}: "${declared}"`);
    }
  });

  test('does not declare Agent', () => {
    // The whole point of this skill is one agent instead of a swarm.
    const declared = /^allowed-tools:\s*(.+)$/m.exec(block)?.[1] ?? '';
    assert.ok(!/\bAgent\b/.test(declared), `allowed-tools should not include Agent: "${declared}"`);
  });

  test('names the script by its real path', () => {
    assert.ok(existsSync(SCRIPT), 'scripts/barrido_laravel.py is missing');
    assert.ok(body.includes('scripts/barrido_laravel.py'), 'SKILL.md never names the script');
  });

  test('every pattern ID the script can print is documented in patterns.md', () => {
    const script = readFileSync(SCRIPT, 'utf8');
    const catalog = readFileSync(path.join(SKILL_DIR, 'references', 'patterns.md'), 'utf8');
    const ids = new Set([
      ...[...script.matchAll(/Patron\('([A-Z-]+)'/g)].map((m) => m[1]),
      ...[...script.matchAll(/'id': '([A-Z-]+)'/g)].map((m) => m[1]),
    ]);
    assert.ok(ids.size > 10, `expected the script to define patterns, found ${ids.size}`);
    for (const id of ids) {
      assert.ok(catalog.includes(`## ${id} `), `${id} is printed by the script but has no section in patterns.md`);
    }
  });
});

describe('the sweep script CLI', () => {
  test('compiles', () => {
    const cache = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-pyc-'));
    try {
      const result = run(['-m', 'py_compile', SCRIPT], { env: { ...process.env, PYTHONPYCACHEPREFIX: cache } });
      assert.equal(result.status, 0, `py_compile failed:\n${result.stderr}`);
    } finally {
      rmSync(cache, { recursive: true, force: true });
    }
  });

  test('--help documents the flags the SKILL.md uses', () => {
    const result = run([SCRIPT, '--help']);
    assert.equal(result.status, 0);
    for (const flag of ['--json', '--sin-composer', '--max']) {
      assert.ok(result.stdout.includes(flag), `--help does not mention ${flag}`);
    }
  });

  test('refuses a directory that does not exist', () => {
    const result = run([SCRIPT, path.join(tmpdir(), 'no-such-laravel-project-xyz')]);
    assert.equal(result.status, 2);
  });

  test('refuses a directory that is not a Laravel project', () => {
    const dir = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-empty-'));
    try {
      assert.equal(run([SCRIPT, dir]).status, 2);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

describe('the sweep on fixture projects', () => {
  let project;
  let report;

  before(() => {
    project = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-10-'));
    put(project, 'artisan', '#!/usr/bin/env php\n');
    put(project, 'composer.lock', lock('v10.48.29'));
    put(project, 'app/Http/Kernel.php', "<?php\nclass Kernel {\n  protected $middleware = [\n    // \\App\\Http\\Middleware\\TrustHosts::class,\n  ];\n}\n");
    put(project, 'app/Http/Controllers/SearchController.php', [
      '<?php',
      'class SearchController {',
      '  public function vulnerable($q) {',
      '    return Product::whereRaw("MATCH(name) AGAINST(\'$q\')")->get();',
      '  }',
      '  public function safe($q) {',
      "    return Product::whereRaw('MATCH(name) AGAINST(?)', [$q])->get();",
      '  }',
      '  public function preview($url) {',
      '    return file_get_contents($url);',
      '  }',
      '  public function upload($request) {',
      "    return $request->file('f')->storeAs($request->directorio, $request->file('f')->getClientOriginalName());",
      '  }',
      '  public function sign() {',
      "    return hash_hmac('sha256', 'x', env('DOWNLOAD_SECRET', 'cambiar-por-clave'));",
      '  }',
      '}',
      '',
    ].join('\n'));
    put(project, 'resources/views/kiosk.blade.php', [
      '<script>',
      '  window.BRIDGE_KEY = @json($bridgeKey);',
      '  const items = @json($items);',
      '</script>',
      '@foreach ($rows as $key => $row) <option value="{{ $key }}">{{ $row }}</option> @endforeach',
      '',
    ].join('\n'));
    put(project, 'config/auth.php', "<?php\nreturn ['passwords' => env('AUTH_PASSWORD_BROKER', 'users'), 'table' => env('AUTH_PASSWORD_RESET_TOKEN_TABLE', 'password_reset_tokens')];\n");
    put(project, 'config/services.php', "<?php\nreturn [\n  'report' => env('REPORT_API_KEY', 'dev-report-key'),\n  'passport' => env('PASSPORT_CLIENT_SECRET', 'dev-secret'),\n];\n");
    put(project, 'routes/api.php', "<?php\nRoute::get('config', fn () => 1)->middleware('throttle:30,1');\nRoute::post('register', fn () => 1)->middleware('throttle:3,1');\n");
    put(project, 'app/Http/Controllers/Auth/PasswordResetLinkController.php', "<?php\n$status = Password::sendResetLink($request->only('email'));\nreturn $status == Password::RESET_LINK_SENT ? back() : back()->withErrors([]);\n");
    put(project, '.env', 'APP_KEY=base64:NEVER-PRINT-THIS-SECRET\nAPP_DEBUG=true\n');

    const result = run([SCRIPT, project, '--json', '--sin-composer']);
    assert.equal(result.status, 0, result.stderr);
    report = JSON.parse(result.stdout);
  });

  after(() => rmSync(project, { recursive: true, force: true }));

  const matches = (id) => report.patrones.find((group) => group.id === id)?.coincidencias ?? [];
  const projectChecks = () => report.proyecto.map((note) => note.id);

  test('reads the version and the Kernel structure', () => {
    assert.equal(report.mayor, 10);
    assert.equal(report.estructura, 'app/Http/Kernel.php');
  });

  test('flags interpolated raw SQL and not the bound version', () => {
    const lines = matches('SQL-RAW').map((m) => m.linea);
    assert.deepEqual(lines, [4], `expected only line 4, got ${JSON.stringify(lines)}`);
  });

  test('flags SSRF, client-controlled uploads and a secret with a literal fallback', () => {
    assert.ok(matches('SSRF').some((m) => m.linea === 10), 'file_get_contents($url) not flagged');
    assert.ok(matches('UPLOAD-NAME').length > 0, 'storeAs with the client name not flagged');
    assert.ok(matches('SECRET-FALLBACK').length > 0, 'env() secret with a default not flagged');
    assert.ok(matches('RESET-ENUM').length > 0, 'forgot-password response that reveals accounts not flagged');
  });

  test('flags a key printed into a page, not a plain @json or a foreach key', () => {
    const lines = matches('SECRET-IN-VIEW').map((m) => m.linea);
    assert.deepEqual(lines, [2], `expected only the window.BRIDGE_KEY line, got ${JSON.stringify(lines)}`);
  });

  test('does not treat the stock broker and token-table names as secrets', () => {
    const files = matches('SECRET-FALLBACK').map((m) => m.archivo);
    assert.ok(!files.includes('config/auth.php'), 'AUTH_PASSWORD_BROKER / AUTH_PASSWORD_RESET_TOKEN_TABLE were flagged');
    assert.ok(files.some((f) => f.endsWith('SearchController.php')), 'the real DOWNLOAD_SECRET fallback was lost');
  });

  test('excludes stock names by whole segment, not by substring', () => {
    // PORT inside REPORT or PASSPORT once made real secrets disappear.
    const lines = matches('SECRET-FALLBACK').filter((m) => m.archivo === 'config/services.php');
    assert.deepEqual(lines.map((m) => m.linea), [3, 4], 'REPORT_API_KEY / PASSPORT_CLIENT_SECRET fallbacks were not both flagged');
  });

  test('raises the shared-throttle check when several routes use throttle:N,1', () => {
    assert.ok(projectChecks().includes('THROTTLE-SHARED'), `project checks: ${projectChecks()}`);
  });

  test('raises the host-header check when resets have no fixed root and TrustHosts is commented', () => {
    assert.ok(projectChecks().includes('HOST-HEADER'), `project checks: ${projectChecks()}`);
  });

  test('reports APP_DEBUG without printing anything else from .env', () => {
    assert.ok(projectChecks().includes('APP-DEBUG'));
    const text = run([SCRIPT, project, '--sin-composer']).stdout + JSON.stringify(report);
    assert.ok(!text.includes('NEVER-PRINT-THIS-SECRET'), 'a value from .env leaked into the output');
  });

  test('drops the host-header check once the reset URL is pinned', () => {
    put(project, 'app/Providers/AuthServiceProvider.php', "<?php\nResetPassword::createUrlUsing(fn ($u, $t) => config('app.url'));\n");
    const pinned = JSON.parse(run([SCRIPT, project, '--json', '--sin-composer']).stdout);
    assert.ok(!pinned.proyecto.some((note) => note.id === 'HOST-HEADER'));
  });

  test('a composer audit that fails is an error, never "no advisories"', () => {
    // Regression: an old composer.lock made `composer audit` exit 1 with empty
    // stdout, the script parsed that as {} and reported a project with 83
    // advisories as clean. The fake binary reproduces exactly that output.
    const bin = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-bin-'));
    try {
      put(bin, 'composer', '#!/bin/sh\necho "In PluginManager.php: allow-plugins" >&2\nexit 1\n');
      execFileSync('chmod', ['+x', path.join(bin, 'composer')]);
      const env = { ...process.env, PATH: `${bin}${path.delimiter}${process.env.PATH}` };
      const result = JSON.parse(run([SCRIPT, project, '--json'], { env }).stdout);
      assert.equal(result.composer_audit.estado, 'error');
      assert.match(result.composer_audit.motivo, /allow-plugins/);
    } finally {
      rmSync(bin, { recursive: true, force: true });
    }
  });

  test('advisories are read even though composer audit exits non-zero when it finds them', () => {
    const bin = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-bin-'));
    try {
      const payload = JSON.stringify({
        advisories: { 'guzzlehttp/guzzle': [{ title: 'Host bypass', cve: 'CVE-2026-0001', affectedVersions: '<7.15.2', link: 'https://example.test' }] },
        abandoned: {},
      });
      put(bin, 'composer', `#!/bin/sh\necho '${payload}'\nexit 1\n`);
      execFileSync('chmod', ['+x', path.join(bin, 'composer')]);
      const env = { ...process.env, PATH: `${bin}${path.delimiter}${process.env.PATH}` };
      const result = JSON.parse(run([SCRIPT, project, '--json'], { env }).stdout);
      assert.equal(result.composer_audit.estado, 'ok');
      assert.equal(result.composer_audit.avisos.length, 1);
      assert.equal(result.composer_audit.avisos[0].cve, 'CVE-2026-0001');
    } finally {
      rmSync(bin, { recursive: true, force: true });
    }
  });

  test('recognizes the bootstrap/app.php structure', () => {
    const modern = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-12-'));
    try {
      put(modern, 'artisan', '');
      put(modern, 'composer.lock', lock('v12.3.0'));
      put(modern, 'bootstrap/app.php', "<?php\nreturn Application::configure()->withMiddleware(function ($m) {\n  $m->trustHosts(at: ['^example\\.com$']);\n})->create();\n");
      const result = JSON.parse(run([SCRIPT, modern, '--json', '--sin-composer']).stdout);
      assert.equal(result.estructura, 'bootstrap/app.php');
      assert.equal(result.mayor, 12);
    } finally {
      rmSync(modern, { recursive: true, force: true });
    }
  });

  test('reports Laravel 3 as out of scope instead of sweeping it', () => {
    const legacy = mkdtempSync(path.join(tmpdir(), 'laravel-sweep-3-'));
    try {
      put(legacy, 'artisan', '');
      put(legacy, 'paths.php', '<?php');
      put(legacy, 'laravel/core.php', '<?php');
      put(legacy, 'application/routes.php', '<?php DB::query("SELECT * FROM x WHERE id = $id");');
      const result = JSON.parse(run([SCRIPT, legacy, '--json', '--sin-composer']).stdout);
      assert.equal(result.mayor, 3);
      assert.equal(result.fuera_de_alcance, true);
      assert.equal(result.patrones, undefined, 'a Laravel 3 project should not be swept');
    } finally {
      rmSync(legacy, { recursive: true, force: true });
    }
  });
});
