/**
 * Basic CLI integration tests (offline, temp dirs).
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import { execFile } from 'node:child_process';
import { mkdtemp, writeFile, mkdir, rm } from 'node:fs/promises';
import { lstatSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import config from '../lib/config.js';

const binPath = join(process.cwd(), 'bin', 'aiskills.js');

function runCli(args, { cwd, env }) {
  return new Promise((resolve) => {
    execFile(process.execPath, [binPath, ...args], { cwd, env }, (error, stdout, stderr) => {
      resolve({
        code: error?.code ?? 0,
        stdout: stdout.toString(),
        stderr: stderr.toString(),
      });
    });
  });
}

async function makeTempDir(prefix) {
  return mkdtemp(join(tmpdir(), prefix));
}

async function makePlatformDirs(dir) {
  await mkdir(join(dir, '.claude'), { recursive: true });
  await mkdir(join(dir, '.gemini'), { recursive: true });
}

async function makeLocalSkills(dir) {
  const skillsDir = join(dir, '.agents', 'skills');
  await mkdir(skillsDir, { recursive: true });
  for (const skill of config.SKILLS) {
    await mkdir(join(skillsDir, skill), { recursive: true });
  }
}

async function writeAiFile(dir, filename = 'CLAUDE.md', content = '') {
  await writeFile(join(dir, filename), content, 'utf8');
}

describe('aiskills CLI', () => {
  it('install: local install links Claude only (Gemini auto-discovers from .agents/skills/)', async () => {
    const cwd = await makeTempDir('aiskills-project-');
    const home = await makeTempDir('aiskills-home-');
    await makePlatformDirs(cwd);

    const result = await runCli(['install', '--local', '--all'], {
      cwd,
      env: { ...process.env, HOME: home, USERPROFILE: home },
    });

    assert.ok(result.stdout.includes('Mode: Local installation'));
    assert.ok(/skills sync complete!/i.test(result.stdout));

    const skillsDir = join(cwd, '.agents', 'skills');
    assert.ok(existsSync(skillsDir));

    const claudeLink = join(cwd, '.claude', 'skills', config.SKILLS[0]);
    assert.ok(lstatSync(claudeLink).isSymbolicLink());

    const geminiSkillPath = join(cwd, '.gemini', 'skills', config.SKILLS[0]);
    assert.ok(!existsSync(geminiSkillPath), '.gemini/skills/ symlinks should not be created (Gemini auto-discovers from .agents/skills/)');

    await rm(cwd, { recursive: true, force: true });
    await rm(home, { recursive: true, force: true });
  });

  it('update: exits early when no skills installed', async () => {
    const cwd = await makeTempDir('aiskills-empty-');
    const home = await makeTempDir('aiskills-home-');
    const result = await runCli(['update'], {
      cwd,
      env: { ...process.env, HOME: home, USERPROFILE: home },
    });
    assert.ok(result.stdout.includes('No skills installed at this location.'));
    await rm(cwd, { recursive: true, force: true });
    await rm(home, { recursive: true, force: true });
  });

  it('update: shows npm update instructions when CLI is outdated and preserves context', async () => {
    const cwd = await makeTempDir('aiskills-project-');
    const home = await makeTempDir('aiskills-home-');
    await makeLocalSkills(cwd);
    await writeAiFile(cwd, 'CLAUDE.md', 'original');

    const result = await runCli(['update', '--local'], {
      cwd,
      env: {
        ...process.env,
        HOME: home,
        USERPROFILE: home,
        AISKILLS_TEST_NPM_LATEST_VERSION: '99.0.0',
      },
    });
    const output = `${result.stdout}\n${result.stderr}`;

    assert.ok(output.includes('New version available'));
    assert.ok(output.includes(`Current: v${config.PACKAGE_VERSION}`));
    assert.ok(output.includes('Latest:  99.0.0'));
    assert.ok(output.includes('npm update -g @maccesar/aiskills'));
    assert.ok(output.includes('aiskills update'));

    const content = await import('node:fs/promises').then(({ readFile }) => readFile(join(cwd, 'CLAUDE.md'), 'utf8'));
    assert.strictEqual(content, 'original');

    await rm(cwd, { recursive: true, force: true });
    await rm(home, { recursive: true, force: true });
  });

  it('update: syncs skills and preserves user context when CLI is current', async () => {
    const cwd = await makeTempDir('aiskills-project-');
    const home = await makeTempDir('aiskills-home-');
    await makeLocalSkills(cwd);
    await writeAiFile(cwd, 'CLAUDE.md', 'original');

    const result = await runCli(['update', '--local'], {
      cwd,
      env: {
        ...process.env,
        HOME: home,
        USERPROFILE: home,
        AISKILLS_TEST_NPM_LATEST_VERSION: config.PACKAGE_VERSION,
      },
    });
    const output = `${result.stdout}\n${result.stderr}`;

    assert.ok(output.includes(`CLI is up to date (v${config.PACKAGE_VERSION})`));
    assert.ok(output.includes('skills updated'));
    assert.ok(output.includes('Update complete!'));

    const content = await import('node:fs/promises').then(({ readFile }) => readFile(join(cwd, 'CLAUDE.md'), 'utf8'));
    assert.strictEqual(content, 'original');

    await rm(cwd, { recursive: true, force: true });
    await rm(home, { recursive: true, force: true });
  });

});
