#!/usr/bin/env python3
"""Reusable primitives copied into an approved technical-video package."""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from statistics import median


DEFAULT_VSCODE_PROFILE = {
  'logical_display': (1920, 1080),
  'minimum_window_size': (1850, 1000),
  'auxiliary_panel_key_code': 19,
  'terminal_open_delay': 1.5,
  'terminal_drag_x': 645,
  'terminal_target_y': 720,
  'terminal_search_y': (90, 950)
}

SWIFT_DRAG_SOURCE = r'''
import CoreGraphics
import Foundation

guard CommandLine.arguments.count == 5,
      let startX = Double(CommandLine.arguments[1]),
      let startY = Double(CommandLine.arguments[2]),
      let endX = Double(CommandLine.arguments[3]),
      let endY = Double(CommandLine.arguments[4]) else {
  exit(2)
}

let start = CGPoint(x: startX, y: startY)
let end = CGPoint(x: endX, y: endY)
CGEvent(mouseEventSource: nil, mouseType: .mouseMoved,
        mouseCursorPosition: start, mouseButton: .left)?.post(tap: .cghidEventTap)
usleep(100_000)
CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown,
        mouseCursorPosition: start, mouseButton: .left)?.post(tap: .cghidEventTap)
for step in 1...20 {
  let progress = Double(step) / 20.0
  let point = CGPoint(
    x: startX + ((endX - startX) * progress),
    y: startY + ((endY - startY) * progress)
  )
  CGEvent(mouseEventSource: nil, mouseType: .leftMouseDragged,
          mouseCursorPosition: point, mouseButton: .left)?.post(tap: .cghidEventTap)
  usleep(15_000)
}
CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp,
        mouseCursorPosition: end, mouseButton: .left)?.post(tap: .cghidEventTap)
'''


