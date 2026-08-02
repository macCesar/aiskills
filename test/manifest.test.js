/**
 * Manifest integrity tests.
 *
 * These check the wiring between the repo's contents and the files that declare
 * them. Every assertion here corresponds to a failure this project has actually
 * shipped:
 *
 *   - `session-log` existed under skills/ but was missing from config's SKILLS,
 *     so the CLI never installed it and the skill reached nobody.
 *   - TiTools (same lib/, same release mechanics) published npm 2.6.0 while
 *     plugin.json still said 3.0.0, so the marketplace announced a version that
 *     did not exist.
 *
 * Both are invisible in review and obvious to a test, which is the whole reason
 * this file exists.
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { SKILLS, LEGACY_SKILLS, COMMANDS, LEGACY_COMMANDS } from '../lib/config.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS_DIR = path.join(ROOT, 'skills');
const COMMANDS_DIR = path.join(ROOT, 'commands');

const readJson = (...segments) => JSON.parse(readFileSync(path.join(ROOT, ...segments), 'utf8'));

const listDirs = (dir) =>
  existsSync(dir)
    ? readdirSync(dir, { withFileTypes: true })
        .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
        .map((entry) => entry.name)
    : [];

/**
 * Minimal frontmatter reader. Deliberately not a YAML parser — it only needs to
 * answer "is there a name and a description, and what is the name", and pulling
 * in a YAML dependency for that would be the expensive way to ask.
 */
const readFrontmatter = (skillPath) => {
  const raw = readFileSync(skillPath, 'utf8');
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(raw);
  if (!match) return null;
  const block = match[1];
  const name = /^name:\s*(.+)$/m.exec(block);
  const description = /^description:\s*([\s\S]+?)(?=\n\w+:|$)/m.exec(block);
  return {
    block,
    name: name ? name[1].trim().replace(/^['"]|['"]$/g, '') : null,
    description: description ? description[1].trim().replace(/^['"]|['"]$/g, '') : null,
  };
};

const skillDirs = listDirs(SKILLS_DIR);

describe('skills are wired into the CLI', () => {
  test('every skill in SKILLS exists on disk', () => {
    for (const skill of SKILLS) {
      const skillMd = path.join(SKILLS_DIR, skill, 'SKILL.md');
      assert.ok(existsSync(skillMd), `SKILLS lists "${skill}" but skills/${skill}/SKILL.md is missing`);
    }
  });

  test('every skill on disk is listed in SKILLS', () => {
    for (const dir of skillDirs) {
      assert.ok(
        SKILLS.includes(dir),
        `skills/${dir}/ exists but is not in lib/config.js SKILLS — the CLI will never install it`,
      );
    }
  });

  test('SKILLS and LEGACY_SKILLS do not overlap', () => {
    const overlap = SKILLS.filter((skill) => LEGACY_SKILLS.includes(skill));
    assert.deepEqual(overlap, [], `these skills are installed and marked legacy at once: ${overlap.join(', ')}`);
  });

  test('LEGACY_SKILLS are gone from the repo', () => {
    for (const skill of LEGACY_SKILLS) {
      assert.ok(
        !existsSync(path.join(SKILLS_DIR, skill)),
        `"${skill}" is marked legacy for removal but skills/${skill}/ still ships`,
      );
    }
  });
});

describe('skill frontmatter', () => {
  for (const skill of skillDirs) {
    test(`${skill} declares a parseable name and description`, () => {
      const fm = readFrontmatter(path.join(SKILLS_DIR, skill, 'SKILL.md'));
      assert.ok(fm, `skills/${skill}/SKILL.md has no YAML frontmatter block`);
      assert.equal(fm.name, skill, `frontmatter name "${fm.name}" does not match directory "${skill}"`);
      assert.ok(fm.description && fm.description.length > 0, `skills/${skill}/SKILL.md has an empty description`);
    });
  }
});

describe('reference files a skill points at exist', () => {
  for (const skill of skillDirs) {
    test(`${skill} has no broken references/ pointer`, () => {
      const skillDir = path.join(SKILLS_DIR, skill);
      const body = readFileSync(path.join(skillDir, 'SKILL.md'), 'utf8');
      const referenced = new Set(body.match(/references\/[A-Za-z0-9._-]+\.md/g) ?? []);
      for (const ref of referenced) {
        assert.ok(existsSync(path.join(skillDir, ref)), `skills/${skill}/SKILL.md points at ${ref}, which does not exist`);
      }
    });
  }
});

describe('commands are wired into the CLI', () => {
  test('every command in COMMANDS exists on disk', () => {
    for (const command of COMMANDS) {
      assert.ok(
        existsSync(path.join(COMMANDS_DIR, `${command}.md`)),
        `COMMANDS lists "${command}" but commands/${command}.md is missing`,
      );
    }
  });

  test('every command file is listed in COMMANDS', () => {
    const files = existsSync(COMMANDS_DIR)
      ? readdirSync(COMMANDS_DIR).filter((file) => file.endsWith('.md'))
      : [];
    for (const file of files) {
      const name = path.basename(file, '.md');
      assert.ok(COMMANDS.includes(name), `commands/${file} exists but is not in lib/config.js COMMANDS`);
    }
  });

  test('COMMANDS and LEGACY_COMMANDS do not overlap', () => {
    const overlap = COMMANDS.filter((command) => LEGACY_COMMANDS.includes(command));
    assert.deepEqual(overlap, [], `these commands are installed and marked legacy at once: ${overlap.join(', ')}`);
  });
});

describe('release manifests stay in sync', () => {
  test('package.json and plugin.json declare the same version', () => {
    const pkg = readJson('package.json');
    const plugin = readJson('.claude-plugin', 'plugin.json');
    assert.equal(
      plugin.version,
      pkg.version,
      'plugin.json is what Claude Code compares to invalidate its plugin cache. Out of sync, ' +
        'marketplace users keep running the old code after an npm release.',
    );
  });

  test('the marketplace points at the plugin by name', () => {
    const marketplace = readJson('.claude-plugin', 'marketplace.json');
    const plugin = readJson('.claude-plugin', 'plugin.json');
    const names = marketplace.plugins.map((entry) => entry.name);
    assert.ok(names.includes(plugin.name), `marketplace.json lists ${names.join(', ')} but plugin.json is "${plugin.name}"`);
  });
});

describe('bundled JSON parses', () => {
  const jsonFiles = [];
  for (const skill of skillDirs) {
    const evalsDir = path.join(SKILLS_DIR, skill, 'evals');
    if (!existsSync(evalsDir)) continue;
    for (const file of readdirSync(evalsDir).filter((entry) => entry.endsWith('.json'))) {
      jsonFiles.push(path.join(evalsDir, file));
    }
  }

  for (const file of jsonFiles) {
    test(path.relative(ROOT, file), () => {
      assert.doesNotThrow(() => JSON.parse(readFileSync(file, 'utf8')));
    });
  }
});
