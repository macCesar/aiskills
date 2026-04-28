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

function getTestLatestNpmVersion() {
  const value = process.env.AISKILLS_TEST_NPM_LATEST_VERSION;
  return value && value.trim() ? value.trim() : null;
}

/**
 * Fetch latest release info from GitHub API
 * @returns {Promise<Object>} Release information
 */
export async function fetchLatestRelease() {
  const response = await fetch(
    `${REPO_API_URL}/releases/latest`,
    {
      headers: GITHUB_API_HEADERS,
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch release info: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch latest version from GitHub
 * @returns {Promise<string>} Latest version tag
 */
export async function fetchLatestVersion() {
  const release = await fetchLatestRelease();
  return release.tag_name;
}

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
 * Download a single file from GitHub raw content
 * @param {string} filePath - Path in repository
 * @param {string} destPath - Local destination path
 * @param {string} ref - Git ref (branch, tag, commit)
 * @returns {Promise<void>}
 */
export async function downloadRawFile(filePath, destPath, ref = 'main') {
  const url = `${REPO_RAW_URL}/${ref}/${filePath}`;

  const dir = dirname(destPath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }

  await downloadFile(url, destPath);
}

/**
 * Fetch latest version from npm registry
 * @returns {Promise<string>} Latest version number
 */
export async function fetchLatestNpmVersion() {
  const testVersion = getTestLatestNpmVersion();
  if (testVersion) {
    return testVersion;
  }

  const response = await fetch('https://registry.npmjs.org/@maccesar/aiskills');

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
  fetchLatestRelease,
  fetchLatestVersion,
  downloadFile,
  downloadRepoArchive,
  downloadRawFile,
  fetchLatestNpmVersion,
  checkForUpdate,
};