class MacVsCodeRecording:
  def __init__(
    self, source_project, output_video, output_events, slug,
    copies_root=None, display_number=1
  ):
    self.source_project = Path(source_project).resolve()
    self.output_video = Path(output_video).resolve()
    self.output_events = Path(output_events).resolve()
    self.slug = slug
    configured_root = copies_root or os.environ.get('TECHNICAL_DEMO_COPIES_ROOT')
    self.copies_root = Path(configured_root).expanduser().resolve() if configured_root else Path.home() / 'TechnicalDemos'
    self.display_number = int(display_number)
    self.temp_root = None
    self.project = None
    self.window_slug = None
    self.capture = None
    self.drag_helper = None
    self.events = []

  @staticmethod
  def _apple_string(value):
    return str(value).replace('\\', '\\\\').replace('"', '\\"')

  def preflight(self, required_files=(), forbidden_files=()):
    for tool in (
      'code', 'magick', 'osascript', 'screencapture', 'swift', 'swiftc'
    ):
      if shutil.which(tool) is None:
        raise RuntimeError(f'missing required tool: {tool}')
    if not self.source_project.is_dir():
      raise RuntimeError(f'project not found: {self.source_project}')
    missing = [path for path in required_files if not (self.source_project / path).exists()]
    if missing:
      raise RuntimeError('missing project files: ' + ', '.join(missing))
    present = [path for path in forbidden_files if (self.source_project / path).exists()]
    if present:
      raise RuntimeError('source already contains generated files: ' + ', '.join(present))
    for artifact in (self.output_video, self.output_events):
      if artifact.exists():
        raise RuntimeError(f'refusing to overwrite: {artifact}')

  @staticmethod
  def logical_display_size():
    source = (
      'import AppKit; '
      'let f = NSScreen.main!.frame; '
      'print(Int(f.width), Int(f.height))'
    )
    result = subprocess.run(
      ['swift', '-e', source], check=True, capture_output=True, text=True
    )
    width, height = result.stdout.strip().split()
    return int(width), int(height)

  def create_copy(self):
    copies_root = self.copies_root
    copies_root.mkdir(parents=True, exist_ok=True)
    if not copies_root.is_dir():
      raise RuntimeError(f'recording copies folder not found: {copies_root}')
    self.temp_root = Path(tempfile.mkdtemp(prefix=f'{self.slug}-recording.'))
    self.project = Path(tempfile.mkdtemp(prefix=f'{self.slug}.', dir=copies_root))
    self.window_slug = self.project.name
    shutil.copytree(self.source_project, self.project, dirs_exist_ok=True)
    self.drag_helper = self.temp_root / 'drag'
    subprocess.run(
      ['swiftc', '-o', str(self.drag_helper), '-'],
      input=SWIFT_DRAG_SOURCE, check=True, capture_output=True, text=True
    )
    return self.project

  def open_vscode(self):
    subprocess.run(['code', '-n', str(self.project)], check=True)

  def targeted(self, body, capture_output=False):
    slug = self._apple_string(self.window_slug)
    script = f'''
set slug to "{slug}"
tell application "System Events"
  tell process "Code"
    set targetWindow to missing value
    repeat with candidateWindow in windows
      if name of candidateWindow contains slug then
        set targetWindow to candidateWindow
        exit repeat
      end if
    end repeat
    if targetWindow is missing value then error "Target window not found: " & slug
    perform action "AXRaise" of targetWindow
    set frontmost to true
    delay 0.15
    if name of front window does not contain slug then error "Wrong front window"
    {body}
  end tell
end tell
'''
    result = subprocess.run(
      ['osascript', '-e', script], check=True,
      capture_output=capture_output, text=True
    )
    return result.stdout.strip() if capture_output else ''

  def wait_for_window(self, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
      try:
        self.targeted('return name of front window', True)
        return
      except subprocess.CalledProcessError:
        time.sleep(0.4)
    raise RuntimeError('VS Code window did not appear')

  def assert_window_size(self, minimum_size):
    raw_size = self.targeted(
      'set s to size of front window\n'
      'return (item 1 of s as text) & "," & (item 2 of s as text)',
      True
    )
    width, height = [int(value) for value in raw_size.split(',')]
    if width < minimum_size[0] or height < minimum_size[1]:
      raise RuntimeError(
        f'VS Code window is {width}x{height}; minimum is '
        f'{minimum_size[0]}x{minimum_size[1]}'
      )

  def window_geometry(self):
    raw_geometry = self.targeted(
      'set p to position of front window\n'
      'set s to size of front window\n'
      'return (item 1 of p as text) & "," & '
      '(item 2 of p as text) & "," & '
      '(item 1 of s as text) & "," & (item 2 of s as text)',
      True
    )
    return tuple(int(value) for value in raw_geometry.split(','))

  def open_terminal(self):
    self.targeted(
      'click menu item "New Terminal" of menu 1 of '
      'menu bar item "Terminal" of menu bar 1'
    )

  def drag(self, start, end):
    self.targeted('return name of front window', True)
    subprocess.run([
      str(self.drag_helper), str(start[0]), str(start[1]),
      str(end[0]), str(end[1])
    ], check=True)

  @staticmethod
  def _column_pixels(image_path, x, height):
    result = subprocess.run([
      'magick', str(image_path), '-crop', f'1x{height}+{x}+0',
      '-depth', '8', 'txt:-'
    ], check=True, capture_output=True, text=True)
    pattern = re.compile(r'^0,(\d+): \((\d+),(\d+),(\d+)')
    pixels = []
    for line in result.stdout.splitlines():
      match = pattern.match(line)
      if match:
        pixels.append(tuple(int(value) for value in match.groups()[1:]))
    if len(pixels) != height:
      raise RuntimeError(
        f'could not read screenshot column at x={x}: '
        f'expected {height} pixels, found {len(pixels)}'
      )
    return pixels

  @staticmethod
  def _average_color(pixels, start, end):
    count = end - start
    return tuple(
      sum(pixels[index][channel] for index in range(start, end)) / count
      for channel in range(3)
    )

  def detect_terminal_divider(self, screenshot_path, search_range):
    window_x, window_y, window_width, window_height = self.window_geometry()
    dimensions = subprocess.run([
      'magick', 'identify', '-format', '%w,%h', str(screenshot_path)
    ], check=True, capture_output=True, text=True).stdout.strip()
    image_width, image_height = [int(value) for value in dimensions.split(',')]
    logical_width, logical_height = self.logical_display_size()
    scale_x = image_width / logical_width
    scale_y = image_height / logical_height
    if abs(scale_x - scale_y) > 0.01:
      raise RuntimeError('display screenshot has inconsistent pixel scaling')
    scale = scale_x

    logical_xs = [
      window_x + round(window_width * fraction)
      for fraction in (0.20, 0.35, 0.55)
    ]
    columns = [
      self._column_pixels(
        screenshot_path, round(logical_x * scale), image_height
      )
      for logical_x in logical_xs
    ]
    first_y = max(window_y + search_range[0], window_y + 80)
    last_y = min(
      window_y + search_range[1], window_y + window_height - 100
    )
    start = max(round(first_y * scale), 16)
    end = min(round(last_y * scale), image_height - 16)

    best = None
    for y in range(start, end):
      column_scores = []
      for pixels in columns:
        above = self._average_color(pixels, y - 12, y - 4)
        below = self._average_color(pixels, y + 4, y + 12)
        distance = sum(
          (above[channel] - below[channel]) ** 2
          for channel in range(3)
        ) ** 0.5
        column_scores.append(distance)
      score = median(column_scores)
      if min(column_scores) < score * 0.6:
        continue
      if best is None or score > best[0]:
        best = (score, y)

    if best is None or best[0] < 6:
      raise RuntimeError(
        'could not locate the horizontal terminal divider with confidence'
      )
    return round(best[1] / scale)

  def resize_terminal_panel(self, x, target_y, search_range=(90, 950)):
    if self.temp_root is None:
      raise RuntimeError('disposable project has not been created')
    before = self.temp_root / 'terminal-before.png'
    after = self.temp_root / 'terminal-after.png'
    self.targeted('return name of front window', True)
    subprocess.run([
      '/usr/sbin/screencapture', '-x', f'-D{self.display_number}', str(before)
    ], check=True)
    handle_offset = 5
    start_y = (
      self.detect_terminal_divider(before, search_range) + handle_offset
    )
    if abs(start_y - target_y) > 4:
      self.drag((x, start_y), (x, target_y))
      time.sleep(0.5)
    subprocess.run([
      '/usr/sbin/screencapture', '-x', f'-D{self.display_number}', str(after)
    ], check=True)
    actual_y = (
      self.detect_terminal_divider(after, search_range) + handle_offset
    )
    if abs(actual_y - target_y) > 8:
      raise RuntimeError(
        f'terminal divider verification failed: expected y={target_y}, '
        f'found y={actual_y} (started at y={start_y})'
      )
    before.unlink(missing_ok=True)
    after.unlink(missing_ok=True)
    return start_y, actual_y

  def prepare_default_vscode(self, profile=None):
    selected = profile or DEFAULT_VSCODE_PROFILE
    if self.logical_display_size() != tuple(selected['logical_display']):
      raise RuntimeError('logical display does not match the accepted profile')
    self.create_copy()
    self.open_vscode()
    self.wait_for_window()
    self.assert_window_size(selected['minimum_window_size'])
    auxiliary_panel_key_code = selected.get('auxiliary_panel_key_code')
    if auxiliary_panel_key_code is not None:
      self.hotkey(auxiliary_panel_key_code)
      time.sleep(0.4)
    self.open_terminal()
    time.sleep(selected.get('terminal_open_delay', 1.5))
    self.resize_terminal_panel(
      selected['terminal_drag_x'], selected['terminal_target_y'],
      selected['terminal_search_y']
    )
    time.sleep(0.4)

  def quick_open(self, relative_path):
    path = self._apple_string(relative_path)
    self.targeted(f'''
keystroke "p" using command down
delay 0.25
set savedClipboard to missing value
try
  set savedClipboard to the clipboard as record
end try
set the clipboard to "{path}"
keystroke "v" using command down
delay 0.2
key code 36
if savedClipboard is not missing value then set the clipboard to savedClipboard
''')

  def hotkey(self, key_code, modifiers='command down'):
    self.targeted(f'key code {key_code} using {modifiers}')

  def type_text(self, text, character_delay=0.045):
    safe = self._apple_string(text)
    self.targeted(f'''
repeat with currentCharacter in characters of "{safe}"
  keystroke currentCharacter
  delay {character_delay}
end repeat
''')

  def wait_for_files(self, relative_paths, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
      if all((self.project / path).exists() for path in relative_paths):
        return
      time.sleep(0.2)
    missing = [path for path in relative_paths if not (self.project / path).exists()]
    raise RuntimeError('timed out waiting for: ' + ', '.join(missing))

  def mark(self, name, **details):
    self.events.append({
      'name': name,
      'timestamp_ms': round(time.monotonic() * 1000),
      **details
    })

  def start_capture(self):
    self.output_video.parent.mkdir(parents=True, exist_ok=True)
    self.capture = subprocess.Popen([
      '/usr/sbin/screencapture', '-v', f'-D{self.display_number}', '-k', str(self.output_video)
    ])
    self.mark('recording_started')

  def stop_capture(self):
    if self.capture is None:
      return
    if self.capture.poll() is None:
      self.capture.send_signal(signal.SIGINT)
    code = self.capture.wait(timeout=30)
    self.capture = None
    if code != 0 or not self.output_video.is_file():
      raise RuntimeError(f'screen capture failed with exit code {code}')
    self.mark('recording_stopped')

  def write_events(self, metadata=None):
    payload = {'schema_version': 1, **(metadata or {}), 'events': self.events}
    self.output_events.write_text(json.dumps(payload, indent=2) + '\n')

  def cleanup(self):
    if self.capture is not None:
      try:
        self.stop_capture()
      except Exception:
        if self.capture is not None:
          self.capture.kill()
          self.capture.wait()
          self.capture = None
    if self.window_slug:
      try:
        self.targeted('keystroke "w" using {command down, shift down}')
      except Exception:
        pass
    if self.project:
      time.sleep(0.8)
      shutil.rmtree(self.project, ignore_errors=True)
      time.sleep(0.4)
      shutil.rmtree(self.project, ignore_errors=True)
    if self.temp_root:
      shutil.rmtree(self.temp_root, ignore_errors=True)
