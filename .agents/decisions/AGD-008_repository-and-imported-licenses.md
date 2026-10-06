---
title: "Repository license and imported upstream licenses"
description: "Work written here is personal use. An imported extension keeps its upstream license and the notices that license requires."
tags: global
---

## Context

This repository publishes two kinds of extensions.

Extensions, scripts, and docs written here share one license. The README states it as personal use. A package that repeats the statement, such as `skills/skill-composer/LICENSE.md`, repeats that same license.

An imported extension is upstream work. Its license is the upstream license, recorded in that extension's directory. `scripts/install.sh` copies the extension directory as the installed artifact, so the license text and the attribution that pertain to the imported files are part of that directory. The collection README names the split; it is not a substitute for the license text in the installed copy.

## Decision

1. Extensions, scripts, and docs written for this repository are under one license: personal use. The repository license statement is that record. Author-written extensions do not each carry a license file.
2. An imported extension keeps the upstream license. The import does not relicense it to personal use.
3. The public license statement names both layers.
4. An import keeps every license text and attribution notice a recipient of the imported files must receive. Apache-2.0 includes a copy of the license in the extension directory. MIT includes the copyright and permission notice. Notices that pertain only to parts the import does not distribute stay out.
5. A file the import modifies carries the change notice the upstream license requires. Apache-2.0 requires a prominent notice on each modified file.
6. When the upstream license forbids this redistribution, the extension is not imported.
7. Plugin metadata, the upstream README and CONTRIBUTING, tests, and CI config stay out of the import once required attribution that lived only there has been copied into the local README or a bundled `NOTICE`.

## Consequences

- The README states personal use for work written here and the upstream license for each import.
- `CONTRIBUTING.md` tells authors they are under personal use, and tells importers to put the upstream license text and pertinent attribution in the extension directory.
- After installation, the extension directory alone is enough for a recipient to read the license terms that apply to that extension.
