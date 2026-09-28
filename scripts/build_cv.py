from pathlib import Path
import os
from content import ROOT, DATA, authors, venue_details
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

D = DATA['cv']
FONT = Path(os.environ.get('CV_FONT_DIR', str(ROOT / 'fonts')))
OUTPUT = Path(os.environ.get('CV_OUTPUT_DIR', str(ROOT / 'assets')))
OUTPUT.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('CV', str(FONT / 'NanumGothic-Regular.ttf')))
pdfmetrics.registerFont(TTFont('CVB', str(FONT / 'NanumGothic-Bold.ttf')))
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
TAGS = ['#DiscreteLearning', '#NeuroSymbolic', '#AdaptiveNetworks']

def p(text, style='body', markup=False):
    text = text.replace('–', '-').replace('—', '-').replace(' ,', ',')
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
    ko = lang == 'ko'
    path = OUTPUT / f'Choi-Soon-Ho-CV-{lang.upper()}.pdf'
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=32, rightMargin=32,
                           topMargin=25, bottomMargin=31, title='Choi Soon Ho - CV', author='Choi Soon Ho')
    story = [p('최순호 · Choi Soon Ho' if ko else 'Choi Soon Ho', 'name'),
             Spacer(1, 3), p(' · '.join(DATA['profile']['roles'][lang]), 'role')]

    story += section('학력' if ko else 'Education')
    rows = [[p(x, 'label') for x in (['연도', '전공 · 학위', '기관'] if ko else ['Year', 'Field · Degree', 'Institution'])]]
    for e in D['education'][lang]:
        field = [p(e['field'], 'field'), Spacer(1, 2), p(e['degree'], 'small')]
        rows.append([p(e['year'], 'small'), field, p(e['school'])])
    story.append(table(rows, [43, 172, WIDTH-215], pad=3.5))

    story += section('자격' if ko else 'Qualification')
    qual = [['2026', 'NCS 확인강사', '인공지능'] if ko else ['2026', 'NCS-registered instructor', 'Artificial intelligence']]
    story.append(table([[p(x) for x in row] for row in qual], [43, 195, WIDTH-238], header=False, pad=3))

    story += section('연구 관심사' if ko else 'Research Interests')
    chips = [[p(tag, 'label'), Spacer(1, 3), p(topic)] for tag, topic in zip(TAGS, D['interests'][lang])]
    tag_table = Table([chips], colWidths=[WIDTH/3]*3, hAlign='LEFT')
    tag_table.setStyle(TableStyle([('VALIGN', (0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),6),
                                   ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),6),
                                   ('BACKGROUND',(0,0),(-1,-1),TINT)]))
    story.append(tag_table)

    story += section('논문' if ko else 'Publications')
    for paper in DATA['papers']:
        venue = venue_details(paper, lang)
        title = '<link href="' + paper['url'] + '">' + escape(paper['title']) + '</link>'
        block = [p(title, 'paper', True), Spacer(1, 2),
                 p(('저자: ' if ko else 'Authors: ') + ', '.join(authors(paper)), 'small'),
                 p(('학회: ' if ko else 'Conference: ') + venue, 'small')]
        t = table([[p(str(paper['year']), 'small'), block]], [43, WIDTH-43], header=False, pad=5)
        story.append(KeepTogether([t]))

    story += section('강의 · 학습지원 이력' if ko else 'Teaching & Learning Support')
    headings = ['기간', '기관', '과정', '역할'] if ko else ['Period', 'Organization', 'Course', 'Role']
    rows = [[p(x, 'label') for x in headings]]
    for j in D['jobs'][lang]:
        org_role = j['org_role'].split(' · ')
        org, role = ' · '.join(org_role[:-1]), org_role[-1]
        course = j['course']
        date = j['date'].replace('-', ' - ')
        rows.append([p(date, 'small'), p(org, 'small'), p(course), p(role, 'small')])
    story.append(table(rows, [99, 105, WIDTH-294, 90], pad=4))

    def footer(c, doc):
        c.setFont('CV', 7.5); c.setFillColor(MUTED)
        c.drawString(32, 16, DATA['updated'].replace('-', '.'))
        c.drawRightString(A4[0]-32, 16, str(doc.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(path)

if __name__ == '__main__':
    import sys
    for lang in sys.argv[1:] or ['ko', 'en']:
        build(lang)
