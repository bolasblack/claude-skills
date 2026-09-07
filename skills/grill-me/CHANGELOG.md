# Changelog

## [Unreleased]

### Clarify the self-contained interview workflow

- **Changed:** Track decision dependencies, look up available facts, ask one question with a recommendation at a time, and finish with a summary of consequential decisions and remaining uncertainties. Reuse decisions and confirmation already supplied by the user.
- **Why:** The local skill must remain independently usable while incorporating the upstream decision-tree approach. Explicit dependency handling and a stopping condition keep the interview focused on choices that affect the user's plan.
