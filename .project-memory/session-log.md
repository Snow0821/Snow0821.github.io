# Session Log

## 2026-05-18
- Inspected the target GitHub Pages repository: plain static HTML/CSS/JS, old root page focused on personal AI research, with many older personal-study folders still present.
- Reworked `index.html`, `style.css`, and `script.js` into a student-facing algorithm class dashboard.
- Added K0-K9 stage map, mastery-based operating principles, prefix sum/BFS/DP visualizer scaffold, problem-source policy, and GitHub Classroom autograding guidance.
- Checked current GitHub-as-judge options: GitHub Classroom autograding is useful for small assignments and feedback, but should not replace KOI-style online judging.
- Checked KOI current official sources: KOI archives expose 2019-2025 records and 2025 round 2 exposes official problem/solution/model-code/test links plus BIKO judge links.
- Added `curriculum/problems/koi/README.md` and `curriculum/problems/koi/2025-round2.md` as a fresh official-link problem collection seed.

## 2026-05-18
- User asked how memory should scale as content grows.
- User preferred metadata and a deeper/wider folder structure.
- Added memory map, metadata templates, taxonomy, topic directories, and session notes.
- User asked for a concise full curriculum structure starting from basic algorithms.
- Added `curriculum/01-algorithm-roadmap.md` and indexed algorithm roadmap memory.
- User asked how to structure a broader lifelong foundation beyond informatics olympiad, including Codeforces-style high-difficulty growth.
- Added `curriculum/02-lifelong-competitive-programming-roadmap.md` and indexed the new long-term direction.
- User asked to split the curriculum into finer stages like solving 2nd-session problem 1, then problem 2, through high-school final problems and beyond.
- Added `curriculum/03-problem-number-stage-ladder.md` with L/E/M/H/C milestone stages.
- User pointed out that elementary-division KOI problems can be difficult.
- Checked official KOI 2022-2025 2nd-round problem tables and added difficulty calibration notes.
- User asked how many stages the elementary/middle/high olympiad path should be classified into based on observed levels.
- Added a 10-stage unified K ladder in `curriculum/05-koi-stage-classification.md`.
- User asked to synthesize previous research and memory into a concrete plan for learning materials and problem design by difficulty.
- Added `curriculum/06-learning-material-and-problem-design.md` with K0-K9 material, problem-set, and student-solving workflow design.
- User asked to create folders and first organize past KOI problems.
- Added `curriculum/problems/koi/` with 2022-2025 round 2 indexes, analysis folder, and problem analysis template.
- User asked to download all official problems and solutions available from the homepage.
- Added a reusable downloader and downloaded 2019-2025 official problem/solution PDFs into `curriculum/problems/koi/raw/`.
- User asked to redo the previous analysis based on the downloaded problems.
- Extracted PDF text with `pdftotext`, added official-PDF-based reanalysis, and updated priority bridge problem analysis stubs.
- User asked to proceed with triaging the downloaded problems.
- Added `curriculum/problems/koi/triage/round2-2022-2025.md` and updated 2022-2025 round2 indexes from `listed` to `triaged`.
- User asked to build K-stage representative problem sets from the triage table.
- Added `curriculum/problems/koi/sets/k-stage-representative-sets.md`.
- User asked to organize folders by stage with goals and problem lists.
- Added `curriculum/stages/` with per-stage overview/problem-list/teaching-notes files and bundle folders.
- User asked whether ambiguous range stages and empty stages should be reorganized, and wanted data-structure/algorithm concepts arranged in learning flow.
- Reorganized `curriculum/stages/` into continuous `K0`-`K9` folders, moved old range folders to `_legacy-ranges/`, and added `concept-flow.md`.
- User said classes do not need fixed session units because progress varies by student and condition; requested achievement/understanding-based organization and visual HTML algorithm materials.
- Added `curriculum/stages/mastery-framework.md`, updated the stages README, and created the first HTML visual textbook at `curriculum/materials/algorithm-visual-textbook/index.html`.
- User asked how to structure the whole project as an HTML/interative textbook and whether integrating with GitHub Pages would be good.
- Added `curriculum/materials/interactive-textbook-architecture.md` with GitHub Pages-oriented project structure and rollout plan.
- User clarified the goal: move this project memory into a GitHub Pages project, inspect/understand that project even if most old content is later removed, install/build an interactive data-structure and algorithm textbook, and design it so students can visually inspect complex algorithms through interaction.
- Updated current state, open questions, decisions, and added a GitHub Pages migration topic so this intent is portable.

## 2026-05-17
- User proposed an informatics olympiad curriculum project.
- User wants a hidden continuity folder for project management across sessions.
- User wants staged teaching: theory, practice problems, then categorized past-problem solving.
- Created initial memory structure and first public curriculum draft.
