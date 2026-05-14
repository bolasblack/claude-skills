# Stitch DESIGN.md Reference Index

This is the entry point for the `design-md` skill. Read this file first, then load the specific reference files needed for the task.

Source docs:

- Implementation/spec/tooling source: `https://github.com/google-labs-code/design.md`
- Implementation spec markdown: `https://github.com/google-labs-code/design.md/blob/main/docs/spec.md`
- Stitch product docs overview: `https://stitch.withgoogle.com/docs/design-md/overview`
- Stitch product docs specification: `https://stitch.withgoogle.com/docs/design-md/specification`
- Stitch product docs usage: `https://stitch.withgoogle.com/docs/design-md/usage`
- Stitch product docs CLI: `https://stitch.withgoogle.com/docs/design-md/cli`
- Stitch product docs linting rules: `https://stitch.withgoogle.com/docs/design-md/linting-rules`

When inspecting Stitch docs in a browser, the actual documentation content may be nested inside two iframe layers. If the visible page has little or no text, inspect the page's nested iframe tree and open the innermost documentation frame.

## Which reference to read

| Task | Read |
|------|------|
| Explain what `DESIGN.md` is or choose a creation path | `overview.md` |
| Create or update `DESIGN.md` content | `overview.md`, `specification.md` |
| Work with Stitch UI exports or project defaults | `usage.md` |
| Validate, diff, export, or integrate tokens with tooling | `cli.md`, `linting-rules.md` |
| Diagnose validation findings | `linting-rules.md`, then `specification.md` if needed |
| Full rebuild or major reconciliation | all reference files |

## Source priority

Use `google-labs-code/design.md` as authoritative for the formal spec, CLI, linter, export formats, and what official tooling accepts. Use Stitch docs for Stitch product/UI behavior and examples. If they conflict, validate against the GitHub implementation/tooling source.

## Core model

A fully structured `DESIGN.md` has two layers:

1. YAML front matter with machine-readable design tokens.
2. Markdown body with human-readable design rationale.

Tokens are normative. Prose explains why the tokens exist and how to apply them. New files should include the token layer; existing prose-only files may still be accepted by official tooling, but provide less precise control.

## Recommended output shape

Use `DESIGN.md` as the file name.

For new or substantially rebuilt files, start with YAML front matter delimited by `---`, then write markdown sections. When validating existing files, do not reject prose-only files solely for lacking front matter if official tooling accepts them. The canonical recognized markdown section order is:

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

- YAML front matter starts and ends with exact `---` delimiter lines and includes a `name` when present; new files should include front matter.
- Token references use `{path.to.token}` and resolve.
- Unknown component sub-token properties are intentional and reported as warnings; prefer recognized properties for interoperability.
- Recognized markdown sections are in canonical order.
- No duplicate recognized markdown sections exist; duplicate recognized headings are errors.
- If colors are defined, include `primary`.
- If colors are defined, include typography tokens unless there is a deliberate reason not to.
- Component `backgroundColor` and `textColor` pairs meet WCAG AA 4.5:1.

## Dependency safety

The official CLI is `@google/design.md`, but do not install or invoke commands that may install it unless the user explicitly approves dependency installation and dependency-safety checks have passed. Plain `npx @google/design.md ...` may install the package implicitly.
