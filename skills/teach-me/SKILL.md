---
name: teach-me
description: Explain an unfamiliar topic to a beginner with a visual HTML explainer. Use when the user asks to learn a concept from scratch, requests ELI5, or wants a simple picture-led explanation.
license: Apache-2.0
---

<!-- Modified from the upstream eli5 skill. See README.md for attribution and CHANGELOG.md for local changes. -->

# Teach Me

Explain the topic to someone who has no background in it, while respecting any knowledge or learning goal the user has already stated.

Use the topic supplied in the request or established in the conversation. If no topic is identifiable, ask what the user wants to learn.

Create one focused HTML explainer with large illustrations and few words. Build the explanation in a short sequence from the basic idea to a concrete example. Define necessary terms when they first appear; use analogies only when they preserve the important relationships.

Keep this a focused introduction to the requested topic. Extend it into a course, exercises, or a quiz only when the user asks.

Preview the rendered explanation when a suitable tool is available. Deliver the HTML through the host's artifact view, or save it as a file and provide a link. If neither artifact nor file delivery is available, present the same visual explanation with concise captions in the conversation.

## Working with show-me

This skill owns the learner's starting point and the explanation sequence. It works independently. When the user also requests `show-me` and that skill is available, use its visual forms within the lesson; the explanation should still suit the learner.
