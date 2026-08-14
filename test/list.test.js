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

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

import { parseDescription, wrapDescription } from '../lib/commands/list.js';

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
