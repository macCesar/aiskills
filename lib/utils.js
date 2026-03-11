/**
 * Utility functions
 */

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
  formatList,
  parseVersion,
  compareVersions,
};
