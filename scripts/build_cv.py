from pathlib import Path
import os
from io import BytesIO
from content import ROOT, DATA, LANGUAGES, display_authors, venue_details, localized, text, teaching_records, teaching_history_records, teaching_values, teaching_columns, teaching_display_columns, current_role_context, teaching_relationships, school_program_groups, school_teaching_summaries, school_names, current_role_records, experience_records, EXPERIENCE_GROUPS, period, cv_filename, validate, write_if_changed
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable, PageBreak, Flowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from design import PALETTE, TYPE, COLUMNS, RADIUS

FONT = Path(os.environ.get('CV_FONT_DIR', str(ROOT / 'assets/fonts')))
OUTPUT = Path(os.environ.get('CV_OUTPUT_DIR', str(ROOT / 'assets')))
def configure_fonts():
    for name, filename in [('CV', TYPE.get('pdfRegularFile', 'NanumGothic-Regular.ttf')), ('CVB', TYPE.get('pdfBoldFile', 'NanumGothic-Bold.ttf')), ('CVHeading', TYPE.get('pdfHeadingFile', 'NanumMyeongjo-Bold.ttf'))]:
        path = FONT / filename
        if not path.is_file():
            raise FileNotFoundError(f'Missing {path}. Set CV_FONT_DIR to the licensed Nanum font directory.')
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily('CV', normal='CV', bold='CVB')
INK, MUTED, LINE, TINT, NAVY, PAPER, CAMEL = [HexColor(PALETTE[key]) for key in ['ink','secondary','line','tint','accent','paper','camel']]
# ReportLab's default frame adds 6 pt at each side inside the document margins.
WIDTH = A4[0] - 76
STYLES = {
    'name': ParagraphStyle('name', fontName='CVHeading', fontSize=22, leading=27, textColor=NAVY),
    'role': ParagraphStyle('role', fontName='CV', fontSize=11, leading=15, textColor=MUTED),
    'section': ParagraphStyle('section', fontName='CVHeading', fontSize=12, leading=16, textColor=NAVY, keepWithNext=True),
    'group': ParagraphStyle('group', fontName='CVB', fontSize=10, leading=14, textColor=NAVY, keepWithNext=True),
    'body': ParagraphStyle('body', fontName='CV', fontSize=TYPE['pdfBody'], leading=TYPE['pdfLeading'], textColor=INK),
    'field': ParagraphStyle('field', fontName='CVB', fontSize=TYPE['pdfBody'], leading=TYPE['pdfLeading'], textColor=INK),
    'small': ParagraphStyle('small', fontName='CV', fontSize=TYPE['pdfSecondary'], leading=TYPE['pdfSecondaryLeading'], textColor=MUTED),
    'context': ParagraphStyle('context', fontName='CV', fontSize=TYPE['pdfSecondary'], leading=TYPE['pdfSecondaryLeading'], textColor=INK),
    'label': ParagraphStyle('label', fontName='CVB', fontSize=9, leading=12, textColor=MUTED),
    'paper': ParagraphStyle('paper', fontName='CVB', fontSize=10.5, leading=14, textColor=NAVY),
}

def p(text, style='body', markup=False):
    text = str(text).replace('–', '-').replace('—', '-').replace(' ,', ',')
    value = text if markup else escape(text)
    value = value.replace('(STEP 2)', '<nobr>(STEP&#160;2)</nobr>')
    value = value.replace('Codex work assistant course', '<nobr>Codex&#160;work&#160;assistant&#160;course</nobr>')
    value = value.replace('Codex work assistant', '<nobr>Codex&#160;work&#160;assistant</nobr>')
    value = value.replace('Cheongwon Girls’ High School', '<nobr>Cheongwon&#160;Girls’&#160;High&#160;School</nobr>')
    value = value.replace('Science and Technology', '<nobr>Science&#160;and&#160;Technology</nobr>')
    value = value.replace('High School', '<nobr>High&#160;School</nobr>')
    value = value.replace('API 연동.', '<nobr>API&#160;연동.</nobr>')
    return Paragraph(value, STYLES[style])

