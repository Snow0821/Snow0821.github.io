"""Home, portfolio and career views built from the public record."""
from content import (
    DATA, current_role_records, cv_filename, detail_program_titles, localized,
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
        entries.append(f'<article class="document"><h3>{label("home."+key,lang)}</h3><p>{label("home."+key+"_desc",lang)}</p><div class="document-links">{pdf}{read}</div></article>')
    return f'<section class="documents" id="documents"><h2>{label("home.docs",lang)}</h2><div class="document-list">{"".join(entries)}</div></section>'


def home(lang):
    works, career = route('work',lang), route('career',lang)
    chart = f'''<figure class="quant-figure">
<a class="figure-link" href="{works}#paper-2025">
<img src="/assets/ternary-quantization.png" width="1536" height="924" alt="{label('figure.alt',lang)}" decoding="async">
<div class="figure-caption"><div><strong>{label('figure.name',lang)}</strong><span>{label('figure.caption',lang)}</span></div><span aria-hidden="true" class="figure-arrow">↗</span></div>
</a></figure>'''
    hero = f'''<section class="hero"><div class="hero-copy"><p class="profession">{label('hero.role',lang)}</p>
<h1><span>{label('hero.title1',lang)}</span><span>{label('hero.title2',lang)}</span></h1>
<p class="introduction">{label('hero.body',lang)}</p><div class="hero-actions">
<a class="primary-link" href="{works}">{label('hero.explore',lang)} <span aria-hidden="true">→</span></a>
<a class="secondary-link" href="/assets/{h(cv_filename(lang))}" download>{label('hero.cv',lang)} <span aria-hidden="true">↓</span></a>
</div></div>{chart}</section>'''
    activities = []
    for position in current_role_records():
        record = position.get('courseRecord') or position
        organization = localized(DATA['organizations'][position['organization']],lang)
        role = localized(position['title'],lang)
        activities.append(link_line(career+'#record-'+record['id'], role,
                                    organization+' · '+period(record,lang)))
    papers = sorted(DATA['papers'],key=lambda p:p['year'],reverse=True)
    projects = [p for p in DATA['otherExperience'] if p.get('portfolioProject') and p.get('url')]
    selected = []
    if papers:
        p = papers[0]
        selected.append(link_line(works+'#paper-'+p['id'],paper_title(p,lang),
                                  str(p['year'])+' · '+localized(DATA['venues'][p['venue']]['short'],lang)))
    if projects:
        p = projects[0]
        selected.append(link_line(works+'#project-'+p['id'],localized(p['title'],lang),
                                  text('works.kind_project',lang)+' · '+localized(p['role'],lang)))
    return hero+f'''<div class="home-index">
<section><div class="section-heading"><h2>{label('section.current_roles',lang)}</h2>{anchor(career,text('home.allcareer',lang),'section-link')}</div>{''.join(activities)}</section>
<section><div class="section-heading"><h2>{label('home.selected',lang)}</h2>{anchor(works,text('home.allwork',lang),'section-link')}</div>{''.join(selected)}</section>
</div>'''+documents(lang)


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


def portfolio(lang):
    papers = sorted(DATA['papers'],key=lambda p:p['year'],reverse=True)
    projects = sorted((p for p in DATA['otherExperience'] if p.get('portfolioProject')), key=lambda p:p['start'],reverse=True)
    groups = [('papers',text('works.papers',lang)),('projects',text('works.projects',lang))]
    publication_html = ''.join(paper_detail(p,lang) for p in papers)
    project_html = ''.join(project(p,lang) for p in projects)
    return page_head('nav.work','works.research_info',lang)+f'''<div class="directory">
{contents(groups,lang)}<div class="directory-body">{section_shell(*groups[0],publication_html)}{section_shell(*groups[1],project_html)}</div></div>'''


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
