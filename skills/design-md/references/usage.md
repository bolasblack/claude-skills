# View, Edit, and Export DESIGN.md

Sources:

- Stitch docs: `https://stitch.withgoogle.com/docs/design-md/usage`
- Implementation/tooling source: `https://github.com/google-labs-code/design.md`

If the Stitch page appears empty or only shows the app shell, inspect the nested iframe content; the actual docs may be two iframe layers deep, and the innermost documentation frame URL may change over time.

This page describes how Stitch exposes and exports design systems, and how `DESIGN.md` remains useful outside Stitch. If live Stitch UI behavior differs from this summary, prefer the live UI and current official docs.

## View the design system

Open the Design System panel to see the active design system for any screen. The panel shows resolved tokens:

- Colors
- Fonts
- Roundedness
- Spacing
- Component patterns

If a project has multiple design systems, the panel displays the one applied to the currently selected screen.

## Set a default design system

A design system can be selected as the project default. New screens generated after that point automatically inherit its tokens.

Existing screens are not retroactively updated. To bring existing screens into alignment, apply the design system to them individually.

## Edit via the Design System panel

The Design System panel supports direct edits to active design system tokens.

Editable properties include:

- Color palette: primary, secondary, tertiary, and neutral base colors
- Typography: headline, body, and label font families
- Roundedness: corner radius scale

For more granular changes, edit the `DESIGN.md` markdown directly. This includes:

- Component guidelines
- Do's and don'ts
- Overview narrative
- Other rationale text

Panel edits update both structured tokens and the `DESIGN.md` summary.

## Export with your project

When exporting a Stitch project, `DESIGN.md` is included in the zip alongside generated screens.

The exported `DESIGN.md` is standalone. It does not depend on Stitch to be useful.

Downstream consumers include:

- Developers
- Other design tools
- Other agents

## Working outside Stitch

The `@google/design.md` CLI validates any `DESIGN.md` file against the formal spec, checks WCAG contrast ratios, and exports tokens to Tailwind or W3C Design Token formats.

Use the CLI guidance in `cli.md`, but follow dependency-safety rules before installing or invoking package-manager commands that may install it.
