import os
import sys

from datetime import datetime
from xml.dom.minidom import parseString

import yaml

from processor import get_abstract, get_authors, get_content

RELATON_DIR = os.getenv("RFC_RELATON_DIR", "relaton-data-rfcs/data/")
BIBXML_DIR = os.getenv("RFC_BIBXML_DIR", "rfcs")


def get_date(data):
    published_date = data["date"][0]["value"]
    date = datetime.strptime(published_date, "%Y-%m")
    return date.strftime('<date month="%B" year="%Y"/>')


def get_doi(data):
    for docid in data["docid"]:
        if docid["type"] == "DOI":
            return docid["id"]


def generate_bibxml(relaton_data):
    rfc = relaton_data["id"]  # RFCNNNNN
    rfc_number = rfc[3:]  # NNNNN
    link = get_content(relaton_data, "link")
    title = get_content(relaton_data, "title")
    doi = get_doi(relaton_data)
    date = get_date(relaton_data)
    abstract = get_abstract(relaton_data)
    authors = get_authors(relaton_data)

    bibxml = f"""<reference anchor="{rfc}" target="{link}"><front><title>{title}</title>{authors}{date}{abstract}</front><seriesInfo name="RFC" value="{rfc_number}"/><seriesInfo name="DOI" value="{doi}"/></reference>"""

    return [rfc_number, bibxml]


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
            rfc_number, bibxml = generate_bibxml(data)
            dom = parseString(bibxml)
            bibxml = dom.toprettyxml(indent="  ")

            bibxml_file_path = os.path.join(
                BIBXML_DIR, f"reference.RFC.{rfc_number}.xml"
            )
            with open(bibxml_file_path, "w", encoding="utf-8") as bibxml_file:
                bibxml_file.write(bibxml)

            print(f"Saved {bibxml_file_path}")
