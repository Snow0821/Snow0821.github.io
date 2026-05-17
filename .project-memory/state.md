# Current State

Project: interactive GitHub Pages textbook for students preparing for Korean informatics olympiad-style exams and long-term algorithm contest growth.

Current direction:
- Migrate the project memory and distilled curriculum intent into a separate GitHub Pages project.
- The existing GitHub Pages root has now been reworked from an old personal research landing page into a student-facing algorithm class dashboard.
- Build an HTML/interactive textbook for data structures and algorithms.
- Use visual, step-by-step interaction so students can see complex algorithm state changes directly.
- Keep KOI/algorithm curriculum documents as planning material, and expose student-facing content as web pages.

Initial deliverables:
- Portable project memory for the GitHub Pages migration.
- Interactive textbook architecture and root-page prototype.
- First student-facing HTML dashboard with K0-K9 stage map and simple prefix sum/BFS/DP visualizers.
- KOI 2025 round 2 official-link problem index under `curriculum/problems/koi/`.

Working assumptions:
- Target students may progress at different speeds; use mastery/understanding instead of fixed lesson counts.
- The curriculum should support both conceptual growth and contest problem judgment.
- GitHub Pages is an appropriate first deployment target because static HTML/CSS/JS is enough for visualization and broad access.
- Do not initially build an online judge or server-side code runner; link to official PDFs/BIKO for problem statements and grading.
- The project should be developed incrementally with the user.
