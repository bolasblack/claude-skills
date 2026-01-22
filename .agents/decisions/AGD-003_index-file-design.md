---
title: "AGD Index File Design"
description: "Index files use grep-friendly format with symbolic relationship markers"
tags: skills/agent-centric
---

## Context

AGD files can have relationships (updates, obsoletes). We needed a way to quickly search these relationships without reading all files. Initial design had separate files (INDEX-OBSOLETES.md, INDEX-UPDATES.md), but this was consolidated.

## Decision

### Single Relations Index

Use one file `INDEX-AGD-RELATIONS.md` for all AGD relationships:

```
decisions/AGD-005_new.md -(o)-> decisions/AGD-001_old.md
decisions/AGD-003_update.md -(u)-> decisions/AGD-001_original.md
```

### Symbolic Markers

- `-(o)->` : obsoletes relationship
- `-(u)->` : updates relationship

### Path Format

Paths are relative to `.agents/` directory:
- `decisions/AGD-001_name.md` (not just `AGD-001_name.md`)

### Tags Index

Separate file `INDEX-TAGS.md`:

```
decisions/AGD-001_name.md: #tag1, #tag2
```

## Consequences

**Benefits:**
- Single `grep "AGD-001" INDEX-AGD-RELATIONS.md` finds all relationships
- Symbolic markers are visually distinct and grep-able
- Consistent path format across all indexes

**Search patterns:**
```bash
# Find what AGD-001 obsoletes or is obsoleted by
grep "AGD-001" .agents/INDEX-AGD-RELATIONS.md

# Find only obsoletes relationships
grep "-(o)->" .agents/INDEX-AGD-RELATIONS.md

# Find by tag
grep "#tagname" .agents/INDEX-TAGS.md
```
