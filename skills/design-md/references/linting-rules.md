# DESIGN.md Linting Rules

Source: `https://stitch.withgoogle.com/docs/design-md/linting-rules`

The `@google/design.md` linter runs 8 rules against a parsed `DESIGN.md` file. Each rule produces findings with a fixed severity: `error`, `warning`, or `info`.

## Rule summary

| Rule | Severity | What it checks |
|------|----------|----------------|
| `broken-ref` | error | Token references that do not resolve; unknown component sub-token property names |
| `missing-primary` | warning | Colors defined but no `primary` exists |
| `contrast-ratio` | warning | Component `backgroundColor`/`textColor` pairs below WCAG AA 4.5:1 |
| `orphaned-tokens` | warning | Color tokens defined but never referenced by a component |
| `missing-typography` | warning | Colors defined but no typography tokens exist |
| `section-order` | warning | Recognized markdown sections out of canonical order |
| `missing-sections` | info | Optional `spacing` or `rounded` absent |
| `token-summary` | info | Count of tokens defined per section |

## broken-ref

Severity: error

Detects token references such as `{path.to.token}` that do not resolve to any defined token in YAML front matter. Also flags unknown component sub-token property names.

Triggers when:

- A component references a missing token path, for example `{colors.accent}` when no accent color is defined.
- A component uses a property name outside the recognized set.

Recognized component properties:

- `backgroundColor`
- `textColor`
- `typography`
- `rounded`
- `padding`
- `size`
- `height`
- `width`

Resolution:

- Define the missing token.
- Correct the reference path.
- Use a recognized component property.

## missing-primary

Severity: warning

Warns when `colors` contains entries but none is named `primary`.

Without `primary`, agents will auto-generate key colors, reducing control over the palette.

Resolution: add a `primary` entry to `colors`.

## contrast-ratio

Severity: warning

Checks WCAG contrast ratios for component `backgroundColor` and `textColor` pairs.

Triggers when a component defines both `backgroundColor` and `textColor`, and the resolved color pair has contrast below 4.5:1.

Resolution: adjust the background or text color to meet WCAG AA 4.5:1.

## orphaned-tokens

Severity: warning

Identifies color tokens defined but never referenced by any component.

Only fires when at least one component is defined.

Resolution:

- Reference the token in a component.
- Remove the token if it is no longer needed.

## missing-typography

Severity: warning

Warns when colors are defined but no typography tokens exist.

Without typography tokens, agents will fall back to their own font choices.

Resolution: add at least one typography token, for example `body-md`.

## section-order

Severity: warning

Warns when recognized markdown sections appear out of canonical order.

Expected order:

1. `Overview`
2. `Colors`
3. `Typography`
4. `Layout`
5. `Elevation & Depth`
6. `Shapes`
7. `Components`
8. `Do's and Don'ts`

Aliases are resolved before checking:

- `Brand & Style` for `Overview`
- `Layout & Spacing` for `Layout`
- `Elevation` for `Elevation & Depth`

Resolution: reorder sections to match canonical order.

## missing-sections

Severity: info

Notes when optional token sections such as `spacing` or `rounded` are absent from a file that already defines other tokens.

These sections are not required, but their absence means agents fall back to defaults.

Resolution: add `spacing` or `rounded` if explicit control matters.

## token-summary

Severity: info

Reports how many tokens are defined in each section.

No fix needed.

## Manual validation checklist

Use this when the CLI is unavailable:

- [ ] All token references resolve.
- [ ] Component sub-token property names are recognized, or unknown properties are reported as warnings.
- [ ] `colors.primary` exists when colors are defined.
- [ ] Component `backgroundColor`/`textColor` pairs meet 4.5:1 contrast.
- [ ] Defined color tokens are referenced by components when components exist, or intentionally left unused.
- [ ] Typography tokens exist when colors exist.
- [ ] Recognized markdown sections are in canonical order.
- [ ] Optional `spacing` and `rounded` are present when explicit control matters.
