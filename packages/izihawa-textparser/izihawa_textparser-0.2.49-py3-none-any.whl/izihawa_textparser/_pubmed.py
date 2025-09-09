import datetime
import re
import time

import iso639
import xmltodict
from bs4 import BeautifulSoup, NavigableString
from izihawa_textutils.html_processing import canonize_tags
from izihawa_textutils.utils import canonize_doi

from ._banned_sections import BANNED_SECTIONS, SECTIONS_MAPS
from .utils import md


def _process_single_pubmed_central_part(
    soup: BeautifulSoup,
    banned_sections: set[str] = BANNED_SECTIONS,
    section_maps: dict[str, str] = SECTIONS_MAPS,
):
    secs = []
    for rep in reversed(range(1, 5)):
        for h in soup.select("section > " * rep + "title"):
            if not h.text.strip():
                h.extract()
            else:
                h.name = f"h{rep + 1}"
            title = section_maps.get(h.text.lower()) or h.text
            title = re.sub(r"\s{2,}", " ", title.replace("\n", " ")).strip()
            if title.lower() in banned_sections:
                h.parent.extract()
            else:
                h.string = title

    for t in soup.select("fig > label, table-wrap > label, caption > title"):
        t.name = "p"

    for sec in soup.children:
        if isinstance(sec, NavigableString):
            secs.append(md.convert(sec))
        else:
            secs.append(md.convert_soup(sec))

    return "\n\n".join(secs)


def process_pubmed_central(text: str):
    text = re.sub(r"<\?properties.*?\?>", "", text)
    raw_text = re.sub(r"\s{2,}", " ", text.replace("\n", " ")).strip()
    soup = BeautifulSoup(raw_text, "lxml")

    document = {"id": {}, "type": "journal-article"}
    metadata = {
        "source": "pmc",
        "content": {
            "source": {
                "name": "pmc",
                "version": "1.0.0",
            },
            "parser": {"name": "textparser", "version": "0.2.40"},
            "parsed_at": int(time.time()),
        },
    }
    if doi_tag := soup.select_one('article-meta > article-id[pub-id-type="doi"]'):
        document["id"]["dois"] = [canonize_doi(doi_tag.text)]
    if pubmed_id_tag := soup.select_one(
        'article-meta > article-id[pub-id-type="pmid"]'
    ):
        document["id"]["pubmed_id"] = int(pubmed_id_tag.text)
    if pmc_id_tag := soup.select_one('article-meta > article-id[pub-id-type="pmc"]'):
        document["id"]["pmc_id"] = int(pmc_id_tag.text.removeprefix("PMC"))

    soup = canonize_tags(soup)

    for issn in soup.select("front issn"):
        metadata.setdefault("issns", [])
        metadata["issns"].append(issn.text.lower())
    for publisher in soup.select("front publisher > publisher-name"):
        metadata["publisher"] = publisher.text
    for title in soup.select("title-group > article-title"):
        document["title"] = md.convert_soup(title)
    for series in soup.select("front series-title"):
        metadata["series"] = series.text
    for journal in soup.select("front journal-title"):
        metadata["container_title"] = journal.text

    for volume in soup.select("front volume"):
        metadata["volume"] = volume.text
    for issue in soup.select("front issue"):
        metadata["issue"] = issue.text
    try:
        for fpage in soup.select("front fpage"):
            metadata["first_page"] = int(fpage.text)
    except Exception:
        pass
    try:
        for lpage in soup.select("front lpage"):
            metadata["last_page"] = int(lpage.text)
    except Exception:
        pass
    for volume in soup.select("front volume"):
        metadata["volume"] = volume.text

    if date := soup.select_one('pub-date[pub-type="epub"]'):
        month = date.select_one("month")
        month = int(month.text) if month else 1
        day = date.select_one("day")
        day = int(day.text) if day else 1
        document["issued_at"] = int(
            time.mktime(
                datetime.datetime(
                    year=int(date.select_one("year").text),
                    month=month,
                    day=day,
                ).utctimetuple()
            )
        )

    ready_authors = []
    for author in soup.select('front contrib-group > contrib[contrib-type="author"]'):
        ready_author = {}
        if surname := author.select_one("name > surname"):
            ready_author["family"] = surname.text
        if surname := author.select_one("name > given-names"):
            ready_author["given"] = surname.text
        if ready_author:
            ready_authors.append(ready_author)

    document["authors"] = ready_authors

    if abstract_tag := soup.select_one("abstract"):
        if abstract := md.convert_soup(abstract_tag).strip():
            if abstract.startswith("pmc") and not abstract[3].isalpha():
                abstract = abstract.removeprefix("pmc")
            document["abstract"] = abstract

    body = soup.select_one("body")
    for part in list(
        body.select(
            "abstract, back, front, journal-id, journal-meta,"
            " license, processing-meta, properties, ref-list, related-article, supplementary-material"
        )
    ):
        part.extract()
    content = _process_single_pubmed_central_part(body)

    if content:
        if content.startswith("pmc") and not content[3].isalpha():
            content = content.removeprefix("pmc")
        document["content"] = content
    if metadata:
        document["metadata"] = metadata
    return document


