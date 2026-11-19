# Skill Composer Specification

## Depends on Nothing the Package Cannot Guarantee

A skill's required behavior runs on what its package carries. It does not depend on a
host-only feature, a sibling skill, or the source repository. An enhancement is optional,
names its host, and has a tested fallback. A skill depends on a host only when it
declares that host as a requirement and claims no broader compatibility.

Today's application: the portable core and harness enhancements in `SKILL.md`, and the
bundled writing rules and red-green loop, which a sibling skill replaces only when it is
installed.

**Why:** The user owns the cross-harness distribution promise. Without this invariant, a
convenient host enhancement can silently become the sole owner of required behavior
while the package still appears portable. The user also decided that a third-party skill
must not carry Skill Composer's writing quality, because its content is outside Skill
Composer's control.

## Mechanical Work Is a Script

What can be done mechanically is a tested script, not prose telling the agent to do it;
prose states only what needs judgment. A script's output is written for an agent to act
on, and it points to the rule text instead of carrying a simplified reason. A script
uses only its runtime's standard library unless the skill's author explicitly allows a
dependency; the language follows the environment the skill supports.

Today's application: Environment-Native Automation in `SKILL.md`, the Script
Requirements in `references/package-layout.md`, and Skill Composer's own package check,
`scripts/check-skill.py`, run on every skill it creates, updates, reviews, or releases.

**Why:** The user requires that whatever can be automated is implemented as a script.
An agent that carries out mechanics from prose re-derives them on every run and drifts.
The user also wants scripts designed for an agent to read, with no simplified failure
reason, so the agent reads the skill's rule file itself. The user holds that every
skill's scripts use only the standard library by default, unless the skill's author
explicitly says a script may depend on something, such as bun.

## Efficient Use of the Agent's Context

The agent gets the complete information it needs and nothing it does not need. This
shows in three other pillars: mechanics leave the prose for scripts (Mechanical Work Is a
Script), explanations sit in separate files read whole and only when needed (The Agent
Acts on the Complete Original Text), and ordinary runs do not load maintenance knowledge
(Maintenance Knowledge Travels with the Package).

Today's application: the 15,000-byte cap on `SKILL.md`, one discriminating trigger per
invocation branch in the description, and a reason kept beside its rule only for a named
case.

**Why:** The user wants the agent's context used efficiently, and wants a generated
`SKILL.md` and its trigger text to stay a reasonable size, so they do not take too much
of the agent's context window. The evidence for the cap's number is in a reference
([why](references/bounded-entry-point.md)).

## The Agent Acts on the Complete Original Text

The agent acts on the rule text itself, never on a fragment or a paraphrase of it.
Completeness pairs with efficiency: each file the agent reads is read whole, and what it
does not need sits in a separate file.

Today's application: pointers target whole files read in full, another skill is invoked
by name instead of having its file read, a script points to the rule text instead of
restating it, and rule explanations sit in their own reference files.

**Why:** The user notes that an AI may tend to read only part of a skill, and an
incomplete read can cause problems. The user requires, with emphasis, that another skill
is reached through the proper mechanism, not by reading its file directly. In the user's
view, pointing the agent to the full rule text keeps it from taking a shortcut and making
a mistake.

## Maintenance Knowledge Travels with the Package

Knowledge for maintaining a skill ships inside its package and costs ordinary runs
nothing. A skill with releases of its own or independent distribution carries a
`CHANGELOG.md`, outside `SKILL.md`, recording what changed and why; dates are the
default and versions are opted into. `SPEC.md` is rare, holds only a skill's core
pillars, and is loaded only when the skill itself is maintained.

**Why:** Maintainer constraints and release rationale must survive a rewrite or the skill
leaving its repository, without ordinary invocations paying for them. The user finds
version numbers unnecessary in their way of working and expects the same for many
others.

## Nothing Is Invented

A reason, source, or claim is written only when it is known; otherwise it is asked for or
marked `unknown`.

Today's application: `unknown` rows in the validation ledger, fresh harness research for
target claims, the changelog's Evidence gate, and asking the author for a rule's reason.
