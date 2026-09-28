"""Profile, education, interests, and teaching views built from shared records."""
from content import DATA, LANGUAGES, DEFAULT_LANGUAGE, localized, text, cv_filename, teaching_records, teaching_values, period
from html_components import h, pair, label, mapped, preview, fold, external_link


def profile():
    person=DATA['profile']
    actions=[]
    for link in person['links']:
        icon=f'<span class="icon" style="--icon:url(\'assets/{h(link["icon"])}\')" aria-hidden="true"></span>'
        actions.append(external_link(link['url'],icon,'action icon-action',link['label']))
    filename=cv_filename(DEFAULT_LANGUAGE)
    download_label=text('ui.download_cv',DEFAULT_LANGUAGE)
    actions.append(f'<a id="snow-cv-download" class="action icon-action cv-download cursor-interaction" href="assets/{h(filename)}" download="{h(filename)}" aria-label="{h(download_label)}" title="{h(download_label)}"><span class="icon file-icon" style="--icon:url(\'assets/file-down.svg\')" aria-hidden="true"></span><span class="cv-mark" aria-hidden="true">CV</span></a>')
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


def interest_summary():
    records=DATA['interests']
    rows=[f'<li><span class="interest-tag" lang="en">{h(item["tag"])}</span>{pair(item["name"])}</li>' for item in records]
    summary=preview(records[0]['tag'],records[0]['name']) if records else ''
    return fold('snow-cv-interests','section.interests',len(records),'<ul class="cv-interest-list">'+''.join(rows)+'</ul>',summary)


def interest_detail():
    return ''.join(f'<article class="interest" data-block><span class="interest-tag" lang="en">{h(item["tag"])}</span><h3>{pair(item["name"])}</h3><p>{pair(item["description"])}</p><div class="keywords desktop-only" lang="en">{h(" · ".join(item["keywords"]))}</div></article>' for item in DATA['interests'])


def teaching_preview(records):
    if not records:
        return ''
    item=records[0]
    title=mapped(lambda lang:localized(DATA['courses'][item['course']]['title'],lang).split(' · ')[0])
    detail=mapped(lambda lang:f'{period(item,lang)} · {localized(DATA["organizations"][item["organization"]],lang)} · {localized(DATA["roles"][item["role"]],lang)}')
    return preview(title,detail)


def teaching_entry(item, summary):
    values={lang:teaching_values(item,lang) for lang in LANGUAGES}
    field=lambda key:{lang:value[key] for lang,value in values.items()}
    if summary:
        return f'''<article class="cv-job" data-record data-teaching="{item['id']}">
<span class="cv-date">{pair(field('period'))}</span><div><strong>{pair(field('course'))}</strong>
<dl class="record-meta"><dt>{label('label.org')}</dt><dd>{pair(field('organization'))}</dd><dt>{label('label.role')}</dt><dd>{pair(field('role'))}</dd></dl></div></article>'''
    course=DATA['courses'][item['course']]
    note=f'<p class="history-note">{pair(course["note"])}</p>' if course.get('note') else ''
    org_role={lang:f'{value["organization"]} · {value["role"]}' for lang,value in values.items()}
    return f'<article class="history-entry" data-record data-teaching="{item["id"]}"><h4>{pair(field("course"))}</h4><div class="history-meta">{pair(org_role)}{pair(field("period"))}</div>{note}</article>'


def teaching_list(records, summary=False):
    result=[]
    for current,key in [(True,'group.current'),(False,'group.previous')]:
        selected=[item for item in records if (item['end'] is None) == current]
        if not selected:
            continue
        cls='cv-group-label' if summary else 'history-status'
        result.append(f'<p class="{cls}">{label(key)}</p>')
        result.extend(teaching_entry(item,summary) for item in selected)
    return ''.join(result)


def teaching_summary():
    records=teaching_records()
    return fold('snow-cv-career','section.teaching',len(records),teaching_list(records,True),teaching_preview(records),classes='cv-section cv-career',short_key='section.teaching_tab')


def teaching_detail():
    columns=[]
    wide=[]
    for group in DATA['teachingGroups']:
        records=teaching_records(group['id'])
        if not records:
            continue
        is_wide=group.get('layout') == 'wide'
        section=fold('snow-history-'+group['id'],group['label'],len(records),teaching_list(records),teaching_preview(records),classes='history-group'+(' history-pbl' if is_wide else ''),level=3,short_key=group['shortLabel'])
        (wide if is_wide else columns).append(section)
    return '<div class="history-columns">'+''.join(columns)+'</div>'+''.join(wide)


def profile_link(link_id, label_key, primary=False):
    link=next(item for item in DATA['profile']['links'] if item['id']==link_id)
    return external_link(link['url'],label(label_key)+'<span aria-hidden="true">↗</span>','action'+(' primary' if primary else ''))
