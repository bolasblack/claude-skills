# Maintainer Specification (`SPEC.md`)

Read this file in full before adding, changing, or reviewing a skill's `SPEC.md`. Most skills have none, and that is the expected result.

`SPEC.md` holds a skill's core pillars: the principles for which its author, the person who owns the skill, wants the skill at all, such as "the skills it generates work in every harness". Because they are pillars, they must survive any rewrite. A `SPEC.md` is not a summary assembled from the skill's rules: the pillars come first, and the more specific, practicable rules in `SKILL.md` and the references derive from them. One pillar may also show in several other entries. It is not a record of everything currently believed correct, and it is not frozen: an entry is added, revised, or removed when the author decides, never silently by an agent. The [Agent Skills specification](https://agentskills.io/specification#directory-structure) permits extra package files but gives `SPEC.md` no meaning, so link it from `SKILL.md` with a pointer that loads it before modifying or reviewing that skill itself; packaging the file alone does not make an agent read it.

## Admission Test

In a simple skill, `SKILL.md` already records nothing but its core pillars: its rules are the pillars, so a `SPEC.md` would repeat it. A skill whose role is complex plays several parts, serves several kinds of situation, or carries many rules and branches, so its pillars are no longer visible from its rules. `SPEC.md` is where such a skill states its pillars. Skill Composer is one: it creates, reviews, checks, and releases other skills for several harnesses. Others of the kind maintain tooling across repositories whose setups differ, perform several kinds of irreversible operation, or advise across many kinds of decision.

Whether a role is complex is the author's judgment, not a count of branches, files, or bytes. Size and importance do not make a role complex: a long skill with one simple job still shows its pillars.

Add `SPEC.md` only when every condition holds:

1. The skill's role is complex.
2. The author holds at least one current principle as a core pillar of the skill, whether stated by the author, written in a repository rule or product contract, or adopted from elsewhere.
3. The principle is stable across plausible implementation and harness changes.
4. A rewrite or review must preserve it, and since the rules do not show it, a rewrite could appear locally correct while silently violating it.

A set of runtime rules or routing is not an entry: those stay in `SKILL.md`, and an entry names only the principle behind them.

## Extracting Entries

1. **Collect candidates.** Look first at how the author shaped the skill: what they want it to be at a level above any one rule, corrections made more than once in the same direction, and points they emphasised. Repeated corrections are a good test of what belongs: a principle the author keeps steering the skill back to is likely a pillar. A candidate can also be a principle the author adopted from elsewhere (another project, skill, or source) or one you propose.
2. **Test each candidate.** Keep it only when all four hold: the author would insist on it if the skill were rewritten from scratch; it is a property that must stay true, not the mechanism that achieves it today; a rewrite could look locally correct while breaking it; and it is a principle, not a rule set (when it shapes ordinary runs, `SKILL.md` keeps the rules that apply it and the entry records only the principle). A useful test: several existing rules read as applications of the candidate.
3. **Let the author pick.** Propose a short list, each candidate with what it rests on (the author's words, the source it came from, or your reasoning), and ask the author to keep or cut each one. Only what the author keeps enters. Expect most candidates to be cut; that is the method working.
4. **Write each kept entry** in the shape below: the invariant, a **Why:** from the author saying why they want it in this skill (it may quote the author or, for an adopted principle, name its source), and its validity boundary when there is one. An entry has a Why when the author's reason tells the reader something, not when it is obvious or just their choice; if you do not know it, ask, and do not invent one. An entry kept without a stated reason has no Why yet.

**Done when:** every entry is one the author kept, each has a present-tense invariant, and each Why came from the author or a cited source.

## Shape

A made-up skill's whole `SPEC.md`:

````markdown
# Recipe Scaler Specification

## Works Offline

The skill scales and converts recipes using only what ships in its package. It calls
no network service.

**Why:** The user runs it on a kitchen tablet that has no network access.

## Measurable Quantities

Scaled amounts are fractions a cook can measure, such as 1/3 cup, unless the user asks
for decimals. This holds for home kitchens; a lab or catering use would revisit it.

**Why:** Home cooks measure with cups and spoons marked in fractions.

## The Original Stays Untouched

The skill writes the scaled recipe as a new file and never edits the source recipe.

**Why:** The user's family recipes exist only as these files.
````

Each `##` section is one property in the present tense, one or two paragraphs, ending in one **Why:**. An entry may add one sentence before the Why naming the rules that apply it today, marked as today's application; it is not part of the pillar. A `SPEC.md` holds the core of the core, so its entries are few. A draft with numbered rules, source labels, or transcript line numbers is a rule ledger, not a `SPEC.md`.

## Not `SPEC.md` Material

- Reasons for runtime rules: they sit beside the rule or in a reference behind a why link; before placing one, read [rule-reasons.md](rule-reasons.md) in full. A pillar's own Why stays in its entry; when another place needs the same explanation, it is written once in a reference file that both link.
- Where a rule came from: per-rule provenance, citations, transcript lines.
- Rejected alternatives; a changelog entry's Why may mention one when it explains the change.
- Open questions: ask the user; an unanswered question stays out.
- Which file owns what: the layout and the pointers in `SKILL.md` already show it.
- Acceptance checklists: tests and the package check enforce what can be checked.
- Workflow steps and lookup material: `SKILL.md` and its references. Past changes: `CHANGELOG.md`.

When reviewing a `SPEC.md`, report each entry the author did not adopt and any material from this list, and propose the cut to the author rather than making it silently.
