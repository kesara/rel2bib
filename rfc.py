import os
import sys

from datetime import datetime

import yaml

RELATON_DIR = os.getenv("RFC_RELATON_DIR", "relaton-data-rfcs/data/")
BIBXML_DIR = os.getenv("RFC_BIBXML_DIR", "rfcs")


def get_content(data, field):
    try:
        return data[field][0]["content"]
    except KeyError:
        return ""


def get_abstract(data):
    abstract = get_content(data, "abstract")
    if abstract:
        return f"<abstract><t>{abstract}</t></abstract>"
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
            fullname = contributor["person"]["name"]["completename"]["content"]
            try:
                initials = contributor["person"]["name"]["given"]["formatted_initials"][
                    "content"
                ]
                initials_str = f'initials="{initials}"'
            except KeyError:
                initials_str = ""
            surname = contributor["person"]["name"]["surname"]["content"]
            try:
                role = contributor["role"][0]["type"]
                authors += f'<author fullname="{fullname}" {initials_str} surname="{surname} role="{role}"/>'
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

    bibxml = f"""<reference anchor="{rfc}" target="{link}">
<front>
    <title>{title}</title>
    {authors}
    {date}
    {abstract}
</front>
<seriesInfo name="RFC" value="{rfc_number}"/>
<seriesInfo name="DOI" value="{doi}"/>
</reference>"""

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

            bibxml_file_path = os.path.join(
                RELATON_DIR, f"reference.RFC.{rfc_number}.xml"
            )
            with open(bibxml_file_path, "w", encoding="utf-8") as bibxml_file:
                bibxml_file.write(bibxml)

            print(f"Saved {bibxml_file_path}")
