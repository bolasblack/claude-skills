# Distribution

Treat each harness and product surface as a separate compatibility surface. Before
choosing a package layout or writing installation guidance, resolve these decisions
through [Harness Research](../HARNESS-RESEARCH.md):

| Decision | Establish |
|---|---|
| Scope | Repository or project, personal, workspace or organization, and the owner of each installation |
| Delivery | Folder, archive, plugin or marketplace, API or SDK, and the exact artifact each surface consumes |
| Discovery and invocation | Current location or enablement path, selection mode, and any session reload requirement |
| Update lifecycle | Who publishes updates, whether recipients receive them, and which version identifier is authoritative |
| Validation | Portable and target validators, clean-install procedure, and representative behavior cases |

Record exact current paths, commands, UI steps, and host behavior in the task evidence
and in a target-specific release artifact only when its users need them. A folder on
disk or a validator pass does not prove that an active session discovered the skill;
test the exact built artifact independently on every claimed surface.

### Repository and Standalone Distribution

- Use a repository-level README for a collection and a skill-local README for an
  independently distributed skill's human-facing installation or compatibility notes.
- Keep runtime instructions in `SKILL.md`; do not duplicate them in a README.
- Keep independently distributed release artifacts, dependencies, and the Skill
  Composer changelog inside the skill folder.
- Produce only the delivery artifacts the verified target consumes.
- Link from MCP documentation when the skill enhances that MCP.

### Positioning Your Skill

How you describe your skill determines whether users understand its value and actually try it. When writing about your skill — in your README, documentation, or marketing — keep these principles in mind.

**Focus on outcomes, not features:**

Good: *"The ProjectHub skill enables teams to set up complete project workspaces in seconds — including pages, databases, and templates — instead of spending 30 minutes on manual setup."*

Bad: *"The ProjectHub skill is a folder containing YAML frontmatter and Markdown instructions that calls our MCP server tools."*

**Highlight the MCP + skills story:**

*"Our MCP server gives the agent access to your project system. Our skills teach the agent your team's planning workflow. Together, they provide consistent tool-assisted project management."*

### Document in Your MCP Repo

If you maintain an MCP server, link to your skills from the MCP documentation:

- Link to skills from MCP documentation
- Explain the value of using both together
- Provide a quick-start guide that covers MCP setup and skill installation