def process_single_record(item):
    medline_citation = item["MedlineCitation"]
    article = medline_citation["Article"]
    pubmed_data = item["PubmedData"]
    issued_date = None

    for date in pubmed_data["History"]["PubMedPubDate"]:
        if date["@PubStatus"] == "pubmed":
            issued_date = date

    document = {
        "id": {"pubmed_id": int(medline_citation["PMID"]["#text"])},
        "metadata": {
            "source": "pmc",
            "content": {
                "source": {
                    "name": "pmc",
                    "version": "1.0.0",
                },
                "parser": {"name": "textparser", "version": "0.2.40"},
                "parsed_at": int(time.time()),
            },
        },
        "type": "journal-article",
        "issued_at": int(
            time.mktime(
                datetime.datetime(
                    year=int(issued_date["Year"]),
                    month=int(issued_date["Month"]),
                    day=int(issued_date["Day"]),
                ).utctimetuple()
            )
        ),
    }

    doi = None
    pii = None

    article_id_list = pubmed_data["ArticleIdList"]["ArticleId"]
    if not isinstance(article_id_list, list):
        article_id_list = [article_id_list]

    for article_id in article_id_list:
        if article_id["@IdType"] == "doi" and "#text" in article_id:
            doi = article_id["#text"].lower().strip()
        if article_id["@IdType"] == "pii" and "#text" in article_id:
            pii = article_id["#text"].strip()

    tags = []
    mesh_heading = medline_citation.get("MeshHeadingList", {"MeshHeading": []})[
        "MeshHeading"
    ]
    if not isinstance(mesh_heading, list):
        mesh_heading = [mesh_heading]
    for mesh_term in mesh_heading:
        tags.append(mesh_term["DescriptorName"]["#text"])
    if tags:
        document["tags"] = tags

    if not article.get("ArticleTitle") or isinstance(article["ArticleTitle"], dict):
        return
    document["title"] = article["ArticleTitle"].strip(".")
    if document["title"].startswith("[") and document["title"].endswith("]"):
        document["title"] = document["title"].lstrip("[").rstrip("]")
    if isinstance(article["Language"], list):
        document["languages"] = [
            iso639.Language.match(lang).part1 for lang in article["Language"]
        ]
    else:
        document["languages"] = [iso639.Language.match(article["Language"]).part1]
    if "ISSN" in article["Journal"]:
        document["metadata"]["issns"] = [article["Journal"]["ISSN"]["#text"]]
    if "Volume" in article["Journal"]["JournalIssue"]:
        document["metadata"]["volume"] = article["Journal"]["JournalIssue"]["Volume"]
    if "Issue" in article["Journal"]["JournalIssue"]:
        document["metadata"]["issue"] = article["Journal"]["JournalIssue"]["Issue"]
    document["metadata"]["container_title"] = (
        article["Journal"]["Title"].split("=")[0].strip()
    )
    try:
        if medline_pgn := article["Pagination"].get("MedlinePgn"):
            pages = medline_pgn.split("-")
            if len(pages) == 2:
                first_page, last_page = pages
                first_page = int(first_page.rstrip("P"))
                last_page = int(last_page.rstrip("P"))
                if last_page < first_page:
                    last_page = int(
                        str(first_page)[: len(str(first_page)) - len(str(last_page))]
                        + str(last_page)
                    )
                (
                    document["metadata"]["first_page"],
                    document["metadata"]["last_page"],
                ) = (first_page, last_page)
            elif len(pages) == 1:
                document["metadata"]["first_page"] = int(pages[0].rstrip("P"))
    except (KeyError, ValueError):
        pass
    if "AuthorList" in article:
        author_list = article["AuthorList"]["Author"]
        if not isinstance(author_list, list):
            author_list = [author_list]
        ready_authors = []
        for author in author_list:
            ready_author = {}
            if "LastName" in author:
                ready_author["family"] = author["LastName"]
            if "ForeName" in author:
                ready_author["given"] = author["ForeName"]
            if ready_author:
                ready_authors.append(ready_author)
        document["authors"] = ready_authors
    if "Abstract" in article:
        if isinstance(article["Abstract"]["AbstractText"], list):
            sections = []
            for part in article["Abstract"]["AbstractText"]:
                if part and "#text" in part:
                    if part.get("@Label") == "UNLABELLED":
                        sections.append(part["#text"])
                    else:
                        if "@Label" in part:
                            label = part["@Label"].capitalize() + ":"
                            sections.append(f"## {label}")
                        sections.append(md.convert(part["#text"].capitalize()))
            abstract = "\n\n".join(sections).strip()
        else:
            abstract = article["Abstract"]["AbstractText"]
            if isinstance(abstract, dict):
                abstract = abstract.get("#text")
            if abstract:
                abstract = md.convert(abstract).strip()
        if abstract:
            document["abstract"] = abstract

    publication_type_list = article["PublicationTypeList"]["PublicationType"]
    if not isinstance(publication_type_list, list):
        publication_type_list = [publication_type_list]

    is_article = False
    stored_publication_type = None
    for publication_type in publication_type_list:
        stored_publication_type = publication_type["#text"]
        is_article = is_article or stored_publication_type in (
            "Journal Article",
            "Historical Article",
            "Case Reports",
            "Comment",
            "Comparative Study",
            "Review",
            "Letter",
            "News",
            "Bibliography",
            "Retraction of Publication",
        )

    if not is_article:
        return

    if doi:
        document["id"]["dois"] = [canonize_doi(doi.lower().strip())]
    if pii:
        document["id"]["pii"] = pii

    return document, stored_publication_type


def process_pubmed_archive(data):
    data_dict = xmltodict.parse(data)
    for item in data_dict["PubmedArticleSet"]["PubmedArticle"]:
        result = process_single_record(item)
        if result:
            yield result
