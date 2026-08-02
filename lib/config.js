/**
 * Configuration constants for AI Skills
 * Single source of truth for version management
 */

import path from 'path';
import os from 'os';
import { readFileSync } from 'fs';

// Read package.json version dynamically
let packageVersion = '1.0.0';
try {
  const packagePath = new URL('../package.json', import.meta.url);
  const pkg = JSON.parse(readFileSync(packagePath, 'utf8'));
  packageVersion = pkg.version;
} catch {
  // Use default version if package.json not found
}

// Version management
export const PACKAGE_VERSION = packageVersion;

// Repository configuration
export const REPO_URL = 'https://github.com/macCesar/aiskills';
export const REPO_RAW_URL = 'https://raw.githubusercontent.com/macCesar/aiskills/main';
export const REPO_API_URL = 'https://api.github.com/repos/macCesar/aiskills';

// Skills to install
export const SKILLS = [
  'audit-codebase',
  'humaniza',
  'refactoring-ui',
  'session-log',
  'stitch-showcase',
  'vscode-extension-dev',
];

// Legacy skills to remove during updates/uninstall
export const LEGACY_SKILLS = [];

// Slash commands to install (Claude Code only — copied to ~/.claude/commands/)
export const COMMANDS = [
  'release',
];

// Legacy commands to remove during updates/uninstall
export const LEGACY_COMMANDS = [];

// Cache/config directory
export const getConfigDir = () => path.join(os.homedir(), '.aiskills');

// Directory paths
export const getAgentsSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.agents', 'skills');
export const getClaudeSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.claude', 'skills');
export const getClaudeCommandsDir = (baseDir = os.homedir()) => path.join(baseDir, '.claude', 'commands');
export const getGeminiSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.gemini', 'skills');
export const getCodexSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.codex', 'skills');

// Name of the Claude marketplace and plugin where this CLI publishes itself.
// Used to detect when a skill is already installed via the marketplace plugin
// and avoid creating a duplicate symlink in ~/.claude/skills/.
export const CLAUDE_PLUGIN_MARKETPLACE = 'maccesar-aiskills';
export const CLAUDE_PLUGIN_NAME = 'aiskills';
export const getClaudePluginSkillsPath = (baseDir = os.homedir()) =>
  path.join(baseDir, '.claude', 'plugins', 'cache', CLAUDE_PLUGIN_MARKETPLACE, CLAUDE_PLUGIN_NAME);

// The key Claude Code writes under "enabledPlugins" when the plugin is installed.
export const CLAUDE_PLUGIN_KEY = `${CLAUDE_PLUGIN_NAME}@${CLAUDE_PLUGIN_MARKETPLACE}`;

// Where Claude Code records which plugins are enabled. Both files are consulted
// because the local variant overrides the shared one, and either may carry the
// entry depending on how the plugin was installed.
export const getClaudeSettingsPaths = (baseDir = os.homedir()) => [
  path.join(baseDir, '.claude', 'settings.json'),
  path.join(baseDir, '.claude', 'settings.local.json'),
];

// AI platform detection
//
// Only platforms that need aiskills-managed symlinks appear here.
// Gemini CLI and Codex CLI auto-discover skills from the canonical
// ~/.agents/skills/ per the agentskills.io standard, so creating
// platform-specific symlinks at ~/.gemini/skills/ or ~/.codex/skills/
// would be redundant — and in Gemini's case actively harmful, since it
// reads both locations and reports "Skill conflict detected" warnings
// when the same skill exists in both.
export const getPlatforms = (baseDir = os.homedir()) => [
  {
    name: 'claude',
    displayName: 'Claude Code',
    skillsDir: getClaudeSkillsDir(baseDir),
    configDir: path.join(baseDir, '.claude'),
  },
];

// API configuration
export const GITHUB_API_HEADERS = {
  Accept: 'application/vnd.github.v3+json',
  'User-Agent': 'aiskills',
};

export default {
  PACKAGE_VERSION,
  REPO_URL,
  REPO_RAW_URL,
  REPO_API_URL,
  SKILLS,
  LEGACY_SKILLS,
  COMMANDS,
  LEGACY_COMMANDS,
  getConfigDir,
  getAgentsSkillsDir,
  getClaudeSkillsDir,
  getClaudeCommandsDir,
  getGeminiSkillsDir,
  getCodexSkillsDir,
  getPlatforms,
  GITHUB_API_HEADERS,
};
