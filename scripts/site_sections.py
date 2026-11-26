"""Home, portfolio and career views built from the public record."""
import json

from content import (
    DATA, ROOT, current_role_records, cv_filename, detail_program_titles, localized,
    period, teaching_columns, teaching_detail_context, teaching_records, text,
)
from html_components import anchor, h, label, local, route
from publications import detail as paper_detail, paper_title


CAREER_SECTIONS = ('education', 'employment', 'teaching', 'training', 'credentials', 'awards', 'writing')


def link_line(url, title, metadata):
    return f'<a class="index-link" href="{h(url)}"><div><p class="index-meta">{h(metadata)}</p><h3>{h(title)}</h3></div><span class="index-arrow" aria-hidden="true">↗</span></a>'


def documents(lang='ko'):
    core = '/assets/'
    records = [
        ('docprofile', None, 'Choi-Soon-Ho-Instructor-Profile-KO.pdf', 'KO'),
        ('doccv', '/cv/' if lang == 'ko' else None, cv_filename(lang), lang.upper()),
        ('doccareer', '/career-statement/', 'Choi-Soon-Ho-Career-Statement-KO.pdf', 'KO'),
    ]
    entries = []
    for key, screen, file, language in records:
        read = (anchor(screen, text('home.read',lang) + (' · KO' if lang != 'ko' else '')) if screen else '')
        pdf = f'<a href="{core}{h(file)}" download>{label("home.pdf",lang)} <span class="file-language">{language}</span></a>'
        if key == 'doccv':
            other = 'en' if lang == 'ko' else 'ko'
            pdf += f'<a href="{core}{h(cv_filename(other))}" download>{label("index.cv"+other,lang)} (PDF)</a>'
        entries.append(f'<article class="document"><h3>{label("home."+key,lang)}</h3><p>{label("home."+key+"_desc",lang)}</p><div class="document-links">{pdf}{read}</div></article>')
    return f'<section class="documents" id="documents"><h2>{label("home.docs",lang)}</h2><div class="document-list">{"".join(entries)}</div></section>'


def home(lang):
    works, career = route('work', lang), route('career', lang)
    incheon = next(row for row in teaching_records() if row['course'] == 'incheon-creator')
    course = teaching_columns(incheon, lang)
    paper = next(p for p in DATA['papers'] if p['id'] == '2026')
    paper_url = works + '#paper-' + paper['id']
    paper_name = paper_title(paper, lang).split(':')[0]
    hero = f'''<section class="hero editorial-hero"><div class="hero-copy">
<p class="profession" lang="en">AI · COMPUTER SCIENCE</p>
<h1><span>{label('hero.title1',lang)}</span><span>{label('hero.title2',lang)}</span></h1>
<p class="introduction">{label('editor.identity',lang)}</p><div class="hero-actions">
{anchor(works+'?type=education',text('editor.teach',lang),'primary-link')}
{anchor(works+'?type=research',text('editor.research',lang),'secondary-link')}</div></div>
<a class="research-cover" href="{paper_url}" aria-label="{h(paper_title(paper,lang))}">
<span class="cover-art" aria-hidden="true"></span>
<span class="cover-title" lang="en">{h(paper_name)}</span>
<span class="cover-caption">{label('editor.cover',lang)}</span></a></section>'''
    selected = f'''<section class="selected-work"><div class="section-heading">
<h2>{label('home.selected',lang)}</h2>{anchor(works,text('home.allwork',lang),'section-link')}</div>
<div class="work-pair">{link_line(career+'#record-'+incheon['id'],course['subject'],text('index.education',lang)+'　/　'+course['provider'])}
{link_line(paper_url,paper_name,text('index.research',lang)+'　/　'+text('editor.researchShort',lang))}</div></section>'''
    chart = f'''<figure class="quant-figure"><a class="figure-link" href="{works}#paper-2025">
<img src="/assets/ternary-quantization.png" width="1536" height="924" alt="{label('figure.alt',lang)}" loading="lazy">
<div class="figure-caption"><div><strong>{label('figure.name',lang)}</strong><span>{label('figure.caption',lang)}</span></div></div></a></figure>'''
    activities = []
    for position in current_role_records():
        record = position.get('courseRecord') or position
        org = localized(DATA['organizations'][position['organization']],lang)
        activities.append(link_line(career+'#record-'+record['id'], localized(position['title'],lang),
                                    org+' · '+period(record,lang)))
    return hero + selected + f'''<div class="home-index">
<section><div class="section-heading"><h2>{label('section.current_roles',lang)}</h2>
{anchor(career,text('home.allcareer',lang),'section-link')}</div><p class="role-summary">{label('hero.body',lang)}</p>{''.join(activities)}</section>
<section><div class="section-heading"><h2>{label('editor.figureSection',lang)}</h2></div>{chart}</section></div>''' + documents(lang)


