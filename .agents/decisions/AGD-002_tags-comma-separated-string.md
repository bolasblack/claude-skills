---
title: "Tags Use Comma-Separated String Format"
description: "AGD frontmatter tags field uses comma-separated string instead of YAML array"
tags: skills/agent-centric
---

## Context

AGD files have a `tags` field in frontmatter. We needed to decide on the format for this field. Options considered:

1. YAML array: `tags: [tag1, tag2]` or `tags:\n  - tag1\n  - tag2`
2. Comma-separated string: `tags: tag1, tag2`

## Decision

Use comma-separated string format:

```yaml
tags: core, api, database
```

**NOT** YAML array:

```yaml
tags:
  - core
  - api
  - database
```

## Consequences

**Benefits:**
- Simpler parsing in bash/python scripts without YAML parser
- Single-line format is more compact
- Easy to split: `tags.split(',')` in Python, or `cut -d,` in bash

**Trade-offs:**
- Tags cannot contain commas (acceptable limitation)
- Less "YAML-native" but still valid YAML
