import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SKILL = path.join(ROOT, 'skills', 'technical-demo-videos')

const read = (...segments) => readFileSync(path.join(SKILL, ...segments), 'utf8')

describe('technical-demo-videos is portable and complete', () => {
  test('ships every referenced helper', () => {
    const skill = read('SKILL.md')
    const references = readdirSync(path.join(SKILL, 'references'))
      .filter((file) => file.endsWith('.md'))
    const scripts = readdirSync(path.join(SKILL, 'scripts'))
      .filter((file) => file.endsWith('.py'))
    const routedInstructions = [
      skill,
      ...references.map((file) => read('references', file)),
    ].join('\n')

    assert.equal(references.length, 9)
    assert.equal(scripts.length, 4)
    for (const file of references) {
      assert.match(skill, new RegExp(file.replaceAll('.', '\\.')))
    }
    for (const file of scripts) {
      assert.match(routedInstructions, new RegExp(file.replaceAll('.', '\\.')))
    }
  })

  test('does not encode the workstation owner or PurgeTSS series', () => {
    const files = [
      read('SKILL.md'),
      ...readdirSync(path.join(SKILL, 'references'))
        .filter((file) => file.endsWith('.md'))
        .map((file) => read('references', file)),
      ...readdirSync(path.join(SKILL, 'scripts'))
        .filter((file) => file.endsWith('.py'))
        .map((file) => read('scripts', file)),
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

  test('normalizer selects YouTube bitrate by resolution and frame-rate class', () => {
    const normalizer = path.join(SKILL, 'scripts', 'normalize_youtube_master.py')
    const probe = [
      'from importlib.util import module_from_spec, spec_from_file_location',
      'import sys',
      "spec = spec_from_file_location('normalize_youtube_master', sys.argv[1])",
      'module = module_from_spec(spec)',
      'spec.loader.exec_module(module)',
      "assert module.default_bitrate(2160, 30) == ('35M', 35_000_000)",
      "assert module.default_bitrate(2160, 60) == ('53M', 53_000_000)",
      "assert module.default_bitrate(1080, 60) == ('12M', 12_000_000)",
    ].join('; ')

    execFileSync('python3', ['-c', probe, normalizer])
  })

  test('Codex metadata names the skill in its default prompt', () => {
    const metadata = read('agents', 'openai.yaml')
    assert.match(metadata, /default_prompt:.*\$technical-demo-videos/)
  })

  test('public plugin catalogs describe technical video production', () => {
    const plugin = readFileSync(path.join(ROOT, '.claude-plugin', 'plugin.json'), 'utf8')
    const marketplace = readFileSync(path.join(ROOT, '.claude-plugin', 'marketplace.json'), 'utf8')

    assert.match(plugin, /technical video production/)
    assert.match(marketplace, /technical video production/)
  })

  test('events helper builds cues only inside a completed capture', () => {
    const work = mkdtempSync(path.join(os.tmpdir(), 'technical-demo-cues-'))
    const input = path.join(work, 'events.json')
    const output = path.join(work, 'cues.json')
    writeFileSync(input, JSON.stringify({
      events: [
        { name: 'preflight', timestamp_ms: 500 },
        { name: 'recording_started', timestamp_ms: 1000 },
        { name: 'command_submitted', timestamp_ms: 1250 },
        { name: 'recording_stopped', timestamp_ms: 2500 },
        { name: 'cleanup', timestamp_ms: 3000 },
      ],
    }))

    try {
      execFileSync('python3', [
        path.join(SKILL, 'scripts', 'events_to_cues.py'),
        input,
        output,
      ])
      const cues = JSON.parse(readFileSync(output, 'utf8'))
      assert.deepEqual(cues.events.map((event) => event.event), [
        'recording_started',
        'command_submitted',
        'recording_stopped',
      ])
      assert.deepEqual(cues.cues, [{
        id: 1,
        event: 'command_submitted',
        start: 0.25,
        end: 1.5,
        text: '',
      }])
    } finally {
      rmSync(work, { recursive: true, force: true })
    }
  })

  test('YouTube publisher dry-run reports caption replacement without authenticating', () => {
    const work = mkdtempSync(path.join(os.tmpdir(), 'technical-demo-youtube-'))
    const manifest = path.join(work, 'episode-youtube-upload.json')
    const videoFixture = 'video fixture'
    writeFileSync(path.join(work, 'episode-final.mp4'), videoFixture)
    writeFileSync(path.join(work, 'episode.srt'), 'caption fixture')
    writeFileSync(manifest, JSON.stringify({
      schemaVersion: 1,
      videoFile: 'episode-final.mp4',
      captionsFile: 'episode.srt',
      thumbnailFile: null,
      title: 'Demo',
      description: 'Demo description',
      categoryId: '28',
      expectedChannelId: 'UCexpected',
      privacyStatus: 'private',
      publishAt: null,
      playlistId: null,
      caption: {
        language: 'en',
        name: 'English',
        isDraft: false,
      },
    }))

    try {
      const publisher = path.join(SKILL, 'scripts', 'youtube_publish.py')
      const initial = JSON.parse(execFileSync('python3', [
        publisher,
        manifest,
      ], { encoding: 'utf8' }))
      assert.deepEqual(
        initial.operations.map((operation) => operation.operation),
        ['videos.insert', 'captions.insert'],
      )
      assert.match(initial.confirmationToken, /^[a-f0-9]{64}$/)
      assert.equal(initial.target.expectedChannelId, 'UCexpected')
      assert.equal(initial.target.playlistId, null)
      const unconfirmed = spawnSync('python3', [
        publisher,
        manifest,
        '--execute',
      ], { encoding: 'utf8' })
      assert.equal(unconfirmed.status, 1)
      assert.match(unconfirmed.stderr, /requires --confirm-plan/)

      writeFileSync(
        path.join(work, 'episode-youtube-upload-receipt.json'),
        JSON.stringify({
          videoId: 'existing-video',
          videoSha256: createHash('sha256').update(videoFixture).digest('hex'),
          captionsUploaded: true,
          captionId: 'existing-caption',
        }),
      )
      const stdout = execFileSync('python3', [
        publisher,
        manifest,
        '--replace-captions',
      ], { encoding: 'utf8' })
      const plan = JSON.parse(stdout)
      assert.equal(plan.mode, 'dry-run')
      assert.deepEqual(
        plan.operations.map((operation) => operation.operation),
        ['captions.update'],
      )
    } finally {
      rmSync(work, { recursive: true, force: true })
    }
  })

  test('YouTube manifest requires explicit channel and publishing choices', () => {
    const work = mkdtempSync(path.join(os.tmpdir(), 'technical-demo-target-'))
    const manifest = path.join(work, 'episode-youtube-upload.json')
    writeFileSync(path.join(work, 'episode-final.mp4'), 'video fixture')
    writeFileSync(manifest, JSON.stringify({
      schemaVersion: 1,
      videoFile: 'episode-final.mp4',
      title: 'Demo',
      description: 'Demo description',
      categoryId: '28',
    }))

    try {
      const run = spawnSync('python3', [
        path.join(SKILL, 'scripts', 'youtube_publish.py'),
        manifest,
      ], { encoding: 'utf8' })
      assert.equal(run.status, 1)
      assert.match(run.stderr, /manifest requires explicit expectedChannelId/)
    } finally {
      rmSync(work, { recursive: true, force: true })
    }
  })

  test('YouTube channel guard rejects a token for another channel', () => {
    const publisher = path.join(SKILL, 'scripts', 'youtube_publish.py')
    const probe = [
      'from importlib.util import module_from_spec, spec_from_file_location',
      'import sys',
      "spec = spec_from_file_location('youtube_publish', sys.argv[1])",
      'module = module_from_spec(spec)',
      'spec.loader.exec_module(module)',
      'class Request:',
      "  def execute(self): return {'items': [{'id': 'UCactual', 'snippet': {'title': 'Actual channel'}}]}",
      'class Channels:',
      '  def list(self, **kwargs): return Request()',
      'class YouTube:',
      '  def channels(self): return Channels()',
      "assert module.verify_expected_channel(YouTube(), 'UCactual')['id'] == 'UCactual'",
      'try:',
      "  module.verify_expected_channel(YouTube(), 'UCexpected')",
      'except RuntimeError as error:',
      "  assert 'authenticated channel mismatch' in str(error)",
      'else:',
      "  raise AssertionError('channel mismatch was accepted')",
    ].join('\n')

    execFileSync('python3', ['-c', probe, publisher])
  })

  test('YouTube playlist guard rejects a playlist from another channel', () => {
    const publisher = path.join(SKILL, 'scripts', 'youtube_publish.py')
    const probe = [
      'from importlib.util import module_from_spec, spec_from_file_location',
      'import sys',
      "spec = spec_from_file_location('youtube_publish', sys.argv[1])",
      'module = module_from_spec(spec)',
      'spec.loader.exec_module(module)',
      'class Request:',
      "  def execute(self): return {'items': [{'id': 'PLdemo', 'snippet': {'title': 'Demos', 'channelId': 'UCactual'}}]}",
      'class Playlists:',
      '  def list(self, **kwargs): return Request()',
      'class YouTube:',
      '  def playlists(self): return Playlists()',
      "assert module.verify_playlist(YouTube(), 'PLdemo', 'UCactual')['id'] == 'PLdemo'",
      'try:',
      "  module.verify_playlist(YouTube(), 'PLdemo', 'UCexpected')",
      'except RuntimeError as error:',
      "  assert 'playlist channel mismatch' in str(error)",
      'else:',
      "  raise AssertionError('playlist mismatch was accepted')",
    ].join('\n')

    execFileSync('python3', ['-c', probe, publisher])
  })

  test('requires approval before recording and external publication', () => {
    const skill = read('SKILL.md')
    assert.match(skill, /Present the recording plan for approval/)
    assert.match(skill, /approval to begin recording/)
    assert.match(skill, /wait for explicit authorization/)
  })
})
