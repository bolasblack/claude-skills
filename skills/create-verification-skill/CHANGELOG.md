# Changelog

## 2026-11-02

### Require a usable launch and honest proof

- **Changed:** Sync upstream PR #573. Launch must reach a usable state from an empty data directory, including migrations and seed data, and "a port answering" no longer counts as ready. A journey whose seed data lacks a precondition reports a failure with the reason in `Gotchas`, or the nearest section of a retained map, and is never weakened to pass. A proof run in a stand-in for the real target lists the setup steps the target will not do, and those steps stay unverified.
- **Why:** Upstream measured a database socket up at 3 seconds while init finished at 19 seconds, so a generated skill could drive the app 16 seconds too early and fail on state that did not exist yet.

### Let people and agents invoke it on every host

- **Changed:** Remove `disable-model-invocation: true`, and narrow the description to explicit requests.
- **Why:** The user chose one invocation behavior on every host. OpenCode ignores the field, so explicit-only behavior could not hold everywhere, and the field stops other skills, agents, and session scheduled tasks from invoking the skill.

## 2026-10-22

### Move feature maps into project documentation

- **Changed:** Reuse the project's documented feature map or seed `docs/features/`, linking to it conditionally from the generated skill and existing test-planning guidance. Keep feature-specific state, actions and outcomes in the map and shared verification workflow in the skill.
- **Why:** The user specified that feature maps belong to the project with skills pointing to them. Project ownership lets investigation, planning and verification share one map.

## 2026-09-17

### Import the verification-skill generator

- **Changed:** Import `create-verification-skill` from Cursor's pstack plugin with its feature-map example references. Retarget the generated skill's output path from `.cursor/skills/verify-<app>/` to `.claude/skills/verify-<app>/` and note the `.agents/skills/` alternative for Codex and pi. Require the generated Launch section to name env vars rather than copy secret values, require the Evidence section to use a gitignored or out-of-repo artifact path, rename the "control skill" trigger phrase to "verification skill", and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill and its `maintain-verification-skill` companion. This repository installs into Claude Code, Codex, OpenCode, and pi, whose project skill directories differ. The import audit found that the generated skill is committed to the repo while its Launch section documents env vars and auth, and that evidence artifacts defaulted to a tracked relative path, so both needed an explicit secrets and version-control rule. The upstream trigger phrase used vocabulary that never appears in the skill body.
