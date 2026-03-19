/**
 * List command
 * Shows available skills with their descriptions
 */

import chalk from 'chalk';
import { SKILLS } from '../config.js';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

function parseSkillDescription(skillName) {
  try {
    const skillPath = join(__dirname, '..', '..', 'skills', skillName, 'SKILL.md');
    const content = readFileSync(skillPath, 'utf8');
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (!match) return null;

    const frontmatter = match[1];

    // Extract name
    const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
    const name = nameMatch ? nameMatch[1].trim() : skillName;

    // Extract description (handles multi-line YAML >)
    let description = '';
    const descMatch = frontmatter.match(/description:\s*>\s*\n([\s\S]*?)(?=\n\w+:|$)/);
    if (descMatch) {
      description = descMatch[1]
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean)
        .join(' ');
    } else {
      const singleMatch = frontmatter.match(/^description:\s*(.+)$/m);
      if (singleMatch) {
        description = singleMatch[1].trim();
      }
    }

    // Trim long descriptions
    const maxLen = 80;
    if (description.length > maxLen) {
      description = description.substring(0, maxLen - 1).trimEnd() + '…';
    }

    return { name, description };
  } catch {
    return null;
  }
}

/**
 * List command handler
 */
export async function listCommand() {
  console.log('');
  console.log(chalk.bold.blue('Available Skills'));
  console.log('');

  const maxNameLen = Math.max(...SKILLS.map(s => s.length));

  for (const skill of SKILLS) {
    const info = parseSkillDescription(skill);
    const name = chalk.cyan(skill.padEnd(maxNameLen));
    const desc = info?.description ? chalk.gray(info.description) : chalk.gray('(no description)');
    console.log(`  ${name}  ${desc}`);
  }

  console.log('');
  console.log(chalk.gray(`${SKILLS.length} skill${SKILLS.length !== 1 ? 's' : ''} available`));
  console.log('');
}

export default listCommand;
