# DESIGN.MD Format Specification

Based on Google's Stitch DESIGN.MD overview:
<https://stitch.withgoogle.com/docs/design-md/overview>

## What is DESIGN.MD?

A design system document that AI agents read to generate consistent UI across a project. It has two representations:

- **Markdown** (human-friendly): what you read and edit
- **Structured tokens** (machine-friendly): hex values, font enums, spacing scales parsed from the markdown for precise enforcement during generation

You can be approximate in the markdown ("warm colors, rounded feel") and the agent translates that into precise tokens. Or you can be exact (`#2665fd`, `8px radius`) and the agent respects those values literally.

## File Location

Place `DESIGN.MD` at the project root.

## Section Structure

Every DESIGN.MD follows the same structure. Sections can be omitted if not relevant, but order should be preserved.

---

### 1. Overview

Top-level heading `# Design System` followed by `## Overview`.

A short paragraph capturing the design philosophy — the feel, not just the facts.

```markdown
# Design System

## Overview
A focused, minimal dark interface for a developer productivity tool.
Clean lines, low visual noise, high information density.
Accessibility-first design with high contrast and generous touch targets.
```

---

### 2. Colors (`## Colors`)

Define 4 base palette colors, each with:
- Bold name
- Hex value in parentheses
- Role description

| Color | Purpose |
|-------|---------|
| **Primary** | CTAs, active states, key interactive elements |
| **Secondary** | Supporting actions, chips, toggle states |
| **Tertiary** | Accent highlights, badges, decorative elements |
| **Neutral** | Backgrounds, surfaces, non-chromatic UI |

The agent also generates **named colors** from these base values following Material color role conventions:

| Named Color | Purpose |
|-------------|---------|
| `surface` | Main background |
| `surface-container` | Card/panel backgrounds |
| `surface-bright` | Elevated or highlighted surfaces |
| `on-surface` | Primary text on dark backgrounds |
| `on-primary` | Text on primary-colored backgrounds |
| `error` | Validation errors, destructive actions |
| `outline` | Borders and dividers |

```markdown
## Colors
- **Primary** (#2665fd): CTAs, active states, key interactive elements
- **Secondary** (#6074b9): Supporting actions, chips, toggle states
- **Tertiary** (#bd3800): Accent highlights, badges, decorative elements
- **Neutral** (#757681): Backgrounds, surfaces, non-chromatic UI

### Named Colors
- **On-surface** (#dae2fd): Primary text on dark backgrounds
- **Error** (#ffb4ab): Validation errors, destructive actions
- **Surface** (#1a1b23): Main background
- **Surface-container** (#242530): Card and panel backgrounds
- **Outline** (#8f9099): Borders and dividers
```

---

### 3. Typography (`## Typography`)

Font families and their roles across the typographic hierarchy: display, headline, title, body, and label levels.

Specify for each role:
- Font family name
- Weight (regular, medium, semi-bold, bold)
- Size (px or rem)
- Any special treatment (uppercase, letter-spacing)

```markdown
## Typography
- **Headlines**: Inter, semi-bold
- **Body**: Inter, regular, 14-16px
- **Labels**: Inter, medium, 12px, uppercase for section headers
```

---

### 4. Elevation (`## Elevation`)

How the design conveys depth and hierarchy. Two approaches:

**Flat (no shadows):**
```markdown
## Elevation
This design uses no shadows. Depth is conveyed through border contrast
and surface color variation (surface, surface-container, surface-bright).
```

**Shadow-based:**
```markdown
## Elevation
Cards and modals use subtle elevation.
- **Level 1** (cards): 0 2px 4px rgba(0,0,0,0.1)
- **Level 2** (modals): 0 8px 24px rgba(0,0,0,0.15)
Buttons do not use elevation.
```

If shadows are used, specify:
- Shadow properties (spread, blur, color)
- Which components should be elevated
- Number of elevation levels

---

### 5. Components (`## Components`)

