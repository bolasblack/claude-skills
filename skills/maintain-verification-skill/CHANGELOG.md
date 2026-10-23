# Changelog

## [Unreleased]

### Import the verification-skill maintenance loop

- **Changed:** Import `maintain-verification-skill` from Cursor's pstack plugin. Retarget the default target lookup from `.cursor/skills/verify-*/` to `.claude/skills/verify-*/` with `.agents/skills/verify-*/` noted for Codex and pi. Resolve the feature map through the target skill's pointer into the project checkout, with a fallback for older skills containing a map without a pointer. Keep maps at their declared location and include the resolved map in the edit scope. Add a serial fallback for hosts without subagents, constrain the `changed` PR to a fresh branch staging only reviewed skill and map changes with a local-commit fallback where no PR workflow exists, keep evidence artifacts out of the PR, and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill as the upkeep companion to `create-verification-skill`, and specified project ownership of feature maps with skills pointing to them. The maintenance loop must reach those documents while preserving unrelated work and existing bundled maps. The lookup path must match where the local generator writes. The import audit found the source wave assumed subagent availability, the `changed` outcome assumed a PR workflow and push rights, and the git step had no staging boundary despite the skill's own edit-scope rule.
