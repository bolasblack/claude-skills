# DESIGN.md CLI

Sources:

- Stitch docs: `https://stitch.withgoogle.com/docs/design-md/cli`
- Implementation/tooling source: `https://github.com/google-labs-code/design.md`

If the Stitch page appears empty or only shows the app shell, inspect the nested iframe content; the actual docs may be two iframe layers deep, and the innermost documentation frame URL may change over time.

The official CLI package is `@google/design.md`.

It validates design systems against the spec, catches broken token references, checks WCAG contrast ratios, exports tokens to other formats, and emits structured JSON agents can act on.

## Dependency safety

Do not install this package automatically.

Do not use plain `npx @google/design.md ...` as a read-only check, because it can install the package implicitly.

Safer execution order:

1. Check whether `@google/design.md` is already installed locally or globally.
2. If installed, use the existing command/package.
3. If not installed, validate manually or ask before installing.
4. Before any installation or version pin, run the dependency-safety workflow and get explicit user approval.

## Install

Official docs show:

```bash
npm install @google/design.md
```

On Windows shells, quote the scoped package if needed:

```bash
npm install "@google/design.md"
```

Or direct execution:

```bash
npx @google/design.md lint DESIGN.md
```

Treat both as dependency-sensitive commands unless the package is already present. On Windows, the package may expose a `designmd` script alias. If npm reports `ENOVERSIONS`, treat it as a registry/package-resolution issue and do not retry installation without checking the package metadata.

## Lint

Official command:

```bash
npx @google/design.md lint DESIGN.md
```

Pipe from stdin:

```bash
cat DESIGN.md | npx @google/design.md lint -
```

The linter parses YAML front matter, resolves token references, runs 8 lint rules, and reports findings.

Output defaults to JSON. Exit code is 1 if errors are found, 0 otherwise.

Options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `file` | positional | required | Path to `DESIGN.md` or `-` for stdin |
| `--format` | `json` | `json` | Output format |

Example output shape:

```json
{
  "findings": [
    {
      "severity": "warning",
      "path": "colors",
      "message": "No 'primary' color defined. The agent will auto-generate key colors, reducing your control over the palette."
    }
  ],
  "summary": { "errors": 0, "warnings": 1, "infos": 1 }
}
```

## Diff

Official command:

```bash
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

Reports token-level changes between two files:

- Tokens added
- Tokens removed
- Tokens modified
- Whether the after file has more errors or warnings

Exit code is 1 if regressions are detected.

## Export

Convert `DESIGN.md` tokens to other formats.

Tailwind JSON:

```bash
npx @google/design.md export --format json-tailwind DESIGN.md
```

Tailwind CSS variables:

```bash
npx @google/design.md export --format css-tailwind DESIGN.md
```

DTCG / W3C Design Tokens:

```bash
npx @google/design.md export --format dtcg DESIGN.md
```

Export formats:

- `json-tailwind`: JSON object with colors, fontFamily, fontSize, borderRadius, and spacing mapped from design tokens
- `css-tailwind`: CSS variables for Tailwind-oriented consumption
- `tailwind`: alias for Tailwind JSON in older examples
- `dtcg`: W3C Design Tokens Format Module compliant `tokens.json`

## Spec

Output the current `DESIGN.md` format specification:

```bash
npx @google/design.md spec
npx @google/design.md spec --rules
npx @google/design.md spec --rules-only --format json
```

Useful for injecting spec context into agent prompts.

Options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--rules` | boolean | false | Append active linting rules table |
| `--rules-only` | boolean | false | Output only linting rules table |
| `--format` | `markdown` or `json` | `markdown` | Output format |

## Programmatic API

The linter is available as a TypeScript library:

```ts
import { lint } from '@google/design.md/linter';

const report = lint(markdownString);

console.log(report.findings);
console.log(report.summary);
console.log(report.designSystem);
console.log(report.tailwindConfig);
```
