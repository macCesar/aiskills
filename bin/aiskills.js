#!/usr/bin/env node

/**
 * aiskills - AI Skills CLI Tool
 * Main entry point for the NPM package
 */

import { Command } from 'commander';
import { PACKAGE_VERSION } from '../lib/config.js';
import { skillsCommand } from '../lib/commands/skills.js';
import { listCommand } from '../lib/commands/list.js';
import { updateCommand } from '../lib/commands/update.js';
import { uninstallCommand } from '../lib/commands/uninstall.js';
import { autoUpdateCommand } from '../lib/commands/auto-update.js';

const program = new Command();

program
  .name('aiskills')
  .description('AI Skills CLI - Manage skills for AI coding assistants (Claude Code, Gemini CLI, Codex CLI)')
  .version(PACKAGE_VERSION);

// List command
program
  .command('list')
  .description('List available AI skills')
  .action(listCommand);

// Install command
program
  .command('install')
  .description('Install AI skills and link them to your AI coding assistants')
  .option('-l, --local', 'Install skills locally in the current project')
  .option('-a, --all', 'Install to all detected platforms without prompting')
  .option('--path <path>', 'Install to a custom path (skips symlink setup)')
  .action(skillsCommand);

// Update command
program
  .command('update')
  .description('Check for newer CLI versions, then sync installed skills')
  .option('-l, --local', 'Update local skills in the current project')
  .action(updateCommand);

// Remove command
program
  .command('remove')
  .description('Remove installed AI skills and symlinks')
  .option('-l, --local', 'Remove local skills from the current project')
  .action(uninstallCommand);

// Auto-update command (used by SessionStart hook)
program
  .command('auto-update')
  .description('Check for updates and sync skills (runs from SessionStart hook)')
  .option('-s, --silent', 'Run silently without output')
  .action(autoUpdateCommand);

// Parse arguments
program.parse();

export { program };