def table(data, widths, header=True, pad=4, surface=None, rounded=False):
    t = Table(data, colWidths=widths, hAlign='LEFT', repeatRows=1 if header else 0, splitByRow=1, splitInRow=0,
              cornerRadii=[RADIUS['pdfPanel']]*4 if rounded else None)
    commands = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), pad),
                ('BOTTOMPADDING', (0, 0), (-1, -1), pad),
                ('LINEBELOW', (0, 0), (-1, -1), .35, LINE)]
    if surface:
        commands += [('BACKGROUND', (0, 0), (-1, -1), HexColor(PALETTE[surface]))]
    if header:
        commands += [('BACKGROUND', (0, 0), (-1, 0), TINT)]
    t.setStyle(TableStyle(commands))
    return t

def section(title):
    gap = Spacer(1, 5)
    gap.keepWithNext = True
    return [Spacer(1, 8), p(title, 'section'), gap]

class PillTags(Flowable):
    """Measured sans-serif labels with rounded outlines and bounded wrapping."""
    font_name = 'CV'
    font_size = 9
    pad_x, pad_y, gap = 6, 2, 4

    def __init__(self, labels, background='tint'):
        super().__init__()
        self.labels = list(labels)
        self.background = HexColor(PALETTE[background])
        self.placements = []

    def wrap(self, availWidth, availHeight):
        width = max(1, availWidth)
        style = ParagraphStyle('pill', fontName=self.font_name, fontSize=self.font_size,
                               leading=10.5, textColor=NAVY)
        rows, row, x, row_height = [], [], 0, 0
        for label in self.labels:
            natural = pdfmetrics.stringWidth(label, self.font_name, self.font_size) + self.pad_x*2
            tag_width = min(natural, width)
            paragraph = Paragraph(escape(label), style)
            _, inner_height = paragraph.wrap(max(1, tag_width-self.pad_x*2), availHeight)
            tag_height = inner_height + self.pad_y*2
            if row and x+tag_width > width+0.001:
                rows.append((row, row_height)); row, x, row_height = [], 0, 0
            row.append((x, tag_width, tag_height, paragraph))
            x += tag_width+self.gap
            row_height = max(row_height, tag_height)
        if row:
            rows.append((row, row_height))
        self.height = sum(height for _,height in rows) + max(0,len(rows)-1)*self.gap
        self.width = width
        self.placements = []
        y = self.height
        for row, row_height in rows:
            y -= row_height
            self.placements.extend((x,y+row_height-height,w,height,paragraph) for x,w,height,paragraph in row)
            y -= self.gap
        return self.width, self.height

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setLineWidth(.45)
        for x,y,width,height,paragraph in self.placements:
            canvas.setStrokeColor(HexColor(PALETTE['tag-border']))
            canvas.setFillColor(self.background)
            canvas.roundRect(x,y,width,height,min(height/2,8),stroke=1,fill=1)
            paragraph.drawOn(canvas,x+self.pad_x,y+self.pad_y)
        canvas.restoreState()


def panel_heading(title, topics=()):
    if topics:
        title_width = pdfmetrics.stringWidth(title,'CVHeading',12)+14
        heading = Table([[p(title,'section'),PillTags(topics,'beige')]],
                        colWidths=[title_width,WIDTH-title_width],hAlign='LEFT')
        heading.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                     ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
                                     ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    else:
        heading = p(title,'section')
    result = [heading, Spacer(1,5), HRFlowable(width='100%',thickness=.6,color=CAMEL),Spacer(1,4)]
    for item in result:
        item.keepWithNext = True
    return result

def compact_rows(rows, widths, pad=6, surface='table-body'):
    return table(rows, widths, header=False, pad=pad, surface=surface, rounded=True)

def column_pair(left, right, left_width, gap=18):
    result = Table([[left, '', right]], colWidths=[left_width, gap, WIDTH-left_width-gap], hAlign='LEFT')
    result.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0)]))
    return result

