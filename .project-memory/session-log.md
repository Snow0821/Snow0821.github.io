# Session Log

## 2026-05-18
- User asked how to proceed because the project still feels loose and should be
  organized as a tree.
- Added a clickable `전체 학습 지도` section to the homepage.
- Defined the visible tree around foundations, data structures, algorithms,
  problem-solving training, and KOI stages.
- Added `curriculum/README.md` and `curriculum/map.md` as the file-level
  curriculum tree and future attachment point for new lessons/materials.
- Recorded the rule that new material should attach to the closest tree branch
  rather than becoming a loose page.
- User asked for collapsible branches and practice links such as BIKO/LeetCode.
- Added expand/collapse controls to the curriculum tree.
- Filled tree nodes with practice links, including BIKO/KOI as the primary path
  and LeetCode/BOJ as supplemental pattern practice.
- Added per-node review questions and a recommendation panel.

## 2026-05-18
- User said they have created a GitHub Classroom named `알고리즘 공부방`.
- Recorded that this classroom can be used later for homework distribution,
  starter repositories, and optional autograding.
- Kept the deployment assumption unchanged: GitHub Pages remains static, BIKO
  remains the main judge path for KOI-style problem solving.

## 2026-05-18
- User clarified that the site is for students already learning from them, so
  promotional copy is unnecessary.
- Reworked homepage order from landing-page style to student workflow style:
  today-work checklist, quick links, problem resources, review procedure,
  K-stage reference, and concept visualization.
- Removed the separate GitHub-as-judge explanation section from the active
  homepage; judge policy remains in project memory and problem-source notes.
- Updated style rules to make the first screen denser and easier to scan.

## 2026-05-18
- User asked to collect as much usable KOI past-problem information as possible,
  including solutions and test cases if available.
- Added `scripts/collect_koi_links.py` to scrape official KOI archive pages.
- Collected official-link metadata from 2019-2025 rounds 1 and 2: 14 pages,
  130 indexed rows, 119 problem links, 101 solution links, 43 model-code links,
  39 solution-code zip links, 85 test-data links, and 90 judge links.
- Generated `curriculum/problems/koi/official-link-index.json`,
  `official-link-index.md`, `test-data-index.md`, and refreshed
  `2025-round2.md`.
- Updated KOI README and `.gitignore`; official test-data zips are indexed but
  not redistributed in the repository by default.

## 2026-05-18
- User decided to finish the CV setup minimally and return focus to curriculum.
- Added `cv/index.html` as the default HTML CV page.
- Kept `cv/cv.pdf` as the downloadable PDF and `cv/cv.tex` as the source.
- Updated homepage About links to separate `CV` and `PDF`.
- Moved LaTeX build artifacts `cv.aux`, `cv.log`, and `cv.out` into history.
- Recorded that CV/profile should remain lightweight while curriculum work is the priority.

## 2026-05-18
- User fixed the project goal as two active purposes: class-centered curriculum site and personal introduction page.
- User said curriculum should be the current focus and project memory should continue to be maintained.
- Archived older unrelated site folders into `history/legacy-personal-site-2026-05-18/`: components, data, dailynotes, experiments, extra_materials, my_curriculum, and paper_reviews.
- Kept `cv/` active for the personal introduction goal.
- Added `history/README.md` to document archive policy and what remains active.
- Added a lightweight personal introduction section to the homepage while keeping the page class-first.
- Updated `state.md`, `decisions.md`, and `open-questions.md` to reflect the new fixed scope.

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
