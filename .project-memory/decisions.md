# Decisions

2026-05-17
- Use `.project-memory` as the hidden project continuity folder.
- Keep memory files intentionally small to force periodic summarization.
- Separate internal project memory from student-facing curriculum files.
- Start with a draft architecture rather than trying to complete the full curriculum at once.

2026-05-18
- Scale memory as many small metadata-bearing nodes instead of a few large files.
- Use `indexes/memory-map.md` as the top-level map for internal memory.
- Use `topics/` for deeper subject-specific memory.
- Use `metadata/` for reusable node conventions and taxonomy.
- Use `sessions/` for date-specific session summaries.
- Reorganize public stage folders as continuous `K0`-`K9` directories.
- Keep ambiguous range folders such as `K4-K5` only under `_legacy-ranges/`; assign each problem to one primary stage and use bridge/challenge references for boundary cases.
- Run the curriculum by mastery/understanding rather than fixed lesson counts.
- Build algorithm materials as visual HTML textbook pages where useful, starting with a standalone `curriculum/materials/algorithm-visual-textbook/index.html`.
- Treat GitHub Pages as a suitable initial deployment target for the interactive textbook; keep grading/execution out of scope at first and link to external judges/offical PDFs.
- When migrating to the user's GitHub Pages project, first inspect the existing repo/site structure, then decide what to preserve. The user is open to removing most old content if needed.
- The migrated project should prioritize an interactive data-structure/algorithm textbook over a fixed-session course schedule.
