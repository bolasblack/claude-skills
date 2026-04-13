# Ecosystem Detection and Package Normalization

Use this file when the install request does not already make the ecosystem obvious.

## Ecosystem Mapping

| User request / command pattern | Ecosystem for `check-deps.py` | Notes |
|---|---|---|
| `npm install`, `npm ci`, `npm add`, `pnpm install`, `pnpm add`, `yarn install`, `yarn add`, `bun install`, `bun add` | `npm` | Includes scoped packages like `@scope/name@1.2.3` |
| `pip install`, `pip3 install`, `pip install -r`, `uv add`, `uv pip install`, `uv sync`, `poetry add`, `poetry install` | `pypi` | Convert Python version syntax to `name@version` when possible |
| `cargo add` | `cargo` | Use crate name plus exact version when available |

## Manifest and Lockfile Hints

If the user request is ambiguous, inspect nearby files:

- npm ecosystem: `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`
- pypi ecosystem: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `uv.lock`, `poetry.lock`
- cargo ecosystem: `Cargo.toml`, `Cargo.lock`

If multiple ecosystems exist in the same repository, ask which environment the user wants to change before running the install.

## Package Spec Normalization

Normalize the requested dependency into the checker's expected input.

### npm family

- Keep `name@version` as-is.
- Scoped packages should remain `@scope/name@version`.
- If the user did not specify a version, use `name` and state that the scan was not pinned.

### PyPI family

Examples:

- `httpx==0.28.1` -> `httpx@0.28.1`
- `pydantic>=2.0` -> use the most specific resolved version you can determine, otherwise `pydantic`
- `uv add ruff==0.11.5` -> `ruff@0.11.5`
- `poetry add fastapi@0.115.12` -> `fastapi@0.115.12`

Prefer exact versions. If the request is a range and no exact version is available yet, run an unpinned scan and say so explicitly.

### cargo

Examples:

- `cargo add serde --vers 1.0.217` -> `serde@1.0.217`
- `cargo add anyhow` -> `anyhow`

## Unsupported Installers

Do not silently treat these as supported:

- OS package managers: `apt`, `brew`, `yum`, `dnf`, `apk`, `pacman`
- Other language ecosystems not covered by the checker: `gem`, `composer`, `go get`, `nuget`, `dotnet add package`

For unsupported ecosystems, stop and tell the user the bundled checker cannot currently screen that dependency source reliably.
