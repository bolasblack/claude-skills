# Stitch DESIGN.md Reference Index

This is the entry point for the `design-md` skill. Read this file first, then load the specific reference files needed for the task.

Source docs:

- What is DESIGN.md?: `https://stitch.withgoogle.com/docs/design-md/overview`
- The specification: `https://stitch.withgoogle.com/docs/design-md/specification`
- View, edit, and export: `https://stitch.withgoogle.com/docs/design-md/usage`
- Validate with the CLI: `https://stitch.withgoogle.com/docs/design-md/cli`
- Linting rules: `https://stitch.withgoogle.com/docs/design-md/linting-rules`

## Which reference to read

| Task | Read |
|------|------|
| Explain what `DESIGN.md` is or choose a creation path | `overview.md` |
| Create or update `DESIGN.md` content | `overview.md`, `specification.md` |
| Work with Stitch UI exports or project defaults | `usage.md` |
| Validate, diff, export, or integrate tokens with tooling | `cli.md`, `linting-rules.md` |
| Diagnose validation findings | `linting-rules.md`, then `specification.md` if needed |
| Full rebuild or major reconciliation | all reference files |

## Core model

`DESIGN.md` has two layers:

1. YAML front matter with machine-readable design tokens.
2. Markdown body with human-readable design rationale.

Tokens are normative. Prose explains why the tokens exist and how to apply them.

## Required output shape

Use `DESIGN.md` as the file name.

Start with YAML front matter delimited by `---`, then write markdown sections. The canonical recognized markdown section order is:

1. `## Overview`
2. `## Colors`
3. `## Typography`
4. `## Layout`
5. `## Elevation & Depth`
6. `## Shapes`
7. `## Components`
8. `## Do's and Don'ts`

Recognized aliases:

- `Brand & Style` for `Overview`
- `Layout & Spacing` for `Layout`
- `Elevation` for `Elevation & Depth`

## Validation priorities

Before reporting a `DESIGN.md` as done, check:

- YAML front matter parses and includes a `name`.
- Token references use `{path.to.token}` and resolve.
- Components use recognized sub-token properties or explicitly preserve unknown properties with a warning.
- Recognized markdown sections are in canonical order.
- No duplicate recognized markdown sections exist.
- If colors are defined, include `primary`.
- If colors are defined, include typography tokens unless there is a deliberate reason not to.
- Component `backgroundColor` and `textColor` pairs meet WCAG AA 4.5:1.

## Dependency safety

The official CLI is `@google/design.md`, but do not install or invoke commands that may install it unless the user explicitly approves dependency installation and dependency-safety checks have passed. Plain `npx @google/design.md ...` may install the package implicitly.
