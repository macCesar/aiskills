/**
 * Uninstall command
 * Removes installed skills and symlinks
 */

import chalk from 'chalk';
import ora from 'ora';
import { SKILLS } from '../config.js';
import {
  detectPlatforms,
} from '../platform.js';
import {
  removeSkillSymlinks,
  removeSkills,
} from '../cleanup.js';
import checkbox, { Separator } from '../prompts/checkboxCancel.js';
import { existsSync } from 'fs';
import { join, resolve } from 'path';
import { getAgentsSkillsDir } from '../config.js';
import { getSkillList } from '../cleanup.js';

/**
 * Uninstall command handler
 */
export async function uninstallCommand(options) {
  console.log('');
  console.log(chalk.bold.blue('AI Skills Uninstaller'));
  console.log('');

  const projectDir = resolve(process.cwd());
  const baseDir = options.local ? projectDir : undefined;
  if (options.local) {
    console.log(chalk.cyan('Mode: Local uninstallation (current project)'));
    console.log('');
  }

  const detectedPlatforms = detectPlatforms(baseDir);

  const skillList = getSkillList();
  const homeSkillsDir = getAgentsSkillsDir();
  const projectSkillsDir = getAgentsSkillsDir(projectDir);

  const hasAnyInDir = (dir, names) =>
    !!dir && existsSync(dir) && names.some((name) => existsSync(join(dir, name)));

  const hasHomeSkills = hasAnyInDir(homeSkillsDir, skillList);
  const hasProjectSkills = options.local && hasAnyInDir(projectSkillsDir, skillList);

  const hasHomeSymlinks = detectedPlatforms.some((platform) =>
    hasAnyInDir(platform.skillsDir, skillList)
  );
  const hasProjectSymlinks = options.local && detectPlatforms(projectDir).some((platform) =>
    hasAnyInDir(platform.skillsDir, skillList)
  );

  const choices = [];
  if (hasHomeSkills) {
    choices.push({ name: 'Skills from the `home` directory', value: 'skills-home', checked: false });
  }
  if (hasProjectSkills) {
    choices.push({ name: 'Skills from the `project` directory', value: 'skills-project', checked: false });
  }
  if (hasHomeSymlinks) {
    choices.push({ name: 'Skill symlinks from `home` directory', value: 'symlinks-home', checked: true });
  }
  if (hasProjectSymlinks) {
    choices.push({ name: 'Skill symlinks from `project` directory', value: 'symlinks-project', checked: false });
  }

  if (choices.length === 0) {
    console.log(chalk.yellow('No skills or symlinks found.'));
    console.log('');
    return;
  }

  let targets = [];
  try {
    targets = await checkbox({
      message: 'What do you want to uninstall:',
      choices: [
        ...choices,
        new Separator(' '),
      ],
      shortcuts: { invert: null },
      theme: {
        style: {
          renderSelectedChoices: () => '',
        },
      },
    });
  } catch (error) {
    console.log('\nCancelled.');
    process.exit(0);
  }

  if (targets.includes('cancel')) {
    console.log('Cancelled.');
    return;
  }

  if (targets.length === 0) {
    console.log(chalk.yellow('Nothing to uninstall. Cancelled.'));
    return;
  }

  const spinner = ora();
  let actionTaken = false;

  if (targets.includes('symlinks-home')) {
    for (const platform of detectedPlatforms) {
      spinner.start(`Removing ${platform.displayName} symlinks...`);
      const symlinkResult = removeSkillSymlinks(platform.skillsDir);
      if (symlinkResult.removed.length > 0) {
        spinner.succeed(`${platform.displayName}: Skills unlinked`);
        actionTaken = true;
      } else {
        spinner.info(`${platform.displayName}: No symlinks found`);
      }
    }
  }

  if (targets.includes('symlinks-project')) {
    const projectPlatforms = detectPlatforms(projectDir);
    for (const platform of projectPlatforms) {
      spinner.start(`Removing ${platform.displayName} symlinks...`);
      const symlinkResult = removeSkillSymlinks(platform.skillsDir);
      if (symlinkResult.removed.length > 0) {
        spinner.succeed(`${platform.displayName}: Skills unlinked`);
        actionTaken = true;
      } else {
        spinner.info(`${platform.displayName}: No symlinks found`);
      }
    }
  }

  if (targets.includes('skills-home')) {
    spinner.start('Removing skills...');
    const skillsResult = removeSkills(undefined);
    if (skillsResult.removed.length > 0) {
      spinner.succeed(`${SKILLS.length} skills removed`);
      actionTaken = true;
    } else {
      spinner.info('No skills to remove');
    }
  }

  if (targets.includes('skills-project')) {
    spinner.start('Removing skills...');
    const skillsResult = removeSkills(projectDir);
    if (skillsResult.removed.length > 0) {
      spinner.succeed(`${SKILLS.length} skills removed`);
      actionTaken = true;
    } else {
      spinner.info('No skills to remove');
    }
  }

  if (actionTaken) {
    console.log('');
    console.log(chalk.green('✓ Uninstallation complete!'));
    console.log('');
  } else {
    console.log('');
    console.log(chalk.yellow('No changes were necessary.'));
    console.log('');
  }
}

export default uninstallCommand;
