# Agent Workflow

This repo uses a living suggestions list with clearly defined sections. Every time we make changes, we update suggestions and tests accordingly.

## Operating Principles

- Always update `SUGGESTIONS.md` after changes: tick completed items and backfill with new ideas to maintain the minimum per section.
- Maintain sections: `Core Functionality`, `Configuration & Defaults`, `Security`, `Formatting`, `Efficiency/Readability/Docs`, `New Features`, `Tests`, and a `Completed` section at the bottom.
- Each active section must contain a minimum of two checklist items at all times (3 is ideal, but 2 is acceptable).
- Move completed items to the `Completed` section (do not leave them in their original section) and add new suggestions to keep the minimum per active section.
- Add or update unit tests for any behavior changes introduced.
- Keep entries formatted as an indented checklist, separated by blank lines.

## Checklist Formatting

- Use two-space indentation followed by `[ ]` or `[x]`.
- Separate each item with a blank line (double newline between items).
- Example:

  [ ] S142 - CLI: Provide small diagnostics CLI (print config, send test email, show templates).

## Update Cycle

- On completing a task:
  - Mark it done with `[x]` and move it to the `Completed` section (at the bottom of `SUGGESTIONS.md`).
  - Backfill a new suggestion in the originating section to maintain at least two items.
  - Keep section ordering by relevance/near‑term payoff. No numeric priorities are used.
  - Ensure tests cover the change (add/adjust unit tests as needed).

- On adding a new feature/fix:
  - Create or update suggestions to reflect follow-ups, docs, and tests.
  - Keep the titles concise and action-oriented; include a brief scope in parentheses when helpful.

## Ownership

- Anyone contributing should follow this workflow. PRs should reference the relevant suggestion IDs (e.g., `S142`) and include test updates.
