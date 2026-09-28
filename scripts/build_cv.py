from pathlib import Path
import os
from io import BytesIO
from content import ROOT, DATA, LANGUAGES, authors, venue_details, localized, text, teaching_records, teaching_values, cv_filename, validate, write_if_changed
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

FONT = Path(os.environ.get('CV_FONT_DIR', str(ROOT / 'fonts')))
OUTPUT = Path(os.environ.get('CV_OUTPUT_DIR', str(ROOT / 'assets')))
def configure_fonts():
    for name, filename in [('CV', 'NanumGothic-Regular.ttf'), ('CVB', 'NanumGothic-Bold.ttf')]:
        path = FONT / filename
        if not path.is_file():
            raise FileNotFoundError(f'Missing {path}. Set CV_FONT_DIR to your NanumGothic font directory.')
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily('CV', normal='CV', bold='CVB')
INK, MUTED, LINE, TINT = [HexColor(v) for v in ['#263238', '#56636A', '#D8DEE1', '#EFF3F5']]
WIDTH = A4[0] - 64
STYLES = {
    'name': ParagraphStyle('name', fontName='CVB', fontSize=22, leading=27, textColor=INK),
    'role': ParagraphStyle('role', fontName='CV', fontSize=10.3, leading=15, textColor=MUTED),
    'section': ParagraphStyle('section', fontName='CVB', fontSize=11.2, leading=15, textColor=INK),
    'body': ParagraphStyle('body', fontName='CV', fontSize=9.2, leading=13, textColor=INK),
    'field': ParagraphStyle('field', fontName='CVB', fontSize=9.2, leading=13, textColor=INK),
    'small': ParagraphStyle('small', fontName='CV', fontSize=8.2, leading=11.6, textColor=MUTED),
    'label': ParagraphStyle('label', fontName='CVB', fontSize=8.1, leading=10.5, textColor=MUTED),
    'paper': ParagraphStyle('paper', fontName='CVB', fontSize=9.5, leading=13.2, textColor=INK),
}

def p(text, style='body', markup=False):
    text = str(text).replace('–', '-').replace('—', '-').replace(' ,', ',')
    return Paragraph(text if markup else escape(text), STYLES[style])

def table(data, widths, header=True, pad=4):
    t = Table(data, colWidths=widths, hAlign='LEFT')
    commands = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), pad),
                ('BOTTOMPADDING', (0, 0), (-1, -1), pad),
                ('LINEBELOW', (0, 0), (-1, -1), .35, LINE)]
    if header:
        commands += [('BACKGROUND', (0, 0), (-1, 0), TINT)]
    t.setStyle(TableStyle(commands))
    return t

def section(title):
    return [Spacer(1, 11), p(title, 'section'), Spacer(1, 5)]

def build(lang):
    validate()
    configure_fonts()
    tr = lambda key: text(key, lang)
    path = OUTPUT / cv_filename(lang)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=32, rightMargin=32,
                           topMargin=25, bottomMargin=31, invariant=1,
                           title=localized(DATA['profile']['name'], 'en')+' - CV', author=localized(DATA['profile']['name'], 'en'))
    names = list(dict.fromkeys(localized(DATA['profile']['name'], code) for code in [lang, 'en']))
    story = [p(' · '.join(names), 'name'), Spacer(1, 3),
             p(' · '.join(localized(DATA['roles'][role], lang) for role in DATA['profile']['roles']), 'role')]

    story += section(tr('section.education'))
    rows = [[p(tr(key), 'label') for key in ['label.year', 'label.field_degree', 'label.institution']]]
    for e in sorted(DATA['education'], key=lambda item:item['year'], reverse=True):
        field = [p(localized(e['field'], lang), 'field'), Spacer(1, 2), p(localized(e['degree'], lang), 'small')]
        rows.append([p(e['year'], 'small'), field, p(localized(e['school'], lang))])
    story.append(table(rows, [43, 172, WIDTH-215], pad=3.5))

    story += section(tr('section.qualifications'))
    qual = [[item['year'], localized(item['title'], lang), localized(item['field'], lang)]
            for item in sorted(DATA['qualifications'], key=lambda item:item['year'], reverse=True)]
    story.append(table([[p(x) for x in row] for row in qual], [43, 195, WIDTH-238], header=False, pad=3))

    story += section(tr('section.interests'))
    chips = [[p(item['tag'], 'label'), Spacer(1, 3), p(localized(item['name'], lang))] for item in DATA['interests']]
    tag_table = Table([chips], colWidths=[WIDTH/len(chips)]*len(chips), hAlign='LEFT')
    tag_table.setStyle(TableStyle([('VALIGN', (0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),6),
                                   ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),6),
                                   ('BACKGROUND',(0,0),(-1,-1),TINT)]))
    story.append(tag_table)

    story += section(tr('section.publications'))
    for paper in sorted(DATA['papers'], key=lambda item:(item['year'], item['month'] or 0), reverse=True):
        venue = venue_details(paper, lang)
        title = '<link href="' + paper['url'] + '">' + escape(paper['title']) + '</link>'
        block = [p(title, 'paper', True), Spacer(1, 2),
                 p((tr('label.authors') + ': ') + ', '.join(authors(paper)), 'small'),
                 p((tr('label.venue') + ': ') + venue, 'small')]
        t = table([[p(str(paper['year']), 'small'), block]], [43, WIDTH-43], header=False, pad=5)
        story.append(KeepTogether([t]))

    story += section(tr('section.teaching'))
    rows = [[p(tr(key), 'label') for key in ['label.period', 'label.org', 'label.course', 'label.role']]]
    for item in teaching_records():
        value = teaching_values(item, lang)
        rows.append([p(value['period'].replace('–', ' - '), 'small'), p(value['organization'], 'small'),
                     p(value['course']), p(value['role'], 'small')])
    story.append(table(rows, [99, 105, WIDTH-294, 90], pad=4))

    def footer(c, doc):
        c.setFont('CV', 7.5); c.setFillColor(MUTED)
        c.drawString(32, 16, DATA['updated'].replace('-', '.'))
        c.drawRightString(A4[0]-32, 16, str(doc.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    changed = write_if_changed(path, buffer.getvalue())
    print(('Built ' if changed else 'Unchanged ') + str(path))

if __name__ == '__main__':
    import sys
    for lang in sys.argv[1:] or LANGUAGES:
        build(lang)
