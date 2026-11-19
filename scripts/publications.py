"""Published papers viewed from one localized record and its canonical citation."""
from content import DATA, bibtex, display_authors, localized, reference, venue_details
from html_components import anchor, h, label, local


def paper_title(paper, lang):
    return localized(paper.get('displayTitle', paper['title']), lang)


def detail(paper, lang):
    pid = h(paper['id'])
    venue = local(DATA['venues'][paper['venue']]['short'], lang)
    title = h(paper_title(paper, lang))
    authors = h(' · '.join(display_authors(paper, lang)))
    description = f'<p>{local(paper["summary"],lang)}</p>' if paper.get('summary') else ''
    topics = ' / '.join(local(t,lang) for t in paper.get('topics',[]))
    return f'''<article class="paper record-row" id="paper-{pid}" data-paper="{pid}">
<div class="row-margin"><span class="year">{paper['year']}</span><span>{venue}</span></div>
<div><h3>{title}</h3><p class="byline">{authors}</p>
<p class="bibliography">{h(venue_details(paper,lang))}</p>{description}
<p class="paper-topics">{topics}</p>
<div class="paper-actions" data-success="{label('works.copied', lang)}" data-failure="{label('works.failed',lang)}">
{anchor(paper['url'], label('works.publication_link',lang), 'source-link', True)}
<button type="button" data-copy="ref-{pid}">{label('works.citation',lang)}</button>
<button type="button" data-copy="bib-{pid}">{label('works.bibtex',lang)}</button>
<span class="copy-status" data-copy-status role="status" aria-live="polite"></span></div>
<template id="ref-{pid}">{h(reference(paper,lang))}</template>
<template id="bib-{pid}">{h(bibtex(paper))}</template></div></article>'''
