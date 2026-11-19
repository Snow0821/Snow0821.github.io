"""Build the single-page public instructor profile with the shared PDF renderer."""
import argparse
import json
import os
from pathlib import Path

from build_cv import render, output_path as default_pdf_path
from build_documents import ROOT


def build(output_path=None):
    data = json.loads((ROOT / "data" / "instructor-profile.json").read_text(encoding="utf-8"))
    blocks = []

    def add(role, text, link=None):
        block = {"role": role, "text": text}
        if link:
            block["link"] = link
        blocks.append(block)

    add("body", data["shortBio"]["ko"])
    for heading, records in (("currentTitle", "current"), ("experienceTitle", "experience")):
        add("heading", data[heading]["ko"])
        for record in data[records]:
            add("lead", record["organization"]["ko"] + " · " + record["role"]["ko"])
            add("meta", record["period"]["ko"])
            add("body", record["description"]["ko"])
    add("heading", data["educationTitle"]["ko"])
    for record in data["educationRecords"]:
        add("body", f"{record['school']['ko']} · {record['field']['ko']} {record['degree']['ko']} ({record['year']})")
    add("heading", data["paperTitle"]["ko"])
    paper = data["representativePaper"]
    add("lead", paper["title"], paper["url"])
    add("meta", paper["venue"] + " · " + paper["authorRole"]["ko"])
    default = default_pdf_path(data["pdfFilename"])
    if os.environ.get("INSTRUCTOR_PROFILE_OUTPUT_DIR"):
        default = Path(os.environ["INSTRUCTOR_PROFILE_OUTPUT_DIR"]) / data["pdfFilename"]
    return render(data["title"]["ko"], data["role"]["ko"], "ko", data["updated"],
                  [{"blocks": blocks}], Path(output_path) if output_path else default)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    print(build(parser.parse_args().output))
