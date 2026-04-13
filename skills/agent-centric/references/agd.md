# AGD Reference

Technical specifications for AGD (Agent-centric Governance Decision) files.

## Purpose

AGD exists to preserve a stable, growing history of project decisions.

Each AGD should act as a durable reference for why some code, convention, or process was chosen at the time. When revisiting the project later, the goal is to quickly recover the original rationale and see whether the decision still stands, was updated, or was obsoleted.

"Decision history tree" is a useful intuition, but the actual structure is closer to a decision history graph because AGDs can have multiple `updates`, `obsoletes`, and `related` links.

## Frontmatter Fields

| Field          | Required | Description                                                  |
| -------------- | -------- | ------------------------------------------------------------ |
| `title`        | Yes      | Decision title                                               |
| `description`  | Yes      | Brief description                                            |
| `tags`         | No       | Comma-separated tags (must be in config.json tags)           |
| `updates`      | No       | AGD number(s) this decision updates                          |
| `obsoletes`    | No       | AGD number(s) this decision obsoletes                        |
| `related`      | No       | AGD number(s) that are related for reference only            |
| `updated_by`   | No       | **Auto-managed** - AGD number(s) that update this decision   |
| `obsoleted_by` | No       | **Auto-managed** - AGD number(s) that obsolete this decision |

**Note:** `obsoleted_by` and `updated_by` are automatically populated by `generate-index.py` based on reverse references from other AGDs. You only need to specify `updates`, `obsoletes`, and `related` in your new AGD files.

## Relationship Semantics

AGD follows the RFC archival model: existing decision files are preserved, and later AGDs express how decisions evolve.

- **updates**: Extends or modifies, original decision still partially valid
- **obsoletes**: Completely replaces, original decision no longer valid
- **related**: Reference-only connection, similar to RFC `see-also`; does not change validity of either decision

`related` is intentionally **not** reverse-synced into the target AGD frontmatter. Reverse discovery happens through `INDEX-AGD-RELATIONS.md`, while only `updated_by` and `obsoleted_by` are auto-managed reverse fields.

## Assigning AGD Numbers

Find the next available number:

```bash
find "$CLAUDE_PROJECT_DIR/.agents/decisions/" -name "AGD-*" | sed 's/.*AGD-\([0-9]*\).*/\1/' | sort -n | tail -1
```

Then increment by 1. If no files exist, start with AGD-001.

## Referencing in Code

When implementing a decision, reference the AGD number in comments:

```python
# Implementation follows AGD-001
class PostgresRepository:
    ...
```

```typescript
// See AGD-002 for architecture rationale
export class UserService {
    ...
}
```
