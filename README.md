# Snow - research & teaching portfolio

First review version of Soon Ho Choi's new portfolio. The source belongs in the existing private `Snow0821/Snow0821.github.io` repository. This branch replaces the previous website; the original remains in its parent commit and on `main` until approved.

## Run

Requires Node.js 22 or newer. There are no frontend package dependencies.

```sh
npm run build
npm run preview
npm test
```

Open `http://127.0.0.1:4173`. The build also creates `preview/Snow-Portfolio-Preview.html`, a self-contained offline preview with the three PDF downloads embedded.

## Edit content

- `content/profile.json` is the shared career and research source.
- `src/app.js` contains bilingual presentation copy and interactions.
- `src/style.css` contains responsive visual styles.
- Run `python scripts/make_pdfs.py` after career changes, then `npm run build`. PDF generation requires reportlab and the bundled subset font.
- Generated PDFs remain review copies until the owner approves the content. LinkedIn remains the preferred source, but its full profile could not be read during this draft.

## Cloudflare deployment

Cloudflare account connection is still required. No deployment was made as part of preparing this branch.

1. Connect this private repository to Workers Builds, granting access to this repository only.
2. Select the review branch. Build command: `npm run build`.
3. Before publishing any review build, configure Cloudflare Access so only the owner's account can open the review URL. `noindex` is not access control.
4. With an authenticated Wrangler environment, upload a review version using `npx wrangler versions upload`. Keep the public production branch unchanged until the owner approves.
5. After content review, remove the draft labels and noindex directives as one reviewed change, then publish with `npx wrangler deploy` and the intended public audience.

Only `dist/` is deployed. Never change the asset directory to the repository root. Static pages, scripts, fonts and PDF files are served as assets; country-based routing runs at `/` and `/index.html`. Korea selects Korean, all other/unknown countries select English. Explicit language selection overrides country and persists in a cookie and local storage. Local file previews cannot detect an IP country and default to English.

## Scope of the first version

Implemented: responsive homepage, English/Korean switch, expandable research summaries, public GitHub/Scholar/LinkedIn links, email inquiries, an illustrative interactive network, three downloadable draft PDFs, and Cloudflare routing code.

Not enabled: private note editor, account login, online CV editing, or a publishing CMS. Private routes fail closed with HTTP 503. No private notes, old journals, unreleased experiments, or personal history files are in the deployment. The Notes area is empty rather than populated with invented entries.

See `docs/decisions.md` and `docs/sources.md` for the review checklist and content provenance.
