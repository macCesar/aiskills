/**
 * Marketplace-plugin detection.
 *
 * Both bugs these cover shipped in v1.16.0 and were found by hand:
 *
 *   1. Uninstalling the plugin leaves its cache directory on disk. The CLI read
 *      that leftover directory as "the plugin provides this skill", skipped every
 *      symlink, and reported `0/6 skills linked` — leaving Claude Code with no
 *      skills and no way to repair it by re-running install.
 *   2. Slash commands never asked the question at all, so `/release` was
 *      installed alongside the plugin's own copy and appeared twice.
 *
 * Each test builds a throwaway home directory so the real one is never touched.
 */

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, existsSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  isClaudePluginEnabled,
  hasClaudePluginCache,
  pluginProvidesSkill,
  pluginProvidesCommand,
} from '../lib/claude-plugin.js';
import { createSkillSymlinks } from '../lib/symlink.js';
import { installCommands } from '../lib/installer.js';
import { CLAUDE_PLUGIN_KEY } from '../lib/config.js';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let home;

/** Build a fake home directory; returns its path. */
function makeHome() {
  return mkdtempSync(path.join(tmpdir(), 'aiskills-test-'));
}

/** Write ~/.claude/settings.json with the plugin enabled or disabled. */
function writeSettings(base, { enabled, file = 'settings.json' } = {}) {
  const dir = path.join(base, '.claude');
  mkdirSync(dir, { recursive: true });
  const body = enabled === undefined ? {} : { enabledPlugins: { [CLAUDE_PLUGIN_KEY]: enabled } };
  writeFileSync(path.join(dir, file), JSON.stringify(body, null, 2));
}

/** Populate the plugin cache as Claude Code leaves it. */
function writePluginCache(base, { skills = [], commands = [], version = '1.16.0' } = {}) {
  const root = path.join(base, '.claude', 'plugins', 'cache', 'maccesar-aiskills', 'aiskills', version);
  for (const skill of skills) {
    mkdirSync(path.join(root, 'skills', skill), { recursive: true });
  }
  if (commands.length > 0) {
    mkdirSync(path.join(root, 'commands'), { recursive: true });
    for (const command of commands) {
      writeFileSync(path.join(root, 'commands', `${command}.md`), '# stub\n');
    }
  }
}

/** Populate ~/.agents/skills so there is something to link to. */
function writeAgentsSkills(base, skills) {
  for (const skill of skills) {
    const dir = path.join(base, '.agents', 'skills', skill);
    mkdirSync(dir, { recursive: true });
    writeFileSync(path.join(dir, 'SKILL.md'), '---\nname: x\ndescription: y\n---\n');
  }
}

before(() => {
  home = makeHome();
});

after(() => {
  if (home) rmSync(home, { recursive: true, force: true });
});

describe('isClaudePluginEnabled', () => {
  test('false when no settings file exists', () => {
    const base = makeHome();
    assert.equal(isClaudePluginEnabled(base), false);
    rmSync(base, { recursive: true, force: true });
  });

  test('false when settings exist but the plugin is not listed', () => {
    const base = makeHome();
    writeSettings(base, {});
    assert.equal(isClaudePluginEnabled(base), false);
    rmSync(base, { recursive: true, force: true });
  });

  test('false when the plugin is listed as disabled', () => {
    const base = makeHome();
    writeSettings(base, { enabled: false });
    assert.equal(isClaudePluginEnabled(base), false);
    rmSync(base, { recursive: true, force: true });
  });

  test('true when enabled in settings.json', () => {
    const base = makeHome();
    writeSettings(base, { enabled: true });
    assert.equal(isClaudePluginEnabled(base), true);
    rmSync(base, { recursive: true, force: true });
  });

  test('true when enabled in settings.local.json', () => {
    const base = makeHome();
    writeSettings(base, { enabled: true, file: 'settings.local.json' });
    assert.equal(isClaudePluginEnabled(base), true);
    rmSync(base, { recursive: true, force: true });
  });

  test('false when settings.json is malformed rather than throwing', () => {
    const base = makeHome();
    mkdirSync(path.join(base, '.claude'), { recursive: true });
    writeFileSync(path.join(base, '.claude', 'settings.json'), '{ not valid json');
    assert.equal(isClaudePluginEnabled(base), false);
    rmSync(base, { recursive: true, force: true });
  });
});

