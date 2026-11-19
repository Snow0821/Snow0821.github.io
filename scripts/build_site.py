"""Publish three directly addressable, bilingual static pages."""
import hashlib
import re

from content import DATA, LANGUAGES, ROOT, localized, text, validate, write_if_changed
from design import css_tokens
from html_components import footer, h, nav, route
import site_sections


def build():
    validate()
    template = (ROOT/'src/index.template.html').read_text()
    origin = DATA['profile']['portfolioUrl'].rstrip('/')
    versions = {name: hashlib.sha256((ROOT/'assets'/('site.'+name)).read_bytes()).hexdigest()[:12]
                for name in ('css', 'js')}
    for lang in LANGUAGES:
        for page, builder in [('home',site_sections.home),('work',site_sections.portfolio),('career',site_sections.career)]:
            path = route(page, lang)
            person = localized(DATA['profile']['name'],lang)
            title = (person+' · '+text('hero.role',lang) if page=='home'
                     else text('nav.'+page,lang)+' · '+person)
            description = {'home':'meta.home','work':'works.research_info','career':'career.intro'}[page]
            alternate = [f'<link rel="alternate" hreflang="{code}" href="{origin}{route(page,code)}">' for code in LANGUAGES]
            alternate.append(f'<link rel="alternate" hreflang="x-default" href="{origin}{route(page,"ko")}">')
            context = {'lang':lang,'page':page,'title':h(title),'description':h(text(description,lang)),
                       'canonical':origin+path,'alternates':'\n'.join(alternate),'tokens':css_tokens(),
                       'cssversion':versions['css'],'jsversion':versions['js'],
                       'skip':h(text('nav.skip',lang)),'header':nav(page,lang),'content':builder(lang),'footer':footer(lang)}
            html = re.sub(r'\{\{([a-z]+)\}\}',lambda m:context[m[1]],template)
            write_if_changed(ROOT/path.strip('/')/'index.html',html)


if __name__ == '__main__':
    build()
