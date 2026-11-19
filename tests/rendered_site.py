"""Read the generated public pages without requiring a browser or a DOM dependency."""
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ("education", "employment", "teaching", "training", "credentials", "awards", "writing")
LANGUAGES = ("ko", "en")
PAGES = ("", "portfolio", "career")
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        element = SubElement(self.stack[-1], tag, {key: value or "" for key, value in attrs})
        if tag not in VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        parent = self.stack[-1]
        if len(parent):
            last = parent[-1]
            last.tail = (last.tail or "") + data
        else:
            parent.text = (parent.text or "") + data


def page_path(lang, tab=""):
    return ROOT / ("en" if lang == "en" else "") / tab / "index.html"


@lru_cache(maxsize=None)
def page(lang="ko", tab=""):
    parser = DocumentParser()
    parser.feed(page_path(lang, tab).read_text(encoding="utf-8"))
    parser.close()
    return parser.root


def text(node):
    if node is None:
        raise AssertionError("Expected element was missing from generated HTML")
    return " ".join(" ".join(node.itertext()).split())


def section(lang, identifier):
    node = page(lang, "career").find('.//*[@id="' + identifier + '"]')
    if node is None:
        raise AssertionError(f"{lang} career page is missing #{identifier}")
    return node
