"""Shared facts, validation, and formatting for the website and generated CV."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/portfolio.json').read_text())
LANGUAGES = [item['code'] for item in DATA['languages']]
DEFAULT_LANGUAGE = DATA['defaultLanguage']
LOCALES = {lang: json.loads((ROOT / f'locales/{lang}.json').read_text()) for lang in LANGUAGES}
RELATIONSHIP_LABELS = {
    'lead': {'ko':'사업 주관','en':'Program lead'},
    'division_lead': {'ko':'AI 분과 주관','en':'AI division lead'},
    'affiliation': {'ko':'소속','en':'Affiliation'},
    'ministry': {'ko':'소관','en':'Responsible ministry'},
    'participating_authorities': {'ko':'참여 교육청','en':'Participating education authorities'},
    'program_management': {'ko':'사업 관리','en':'Program administration'},
    'project_support': {'ko':'사업 기획·운영 지원','en':'Project planning and delivery support'},
    'dedicated_agency': {'ko':'전담기관','en':'Dedicated agency'},
    'program_body': {'ko':'사업기관','en':'Program bodies'},
    'program_institution': {'ko':'사업기관','en':'Program institution'},
    'support': {'ko':'지원','en':'Supported by'},
}

EXPERIENCE_GROUPS = [('development', 'section.other_experience'),
                     ('activities', 'section.activities')]


def experience_records(group=None):
    records = DATA.get('otherExperience', [])
    teaching = {item['id']: item for item in DATA['teaching']}
    result = []
    for item in records:
        if group is not None and item.get('group', 'development') != group:
            continue
        if item.get('teachingAssignments'):
            assignments = [teaching[key] for key in item['teachingAssignments']]
            description = {lang: '\n'.join(teaching_primary(row, lang)+' · '+localized(DATA['roles'][row['role']],lang)
                           +': '+localized(row['summary'],lang) for row in assignments) for lang in LANGUAGES}
            item = dict(item, assignments=assignments, description=description)
        result.append(item)
    return result


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


def teaching_records():
    """Return each source program once, with its complete school details."""
    records = []
    for item in DATA['teaching']:
        course = DATA['courses'][item['course']]
        if course.get('showSchoolPrograms') or course.get('classifyDetails'):
            item = dict(item, schoolSummary={lang: ' · '.join(localized(detail['title'], lang)
                        for detail in item.get('details', [])) for lang in LANGUAGES})
        records.append(item)
    return sorted(records, key=lambda item: (item['end'] is None, item['start']), reverse=True)


def teaching_history_records():
    """Display past teaching once; current activities own their linked detail."""
    current_ids = {row['teaching'] for row in current_role_records() if row.get('teaching')}
    current_ids.update(key for item in DATA.get('otherExperience', []) for key in item.get('teachingAssignments', []))
    records = [row for row in teaching_records() if row['id'] not in current_ids]
    return sorted(records, key=lambda row:(row['end'] is None, row['end'] or DATA['updated'], row['start']), reverse=True)


def detail_program_titles(detail):
    """Actual verified titles from all tracks, without duplicate names."""
    titles = []
    for source in detail.get('tracks') or [detail]:
        values = source.get('programTitles') or ([source['programTitle']] if source.get('programTitle') else [])
        if not values and source is not detail:
            values = detail.get('programTitles') or ([detail['programTitle']] if detail.get('programTitle') else [])
        for title in values:
            if not any(all(localized(existing,lang)==localized(title,lang) for lang in LANGUAGES) for existing in titles):
                titles.append(title)
    return titles


def school_program_groups(item, lang):
    """Condensed verified title/school associations shared by HOME, history and CV."""
    groups = []
    for detail in item.get('details',[]):
        titles = detail_program_titles(detail)
        school = localized(detail['title'],lang).split(' · ')[0]
        key = (tuple(tuple(localized(title,code) for code in LANGUAGES) for title in titles), detail['role'])
        existing = next((group for group in groups if group['_key']==key),None)
        if existing is None:
            existing = {'_key':key,'titles':[localized(title,lang) for title in titles],'schools':[], 'role':localized(DATA['roles'][detail['role']],lang)}
            groups.append(existing)
        if school not in existing['schools']:
            existing['schools'].append(school)
    return [{key:value for key,value in group.items() if key!='_key'} for group in groups] if any(group['titles'] for group in groups) else []


def current_role_records():
    """Resolve explicitly curated roles; a current course is not a new job."""
    teaching = {item['id']: item for item in DATA['teaching']}
    records = []
    for item in DATA.get('currentRoles', []):
        if not item.get('display', True):
            continue
        source = teaching[item['teaching']] if item.get('teaching') else item
        if source['end'] is None:
            records.append(dict(item, organization=source['organization'],
                                start=source['start'], end=source['end'],
                                plannedEnd=source.get('plannedEnd'),
                                summary=source.get('summary'),
                                courseRecord=source if item.get('teaching') else None))
    return sorted(records, key=lambda item: item['start'], reverse=True)


def teaching_subject(item, lang):
    course = DATA['courses'][item['course']]
    title = localized(course['title'], lang)
    program = course.get('program')
    if program:
        name = localized(program, lang)
        if title.startswith(name+' · '):
            return title[len(name)+3:]
        if title.endswith(' · '+name):
            return title[:-(len(name)+3)]
    return title


def teaching_primary(item, lang):
    columns = teaching_columns(item, lang)
    return ' · '.join(dict.fromkeys(value for value in
                     [columns['provider'], columns['audience'], columns['subject']] if value))


def period(item, lang, *, include_planned_notice=True):
    if item.get('periodLabel'):
        return localized(item['periodLabel'], lang)
    if item.get('activeMonths'):
        return ' · '.join(month.replace('-', '.') for month in item['activeMonths'])
    start = item['start'].replace('-', '.')
    end_date = item['end'] or item.get('plannedEnd')
    end = end_date.replace('-', '.') if end_date else text('label.present', lang)
    value = start if end_date == item['start'] else f'{start}–{end}'
    if include_planned_notice and item.get('plannedEnd') and item['end'] is None:
        month = int(item['plannedEnd'][5:7])
        month_name = str(month) if lang == 'ko' else [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'][month]
        value += f' ({text("label.planned_end", lang, month=month_name)})'
    return value


def teaching_relationships(item, lang, *, summary=False):
    """Public, role-labelled program context; never inferred from contract/payment."""
    return [localized(RELATIONSHIP_LABELS[row['role']],lang)+': '+localized(row['name'],lang)
            for row in item.get('relationships',[]) if not summary or row.get('summary')]


def teaching_columns(item, lang):
    """Separate verified context labels without changing canonical course names."""
    course = DATA['courses'][item['course']]
    provider = localized(course['program'], lang) if course.get('program') else ''
    subject = teaching_subject(item, lang)
    audience = localized(item.get('audience') or course.get('client'), lang) if item.get('audience') or course.get('client') else ''
    # These existing titles name their client/context before the separator.
    # This display split does not claim that the client is the employer.
    if not provider and not course.get('client') and item['course'] in {'lginnotek','sds','hanalife','paju','lgcns-coding'}:
        inferred_audience, subject = subject.split(' · ', 1)
        audience = audience or inferred_audience
    organization = localized(DATA['organizations'][item['organization']],lang)
    operator = localized(item['operator'], lang) if item.get('operator') else ''
    organization_lines = teaching_relationships(item,lang,summary=True)
    lead = next((row for row in item.get('relationships',[]) if row['role']=='lead' and row.get('summary')),None)
    if lead and localized(lead['name'],lang)==operator:
        organization_lines = [('사업 주관·운영: ' if lang=='ko' else 'Program lead / operator: ')+operator]
    elif operator:
        organization_lines.append(text('label.operator',lang)+': '+operator)
    elif audience != organization and not organization_lines:
        organization_lines.append(organization)
    organization_label = '\n'.join(organization_lines)
    return {'provider':provider, 'subject':subject, 'audience':audience, 'organizationLabel':organization_label,
            'organizationLines':organization_lines,
            'organization':localized(DATA['organizations'][item['organization']],lang),
            'role':localized(DATA['roles'][item['role']],lang)}




def teaching_detail_context(item, lang):
    """Keep verified relationship roles explicit in expanded history only."""
    columns = teaching_columns(item,lang)
    supplementary = [localized(RELATIONSHIP_LABELS[row['role']],lang)+': '+localized(row['name'],lang)
                     for row in item.get('relationships',[]) if not row.get('summary')]
    return list(dict.fromkeys(columns['organizationLines'] + supplementary))


def teaching_display_columns(item, lang):
    """CV-style program/institution presentation; evidence roles stay in details."""
    value = teaching_columns(item, lang)
    institution = localized(item.get('operator') or DATA['organizations'][item['organization']], lang)
    lines = [institution] if institution != value['audience'] else []
    return {**value, 'organizationLines': lines, 'organizationLabel': '\n'.join(lines)}


def current_role_context(item, lang):
    """A course and its program institution, distinct from the role's affiliation."""
    parts = [localized(item['context'],lang)] if item.get('context') else []
    parts += [localized(row['name'],lang) for row in (item.get('courseRecord') or {}).get('relationships',[])
              if row['role']=='program_institution']
    return ' · '.join(parts)


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
    def validate_planned_end(item):
        if item.get('plannedEnd'):
            planned = item['plannedEnd']
            require(bool(re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', planned)), f'Invalid planned end: {item["id"]}')
            require(item['end'] is None, f'Planned end requires ongoing status: {item["id"]}')
            require(planned >= item['start'], f'Reversed planned period: {item["id"]}')
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
        require(isinstance(item.get('display', True), bool), f'Invalid current role display flag: {item["id"]}')
        require(re.fullmatch(r'[a-zA-Z0-9_-]+', item['id']), 'Invalid current role ID')
        require(all(lang in item['title'] for lang in LANGUAGES), f'Missing current role translation: {item["id"]}')
        if item.get('periodLabel'):
            require(item.get('periodBasis') == 'selection_and_onboarding', f'Unknown current role period basis: {item["id"]}')
            require(all(lang in item['periodLabel'] for lang in LANGUAGES), f'Missing current role period label: {item["id"]}')
        if item.get('context'):
            require(all(lang in item['context'] for lang in LANGUAGES), f'Missing current role context translation: {item["id"]}')
        if item.get('teaching'):
            require(item['teaching'] in teaching_ids, f'Unknown current role teaching reference: {item["id"]}')
            require(not any(key in item for key in ['organization', 'start', 'end', 'plannedEnd']), f'Duplicated current role facts: {item["id"]}')
        else:
            require(item['organization'] in DATA['organizations'], f'Unknown current role organization: {item["id"]}')
            require(bool(re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', item['start'])), f'Invalid current role start: {item["id"]}')
            require(item['end'] is None or bool(re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', item['end'])), f'Invalid current role end: {item["id"]}')
            require(item['end'] is None or item['end'] >= item['start'], f'Reversed current role period: {item["id"]}')
            validate_planned_end(item)
    topics = [topic for group in DATA['teachingGroups'] for topic in group.get('topics', [group['id']])]
    require(len(topics) == len(set(topics)), 'Overlapping teaching display topics')
    require(all(group.get('topics', [group['id']]) for group in DATA['teachingGroups']), 'Empty teaching display topics')
    groups = set(topics)
    for key, course in DATA['courses'].items():
        require(course['group'] in groups or (course.get('classifyDetails') and course['group'] is None), f'Unknown teaching group: {key}')
        if 'program' in course:
            require(isinstance(course['program'], dict) and all(isinstance(course['program'].get(lang), str)
                    and course['program'][lang].strip() for lang in LANGUAGES), f'Invalid program translation: {key}')
        if 'client' in course:
            require(isinstance(course['client'], dict) and all(isinstance(course['client'].get(lang), str)
                    and course['client'][lang].strip() for lang in LANGUAGES), f'Invalid client translation: {key}')
        if course.get('classifyDetails'):
            require(set(course.get('groupTitles', {})) == groups | {'unclassified'}, f'Missing school-course group titles: {key}')
    for item in DATA['teaching']:
        for relationship in item.get('relationships',[]):
            require(relationship['role'] in RELATIONSHIP_LABELS, f'Unknown relationship role: {item["id"]}')
            require(all(isinstance(relationship.get('name',{}).get(lang),str) and relationship['name'][lang].strip() for lang in LANGUAGES), f'Missing relationship translation: {item["id"]}')
            require(isinstance(relationship.get('summary',False),bool), f'Invalid relationship display: {item["id"]}')
        for field in ['operator', 'audience']:
            if item.get(field):
                require(all(isinstance(item[field].get(lang), str) and item[field][lang].strip()
                            for lang in LANGUAGES), f'Missing teaching {field} translation: {item["id"]}')
        for group, summary in item.get('groupSummaries', {}).items():
            require(group in {row['id'] for row in DATA['teachingGroups']}, f'Unknown summary group: {item["id"]}')
            require(all(lang in summary for lang in LANGUAGES), f'Missing group summary translation: {item["id"]}')
        if item.get('summary'):
            require(all(lang in item['summary'] for lang in LANGUAGES), f'Missing teaching summary translation: {item["id"]}')
        for field, collection in [('course', 'courses'), ('organization', 'organizations'), ('role', 'roles')]:
            require(item[field] in DATA[collection], f'Unknown {field}: {item["id"]}')
        for date in [item['start'], item['end']]:
            require(date is None or re.fullmatch(r'\d{4}(?:-(?:0[1-9]|1[0-2]))?', date), f'Invalid date: {date}')
        require(item['end'] is None or item['end'] >= item['start'], f'Reversed period: {item["id"]}')
        validate_planned_end(item)
    detail_ids=[]
    for item in DATA['teaching']:
        for detail in item.get('details', []):
            detail_ids.append(detail['id'])
            require(re.fullmatch(r'[a-zA-Z0-9_-]+', detail['id']), 'Invalid career detail ID')
            require(detail['role'] in DATA['roles'], f'Unknown detail role: {detail["id"]}')
            require(all(lang in detail[field] for field in ['title', 'curriculum'] for lang in LANGUAGES), f'Missing career detail translation: {detail["id"]}')
            for source in [detail]+detail.get('tracks',[]):
                if 'focus' in source:
                    require(all(isinstance(source['focus'].get(lang), str) and source['focus'][lang].strip()
                                for lang in LANGUAGES), f'Missing school focus translation: {detail["id"]}')
                for title in source.get('programTitles',[]):
                    require(all(isinstance(title.get(lang),str) and title[lang].strip() for lang in LANGUAGES),
                            f'Missing verified course title translation: {detail["id"]}')
                    if 'verifiedTeachingStart' in title:
                        require(detail['start'] <= title['verifiedTeachingStart'] <= title['verifiedTeachingEnd'] <= detail['end'],
                                f'Course title scope outside school period: {detail["id"]}')
            if DATA['courses'][item['course']].get('showSchoolPrograms'):
                require(all(lang in detail.get('programTitle', {}) for lang in LANGUAGES),
                        f'Missing school program title: {detail["id"]}')
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
    for item in DATA.get('otherExperience', []):
        for reference in item.get('teachingAssignments', []):
            require(reference in teaching_ids, f'Unknown experience teaching assignment: {reference}')
            source = next(row for row in DATA['teaching'] if row['id'] == reference)
            require(source['organization'] == item.get('organization'), f'Mismatched assignment organization: {reference}')
        require(item.get('group', 'development') in {group for group, _ in EXPERIENCE_GROUPS},
                f'Unknown experience group: {item["id"]}')
    for item in DATA['teaching'] + [detail for row in DATA['teaching'] for detail in row.get('details', [])]:
        if item.get('activeMonths'):
            months = item['activeMonths']
            require(months == sorted(set(months)) and all(re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', month) for month in months), f'Invalid active months: {item["id"]}')
            require(months[0] == item['start'] and months[-1] == item['end'], f'Active months do not match period: {item["id"]}')
    dated_details=[detail for item in DATA['teaching'] for detail in item.get('details', [])]
    for item in dated_details+DATA.get('otherExperience', []):
        for date in [item['start'], item['end']]:
            require(date is None or re.fullmatch(r'\d{4}(?:-(?:0[1-9]|1[0-2]))?', date), f'Invalid career date: {date}')
        require(item['end'] is None or item['end'] >= item['start'], f'Reversed career period: {item["id"]}')
        validate_planned_end(item)
    def validate_topics(topics, context):
        require(isinstance(topics, list) and 0 < len(topics) <= 2
                and all(isinstance(tag, dict) and all(isinstance(tag.get(lang), str)
                        and tag[lang].strip() for lang in LANGUAGES) for tag in topics),
                f'Invalid {context} topics')
        for lang in LANGUAGES:
            require(len({tag[lang] for tag in topics}) == len(topics), f'Invalid {context} topics')
    validate_topics(DATA.get('researchTopics', []), 'research')
    for paper in DATA['papers']:
        validate_topics(paper.get('topics', []), 'paper')
        require(bool(paper['authors']), f'Missing authors: {paper["id"]}')
        require(all(author in DATA['authors'] for author in paper['authors']), f'Unknown author: {paper["id"]}')
        overrides = paper.get('authorOverrides', {})
        require(isinstance(overrides, dict) and set(overrides) <= set(paper['authors']),
                f'Unknown author override: {paper["id"]}')
        for author, values in overrides.items():
            require(isinstance(values, dict) and bool(values)
                    and set(values) <= {'name', 'initials', 'bibtex'}
                    and all(isinstance(value, str) and value.strip() for value in values.values()),
                    f'Invalid author override: {paper["id"]}/{author}')
        require(paper.get('authorRole') in [None, 'first'], f'Unknown author role: {paper["id"]}')
        if paper.get('authorRole') == 'first':
            require(DATA['authors'][paper['authors'][0]].get('profile'), f'First-author role conflicts with author order: {paper["id"]}')
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
    """Use each paper's source spelling, including its citation-name variants."""
    names = []
    for author in paper['authors']:
        override = paper.get('authorOverrides', {}).get(author, {})
        if field in override:
            names.append(override[field])
        elif field == 'name' and DATA['authors'][author].get('profile'):
            names.append(localized(DATA['profile']['name'], 'en'))
        else:
            names.append(DATA['authors'][author][field])
    return names


def display_authors(paper, lang):
    """Annotate the confirmed profile-author role without changing citations."""
    role = text('label.first_author', lang) if paper.get('authorRole') == 'first' else ''
    return [name + (' (' + role + ')' if role and DATA['authors'][author].get('profile') else '')
            for author, name in zip(paper['authors'], authors(paper))]


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

