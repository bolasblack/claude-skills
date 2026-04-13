---
name: dependency-safety-check
description: Screens third-party project dependencies for known vulnerabilities and supply-chain risk before installation using a bundled check-deps.py script. Use when user asks to install, add, update, upgrade, or pin packages with npm, pnpm, yarn, bun, pip, uv, poetry, or cargo, or when deciding whether a package version is safe to install. Do NOT use for OS package managers such as apt, brew, yum, apk, or pacman.
allowed-tools: Bash, Read
compatibility: Requires bash access and python3 or python to run scripts/check-deps.py.
---

# Dependency Safety Check

Run a dependency security screen before installing third-party project packages.

## Critical Rules

- **Always run `scripts/check-deps.py` before installing or upgrading third-party dependencies.**
- **Never silently skip the check because the user seems in a hurry.**
- **If the checker returns `REJECT`, do not install unless the user explicitly overrides the risk.**
- **If the checker returns `REVIEW`, summarize the warnings and ask before proceeding.**
- **If the checker cannot complete because of network/API failures, treat the install as blocked until the user chooses a manual override.**
- **For plain bootstrap installs** like `npm install`, `npm ci`, `pnpm install`, `yarn install`, `bun install`, `pip install -r requirements.txt`, `uv sync`, or `poetry install`, inspect the manifest first and screen the direct dependencies being introduced or changed in this task. If there is no diff, screen the direct dependencies from the manifest before installing.

## Workflow

### 1. Determine ecosystem and target packages

Infer the dependency ecosystem from the user request first. If that is ambiguous, inspect the project files.

Use [references/ecosystems.md](references/ecosystems.md) for command mapping, manifest detection, and package-spec normalization.

Prefer checking **exact versions**. If the user gave a range or no version:

- keep the original request for the eventual install command,
- but convert to the most specific `name@version` form you can determine for the safety check,
- and tell the user when the scan was performed without an exact version.

### 2. Resolve a Python interpreter and script path

Use a Python interpreter explicitly before invoking the checker. Resolve `scripts/check-deps.py` relative to this skill directory; if you are not already running from the skill folder, use an absolute path.

```bash
CHECK_DEPS=/absolute/path/to/this-skill/scripts/check-deps.py

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "Python is required to run scripts/check-deps.py" >&2
  exit 1
fi
```

### 3. Run the checker before installation

Run the bundled script from this skill:

```bash
"$PYTHON_BIN" "$CHECK_DEPS" <pkg[@version]> [more packages...]
"$PYTHON_BIN" "$CHECK_DEPS" --ecosystem pypi <pkg[@version]> [more packages...]
"$PYTHON_BIN" "$CHECK_DEPS" --ecosystem cargo <pkg[@version]> [more packages...]
```

Examples:

```bash
"$PYTHON_BIN" "$CHECK_DEPS" react-router-dom@7.0.2
"$PYTHON_BIN" "$CHECK_DEPS" --ecosystem pypi httpx@0.28.1
"$PYTHON_BIN" "$CHECK_DEPS" --ecosystem cargo serde@1.0.217
```

### 4. Interpret the result

The checker ends with one of these verdicts:

- `PASS` → installation may proceed
- `REVIEW` → summarize the warnings, ask the user, then continue only with approval
- `REJECT` → do not install unless the user explicitly accepts the risk

When reporting back, include:

- ecosystem checked,
- exact packages scanned,
- final verdict,
- the most important findings,
- the install command you plan to run next if approval exists.

### 5. Perform the install only after the screen

Once the safety check has passed or the user has explicitly approved the risk, run the requested package-manager command.

Examples:

- `npm install react-router-dom@7.0.2`
- `pnpm add zod@4.1.0`
- `pip install httpx==0.28.1`
- `poetry add pydantic@2.11.3`
- `cargo add serde@1.0.217`

## Handling Unsupported Cases

- **Unsupported ecosystem**: explain that `scripts/check-deps.py` currently supports npm directly and can also query PyPI/cargo packages through generic advisory sources via `--ecosystem`. If the requested package manager is outside that scope, stop and ask whether the user wants a manual review or an extension of the checker.
- **Bulk manifest installs**: if the dependency list is large, prioritize the dependencies newly introduced or changed in the current task. If no change set is available, scan direct dependencies in manageable batches and summarize the outcome.
- **No exact version available**: run the best possible package-level scan, state the limitation clearly, and prefer pinning a version before installation.
- **Checker failure**: do not proceed automatically. Report the failure and ask whether to retry or override.

## Examples

### Example 1: npm package install

**User says:** "Install `react-router-dom` into this frontend app."

**Actions:**
1. Detect npm ecosystem from `package.json`.
2. Resolve the target version if needed.
3. Run `scripts/check-deps.py` for that package.
4. If verdict is `PASS`, run the install command.

**Result:** Package is installed only after the dependency safety screen completes.

### Example 2: Python dependency upgrade

**User says:** "Upgrade `httpx` in this project."

**Actions:**
1. Detect PyPI ecosystem from `pyproject.toml` or `requirements.txt`.
2. Normalize the check target to `httpx@<resolved-version>` when possible.
3. Run `scripts/check-deps.py --ecosystem pypi ...`.
4. Ask for approval on `REVIEW`; block on `REJECT`.

**Result:** Upgrade proceeds only after the script reports an acceptable result.

### Example 3: Repo bootstrap install

**User says:** "Install project dependencies."

**Actions:**
1. Detect the package manager from manifest files.
2. Inspect the direct dependencies to be installed.
3. Run the checker on the relevant dependency set first.
4. Proceed with install only after the safety gate.

**Result:** Environment setup includes a dependency risk screen instead of blindly installing.

## Version History

- v1.0.0 (2026-04-13): Initial version
