from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import json
import re


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "curriculum" / "problems" / "koi"
YEARS = range(2019, 2026)
ROUNDS = (1, 2)


class KoiPageParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.tables = []
        self.current_heading = ""
        self._heading_tag = None
        self._heading_text = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._in_link = False
        self._table = None
        self._row = None
        self._cell = None
        self._link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("h2", "h3", "h4"):
            self._heading_tag = tag
            self._heading_text = []
        elif tag == "table":
            self._in_table = True
            self._table = {"heading": self.current_heading, "rows": []}
        elif self._in_table and tag == "tr":
            self._in_row = True
            self._row = []
        elif self._in_row and tag in ("td", "th"):
            self._in_cell = True
            self._cell = {"text": "", "links": []}
        elif self._in_cell and tag == "a":
            self._in_link = True
            self._link = {"text": "", "href": urljoin(self.base_url, attrs.get("href", ""))}

    def handle_data(self, data):
        if self._heading_tag:
            self._heading_text.append(data)
        if self._in_cell and self._cell is not None:
            self._cell["text"] += data
        if self._in_link and self._link is not None:
            self._link["text"] += data

    def handle_endtag(self, tag):
        if self._heading_tag == tag:
            heading = clean("".join(self._heading_text))
            if heading:
                self.current_heading = heading
            self._heading_tag = None
            self._heading_text = []
        elif self._in_cell and tag == "a":
            self._in_link = False
            if self._link:
                self._link["text"] = clean(self._link["text"])
                self._cell["links"].append(self._link)
            self._link = None
        elif self._in_row and tag in ("td", "th"):
            self._in_cell = False
            self._cell["text"] = clean(self._cell["text"])
            self._row.append(self._cell)
            self._cell = None
        elif self._in_table and tag == "tr":
            self._in_row = False
            if self._row:
                self._table["rows"].append(self._row)
            self._row = None
        elif self._in_table and tag == "table":
            self._in_table = False
            if self._table and self._table["rows"]:
                self.tables.append(self._table)
            self._table = None


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def fetch(url):
    request = Request(url, headers={"User-Agent": "Snow0821 curriculum KOI link collector"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def classify_link(href, column=""):
    lower = href.lower()
    column = column or ""
    if "biko.kr" in lower:
        return "judge"
    if "/problems/" in lower or lower.endswith("-problems.pdf"):
        return "problem"
    if "/solutions/" in lower or lower.endswith("-answers.pdf"):
        if lower.endswith((".cpp", ".py", ".java", ".cc", ".c")):
            return "model_code"
        if lower.endswith(".zip"):
            return "solution_code_zip"
        return "solution"
    if "/tests/" in lower:
        return "test_data"
    if lower.endswith(".zip") and ("모범" in column or "코드" in column or "해설" in column):
        return "solution_code_zip"
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".zip"):
        return "zip"
    return "link"


def extract_tables(year, round_no, url, html):
    parser = KoiPageParser(url)
    parser.feed(html)
    extracted = []
    for table_index, table in enumerate(parser.tables):
        rows = table["rows"]
        if not rows:
            continue
        headers = [cell["text"] for cell in rows[0]]
        if not any(keyword in " ".join(headers) for keyword in ("문제", "정답", "해설", "테스트", "채점")):
            continue
        for row_index, row in enumerate(rows[1:], start=1):
            if len(row) != len(headers):
                continue
            cells = {headers[i] or f"column_{i + 1}": row[i] for i in range(len(headers))}
            all_links = []
            typed_links = {}
            for header, cell in cells.items():
                for link in cell["links"]:
                    link_type = classify_link(link["href"], header)
                    record = {
                        "column": header,
                        "text": link["text"],
                        "href": link["href"],
                        "type": link_type,
                    }
                    all_links.append(record)
                    typed_links.setdefault(link_type, []).append(link["href"])
            if not all_links:
                continue
            title = (
                cells.get("문제 제목", {}).get("text")
                or cells.get("문제 이름", {}).get("text")
                or cells.get("부문", {}).get("text")
                or f"row-{row_index}"
            )
            extracted.append(
                {
                    "year": year,
                    "round": round_no,
                    "page": url,
                    "section": table["heading"] or f"table-{table_index + 1}",
                    "table_index": table_index + 1,
                    "row_index": row_index,
                    "title": title,
                    "division": cells.get("출제 부문", cells.get("부문", {"text": ""}))["text"],
                    "author": cells.get("출제자", {"text": ""})["text"],
                    "cells": {key: {"text": value["text"], "links": value["links"]} for key, value in cells.items()},
                    "links": all_links,
                    "typed_links": typed_links,
                }
            )
    return extracted


def markdown_link(url, label):
    return f"[{label}]({url})" if url else ""


def links_of(item, link_type):
    urls = item["typed_links"].get(link_type, [])
    return "<br>".join(markdown_link(url, str(i + 1)) for i, url in enumerate(urls))


def write_markdown(items):
    lines = [
        "# KOI Official Link Index",
        "",
        "Updated: 2026-05-18",
        "",
        "This index is generated from the official KOI archive pages. It stores",
        "links to official problem statements, solutions, model code, test data,",
        "and BIKO judging pages without copying problem statements.",
        "",
        "Source archive: https://koi.or.kr/archives/",
        "",
        "## Coverage",
        "",
        f"- Years: 2019-2025",
        f"- Rounds: 1 and 2",
        f"- Indexed rows: {len(items)}",
        f"- Problem links: {sum(len(item['typed_links'].get('problem', [])) for item in items)}",
        f"- Solution links: {sum(len(item['typed_links'].get('solution', [])) for item in items)}",
        f"- Model-code links: {sum(len(item['typed_links'].get('model_code', [])) for item in items)}",
        f"- Solution-code zip links: {sum(len(item['typed_links'].get('solution_code_zip', [])) for item in items)}",
        f"- Test-data links: {sum(len(item['typed_links'].get('test_data', [])) for item in items)}",
        f"- Judge links: {sum(len(item['typed_links'].get('judge', [])) for item in items)}",
        "",
        "## Index",
        "",
    ]
    for year in YEARS:
        lines.extend([f"### {year}", ""])
        for round_no in ROUNDS:
            subset = [item for item in items if item["year"] == year and item["round"] == round_no]
            lines.extend([f"#### Round {round_no}", ""])
            if not subset:
                lines.extend(["No indexed rows.", ""])
                continue
            lines.extend(
                [
                    "| Section | Title | Division | Judge | Problem | Solution | Code | Tests |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                ]
            )
            for item in subset:
                code_links = "<br>".join(
                    part
                    for part in [links_of(item, "model_code"), links_of(item, "solution_code_zip")]
                    if part
                )
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            item["section"],
                            item["title"],
                            item["division"],
                            links_of(item, "judge"),
                            links_of(item, "problem") or links_of(item, "pdf"),
                            links_of(item, "solution"),
                            code_links,
                            links_of(item, "test_data"),
                        ]
                    )
                    + " |"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def write_round2_2025(items):
    subset = [item for item in items if item["year"] == 2025 and item["round"] == 2]
    lines = [
        "# KOI 2025 Round 2 Link Index",
        "",
        "Official page: https://koi.or.kr/koi/2025/2/",
        "",
        "The official page provides problem PDFs, solution PDFs, model code, test",
        "data, and BIKO judging links. This file keeps a lightweight teaching",
        "index without duplicating problem statements.",
        "",
        "| Problem | Division | Judge | Problem PDF | Solution | Code | Tests | First teaching placement |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    placements = {
        "장애물": "K1-K2 implementation and reading",
        "거울": "K3 observation bridge",
        "점프": "K4-K5 transition problem",
        "통행료": "K4 implementation and optimization bridge",
        "가방": "K5 middle-stage target",
        "새로운 인연": "K6-K7 graph/structure bridge",
        "로봇": "K6 implementation-heavy search",
        "상자 보관": "K6 interval/data-structure bridge",
        "수열과 쿼리": "K8 advanced query optimization",
        "축제": "K8 advanced tree DP",
    }
    for item in subset:
        title = item["title"]
        code_links = "<br>".join(
            part for part in [links_of(item, "model_code"), links_of(item, "solution_code_zip")] if part
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    title,
                    item["division"],
                    links_of(item, "judge"),
                    links_of(item, "problem"),
                    links_of(item, "solution"),
                    code_links,
                    links_of(item, "test_data"),
                    placements.get(title, "TBD"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Collection Notes",
            "",
            "- 2025 round 2 has 10 unique problems across elementary, middle, and high divisions.",
            "- Shared problems confirm the project-memory decision to use one continuous K0-K9 ladder.",
            "- Elementary problem 4 can still be a K6-level bridge problem; division number alone is not a sufficient difficulty signal.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_test_data_index(items):
    test_items = [item for item in items if item["typed_links"].get("test_data")]
    lines = [
        "# KOI Test Data Link Index",
        "",
        "Updated: 2026-05-18",
        "",
        "This file lists official KOI test-data zip links exposed from the KOI",
        "archive pages. It is a link inventory only; the zip files are not",
        "redistributed in this repository.",
        "",
        f"Indexed test-data rows: {len(test_items)}",
        "",
        "| Year | Round | Section | Title | Division | Test data |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in test_items:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["year"]),
                    str(item["round"]),
                    item["section"],
                    item["title"],
                    item["division"],
                    links_of(item, "test_data"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    pages = []
    for year in YEARS:
        for round_no in ROUNDS:
            url = f"https://koi.or.kr/koi/{year}/{round_no}/"
            html = fetch(url)
            page_items = extract_tables(year, round_no, url, html)
            pages.append({"year": year, "round": round_no, "url": url, "indexed_rows": len(page_items)})
            items.extend(page_items)
    data = {
        "updated": "2026-05-18",
        "source_archive": "https://koi.or.kr/archives/",
        "pages": pages,
        "items": items,
    }
    (OUT_DIR / "official-link-index.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "official-link-index.md").write_text(write_markdown(items), encoding="utf-8")
    (OUT_DIR / "test-data-index.md").write_text(write_test_data_index(items), encoding="utf-8")
    (OUT_DIR / "2025-round2.md").write_text(write_round2_2025(items), encoding="utf-8")
    print(json.dumps({
        "pages": len(pages),
        "items": len(items),
        "problem_links": sum(len(item["typed_links"].get("problem", [])) for item in items),
        "solution_links": sum(len(item["typed_links"].get("solution", [])) for item in items),
        "test_data_links": sum(len(item["typed_links"].get("test_data", [])) for item in items),
        "judge_links": sum(len(item["typed_links"].get("judge", [])) for item in items),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
