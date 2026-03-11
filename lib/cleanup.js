/**
 * Cleanup helpers for skills and symlinks
 */

import {
  SKILLS,
  LEGACY_SKILLS,
  getAgentsSkillsDir,
} from './config.js';
import { detectPlatforms } from './platform.js';
import { existsSync, lstatSync, rmSync } from 'fs';
import { join } from 'path';

export function getSkillList({ includeLegacy = true, legacyOnly = false } = {}) {
  if (legacyOnly) return [...LEGACY_SKILLS];
  return includeLegacy ? [...SKILLS, ...LEGACY_SKILLS] : [...SKILLS];
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

export function cleanupLegacyArtifacts(baseDir) {
  removeSkills(baseDir, { legacyOnly: true });

  const platforms = detectPlatforms(baseDir);
  for (const platform of platforms) {
    removeLegacySkillSymlinks(platform.skillsDir);
  }

  if (baseDir) {
    removeSkills(undefined, { legacyOnly: true });
    const globalPlatforms = detectPlatforms();
    for (const platform of globalPlatforms) {
      removeLegacySkillSymlinks(platform.skillsDir);
    }
  }
}

export default {
  getSkillList,
  removeSkillSymlinks,
  removeLegacySkillSymlinks,
  removeSkills,
  cleanupLegacyArtifacts,
};
