/**
 * Cleanup helpers for skills, commands, and symlinks
 */

import {
  SKILLS,
  LEGACY_SKILLS,
  COMMANDS,
  LEGACY_COMMANDS,
  getAgentsSkillsDir,
  getClaudeCommandsDir,
} from './config.js';
import { detectPlatforms } from './platform.js';
import { existsSync, lstatSync, rmSync } from 'fs';
import { join } from 'path';

export function getSkillList({ includeLegacy = true, legacyOnly = false } = {}) {
  if (legacyOnly) return [...LEGACY_SKILLS];
  return includeLegacy ? [...SKILLS, ...LEGACY_SKILLS] : [...SKILLS];
}

export function getCommandList({ includeLegacy = true, legacyOnly = false } = {}) {
  if (legacyOnly) return [...LEGACY_COMMANDS];
  return includeLegacy ? [...COMMANDS, ...LEGACY_COMMANDS] : [...COMMANDS];
}

function removeEntriesAtDir(dir, names, { suffix = '', recursive = true } = {}) {
  const results = { removed: [], failed: [] };
  if (!dir || !existsSync(dir)) return results;

  for (const name of names) {
    const target = join(dir, suffix ? `${name}${suffix}` : name);
    try {
      lstatSync(target);
      rmSync(target, { recursive, force: true });
      results.removed.push(name);
    } catch (error) {
      if (error.code && error.code !== 'ENOENT') {
        results.failed.push(name);
      }
    }
  }

  return results;
}

export function removeSkillSymlinks(platformSkillsDir, options = {}) {
  const skillList = getSkillList(options);
  return removeEntriesAtDir(platformSkillsDir, skillList, { recursive: true });
}

export function removeLegacySkillSymlinks(platformSkillsDir) {
  return removeSkillSymlinks(platformSkillsDir, { legacyOnly: true });
}

export function removeSkills(baseDir, options = {}) {
  const skillsDir = getAgentsSkillsDir(baseDir);
  const skillList = getSkillList(options);
  return removeEntriesAtDir(skillsDir, skillList, { recursive: true });
}

export function removeCommands(baseDir, options = {}) {
  const commandsDir = getClaudeCommandsDir(baseDir);
  const commandList = getCommandList(options);
  return removeEntriesAtDir(commandsDir, commandList, { suffix: '.md', recursive: false });
}

export function cleanupLegacyArtifacts(baseDir) {
  removeSkills(baseDir, { legacyOnly: true });
  removeCommands(baseDir, { legacyOnly: true });

  const platforms = detectPlatforms(baseDir);
  for (const platform of platforms) {
    removeLegacySkillSymlinks(platform.skillsDir);
  }

  if (baseDir) {
    removeSkills(undefined, { legacyOnly: true });
    removeCommands(undefined, { legacyOnly: true });
    const globalPlatforms = detectPlatforms();
    for (const platform of globalPlatforms) {
      removeLegacySkillSymlinks(platform.skillsDir);
    }
  }
}

export default {
  getSkillList,
  getCommandList,
  removeSkillSymlinks,
  removeLegacySkillSymlinks,
  removeSkills,
  removeCommands,
  cleanupLegacyArtifacts,
};
