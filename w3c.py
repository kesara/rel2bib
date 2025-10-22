import os
import sys

from datetime import datetime
from xml.dom.minidom import parseString

import yaml

from processor import get_content

RELATON_DIR = os.getenv("W3C_RELATON_DIR", "relaton-data-w3c/data/")
BIBXML_DIR = os.getenv("W3C_BIBXML_DIR", "w3c")


def get_doc_id(data):
    return f"W3C.{data["id"][3:]}"


def generate_bibxml(relaton_data):
    doc_id = get_doc_id(relaton_data)
    title = get_content(relaton_data, "title")
    link = get_content(relaton_data, "link")

    bibxml = f"""<reference anchor="{doc_id}" target="{link}"><front><title>{title}</title></front></reference>"""

    return [doc_id, bibxml]


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
            doc_id, bibxml = generate_bibxml(data)
            dom = parseString(bibxml)
            bibxml = dom.toprettyxml(indent="  ")

            bibxml_file_path = os.path.join(BIBXML_DIR, f"reference.{doc_id}.xml")
            with open(bibxml_file_path, "w", encoding="utf-8") as bibxml_file:
                bibxml_file.write(bibxml)

            print(f"Saved {bibxml_file_path}")
