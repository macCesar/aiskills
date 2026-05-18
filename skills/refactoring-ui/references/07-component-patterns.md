# Component Patterns: Modals, Forms, Tables

> **Scope note**: *Refactoring UI* covers button tiers and label patterns directly (see `02-page-mechanics.md`), but does not have dedicated chapters for modals, forms, or tables. This file applies the book's principles — hierarchy through weight/color, generous spacing, grouping by proximity, finishing with restraint — to these three common components.

---

## Modals

### When to Use a Modal

- A focused decision that **blocks** the current task (confirm destructive action, complete a required step)
- Short content that doesn't deserve a full page
- Multi-step flows that should preserve the underlying context (the page behind the modal)

When **not** to use a modal:

- Anything the user might want to consult while doing the surrounding task — modals trap them
- Long content that scrolls — make it a page
- Anything that needs to be linkable — modals are stateless to the URL by default

### Layout

| Element | Rule |
|---|---|
| Width | Fixed pixel max (`max-width: 480px` typical) — never percentage |
| Vertical position | Anchored ~10–15% from the top of viewport, not centered — feels more stable |
| Backdrop | Semi-opaque dark overlay (~50–70% opacity) — darkens the page enough to focus attention |
| Padding | Generous — modal content is usually short; tight padding feels cramped |
| Close affordance | "Cancel" button in the footer AND an `×` in the top corner — keyboard users use Esc |

### Focus and Keyboard

Three keyboard requirements, all non-negotiable:

1. **Focus moves into the modal on open** — typically to the first interactive element, or the close button if the modal is informational
2. **Focus traps inside the modal** — Tab/Shift+Tab cycle through modal elements only, never leaking to the page behind
3. **Esc closes the modal** AND focus returns to the element that opened it

These are the table-stakes of accessibility for modals. Libraries like `focus-trap` or `@radix-ui/react-dialog` solve them — don't roll your own unless you must.

### Button Order

The primary action sits on the **right** in left-to-right UIs:

```
[ Cancel ]   [ Save changes ]
```

Destructive primary actions get an extra confirmation (a typed confirmation, or a secondary modal). Don't bury a destructive button next to a safe one.

## Forms

### Label Placement

Top-aligned labels are the default for almost every form:

- Fastest to scan top-to-bottom
- Work on narrow screens without reflow
- Easier to localize (labels grow in length across languages)

Left-aligned labels look formal but force the user's eye to zig-zag and break on mobile. Reserve for dense data-entry screens where users repeatedly fill the same form.

### Validation Timing

- **On blur** for individual fields — show the error after the user leaves the field, not while they're typing
- **On submit** for fields they haven't touched yet
- **On change** ONLY for fields where the answer is binary and visible (e.g., a password strength meter, a username availability check)

Inline validation while the user is mid-typing reads as the form fighting them.

### Error Display

A field in error state should have:

- A color change (red border, but not the *only* signal)
- A short message **below** the field, in the same color as the border
- An icon at the start of the message — color is not enough (≈8% of males can't distinguish red from green)
- The field's normal label and placeholder stay legible — don't replace them with the error

### Spacing Within a Form

Apply the Law of Proximity from `02-page-mechanics.md`:

```
[Label]
[Input]
 (small gap, ~8px)
[Helper text]

(large gap, ~24-32px to the next field group)

[Label]
[Input]
```

Label sits closer to its own input than to anything else. Each field group is clearly separated from the next.

### Button Placement

- **Single primary button** at the bottom left or center — never aligned right unless the form sits inside a modal (modals follow the modal rule)
- **Secondary "Cancel"** to the left of the primary
- Disable the submit button only when there are concrete errors — disabling it preemptively because the user "hasn't typed everything yet" leaves them guessing

### Required vs Optional

If most fields are required, mark only the **optional** ones — less noise overall. If most are optional, mark the required ones with `*`. Either system is fine — pick one and stay consistent.

## Tables

### Density Tiers

Pick a row density based on the user's job:

| Tier | Row height | Use |
|---|---|---|
| Comfortable | 56–64px | Marketing tables, dashboards seen occasionally |
| Default | 40–48px | Most app tables |
| Compact | 28–36px | Operator dashboards (CRM, admin, finance) where rows are scanned in bulk |

Don't go below 28px unless the data is genuinely homogeneous — eye fatigue scales with row count, not just total height.

### Alignment by Data Type

| Data type | Alignment | Reason |
|---|---|---|
| Text (names, labels) | Left | Default reading direction |
| Numbers (counts, money, percentages) | Right | Digits and decimals line up; magnitudes are scannable |
| Dates | Left or right consistent | Pick one and stick — comparing dates is easier with consistent alignment |
| Status / chips | Center inside their own column | Visually balanced when the chip is the only content |
| Actions (icons, kebabs) | Right | Out of the way of the data |

### Column Headers

Mirror the column's content alignment. A right-aligned numeric column gets a right-aligned header.

Sortable columns get an indicator (arrow up/down) AND show the active sort with stronger contrast — color alone isn't enough.

### Sticky Headers

For tables that scroll vertically inside their container, the header should stick. Two ways:

1. `position: sticky; top: 0;` on the `<thead>` — easiest, works inside scrollable containers
2. A second fixed header rendered above the scroll area — needed when the table itself scrolls in `<body>` (not its own container)

Sticky headers must have a solid (opaque) background, otherwise rows scrolling behind them show through.

### Row Hover and Selection

- Subtle row hover background (one shade-step on neutrals) — helps the eye track across wide tables
- Selection: a left-edge accent stripe **plus** a tinted background — selection should be obvious without screaming
- Don't animate row hover — adds latency to bulk scanning

### Empty Tables

Apply the empty-state rule from `04-polish.md`: don't just show "No data" centered in a blank rectangle. The empty state communicates what could go there and offers a way to start.

## Anti-Patterns

### Modals

- ❌ Centering vertically — feels unanchored
- ❌ No close affordance — Esc users can escape, mouse users get stuck
- ❌ Modals over modals (nested) — confusing back-stack
- ❌ Destructive action as primary button without confirmation step
- ❌ No focus trap — Tab leaks to the page behind

### Forms

- ❌ Placeholder as the only label — vanishes on focus, accessibility regression
- ❌ Inline validation on keystroke — fights the user
- ❌ Disabling the submit button without explaining why
- ❌ Red asterisks on every field — visual noise
- ❌ Forms wider than ~600px — eye tracking degrades

### Tables

- ❌ Centered text columns — slow to scan
- ❌ Left-aligned numeric columns — magnitudes hide
- ❌ Translucent sticky header — rows show through
- ❌ Row dividers AND row hover background — over-decorated
- ❌ A single fixed column width for every column — wastes space; let content determine width within sensible min/max
