/**
 * File installation utilities
 * Installs skills to their respective directories
 */

import {
  existsSync,
  mkdirSync,
} from 'fs';
import { join } from 'path';
import { remove, copy } from 'fs-extra';
import os from 'os';
import {
  SKILLS,
  getAgentsSkillsDir,
} from './config.js';
import { removeSkills } from './cleanup.js';

/**
 * Recursively copy a directory
 * @param {string} src - Source directory
 * @param {string} dest - Destination directory
 * @returns {Promise<void>}
 */
export async function copyDirectory(src, dest) {
  if (!existsSync(dest)) {
    mkdirSync(dest, { recursive: true });
  }
  await copy(src, dest, { overwrite: true });
}

/**
 * Install a single skill to the agents skills directory
 * @param {string} repoDir - Repository directory
 * @param {string} skillName - Name of the skill
 * @param {string} baseDir - Base directory for installation
 * @returns {Promise<boolean>} True if installed successfully
 */
export async function installSkill(repoDir, skillName, baseDir = os.homedir()) {
  const skillsDir = getAgentsSkillsDir(baseDir);
  const skillSrc = join(repoDir, 'skills', skillName);
  const skillDest = join(skillsDir, skillName);

  if (!existsSync(skillsDir)) {
    mkdirSync(skillsDir, { recursive: true });
  }

  if (!existsSync(skillSrc)) {
    return false;
  }

  if (existsSync(skillDest)) {
    await remove(skillDest);
  }

  await copyDirectory(skillSrc, skillDest);
  return true;
}

/**
 * Install all skills to the agents skills directory
 * @param {string} repoDir - Repository directory
 * @param {string} baseDir - Base directory for installation
 * @returns {Promise<Object>} Results object with success/failure counts
 */
export async function installSkills(repoDir, baseDir = os.homedir()) {
  const results = {
    installed: [],
    failed: [],
    removed: [],
  };

  const legacyLocal = removeSkills(baseDir, { legacyOnly: true });
  results.removed.push(...legacyLocal.removed);
  results.failed.push(...legacyLocal.failed);

  if (baseDir && baseDir !== os.homedir()) {
    const legacyGlobal = removeSkills(undefined, { legacyOnly: true });
    results.removed.push(...legacyGlobal.removed);
    results.failed.push(...legacyGlobal.failed);
  }

  for (const skill of SKILLS) {
    if (await installSkill(repoDir, skill, baseDir)) {
      results.installed.push(skill);
    } else {
      results.failed.push(skill);
    }
  }

  return results;
}

/**
 * Get the local repository directory if running from source
 * @returns {string|null} Local repo directory or null
 */
export function getLocalRepoDir() {
  const scriptDir = new URL('..', import.meta.url).pathname;
  const skillsDir = join(scriptDir, 'skills');

  if (existsSync(skillsDir)) {
    return scriptDir;
  }

  return null;
}

export default {
  copyDirectory,
  installSkill,
  installSkills,
  getLocalRepoDir,
};
