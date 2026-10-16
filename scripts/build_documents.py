"""Build responsive, accessible reading editions from reviewed public text."""
import json
from html import escape
from content import DATA, ROOT, write_if_changed
def build():
    papers=DATA['papers']
    for slug,title,pdf in [('cv','CV','Choi-Soon-Ho-CV-KO.pdf'),('career-statement','경력기술서','Choi-Soon-Ho-Career-Statement-KO.pdf')]:
        data=json.loads((ROOT/'data'/f'{slug}-public.json').read_text())
        sections=[]
        for page in data['pages']:
            blocks=[]
            for b in page['blocks']:
                t=b['text']
                if t=='최순호' or 'sosaror@gmail.com' in t or t.startswith('AI Native 퍼실리테이터 ·'): continue
                tag={'heading':'h2','lead':'h3','body':'p'}[b['role']]
                rendered=escape(t).replace('\n','<br>')
                for paper in papers:
                    if t.startswith(paper['title']):
                        rendered='<a href="'+escape(paper['url'],quote=True)+'">'+rendered+'</a>'
                        break
                blocks.append(f'<{tag}>'+rendered+f'</{tag}>')
            sections.append('<section>'+''.join(blocks)+'</section>')
        css='''@font-face{font-family:G;src:url(../assets/fonts/NanumGothic-Regular.woff)}@font-face{font-family:M;src:url(../assets/fonts/NanumMyeongjo-Bold.woff)}*{box-sizing:border-box}body{margin:0;color:#303B40;background:white;font:16px/1.8 G,sans-serif}main{max-width:900px;margin:auto;padding:36px 48px 72px}nav{display:flex;gap:24px;flex-wrap:wrap;font-size:14px}a{color:#203C4B;text-underline-offset:5px;display:inline-block;padding:10px 0}a:focus-visible{outline:2px solid #203C4B;outline-offset:4px}header{border-bottom:1px solid #B68D64;padding:32px 0;margin-bottom:36px}h1{font:700 36px/1.4 M,serif;margin:0 0 10px}header p{color:#526267;margin:0}h2{font:700 23px/1.6 M,serif;border-bottom:1px solid #DBE3DF;padding:0 0 10px;margin:36px 0 22px}h3{font-size:17px;color:#203C4B;margin:26px 0 6px}section p{margin:6px 0 12px;padding-left:14px;border-left:2px solid #DBE3DF;white-space:normal;overflow-wrap:anywhere}footer{font-size:12px;color:#526267;border-top:1px solid #B68D64;margin-top:40px;padding-top:16px}@media(max-width:600px){main{padding:20px 22px 48px}h1{font-size:30px}h2{font-size:21px}nav{gap:16px}}@media print{nav{display:none}main{padding:0}h2,h3{break-after:avoid}section p{break-inside:avoid}}'''
        write_if_changed(ROOT/slug/'index.html', '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="최순호 '+title+'"><title>최순호 · '+title+'</title><style>'+css+'</style></head><body><main><nav aria-label="문서 탐색"><a href="../">포트폴리오</a><a href="../cv/">CV</a><a href="../career-statement/">경력기술서</a><a href="../assets/'+pdf+'" download>PDF 다운로드</a></nav><header><h1>최순호 · '+title+'</h1><p>AI 강사 · 연구자</p><a href="mailto:sosaror@gmail.com">sosaror@gmail.com</a></header>'+''.join(sections)+'<footer>최종 업데이트 · 2026.10.16</footer></main></body></html>')
if __name__=='__main__':build()
