"""Publication views reuse the same metadata and citation formatters."""
from content import DATA, LANGUAGES, DEFAULT_LANGUAGE, venue_details, text
from content import display_authors
from html_components import h, pair, label

def metadata(paper):
    return {lang: venue_details(paper, lang) for lang in LANGUAGES}


def topline(paper):
    return f'<span class="paper-topline"><span>{paper["year"]}</span>{pair(DATA["venues"][paper["venue"]]["short"])}</span>'


def topic_tags(paper):
    tags = ''.join('<li>'+pair(tag)+'</li>' for tag in paper.get('topics', []))
    return '<ul class="paper-topics">'+tags+'</ul>' if tags else ''


def research_tags():
    return '<span class="research-topics">'+''.join(
        '<span class="topic-tag">'+pair(tag)+'</span>' for tag in DATA['researchTopics'])+'</span>'


def summary(paper):
    return f'''<article class="cv-paper" data-paper="{paper['id']}" data-record>
      <div class="cv-year">{paper['year']}</div><div>
      <h3 lang="en">{h(paper['title'])}</h3>
      {topic_tags(paper)}
      <dl class="record-meta"><dt>{label('label.authors')}</dt><dd>{pair({lang:', '.join(display_authors(paper, lang)) for lang in LANGUAGES})}</dd>
      <dt>{label('label.venue')}</dt><dd class="paper-venue">{pair(metadata(paper))}</dd></dl>
      </div></article>'''


def detail(paper):
    pid, title = paper['id'], h(paper['title'])
    author_line = {lang:', '.join(f'<strong>{h(name)}</strong>' if i == 0 else h(name)
                                for i,name in enumerate(display_authors(paper,lang)))
                   for lang in LANGUAGES}
    link_label = label('action.paper_pdf') if paper['linkLabel'] == 'pdf' else h(paper['linkLabel'])
    expand_label = h(text('ui.details', DEFAULT_LANGUAGE, title=paper['title']))
    return f'''<article class="paper" data-paper="{pid}" data-open="false" data-block>
      <div class="desktop-only">{topline(paper)}<h3 class="paper-title" lang="en">{title}</h3></div>
      <button type="button" class="paper-expand mobile-only cursor-interaction" aria-expanded="false" aria-controls="snow-detail-{pid}" aria-label="{expand_label}">
      <span>{topline(paper)}<span class="paper-name" lang="en">{title}</span></span><span class="expand-sign" aria-hidden="true">+</span></button>
      {topic_tags(paper)}
      <div class="paper-detail" id="snow-detail-{pid}">
        <p class="paper-authors">{pair(author_line,markup=True)}</p>
        <p class="paper-venue">{pair(metadata(paper))}</p>
        <div class="paper-actions"><a class="action cursor-interaction" href="{h(paper['url'])}" target="_blank" rel="noopener noreferrer">{link_label}<span aria-hidden="true">↗</span></a>
        <button type="button" class="action cite-toggle cursor-interaction" aria-expanded="false" aria-controls="snow-citation-{pid}">{label('action.cite')}</button></div>
        <div class="citation" id="snow-citation-{pid}" data-paper="{pid}" hidden>
          <div class="cite-tools"><label class="format-label">{label('action.citation_format')}<select class="cite-format cursor-interaction"><option value="reference">Reference</option><option value="bibtex">BibTeX</option></select></label>
          <button type="button" class="action copy cursor-interaction">{label('action.copy')}</button></div>
          <pre class="cite-text" data-format="reference"></pre><p class="copy-status" aria-live="polite"></p>
        </div>
      </div></article>'''

