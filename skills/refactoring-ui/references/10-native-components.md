# Native component patterns with Tailwind CSS

Start with the task people perform. Study a few interfaces that support that task, catalog their recurring patterns and states, and compare how they handle the same constraints. Then design your own example with representative data. This adapts the research method described by Adam Wathan for Tailwind UI Ecommerce. The visual principles come from *Refactoring UI*, the utility syntax comes from Tailwind CSS, and HTML and the browser supply semantics and interaction. The downloadable demo uses semantic HTML, Tailwind and native JavaScript. The Blade examples also cover Alpine.js. [Tailwind UI design process](https://tailwindcss.com/blog/designing-tailwind-ui-ecommerce) · [HTML Standard](https://html.spec.whatwg.org/multipage/) · [W3C interaction patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)

## Run and rebuild the demo

Open [the orders dashboard](../assets/index.html) from disk. [The script](../assets/orders.js) and [compiled CSS](../assets/orders.css) load from neighboring files. Keep them together. The demo uses sample data in memory. Reload to restore the original orders and follow the system theme again.

From the repository root, rebuild with the same version used for the checked-in stylesheet. The temporary directory keeps the build dependencies outside AISkills. The two explicit sources in [the CSS input](../assets/orders.input.css) make the scan independent of other files in the repository.

```sh
assets="$PWD/skills/refactoring-ui/assets"
build_dir=$(mktemp -d)
cp "$assets/index.html" "$assets/orders.js" "$assets/orders.input.css" "$build_dir/"
npm install --prefix "$build_dir" --no-save --no-package-lock tailwindcss@4.3.0 @tailwindcss/cli@4.3.0
"$build_dir/node_modules/.bin/tailwindcss" -i "$build_dir/orders.input.css" -o "$assets/orders.css" --minify
```

## Adapt a pattern to Blade

Put the selected markup in the existing view or Blade component under `resources/views/`. Render server data with escaped Blade output and connect changes to the application's existing form submission, validation and authorization. Put shared tokens in the project's Vite CSS entry and use its existing JS entry for behavior that needs JavaScript. Run the production build and confirm in DevTools that the rendered view loads the emitted CSS and that the utility takes effect. If a class disappears, follow [the source-detection checklist](09-tailwind-v4.md#diagnose-a-missing-production-class) before adding directives. [Laravel and Vite](https://tailwindcss.com/docs/installation/framework-guides/laravel/vite)

## Use Alpine.js in Blade

Use Alpine for local state and interaction, such as revealing a section or marking the active filter. Tailwind supplies the styles. In a Blade application that already loads Alpine, use the existing setup. If the project needs standalone Alpine, install `alpinejs` and initialize it once in the Vite JavaScript entry, usually `resources/js/app.js`. Make sure the layout loads that entry through `@vite`. Recent Livewire versions already load Alpine, so check the installed setup before adding a separate import. [Alpine installation](https://alpinejs.dev/essentials/installation) · [Laravel Vite](https://laravel.com/docs/13.x/vite) · [Livewire 4 installation](https://livewire.laravel.com/docs/4.x/installation)

```js
import Alpine from 'alpinejs';

Alpine.start();
```

This Blade markup gives each disclosure its own ID, keeps the button keyboard-operable and exposes the expanded state. Add `[x-cloak] { display: none !important; }` to the CSS entry so the content stays hidden until Alpine initializes. The complete utility names in both branches of `x-bind:class` are visible to Tailwind at build time. [Alpine x-show](https://alpinejs.dev/directives/show) · [Alpine class bindings](https://alpinejs.dev/directives/bind#binding-classes) · [Alpine x-id](https://alpinejs.dev/directives/id) · [Tailwind source detection](09-tailwind-v4.md#diagnose-a-missing-production-class)

```html
<div x-data="{ open: false }" x-id="['shipping-notes']">
  <button
    type="button"
    class="rounded-md px-3 py-2 font-medium focus-visible:outline-2 focus-visible:outline-offset-2"
    x-on:click="open = !open"
    x-bind:aria-controls="$id('shipping-notes')"
    x-bind:aria-expanded="open"
    x-bind:class="open ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-900'"
  >
    Shipping notes
  </button>

  <div x-bind:id="$id('shipping-notes')" x-show="open" x-cloak class="mt-2">
    Shipments leave the warehouse on business days.
  </div>
</div>
```

The snippet uses full Alpine directives on plain HTML tags. When passing a colon-prefixed Alpine attribute to a Blade component tag, use Blade’s double-colon escape, such as `<x-button ::class="open ? 'bg-slate-800' : 'bg-slate-100'">`, if the component forwards its attributes. [Blade attribute escaping](https://laravel.com/docs/13.x/blade#escaping-attribute-rendering)

From a production build, Tab to the button, use Enter and Space, and check that the panel visibility, expanded state and button classes follow the interaction. Test two instances on the same page if the component is repeated. For a complete menu example, see the official Alpine dropdown and the Blade component from Laravel Breeze. [Alpine dropdown](https://alpinejs.dev/component/dropdown) · [Breeze dropdown source](https://github.com/laravel/breeze/blob/2.x/stubs/default/resources/views/components/dropdown.blade.php)

For a small client-side filter, bind a native select with `x-model`. Put larger or repeated behavior in `Alpine.data()` and register it through the project’s Alpine setup. For results paginated on the server, send the selected value through the application’s existing query flow so the filter covers the full dataset. [Alpine select binding](https://alpinejs.dev/directives/model#select-inputs) · [Alpine data providers](https://alpinejs.dev/globals/alpine-data) · [Alpine in Livewire](https://livewire.laravel.com/docs/4.x/alpine)

```html
<div x-data="{ status: '' }" x-id="['status-filter']">
  <label x-bind:for="$id('status-filter')" class="block font-medium">Filter by status</label>
  <select x-bind:id="$id('status-filter')" x-model="status" class="rounded-md border px-3 py-2">
    <option value="">All statuses</option>
    <option value="queued">Queued</option>
    <option value="shipped">Shipped</option>
  </select>
  <p role="status" class="mt-2 text-sm" x-text="status ? '1 order' : '2 orders'">2 orders</p>
  <ul class="mt-2 space-y-1">
    <li x-show="!status || status === 'queued'">#1047 · Queued</li>
    <li x-show="!status || status === 'shipped'">#1046 · Shipped</li>
  </ul>
</div>
```

For a modal, Alpine can invoke `$refs.confirmation.showModal()` while the native `<dialog>` handles modality. Use the [confirmation pattern below](#disclosure-and-confirmation) for focus and dismissal checks. If a disclosure needs animation, Alpine supports transitions with Tailwind utility classes. Apply motion variants to respect the user’s reduced-motion preference. [Alpine refs](https://alpinejs.dev/magics/refs) · [Alpine transitions](https://alpinejs.dev/directives/transition) · [Tailwind motion variants](https://tailwindcss.com/docs/hover-focus-and-other-states#prefers-reduced-motion)

## Panel and navigation

Give the work area a descriptive title and one primary action. Keep navigation as links and changes to data as buttons. In the demo, the editor sits beside the order queue when both fit. On a narrow screen it follows the list in reading order. Match the canvas and panel tokens to the surrounding application. Reserve the action token for the leading action, and use weight and spacing to distinguish titles from supporting labels. Tab through the navigation, theme control and primary action at both widths. Activate the skip link and verify that the next Tab continues within the work area. [Complete panel](../assets/index.html#orders) · [Visual hierarchy and layout](02-page-mechanics.md) · [Responsive design](https://tailwindcss.com/docs/responsive-design)

```html
<!-- Reading order follows the markup at either width. -->
<div class="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_20rem]">
  <section aria-labelledby="queue-title">…</section>
  <section aria-labelledby="editor-title">…</section>
</div>
```

## Table, filters and empty results

Use a table when people compare attributes across orders. Scope headers to rows and columns, right-align amounts, and use tabular numerals. Give status labels distinct text as well as color and give repeated actions names that identify their order. A small table whose columns matter together can scroll in a labeled, focusable region at narrow widths. Keep the page itself in view and check that tabbing to a row action brings the control into view. For a wider table, evaluate sticky headers or a comparison-preserving narrow layout. Adjust separator and status tokens together for each theme. [Full order queue](../assets/index.html#queue-title) · [Table patterns](07-component-patterns.md#tables) · [HTML tables](https://html.spec.whatwg.org/multipage/tables.html) · [Overflow](https://tailwindcss.com/docs/overflow)

```html
<!-- Name the scroll region so it makes sense when it receives focus. -->
<div role="region" aria-labelledby="queue-title" tabindex="0" class="overflow-x-auto">
  <table class="w-full min-w-[34rem]">
    <caption class="sr-only">Orders by customer, status, and total</caption>
    <!-- Column headers and the order number as a row header give cells context. -->
  </table>
</div>
```

Label the text and status filters separately. Give results a short live count and show an actionable empty state when nothing matches. Try a matching search, a status filter and an empty combination. Clear the filters from the keyboard and check that focus returns to search. Keep the empty state within the same panel surface and use the same secondary button treatment as row actions. [Filter markup](../assets/index.html#filters) · [Filtering and reset code](../assets/orders.js) · [Empty states](04-polish.md)

## Form and native select

Use a short inline editor when users benefit from seeing their place in the order queue. Group each visible label with its input, then separate field groups using the layout spacing scale. Use native constraints for required values, numeric ranges and steps. The demo reveals error text on an invalid submission and clears the message when the field is valid. A real Blade form should validate again on the server. Share the same height, border, text, surface and focus tokens between inputs and selects. The demo styles the closed select with `appearance: none` and an inset CSS chevron to keep its height consistent with the text input in WebKit. It restores the native arrow in forced colors. The built-in picker remains available, and `color-scheme` signals the current theme to the browser. [Full editor](../assets/index.html#order-editor) · [Form patterns](07-component-patterns.md#forms) · [HTML form elements](https://html.spec.whatwg.org/multipage/forms.html) · [Tailwind color scheme](https://tailwindcss.com/docs/color-scheme)

```html
<!-- The field class is shared with the text input. Keep the native picker. -->
<label for="order-status" class="field-label">Status</label>
<div class="select-field">
  <select id="order-status" name="status" class="field" required>
    <option value="Queued">Queued</option>
    <option value="Packing">Packing</option>
    <option value="Shipped">Shipped</option>
  </select>
</div>
```

Compare closed selects to neighboring inputs in both themes at desktop and narrow widths. Open each picker, check that options and selection are legible, and choose an option with the keyboard and by touch where available. Platform pickers can draw the open list with different colors or spacing. Inspect the actual browser picker as part of verification. Tab through the editor, try to submit with an empty name and an out-of-range total, and check that the browser focuses the invalid field and the correction clears the error. [Select checks](07-component-patterns.md#select-controls) · [HTML select](https://html.spec.whatwg.org/multipage/form-elements.html#the-select-element)

## Disclosure and confirmation

Use `<details>` when the information is useful but secondary to the task. Give `<summary>` a short label, keep the disclosure marker, and use the same focus token as other controls. On a narrow screen, check that opening the guide keeps its contents readable. Activate it with Enter and Space without moving keyboard focus into the content. [Full status guide](../assets/index.html#status-guide) · [HTML disclosure](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-details-element) · [W3C disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/)

```html
<details>
  <!-- The summary is the browser-provided toggle. -->
  <summary>Status guide</summary>
  <p>Queued orders are waiting for fulfillment.</p>
</details>
```

Use a named modal when a change needs an explicit decision. Show what will be saved, use the panel surface and a backdrop, and allow actions to wrap within the available width. Opening with `showModal()` gives the browser control of the top layer, background inertness and Escape. The demo focuses the review button before opening so the browser can restore focus to it even when a pointer click leaves focus elsewhere. It applies the draft only for an explicit confirmation. [Complete dialog](../assets/index.html#confirm-order) · [Opening and saving code](../assets/orders.js) · [HTML dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element) · [W3C modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

```html
<!-- Cancel closes natively. The script handles Confirm on submit. -->
<form method="dialog">
  <button value="cancel" autofocus>Cancel</button>
  <button value="confirm">Save order</button>
</form>
```

Open the dialog from the keyboard. Confirm that Cancel receives initial focus, Tab and Shift+Tab keep the focus out of the underlying form, and Escape and Cancel preserve the previous order. Reopen, confirm, and check that the row changes and the form reports the save. After each dismissal, check focus on the Review changes button. Repeat in both themes at a narrow width, including a long customer name and visible focus rings. Use the same checks when adapting the panel to another browser support policy. [Modal design](07-component-patterns.md#modals) · [Dark mode](06-dark-mode.md)
