"""Generate the static page without a browser-side data request or a framework."""
import re
from html import escape as h
from content import ROOT, DATA, LANGUAGES, LOCALES, localized, authors, venue_details, reference, bibtex


def translations(values, markup=False):
    return ''.join(f'<span data-l="{lang}" lang="{lang}"' + (' aria-hidden="true"' if lang != 'ko' else '')
                   + '>' + (localized(values, lang) if markup else h(localized(values, lang))) + '</span>'
                   for lang in LANGUAGES)


def pair(values):
    return '<span class="pair">' + translations(values) + '</span>'


def label(key):
    return pair({lang: LOCALES[lang][key] for lang in LANGUAGES})


def metadata(paper):
    return {lang: venue_details(paper, lang) for lang in LANGUAGES}


def topline(paper):
    return f'<span class="paper-topline"><span>{paper["year"]}</span>{pair(DATA["venues"][paper["venue"]]["short"])}</span>'


def summary(paper):
    return f'''<article class="cv-paper" data-paper="{paper['id']}" data-record>
      <div class="cv-year">{paper['year']}</div><div>
      <h3 lang="en">{h(paper['title'])}</h3>
      <dl class="record-meta"><dt>{label('authors')}</dt><dd lang="en">{h(', '.join(authors(paper)))}</dd>
      <dt>{label('venue')}</dt><dd class="paper-venue">{pair(metadata(paper))}</dd></dl>
      </div></article>'''


def detail(paper):
    pid, title = paper['id'], h(paper['title'])
    author_line = ', '.join(f'<strong>{h(name)}</strong>' if i == 0 else h(name) for i, name in enumerate(authors(paper)))
    link_label = label('paper_pdf') if paper['linkLabel'] == 'pdf' else h(paper['linkLabel'])
    return f'''<article class="paper" data-paper="{pid}" data-open="false" data-block>
      <div class="desktop-only">{topline(paper)}<h3 class="paper-title" lang="en">{title}</h3></div>
      <button type="button" class="paper-expand mobile-only cursor-interaction" aria-expanded="false" aria-controls="snow-detail-{pid}" aria-label="{title} 상세 보기">
      <span>{topline(paper)}<span class="paper-name" lang="en">{title}</span></span><span class="expand-sign" aria-hidden="true">+</span></button>
      <div class="paper-detail" id="snow-detail-{pid}">
        <p class="paper-authors" lang="en">{author_line}</p>
        <p class="paper-venue">{pair(metadata(paper))}</p>
        <div class="paper-actions"><a class="action cursor-interaction" href="{h(paper['url'])}" target="_blank" rel="noopener noreferrer">{link_label}<span aria-hidden="true">↗</span></a>
        <button type="button" class="action cite-toggle cursor-interaction" aria-expanded="false" aria-controls="snow-citation-{pid}">{label('cite')}</button></div>
        <div class="citation" id="snow-citation-{pid}" data-paper="{pid}" hidden>
          <div class="cite-tools"><label class="format-label">{label('citation_format')}<select class="cite-format cursor-interaction"><option value="reference">Reference</option><option value="bibtex">BibTeX</option></select></label>
          <button type="button" class="action copy cursor-interaction">{label('copy')}</button></div>
          <pre class="cite-text" data-format="reference"></pre><p class="copy-status" aria-live="polite"></p>
        </div>
      </div></article>'''


def build():
    papers = DATA['papers']
    latest = papers[0]
    preview = '<span class="pair preview-title">' + translations({lang: f'{latest["year"]} · {localized(DATA["venues"][latest["venue"]]["short"], lang)}' for lang in LANGUAGES}) + '</span>'
    preview += f'<span class="preview-line" lang="en">{h(latest["title"])}</span>'
    citation_templates = []
    for paper in papers:
        for lang in LANGUAGES:
            citation_templates.append(f'<template id="snow-ref-{paper["id"]}-{lang}">{h(reference(paper, lang))}</template>')
        citation_templates.append(f'<template id="snow-bib-{paper["id"]}">{h(bibtex(paper))}</template>')
    slots = {
        'profile_roles': ''.join(pair({lang: DATA['profile']['roles'][lang][i] for lang in LANGUAGES}) for i in range(len(DATA['profile']['roles']['en']))),
        'publication_summary': '\n'.join(map(summary, papers)),
        'publication_detail': '\n'.join(map(detail, papers)),
        'publication_preview': preview,
        'citations': '\n'.join(citation_templates),
        'last_updated': label('last_updated') + f'<time datetime="{DATA["updated"]}">{DATA["updated"].replace("-", ".")}</time>',
    }
    def replace(match):
        key = match[1]
        if key.startswith('i18n:'):
            return translations({lang: LOCALES[lang][key[5:]] for lang in LANGUAGES}, markup=True)
        return slots[key]
    template = (ROOT / 'src/index.template.html').read_text()
    result = re.sub(r'\{\{([a-zA-Z0-9_:]+)\}\}', replace, template)
    (ROOT / 'index.html').write_text('\n'.join(line.rstrip() for line in result.splitlines()) + '\n')
    print('Built index.html from shared metadata and locale files.')


if __name__ == '__main__':
    build()
