# Changelog

## [Unreleased]

### Import the verification-skill generator

- **Changed:** Import `create-verification-skill` from Cursor's pstack plugin with its feature-map example references. Retarget the generated skill's output path from `.cursor/skills/verify-<app>/` to `.claude/skills/verify-<app>/` and note the `.agents/skills/` alternative for Codex and pi. Require the generated Launch section to name env vars rather than copy secret values, require the Evidence section to use a gitignored or out-of-repo artifact path, rename the "control skill" trigger phrase to "verification skill", and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill and its `maintain-verification-skill` companion. This repository installs into Claude Code, Codex, OpenCode, and pi, whose project skill directories differ. The import audit found that the generated skill is committed to the repo while its Launch section documents env vars and auth, and that evidence artifacts defaulted to a tracked relative path, so both needed an explicit secrets and version-control rule. The upstream trigger phrase used vocabulary that never appears in the skill body.