def page_head(title, desc, lang):
    return f'<header class="page-intro"><h1>{label(title,lang)}</h1><p>{label(desc,lang)}</p></header>'


def section_shell(key, title, body):
    return f'<section class="directory-section" id="{h(key)}" aria-labelledby="heading-{h(key)}"><h2 id="heading-{h(key)}">{h(title)}</h2>{body}</section>'


def contents(entries, lang):
    links = ''.join(anchor('#'+key,title) for key,title in entries)
    return f'<nav class="contents" aria-label="{label("jump.sections",lang)}">{links}</nav>'


def project(item, lang):
    url = item.get('url')
    link = anchor(url,text('works.project_link',lang),'source-link',True) if url else ''
    return f'''<article class="record-row project" id="project-{h(item['id'])}">
<div class="row-margin"><span class="year">{h(period(item,lang))}</span></div><div><h3>{local(item['title'],lang)}</h3>
<p class="byline">{local(item['role'],lang)}</p><p>{local(item['description'],lang)}</p>{link}</div></article>'''


def portfolio_links(lang, papers, projects):
    rows = {}
    for item in sorted(teaching_records(), key=lambda x: x['start'], reverse=True):
        if item.get('careerCategory') == 'employment':
            continue
        fields = teaching_columns(item, lang)
        context = fields['audience'] or fields['provider'] or fields['organization']
        url = route('career',lang)+'#record-'+item['id']
        rows[item['id']] = ('education', url, fields['subject'], context+' · '+fields['role'])
    for paper in papers:
        title = paper_title(paper,lang).split(':')[0] if paper['id']=='2026' else paper_title(paper,lang)
        venue = localized(DATA['venues'][paper['venue']]['short'],lang)
        rows[paper['id']] = ('research', '#paper-'+paper['id'], title, str(paper['year'])+' · '+venue)
    for item in projects:
        rows[item['id']] = ('development', '#project-'+item['id'], localized(item['title'],lang),
                            localized(item['role'],lang)+' · '+period(item,lang))
    return rows


def index_rows(lang, rows):
    featured = ['incheon-ablearn-2026-11','2026','hanalife-2026-10','kimanna-capstone','algorithms-coderland-2023-03']
    ordered = dict.fromkeys([key for key in featured if key in rows] + list(rows))
    cards = []
    for key in ordered:
        kind, url, title, context = rows[key]
        cards.append(f'<li data-kind="{kind}"><a href="{h(url)}"><span class="kind">{label("index."+kind,lang)}</span>'
                     f'<span class="entry"><strong>{h(title)}</strong><small>{h(context)}</small></span>'
                     '<span class="entry-arrow" aria-hidden="true">↗</span></a></li>')
    return ''.join(cards)



