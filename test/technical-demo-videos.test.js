import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { readFileSync, readdirSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SKILL = path.join(ROOT, 'skills', 'technical-demo-videos')

const read = (...segments) => readFileSync(path.join(SKILL, ...segments), 'utf8')

describe('technical-demo-videos is portable and complete', () => {
  test('ships every referenced helper', () => {
    assert.equal(readdirSync(path.join(SKILL, 'references')).filter((file) => file.endsWith('.md')).length, 9)
    assert.equal(readdirSync(path.join(SKILL, 'scripts')).filter((file) => file.endsWith('.py')).length, 4)
  })

  test('does not encode the workstation owner or PurgeTSS series', () => {
    const files = [
      read('SKILL.md'),
      ...readdirSync(path.join(SKILL, 'references')).map((file) => read('references', file)),
      ...readdirSync(path.join(SKILL, 'scripts')).map((file) => read('scripts', file)),
    ]
    const bundled = files.join('\n')

    assert.doesNotMatch(bundled, /\/Users\/cesar|\/Users\/PurgeTSS/)
    assert.doesNotMatch(bundled, /classic-video-series|For this PurgeTSS series/)
  })

  test('runtime accepts a configurable copies root and display', () => {
    const runtime = read('scripts', 'recording_runtime.py')
    assert.match(runtime, /TECHNICAL_DEMO_COPIES_ROOT/)
    assert.match(runtime, /copies_root=None, display_number=1/)
    assert.match(runtime, /f'-D\{self\.display_number\}'/)
  })

  test('Python helpers parse and command-line helpers expose help', () => {
    const scripts = path.join(SKILL, 'scripts')
    const pythonFiles = readdirSync(scripts)
      .filter((file) => file.endsWith('.py'))
      .map((file) => path.join(scripts, file))

    for (const file of pythonFiles) {
      execFileSync('python3', ['-c', 'import ast, pathlib, sys; ast.parse(pathlib.Path(sys.argv[1]).read_text())', file])
    }

    for (const file of ['events_to_cues.py', 'normalize_youtube_master.py', 'youtube_publish.py']) {
      const output = execFileSync('python3', [path.join(scripts, file), '--help'], { encoding: 'utf8' })
      assert.match(output, /usage:/)
    }
  })

  test('runtime applies copies-root and display configuration', () => {
    const runtime = path.join(SKILL, 'scripts', 'recording_runtime.py')
    const probe = [
      'from importlib.util import module_from_spec, spec_from_file_location',
      'from pathlib import Path',
      'import sys',
      "spec = spec_from_file_location('recording_runtime', sys.argv[1])",
      'module = module_from_spec(spec)',
      'spec.loader.exec_module(module)',
      "item = module.MacVsCodeRecording('.', '/tmp/example.mov', '/tmp/example.json', 'example', copies_root='/tmp/demo-copies', display_number=2)",
      "assert item.copies_root == Path('/tmp/demo-copies').resolve()",
      'assert item.display_number == 2',
    ].join('; ')

    execFileSync('python3', ['-c', probe, runtime])
  })

  test('requires approval before recording and external publication', () => {
    const skill = read('SKILL.md')
    assert.match(skill, /Present the recording plan for approval/)
    assert.match(skill, /approval to begin recording/)
    assert.match(skill, /requires explicit authorization/)
  })
})
