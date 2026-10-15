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
    """Return source programs, or field-specific views of their school courses.

    Source programs/details are stored once. Views carry stable source IDs so
    splitting a school course into evidenced tracks cannot inflate totals.
    """
    records = []
    for item in DATA['teaching']:
        course = DATA['courses'][item['course']]
        if group is None:
            records.append(item)
        elif not course.get('classifyDetails'):
            if course['group'] == group:
                records.append(item)
        else:
            details = []
            for detail in item.get('details', []):
                tracks = detail.get('tracks')
                for track in tracks or [detail]:
                    if (track.get('group') or 'unclassified') != group:
                        continue
                    row = dict(detail)
                    row.pop('tracks', None)
                    if tracks:
                        row.update(track)
                        row['id'] = detail['id'] + '-' + track['id']
                        row['title'] = {lang: localized(detail['title'], lang) + ' · ' + localized(track['title'], lang) for lang in LANGUAGES}
                        if 'start' not in track:
                            row['periodNote'] = {lang: text('label.shared_period', lang) for lang in LANGUAGES}
                    row['sourceDetail'] = detail['id']
                    details.append(row)
            if details:
                view = dict(item, id=item['id']+'-'+group, sourceId=item['id'], details=details,
                            viewTitle=course['groupTitles'][group],
                            start=min(detail['start'] for detail in details),
                            end=None if any(detail['end'] is None for detail in details) else max(detail['end'] for detail in details))
                view['schoolSummary'] = {lang: ' · '.join(dict.fromkeys(localized(detail['title'],lang).split(' · ')[0] for detail in details)) for lang in LANGUAGES}
                records.append(view)
    return sorted(records, key=lambda item: (item['end'] is None, item['start']), reverse=True)


def current_role_records():
    """Resolve explicitly curated roles; a current course is not a new job."""
    teaching = {item['id']: item for item in DATA['teaching']}
    records = []
    for item in DATA.get('currentRoles', []):
        source = teaching[item['teaching']] if item.get('teaching') else item
        if source['end'] is None:
            records.append(dict(item, organization=source['organization'],
                                start=source['start'], end=source['end']))
    return sorted(records, key=lambda item: item['start'], reverse=True)


def teaching_title(item):
    return item.get('viewTitle', DATA['courses'][item['course']]['title'])


def period(item, lang):
    start = item['start'].replace('-', '.')
    if item['end'] == item['start']:
        return start
    end = item['end'].replace('-', '.') if item['end'] else text('label.present', lang)
    return f'{start}–{end}'


def teaching_values(item, lang):
    return {'period': period(item, lang),
            'course': localized(teaching_title(item), lang),
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
        runtime_keys = {'portfolio', 'download_cv', 'current_language', 'switch_to', 'switched', 'details', 'copied', 'copy_failed', 'email', 'expand_career', 'collapse_career'}
        require(all('ui.'+key in LOCALES[lang] for key in runtime_keys), f'Missing interface message: {lang}')
    for collection in ['education', 'qualifications', 'interests', 'papers', 'teaching', 'teachingGroups']:
        ids = [item['id'] for item in DATA[collection]]
        require(len(ids) == len(set(ids)), f'Duplicate ID in {collection}')
        require(all(re.fullmatch(r'[a-zA-Z0-9_-]+', item) for item in ids), f'Invalid ID in {collection}')
    current_roles = DATA.get('currentRoles', [])
    require(len({item['id'] for item in current_roles}) == len(current_roles), 'Duplicate current role ID')
    teaching_ids = {item['id'] for item in DATA['teaching']}
    for item in current_roles:
        require(re.fullmatch(r'[a-zA-Z0-9_-]+', item['id']), 'Invalid current role ID')
        require(all(lang in item['title'] for lang in LANGUAGES), f'Missing current role translation: {item["id"]}')
        if item.get('context'):
            require(all(lang in item['context'] for lang in LANGUAGES), f'Missing current role context translation: {item["id"]}')
        if item.get('teaching'):
            require(item['teaching'] in teaching_ids, f'Unknown current role teaching reference: {item["id"]}')
            require(not any(key in item for key in ['organization', 'start', 'end']), f'Duplicated current role facts: {item["id"]}')
        else:
            require(item['organization'] in DATA['organizations'], f'Unknown current role organization: {item["id"]}')
            require(bool(re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', item['start'])), f'Invalid current role start: {item["id"]}')
            require(item['end'] is None or bool(re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', item['end'])), f'Invalid current role end: {item["id"]}')
            require(item['end'] is None or item['end'] >= item['start'], f'Reversed current role period: {item["id"]}')
    groups = {group['id'] for group in DATA['teachingGroups']}
    for key, course in DATA['courses'].items():
        require(course['group'] in groups or (course.get('classifyDetails') and course['group'] is None), f'Unknown teaching group: {key}')
        if course.get('classifyDetails'):
            require(set(course.get('groupTitles', {})) == groups | {'unclassified'}, f'Missing school-course group titles: {key}')
    for item in DATA['teaching']:
        for field, collection in [('course', 'courses'), ('organization', 'organizations'), ('role', 'roles')]:
            require(item[field] in DATA[collection], f'Unknown {field}: {item["id"]}')
        for date in [item['start'], item['end']]:
            require(date is None or re.fullmatch(r'\d{4}(?:-(?:0[1-9]|1[0-2]))?', date), f'Invalid date: {date}')
        require(item['end'] is None or item['end'] >= item['start'], f'Reversed period: {item["id"]}')
    detail_ids=[]
    for item in DATA['teaching']:
        for detail in item.get('details', []):
            detail_ids.append(detail['id'])
            require(re.fullmatch(r'[a-zA-Z0-9_-]+', detail['id']), 'Invalid career detail ID')
            require(detail['role'] in DATA['roles'], f'Unknown detail role: {detail["id"]}')
            require(all(lang in detail[field] for field in ['title', 'curriculum'] for lang in LANGUAGES), f'Missing career detail translation: {detail["id"]}')
            if DATA['courses'][item['course']].get('classifyDetails'):
                require('group' in detail, f'Missing school-course group: {detail["id"]}')
                require(detail['group'] is None or detail['group'] in groups, f'Unknown school-course group: {detail["id"]}')
                tracks=detail.get('tracks', [])
                require(len({track['id'] for track in tracks}) == len(tracks), f'Duplicate track ID: {detail["id"]}')
                for track in tracks:
                    require(track['group'] is None or track['group'] in groups, f'Unknown track group: {detail["id"]}')
                    require(all(lang in track[field] for field in ['title','curriculum'] for lang in LANGUAGES), f'Missing track translation: {detail["id"]}')
                    require(('start' in track) == ('end' in track), f'Incomplete track dates: {detail["id"]}')
                    if 'start' in track:
                        require(detail['start'] <= track['start'] <= track['end'] <= detail['end'], f'Track dates outside school period: {detail["id"]}')

    require(len(detail_ids)==len(set(detail_ids)), 'Duplicate career detail ID')
    other_ids=[item['id'] for item in DATA.get('otherExperience', [])]
    require(len(other_ids)==len(set(other_ids)), 'Duplicate other experience ID')
    dated_details=[detail for item in DATA['teaching'] for detail in item.get('details', [])]
    for item in dated_details+DATA.get('otherExperience', []):
        for date in [item['start'], item['end']]:
            require(date is None or re.fullmatch(r'\d{4}(?:-(?:0[1-9]|1[0-2]))?', date), f'Invalid career date: {date}')
        require(item['end'] is None or item['end'] >= item['start'], f'Reversed career period: {item["id"]}')
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

