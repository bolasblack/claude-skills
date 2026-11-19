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

When a branch needs only one section of a reference, read [package-check.md](package-check.md) in full and apply its whole-file-pointers choices.

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

- A script uses only its runtime's standard library. Add a dependency, or require a runtime the environment does not already provide (such as bun), only when the skill's author explicitly allows it, and document it with the environments the script supports.
- Include helpful error messages, validate inputs, and handle expected edge cases.
- Use portable forward-slash paths in instructions and code unless the target is explicitly platform-specific.
- Add executable permissions and a shebang when the script is meant to run directly; neither is required for every bundled source file.
- Red-green loop, replaced by the `tdd` skill when available: run the public-seam test and preserve its observed failure before writing the implementation; then make the minimum implementation change and rerun the same test to green. Writing the test and implementation together and calling the first green run red-green evidence does not count.
- The language follows the environment the skill supports. When every claimed environment provides Python and no native runtime is already selected, Python is a reasonable default for a standalone portable helper; a target-specific skill prefers its environment's runtime. When the claimed environments share no runtime, keep a portable manual path or provide tested environment adapters.
- A script that checks or validates something checks only what it can decide exactly; a rule that needs judgment, or could be checked only by matching wording, stays in the instructions, because a wording check rewards the phrase, not the behavior. A false positive is a bug: run a new or changed check against the real inputs at hand before it ships (for a package check, every real skill in the repositories at hand), and judge each new finding real or false.
- A script's output is written for an agent to read and act on: one fact per line behind a stable prefix, the facts the next decision needs (such as a target file's size), a final result line, and exit codes that separate pass, findings, and a usage error. Prefixes and exit codes stay stable, so the output can be filtered and scripted. When it reports that something fails a requirement the skill sets, it states this run's facts (what was checked, what was found, and where) and points to the file in the skill that holds the requirement and its explanation; one pointer for the whole run is enough. It carries no reason of its own, not even a short faithful one, because an agent acts on the reason in front of it, skips the explanation, and takes a shortcut that gets the fix wrong. The pointed-to text exists and explains enough for the author to judge the fix. The output does not list fixes inline, because an agent takes the first one mechanically.
- For a worked example of these output rules, run Skill Composer's own `scripts/check-skill.py` on a skill or read its docstring; model a new script on it rather than copying it. One copy of the package check lives in Skill Composer and is never copied into a skill it checks.
- Retain public-seam tests with the script and run them on every environment the skill claims to support.
- When a script is a harness enhancement rather than a declared requirement, provide and test a portable manual fallback for the core behavior.
