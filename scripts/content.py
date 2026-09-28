"""Shared portfolio metadata for the website, citations, and PDF CVs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/portfolio.json').read_text())
LANGUAGES = DATA['languages']
LOCALES = {lang: json.loads((ROOT / f'locales/{lang}.json').read_text()) for lang in LANGUAGES}


def localized(value, lang):
    return value.get(lang, value['en'])


def authors(paper, field='name'):
    return [DATA['authors'][author][field] for author in paper['authors']]


def venue_name(paper, lang):
    return localized(DATA['venues'][paper['venue']]['name'], lang)


def venue_details(paper, lang):
    parts = [venue_name(paper, lang)]
    if paper['pages']:
        parts.append('pp. ' + '–'.join(map(str, paper['pages'])))
    if paper['month']:
        parts.append(f"{paper['year']}.{paper['month']:02d}")
    return ' · '.join(parts)


def reference(paper, lang):
    names = authors(paper, 'initials')
    name = ' and '.join(names) if len(names) == 2 else ', '.join(names[:-1]) + ', and ' + names[-1]
    pages = ', pp. ' + '–'.join(map(str, paper['pages'])) if paper['pages'] else ''
    months = ['', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
    month = months[paper['month']] + ' ' if paper['month'] else ''
    return f'{name}, “{paper["title"]},” in {venue_name(paper, lang)}{pages}, {month}{paper["year"]}.'


def bibtex(paper):
    fields = {'author': ' and '.join(authors(paper, 'bibtex')),
              'title': '{' + paper['title'] + '}',
              'booktitle': venue_name(paper, 'en'), 'year': str(paper['year'])}
    venue = DATA['venues'][paper['venue']]
    if 'publisher' in venue:
        fields['publisher'] = localized(venue['publisher'], 'en')
    if paper['pages']:
        fields['pages'] = '--'.join(map(str, paper['pages']))
    if paper['month']:
        fields['month'] = str(paper['month'])
    fields['url'] = paper['url']
    rows = [f'  {key:<9} = {{{value}}}' for key, value in fields.items()]
    return '@inproceedings{' + paper['citationKey'] + ',\n' + ',\n'.join(rows) + '\n}'
