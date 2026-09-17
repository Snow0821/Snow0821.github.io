"""Generate the three review documents from the shared career source."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'content/profile.json').read_text())
OUT = ROOT / 'public/downloads'
OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'scripts/assets/SnowPortfolio-Regular.ttf'
pdfmetrics.registerFont(TTFont('Snow', str(FONT)))
INK = colors.HexColor('#253b34')
MUTED = colors.HexColor('#617068')
LINE = colors.HexColor('#d5dcd1')
CLAY = colors.HexColor('#a85a42')
W, H = A4

def safe(value):
    return escape(str(value).replace('—', '-').replace('–', '-').replace('‑', '-'))

class Document:
    def __init__(self, filename, title, lang):
        self.c = canvas.Canvas(str(OUT / filename), pagesize=A4)
        self.c.setTitle(title + ' - Soon Ho Choi - Draft')
        self.c.setAuthor('Soon Ho Choi')
        self.lang = lang
        self.y = H - 48
        self.c.setFillColor(CLAY)
        self.c.setFont('Snow', 8)
        self.c.drawString(52, self.y, 'DRAFT / FOR REVIEW - SEPTEMBER 2026')
        self.y -= 37
        self.c.setFillColor(INK)
        self.c.setFont('Times-Roman' if lang == 'en' else 'Snow', 30 if lang == 'en' else 27)
        self.c.drawString(52, self.y, 'Soon Ho Choi' if lang == 'en' else '최순호')
        self.y -= 23
        self.para(title, size=11, color=INK, gap=8)
        self.para('sosaror@gmail.com  |  GitHub: Snow0821  |  LinkedIn: snowian', size=8.4, gap=4)
        self.para('<link href="https://github.com/Snow0821" color="#253b34">github.com/Snow0821</link>  |  <link href="https://www.linkedin.com/in/snowian" color="#253b34">linkedin.com/in/snowian</link>', size=8.2, markup=True, gap=8)
    def para(self, text, size=9.3, color=MUTED, gap=8, markup=False):
        style = ParagraphStyle('body',fontName='Snow',fontSize=size,leading=size*1.6,textColor=color,wordWrap='CJK' if self.lang=='ko' else None)
        p = Paragraph(text if markup else safe(text),style)
        _, h = p.wrap(W - 104, H)
        if self.y - h < 66:
            raise ValueError('Page overflow: '+text[:80])
        p.drawOn(self.c,52,self.y-h)
        self.y -= h + gap
    def section(self, title):
        self.y -= 6
        self.c.setStrokeColor(LINE)
        self.c.line(52,self.y,W-52,self.y)
        self.y -= 8
        self.para(title,size=10.2,color=INK,gap=7)
    def item(self, title, body=None):
        self.para(title,size=10,color=INK,gap=2)
        if body:self.para(body,size=9,gap=9)
    def finish(self):
        self.c.setStrokeColor(LINE)
        self.c.line(52,53,W-52,53)
        self.c.setFont('Snow',7.2)
        self.c.setFillColor(MUTED)
        note = 'Review copy. Verify career details before submission.' if self.lang=='en' else '검토용 초안입니다. 외부 제출 전 경력과 세부 정보를 확인해 주세요.'
        self.c.drawString(52,38,note)
        self.c.drawRightString(W-52,38,'1 / 1')
        self.c.save()

cv = Document(DATA['documents'][0]['filename'],'Research Curriculum Vitae','en')
cv.section('RESEARCH INTERESTS')
cv.para('Discrete and integer neural networks; logic-gate networks; binary and ternary quantization; efficient neural representations.')
cv.section('EDUCATION')
for edu in DATA['education']:
    cv.item(edu['institution']['en'] + ' | ' + edu['period'], edu['degree']['en'])
cv.section('SELECTED RESEARCH')
for research in DATA['research']:
    cv.item(research['short'] + ' | ' + research['year'], research['summary']['en'])
    cv.para('<link href="'+research['github']+'" color="#253b34">Public research repository</link>',size=8,markup=True,gap=6)
cv.section('CONFERENCE CONTRIBUTION')
cv.para('Choi Soon Ho and Soo-Yeon Yoon. Comparing accuracy of sign-quantized layers with linear layer in small models. Proceedings of the KICS Symposium, June 19, 2024.',size=9)
cv.section('TEACHING & PRACTICE')
cv.para('Freelance developer and AI instructor (2023 - present). Teaching areas: Python, C++, data structures, algorithms, practical AI, and web development.',size=9)
cv.finish()

resume = Document(DATA['documents'][1]['filename'],'AI 연구자 · 강사 | 국문 이력서','ko')
resume.section('소개')
resume.para(DATA['profile']['bio']['ko'])
resume.section('경력')
resume.item('프리랜서 개발자 · AI 강사 | 2023 - 현재','Python·C++ 프로그래밍, 자료구조·알고리즘, AI 활용과 웹 제작을 강의합니다.')
resume.section('학력')
for edu in DATA['education']:
    resume.item(edu['institution']['ko'] + ' | ' + edu['period'],edu['degree']['ko'])
resume.section('주요 연구')
for research in DATA['research']:
    resume.item(research['title']['ko']+' | '+research['year'],research['summary']['ko'])
resume.section('학술 활동')
resume.para('부호 양자화 층과 선형 층의 정확도 비교 연구. 한국통신학회 학술대회, 2024년 6월 19일. 저자: Choi Soon Ho, Soo-Yeon Yoon.')
resume.finish()

instructor=Document(DATA['documents'][2]['filename'],'AI · 프로그래밍 강사 소개서','ko')
instructor.section('강사 소개')
instructor.para('AI 연구자이자 프리랜서 개발자·강사입니다. 첫 코드 한 줄부터 작동하는 프로젝트까지, 컴퓨터과학의 기초와 실용적인 AI 활용을 연결합니다.')
instructor.section('강의 분야')
for course in DATA['teaching']:
    instructor.item(course['title']['ko'],course['description']['ko'])
instructor.section('수업 방식')
instructor.item('작은 목표를 완성하는 실습','학습자가 직접 만든 결과물을 확인하면서 다음 단계로 이어갑니다.')
instructor.item('개념과 구현의 연결','작동 원리를 이해하고, 예제를 수정하며, 자신에게 필요한 프로젝트에 적용합니다.')
instructor.item('대상과 목적에 맞는 구성','프로그래밍 입문, 알고리즘 학습, 실생활 AI 활용 등 수강생의 목표에 맞춰 수업 범위를 협의합니다.')
instructor.section('경력 · 학력')
instructor.para('프리랜서 개발자 · AI 강사 (2023 - 현재)\n국민대학교 인공지능 전공 공학석사 (2025)\n한동대학교 컴퓨터공학 공학사 (2019)'.replace('\n','<br/>'),markup=True)
instructor.section('출강 문의')
instructor.para('이메일: sosaror@gmail.com\n교육 대상, 주제, 희망 일정과 시간을 함께 알려주시면 과정 구성을 논의할 수 있습니다.'.replace('\n','<br/>'),markup=True)
instructor.finish()
print('Created 3 one-page PDF review documents.')
