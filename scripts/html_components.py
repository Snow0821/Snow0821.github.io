"""Small HTML helpers shared by every section."""
from html import escape
from content import LANGUAGES, DEFAULT_LANGUAGE, localized, text


def h(value):
    return escape(str(value), quote=True)


def translations(values, markup=False):
    parts=[]
    for lang in LANGUAGES:
        value=localized(values,lang)
        hidden=' hidden aria-hidden="true"' if lang != DEFAULT_LANGUAGE else ''
        content=value if markup else h(value).replace('\n','<br>')
        parts.append(f'<span data-l="{lang}" lang="{lang}"{hidden}>{content}</span>')
    return ''.join(parts)


def pair(values, classes='', markup=False):
    return f'<span class="pair {classes}">{translations(values,markup)}</span>'


def label(key):
    return pair({lang:text(key,lang) for lang in LANGUAGES})


def mapped(function):
    return {lang:function(lang) for lang in LANGUAGES}


def preview(title, detail, markup=False):
    return f'<p class="fold-preview">{pair(title,"preview-title",markup)}{pair(detail,"preview-line")}</p>'


def fold(section_id, key, count, content, preview_html='', *, classes='cv-section', level=2, short_key=None):
    heading=mapped(lambda lang: h(text(key,lang)))
    compact=mapped(lambda lang:h(text(short_key or key,lang)))
    badge=f' <small>{count}</small>'
    heading={lang:value+badge for lang,value in heading.items()}
    compact={lang:value+badge for lang,value in compact.items()}
    return f'''<section class="{classes} fold-section" data-expanded="false" data-block>
<h{level} class="cv-heading desktop-only">{pair(heading,markup=True)}</h{level}>
<button type="button" class="fold-toggle mobile-only cursor-interaction" aria-expanded="false" aria-controls="{section_id}">{pair(compact,markup=True)}<span class="fold-sign" aria-hidden="true">+</span></button>
{preview_html}<div class="fold-content" id="{section_id}">{content}</div>
</section>'''


def external_link(url, content, classes='action', label_text=None):
    attrs=f' aria-label="{h(label_text)}" title="{h(label_text)}"' if label_text else ''
    return f'<a class="{classes} cursor-interaction" href="{h(url)}" target="_blank" rel="noopener noreferrer"{attrs}>{content}</a>'
