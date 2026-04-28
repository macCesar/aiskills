/**
 * Status command
 * Shows a quick overview of what's installed (read-only)
 */

import chalk from 'chalk';
import { existsSync, lstatSync } from 'fs';
import { join } from 'path';
import os from 'os';
import {
  SKILLS,
  PACKAGE_VERSION,
  getAgentsSkillsDir,
  getConfigDir,
  getPlatforms,
} from '../config.js';
import { hasHook } from '../hooks.js';
import { readLastCheck } from '../cache.js';

const CHECK = chalk.green('✓');
const CROSS = chalk.red('✗');

function countInstalledSkills(skillsDir) {
  let count = 0;
  for (const skill of SKILLS) {
    if (existsSync(join(skillsDir, skill))) {
      count++;
    }
  }
  return count;
}

function countLinkedSkills(platformSkillsDir) {
  let count = 0;
  for (const skill of SKILLS) {
    const linkPath = join(platformSkillsDir, skill);
    try {
      lstatSync(linkPath);
      count++;
    } catch {
      // not found
    }
  }
  return count;
}

function formatLastCheck(data) {
  if (!data) return chalk.gray('never');
  const date = new Date(data.lastCheck);
  const formatted = date.toISOString().replace('T', ' ').slice(0, 16);
  return `${formatted} (v${data.latestVersion})`;
}

export async function statusCommand() {
  const homeDir = os.homedir();
  const skillsDir = getAgentsSkillsDir(homeDir);
  const claudeDir = join(homeDir, '.claude');
  const cacheDir = getConfigDir();

  // Skills count
  const installedCount = countInstalledSkills(skillsDir);
  const totalCount = SKILLS.length;

  // Hook check
  const hookExists = hasHook(claudeDir);

  // Cache
  const lastCheck = readLastCheck(cacheDir);

  console.log('');
  console.log(chalk.bold('AI Skills Status'));
  console.log('');
  console.log(`  Version:    v${PACKAGE_VERSION}`);
  console.log(`  Skills:     ${installedCount}/${totalCount} installed`);
  console.log(`  Hook:       Claude Code SessionStart ${hookExists ? CHECK : CROSS}`);
  console.log(`  Last npm check: ${formatLastCheck(lastCheck)}`);

  // Platforms
  console.log('');
  console.log('  Platforms:');
  const platforms = getPlatforms(homeDir);
  for (const platform of platforms) {
    const linked = countLinkedSkills(platform.skillsDir);
    if (linked > 0) {
      console.log(`    ${platform.displayName.padEnd(13)} ${CHECK} ${linked} skills linked`);
    } else {
      console.log(`    ${platform.displayName.padEnd(13)} ${CROSS} ${chalk.gray('not linked')}`);
    }
  }

  console.log('');
}

export default { statusCommand };
