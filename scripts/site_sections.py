"""Profile, education, interests, and teaching views built from shared records."""
from content import DATA, LANGUAGES, DEFAULT_LANGUAGE, localized, text, cv_filename, teaching_records, teaching_values, teaching_columns, teaching_title, detail_program_titles, school_program_groups, current_role_records, period, experience_records, EXPERIENCE_GROUPS
from html_components import h, pair, label, mapped, preview, fold, external_link, asset_icon


def profile():
    person=DATA['profile']
    actions=[]
    for link in person['links']:
        actions.append(external_link(link['url'],asset_icon(link['icon']),'action icon-action',link['label']))
    filename=cv_filename(DEFAULT_LANGUAGE)
    download_label=text('ui.download_cv',DEFAULT_LANGUAGE)
    actions.append(f'<a id="snow-cv-download" class="action icon-action cv-download cursor-interaction" href="assets/{h(filename)}" download="{h(filename)}" aria-label="{h(download_label)}" title="{h(download_label)}">{asset_icon("file-down.svg","file-icon")}<span class="cv-mark" aria-hidden="true">CV</span></a>')
    mail_icon='<svg class="mail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m3 7 9 6 9-6"></path></svg>'
    email=h(person['email'])
    return f'''<div class="cv-identity" data-block>
<h1>{pair(person['name'])}</h1>
<div class="roles">{''.join(pair(DATA['roles'][role]) for role in person['roles'])}</div>
<p class="cv-intro">{pair(person['intro'])}</p>
<div class="actions cv-contact">{''.join(actions)}</div>
<a class="contact-email cursor-interaction" href="mailto:{email}" aria-label="{h(text('ui.email',DEFAULT_LANGUAGE,email=person['email']))}">{mail_icon}<span>{email}</span></a>
</div>'''


def education():
    records=sorted(DATA['education'],key=lambda item:item['year'],reverse=True)
    rows=[]
    for item in records:
        title=mapped(lambda lang:h(localized(item['field'],lang))+f'<span class="degree-type">{h(localized(item["degree"],lang))}</span>')
        rows.append(f'<article class="cv-education" data-record data-education="{item["id"]}"><span class="cv-year">{item["year"]}</span><div><strong>{pair(title,markup=True)}</strong><p class="cv-sub">{pair(item["school"])}</p></div></article>')
    summary=''
    if records:
        latest=records[0]
        title=mapped(lambda lang:h(localized(latest['field'],lang))+f' <span class="preview-degree">· {h(localized(latest["degreeShort"],lang))}</span>')
        summary=preview(title,mapped(lambda lang:f'{localized(latest["institution"],lang)} · {latest["year"]}'),markup=True)
    return fold('snow-cv-education','section.education',len(records),''.join(rows),summary)


def qualifications():
    records=sorted(DATA['qualifications'],key=lambda item:item['year'],reverse=True)
    rows=[f'<article class="cv-education" data-record data-qualification="{item["id"]}"><span class="cv-year">{item["year"]}</span><div><strong>{pair(item["title"])}</strong><p class="cv-sub">{pair(item["field"])}</p></div></article>' for item in records]
    summary=preview(records[0]['title'],mapped(lambda lang:f'{records[0]["year"]} · {localized(records[0]["field"],lang)}')) if records else ''
    return fold('snow-cv-qualifications','section.qualifications',len(records),''.join(rows),summary)


def current_roles():
    records = current_role_records()
    if not records:
        return ''
    rows = []
    for item in records:
        organization = DATA['organizations'][item['organization']]
        dates = mapped(lambda lang: period(item, lang, include_planned_notice=False))
        context = f'<p class="current-role-context">{pair(item["context"])}</p>' if item.get('context') else ''
        rows.append(f'<li class="current-role" data-current-role="{h(item["id"])}"><p class="current-role-date">{pair(dates)}</p><div><h3>{pair(item["title"])}</h3>{context}<p class="current-role-organization">{pair(organization)}</p></div></li>')
    return f'<section class="current-roles" aria-labelledby="snow-current-roles-heading" data-block><h2 class="cv-heading" id="snow-current-roles-heading">{label("section.current_roles")}</h2><ul class="current-role-list">{"".join(rows)}</ul></section>'


def teaching_preview(records):
    if not records:
        return ''
    item=records[0]
    title=mapped(lambda lang:teaching_values(item,lang)['primary'])
    detail=mapped(lambda lang:f'{period(item,lang)} · {teaching_values(item,lang)["organization"]} · {localized(DATA["roles"][item["role"]],lang)}')
    return preview(title,detail)


