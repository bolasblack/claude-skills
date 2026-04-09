---
name: design-md
description: "Generate or update a DESIGN.MD file — a design system document that AI agents read to produce consistent UI. Use when user asks to 'create a design system', 'write a DESIGN.MD', 'generate design tokens', 'set up design guidelines', or wants consistent UI theming across a project."
---

# DESIGN.MD Generator

Create a structured DESIGN.MD that AI coding agents read to generate consistent UI across a project. Based on Google's Stitch DESIGN.MD overview:
<https://stitch.withgoogle.com/docs/design-md/overview>

## Important

Before writing any DESIGN.MD content, read `references/format.md` for the complete format specification, section structure, token conventions, and validation checklist.

## Instructions

### Step 1: Gather Context

1. Check if `DESIGN.MD` already exists in the project root
2. Scan existing UI code for current patterns (colors, fonts, component libraries in use)
3. If the user's intent is unclear, ask:
   - What's the overall vibe? (e.g., "minimal dark dev tool", "playful consumer app")
   - Any existing brand colors or fonts?
   - Target platform? (mobile, web, desktop)

### Step 2: Generate

Read `references/format.md` then write `DESIGN.MD` to the project root following the 6-section structure:

1. **Overview** — design philosophy in 2-3 sentences
2. **Colors** — 4 base palette colors (Primary, Secondary, Tertiary, Neutral) with hex + role, plus named/semantic colors
3. **Typography** — font families, weights, sizes per role
4. **Elevation** — shadow-based or flat, with specifics
5. **Components** — concrete specs for relevant component atoms
6. **Do's and Don'ts** — actionable constraints, not opinions

### Step 3: Validate

Run through the checklist in `references/format.md`:
- Hex colors are valid 6-digit codes
- Text/background contrast meets WCAG AA (4.5:1 body, 3:1 large)
- Component specs are concrete values, not vague adjectives
- Do's and Don'ts are enforceable constraints

### Step 4: Present and Iterate

Show the generated file and ask:
- Does this capture the right vibe?
- Any colors or fonts to adjust?
- Missing components important for your project?

Iterate based on feedback before finalizing.

## Examples

### Example 1: New dark theme
**User says:** "Create a DESIGN.MD for my developer dashboard, dark theme, minimal"
**Actions:**
1. Check for existing UI patterns in the codebase
2. Generate DESIGN.MD with dark surfaces, high-contrast text, minimal elevation
**Result:** Complete DESIGN.MD at project root

### Example 2: Update existing
**User says:** "Update my DESIGN.MD to use Inter instead of Roboto"
**Actions:**
1. Read existing DESIGN.MD
2. Update typography section only, preserve everything else
**Result:** Updated DESIGN.MD with new font family

## Version History
- v1.0.0: Initial version based on the Stitch DESIGN.MD overview
