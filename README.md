# Choi Soon Ho — Portfolio

Static bilingual portfolio hosted on GitHub Pages.

## Content and translations

- `data/portfolio.json`: publication titles, authors, venues, dates, links, profile roles, update date, and PDF CV data.
- `locales/ko.json`, `locales/en.json`: website labels and translated copy. Keep matching keys in both files; limited inline HTML such as `<br>` and `<small>` is supported.
- `src/index.template.html`: page layout, with translation and publication slots.
- `scripts/content.py`: shared publication formatting for the home page, Publications tab, references, BibTeX, and PDFs.

Paper titles and author names use their English forms in both languages. Venue names follow the selected language everywhere. BibTeX uses the English venue name for portability. `updated` records the last actual content revision, not the visitor's current date.

After editing content, generate the committed static page:

```sh
python3 scripts/build_site.py
```

To regenerate both CV PDFs, install `reportlab`, put `NanumGothic-Regular.ttf` and `NanumGothic-Bold.ttf` in a local font directory, then run:

```sh
CV_FONT_DIR=/path/to/fonts python3 scripts/build_cv.py
```

PDFs are written to `assets/` by default; `CV_OUTPUT_DIR` can override that directory. Commit the generated `index.html` and PDF files together with their sources. GitHub Pages serves the generated files directly; visitors need no build tools or extra data requests.

The current language control supports Korean and English. Adding another language requires a locale file, localized metadata, a flag/control entry, and updating the language-selection code/styles.