def teaching_table(records, summary=False):
    headings = ''.join('<th scope="col">'+label(key)+'</th>' for key in
                       ['label.period','label.org_program','label.role_course'])
    rows = ''.join(teaching_entry(item,summary) for item in records)
    return ('<table class="teaching-table" role="table"><caption class="sr-only">'+label('section.teaching_history')+'</caption>'
            '<colgroup><col class="teaching-period-col"><col class="teaching-provider-col"><col class="teaching-course-col"></colgroup>'
            '<thead><tr>'+headings+'</tr></thead><tbody>'+rows+'</tbody></table>')


def teaching_entry(item, summary):
    values={lang:teaching_columns(item,lang) for lang in LANGUAGES}
    field=lambda key:{lang:value[key] for lang,value in values.items()}
    provenance=f' data-source-program="{h(item["sourceId"])}"' if item.get('sourceId') else ''
    dates=mapped(lambda lang:period(item,lang).replace(' (','\n('))
    provider = '<strong class="teaching-program">'+pair(field('provider'))+'</strong>' if any(field('provider').values()) else ''
    organization = '<p class="teaching-organization">'+pair(field('organization'))+'</p>'
    schools=f'<p class="cv-sub teaching-schools">{pair(item["schoolSummary"])}</p>' if item.get('schoolSummary') else ''
    program_groups = {lang:school_program_groups(item,lang) for lang in LANGUAGES}
    if any(program_groups.values()):
        schools = '<div class="teaching-programs">'+''.join(f'<p><strong>{pair({lang:(" · ".join(program_groups[lang][index]["titles"]) or values[lang]["subject"]) for lang in LANGUAGES})}</strong> <span class="cv-sub">{pair({lang:" · ".join(program_groups[lang][index]["schools"]) for lang in LANGUAGES})}</span></p>' for index in range(len(program_groups[DEFAULT_LANGUAGE])))+'</div>'
    duty=f'<p class="cv-sub">{pair(item["summary"])}</p>' if item.get('summary') else ''
    course=DATA['courses'][item['course']]
    note = '<p class="history-note">'+pair(course['note'])+'</p>' if not summary and not (schools or duty) and course.get('note') else ''
    details='' if summary else teaching_details(item)
    toggle=career_toggle(item['id'],mapped(lambda lang:teaching_values(item,lang)['primary'])) if details else ''
    title_tag='strong' if summary else 'h4'
    title=f'<{title_tag} class="teaching-course-title">{pair(field("subject"))}</{title_tag}>'
    course_title=f'<div class="teaching-course-heading">{title}{toggle}</div>'
    role='<p class="teaching-role">'+pair(field('role'))+'</p>'
    cls='teaching-row' if summary else 'history-entry teaching-row'
    return f'''<tr class="{cls}"{provenance} data-record data-teaching="{h(item['id'])}" role="row">
<td class="teaching-period" role="cell"><span class="teaching-cell-label" aria-hidden="true">{label('label.period')}</span>{pair(dates)}</td>
<td class="teaching-provider" role="cell"><span class="teaching-cell-label" aria-hidden="true">{label('label.org_program')}</span>{provider}{organization}</td>
<td class="teaching-course" role="cell"><span class="teaching-cell-label" aria-hidden="true">{label('label.role_course')}</span>{course_title}{role}{duty}{schools}{note}{details}</td></tr>'''


def career_toggle(record_id, title):
    target='snow-career-'+record_id
    aria=text('ui.expand_career',DEFAULT_LANGUAGE,title=localized(title,DEFAULT_LANGUAGE))
    titles=''.join(f' data-title-{lang}="{h(localized(title,lang))}"' for lang in LANGUAGES)
    return f'<button type="button" class="career-toggle cursor-interaction" aria-expanded="false" aria-controls="{h(target)}" aria-label="{h(aria)}"{titles}><span class="career-sign" aria-hidden="true">+</span></button>'


def teaching_details(item):
    records=item.get('details', [])
    if not records:
        return ''
    rows=[]
    for detail in records:
        meta=mapped(lambda lang:f"{period(detail,lang)} · {localized(DATA['roles'][detail['role']],lang)}")
        note=''.join(f'<p class="career-detail-note">{pair(detail[key])}</p>' for key in ['note','periodNote'] if detail.get(key))
        source=f' data-source-detail="{h(detail["sourceDetail"])}"' if detail.get('sourceDetail') else ''
        program=''
        for title in detail_program_titles(detail):
            scope = ''
            if title.get('verifiedTeachingStart'):
                scope = ' '+pair(mapped(lambda lang:period({'start':title['verifiedTeachingStart'],'end':title['verifiedTeachingEnd']},lang)))
            program += f'<p class="verified-course-title"><strong>{pair(title)}</strong>{scope}</p>' 
        curriculum = ''.join(f'<p><strong>{pair(track["title"])}</strong></p><p>{pair(track["curriculum"])}</p>'
                             for track in detail.get('courseTracks', [])) or f'<p>{pair(detail["curriculum"])}</p>'
        rows.append(f'<li data-career-detail="{h(detail["id"])}"{source}><h5>{pair(detail["title"])}</h5><div class="career-detail-meta">{pair(meta)}</div>{program}{curriculum}{note}</li>')
    return f'<div class="career-details" id="snow-career-{h(item["id"])}" hidden><ul>{"".join(rows)}</ul></div>'


