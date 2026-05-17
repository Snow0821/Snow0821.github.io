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
- Set the project goals to exactly two active purposes: class-centered algorithm/curriculum materials and a lightweight personal introduction page.
- Current priority is curriculum development; personal materials should stay minimal and should not drive the site structure.
- Archive unrelated legacy site material under `history/` instead of deleting it.
- Keep `.project-memory` updated continuously as the operating memory for goals, decisions, open questions, and session history.
- Use `cv/index.html` as the default CV page, keep `cv/cv.pdf` as a download link, and keep `cv/cv.tex` only as source for regenerating the PDF.
- Keep the CV/profile area lightweight; after this pass, return focus to curriculum and class materials.
- For KOI past problems, store official links and metadata rather than copying
  problem statements or redistributing downloaded test-data zips.
- Keep any optional local KOI downloads under ignored directories such as
  `curriculum/problems/koi/downloads/`.
- The homepage should be a student work dashboard, not a promotional landing
  page. Prioritize quick access to assigned work, problem links, review flow,
  stage reference, and concept visualizations.
- Assume the primary website users are existing students already taking the
  class; avoid explanatory marketing copy unless it directly helps them find or
  use class material.
- Use the GitHub Classroom named `알고리즘 공부방` as an optional homework channel
  when assignments need repository distribution, starter code, or autograding.
- Keep BIKO/official judges as the primary contest-problem judging path; GitHub
  Classroom is for class homework support, not a replacement online judge.
- Organize the curriculum around a visible tree so students can always locate
  the current topic in the whole course.
- Use the top-level tree branches: foundations, data structures, algorithms,
  problem-solving training, and KOI stages.
- When adding new material, attach it to the nearest tree branch before adding
  loose pages or links.
- Curriculum tree branches should be collapsible so students can see the whole
  structure without being overwhelmed.
- Attach BIKO/KOI links as the primary practice path and use LeetCode/BOJ links
  as supplemental pattern practice where useful.