describe('a leftover cache is not an installed plugin', () => {
  test('pluginProvidesSkill is false when the cache remains but the plugin was uninstalled', () => {
    const base = makeHome();
    writePluginCache(base, { skills: ['session-log'] });
    writeSettings(base, {}); // uninstalled: key gone from enabledPlugins
    assert.equal(
      pluginProvidesSkill('session-log', base),
      false,
      'a cache directory left behind by an uninstall must not count as the plugin providing the skill',
    );
    rmSync(base, { recursive: true, force: true });
  });

  test('hasClaudePluginCache tells "never installed" apart from "leftovers on disk"', () => {
    const clean = makeHome();
    assert.equal(hasClaudePluginCache(clean), false, 'no cache: the plugin was never installed');
    rmSync(clean, { recursive: true, force: true });

    const leftover = makeHome();
    writePluginCache(leftover, { skills: ['session-log'] });
    writeSettings(leftover, {});
    assert.equal(hasClaudePluginCache(leftover), true, 'cache present though the plugin is gone');
    assert.equal(
      isClaudePluginEnabled(leftover),
      false,
      'the pair (cache yes, enabled no) is what diagnostics report as an orphaned cache',
    );
    rmSync(leftover, { recursive: true, force: true });
  });

  test('pluginProvidesSkill is true only with cache AND enabled plugin', () => {
    const base = makeHome();
    writePluginCache(base, { skills: ['session-log'] });
    writeSettings(base, { enabled: true });
    assert.equal(pluginProvidesSkill('session-log', base), true);
    assert.equal(pluginProvidesSkill('not-shipped', base), false, 'skill absent from the cache');
    rmSync(base, { recursive: true, force: true });
  });
});

describe('createSkillSymlinks', () => {
  test('links the skill when the cache is stale but the plugin is gone', async () => {
    const base = makeHome();
    writeAgentsSkills(base, ['session-log']);
    writePluginCache(base, { skills: ['session-log'] });
    writeSettings(base, {}); // the exact v1.16.0 failure state

    const claudeSkills = path.join(base, '.claude', 'skills');
    const result = await createSkillSymlinks(claudeSkills, ['session-log'], base);

    assert.deepEqual(result.linked, ['session-log'], 'the skill must be linked, not skipped');
    assert.ok(existsSync(path.join(claudeSkills, 'session-log')));
    rmSync(base, { recursive: true, force: true });
  });

  test('skips and removes the stale symlink when the plugin is enabled', async () => {
    const base = makeHome();
    writeAgentsSkills(base, ['session-log']);
    writePluginCache(base, { skills: ['session-log'] });
    writeSettings(base, { enabled: true });

    const claudeSkills = path.join(base, '.claude', 'skills');
    mkdirSync(claudeSkills, { recursive: true });
    symlinkSync(path.join(base, '.agents', 'skills', 'session-log'), path.join(claudeSkills, 'session-log'), 'dir');

    const result = await createSkillSymlinks(claudeSkills, ['session-log'], base);

    assert.deepEqual(result.skipped, ['session-log']);
    assert.equal(
      existsSync(path.join(claudeSkills, 'session-log')),
      false,
      'the duplicate symlink must be cleaned up',
    );
    rmSync(base, { recursive: true, force: true });
  });

  test('links when there is no plugin cache at all', async () => {
    const base = makeHome();
    writeAgentsSkills(base, ['session-log']);
    const claudeSkills = path.join(base, '.claude', 'skills');
    const result = await createSkillSymlinks(claudeSkills, ['session-log'], base);
    assert.deepEqual(result.linked, ['session-log']);
    rmSync(base, { recursive: true, force: true });
  });
});

describe('installCommands', () => {
  test('installs the command when the plugin is not enabled', async () => {
    const base = makeHome();
    const result = await installCommands(REPO_ROOT, base);
    assert.ok(result.installed.includes('release'));
    assert.ok(existsSync(path.join(base, '.claude', 'commands', 'release.md')));
    rmSync(base, { recursive: true, force: true });
  });

  test('skips the command and removes the duplicate when the plugin provides it', async () => {
    const base = makeHome();
    writePluginCache(base, { commands: ['release'] });
    writeSettings(base, { enabled: true });

    // A copy left from an install that ran before the plugin existed.
    const commandsDir = path.join(base, '.claude', 'commands');
    mkdirSync(commandsDir, { recursive: true });
    writeFileSync(path.join(commandsDir, 'release.md'), '# stale copy\n');

    const result = await installCommands(REPO_ROOT, base);

    assert.deepEqual(result.skipped, ['release']);
    assert.deepEqual(result.installed, []);
    assert.equal(
      existsSync(path.join(commandsDir, 'release.md')),
      false,
      'the duplicate slash command must be cleaned up',
    );
    rmSync(base, { recursive: true, force: true });
  });

  test('installs the command when the cache is stale but the plugin is gone', async () => {
    const base = makeHome();
    writePluginCache(base, { commands: ['release'] });
    writeSettings(base, {});

    const result = await installCommands(REPO_ROOT, base);

    assert.ok(result.installed.includes('release'));
    assert.ok(existsSync(path.join(base, '.claude', 'commands', 'release.md')));
    rmSync(base, { recursive: true, force: true });
  });

  test('pluginProvidesCommand needs both the cache entry and the enabled plugin', () => {
    const base = makeHome();
    writePluginCache(base, { commands: ['release'] });
    writeSettings(base, { enabled: true });
    assert.equal(pluginProvidesCommand('release', base), true);
    assert.equal(pluginProvidesCommand('nonexistent', base), false);
    rmSync(base, { recursive: true, force: true });
  });
});
