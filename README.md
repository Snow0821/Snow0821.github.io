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

Cloudflare Workers Builds에서 아래 값으로 GitHub 저장소를 연결합니다. 로컬 MCP 연결이나 로컬 터미널 작업은 필요하지 않습니다.

| 설정 | 값 |
| --- | --- |
| 저장소 | `Snow0821/Snow0821.github.io` |
| 브랜치 | `codex/portfolio-preview-2026-09-13` |
| Worker 이름 | `snow-portfolio` (`wrangler.jsonc`와 동일) |
| 루트 디렉터리 | 저장소 루트 `/` |
| Build command | 비워 둠 |
| Deploy command | `npm run deploy` |
| Non-production branch deploy command | `npm run deploy:preview` |

배포 명령이 `dist/` 생성을 먼저 실행하므로 별도 빌드 명령을 설정할 필요가 없습니다. 프런트엔드 패키지, 데이터베이스, 런타임 환경변수는 필요하지 않습니다. Cloudflare Builds가 배포 인증을 처리합니다. 기존 Worker를 연결할 경우 이름이 `wrangler.jsonc`의 `name`과 같아야 합니다.

이 브랜치를 별도 검토용 Worker의 배포 브랜치로 선택하거나, 기존 Worker의 non-production branch builds를 활성화해 미리보기로 배포할 수 있습니다. 후자의 경우 `npm run deploy:preview`를 사용합니다. 기존 Build command가 `npm run build`이면 그대로 두어도 동작하지만 빌드가 두 번 실행됩니다.

GitHub 업로드만으로 Cloudflare 연결이 생기지는 않습니다. 연결 및 배포가 성공한 뒤 Workers & Pages의 해당 Worker에서 `Visit` 또는 Preview URL을 열 수 있습니다. 이후 이 브랜치의 커밋은 자동 배포됩니다. 이 환경에서는 Cloudflare 계정, 실제 배포 결과, 공개 URL을 확인하지 않았습니다.

Review policy: before deploying a review build, configure Cloudflare Access so only the owner can open the review URL. `noindex` is not access control. Keep draft labels and noindex directives until the owner approves public release.

[Cloudflare Workers Builds configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)

Only `dist/` is deployed. Never change the asset directory to the repository root. Static pages, scripts, fonts and PDF files are served as assets; country-based routing runs at `/` and `/index.html`. Korea selects Korean, all other/unknown countries select English. Explicit language selection overrides country and persists in a cookie and local storage. Local file previews cannot detect an IP country and default to English.

## Scope of the first version

Implemented: responsive homepage, English/Korean switch, expandable research summaries, public GitHub/Scholar/LinkedIn links, email inquiries, an illustrative interactive network, three downloadable draft PDFs, and Cloudflare routing code.

Not enabled: private note editor, account login, online CV editing, or a publishing CMS. Private routes fail closed with HTTP 503. No private notes, old journals, unreleased experiments, or personal history files are in the deployment. The Notes area is empty rather than populated with invented entries.

See `docs/decisions.md` and `docs/sources.md` for the review checklist and content provenance.
