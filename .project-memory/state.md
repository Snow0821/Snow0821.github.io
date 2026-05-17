# Current State

Project: class-first GitHub Pages site for Korean informatics olympiad-style algorithm instruction, with a lightweight personal introduction for the instructor.

Current direction:
- Treat the active site as two-purpose only: class materials first, personal introduction second.
- Keep curriculum development as the current priority.
- The homepage is now intended as a student work dashboard for existing class
  students, not a promotional page.
- The homepage now includes a clickable whole-course tree so students can see
  where each topic sits in the curriculum.
- The GitHub Pages root has been reworked from an old personal research landing page into a student-facing algorithm class dashboard.
- Older unrelated materials have been moved to `history/legacy-personal-site-2026-05-18/` rather than deleted.
- CV is now represented by `cv/index.html` with `cv/cv.pdf` as the download version.
- Build an HTML/interactive textbook for data structures and algorithms.
- Use visual, step-by-step interaction so students can see complex algorithm state changes directly.
- Keep KOI/algorithm curriculum documents as planning material, and expose student-facing content as web pages.

Initial deliverables:
- Portable project memory for the GitHub Pages migration.
- Interactive textbook architecture and root-page prototype.
- First student-facing HTML dashboard with K0-K9 stage map and simple prefix sum/BFS/DP visualizers.
- Homepage now starts with today-work guidance, quick links, problem resources,
  and review procedure before stage/visual reference sections.
- `curriculum/README.md` and `curriculum/map.md` now define the active
  curriculum tree.
- KOI 2025 round 2 official-link problem index under `curriculum/problems/koi/`.
- KOI official-link index for 2019-2025 rounds 1 and 2, including problem,
  solution, model-code, test-data, and judge links.
- `history/README.md` explaining archived old site materials.
- Lightweight HTML CV page under `cv/`, with PDF retained as a download.

Working assumptions:
- Target students may progress at different speeds; use mastery/understanding instead of fixed lesson counts.
- The curriculum should support both conceptual growth and contest problem judgment.
- GitHub Pages is an appropriate first deployment target because static HTML/CSS/JS is enough for visualization and broad access.
- Do not initially build an online judge or server-side code runner; link to official PDFs/BIKO for problem statements and grading.
- GitHub Classroom exists as `알고리즘 공부방` and can be used later for
  homework distribution/autograding when suitable.
- The project should be developed incrementally with the user.
