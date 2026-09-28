"""One content model and formatting rules for the website and both CVs."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/portfolio.json').read_text())
LANGUAGES = [item['code'] for item in DATA['languages']]
DEFAULT_LANGUAGE = DATA['defaultLanguage']
LOCALES = {lang: json.loads((ROOT / f'locales/{lang}.json').read_text()) for lang in LANGUAGES}


def localized(value, lang):
    if isinstance(value, str):
        return value
    for code in [lang, 'en', DEFAULT_LANGUAGE]:
        if code in value:
            return value[code]
    raise ValueError(f'Missing localized value for {lang}')


def text(key, lang, **values):
    return LOCALES[lang][key].format(**values)


def cv_filename(lang):
    return DATA['profile']['cvFilename'].format(language=lang.upper())


def teaching_records(group=None):
    records = [item for item in DATA['teaching']
               if group is None or DATA['courses'][item['course']]['group'] == group]
    return sorted(records, key=lambda item: (item['end'] is None, item['start']), reverse=True)


def period(item, lang):
    start = item['start'].replace('-', '.')
    if item['end'] == item['start']:
        return start
    end = item['end'].replace('-', '.') if item['end'] else text('label.present', lang)
    return f'{start}–{end}'


def teaching_values(item, lang):
    return {'period': period(item, lang),
            'course': localized(DATA['courses'][item['course']]['title'], lang),
            'organization': localized(DATA['organizations'][item['organization']], lang),
            'role': localized(DATA['roles'][item['role']], lang)}


def year_range(records, teaching=False):
    if not records:
        return ''
    years = [int(value[:4]) for item in records
             for value in ([item['start'], item['end'] or DATA['updated']] if teaching else [str(item['year'])])]
    start, end = min(years), max(years)
    return str(start) if start == end else f'{start}–{end}'


def write_if_changed(path, value):
    content = value.encode() if isinstance(value, str) else value
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return True


def validate():
    """Fail before generation when an edit leaves a missing translation or reference."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(len(set(LANGUAGES)) == len(LANGUAGES), 'Duplicate language code')
    require(DEFAULT_LANGUAGE in LANGUAGES, 'Unknown default language')
    for lang in LANGUAGES:
        require(set(LOCALES[lang]) == set(LOCALES[DEFAULT_LANGUAGE]), f'Locale keys differ: {lang}')
        runtime_keys = {'portfolio', 'download_cv', 'current_language', 'switch_to', 'switched', 'details', 'copied', 'copy_failed', 'email'}
        require(all('ui.'+key in LOCALES[lang] for key in runtime_keys), f'Missing interface message: {lang}')
    for collection in ['education', 'qualifications', 'interests', 'papers', 'teaching', 'teachingGroups']:
        ids = [item['id'] for item in DATA[collection]]
        require(len(ids) == len(set(ids)), f'Duplicate ID in {collection}')
        require(all(re.fullmatch(r'[a-zA-Z0-9_-]+', item) for item in ids), f'Invalid ID in {collection}')
    groups = {group['id'] for group in DATA['teachingGroups']}
    for key, course in DATA['courses'].items():
        require(course['group'] in groups, f'Unknown teaching group: {key}')
    for item in DATA['teaching']:
        for field, collection in [('course', 'courses'), ('organization', 'organizations'), ('role', 'roles')]:
            require(item[field] in DATA[collection], f'Unknown {field}: {item["id"]}')
        for date in [item['start'], item['end']]:
            require(date is None or re.fullmatch(r'\d{4}(?:-(?:0[1-9]|1[0-2]))?', date), f'Invalid date: {date}')
        require(item['end'] is None or item['end'] >= item['start'], f'Reversed period: {item["id"]}')
    for paper in DATA['papers']:
        require(bool(paper['authors']), f'Missing authors: {paper["id"]}')
        require(all(author in DATA['authors'] for author in paper['authors']), f'Unknown author: {paper["id"]}')
        require(paper['venue'] in DATA['venues'], f'Unknown venue: {paper["id"]}')
    for role in DATA['profile']['roles']:
        require(role in DATA['roles'], f'Unknown profile role: {role}')
    for lang in LANGUAGES:
        require(Path(cv_filename(lang)).name == cv_filename(lang), 'CV filename must be a basename')
    for language in DATA['languages']:
        require((ROOT / language['flag']).is_file(), f'Missing flag asset: {language["code"]}')
    for link in DATA['profile']['links']:
        require((ROOT / 'assets' / link['icon']).is_file(), f'Missing link icon: {link["id"]}')


def authors(paper, field='name'):
    return [localized(DATA['profile']['name'], 'en') if field == 'name' and DATA['authors'][author].get('profile')
            else DATA['authors'][author][field] for author in paper['authors']]


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
    name = ' and '.join(names) if len(names) <= 2 else ', '.join(names[:-1]) + ', and ' + names[-1]
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