def theme_tree(lang, rows, papers, projects):
    themes = json.loads((ROOT/'data/portfolio-themes.json').read_text())
    evidence = {x['id']: x['summary'] for x in [*papers, *teaching_records()]}
    evidence.update({x['id']: x['description'] for x in projects})
    cards = []
    seen = set()
    for number, theme in enumerate(themes, 1):
        root, children = theme['representative'], theme['related']
        keys = [root, *children]
        if len(keys) != len(set(keys)) or seen.intersection(keys) or any(key not in rows for key in keys):
            raise ValueError(f"Invalid portfolio theme entries: {theme['id']}")
        seen.update(keys)
        kind, url, title, _ = rows[root]
        if kind == 'research':
            title = paper_title(next(p for p in papers if p['id'] == root), lang)
        children_html = ''.join(
            f'<li>{anchor(rows[key][1],rows[key][2])}</li>' for key in children
        )
        heading = 'theme-' + theme['id']
        cards.append(f'''<li class="theme-branch" aria-labelledby="{h(heading)}">
<span class="theme-number" aria-hidden="true">{number:02d}</span>
<h3 id="{h(heading)}">{local(theme['title'],lang)}</h3>
<div class="theme-evidence">
<p class="theme-label">{label('themes.representative',lang)} <span aria-hidden="true">·</span> {label('index.'+kind,lang)}</p>
{anchor(url,title,'theme-lead')}
<p class="theme-summary">{local(evidence[root],lang)}</p>
<p class="theme-label theme-related">{label('themes.related',lang)}</p>
<ul class="theme-children">{children_html}</ul>
</div></li>''')
    return f'''<section class="theme-section" aria-labelledby="portfolio-themes">
<h2 id="portfolio-themes">{label('themes.title',lang)}</h2>
<div class="theme-intro"><p>{label('themes.intro',lang)}</p>{anchor('#all-activities',text('themes.all',lang))}</div>
<ol class="theme-branches">{"".join(cards)}</ol></section>'''


def portfolio(lang):
    papers = sorted(DATA['papers'], key=lambda p:p['year'], reverse=True)
    projects = sorted((p for p in DATA['otherExperience'] if p.get('portfolioProject')), key=lambda p:p['start'], reverse=True)
    rows = portfolio_links(lang, papers, projects)
    documents_list = [('home.docprofile','Choi-Soon-Ho-Instructor-Profile-KO.pdf'),
                      ('index.cvko',cv_filename('ko')), ('index.cven',cv_filename('en')),
                      ('home.doccareer','Choi-Soon-Ho-Career-Statement-KO.pdf')]
    docs = ''.join(anchor('/assets/'+file,text(key,lang),'rail-doc',True) for key,file in documents_list)
    filters = ''.join(f'<a class="index-filter" data-filter="{kind}" href="?type={kind}">{label("index."+kind,lang)}</a>'
                      for kind in ('all','education','research','development'))
    summary = h(text('index.count',lang,shown='{shown}',total='{total}'))
    more = h(text('index.more',lang,count='{count}'))
    catalogue = f'''<section class="catalogue" data-work-index data-count="{summary}" data-more="{more}" data-less="{label('index.less',lang)}">
<div class="index-identity"><div class="index-word" lang="en" aria-hidden="true">Index.</div><p>{label('index.intro',lang)}</p></div>
<aside class="index-docs"><h2>{label('home.docs',lang)}</h2>{docs}</aside>
<div class="index-main" id="activity-list"><h1>{label('index.title',lang)}</h1>
{theme_tree(lang,rows,papers,projects)}
<h2 id="all-activities" class="all-activities">{label('themes.all',lang)}</h2>
<nav class="index-filters" aria-label="{label('index.filters',lang)}" data-filters hidden>{filters}</nav>
<ul class="work-entries" aria-label="{label('index.list',lang)}">{index_rows(lang,rows)}</ul>
<div class="index-controls"><button type="button" class="more-entries" data-expand hidden></button>
<span class="result-count" data-result-count role="status"></span></div></div></section>'''
    publication_html = ''.join(paper_detail(p,lang) for p in papers)
    project_html = ''.join(project(p,lang) for p in projects)
    groups = [('papers',text('works.papers',lang)),('projects',text('works.projects',lang))]
    return catalogue + f'''<div class="directory work-directory">{contents(groups,lang)}<div class="directory-body">
{section_shell(*groups[0],publication_html)}{section_shell(*groups[1],project_html)}</div></div>'''


def record_row(record_id, date, title, metadata='', summary='', extra=''):
    meta = f'<p class="byline">{h(metadata)}</p>' if metadata else ''
    body = f'<p>{h(summary)}</p>' if summary else ''
    return f'''<article class="record-row" id="record-{h(record_id)}" data-record="{h(record_id)}">
<div class="row-margin"><span class="year">{h(date)}</span></div><div><h3>{h(title)}</h3>{meta}{body}{extra}</div></article>'''


