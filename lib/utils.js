/**
 * Utility functions
 */

import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Read the description field from a skill's SKILL.md frontmatter.
 * @param {string} repoDir - Repository directory containing skills/
 * @param {string} skillName - Skill name (directory under skills/)
 * @returns {string} Description text, or empty string if not available.
 */
export function readSkillDescription(repoDir, skillName) {
  try {
    const skillPath = join(repoDir, 'skills', skillName, 'SKILL.md');
    const content = readFileSync(skillPath, 'utf8');
    const fmMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
    if (!fmMatch) return '';
    const descMatch = fmMatch[1].match(/^description:\s*["']?(.+?)["']?\s*$/m);
    return descMatch ? descMatch[1].trim() : '';
  } catch {
    return '';
  }
}

/**
 * Compress a skill description to a one-line summary suitable for an inline
 * checkbox preview. Picks the first segment of the description and trims it
 * to `maxLen` characters, appending an ellipsis when the source is longer.
 *
 * @param {string} description - The full SKILL.md description.
 * @param {number} maxLen - Maximum characters of the output (excluding ellipsis).
 * @returns {string} Trimmed one-liner, or empty string if input was empty.
 */
export function shortenSkillDescription(description, maxLen = 60) {
  if (!description) return '';
  let firstSegment = description.split(/\s*[—.:;]\s*/)[0].trim();
  firstSegment = firstSegment.replace(/\s+/g, ' ');
  if (firstSegment.length <= maxLen) return firstSegment;
  return firstSegment.slice(0, maxLen).trimEnd() + '…';
}

/**
 * Format a list of items for display
 * @param {Array} items - Array of strings
 * @returns {string} Comma-separated list
 */
export function formatList(items) {
  return items.join(', ');
}

/**
 * Parse version string to compare
 * @param {string} version - Version string (e.g., "1.0.0")
 * @returns {Array} Array of version parts
 */
export function parseVersion(version) {
  const matches = version.match(/\d+/g) || [];
  return matches.map((v) => parseInt(v, 10));
}

/**
 * Compare two version strings
 * @param {string} v1 - First version
 * @param {string} v2 - Second version
 * @returns {number} -1 if v1 < v2, 0 if equal, 1 if v1 > v2
 */
export function compareVersions(v1, v2) {
  const parts1 = parseVersion(v1);
  const parts2 = parseVersion(v2);

  for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
    const p1 = parts1[i] || 0;
    const p2 = parts2[i] || 0;

    if (p1 < p2) return -1;
    if (p1 > p2) return 1;
  }

  return 0;
}

export default {
  readSkillDescription,
  shortenSkillDescription,
  formatList,
  parseVersion,
  compareVersions,
};
