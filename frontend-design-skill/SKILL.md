---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:

- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Spacing System**: Use 4pt or 8pt grid. All margins, padding, line-heights, and element sizes must be exact multiples.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.
- **Responsive Design**: All outputs must be responsive and look good on mobile, tablet, and desktop.

## Avoid These (Negative Examples)

- **Colors**: Indigo/blue unless specified; bootstrap-style blue (#0d6efd); purple gradients on white
- **Fonts**: Inter, Roboto, Arial, system fonts, Space Grotesk (overused)
- **Patterns**: Centered cards on gradient backgrounds; generic SaaS layouts; cookie-cutter component styles

Interpret creatively. No design should be the same. Vary themes, fonts, and aesthetics across generations.

## Communicating with Users

### Layout: Use ASCII Wireframes

When discussing layout, present structure as ASCII diagrams:

```
┌─────────────────────────────────────┐
│ ☰  HEADER                       +   │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │     Content Area            │   │
│   └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│   [Input Field]            [Send]   │
└─────────────────────────────────────┘
```

### Animation: Use Micro-Syntax

When discussing animations, use concise notation:

```
element: duration easing [properties] modifiers

Examples:
  fadeIn:   400ms ease-out [Y+20→0, α0→1]
  bounce:   600ms bounce [S0.9→1.1→1]
  hover:    200ms [S1→1.05, shadow↑]
  shake:    400ms [X±5] error
  typing:   1400ms ∞ [α0.4→1] stagger+200ms
  slide:    350ms ease-out [X-100%→0]
```

Notation: `Y` = translateY, `X` = translateX, `S` = scale, `α` = opacity, `R` = rotate, `∞` = infinite, `↑↗` = increase

## Implementation

Match complexity to vision. Maximalist designs need elaborate animations. Minimalist designs need restraint and precision.

Remember: Claude is capable of extraordinary creative work. Commit fully to a distinctive vision.