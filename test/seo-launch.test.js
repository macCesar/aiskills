/**
 * seo-launch ships an executable, which is what makes it different from every
 * other skill here: a broken reference file degrades an answer, a broken script
 * fails in front of the user mid-audit. These tests cover the three ways that
 * happens — the file does not parse, the CLI contract moved, or the skill's
 * frontmatter stopped declaring the tools the workflow needs.
 *
 * The checks that read a live site are not tested here: they talk to the network
 * by design, and a test that depends on a third party's headers fails for
 * reasons that have nothing to do with this repo. What validates those is
 * running the script against a site known to be complete and one known not to
 * be, and seeing it tell them apart.
 *
 * `dimensiones()` is the exception, and it gets its own suite below. It is pure
 * — bytes in, a tuple out, no network — and it is the most intricate code in the
 * script: it walks JPEG segments looking for the SOF and unpacks bit fields out
 * of VP8L and VP8X headers. It also produces the skill's most valuable finding,
 * the image declared 1200×630 that measures something else, so a silent
 * regression there costs the audit its best check.
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILL_DIR = path.join(ROOT, 'skills', 'seo-launch');
const SCRIPT = path.join(SKILL_DIR, 'scripts', 'auditar_seo.py');

/** Runs python3 and returns { status, stdout, stderr } without throwing on a non-zero exit. */
const run = (args, options = {}) => {
  try {
    const stdout = execFileSync('python3', args, { encoding: 'utf8', stdio: 'pipe', ...options });
    return { status: 0, stdout, stderr: '' };
  } catch (error) {
    return { status: error.status ?? 1, stdout: error.stdout ?? '', stderr: error.stderr ?? '' };
  }
};

