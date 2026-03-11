/**
 * GitHub download utilities
 * Fetches releases and archives from GitHub
 */

import { createWriteStream, existsSync, mkdirSync } from 'fs';
import { tmpdir } from 'os';
import { join, dirname } from 'path';
import { pipeline } from 'stream/promises';
import { unlink } from 'fs/promises';
import { extract } from 'tar';
import { REPO_API_URL, REPO_RAW_URL, GITHUB_API_HEADERS } from './config.js';

/**
 * Download a file from URL to local path
 * @param {string} url - URL to download
 * @param {string} destPath - Destination path
 * @returns {Promise<void>}
 */
export async function downloadFile(url, destPath) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to download: ${response.statusText}`);
  }

  const dir = dirname(destPath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }

  await pipeline(response.body, createWriteStream(destPath));
}

/**
 * Download and extract GitHub repository archive
 * @param {string} destDir - Destination directory
 * @param {string} ref - Git ref (branch, tag, commit)
 * @returns {Promise<string>} Path to extracted directory
 */
export async function downloadRepoArchive(destDir, ref = 'main') {
  const archiveUrl = `${REPO_API_URL}/tarball/${ref}`;
  const tempFile = join(tmpdir(), `aiskills-${Date.now()}.tar.gz`);

  try {
    await downloadFile(archiveUrl, tempFile);

    await extract({
      file: tempFile,
      cwd: destDir,
      strip: 1,
    });

    return destDir;
  } finally {
    if (existsSync(tempFile)) {
      await unlink(tempFile);
    }
  }
}

/**
 * Fetch latest version from npm registry
 * @returns {Promise<string>} Latest version number
 */
export async function fetchLatestNpmVersion() {
  const response = await fetch('https://registry.npmjs.org/aiskills');

  if (!response.ok) {
    throw new Error(`Failed to fetch npm info: ${response.statusText}`);
  }

  const data = await response.json();
  return data['dist-tags'].latest;
}

/**
 * Check if an update is available (checks npm)
 * @param {string} currentVersion - Current version
 * @returns {Promise<boolean>} True if update available
 */
export async function checkForUpdate(currentVersion) {
  try {
    const latestVersion = await fetchLatestNpmVersion();
    const latest = latestVersion.replace(/^v/, '');
    const current = currentVersion.replace(/^v/, '');

    const latestParts = latest.split('.').map((v) => parseInt(v, 10));
    const currentParts = current.split('.').map((v) => parseInt(v, 10));

    for (let i = 0; i < Math.max(latestParts.length, currentParts.length); i++) {
      const l = latestParts[i] || 0;
      const c = currentParts[i] || 0;

      if (l > c) return true;
      if (l < c) return false;
    }

    return false;
  } catch {
    return false;
  }
}

export default {
  downloadFile,
  downloadRepoArchive,
  fetchLatestNpmVersion,
  checkForUpdate,
};
