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
import select from '../prompts/selectCancel.js';
import {
  detectPlatforms,
} from '../platform.js';
import { cleanupLegacyArtifacts, getSkillList } from '../cleanup.js';
import {
  installSkills,
  installCommands,
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
import os from 'os';

/**
 * Check if a platform has any skill symlinks installed
 * @param {string} platformSkillsDir - Platform skills directory
 * @returns {boolean} True if any skill symlink exists
 */
function hasAnySkillSymlink(platformSkillsDir) {
  if (!platformSkillsDir || !existsSync(platformSkillsDir)) return false;
  const skillList = getSkillList();
  return skillList.some((skill) => existsSync(join(platformSkillsDir, skill)));
}

/**
 * Perform the actual update for a specific scope
 * @param {string|undefined} baseDir - Base directory (undefined = global, path = local)
 * @param {string} repoDir - Repository directory
 * @param {Object} spinner - Ora spinner instance
 * @returns {Promise<void>}
 */
async function performUpdate(baseDir, repoDir, spinner) {
  const detectedPlatforms = detectPlatforms(baseDir);
  const platformsWithSymlinks = detectedPlatforms.filter((p) =>
    hasAnySkillSymlink(p.skillsDir)
  );

  spinner.start('Syncing skills...');
  const skillsResult = await installSkills(repoDir, baseDir);
  spinner.succeed(`${skillsResult.installed.length} skills updated`);

  // Sync slash commands when Claude Code has skill symlinks installed
  const claudePlatform = platformsWithSymlinks.find((p) => p.name === 'claude');
  if (claudePlatform) {
    spinner.start('Syncing slash commands...');
    const commandsResult = await installCommands(repoDir, baseDir);
    if (commandsResult.installed.length > 0) {
      spinner.succeed(
        `${commandsResult.installed.length} slash command${commandsResult.installed.length !== 1 ? 's' : ''} synced`
      );
    } else {
      spinner.info('No slash commands to sync');
    }
  }

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
 * @param {Object} options - Command options
 */
export async function updateCommand(options) {
  console.log('');
  console.log(chalk.bold.blue('AI Skills Updater'));
  console.log('');

  const spinner = ora();

  let baseDir = options.local ? process.cwd() : undefined;
  const hasSkillsAt = (dir) =>
    SKILLS.some((skill) => existsSync(join(getAgentsSkillsDir(dir), skill)));

  if (!options.local) {
    const projectDir = process.cwd();
    // When cwd === home, "local" and "global" point to the same .agents/skills dir
    const isHomeDir = projectDir === os.homedir();
    const hasLocalSkills = !isHomeDir && hasSkillsAt(projectDir);
    const hasGlobalSkills = hasSkillsAt(undefined);

    if (hasLocalSkills && hasGlobalSkills) {
      try {
        const scope = await select({
          message: 'Both local and global skills detected. What do you want to update:',
          choices: [
            { name: 'Global skills (user home)', value: 'global' },
            { name: 'Local skills (current project)', value: 'local' },
            { name: 'Both locations', value: 'both' },
          ],
          theme: {
            style: {
              answer: () => '',
              prefix: () => chalk.cyan('?'),
            },
          },
        });
        if (scope === 'cancel') {
          console.log('Cancelled.');
          process.exit(0);
        }
        if (scope === 'local') {
          baseDir = projectDir;
        } else if (scope === 'both') {
          baseDir = 'both';
        }
      } catch (error) {
        console.log('\nCancelled.');
        process.exit(0);
      }
    } else if (hasLocalSkills && !hasGlobalSkills) {
      baseDir = projectDir;
    }
  }

  if (baseDir === 'both') {
    console.log(chalk.cyan('Mode: Updating both global and local skills'));
  } else if (baseDir) {
    console.log(chalk.cyan('Mode: Local update (current project)'));
  } else {
    console.log(chalk.cyan('Mode: Global update (user home)'));
  }
  console.log('');

  if (baseDir !== 'both') {
    const skillsDir = getAgentsSkillsDir(baseDir);
    const hasSkillsInstalled = skillsDir && SKILLS.some((skill) => existsSync(join(skillsDir, skill)));
    if (!hasSkillsInstalled) {
      console.log(chalk.yellow('No skills installed at this location.'));
      console.log('Install them first with:');
      console.log('  aiskills install');
      console.log('');
      console.log('Looked for skills in:');
      console.log(`  ${baseDir ? 'Local' : 'Global'}: ${skillsDir}`);
      return;
    }
  }

  spinner.start('Checking for updates...');

  try {
    const hasUpdate = await checkForUpdate(PACKAGE_VERSION);

    if (hasUpdate) {
      let latestVersion = '(newer)';
      try {
        latestVersion = await fetchLatestNpmVersion();
      } catch {
        // Ignore error, we already know there's an update
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

    if (baseDir === 'both') {
      console.log(chalk.bold('Updating global skills...'));
      await performUpdate(undefined, repoDir, spinner);
      console.log('');

      console.log(chalk.bold('Updating local skills...'));
      await performUpdate(process.cwd(), repoDir, spinner);
    } else {
      await performUpdate(baseDir, repoDir, spinner);
    }

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
