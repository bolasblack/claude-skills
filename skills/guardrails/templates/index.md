# Guardrails

Read this router first, then render only the GRL IDs listed for your task. Do not open rule files directly for ordinary implementation context.

This file is a routing map, not a catalog and not a rule summary. Keep it compact: task or scenario headings, then the IDs to read, in human-curated reading order. Duplicate IDs across rows are expected when a rule applies to several tasks.

## Required Reading by Task

- Add or change a module's public interface
  - GRL-1, GRL-2

- Add or change a dependency between modules
  - GRL-2, GRL-1

- Move a helper between a module internal directory and its entry file
  - GRL-2, GRL-1

<!--
Replace these rows with your repo's real tasks. Rules to keep in mind while editing:
- Every rule ID token anywhere in this file counts as listed, including prose, notes, and examples.
- Review-governed rules (pure review and lint-assisted review) must be listed here.
- Pure-lint rules and retired rules must never appear here.
- No rule summaries, no long detail, no examples, no command snippets containing rule IDs.
-->
