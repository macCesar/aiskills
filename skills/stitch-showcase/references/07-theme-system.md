# Section: Theme System (Light/Dark Mode)

## Purpose

Consistent light/dark mode across index.html and viewer.html, with intelligent defaults based on the project's surface color and user preference persistence.

## Data Required (from showcase_context.json)

- `default_theme` — "light" or "dark", computed from surface color luminance
- `color_tokens.surface` — the app's surface color (used to compute smart default)

## Design Requirements

### Smart Default

The default theme is the **opposite** of the app's surface color for maximum contrast:
- Dark app surface (luminance < 100) → showcase opens in **light** mode
- Light app surface (luminance > 155) → showcase opens in **dark** mode
- This ensures thumbnails stand out against the showcase background

### Color Tokens

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Page background | `#f5f5f5` or `#fafafa` | `#0d0d0d` or `#0a0a0a` |
| Card background | `#ffffff` | `#1a1a1a` |
| Card border | `rgba(0,0,0,0.08)` | `rgba(255,255,255,0.08)` |
| Text primary | `#111827` (gray-900) | `#f3f4f6` (gray-100) |
| Text secondary | `#6b7280` (gray-500) | `#9ca3af` (gray-400) |
| Text muted | `#9ca3af` (gray-400) | `#6b7280` (gray-500) |

### Transitions

- All color transitions: `transition-colors duration-200`
- Apply to `<body>` and major containers
- No flash of wrong theme on load (theme class applied before render)

## Functional Requirements

### Initialization (Critical — no flash)

```javascript
// In <head> BEFORE any rendering — blocks render until class is set
(function() {
  const saved = localStorage.getItem('showcase-theme');
  const defaultTheme = '{{DEFAULT_THEME}}'; // from context
  const theme = saved || defaultTheme;
  if (theme === 'dark') document.documentElement.classList.add('dark');
})();
```

### Toggle Logic

```javascript
document.getElementById('theme-toggle').addEventListener('click', () => {
  document.documentElement.classList.toggle('dark');
  const isDark = document.documentElement.classList.contains('dark');
  localStorage.setItem('showcase-theme', isDark ? 'dark' : 'light');
});
```

### Shared State

- Both index.html and viewer.html read/write the same `localStorage` key: `'showcase-theme'`
- Opening viewer from index inherits the current theme immediately

## Implementation Notes

- Use Tailwind's `darkMode: 'class'` configuration
- Tailwind config should extend colors with the project's accent: `colors: { accent: '{{PRIMARY_COLOR}}' }`
- The theme initialization script MUST be in `<head>`, not at end of body, to prevent flash

## Anti-Patterns

- Do NOT use `prefers-color-scheme` as the only source — the smart default from surface luminance is more important for showcase contrast
- Do NOT animate the initial theme application (only transitions after user interaction)
- Do NOT forget to sync theme between index and viewer pages