Style guidance for component atoms. Focus on the components most relevant to the application.

| Component | What to specify |
|-----------|----------------|
| **Buttons** | Variants (primary, secondary, tertiary), sizing, padding, corner radius, states |
| **Inputs** | Border style, background, padding |
| **Cards** | Elevation, border, corner radius |
| **Chips** | Selection, filter, and action variants |
| **Lists** | Item styling, dividers, leading/trailing elements |
| **Navigation** | Bar style, active indicators, positioning |
| **Modals/Dialogs** | Overlay, sizing, corner radius |
| **Tabs** | Active/inactive styling, indicator style |

You can suggest components based on the project's context. For example, a mobile app needs a bottom navigation bar; a dashboard needs data tables.

```markdown
## Components
- **Buttons**: Rounded (8px), primary uses brand blue fill, secondary uses outline
- **Inputs**: 1px border, surface-variant background, 12px padding
- **Cards**: No elevation, 1px outline border, 12px corner radius
- **Navigation**: Bottom bar with 5 items, filled icon for active state
```

---

### 6. Do's and Don'ts (`## Do's and Don'ts`)

Practical guardrails that constrain generation. These should be:
- Actionable (not aspirational)
- Specific (not "make it look good")
- Measurable where possible (contrast ratios, counts, sizes)

```markdown
## Do's and Don'ts
- Do use the primary color only for the single most important action per screen
- Don't mix rounded and sharp corners in the same view
- Do maintain WCAG AA contrast ratios (4.5:1 for normal text)
- Don't use more than two font weights on a single screen
- Do keep touch targets at least 44x44px on mobile
- Don't use color as the only way to convey information
```

---

## Validation Checklist

After writing a DESIGN.MD, verify:

- [ ] All hex colors are valid 6-digit codes (e.g., `#2665fd` not `#2665f`)
- [ ] Text-on-background pairs meet WCAG AA contrast (4.5:1 for body, 3:1 for large text)
- [ ] Font sizes are in px or rem, not arbitrary units
- [ ] Component specs use concrete values (not "modern" or "clean")
- [ ] Do's and Don'ts are constraints an agent can check, not opinions
- [ ] All 4 base colors have distinct hex values and clear role separation
- [ ] Section order matches: Overview > Colors > Typography > Elevation > Components > Do's and Don'ts

## Complete Example

A minimal DESIGN.MD for a dark-themed productivity app:

```markdown
# Design System

## Overview
A focused, minimal dark interface for a developer productivity tool.
Clean lines, low visual noise, high information density.

## Colors
- **Primary** (#2665fd): CTAs, active states, key interactive elements
- **Secondary** (#6074b9): Supporting actions, chips, toggle states
- **Tertiary** (#bd3800): Accent highlights, badges, decorative elements
- **Neutral** (#757681): Backgrounds, surfaces, non-chromatic UI

### Named Colors
- **On-surface** (#dae2fd): Primary text on dark backgrounds
- **Error** (#ffb4ab): Validation errors, destructive actions
- **Surface** (#1a1b23): Main background
- **Surface-container** (#242530): Card and panel backgrounds

## Typography
- **Headlines**: Inter, semi-bold
- **Body**: Inter, regular, 14-16px
- **Labels**: Inter, medium, 12px, uppercase for section headers

## Elevation
This design uses no shadows. Depth is conveyed through border contrast
and surface color variation (surface, surface-container, surface-bright).

## Components
- **Buttons**: Rounded (8px), primary uses brand blue fill, secondary uses outline
- **Inputs**: 1px border, surface-variant background, 12px padding
- **Cards**: No elevation, 1px outline border, 12px corner radius

## Do's and Don'ts
- Do use the primary color only for the single most important action per screen
- Don't mix rounded and sharp corners in the same view
- Do maintain WCAG AA contrast ratios (4.5:1 for normal text)
- Don't use more than two font weights on a single screen
```
