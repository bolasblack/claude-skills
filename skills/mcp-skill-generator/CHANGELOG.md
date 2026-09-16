# Changelog

## [Unreleased]

### Establish independent release ownership

- **Changed:** Introduced `VERSION` as the skill's machine-readable version owner with the maintainer-confirmed initial baseline `0.1.0`, plus a package-local changelog and independent source-release contract.
- **Why:** The generator needs its own release identity, separate from versions of MCP servers recorded in generated or example connection configurations.

## Baseline registration

This skill previously had no recorded skill version. `0.1.0` registers the current
source package for future releases; it does not claim a historical tag or a published
GitHub Release. The example server version in `config.toml` is not the skill version.
