# What is DESIGN.md?

Source: `https://stitch.withgoogle.com/docs/design-md/overview`

If this Stitch page appears empty or only shows the app shell, inspect the nested iframe content; the actual docs may be two iframe layers deep, and the innermost documentation frame URL may change over time.

`DESIGN.md` is a design system document that AI agents read to generate consistent UI across a project.

It is the design counterpart to `AGENTS.md`:

| File | Who reads it | What it defines |
|------|--------------|-----------------|
| `README.md` | Humans | What the project is |
| `AGENTS.md` | Coding agents | How to build the project |
| `DESIGN.md` | Design agents | How the project should look and feel |

## What it gives you

When a design agent reads `DESIGN.md`, generated screens follow the same visual rules: color palette, typography, and component patterns. Without it, screens stand alone. With it, they look like they belong together.

`DESIGN.md` is a living artifact, not a static config file. It evolves as the design evolves. The agent generates it, the user refines it, and it is re-applied to screens during iteration.

## Two-layer model

A fully structured `DESIGN.md` has two layers:

1. **YAML front matter** containing machine-readable design tokens: exact hex values, font properties, spacing scales.
2. **Markdown body** providing human-readable design rationale.

Tokens give agents precise values. Prose tells them why those values exist. Generate both layers for new files; existing prose-only files can still be useful, but are less precise for tools and agents.

## Philosophy

The spec is a foundation, not a prescription. It provides common ground and shared vocabulary for colors, typography, layout, and components while preserving room for domain-specific extensions.

Unknown sections and custom tokens are accepted, not rejected.

## Creation paths

### Let the agent generate it

Describe the vibe. The agent translates aesthetic intent into tokens and guidelines.

Example prompt:

```text
A playful coffee shop ordering app with warm colors, rounded corners, and a friendly feel
```

### Derive from branding

If branding already exists, provide a URL or image. The agent extracts palette, typography, and style patterns to build `DESIGN.md` from what exists.

### Write it by hand

Advanced users can author `DESIGN.md` directly. Prefer starting with YAML front matter for design tokens, then use standard markdown for rationale. No special syntax beyond standard YAML and markdown.

## Minimal example from the docs

```markdown
---
name: DevFocus Dark
colors:
  primary: "#2665fd"
  secondary: "#475569"
  surface: "#0b1326"
  on-surface: "#dae2fd"
  error: "#ffb4ab"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
rounded:
  md: 8px
---

# Design System

## Overview
A focused, minimal dark interface for a developer productivity tool.
Clean lines, low visual noise, high information density.

## Colors
- **Primary** (#2665fd): CTAs, active states, key interactive elements
- **Secondary** (#475569): Supporting UI, chips, secondary actions
- **Surface** (#0b1326): Page backgrounds
- **On-surface** (#dae2fd): Primary text on dark backgrounds
- **Error** (#ffb4ab): Validation errors, destructive actions

## Typography
- **Headlines**: Inter, semi-bold
- **Body**: Inter, regular, 14-16px
- **Labels**: Inter, medium, 12px, uppercase for section headers

## Components
- **Buttons**: Rounded (8px), primary uses brand blue fill
- **Inputs**: 1px border, subtle surface-variant background
- **Cards**: No elevation, relies on border and background contrast

## Do's and Don'ts
- Do use the primary color sparingly, only for the most important action
- Don't mix rounded and sharp corners in the same view
- Do maintain 4.5:1 contrast ratio for all body text
```