def current_activities(lang, width):
    records = current_role_records()
    if not records:
        return []
    rows = []
    for item in records:
        organization = localized(DATA['organizations'][item['organization']], lang)
        heading = '<b>'+escape(localized(item['title'], lang))+'</b> <font size="9" color="'+PALETTE['secondary']+'"><nobr>·&#160;'+escape(organization).replace(' ', '&#160;')+'</nobr></font>'
        role = [p(heading, 'body', True)]
        context = current_role_context(item,lang)
        if context:
            role.append(p(context, 'context'))
        if item.get('summary'):
            role.append(p(localized(item['summary'], lang), 'small'))
        dates = period(item, lang, include_planned_notice=False)
        rows.append([p(dates, 'small'), role])
    return panel_heading(text('section.current_roles', lang)) + [table(rows, [92, width-92], header=False, pad=5, surface='table-body', rounded=True)]

def education_and_qualifications(lang, width, compact=False):
    result = panel_heading(text('section.education_qualifications', lang))
    rows = []
    for item in sorted(DATA['education'], key=lambda row:row['year'], reverse=True):
        degree = item['degreeShort'] if compact else item['degree']
        title = escape(localized(item['field'], lang)) + ' · ' + escape(localized(degree, lang))
        body = [p(title, 'field', True),
                p(localized(item['school'], lang), 'small')]
        rows.append([p(item['year'], 'small'), body])
    for item in sorted(DATA['qualifications'], key=lambda row:row['year'], reverse=True):
        title = localized(item['title'], lang) + ' · ' + localized(item['field'], lang)
        rows.append([p(item['year'], 'small'), p(title, 'small')])
    return result + [compact_rows(rows, [34, width-34], pad=4.5, surface='table-meta')]

def publications(lang, width):
    result = panel_heading(text('section.publications', lang), [localized(tag, lang) for tag in DATA['researchTopics']])
    rows = []
    for paper in sorted(DATA['papers'], key=lambda item:(item['year'], item['month'] or 0), reverse=True):
        title = '<link href="' + paper['url'] + '">' + escape(paper['title']) + '</link>'
        block = [p(title, 'paper', True), Spacer(1, 2),
                 PillTags([localized(tag,lang) for tag in paper.get('topics',[])]), Spacer(1,2),
                 p(text('label.authors', lang) + ': ' + ', '.join(display_authors(paper, lang)), 'small'),
                 p(text('label.venue', lang) + ': ' + venue_details(paper, lang), 'small')]
        rows.append([p(paper['year'], 'small'), block])
    return result + [compact_rows(rows, [36, width-36], pad=6, surface='table-body')]

def date_cell(item, lang):
    dates = period(item, lang).split(' (', 1)
    result = [p(dates[0].replace('–', ' - '), 'small')]
    if len(dates) > 1:
        note = dates[1].removesuffix(')')
        if lang == 'en':
            import calendar
            for month in range(1, 13):
                note = note.replace(calendar.month_name[month], calendar.month_abbr[month])
        result.append(p(note, 'small'))
    return result

def teaching_pdf_rows(item, lang):
    value = teaching_display_columns(item, lang)
    provider = ([p(value['provider'],'field')] if value['provider'] else []) + [p(line,'small') for line in value['organizationLines']]
    heading = '<b>'+escape(value['subject'])+'</b>'
    if item.get('showRole', True):
        heading += ' <font size="9" color="'+PALETTE['secondary']+'">· '+escape(value['role'])+'</font>'
    programs = school_program_groups(item,lang)
    body = ([p(value['audience'],'field')] if value['audience'] else []) + ([] if programs else [p(heading, 'body', True)])
    if item.get('summary'):
        body.append(p(localized(item['summary'], lang), 'small'))
    programs = school_program_groups(item,lang)
    if programs:
        for group in programs:
            body.append(p('<b>'+escape(' · '.join(group['schools']))+'</b> <font size="9" color="'+PALETTE['secondary']+'">· '+escape(group['role'])+'</font>', 'body', True))
            body.append(p(' · '.join(group['titles']) or ('Python 프로그래밍' if lang=='ko' else 'Python programming'),'body'))
    elif item.get('schoolSummary'):
        body.append(p(localized(item['schoolSummary'],lang),'small'))
    return [[date_cell(item,lang),provider,body]]

