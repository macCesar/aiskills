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

    test(`${skill} frontmatter stays within the 1024-char spec limit`, () => {
      const fm = readFrontmatter(path.join(SKILLS_DIR, skill, 'SKILL.md'));
      assert.ok(
        fm.block.length <= 1024,
        `frontmatter is ${fm.block.length} chars; agentskills.io caps it at 1024, past which agents may fail to load the skill`,
      );
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

describe('everything that ships is in the npm files allowlist', () => {
  // The quiet failure mode: the repo is correct, the tarball is not. `commands/`
  // was missing from this list until 2026-08-02, so every published version up to
  // 1.16.1 shipped without the /release slash command — invisible locally, because
  // the maintainer's CLI is npm link-ed to the repo and reads the working tree.
  const shipped = ['bin/', 'lib/', 'skills/', 'commands/'];

  for (const entry of shipped) {
    test(`${entry} is listed`, () => {
      const pkg = readJson('package.json');
      assert.ok(
        pkg.files.includes(entry),
        `package.json files omits ${entry} — npm would publish a package without it`,
      );
    });
  }

  test('maintainer-only paths stay out of the tarball', () => {
    const pkg = readJson('package.json');
    for (const entry of pkg.files) {
      assert.ok(
        !entry.startsWith('scripts/') && !entry.startsWith('.claude/'),
        `package.json files includes ${entry}, which is maintainer tooling and should not ship`,
      );
    }
  });
});

describe('the bundled hook uses the format Claude Code accepts', () => {
  // hooks.json currently declares no events, which is fine — this repo ships no
  // SessionStart hook. The assertions describe the shape any future entry must
  // take: the flat `{ command, timeout }` form fails settings validation on
  // session start, which is what forced TiTools's v2.4.0 → v2.4.1 hotfix. Same
  // lib/, same rule, so the guard belongs here before the first hook is added,
  // not after it breaks.
  test('every declared hook entry nests under a hooks array', () => {
    const hooks = readJson('hooks', 'hooks.json');
    const groups = Object.values(hooks.hooks ?? {}).flat();

    for (const group of groups) {
      assert.ok(
        Array.isArray(group.hooks),
        'a hook entry is missing its nested `hooks` array — this is the flat format that fails validation',
      );
      for (const entry of group.hooks) {
        assert.equal(entry.type, 'command', 'hook entries must declare type: "command"');
        assert.ok(entry.command, 'hook entry has no command');
      }
    }
  });

  test('any script a hook points at exists', () => {
    const hooks = readJson('hooks', 'hooks.json');
    const commands = Object.values(hooks.hooks ?? {})
      .flat()
      .flatMap((group) => group.hooks ?? [])
      .map((entry) => entry.command);

    for (const command of commands) {
      const match = /\$\{CLAUDE_PLUGIN_ROOT\}\/(\S+)/.exec(command);
      if (!match) continue;
      assert.ok(existsSync(path.join(ROOT, match[1])), `hooks.json points at ${match[1]}, which does not exist`);
    }
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
