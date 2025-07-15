import os
import sys

from datetime import datetime
from xml.dom.minidom import parseString

import yaml

from processor import get_abstract, get_authors, get_content

RELATON_DIR = os.getenv("MISC_RELATON_DIR", "relaton-data-misc/data/")
BIBXML_DIR = os.getenv("MISC_BIBXML_DIR", "misc")
IGNORE = [
    "IANA",
    "W3C",
    "IETF",
    "Internet-Draft",
    "3GPP",
    "IEEE",
    "NIST",
]


def get_date(data):
    if "date" in data.values():
        published_date = data["date"][0]["value"]
        try:
            date = datetime.strptime(published_date, "%Y-%m-%d")
            return date.strftime('<date day="%d" month="%B" year="%Y"/>')
        except ValueError:
            date = datetime.strptime(published_date, "%Y-%m")
            return date.strftime('<date month="%B" year="%Y"/>')
    else:
        return ""


def get_doc_id(data, doc_type):
    return f"{data['id'][len(doc_type):]}"


def get_doc_type(data):
    for doc_id in data["docid"]:
        if doc_id["primary"]:
            return doc_id["type"]


def generate_bibxml(relaton_data, doc_type):
    doc_id = get_doc_id(relaton_data, doc_type)
    doc_name = f"{doc_type}.{doc_id}"
    title = get_content(relaton_data, "title")
    abstract = get_abstract(relaton_data)
    link = get_content(relaton_data, "link")
    date = get_date(relaton_data)
    authors = get_authors(relaton_data)

    bibxml = f"""<reference anchor="{doc_name}" target="{link}"><front><title>{title}</title>{authors}{date}{abstract}</front></reference>"""

    return [doc_name, bibxml]


if not os.path.isdir(RELATON_DIR):
    print(f"relaton source dir: {RELATON_DIR} doesn't exist.")
    sys.exit(1)

os.makedirs(BIBXML_DIR, exist_ok=True)

for filename in os.listdir(RELATON_DIR):
    if filename.endswith(".yaml"):
        file_path = os.path.join(RELATON_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            print(f"Processing {file_path}")

            data = yaml.safe_load(file)

            doc_type = get_doc_type(data)
            if doc_type in IGNORE:
                print(f"Skiping {doc_type}")
                continue

            doc_name, bibxml = generate_bibxml(data, doc_type)
            dom = parseString(bibxml)
            bibxml = dom.toprettyxml(indent="  ")

            bibxml_file_path = os.path.join(BIBXML_DIR, f"reference.{doc_name}.xml")
            with open(bibxml_file_path, "w", encoding="utf-8") as bibxml_file:
                bibxml_file.write(bibxml)

            print(f"Saved {bibxml_file_path}")
