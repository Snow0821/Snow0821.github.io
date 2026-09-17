# Validation of the review version

- `npm run build`: passed.
- `npm test`: all five routing and artifact checks passed. These cover language precedence, private routes failing closed, source-path rejection, non-cacheable country redirects, and the presence of actual PDF files.
- All three final PDFs rendered and visually inspected: one page each, readable Korean glyphs, no clipping.
- Static source review completed, including tablet spacing, separate public build output and embedded preview downloads.
- Browser visual and interaction checks remain outstanding. This environment has no local Chromium binary, and the available cloud browser explicitly rejects local-file navigation. No browser rendering, mobile overflow or click/download test is claimed as passed.
- Cloudflare deployment, country routing on the edge, and owner-only Access protection have not been exercised because the account is not connected.

The bundled web/PDF font is an OFL-licensed subset of Nanum Gothic, renamed internally to Snow Portfolio. The original license and attribution remain in `public/fonts/OFL.txt`. Regenerate the font subset from the original licensed font if future Korean content introduces additional glyphs.
