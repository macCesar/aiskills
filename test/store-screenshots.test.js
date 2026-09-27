import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const skill = path.join(root, 'skills/store-screenshots');
const script = path.join(skill, 'scripts/artwork.py');
const run = (...args) => spawnSync('python3', [script, ...args], { encoding: 'utf8' });
const svg = (w = '80', view = '0 0 80 120') => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="120" viewBox="${view}"><rect width="40" height="120" fill="#123456"/></svg>`;
const available = ['magick', 'rsvg-convert'].every(tool => !spawnSync(tool, ['--version']).error);

test('store-screenshots has valid discovery metadata and linked references', () => {
  const body = readFileSync(path.join(skill, 'SKILL.md'), 'utf8');
  const front = /^---\n([\s\S]*?)\n---/.exec(body)?.[1];
  assert.ok(front);
  assert.match(front, /^name: store-screenshots$/m);
  const description = /^description: (.+)$/m.exec(front)?.[1];
  assert.ok(description?.startsWith('Use when') && description.length <= 1024);
  for (const [, ref] of body.matchAll(/\]\((references\/[^)]+)\)/g)) {
    assert.ok(readFileSync(path.join(skill, ref)).length > 0);
  }
});

test('artwork CLI explains use and rejects malformed size', () => {
  assert.equal(run('--help').status, 0);
  assert.notEqual(run('check', '--size', '0x12', 'missing.png').status, 0);
});

test('export rejects ambiguous SVG dimensions before writing', () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'artwork-invalid-'));
  try {
    const input = path.join(dir, 'input.svg');
    for (const source of [svg('100%'), svg('80', '0 0 160 120')]) {
      writeFileSync(input, source);
      assert.notEqual(run('export', input, path.join(dir, 'output.png')).status, 0);
    }
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('SVG export preserves canvas, produces opaque RGB, and protects existing output', { skip: !available }, () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'artwork-render-'));
  try {
    const input = path.join(dir, 'input.svg');
    const output = path.join(dir, 'output.png');
    writeFileSync(input, svg());
    const rendered = run('export', input, output);
    assert.equal(rendered.status, 0, rendered.stderr);
    assert.equal(JSON.parse(rendered.stdout).width, 80);
    const bytes = readFileSync(output);
    assert.equal(bytes[24], 8);
    assert.equal(bytes[25], 2);
    assert.equal(run('check', '--size', '80x120', output).status, 0);
    assert.notEqual(run('check', '--size', '120x80', output).status, 0);
    assert.notEqual(run('export', input, output).status, 0);
    assert.deepEqual(readFileSync(output), bytes);
    writeFileSync(input, '<broken>');
    assert.notEqual(run('export', input, output, '--force').status, 0);
    assert.deepEqual(readFileSync(output), bytes);
    writeFileSync(input, svg());
    assert.equal(run('export', input, output, '--force').status, 0);
    const alpha = path.join(dir, 'alpha.png');
    assert.equal(spawnSync('magick', ['-size', '80x120', 'xc:none', '-define', 'png:color-type=6', alpha]).status, 0);
    assert.notEqual(run('check', alpha).status, 0);
    writeFileSync(output, bytes.subarray(0, 40));
    assert.notEqual(run('check', output).status, 0);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