describe('seo-launch frontmatter', () => {
  const body = readFileSync(path.join(SKILL_DIR, 'SKILL.md'), 'utf8');
  const block = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(body)?.[1] ?? '';

  test('declares the tools the workflow needs', () => {
    // Stage 2 writes files and generates images; without Write, Edit and Bash
    // the skill can audit and then not do the half the user authorized.
    const declared = /^allowed-tools:\s*(.+)$/m.exec(block)?.[1] ?? '';
    for (const tool of ['Read', 'Grep', 'Glob', 'Bash', 'Edit', 'Write']) {
      assert.ok(declared.includes(tool), `allowed-tools is missing ${tool}: "${declared}"`);
    }
  });

  test('points at the audit script by its real path', () => {
    assert.ok(existsSync(SCRIPT), 'skills/seo-launch/scripts/auditar_seo.py is missing');
    assert.ok(
      body.includes('scripts/auditar_seo.py'),
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
    const cache = mkdtempSync(path.join(tmpdir(), 'seo-launch-'));
    try {
      const result = run(['-m', 'py_compile', SCRIPT], { env: { ...process.env, PYTHONPYCACHEPREFIX: cache } });
      assert.equal(result.status, 0, `py_compile failed:\n${result.stderr}`);
    } finally {
      rmSync(cache, { recursive: true, force: true });
    }
  });

  test('--help answers and documents both flags', () => {
    const result = run([SCRIPT, '--help']);
    assert.equal(result.status, 0, `--help exited ${result.status}:\n${result.stderr}`);
    assert.match(result.stdout, /--no-network/);
    assert.match(result.stdout, /--local/);
  });

  test('a missing URL is an error, not a crash', () => {
    const result = run([SCRIPT]);
    assert.equal(result.status, 2, 'argparse should exit 2 when the required argument is absent');
    assert.match(result.stderr, /url/i);
  });

  test('TLS verification is on unless --local asks for it', () => {
    // The regression this guards: an audit tool that never verifies would
    // happily read a man-in-the-middled response and report it as healthy.
    const source = readFileSync(SCRIPT, 'utf8');
    assert.match(source, /VERIFICAR_TLS = True/, 'the default must be verification on');
    assert.match(
      source,
      /if not VERIFICAR_TLS:[\s\S]{0,200}?CERT_NONE/,
      'CERT_NONE must be reachable only behind the --local flag',
    );
  });
});

/**
 * Loads the script as a module and calls dimensiones() on headers built byte by
 * byte here, so the fixtures are readable as the format specs they encode
 * rather than opaque blobs checked into the repo.
 */
const PROBE = `
import importlib.util, json, sys

spec = importlib.util.spec_from_file_location('auditar_seo', sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def png(w, h):
    # 8-byte signature, then the IHDR chunk: width at 16:20, height at 20:24.
    return b'\\x89PNG\\r\\n\\x1a\\n' + (13).to_bytes(4, 'big') + b'IHDR' \\
        + w.to_bytes(4, 'big') + h.to_bytes(4, 'big')

def jpeg(w, h):
    # SOI, an APP0 the parser must step over, then SOF0 carrying the size.
    return (b'\\xff\\xd8'
            + b'\\xff\\xe0' + (16).to_bytes(2, 'big') + b'\\x00' * 14
            + b'\\xff\\xc0' + (17).to_bytes(2, 'big') + b'\\x08'
            + h.to_bytes(2, 'big') + w.to_bytes(2, 'big')
            + b'\\x00' * 10)

def webp_vp8l(w, h):
    # 14 bits per axis, stored minus one, packed little-endian after the 0x2f tag.
    bits = (w - 1) | ((h - 1) << 14)
    return b'RIFF' + (0).to_bytes(4, 'little') + b'WEBP' + b'VP8L' \\
        + (0).to_bytes(4, 'little') + b'\\x2f' + bits.to_bytes(4, 'little')

def webp_vp8x(w, h):
    # 24 bits per axis, minus one, after four bytes of flags.
    return b'RIFF' + (0).to_bytes(4, 'little') + b'WEBP' + b'VP8X' \\
        + (10).to_bytes(4, 'little') + b'\\x00' * 4 \\
        + (w - 1).to_bytes(3, 'little') + (h - 1).to_bytes(3, 'little')

print(json.dumps({
    'png': mod.dimensiones(png(1200, 630)),
    'jpeg': mod.dimensiones(jpeg(1200, 630)),
    'webp_vp8l': mod.dimensiones(webp_vp8l(1200, 630)),
    'webp_vp8x': mod.dimensiones(webp_vp8x(1200, 630)),
    'apple_touch_png': mod.dimensiones(png(180, 180)),
    'truncated_png': mod.dimensiones(b'\\x89PNG\\r\\n\\x1a\\n' + b'\\x00' * 8),
    'html_not_an_image': mod.dimensiones(b'<!doctype html><html><head><title>'),
}))
`;

describe('dimensiones() reads the real size out of a file header', () => {
  const result = run(['-c', PROBE, SCRIPT]);
  assert.equal(result.status, 0, `the probe crashed:\n${result.stderr}`);
  const sizes = JSON.parse(result.stdout);

  for (const format of ['png', 'jpeg', 'webp_vp8l', 'webp_vp8x']) {
    test(`${format} at 1200x630`, () => {
      assert.deepEqual(sizes[format], [1200, 630]);
    });
  }

  test('a non-square-friendly size is not rounded or assumed', () => {
    // 180x180 is the apple-touch-icon. Reading it as 1200x630 because that is
    // what the skill talks about the most would hide a real mismatch.
    assert.deepEqual(sizes.apple_touch_png, [180, 180]);
  });

  test('a truncated header gives up instead of returning garbage', () => {
    // A Range request can return fewer bytes than asked for. Inventing a size
    // here would report a wrong dimension as if it had been measured.
    assert.equal(sizes.truncated_png, null);
  });

  test('an og:image URL that serves HTML is not read as an image', () => {
    assert.equal(sizes.html_not_an_image, null);
  });
});

const php = (() => {
  try {
    execFileSync('php', ['--version'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
})();

describe('the assets templates', () => {
  test('head.php parses', { skip: php ? false : 'php is not installed here' }, () => {
    // A parse error in this template does not show up as an error to the
    // person installing it: PHP renders a blank page, which reads as the skill
    // having done nothing.
    const template = path.join(SKILL_DIR, 'assets', 'head.php');
    try {
      execFileSync('php', ['-l', template], { encoding: 'utf8', stdio: 'pipe' });
    } catch (error) {
      assert.fail(`php -l rejected head.php:\n${error.stdout ?? ''}${error.stderr ?? ''}`);
    }
  });
});
