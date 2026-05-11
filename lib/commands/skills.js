/**
 * Skills command
 * Installs and manages skills in AI coding assistant directories
 */

import chalk from 'chalk';
import ora from 'ora';
import {
  SKILLS,
  getPlatforms,
  getAgentsSkillsDir,
} from '../config.js';
import select from '../prompts/selectCancel.js';
import checkbox, { Separator } from '../prompts/checkboxCancel.js';
import {
  detectPlatforms,
  detectOS,
} from '../platform.js';
import {
  getSkillList,
  removeSkillSymlinks,
  removeLegacySkillSymlinks,
  removeSkills,
  removeCommands,
} from '../cleanup.js';
import {
  installSkills,
  installCommands,
  getLocalRepoDir,
} from '../installer.js';
import { downloadRepoArchive } from '../downloader.js';
import { createSkillSymlinks } from '../symlink.js';
import { installHook } from '../hooks.js';
import { mkdtemp } from 'fs/promises';
import { existsSync } from 'fs';
import { join, resolve } from 'path';
import { tmpdir } from 'os';

function hasAnySkillSymlink(platformSkillsDir) {
  if (!platformSkillsDir || !existsSync(platformSkillsDir)) return false;
  const skillList = getSkillList();
  return skillList.some((skill) => existsSync(join(platformSkillsDir, skill)));
}

/**
 * Skills command handler
 * @param {Object} options - Command options
 */
