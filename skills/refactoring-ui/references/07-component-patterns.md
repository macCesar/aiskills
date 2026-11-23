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
| Width | Use a readable maximum (for example, 480px) and leave gutters at narrow widths |
| Vertical position | Anchored ~10–15% from the top of viewport, not centered — feels more stable |
| Backdrop | Semi-opaque dark overlay (~50–70% opacity) — darkens the page enough to focus attention |
| Padding | Generous — modal content is usually short; tight padding feels cramped |
| Close affordance | Give the dialog a visible Cancel or Close action. An additional corner button can help on longer dialogs. |

### Focus and Keyboard

Three keyboard requirements, all non-negotiable:

1. **Move focus into the modal on open.** Use the control that fits the task, such as Cancel for a hard-to-reverse action or a focusable heading for lengthy content.
2. **Keep Tab and Shift+Tab within the modal.** The page behind it stays inert.
3. **Support Escape and restore focus on close.** Return to the opener where it still exists, or choose the next logical target in the workflow.

On the web, use a named native `<dialog>` opened with `showModal()` when it fits the project. Verify the browser’s focus behavior with the actual markup. [HTML dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element) · [WAI modal pattern and examples](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) · [Runnable confirmation](10-native-components.md#disclosure-and-confirmation)

### Button Order

The primary action sits on the **right** in left-to-right UIs:

```
[ Cancel ]   [ Save changes ]
```

For hard-to-reverse changes, describe the consequence and name the action precisely. A typed confirmation can fit an unusually costly operation. Use one clear confirmation step and give the safer action initial focus when appropriate. [WAI modal guidance](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

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
- **On change** for feedback tied to a deliberate selection. During typing, update helpful cues such as a password strength meter or clear a resolved error. Validate on blur or submit when the user needs time to finish.

Inline validation while the user is mid-typing reads as the form fighting them.

### Error Display

A field in error state should have:

- A color change (red border, but not the *only* signal)
- A short message **below** the field, in the same color as the border
- Text that identifies the error and tells the user how to correct it. An icon can reinforce the message.
- The field’s normal label and placeholder stay legible. Associate the message with the field using `aria-describedby`, and mark it `aria-invalid="true"` while invalid. On a failed submit, ensure keyboard users can reach the first invalid field or a linked error summary. [WAI form notifications](https://www.w3.org/WAI/tutorials/forms/notifications/)

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
- Let users attempt submission so validation can explain concrete errors. For a submission already in progress, use the project’s pending state to prevent duplicates and give visible feedback. [WAI form validation](https://www.w3.org/WAI/tutorials/forms/validation/)

### Required vs Optional

If most fields are required, mark only the **optional** ones — less noise overall. If most are optional, mark the required ones with `*`. Either system is fine — pick one and stay consistent.

### Select controls

- Compare each select with a neighboring input in the rendered form. Match the control height, text alignment, left padding, border, radius, background, typography, and focus treatment. Use the same field tokens and meet the project's touch-target size. Add an inset chevron when the browser's arrow differs from the design system.
- For web forms, retain native `<select>` semantics and form behavior when styling is the only issue. A custom-styled closed control and a custom-styled option list are separate. Use the same design tokens for the open list where browser support allows it, and note when the tested browser uses its native picker.
- Before handoff, compare the closed controls on desktop and at a narrow touch width, then open each menu and select an option by keyboard and touch where available. A shared class or a passing submission test does not verify visual parity.

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

Use a button inside the sortable column header and put `aria-sort` on the currently sorted `<th>`. Give the active sort a direction indicator and sufficient contrast. [WAI sortable table example](https://www.w3.org/WAI/ARIA/apg/patterns/table/examples/sortable-table/)

### Sticky Headers

For a table long enough to lose column context, consider a sticky header. Keep a single semantic header and use `position: sticky; top: 0;` on the header row group or its cells. Check the nearest scrolling ancestor and account for any fixed navigation. Use an opaque background and verify that focused controls remain visible when scrolling. [Tailwind position](https://tailwindcss.com/docs/position#sticky-positioning-elements) · [WCAG focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)

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
