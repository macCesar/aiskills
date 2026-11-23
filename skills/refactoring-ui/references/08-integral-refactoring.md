# Integral UI Refactoring

This implementation and verification workflow is an AISkills extension to the design guidance inspired by *Refactoring UI*.

## Inventory the requested scope

Before editing, use the navigation, routes, and app structure to build a working inventory by module. Include list, create, edit, and detail screens, plus the modals, previews, and row actions reached from them. Account for alternate states and permissions that materially change the UI. Keep the inventory lightweight and in the working context unless a persistent artifact is requested. For a targeted request, keep the inventory and verification local to the affected flow and its direct regressions.

## Apply patterns across modules

Read the supplied references and identify reusable layout, hierarchy, and interaction patterns. Compare screens that serve the same purpose, including ones without a matching reference. Use shared components and styles where they fit. Choose the layout for each task and note intentional exceptions, such as a short editor that fits in a modal or a long form that benefits from a secondary column. Review the body of each screen and the UI reached through its controls.

## Verify rendered flows

Use the running app with real or representative, safely accessible records. Open the previews and read their contents. Compare related tables side by side for action visibility, labels, spacing, and touch targets. Check meaningful states at desktop and narrow widths, and test pointer, keyboard, and touch interactions where they apply. Cover shared patterns in representative flows and inspect their exceptions separately. For web work, confirm that sticky headers and panels leave focused controls visible and that row actions have adequate target size and spacing. WCAG 2.2 AA specifies at least 24 × 24 CSS px for pointer targets, with exceptions including sufficient spacing. [Focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) · [Target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) Fix in-scope problems you find and recheck the affected flows. Use builds and automated tests as supporting evidence alongside the rendered review. For any affected form with selects, complete the closed and open state checks in [Select controls](07-component-patterns.md#select-controls).

## Close against the inventory

Give every item a disposition and record what was changed and checked, what already met the pattern, or what remains and why. Distinguish browser observations from static checks. If a route, role, or interaction could not be exercised, report the specific limitation and continue the checks you can perform. Claim completion only when the requested coverage is accounted for and the required work is done.
