# Why the Entry Point Is Bounded

This file explains the Bounded Entry Point rules in `SKILL.md`, the Efficient Use of the Agent's Context and The Agent Acts on the Complete Original Text pillars in `SPEC.md`, and the entry-point-size check in `package-check.md`. A run does not need it; read it when questioning or changing those rules.

## The 15,000-Byte Cap

Text past a host's cap is lost without warning, and only the start of a skill survives:

- The [Agent Skills specification](https://agentskills.io/specification) recommends
  "Instructions (< 5000 tokens recommended)" and "Keep your main `SKILL.md` under 500
  lines."
- Claude Code's [skill content lifecycle](https://code.claude.com/docs/en/skills.md#skill-content-lifecycle)
  states: "Claude Code re-attaches the most recent invocation of each skill after the
  summary, keeping the first 5,000 tokens of each. Re-attached skills share a combined
  budget of 25,000 tokens."

The cap is in bytes because no local tokenizer is available. English prose runs about 3.5
to 4.5 bytes per token, so 15,000 bytes stays under 5,000 tokens. Text that is mostly CJK
may use more tokens per byte, and its margin has not been measured.

Both documents above, and the compaction table below, were read in full on 2026-11-17,
with Claude Code 2.1.326 installed.

## Standing Rules and Invocation by Name

Claude Code's [compaction table](https://code.claude.com/docs/en/context-window.md#what-survives-compaction)
re-reads only up to five recently read files and gives a file over 5,000 tokens back as a
path only, so a standing rule kept in a reference can disappear. Claude Code records only
Skill tool and slash-command invocations for re-attachment (verified in the 2.1.326
binary), so a skill reached by reading its `SKILL.md` as a file is not re-attached after
compaction.

## Whole-File Pointers

A file tool cannot jump to a Markdown anchor, so an agent that follows a section pointer
searches or slices the file and reads one fragment, missing the prerequisites and gates
around it. In four scheduled cloud runs, agents reached a skill through a Markdown link to
a section of its `SKILL.md` and read it with `head`, `sed`, or `grep` in place of invoking
it. The 2026-11-17 run read only `/^## Step 1/,/^## Step 3/`, never saw the instruction
written above Step 1, and marked a pull request ready without the check the skill
requires before that step.

## Scripted Checks and Terse Rules

Mechanical rules restated in prose cost context on every invocation and were still not
followed: the package check, on its first runs, found about ten real violations across two
repositories that the prose rules had not prevented.

## Where Reasons Go

Placing a reason is judged by behavior rather than length. Requiring a named case keeps a
reason from staying beside its rule just in case. `SPEC.md` holds core pillars, while a why
explains a rule or principle, so rule reasons do not go to `SPEC.md`. A reason is written where it helps the reader
understand context; a plainly obvious reason, or a rule that is simply the author's
choice, adds nothing and is left out.
