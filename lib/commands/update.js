/**
 * Update command
 * Checks for a newer CLI version, then syncs skills from the installed package
 */

import chalk from 'chalk';
import ora from 'ora';
import {
  PACKAGE_VERSION,
  REPO_URL,
  SKILLS,
} from '../config.js';
import {
  detectPlatforms,
} from '../platform.js';
import { cleanupLegacyArtifacts, getSkillList } from '../cleanup.js';
import {
  installSkills,
  getLocalRepoDir,
} from '../installer.js';
import {
  checkForUpdate,
  fetchLatestNpmVersion,
} from '../downloader.js';
import { createSkillSymlinks } from '../symlink.js';
import { getAgentsSkillsDir } from '../config.js';
import { existsSync } from 'fs';
import { join } from 'path';

/**
 * Check if a platform has any skill symlinks installed
 */
function hasAnySkillSymlink(platformSkillsDir) {
  if (!platformSkillsDir || !existsSync(platformSkillsDir)) return false;
  const skillList = getSkillList();
  return skillList.some((skill) => existsSync(join(platformSkillsDir, skill)));
}

/**
 * Perform the actual update for a specific scope
 */
async function performUpdate(baseDir, repoDir, spinner) {
  const detectedPlatforms = detectPlatforms(baseDir);
  const platformsWithSymlinks = detectedPlatforms.filter((p) =>
    hasAnySkillSymlink(p.skillsDir)
  );

  spinner.start('Syncing skills...');
  const skillsResult = await installSkills(repoDir, baseDir);
  spinner.succeed(`${skillsResult.installed.length} skills updated`);

  cleanupLegacyArtifacts(baseDir);

  for (const platform of platformsWithSymlinks) {
    await createSkillSymlinks(
      platform.skillsDir,
      SKILLS,
      baseDir
    );
  }
}

/**
 * Update command handler
 */
export async function updateCommand(options) {
  console.log('');
  console.log(chalk.bold.blue('AI Skills Updater'));
  console.log('');

  const spinner = ora();

  const baseDir = options.local ? process.cwd() : undefined;

  if (baseDir) {
    console.log(chalk.cyan('Mode: Local update (current project)'));
  } else {
    console.log(chalk.cyan('Mode: Global update (user home)'));
  }
  console.log('');

  // Verify skills are installed
  const skillsDir = getAgentsSkillsDir(baseDir);
  const hasSkillsInstalled = skillsDir && SKILLS.some((skill) => existsSync(join(skillsDir, skill)));
  if (!hasSkillsInstalled) {
    console.log(chalk.yellow('No skills installed at this location.'));
    console.log('Install them first with:');
    console.log('  aiskills install');
    console.log('');
    return;
  }

  // Check for updates
  spinner.start('Checking for updates...');

  try {
    const hasUpdate = await checkForUpdate(PACKAGE_VERSION);

    if (hasUpdate) {
      let latestVersion = '(newer)';
      try {
        latestVersion = await fetchLatestNpmVersion();
      } catch {
        // Ignore
      }

      spinner.warn('New version available');
      console.log('');
      console.log(chalk.yellow('A newer version of aiskills is available on npm:'));
      console.log(`  Current: ${chalk.gray('v' + PACKAGE_VERSION)}`);
      console.log(`  Latest:  ${chalk.green(latestVersion)}`);
      console.log('');
      console.log('Update the CLI with:');
      console.log(`  ${chalk.cyan('npm update -g @maccesar/aiskills')}`);
      console.log('');
      console.log('After updating, run this command again:');
      console.log(`  ${chalk.cyan('aiskills update')}`);
      console.log('');
      return;
    }

    spinner.succeed(`CLI is up to date (v${PACKAGE_VERSION})`);

    const repoDir = getLocalRepoDir();
    if (!repoDir) {
      console.log('');
      console.log(chalk.red('Error: Could not locate skills source directory.'));
      console.log('Try reinstalling with:');
      console.log(`  ${chalk.cyan('npm install -g @maccesar/aiskills')}`);
      return;
    }

    await performUpdate(baseDir, repoDir, spinner);

    console.log('');
    console.log(chalk.green('✓ Update complete!'));
    console.log('');

  } catch (error) {
    spinner.fail('Update failed');
    console.error(chalk.red(error.message));
    console.log('');
    console.log('You can try manually installing from:');
    console.log(chalk.cyan(REPO_URL));
    process.exit(1);
  }
}

export default updateCommand;
