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
  'humaniza',
  'refactoring-ui',
  'stitch-showcase',
  'vscode-extension-dev',
];

// Legacy skills to remove during updates/uninstall
export const LEGACY_SKILLS = [];

// Directory paths
export const getAgentsSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.agents', 'skills');
export const getClaudeSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.claude', 'skills');
export const getGeminiSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.gemini', 'skills');
export const getCodexSkillsDir = (baseDir = os.homedir()) => path.join(baseDir, '.codex', 'skills');

// AI platform detection
export const getPlatforms = (baseDir = os.homedir()) => [
  {
    name: 'claude',
    displayName: 'Claude Code',
    skillsDir: getClaudeSkillsDir(baseDir),
    configDir: path.join(baseDir, '.claude'),
  },
  {
    name: 'gemini',
    displayName: 'Gemini CLI',
    skillsDir: getGeminiSkillsDir(baseDir),
    configDir: path.join(baseDir, '.gemini'),
  },
  {
    name: 'codex',
    displayName: 'Codex CLI',
    skillsDir: getCodexSkillsDir(baseDir),
    configDir: path.join(baseDir, '.codex'),
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
  getAgentsSkillsDir,
  getClaudeSkillsDir,
  getGeminiSkillsDir,
  getCodexSkillsDir,
  getPlatforms,
  GITHUB_API_HEADERS,
};
