"""Reproduce the approved four-page Korean editorial CV selection.

The public website retains the complete portfolio; this CV is a curated snapshot.
"""
from pathlib import Path
import sys,json,copy,re,os
from io import BytesIO
sys.dont_write_bytecode=True
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('CV_OUTPUT_DIR', str(ROOT/'assets')))
FONT=Path(os.environ.get('CV_FONT_DIR', str(ROOT/'assets/fonts')))
OUT.mkdir(parents=True, exist_ok=True)
for n,f in [('Sans','NanumGothic-Regular.ttf'),('SansBold','NanumGothic-Bold.ttf'),('Serif','NanumMyeongjo-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(FONT/f)))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold')
W,H=A4;NAVY='#203C4B';INK='#303B40';MUTED='#5D6B70';CAMEL='#B68D64';LINE='#DBE3DF';GREEN='#52786C'
BASE=json.loads((ROOT/'data/cv-ko-editorial.json').read_text())
TOPICS='신경망 양자화 · 신경망 구조 학습'
CURRENT=[('2026.08-2026.10','고양 스마트시티즌 강사 · 에듀코어센터',['AI 웹 제작 과정 1차(2026.08-09): 웹페이지 제작·배포.','AI 웹 제작 과정 2차(2026.09): 웹 제작·LLM 에이전트.','Codex 업무 비서 과정(2026.10): 실습 교안 구성·교육.']),('2026.06-2026.10','PBL 퍼실리테이터 · 모두의연구소',['코디세이 · AI Native 과정 · 이노베이션아카데미','학습 이슈 조율·과제 수행 지원·교양 세미나 개설·운영.']),('2023.03-현재','온라인 코딩강사(프리랜서) · 코더랜드',['Python·C++ · 자료구조·알고리즘','개별 학습 및 2024-2026 정보올림피아드 대비 지도.'])]
DEGREES=[('2025','인공지능 · 공학석사','국민대학교\n소프트웨어융합대학원'),('2019','컴퓨터공학·전자공학\n공학사','한동대학교 전산전자공학부'),('2026','NCS 확인강사 · 인공지능','')]
SELECTED=[('2026.10 / 하나생명 임직원','AI로 설계하는 데이터 서비스 실무(STEP 2)','K-하이테크플랫폼 · 엘리스그룹 · 강사','업무 문제 정의·PRD 기반 AI PoC 실습 및 프로젝트 피드백.'),('2026.07 / LG이노텍 임직원','AI·AX Lv2 집체교육','엘리스그룹 · 강사','AI·AX 강의·실습 및 현업 과제 계획 수립·발표에 대한 피드백.')]
PAPER='Learning to Wire: End-to-End Operand Selection for Symbolic Logic Networks'
def display_text(t):
 t=t.replace(' LLM·에이전트·업무 자동화 교안 준비.','')
 t=t.replace('Codex 업무 비서 과정(2026.10): 실습 교안 구성·교육.','Codex 업무 비서 과정(2026.10): 업무 비서 제작 교육.')
 t=t.replace('코딩테스트 문제해결·학습법, Python 자료구조·알고리즘 교안 작성.','코딩테스트 문제해결·학습법, Python 자료구조·알고리즘.')
 t=t.replace('고양 스마트시티즌 강사','고양 스마트시티즌')
 t=t.replace('온라인 코딩강사(프리랜서)','온라인 프로그래밍 교육(프리랜서)')
 return re.sub(r' · (?:주강사|강사)(?=\s*(?:\||$))','',t)
def display_block(t):
 out=dict(t);out['text']=display_text(out['text'])
 if out.get('bold_prefix'):out['bold_prefix']=display_text(out['bold_prefix'])
 return out
def display_meta(values):return [v for v in values if v not in ('강사','주강사')]
def b(t,k='body',url=None):return dict(text=t,kind=k,url=url)
class Layout:
 def __init__(self,v):
  self.v=v;self.page=0;self.y=0;self.section='';self.log=[];self.ids=[];self.buffer=BytesIO();self.c=canvas.Canvas(self.buffer,pagesize=A4,pageCompression=1,invariant=1)
  self.c.setAuthor('Choi Soon Ho');self.c.setTitle('최순호 · 교육·연구 이력서')
  self.x=142 if v=='A' else 162;self.w=553-self.x;self.mw=self.x-54
  self.fs=10 if v=='A' else 10.8;self.ld=13.2 if v=='A' else 15.2
  self.gap=1.2 if v=='A' else 1.7;self.igap=2.5 if v=='A' else 5
  self.rgap=5 if v=='A' else 7
  self.styles={'body':(self.fs,self.ld,'Sans',INK),'title':(10.7 if v=='A' else 11.4,14 if v=='A' else 16,'SansBold',NAVY),'school':(self.fs,self.ld,'SansBold',NAVY),'program':(self.fs,self.ld,'Sans',INK),'meta':(8.8 if v=='A' else 9.5,12 if v=='A' else 13.5,'Sans',MUTED),'date':(8.8 if v=='A' else 9.5,12 if v=='A' else 13.5,'SansBold',GREEN),'paper':(10.7,14 if v=='A' else 15.2,'SansBold',NAVY)}
  self.newpage(profile=True)
 def para(self,t,w,style):
  t=display_block(t)
  fs,ld,font,col=style;st=ParagraphStyle('p',fontName=font,fontSize=fs,leading=ld,textColor=HexColor(col),splitLongWords=False)
  val=escape(t['text']).replace('\n','<br/>')
  if t.get('bold_prefix'):val='<b>'+escape(t['bold_prefix'])+'</b>'+escape(t['text'][len(t['bold_prefix']):])
  if t.get('url'):val=f'<link href="{escape(t["url"])}">{val}</link>'
  p=Paragraph(val,st);_,h=p.wrap(w,2000);return p,h
 def draw(self,t,x,y,w,style=None):
  t=display_block(t)
  st=style or self.styles[t['kind']];p,h=self.para(t,w,st);assert y+h<783,(self.v,self.page,t['text'],y,h)
  p.drawOn(self.c,x,H-y-h);self.log.append(dict(page=self.page,text=t['text'],kind=t['kind'],x=x,y=y,w=w,h=h,fontsize=st[0]));return h
 def txt(self,t,x,y,w,fs=10,ld=None,font='Sans',color=INK):return self.draw(b(t),x,y,w,(fs,ld or fs*1.4,font,color))
 def rule(self,y,x1=42,x2=553,col=LINE,lw=.45):self.c.setStrokeColor(HexColor(col));self.c.setLineWidth(lw);self.c.line(x1,H-y,x2,H-y)
 def vertical(self,x,y1,y2):self.c.setStrokeColor(HexColor(LINE));self.c.setLineWidth(.5);self.c.line(x,H-y1,x,H-y2)
 def foot(self):
  self.rule(793);self.c.setFont('Sans',7.5);self.c.setFillColor(HexColor(MUTED));self.c.drawString(42,H-811,'2026.10.15');self.c.drawCentredString(W/2,H-811,'CURRICULUM VITAE');self.c.setFont('SansBold',8);self.c.drawRightString(553,H-811,f'{self.page:02d}')
 def newpage(self,profile=False):
  if self.page:self.foot();self.c.showPage()
  self.page+=1
  if not profile:
   self.txt('최순호',42,33,70,14,18,'Serif',NAVY);self.txt('Choi Soon Ho',115,39,160,8.5,11,color=MUTED);self.txt(self.section or '교육·연구 이력',438,39,115,8.5,11,color=MUTED);self.rule(64,col=CAMEL,lw=.7);self.y=78
 def heading(self,t,x,y,w,size=15):return self.txt(t,x,y,w,size,size*1.3,'Serif',NAVY)
 def header(self,compact):
  self.txt('CURRICULUM VITAE',42,27 if compact else 38,240,8.2,11,'SansBold',CAMEL)
  self.txt('최순호',40,46 if compact else 66,280,32 if compact else 36,40 if compact else 44,'Serif',NAVY)
  self.txt('Choi Soon Ho',43,91 if compact else 113,230,11 if compact else 12,15,color=MUTED)
  self.txt('강사 · 연구자',440,34 if compact else 49,113,10,14,'SansBold',NAVY)
  self.txt('sosaror@gmail.com\nsnow0821.github.io',378,55 if compact else 74,175,9.1,13,color=MUTED)
  self.c.linkURL('mailto:sosaror@gmail.com',(378,H-(81 if compact else 100),553,H-(55 if compact else 74)),relative=0,thickness=0)
  self.c.linkURL('https://snow0821.github.io/',(378,H-(94 if compact else 113),553,H-(68 if compact else 87)),relative=0,thickness=0)
  self.txt('프로그래밍과 AI 활용을 가르치며,\n신경망의 구조와 연산을 연구합니다.',350,89 if compact else 119,203,9.5 if compact else 10,13.3 if compact else 14)
  self.rule(127 if compact else 163,col=CAMEL,lw=.9)
 def current(self,y,w=315,fs=10):
  self.heading('현재 활동',42,y,w,14);y+=30
  for i,(d,t,ds) in enumerate(CURRENT):
   y+=self.txt(d,42,y,w,8.8 if self.v=='A' else 9,12,'SansBold',GREEN)+3
   y+=self.txt(t,42,y,w,10.5 if self.v=='A' else 10.8,15,'SansBold',NAVY)+4
   for st in ds:y+=self.txt(st,42,y,w,fs,14)+2
   y+=8
   if i<2:self.rule(y-4,42,42+w);y+=4
  return y
 def degrees(self,y,x=403,w=150,fs=10):
  self.heading('학위·자격',x,y,w,14);y+=30
  for year,t,school in DEGREES:
   y+=self.txt(year,x,y,w,8.8,12,'SansBold',CAMEL)+3
   y+=self.txt(t,x,y,w,fs,14,'SansBold',NAVY)+3
   if school:y+=self.txt(school,x,y,w,fs,14,color=MUTED)+12
  return y
 def profile(self):
  compact=self.v=='A';self.header(compact)
  top=145 if compact else 187
  end=self.current(top,315,10 if compact else 10.2);dy=self.degrees(top,fs=10 if compact else 10.2)
  self.vertical(381,top+4,end-8)
  if compact:
   self.y=max(end,dy)+3
   self.section='교육 경력'
   return
  row=max(end,dy)+14;self.rule(row,col=CAMEL,lw=.7);row+=21
  self.heading('주요 강의 경험',42,row,230,14);self.heading('연구활동',312,row,78,14);self.txt('대표 논문',393,row+5,160,8.5,12,'SansBold',CAMEL)
  ty=row+33
  for i,(d,t,org,desc) in enumerate(SELECTED):
   ty+=self.txt(d,42,ty,230,8.8,12,'SansBold',GREEN)+5
   ty+=self.txt(t,42,ty,230,10.8,15,'SansBold',NAVY)+4
   ty+=self.txt(org,42,ty,230,9.2,13,color=MUTED)+4
   ty+=self.txt(desc,42,ty,230,10.2,14.5)+12
   if i==0:self.rule(ty-4,42,272);ty+=5
  ry=row+33;ry+=self.txt(PAPER,312,ry,241,11,16,'SansBold',NAVY)+9
  ry+=self.txt('2026 IJCNN · Soon Ho Choi(제1저자), Soo Yong Kim',312,ry,241,9.3,13,color=MUTED)+12
  ry+=self.txt('연구 분야',312,ry,241,9.3,13,'SansBold',GREEN)+5;ry+=self.txt(TOPICS,312,ry,241,10.2,14.5)
  self.vertical(286,row+3,max(ty,ry)-8)
  self.section='교육 경력';self.newpage()
 def height(self,bs,w=None):return sum(self.para(t,w or self.w,self.styles[t['kind']])[1]+self.gap for t in bs)
 def titleblock(self,r):return b(r['title'],'paper' if r['id'].startswith('paper-') else 'title',r.get('url'))
 def minh(self,r):return self.height([self.titleblock(r)])+4+sum(self.height(i['blocks'])+self.igap for i in (r['items'] if r['id']=='exp-mincoding' else r['items'][:1]))
 def ensure(self,h,repeat=None):
  if self.y+h>774:
   self.newpage()
   if repeat:
    ly=self.y
    for t in [b(repeat['date'],'date')]+[b(v,'meta') for v in display_meta(repeat['meta'])]:ly+=self.draw(t,42,ly,self.mw)+self.gap
    self.y+=self.draw(b(repeat['title']+' · 계속','meta'),self.x,self.y,self.w)+5
 def sectionhead(self,s):
  self.section=s['title']
  self.igap=7 if s['title']=='교육 경력' else 5
  if self.v=='B' and s['title']=='연구활동' and self.y>100:self.newpage()
  self.ensure(38+(self.height([b(s['intro'],'meta')],511)+4 if s['intro'] else 0)+self.minh(s['records'][0]));self.y+=4 if self.y>100 else 0
  self.y+=self.heading(s['title'],42,self.y,511,15)+5
  if s['intro']:self.y+=self.draw(b(s['intro'],'meta'),42,self.y,511)+4
  self.rule(self.y,col=CAMEL,lw=.65);self.y+=10
 def record(self,r):
  if self.v=='B' and r['id']=='saessak-elice-2023' and self.page==2:self.newpage()
  self.ensure(self.minh(r));start=self.page;ly=self.y
  for t in [b(r['date'],'date')]+[b(v,'meta') for v in display_meta(r['meta'])]:ly+=self.draw(t,42,ly,self.mw)+self.gap
  self.y+=self.draw(self.titleblock(r),self.x,self.y,self.w)+4
  for it in r['items']:
   self.ensure(self.height(it['blocks'])+self.igap,r)
   for t in it['blocks']:self.y+=self.draw(t,self.x,self.y,self.w)+self.gap
   self.y+=self.igap;self.ids.extend(it['source_ids'])
  if self.page==start:self.y=max(self.y,ly)
  self.rule(self.y+1);self.y+=self.rgap
  if self.v=='B' and self.page==2:self.y+=23
 def finish(self):
  self.foot();self.c.showPage();self.c.save()
  target=OUT/'Choi-Soon-Ho-CV-KO.pdf';data=self.buffer.getvalue()
  if not target.exists() or target.read_bytes()!=data:target.write_bytes(data)
  print('Built approved editorial Korean CV:', self.page, 'pages')
def build():
 model=copy.deepcopy(BASE)
 l=Layout('B');l.profile()
 for sec in model:
  l.sectionhead(sec)
  for r in sec['records']:l.record(r)
 l.finish()
 return l

if __name__ == '__main__':
 build()
