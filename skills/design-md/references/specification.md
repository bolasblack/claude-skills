# DESIGN.md Specification

Source: `https://stitch.withgoogle.com/docs/design-md/specification`

A `DESIGN.md` file has two layers:

- YAML front matter with machine-readable design tokens.
- Markdown body with human-readable design rationale organized into `##` sections.

Tokens are normative. Prose provides context for how to apply them.

The spec is a foundation, not a prescription. It provides common ground while preserving freedom to extend the format.

## YAML front matter

The front matter block must begin with a line containing exactly `---` and end with a line containing exactly `---`.

```yaml
---
version: alpha
name: Daylight Prestige
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  on-surface: "#FFFFFF"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 12px
---
```

The token system is inspired by the W3C Design Token Format. Tokens can be converted to and from `tokens.json`, Figma variables, and Tailwind theme configs.

## Schema

```yaml
version: <string>          # optional, current version: "alpha"
name: <string>
description: <string>      # optional
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <token-name>: <string | token reference>
```

`<scale-level>` is a named level in a sizing or spacing scale. Common names: `xs`, `sm`, `md`, `lg`, `xl`, `full`. Any descriptive string key is valid.

## Token types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex code, sRGB | `"#1A1C1E"` |
| Dimension | number + unit `px`, `em`, `rem` | `48px`, `-0.02em` |
| Token Reference | `{path.to.token}` | `{colors.primary}` |
| Typography | composite object | see typography properties |

## Typography properties

| Property | Type | Description |
|----------|------|-------------|
| `fontFamily` | string | Font family name |
| `fontSize` | Dimension | Font size |
| `fontWeight` | number | Numeric weight, for example 400 or 700 |
| `lineHeight` | Dimension or number | Dimension such as `24px`, or unitless multiplier such as `1.6`; unitless is recommended |
| `letterSpacing` | Dimension | Letter spacing adjustment |
| `fontFeature` | string | Configures `font-feature-settings` |
| `fontVariation` | string | Configures `font-variation-settings` |

## Token references

A token reference is wrapped in curly braces and contains an object path to another value in the YAML tree.

For most token groups, references must point to primitive values, not groups. Within `components`, references to composite values such as `{typography.label-md}` are permitted.

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
```

## Markdown sections

Recognized sections should appear in this sequence. All sections use `##` headings. An optional `#` heading may appear for document titling but is not parsed as a section.

| # | Section | Aliases |
|---|---------|---------|
| 1 | `Overview` | `Brand & Style` |
| 2 | `Colors` | |
| 3 | `Typography` | |
| 4 | `Layout` | `Layout & Spacing` |
| 5 | `Elevation & Depth` | `Elevation` |
| 6 | `Shapes` | |
| 7 | `Components` | |
| 8 | `Do's and Don'ts` | |

The section structure is open-ended. Add domain-specific sections when useful. Preserve unknown sections.

### Overview

Also known as `Brand & Style`. A holistic description of product look and feel, brand personality, target audience, and emotional response.

### Colors

Defines color palettes. At least the primary palette should be defined when colors are present. Additional palettes may be named freely. Common convention: `primary`, `secondary`, `tertiary`, `neutral`.

Recommended color token names: `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`.

### Typography

Defines typography levels. Most design systems have 9-15 levels, each with a semantic role and size variant.

Recommended typography token names: `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`.

### Layout

Also known as `Layout & Spacing`. Describes grid models, spacing scales, and containment principles.

Spacing token example:

```yaml
spacing:
  base: 16px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
  gutter: 24px
  margin: 32px
```

### Elevation & Depth

Also known as `Elevation`. Describes how visual hierarchy is conveyed. For shadow-based designs, define shadow properties. For flat designs, explain alternatives such as borders, tonal layers, and color contrast.

### Shapes

Describes corner radii, edge treatments, and overall shape language.

Rounded token example:

```yaml
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
```

Recommended rounded token names: `none`, `sm`, `md`, `lg`, `xl`, `full`.

### Components

Style guidance for component atoms. Common component types include Buttons, Chips, Lists, Inputs, Checkboxes, Radio buttons, and Tooltips. Add project-specific components when needed.

A component may have variants for UI states such as hover, active, and pressed. Variants are defined as separate component entries with related key names.

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.secondary}"
```

Recognized component property tokens:

| Property | Type |
|----------|------|
| `backgroundColor` | Color |
| `textColor` | Color |
| `typography` | Typography |
| `rounded` | Dimension |
| `padding` | Dimension |
| `size` | Dimension |
| `height` | Dimension |
| `width` | Dimension |

### Do's and Don'ts

Practical guidelines and common pitfalls. These act as guardrails during generation.

## Consumer behavior for unknown content

| Scenario | Behavior | Example |
|----------|----------|---------|
| Unknown section heading | Preserve; do not error | `## Iconography` |
| Unknown color token name | Accept if value is valid | `surface-container-high: "#ede7dd"` |
| Unknown typography token name | Accept as valid typography | `telemetry-data` |
| Unknown spacing value | Accept; store as string if not a valid dimension | `grid-columns: "5"` |
| Unknown component property | Accept with warning | `borderColor` |
| Duplicate section heading | Error; reject the file | two `## Colors` headings |
