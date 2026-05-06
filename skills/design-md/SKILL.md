---
name: design-md
description: "Create, update, or validate DESIGN.md files following Google's Stitch DESIGN.md spec. Use when the user asks to write/update DESIGN.md, create a design system document, generate design tokens, encode brand/UI guidelines, export a Stitch design system, or document UI consistency rules for AI agents. Do NOT use for ordinary UI implementation unless the user asks for DESIGN.md or design-system documentation."
---

# DESIGN.md

Create or update a project-root `DESIGN.md` using the Stitch DESIGN.md format: YAML front matter for machine-readable design tokens, followed by markdown sections for human-readable design rationale.

## Source of Truth

Read `references/format.md` first. It is the reference index and tells you which detailed files to load for the task.

Detailed references:
- `references/overview.md` for the DESIGN.md concept, creation paths, and minimal example.
- `references/specification.md` for YAML front matter, token schema, token references, canonical section order, aliases, and unknown-content behavior.
- `references/usage.md` for Stitch view/edit/export behavior and outside-Stitch workflow.
- `references/cli.md` for `@google/design.md` lint, diff, export, spec, and programmatic API behavior.
- `references/linting-rules.md` for the 8 linter rules and manual validation checklist.

The core rule: tokens are normative; prose explains how to apply them. Do not use the old prose-only 6-section format.

## What This Skill Covers

The current Stitch DESIGN.md docs are split across five pages, all summarized in `references/format.md`:

- **What is DESIGN.md?**: purpose, creation paths, and the two-layer token/prose model.
- **The specification**: YAML front matter schema, token types, token references, canonical sections, aliases, and unknown-content behavior.
- **View, edit, and export**: how Stitch exposes the active design system, project defaults, editable token groups, export behavior, and outside-Stitch workflow.
- **Validate with the CLI**: lint, diff, export, spec, and programmatic API behavior for `@google/design.md`.
- **Linting rules**: the 8 rules agents should satisfy or report: `broken-ref`, `missing-primary`, `contrast-ratio`, `orphaned-tokens`, `missing-typography`, `section-order`, `missing-sections`, and `token-summary`.

## Workflow

### 1. Determine the task

- **Create**: no `DESIGN.md` exists, or the user asks for a new design system.
- **Update**: `DESIGN.md` exists and the user asks for a targeted change.
- **Validate**: the user asks whether a `DESIGN.md` follows the spec.
- **Export or integrate**: the user asks how to use `DESIGN.md` outside Stitch, export tokens, or carry the design system into code.
- **Reconcile**: the user asks to align `DESIGN.md` with current UI, brand assets, screenshots, or code.

### 2. Gather design context

Check, as available:

- Existing `DESIGN.md`
- README/product description
- Theme files, CSS variables, Tailwind config, component library config
- Representative UI components
- Brand URLs, screenshots, logos, or user-provided vibe prompts

If the project has no design context and the user gave no direction, ask for the product type, target platform, and intended look/feel.

### 3. Write the YAML token layer

`DESIGN.md` should start with YAML front matter delimited by `---` lines.

Use the Stitch token schema:

- `version` optional, current version is `alpha`
- `name` required
- `description` optional
- `colors`
- `typography`
- `rounded`
- `spacing`
- `components`

Use exact values from existing code or brand assets when available. Token references use `{path.to.token}` syntax, for example `{colors.primary}` or `{rounded.md}`.

### 4. Write the markdown rationale layer

Use the canonical section order from the Stitch spec for recognized sections:

1. `## Overview`
2. `## Colors`
3. `## Typography`
4. `## Layout`
5. `## Elevation & Depth`
6. `## Shapes`
7. `## Components`
8. `## Do's and Don'ts`

Sections can be omitted when irrelevant, but keep recognized sections in order. Unknown sections are allowed and should be preserved.

### 5. Update safely

When editing an existing `DESIGN.md`:

- Preserve custom sections and unknown tokens.
- Do not discard user-authored rationale.
- Fix broken token references instead of removing dependent components.
- Keep aliases recognizable: `Brand & Style` for Overview, `Layout & Spacing` for Layout, `Elevation` for Elevation & Depth.
- Avoid introducing duplicate recognized sections.

### 6. Validate

Use the `@google/design.md` CLI only when it is already installed in the project or globally. Do not run plain `npx @google/design.md ...`, because it can install the package implicitly.

If the CLI is unavailable, validate manually using `references/format.md`. If the user wants CLI validation and the package is not installed, first run the dependency-safety workflow and get explicit approval before installing or invoking package-manager commands that may install it.

- YAML front matter parses and has valid token types.
- Token references resolve.
- Component sub-token properties are recognized.
- Sections are in canonical order.
- Component text/background color pairs meet WCAG AA 4.5:1.
- Colors include `primary` when colors are defined.
- Typography exists when colors are defined.
- Optional `spacing` and `rounded` sections are present when explicit control matters.

## Examples

### Create from a vibe prompt

**User says:** "Create a DESIGN.md for a playful coffee shop ordering app with warm colors, rounded corners, and a friendly feel."

**Actions:**
1. Inspect existing app/theme files if present.
2. Read `references/overview.md` and `references/specification.md`.
3. Create YAML tokens for colors, typography, rounded, spacing, and core components.
4. Add markdown sections explaining the warm, rounded, friendly design rationale.

### Derive from existing branding

**User says:** "Make a DESIGN.md from our homepage and app components."

**Actions:**
1. Read `references/overview.md` and `references/specification.md`.
2. Read brand colors, fonts, spacing, and component patterns from the site/code.
3. Encode exact values as YAML tokens.
4. Use markdown sections to explain where each token should be applied.

### Validate a file

**User says:** "Check whether this DESIGN.md is valid."

**Actions:**
1. Read `references/cli.md` and `references/linting-rules.md`.
2. Use the CLI only if available without new installation.
3. Otherwise manually check Stitch lint rules from `references/linting-rules.md`.
4. Report errors, warnings, and concrete fixes.

## Version History

- v2.0.0: Rebuilt around the Stitch DESIGN.md overview, specification, CLI, and linting rules.
- v1.0.0: Initial version based on the Stitch DESIGN.md overview.
