/**
 * `aiskills list` renders the only screen where a skill's description is read
 * by a human instead of an agent. Both assertions here correspond to what that
 * screen actually shipped:
 *
 *   - every row printed a stray leading `'`, because the parser handled
 *     `description: "…"` but not the single-quoted YAML all seven skills use.
 *   - long descriptions were printed unwrapped, so the terminal broke them at
 *     column zero and the description column stopped lining up.
 */

import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdtemp, rm, mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

import { parseDescription, wrapDescription } from '../lib/commands/list.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const binPath = join(resolve(__dirname, '..'), 'bin', 'aiskills.js');

describe('parseDescription', () => {
  test('strips single-quoted YAML, which is what every skill here uses', () => {
    const block = "name: demo\ndescription: 'Audit a codebase. Then fix it.'\nallowed-tools: Read";
    assert.equal(parseDescription(block), 'Audit a codebase.');
  });

  test('strips double quotes too', () => {
    const block = 'name: demo\ndescription: "Design advice. More text."\n';
    assert.equal(parseDescription(block), 'Design advice.');
  });

  test('resolves the doubled apostrophe of single-quoted YAML', () => {
    // audit-codebase writes "what''s actually broken" — printing it raw shows
    // the escape to the user.
    const block = "description: 'Find what''s broken and say so. Nothing else.'\n";
    assert.equal(parseDescription(block), "Find what's broken and say so.");
  });

  test('keeps the whole text when there is no sentence break', () => {
    const block = "description: 'A short one with no period'\nallowed-tools: Read";
    assert.equal(parseDescription(block), 'A short one with no period');
  });

  test('collapses a description written across several lines', () => {
    const block = "description: 'First line\n  continues here. Second sentence.'\nallowed-tools: Read";
    assert.equal(parseDescription(block), 'First line continues here.');
  });

  test('returns null when there is no description', () => {
    assert.equal(parseDescription('name: demo\nallowed-tools: Read'), null);
  });
});

describe('wrapDescription', () => {
  // Widths here are at or above the 24-column floor the module enforces;
  // anything narrower is clamped, which is its own test at the end.
  test('breaks on word boundaries, never past the column', () => {
    const lines = wrapDescription('one two three four five six seven eight nine', 24, 5);
    for (const line of lines) {
      assert.ok(line.length <= 24, `"${line}" is ${line.length} columns, over the 24 available`);
    }
    assert.ok(lines.length > 1, 'the text is longer than one line and should have wrapped');
    assert.equal(lines.join(' '), 'one two three four five six seven eight nine');
  });

  test('caps at maxLines and marks the cut with an ellipsis', () => {
    const text = 'one two three four five six seven eight nine ten eleven twelve thirteen';
    const lines = wrapDescription(text, 24, 2);
    assert.equal(lines.length, 2);
    assert.ok(lines[1].endsWith('…'), `expected an ellipsis, got "${lines[1]}"`);
    assert.ok(lines[1].length <= 24);
  });

  test('does not truncate what already fits', () => {
    const lines = wrapDescription('short enough', 40, 2);
    assert.deepEqual(lines, ['short enough']);
    assert.ok(!lines[0].endsWith('…'));
  });

  test('hard-breaks a word wider than the column instead of hanging', () => {
    // A bare URL in a description would otherwise never fit, and a wrapper that
    // waits for it to fit loops forever.
    const lines = wrapDescription('see https://example.com/a/very/long/path/that/never/fits', 24, 4);
    for (const line of lines) {
      assert.ok(line.length <= 24, `"${line}" is ${line.length} columns, over the 24 available`);
    }
  });

  test('a narrow window is clamped to a readable column', () => {
    const lines = wrapDescription('one two three four five six seven eight', 3, 2);
    assert.ok(lines[0].length > 3, 'width is clamped to a readable minimum');
  });
});


// The unit tests above cover the two pure functions. These run the command
// itself, which is the layer that caught nothing until `list` was found
// printing "No skills installed yet." and returning — a regression neither
// parseDescription nor wrapDescription can see.
//
// Every assertion runs against a temporary HOME. Reading the real one would
// make the result depend on whether this machine happens to have skills
// installed, which is how the sibling repo's suite passed locally and failed
// on a clean CI runner.
describe('list command', () => {
  let home;

  function run(args) {
    return new Promise((resolvePromise) => {
      execFile(
        process.execPath,
        [binPath, ...args],
        { timeout: 15000, env: { ...process.env, HOME: home, USERPROFILE: home } },
        (error, stdout, stderr) => {
          resolvePromise({
            code: error?.code ?? 0,
            stdout: stdout.toString(),
            stderr: stderr.toString(),
          });
        },
      );
    });
  }

  // Seed an installed skill by writing the SKILL.md `list` reads.
  async function install(name, description) {
    const skillDir = join(home, '.agents', 'skills', name);
    await mkdir(skillDir, { recursive: true });
    await writeFile(
      join(skillDir, 'SKILL.md'),
      `---\nname: ${name}\ndescription: '${description}'\n---\n\n# ${name}\n`,
      'utf8',
    );
  }

  beforeEach(async () => {
    home = await mkdtemp(join(tmpdir(), 'aiskills-list-'));
  });

  afterEach(async () => {
    await rm(home, { recursive: true, force: true });
  });

  test('prints a skills header', async () => {
    const result = await run(['list']);
    assert.equal(result.code, 0);
    assert.match(result.stdout, /AI Skills/i);
  });

  test('lists every skill even when none are installed', async () => {
    const result = await run(['list']);
    assert.equal(result.code, 0);
    for (const skill of ['audit-codebase', 'session-log']) {
      assert.match(result.stdout, new RegExp(skill), `expected skill "${skill}" in list output`);
    }
  });

  test('describes a skill that is not installed, from the bundled copy', async () => {
    const result = await run(['list']);
    assert.equal(result.code, 0);
    // The catalog is only useful before installing if it says what each skill
    // is for, so an uninstalled row must carry more than its own name.
    const row = result.stdout.split('\n').find((line) => line.includes('audit-codebase'));
    assert.ok(row, 'expected an audit-codebase row');
    assert.ok(
      row.replace('audit-codebase', '').trim().length > 20,
      `expected a description next to the skill name, got: ${row}`,
    );
  });

  test('reports 0 installed and how to install when nothing is there', async () => {
    const result = await run(['list']);
    assert.equal(result.code, 0);
    assert.match(result.stdout, /0\/\d+ installed/);
    assert.match(result.stdout, /No skills installed yet/i);
    assert.match(result.stdout, /aiskills install/);
  });

  test('counts installed skills and points at the directory holding them', async () => {
    await install('audit-codebase', 'Audit a whole codebase as one unit.');
    const result = await run(['list']);
    assert.equal(result.code, 0);
    assert.match(result.stdout, /1\/\d+ installed/);
    assert.match(result.stdout, /Audit a whole codebase as one unit/);
    assert.doesNotMatch(result.stdout, /No skills installed yet/i);
  });
});
