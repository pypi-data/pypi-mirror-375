import re

BANNED_SECTION_PREFIXES = ["bibliography of", "\\d+ index\\s*$"]
_BANNED_SECTION_PREFIXES_REGEXP_PART = "|".join(BANNED_SECTION_PREFIXES)
BANNED_SECTION_PREFIXES_REGEXP = re.compile(
    rf"^({_BANNED_SECTION_PREFIXES_REGEXP_PART})", flags=re.IGNORECASE
)

BANNED_SECTIONS = {
    "abbreviations",
    "academic books",
    "academic journal articles",
    "acknowledgment",
    "acknowledgments",
    "acknowledgements",
    "author contribution",
    "bibliography",
    "bibliography and references",
    "conflict of interest",
    "conflict of interest disclosures",
    "conflict of interest statement",
    "conflicts of interest statement",
    "contents",
    "copyright",
    "data availability",
    "data availability statement",
    "declarations",
    "declaration of competing interest",
    "disclosure",
    "ethics statement",
    "external links",
    "footnotes",
    "full citations can be found in the bibliography",
    "further reading",
    "index",
    "keywords",
    "list of hyperlinks",
    "notes on images",
    "supporting information",
    "table of content",
    "references",
    "sources",
    "suggested readings",
    "supplementary information",
    "table of contents",
    "works cited",
    "verlagsprogramm",
    "содержание",
    "список литературы",
    "источники",
    "ссылки",
    "благодарность",
    "благодарности",
    "литература",
    "оглавление",
    "примечания",
    "обратная связь",
    "сборники документов",
    "рекомендуемая литература",
}

SECTIONS_MAPS = {
    "abstract": "Abstract",
    "acknowledgement": "Acknowledgements",
    "acknowledgments": "Acknowledgements",
    "acknowledgements": "Acknowledgements",
    "authors": "Authors",
    "authors' contributions": "Author Contribution",
    "biographies": "Bibliography",
    "bibliography and references": "Bibliography",
    "conflict of interest": "Disclosure",
    "conflict of interest disclosures": "Disclosure",
    "conflict of interest statement": "Disclosure",
    "conflictofintereststatement": "Disclosure",
    "conclusions": "Conclusions",
    "conclusions and future applications": "Conclusions",
    "date": "Date",
    "declaration of conflicting interests": "Disclosure",
    "declaration of competing interest": "Disclosure",
    "disclaimer": "Disclosure",
    "disclosure": "Disclosure",
    "discussion": "Discussion",
    "funding": "Funding",
    "fundinginformation": "Funding",
    "introduction": "Introduction",
    "materials and methods": "Methods",
    "methods": "Methods",
    "referencesfigure": "References Figure",
    "results": "Results",
    "tables": "Tables",
    "tabnles": "Tables",
}


def is_banned_section(text: str):
    text = text.lower()
    stripped_text = re.sub(r"^\d+\s*\.\s*", "", text).strip()
    return (
        text in BANNED_SECTIONS
        or stripped_text in BANNED_SECTIONS
        or BANNED_SECTION_PREFIXES_REGEXP.match(text)
        or BANNED_SECTION_PREFIXES_REGEXP.match(stripped_text)
    )
