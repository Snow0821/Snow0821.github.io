# Study Preferences and Workflow

The rules here apply to the entire curriculum. If a subject needs extra instructions, note them in that subject’s `overview.md` or metadata.

1. **Local Sources First**  
   Always consult the primary resource stored in the repository (e.g., PDFs inside each subject’s `textbooks/`) before looking at summaries or external explanations. Use outside references only as supplemental context.
2. **Versioning & Portability**  
   Large binaries (PDFs, split chapters, datasets) live in subject-specific `textbooks/` folders and are Git-ignored. When moving to another computer, copy those assets manually after pulling the repo.
3. **Metadata Before Deep Dives**  
   Each subject or chapter should have a machine-readable `metadata` file capturing scope, page ranges, status, and next actions. Update it as soon as something changes so Codex can reload context without scanning lengthy notes.
4. **Progress Notes**  
   Use the `progress.md` files (project, field, subject, chapter) for narrative logs. Keep “Notes for Codex” focused on open questions, blockers, or tasks you want help with in future sessions.
5. **Problem Workflow**  
   Work exercises offline (paper or code), then document outcomes in the relevant `problems/` or `notes/` folder. Reference exact exercise numbers or page ranges so they can be found later.
6. **Subject-Specific Preferences**  
   When a subject has unique constraints (e.g., “use split chapter PDFs for Calculus”), record them in that subject’s `overview.md` and link them from metadata so every machine—and Codex—follows the same procedure.
