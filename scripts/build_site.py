"""Compose the static page from small views and one shared content model."""
import json
import re
from content import ROOT, DATA, LANGUAGES, DEFAULT_LANGUAGE, LOCALES, localized, text, cv_filename, reference, bibtex, year_range, validate, write_if_changed
from html_components import h, pair, label, mapped, preview, fold
import site_sections as sections
import publications


def navigation():
    tabs=[]
    for key,full,short in [('home','nav.home',None),('interests','nav.interests','nav.interests_short'),('publications','nav.publications','nav.publications_short'),('teaching','nav.teaching',None)]:
        selected=key=='home'
        title=label(full) if not short else f'<span class="desktop-only">{label(full)}</span><span class="mobile-only">{label(short)}</span>'
        tabs.append(f'<button type="button" class="tab cursor-interaction" id="snow-tab-{key}" role="tab" aria-selected="{str(selected).lower()}" aria-controls="snow-panel-{key}" data-tab="{key}" tabindex="{0 if selected else -1}">{title}</button>')
    return '\n'.join(tabs)


def language_control():
    current=next(item for item in DATA['languages'] if item['code']==DEFAULT_LANGUAGE)
    next_code=LANGUAGES[(LANGUAGES.index(DEFAULT_LANGUAGE)+1)%len(LANGUAGES)]
    aria=text('ui.current_language',DEFAULT_LANGUAGE,name=current['name'])+' '+text('ui.switch_to',next_code)
    title=current['name']+' · '+text('ui.switch_to',next_code)
    flags=''.join(f'<img data-l="{h(item["code"])}" src="{h(item["flag"])}" alt="" width="24" height="18"'+(' hidden aria-hidden="true"' if item['code']!=DEFAULT_LANGUAGE else '')+'>' for item in DATA['languages'])
    return f'<button type="button" class="language cursor-interaction" id="snow-language" aria-label="{h(aria)}" title="{h(title)}"><span class="pair language-flags" aria-hidden="true">{flags}</span></button>'


def build():
    validate()
    papers=sorted(DATA['papers'],key=lambda item:(item['year'],item['month'] or 0),reverse=True)
    publication_preview=''
    if papers:
        latest=papers[0]
        publication_preview=preview(mapped(lambda lang:f'{latest["year"]} · {localized(DATA["venues"][latest["venue"]]["short"],lang)}'),latest['title'])
    citation_templates=[]
    for paper in papers:
        for lang in LANGUAGES:
            citation_templates.append(f'<template id="snow-ref-{paper["id"]}-{lang}">{h(reference(paper,lang))}</template>')
        citation_templates.append(f'<template id="snow-bib-{paper["id"]}">{h(bibtex(paper))}</template>')
    runtime={
        'defaultLanguage':DEFAULT_LANGUAGE,'languages':DATA['languages'],
        'messages':{lang:{key[3:]:value for key,value in LOCALES[lang].items() if key.startswith('ui.')} for lang in LANGUAGES},
        'pdfs':{lang:{'href':'assets/'+cv_filename(lang),'filename':cv_filename(lang)} for lang in LANGUAGES},
        'email':DATA['profile']['email']}
    names=' · '.join(dict.fromkeys(localized(DATA['profile']['name'],lang) for lang in LANGUAGES))
    roles=' and '.join(localized(DATA['roles'][role],'en') for role in DATA['profile']['roles'])
    slots={
        'default_language':h(DEFAULT_LANGUAGE),'portfolio_label':h(text('ui.portfolio',DEFAULT_LANGUAGE)),
        'page_title':h(names+' | Research & Teaching'),
        'meta_description':h(names+' — '+roles+'. Research interests, publications, teaching experience, and CV.'),
        'navigation':navigation(),'language_control':language_control(),
        'profile':sections.profile(),'education':sections.education(),'qualifications':sections.qualifications(),
        'interest_summary':sections.interest_summary(),'interest_detail':sections.interest_detail(),
        'publication_summary':fold('snow-cv-papers','section.publications',len(papers),'\n'.join(map(publications.summary,papers)),publication_preview),
        'publication_detail':'\n'.join(map(publications.detail,papers)),
        'publication_range':f'{year_range(papers)} · {len(papers)}',
        'teaching_summary':sections.teaching_summary(),'teaching_detail':sections.teaching_detail(),
        'teaching_range':f'{year_range(DATA["teaching"],teaching=True)} · {len(DATA["teaching"])}',
        'github_link':sections.profile_link('github','action.github'),
        'teaching_link':sections.profile_link('linkedin','action.teaching_inquiries',True),
        'last_updated':label('label.updated')+f'<time datetime="{h(DATA["updated"])}">{h(DATA["updated"].replace("-","."))}</time>',
        'citations':'\n'.join(citation_templates),
        'runtime_config':json.dumps(runtime,ensure_ascii=False).replace('<','\\u003c'),
    }
    template=(ROOT/'src/index.template.html').read_text()
    def replace(match):
        key=match[1]
        return label(key[6:]) if key.startswith('label:') else slots[key]
    result=re.sub(r'\{\{([^{}]+)\}\}',replace,template)
    changed=write_if_changed(ROOT/'index.html','\n'.join(line.rstrip() for line in result.splitlines())+'\n')
    print('Built index.html' if changed else 'index.html unchanged')


if __name__=='__main__':
    build()
