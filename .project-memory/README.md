# Project Memory

Purpose: preserve continuity for the IOI/KOI curriculum project across sessions.

This folder is intentionally structured as a graph of small files. Update it after
meaningful decisions, but do not turn it into a full transcript archive.

File size policy:
- `state.md`: max 120 lines
- `decisions.md`: max 80 lines
- `open-questions.md`: max 80 lines
- `session-log.md`: max 120 lines, newest entries at top
- topic node files: max 80 lines each
- index files: max 120 lines each

When a file approaches its limit, summarize older details into `state.md` and remove
low-value repetition.

Scaling policy:
- Do not grow one large memory file indefinitely.
- When a topic accumulates detail, create a directory under `topics/`.
- Inside each topic directory, create small node files such as `overview.md`,
  `decisions.md`, `questions.md`, `references.md`, or `notes-YYYY-MM-DD.md`.
- Register important nodes in `indexes/memory-map.md`.
- Put machine-readable conventions and templates under `metadata/`.
- Put session-specific notes under `sessions/YYYY-MM-DD.md`.

Default node metadata:
- `id`: stable kebab-case id
- `type`: state, decision, question, topic, reference, session, template
- `status`: active, parked, decided, superseded
- `updated`: YYYY-MM-DD
- `links`: related node ids or paths

Use metadata to connect files. Use prose to explain judgment.
