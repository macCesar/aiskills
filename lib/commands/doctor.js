/**
 * Doctor command
 * Diagnoses installation health (read-only)
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
const WARN = chalk.yellow('⚠');

export async function doctorCommand() {
  const homeDir = os.homedir();
  const skillsDir = getAgentsSkillsDir(homeDir);
  const claudeDir = join(homeDir, '.claude');
  const cacheDir = getConfigDir();

  let issues = 0;
  const symlinkIssues = [];

  console.log('');
  console.log(chalk.bold('AI Skills Doctor'));
  console.log('');
  console.log('  Checking installation health...');
  console.log('');

  // CLI version
  console.log(`  ${CHECK} CLI version: v${PACKAGE_VERSION}`);

  // Skills check
  const missingSkills = [];
  for (const skill of SKILLS) {
    if (!existsSync(join(skillsDir, skill))) {
      missingSkills.push(skill);
    }
  }
  const installedCount = SKILLS.length - missingSkills.length;
  if (missingSkills.length === 0) {
    console.log(`  ${CHECK} Skills: ${installedCount}/${SKILLS.length} installed in ~/.agents/skills/`);
  } else {
    console.log(`  ${CROSS} Skills: ${installedCount}/${SKILLS.length} installed in ~/.agents/skills/ (missing: ${missingSkills.join(', ')})`);
    issues += missingSkills.length;
  }

  // Hook check
  if (hasHook(claudeDir)) {
    console.log(`  ${CHECK} Hook: SessionStart configured`);
  } else {
    console.log(`  ${CROSS} Hook: SessionStart not configured`);
    issues++;
  }

  // Cache check
  const lastCheck = readLastCheck(cacheDir);
  if (lastCheck) {
    const hoursAgo = Math.round((Date.now() - lastCheck.lastCheck) / (1000 * 60 * 60));
    const timeLabel = hoursAgo < 1 ? 'less than an hour ago' : `${hoursAgo} hour${hoursAgo === 1 ? '' : 's'} ago`;
    console.log(`  ${CHECK} Cache: last check ${timeLabel}`);
  } else {
    console.log(`  ${WARN} Cache: no check recorded`);
  }

  // Platforms
  console.log('');
  console.log('  Platforms:');
  const platforms = getPlatforms(homeDir);
  for (const platform of platforms) {
    const missing = [];
    const broken = [];

    for (const skill of SKILLS) {
      const linkPath = join(platform.skillsDir, skill);
      try {
        const stat = lstatSync(linkPath);
        if (stat.isSymbolicLink()) {
          // Check if target exists
          if (!existsSync(linkPath)) {
            broken.push(skill);
          }
        }
        // exists (symlink or directory), count as linked
      } catch {
        missing.push(skill);
      }
    }

    const linkedCount = SKILLS.length - missing.length - broken.length;

    if (missing.length === 0 && broken.length === 0) {
      console.log(`    ${CHECK} ${platform.displayName}: ${SKILLS.length}/${SKILLS.length} skills linked`);
    } else {
      const problems = [];
      if (missing.length > 0) problems.push(`missing: ${missing.join(', ')}`);
      if (broken.length > 0) problems.push(`broken: ${broken.join(', ')}`);
      console.log(`    ${CROSS} ${platform.displayName}: ${linkedCount}/${SKILLS.length} skills linked (${problems.join('; ')})`);
      issues += missing.length + broken.length;

      // Collect symlink issues for detailed report
      for (const skill of broken) {
        symlinkIssues.push(`${CROSS} ~/${platform.name === 'claude' ? '.claude' : `.${platform.name}`}/skills/${skill} → broken symlink (target missing)`);
      }
      for (const skill of missing) {
        symlinkIssues.push(`${CROSS} ~/${platform.name === 'claude' ? '.claude' : `.${platform.name}`}/skills/${skill} → not found`);
      }
    }
  }

  // Symlink issues detail
  if (symlinkIssues.length > 0) {
    console.log('');
    console.log(`  ${WARN} Symlink issues:`);
    for (const issue of symlinkIssues) {
      console.log(`    ${issue}`);
    }
  }

  // Summary
  console.log('');
  if (issues === 0) {
    console.log(chalk.green(`  No issues found.`));
  } else {
    console.log(chalk.yellow(`  ${issues} issue${issues === 1 ? '' : 's'} found. Run 'aiskills install' to fix.`));
  }
  console.log('');
}

export default { doctorCommand };
