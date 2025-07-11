import os
import sys

from datetime import datetime
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape

import yaml
from lxml import etree

RELATON_DIR = os.getenv("RFC_RELATON_DIR", "relaton-data-rfcs/data/")
BIBXML_DIR = os.getenv("RFC_BIBXML_DIR", "rfcs")


def get_content(data, field, escape_content=True):
    try:
        content = data[field][0]["content"]
        if escape_content:
            return escape(content)
        else:
            return content
    except KeyError:
        return ""


def get_abstract(data):
    abstract = get_content(data, "abstract", escape_content=False)
    if abstract:
        paragraphs = []
        try:
            tree = etree.fromstring(f"<t>{abstract}</t>")
            paragraphs = [
                p.text
                for p in tree.findall("p")
                if (getattr(p, "text", "") or "").strip() != ""
            ]
        except (etree.XMLSyntaxError, ValueError):
            paragraphs = [p.strip() for p in abstract.split("\n\n") if p.strip() != ""]
        return f"<abstract><t>{escape(' '.join(paragraphs))}</t></abstract>"
    else:
        return ""


def get_doi(data):
    for docid in data["docid"]:
        if docid["type"] == "DOI":
            return docid["id"]


def get_date(data):
    published_date = data["date"][0]["value"]
    date = datetime.strptime(published_date, "%Y-%m")
    return date.strftime('<date month="%B" year="%Y"/>')


def get_authors(data):
    authors = ""
    for contributor in data["contributor"]:
        if "person" in contributor.keys():  # ignore organizations
            fullname = escape(contributor["person"]["name"]["completename"]["content"])
            try:
                initials = contributor["person"]["name"]["given"]["formatted_initials"][
                    "content"
                ]
                initials_str = f'initials="{escape(initials)}"'
            except KeyError:
                initials_str = ""
            surname = escape(contributor["person"]["name"]["surname"]["content"])
            try:
                role = escape(contributor["role"][0]["type"])
                authors += f'<author fullname="{fullname}" {initials_str} surname="{surname}" role="{role}"/>'
            except KeyError:
                authors += f'<author fullname="{fullname}" {initials_str}" surname="{surname}/>'

    return authors


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
