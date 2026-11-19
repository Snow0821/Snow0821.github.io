"""Shared, escaped markup for the static portfolio pages."""
from html import escape

from content import DATA, localized, text


def h(value):
    return escape(str(value), quote=True)


def route(page, lang):
    directory = {'home': '', 'work': 'portfolio/', 'career': 'career/'}[page]
    return ('/' if lang == 'ko' else f'/{lang}/') + directory


def label(key, lang):
    return h(text(key, lang))


def local(value, lang):
    return h(localized(value, lang))


def anchor(href, caption, css='', arrow=False):
    style = f' class="{h(css)}"' if css else ''
    icon = '<span class="arrow" aria-hidden="true">↗</span>' if arrow else ''
    return f'<a{style} href="{h(href)}">{h(caption)}{icon}</a>'


def nav(page, lang):
    links = []
    for target in ('home', 'work', 'career'):
        state = ' aria-current="page"' if page == target else ''
        links.append(f'<a href="{route(target, lang)}"{state}>{label("nav."+target, lang)}</a>')
    other = 'en' if lang == 'ko' else 'ko'
    lang_name = 'EN' if other == 'en' else '한국어'
    switch = f'<a class="language-link" href="{route(page, other)}" hreflang="{other}" lang="{other}" aria-label="{label("nav.alt",lang)}">{lang_name}</a>'
    home = route('home', lang)
    name = local(DATA['profile']['name'], lang)
    return f'''<header class="site-header"><div class="shell header-inner">
<a href="{home}" class="wordmark">{name}</a>
<nav class="site-nav" aria-label="{label("nav.label",lang)}">{"".join(links)}</nav>{switch}
</div></header>'''


def footer(lang):
    who = DATA['profile']
    networks = [anchor(item['url'], item['label']) for item in who['links']]
    networks.append(anchor('mailto:'+who['email'], text('footer.contact',lang)))
    date = h(DATA['updated'])
    return f'''<footer class="site-footer"><div class="shell footer-inner">
<div class="footer-id"><strong>{local(who['name'],lang)}</strong><span>{label('label.updated',lang)} <time datetime="{date}">{date.replace('-', '.')}</time></span></div>
<nav class="social-links" aria-label="{label('footer.links',lang)}">{"".join(networks)}</nav>
</div></footer>'''
