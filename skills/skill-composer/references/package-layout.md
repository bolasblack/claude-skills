# Package Layout

## Directory Structure Patterns

Every portable package root contains a file named exactly `SKILL.md`. Its parent
directory matches the portable `name` field and therefore follows the same lowercase
letter, digit, and hyphen constraints. Keep runtime instructions in `SKILL.md`, lookup
material in directly linked references, executable resources in `scripts/`, and output
templates or media in `assets/`. Add human-facing, maintainer, license, and release
files only when their admission or distribution condition applies; keep all required
dependencies and notices inside a standalone artifact.

### Minimal (Single File)

```
skill-name/
└── SKILL.md
```

All instructions in one file. Best for focused, simple skills.

### With References

```
skill-name/
├── SKILL.md
└── references/
    ├── api-guide.md
    └── examples.md
```

Core workflow in SKILL.md. Technical details and examples in references/.

### With Scripts

```
skill-name/
├── SKILL.md
├── references/
│   └── api-guide.md
└── scripts/
    ├── process.py
    └── validate.sh
```

Scripts for programmatic validation and utilities. Add `chmod +x` and a shebang only when a script is intended to run directly.

### Full-Featured

```
skill-name/
├── SKILL.md
├── references/
│   ├── api-guide.md
│   └── examples.md
├── scripts/
│   ├── process.py
│   └── validate.sh
└── assets/
    ├── template.json
    └── report-template.md
```

Maximum organization. Assets for templates, fonts, icons used in output.

### Script Requirements

Apply [Environment-Native Automation](../SKILL.md#environment-native-automation) before these low-level packaging checks.

- Keep scripts self-contained or document every dependency and supported environment.
- Include helpful error messages, validate inputs, and handle expected edge cases.
- Use portable forward-slash paths in instructions and code unless the target is explicitly platform-specific.
- Add executable permissions and a shebang when the script is meant to run directly; neither is required for every bundled source file.
- Run the public-seam test and preserve its observed failure before writing the implementation; then make the minimum implementation change and rerun the same test to green. Writing the test and implementation together and calling the first green run red-green evidence does not count.
- When every claimed environment provides Python and no native runtime is already selected, Python's standard library is a reasonable default for a standalone portable helper; a target-specific skill prefers its environment's runtime. When the claimed environments share no runtime, keep a portable manual path or provide tested environment adapters.
- Retain public-seam tests with the script and run them on every environment the skill claims to support.
- When a script is a harness enhancement rather than a declared requirement, provide and test a portable manual fallback for the core behavior.

## Exceptional Maintainer Specifications

The [Agent Skills specification](https://agentskills.io/specification#directory-structure) permits additional package files but assigns no portable meaning to `SPEC.md`. Skill Composer therefore treats it as an exceptional convention, reached through an explicit conditional pointer rather than assumed harness behavior. The default package has no `SPEC.md`.

Add `SPEC.md` only when every condition holds:

1. An explicit user requirement, repository rule, or authoritative product contract supplies at least one current requirement and the reason it must survive.
2. The requirement is stable across plausible implementation and harness changes.
3. It constrains modification or review, while ordinary skill execution does not need it.
4. A future rewrite could appear locally correct while silently violating it, and a separate maintenance contract materially reduces that risk.

Put principles, decision rules, routing, and completion criteria needed during normal execution in `SKILL.md`. Put branch-only lookup material in a referenced file and past changes in `CHANGELOG.md`. Skill importance, size, or complexity does not satisfy the admission test, and the absence of `SPEC.md` is the expected result for most skills.

A qualifying `SPEC.md` stays short and current-state. For every retained requirement, name the invariant, its enduring reason or concrete failure mode, and any validity boundary. Keep workflow steps and release narration in their runtime and history owners. In `SKILL.md`, add a pointer that loads the file before modifying or reviewing that skill itself; packaging the file alone does not make an agent read it.

A skill whose principles define every run, or whose routing rules are the workflow,
keeps those requirements in `SKILL.md` and does not qualify.