export async function skillsCommand(options) {
  console.log('');
  console.log(chalk.bold.blue('AI Skills Manager'));
  console.log('');

  const isLocal = options.local;
  const customPath = options.path;

  // Determine base directory (Local vs Global)
  const baseDir = isLocal ? process.cwd() : (customPath ? resolve(customPath) : undefined);

  if (isLocal) {
    console.log(chalk.cyan('Mode: Local installation (current project)'));
  } else if (customPath) {
    console.log(chalk.cyan(`Mode: Custom path (${baseDir})`));
  } else {
    console.log(chalk.cyan('Mode: Global installation (user home)'));
  }
  console.log('');

  // Detect installed platforms at the target base directory
  const localPlatforms = detectPlatforms(baseDir);
  const globalPlatforms = detectPlatforms();
  let detectedPlatforms = localPlatforms;

  if (isLocal || options.path) {
    const localNames = new Set(localPlatforms.map((platform) => platform.name));
    const globalNames = new Set(globalPlatforms.map((platform) => platform.name));
    const allPlatforms = getPlatforms(baseDir);
    const merged = [...localPlatforms];
    for (const platform of allPlatforms) {
      if (globalNames.has(platform.name) && !localNames.has(platform.name)) {
        merged.push(platform);
      }
    }
    detectedPlatforms = merged;
  }

  if (detectedPlatforms.length === 0 && !options.path && !isLocal) {
    console.log(chalk.yellow('No AI coding assistants detected globally.'));
    console.log('Install one of: Claude Code or Gemini CLI.');
    console.log('(Codex CLI is supported via the canonical ~/.agents/skills/ — no platform-specific symlink needed.)');
    console.log('Or use: aiskills install --local');
    process.exit(1);
  }

  // Show detected platforms
  if (detectedPlatforms.length > 0) {
    for (const platform of detectedPlatforms) {
      console.log(chalk.green('✓'), `${platform.displayName} detected`);
    }
    console.log('');
  } else if (isLocal) {
    detectedPlatforms = getPlatforms(baseDir);
  }

  // Select platforms to install
  let selectedPlatforms = [];

  if (options.path) {
    selectedPlatforms = detectedPlatforms;
  } else if (options.all) {
    selectedPlatforms = detectedPlatforms;
  } else {
    try {
      const platformChoices = await checkbox({
        message: 'Select platforms to sync:',
        choices: [
          ...detectedPlatforms.map((p) => ({
            name: p.displayName,
            value: p.name,
            checked: hasAnySkillSymlink(p.skillsDir),
          })),
          new Separator(' ')
        ],
        shortcuts: { invert: null },
        theme: {
          style: {
            renderSelectedChoices: () => '',
            prefix: () => chalk.cyan('?'),
          },
        },
      });

      if (platformChoices.includes('cancel')) {
        console.log('Cancelled.');
        process.exit(0);
      }

      selectedPlatforms = detectedPlatforms.filter((p) =>
        platformChoices.includes(p.name)
      );
    } catch (error) {
      console.log('\nCancelled.');
      process.exit(0);
    }
  }

  const removeOnly = selectedPlatforms.length === 0;
  if (removeOnly) {
    console.log(chalk.yellow('No platforms selected. Removing all platform symlinks.'));
  }

  // Get repository directory (local or download)
  const spinner = ora();
  let repoDir = null;
  let tempDir = null;

  if (!removeOnly) {
    repoDir = getLocalRepoDir();

    if (!repoDir) {
      spinner.start('Downloading from GitHub...');
      try {
        tempDir = await mkdtemp(join(tmpdir(), 'aiskills-'));
        repoDir = await downloadRepoArchive(tempDir);
        spinner.succeed('Downloaded from GitHub');
      } catch (error) {
        spinner.fail('Failed to download');
        console.error(chalk.red(error.message));
        process.exit(1);
      }
    } else {
      console.log(chalk.green('Using local repository'));
    }
  }

  const selectedPlatformNames = new Set(selectedPlatforms.map((platform) => platform.name));

  try {
    if (!removeOnly) {
      // Install skills
      spinner.start('Installing skills...');
      const skillsResult = await installSkills(repoDir, baseDir);
      spinner.succeed(`${SKILLS.length} skill${SKILLS.length !== 1 ? 's' : ''} installed`);

      // Install or remove slash commands based on Claude Code selection
      if (selectedPlatformNames.has('claude')) {
        spinner.start('Installing slash commands...');
        const commandsResult = await installCommands(repoDir, baseDir);
        if (commandsResult.installed.length > 0) {
          spinner.succeed(
            `${commandsResult.installed.length} slash command${commandsResult.installed.length !== 1 ? 's' : ''} installed`
          );
        } else {
          spinner.info('No slash commands to install');
        }
      } else {
        const removed = removeCommands(baseDir);
        if (removed.removed.length > 0) {
          console.log(chalk.green('✓'), `${removed.removed.length} slash commands removed`);
        }
      }

      // Create symlinks for selected platforms
      for (const platform of selectedPlatforms) {
        removeLegacySkillSymlinks(platform.skillsDir);
        spinner.start(`Linking ${platform.displayName}...`);
        const symlinkResult = await createSkillSymlinks(
          platform.skillsDir,
          SKILLS,
          baseDir
        );
        if (symlinkResult.linked.length === SKILLS.length) {
          spinner.succeed(`${platform.displayName}: Skills linked`);
        } else {
          spinner.warn(
            `${platform.displayName}: ${symlinkResult.linked.length}/${SKILLS.length} skills linked`
          );
        }
      }
    } else {
      const skillsResult = removeSkills(baseDir);
      const commandsResult = removeCommands(baseDir);
      const platformResults = detectedPlatforms.map((platform) => {
        const symlinkResult = removeSkillSymlinks(platform.skillsDir);
        return {
          displayName: platform.displayName,
          removedCount: symlinkResult.removed.length,
        };
      });

      if (skillsResult.removed.length > 0) {
        console.log(chalk.green('✓'), `${skillsResult.removed.length} skills removed`);
      } else {
        console.log(chalk.gray('ℹ'), 'No skills to remove');
      }

      if (commandsResult.removed.length > 0) {
        console.log(chalk.green('✓'), `${commandsResult.removed.length} slash commands removed`);
      }

      for (const result of platformResults) {
        if (result.removedCount > 0) {
          console.log(chalk.green('✓'), `${result.displayName}: Skills unlinked`);
        } else {
          console.log(chalk.gray('ℹ'), `${result.displayName}: No symlinks found`);
        }
      }
    }

    // Install SessionStart hook for Claude Code auto-update
    if (!removeOnly && selectedPlatformNames.has('claude')) {
      const claudePlatform = selectedPlatforms.find((p) => p.name === 'claude');
      if (claudePlatform) {
        installHook(claudePlatform.configDir);
      }
    }

    // Remove symlinks for unselected detected platforms
    if (!removeOnly) {
      for (const platform of detectedPlatforms) {
        if (selectedPlatformNames.has(platform.name)) continue;
        spinner.start(`Unlinking ${platform.displayName}...`);
        const symlinkResult = removeSkillSymlinks(platform.skillsDir);
        if (symlinkResult.removed.length > 0) {
          spinner.succeed(`${platform.displayName}: Skills unlinked`);
        } else {
          spinner.info(`${platform.displayName}: No symlinks found`);
        }
      }
    }

    // Summary
    console.log('');
    console.log(chalk.green('✓ Skills sync complete!'));
    console.log('');

    if (!removeOnly && !isLocal && detectOS() === 'windows') {
      console.log(chalk.yellow('▸'), 'Windows: Ensure ~/bin is in your PATH');
      console.log('');
    }

  } finally {
    if (tempDir) {
      await import('fs-extra').then(({ remove }) => remove(tempDir));
    }
  }
}

export default skillsCommand;
