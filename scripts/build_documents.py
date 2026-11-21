"""Generate responsive Korean reading pages from the same copy as the PDFs."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path

from design import css_tokens

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = {
    "cv": ("국문 CV", "Choi-Soon-Ho-CV-KO.pdf"),
    "career-statement": ("경력기술서", "Choi-Soon-Ho-Career-Statement-KO.pdf"),
}


def read_copy(slug):
    return json.loads((ROOT / "data" / f"{slug}-public.json").read_text(encoding="utf-8"))


def write_if_changed(path, data):
    if not path.is_file() or path.read_bytes() != data:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def html_block(block):
    tag = {"heading": "h2", "lead": "h3", "body": "p", "meta": "p"}[block["role"]]
    value = "<br>".join(escape(line) for line in block["text"].splitlines())
    if block.get("link"):
        value = f'<a href="{escape(block["link"], quote=True)}">{value}</a>'
    attrs = ' class="entry-meta"' if block["role"] == "meta" else ""
    return f"<{tag}{attrs}>{value}</{tag}>"


def build():
    css_version = sha256((ROOT / "cv/documents.css").read_bytes()).hexdigest()[:12]
    for slug, (title, filename) in DOCUMENTS.items():
        copy = read_copy(slug)
        content = "\n".join(html_block(block) for page in copy["pages"] for block in page["blocks"])
        date = copy["updated"]
        related = '<a href="../assets/Choi-Soon-Ho-CV-EN.pdf">English CV (PDF)</a>' if slug == "cv" else '<a href="../cv/">국문 CV</a>'
        html = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="독립연구자이자 AI·CS 강사 최순호의 {title}">
<title>최순호 · {title}</title><style>{css_tokens()}</style><link rel="stylesheet" href="../cv/documents.css?v={css_version}">
</head><body>
<a class="skip" href="#document">본문 바로가기</a>
<header class="masthead"><a class="name" href="../">최순호</a>
<nav aria-label="사이트 탐색"><a href="../">메인</a><a href="../portfolio/">포트폴리오</a><a href="../career/">전체 이력</a></nav></header>
<main id="document"><header class="doc-intro"><h1>{title}</h1>
<p>최순호 <span>·</span> 독립연구자 · AI·CS 강사</p>
<div class="doc-actions"><a href="../assets/{filename}" download>PDF 다운로드</a>{related}
<a href="mailto:sosaror@gmail.com">이메일</a></div></header>
<article aria-label="{title}">{content}</article>
<footer><time datetime="{date}">{date.replace('-', '.')} 기준</time><a href="../career/">전체 이력</a></footer>
</main></body></html>
"""
        write_if_changed(ROOT / slug / "index.html", html.encode("utf-8"))


if __name__ == "__main__":
    build()