def experience_block(group, heading, lang):
    other = experience_records(group)
    if not other:
        return []
    rows = []
    for item in other:
        title = escape(localized(item['title'], lang))
        if item.get('url'):
            title = '<link href="'+escape(item['url'])+'">'+title+'</link>'
        role = '<font size="9" color="'+PALETTE['secondary']+'"> · '+escape(localized(item['role'], lang))+'</font>'
        body = [p(title+role, 'field', True)]
        if item.get('description'):
            body.append(p(localized(item['description'], lang), 'small'))
        if item.get('note'):
            body.append(p(localized(item['note'], lang), 'small'))
        rows.append([p(period(item, lang), 'small'), body])
    return [KeepTogether(section(text(heading, lang)) +
                         [table(rows, [99, WIDTH-99], header=False, pad=5,
                                surface='table-meta' if group == 'development' else 'table-body', rounded=True)])]

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
    name_markup = ' · '.join('<font name="CVHeading" size="21">'+escape(name)+'</font>' if any(ord(c)>127 for c in name) else escape(name) for name in names)
    story = [p(name_markup, 'name', True), Spacer(1, 3),
             p(' · '.join(localized(DATA['roles'][role], lang) for role in DATA['profile']['roles']), 'role')]
    portfolio = DATA['profile']['portfolioUrl']
    contact = '<link href="mailto:'+escape(DATA['profile']['email'])+'">'+escape(DATA['profile']['email'])+'</link> &nbsp; · &nbsp; '
    contact += '<link href="'+escape(portfolio)+'">'+escape(portfolio.removeprefix('https://').rstrip('/'))+'</link>'
    story += [Spacer(1, 4), p(contact, 'small', True), Spacer(1, 7),
              HRFlowable(width='100%', thickness=.8, color=CAMEL)]

    activity_width = (WIDTH-18)*.68
    story += [Spacer(1, 10), column_pair(current_activities(lang, activity_width),
               education_and_qualifications(lang, WIDTH-activity_width-18, compact=True), activity_width)]
    # The default CV supports teaching applications: current work and recent
    # teaching first, historical instruction next, then research and employment.
    records = teaching_history_records()
    chunks = [(records[:4],False),(records[4:],True)]
    first_teaching = True
    for records,new_page in chunks:
        if not records:
            continue
        if new_page:
            story.append(PageBreak())
        else:
            story.append(Spacer(1, 14))
        if first_teaching:
            story += panel_heading(tr('section.teaching_history'))
        header_index = 0
        rows = [[p(tr(key), 'label') for key in ['label.period', 'label.org_program', 'label.role_course']]]
        for item in records:
            rows.extend(teaching_pdf_rows(item, lang))
        career_table = table(rows, [WIDTH*value/100 for value in COLUMNS], header=False, pad=5, rounded=True)
        career_table.repeatRows = (header_index,)
        commands = [
            ('NOSPLIT', (0, 0), (-1, header_index+1)),
            ('BACKGROUND', (0, header_index), (-1, header_index), TINT),
            ('LINEABOVE', (0, header_index), (-1, header_index), .65, CAMEL),
            ('BACKGROUND', (0, header_index+1), (1, -1), HexColor(PALETTE['table-meta'])),
            ('BACKGROUND', (2, header_index+1), (2, -1), HexColor(PALETTE['table-body'])),
        ]
        career_table.setStyle(TableStyle(commands))
        story.append(career_table)
        first_teaching = False

    story += [PageBreak(), KeepTogether(publications(lang, WIDTH))]
    for group, heading in EXPERIENCE_GROUPS:
        story += experience_block(group, heading, lang)

    def footer(c, doc):
        c.saveState()
        c.setFillColor(PAPER)
        c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        c.restoreState()
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