def other_experience(summary=False, group='development'):
    records=experience_records(group)
    rows=[]
    for item in records:
        date=pair(mapped(lambda lang:period(item,lang)))
        title=pair(item['title'])
        if item.get('url'):
            title=f'<a href="{h(item["url"])}" target="_blank" rel="noopener noreferrer">{title}</a>'
        if summary:
            rows.append(f'<article class="cv-job" data-record data-other-experience="{h(item["id"])}"><span class="cv-date">{date}</span><div><strong>{title}</strong><p class="cv-sub">{pair(item["role"])}</p></div></article>')
            continue
        note=f'<p class="career-detail-note">{pair(item["note"])}</p>' if item.get('note') else ''
        description=f'<p class="history-note">{pair(item["description"])}</p>' if item.get('description') else ''
        has_details=bool(description or note)
        details=f'<div class="career-details" id="snow-career-{h(item["id"])}" hidden>{description}{note}</div>' if has_details else ''
        toggle=career_toggle(item['id'],item['title']) if has_details else ''
        rows.append(f'<article class="history-entry" data-other-experience="{h(item["id"])}"><div class="history-title"><h4>{title}</h4>{toggle}</div><div class="history-meta">{pair(item["role"])}{date}</div>{details}</article>')
    if summary:
        return ''.join(rows)
    summary_html=preview(records[0]['title'],mapped(lambda lang:f"{period(records[0],lang)} · {localized(records[0]['role'],lang)}")) if records else ''
    return fold('snow-history-'+group,dict(EXPERIENCE_GROUPS)[group],len(records),''.join(rows),summary_html,classes='history-group history-'+group,level=3) if records else ''


def teaching_list(records, summary=False):
    result=[]
    for current,key in [(True,'group.current'),(False,'group.previous')]:
        selected=[item for item in records if (item['end'] is None) == current]
        if not selected:
            continue
        cls='cv-group-label' if summary else 'history-status'
        result.append(f'<p class="{cls}">{label(key)}</p>')
        result.append(teaching_table(selected,summary))
    return ''.join(result)


def teaching_summary():
    records=teaching_records()
    groups=[]
    for group in DATA['teachingGroups']:
        selected=teaching_records(group['id'])
        if selected:
            groups.append(f'<h3 class="cv-group-label">{label(group["label"])}</h3>'+teaching_table(selected,True))
    for group, heading in EXPERIENCE_GROUPS:
        if experience_records(group):
            groups.append(f'<h3 class="cv-group-label">{label(heading)}</h3>'+other_experience(summary=True, group=group))
    pending=unclassified_teaching(summary=True)
    if pending:
        groups.append(pending)
    count=len(records)+len(DATA.get('otherExperience',[]))
    return fold('snow-cv-career','section.teaching',count,''.join(groups),teaching_preview(records),classes='cv-section cv-career',short_key='section.teaching_tab')


def teaching_detail():
    groups=[]
    for group in DATA['teachingGroups']:
        records=teaching_records(group['id'])
        if not records:
            continue
        groups.append(fold('snow-history-'+group['id'],group['label'],None,teaching_list(records),teaching_preview(records),classes='history-group',level=3,short_key=group['shortLabel']))
    groups.extend(other_experience(group=group) for group, _ in EXPERIENCE_GROUPS)
    return '<div class="history-columns">'+''.join(groups)+'</div>'+unclassified_teaching()


def unclassified_teaching(summary=False):
    records=teaching_records('unclassified')
    if not records:
        return ''
    heading=f'<p class="cv-group-label">{label("label.unclassified")}</p>'
    note='' if summary else f'<p class="career-detail-note">{label("label.unclassified_note")}</p>'
    return '<aside class="career-unclassified">'+heading+note+teaching_table(records,summary)+'</aside>'


def profile_link(link_id, label_key, primary=False):
    link=next(item for item in DATA['profile']['links'] if item['id']==link_id)
    return external_link(link['url'],label(label_key)+'<span aria-hidden="true">↗</span>','action'+(' primary' if primary else ''))