def school_details(item, lang):
    rows = []
    for school in item.get('details',[]):
        role = localized(DATA['roles'][school['role']],lang)
        date = period(school,lang)
        courses = []
        for title in detail_program_titles(school):
            name = localized(title,lang)
            if title.get('verifiedTeachingStart'):
                name += ' ('+title['verifiedTeachingStart'].replace('-','.')+'–'+title['verifiedTeachingEnd'].replace('-','.')+')'
            if name not in courses:
                courses.append(name)
        programs = f'<p class="school-program">{h(" · ".join(courses))}</p>' if courses else ''
        if school.get('tracks'):
            detail = ''.join(f'<p>{local(t["title"],lang)} · {local(t["curriculum"],lang)}</p>' for t in school['tracks'])
        else:
            detail = f'<p>{local(school["curriculum"],lang)}</p>' if school.get('curriculum') else ''
        note = f'<p>{local(school["note"],lang)}</p>' if school.get('note') else ''
        rows.append(f'<li data-detail="{h(school["id"])}"><div class="school-head"><strong>{local(school["title"],lang)}</strong><span>{h(date)} · {h(role)}</span></div>{programs}{detail}{note}</li>')
    return '<ul class="school-list">'+''.join(rows)+'</ul>' if rows else ''


def teaching_row(item, lang):
    info = teaching_columns(item,lang)
    org = localized(item.get('operator') or DATA['organizations'][item['organization']],lang)
    # Enterprise clients and program operators have distinct roles in the record.
    title = ' · '.join(dict.fromkeys(v for v in [info['provider'],info['audience'],info['subject']] if v))
    meta = ' · '.join(dict.fromkeys([org,info['role']]))
    context = teaching_detail_context(item,lang)
    secondary = [part for part in context if part != org and part.split(': ')[-1] != org]
    relationships = '<p class="program-context">'+h(' / '.join(secondary))+'</p>' if secondary else ''
    description = localized(item['summary'],lang) if item.get('summary') else ''
    return record_row(item['id'],period(item,lang),title,meta,description,relationships+school_details(item,lang))


def experience_row(item, lang):
    return record_row(item['id'],period(item,lang),localized(item['title'],lang),
                      localized(item['role'],lang),localized(item['description'],lang))


def career(lang):
    rows = {key:[] for key in CAREER_SECTIONS}
    for school in sorted(DATA['education'],key=lambda s:s['year'],reverse=True):
        date = school.get('awardedOn',str(school['year'])).replace('-','.')
        rows['education'].append(record_row(school['id'],date,localized(school['school'],lang),
            localized(school['field'],lang)+' · '+localized(school['degree'],lang)))
    history = sorted(teaching_records(),key=lambda t:(t['end'] is None,t['end'] or '',t['start']),reverse=True)
    for item in history:
        group = 'employment' if item.get('careerCategory')=='employment' else 'teaching'
        rows[group].append(teaching_row(item,lang))
    for development in sorted(DATA.get('professionalDevelopment',[]),key=lambda p:p['date'],reverse=True):
        rows['training'].append(record_row(development['id'],development['date'].replace('-','.'),
            localized(development['title'],lang),localized(development['organization'],lang),
            localized(development['summary'],lang)))
    for item in sorted(DATA['otherExperience'],key=lambda v:v['start'],reverse=True):
        if item.get('careerCategory') in ('training','employment'):
            rows[item['careerCategory']].append(experience_row(item,lang))
    for item in DATA['qualifications']:
        rows['credentials'].append(record_row(item['id'],str(item['year']),localized(item['title'],lang),localized(item['field'],lang)))
    groups = [(key,text('career.'+key,lang)) for key in CAREER_SECTIONS]
    parts = [section_shell(key,title,''.join(rows[key]) or '<p class="empty">'+label('career.empty',lang)+'</p>') for key,title in groups]
    return page_head('nav.career','career.intro',lang)+f'<div class="directory">{contents(groups,lang)}<div class="directory-body">{"".join(parts)}</div></div>'
