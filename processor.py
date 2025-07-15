from xml.sax.saxutils import escape, quoteattr

from lxml import etree


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


def get_authors(data):
    authors = ""
    if "contributor" not in data.keys():
        # There is no author information
        return "<author/>"
    for contributor in data["contributor"]:
        if "person" in contributor.keys():  # ignore organizations
            fullname = quoteattr(
                contributor["person"]["name"]["completename"]["content"]
            )
            try:
                initials = contributor["person"]["name"]["given"]["formatted_initials"][
                    "content"
                ]
                initials_str = f"initials={quoteattr(initials)}"
            except KeyError:
                initials_str = ""
            surname = quoteattr(contributor["person"]["name"]["surname"]["content"])
            try:
                role = quoteattr(contributor["role"][0]["type"])
                authors += f"<author fullname={fullname} {initials_str} surname={surname} role={role}/>"
            except KeyError:
                authors += (
                    f"<author fullname={fullname} {initials_str} surname={surname}/>"
                )

    return authors
