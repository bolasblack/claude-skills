# Changelog

## 2026-11-02

### Let people and agents invoke it on every host

- **Changed:** Remove `disable-model-invocation: true`. A `changed` run opens a PR only when the user asked for the pass; otherwise one commit on a branch plus the diff counts as shipped.
- **Why:** The user chose one invocation behavior on every host. OpenCode ignores the field, so explicit-only behavior could not hold everywhere, and the field stops other skills, agents, and session scheduled tasks from invoking the skill. Without the field a run can start without a request, and opening a PR needs one.

## 2026-10-22

### Follow feature maps into project documentation

- **Changed:** Resolve the feature map through the target skill's pointer into the project checkout, with a fallback for older skills containing a map without a pointer. Keep maps at their declared location and include the resolved map in the edit scope. Stage only reviewed skill and map changes for a `changed` PR.
- **Why:** The user specified project ownership of feature maps with skills pointing to them. The maintenance loop must reach those documents while preserving unrelated work and existing bundled maps.

## 2026-09-17

### Import the verification-skill maintenance loop

- **Changed:** Import `maintain-verification-skill` from Cursor's pstack plugin. Retarget the default target lookup from `.cursor/skills/verify-*/` to `.claude/skills/verify-*/` with `.agents/skills/verify-*/` noted for Codex and pi. Add a serial fallback for hosts without subagents, constrain the `changed` PR to a fresh branch staging only the verification skill's directory with a local-commit fallback where no PR workflow exists, keep evidence artifacts out of the PR, and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill as the upkeep companion to `create-verification-skill`. The lookup path must match where the local generator writes. The import audit found the source wave assumed subagent availability, the `changed` outcome assumed a PR workflow and push rights, and the git step had no staging boundary despite the skill's own edit-scope rule.
