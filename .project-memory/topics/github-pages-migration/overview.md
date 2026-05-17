---
id: github-pages-migration
type: topic
status: active
updated: 2026-05-18
links: [mastery-based-operation, stage-folder-structure, learning-material-and-problem-design]
---

# GitHub Pages Migration

## Goal

Move the distilled project memory and curriculum direction into the user's
GitHub Pages project, then turn that site into an interactive data-structure and
algorithm textbook.

The target site already has other/older content. It should be inspected first so
the project can be understood. The user is open to major cleanup or deletion
later, so preservation is not a hard constraint unless specific content is
identified as valuable.

## Product Intent

Student-facing result:
- A browser-based interactive textbook.
- Focus on data structures and algorithms.
- Students should be able to see complex algorithms through visual state changes,
  not only read text.
- The site should support mastery-based learning rather than fixed lesson counts.

Teacher/planning result:
- Project memory, KOI stage classification, problem triage, and representative
  problem sets remain available as planning/reference material.
- Student-facing pages should be simpler and more visual than the internal
  Markdown planning docs.

## Migration Strategy

1. Inspect the GitHub Pages repository structure.
2. Identify the current framework or build model:
   - plain HTML/CSS/JS
   - Jekyll
   - Astro
   - VitePress
   - Docusaurus
   - another static setup
3. Identify content that must be kept versus content that can be archived or removed.
4. Copy over the portable project memory and curriculum design.
5. Add the interactive textbook scaffold.
6. Create the first student-facing learning dashboard.
7. Add algorithm chapters incrementally.
8. Wire chapters to KOI stages and representative problems.

## Preferred Initial Scope

Do first:
- Keep the site static.
- Use HTML/CSS/JS or a light static-site framework.
- Add visual chapters for arrays, prefix sums, BFS, DP, trees/DSU, and segment tree.
- Link to KOI PDFs/external judges instead of building a judge.

Do not do first:
- Do not build login/accounts.
- Do not build server-side code execution.
- Do not build a full LMS.
- Do not over-preserve outdated site content if it blocks the new structure.

## Suggested Public Site Sections

- `Home`: learning dashboard, not a marketing landing page.
- `Stages`: K0-K9 mastery map.
- `Textbook`: interactive algorithm chapters.
- `Problems`: KOI problem map by stage and concept.
- `Practice Log`: printable/copyable student record templates.
- `About`: short explanation of the curriculum philosophy.

## Interactive Textbook Requirements

Every algorithm page should prefer this structure:

1. Problem situation.
2. Slow approach.
3. Bottleneck visualization.
4. Improved idea.
5. Interactive algorithm visualization.
6. Implementation skeleton.
7. KOI/contest problem connections.
8. Mastery check.

Interaction examples:
- Step buttons for BFS queue expansion.
- Highlighted arrays for prefix sums and two pointers.
- State tables for DP transitions.
- Tree diagrams for DFS, rerooting, DSU, segment tree.
- Range query/update animations.
- Sliders for input size and complexity comparison.

## Existing Local References

Current local files to migrate or use as source:

- `curriculum/materials/interactive-textbook-architecture.md`
- `curriculum/materials/algorithm-visual-textbook/index.html`
- `curriculum/stages/README.md`
- `curriculum/stages/mastery-framework.md`
- `curriculum/stages/concept-flow.md`
- `curriculum/problems/koi/sets/k-stage-representative-sets.md`
- `curriculum/problems/koi/triage/round2-2022-2025.md`

Internal memory to port:
- `.project-memory/state.md`
- `.project-memory/decisions.md`
- `.project-memory/indexes/memory-map.md`
- `.project-memory/topics/github-pages-migration/overview.md`
- `.project-memory/topics/mastery-based-operation/overview.md`

## Open Questions Before Editing Target Repo

- What is the target GitHub Pages repo path?
- What framework/build system does it use?
- Which old pages, if any, should be preserved?
- Should the textbook be the new homepage or a sub-section?
- Should the first version be plain HTML or use a framework such as Astro/VitePress?

## Next Action

When the target GitHub Pages repository is available, inspect it first and create
a migration plan before editing. If it is already very old or messy, propose an
archive-and-rebuild approach rather than trying to patch everything in place.
