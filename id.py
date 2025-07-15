import os
import sys

from datetime import datetime
from xml.dom.minidom import parseString

import yaml

from processor import get_abstract, get_authors, get_content

RELATON_DIR = os.getenv("ID_RELATON_DIR", "relaton-data-ids/data/")
BIBXML_DIR = os.getenv("ID_BIBXML_DIR", "ids")


def get_date(data):
    published_date = data["date"][0]["value"]
    date = datetime.strptime(published_date, "%Y-%m-%d")
    return date.strftime('<date day="%d" month="%B" year="%Y"/>')


def get_anchor(data):
    for doc_id in data["docid"]:
        if "scope" in doc_id.keys() and doc_id["scope"] == "anchor":
            return doc_id["id"]
    return ""


def is_non_revision(data):
    if "link" not in data.keys():
        return True
    else:
        return False


def get_latest_draft(data):
    latest = ""
    latest_revision = -1
    for rel in data["relation"]:
        revision = rel["bibitem"]["id"].split("-")[-1]
        if latest_revision < int(revision):
            latest_revision = int(revision)
            latest = rel["bibitem"]["id"]
    return latest


def generate_bibxml(relaton_data):
    doc_name = relaton_data["id"]
    title = get_content(relaton_data, "title")
    abstract = get_abstract(relaton_data)
    if is_non_revision(relaton_data):
        latest = get_latest_draft(data)
        file_path = os.path.join(RELATON_DIR, f"{latest}.yaml")
        with open(file_path, "r", encoding="utf-8") as file:
            print(f"Processing {file_path}")
            relaton_data = yaml.safe_load(file)
    anchor = get_anchor(relaton_data)
    link = get_content(relaton_data, "link")
    date = get_date(relaton_data)
    authors = get_authors(relaton_data)

    bibxml = f"""<reference anchor="{anchor}" target="{link}"><front><title>{title}</title>{authors}{date}{abstract}</front><seriesInfo name="Internet-Draft" value="{doc_name}"/></reference>"""

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
            doc_name, bibxml = generate_bibxml(data)
            dom = parseString(bibxml)
            bibxml = dom.toprettyxml(indent="  ")

            bibxml_file_path = os.path.join(BIBXML_DIR, f"reference.I-D.{doc_name}.xml")
            with open(bibxml_file_path, "w", encoding="utf-8") as bibxml_file:
                bibxml_file.write(bibxml)

            print(f"Saved {bibxml_file_path}")
