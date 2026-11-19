# Writing Instructions

Read this file in full before writing instructions in Step 5 when the `writing-for-agents` skill is unavailable; that skill replaces it when available. These rules stay a short core, not a copy of that skill.

- Put standing rules before the workflow, must-follow gates first; the agent acts on what it reads first.
- End every step on a completion criterion the agent can check, and make it demand the whole job: "every changed file is accounted for", not "produce a list". A partial criterion passes a partial job.
- State the behavior you want. Keep a prohibition only for a hard guardrail, and pair it with what to do instead.
- Leave out what the environment already shows, such as config files, `--help` output, or the directory layout.
- Cut what the model does by default: if deleting a sentence changes no behavior, delete the whole sentence.
- Inline what every branch needs; put what only some branches need behind a pointer.
- Keep a concept's definition, rules, and caveats under one heading, with one term per concept; a second name reads as a second concept.
