"""Every citation this repository publishes, rendered from one place.

    cite.api in docs/api/index.json            the API/dataset of a release: APA 7, BibTeX, CSL-JSON
    citation in docs/api/cases/{id}.json       the Zenodo dataset of one case: APA 7, BibTeX
    docs/_includes/cite.md                     the About page's Cite section
    README.md between <!--cite--> and <!--/cite-->
    the Cite section of every case's Data page
    CITATION.cff, .zenodo.json                 GitHub's "Cite this repository" and Zenodo's GitHub integration

scripts/build_api.py writes all of them with these functions, scripts/check_citation.py checks them, and a release
bump (VERSION, its CHANGELOG.md date, the data version of the build) is the only input that changes them: the title,
the author, the keywords and the pinned address are defined once, here.

The API's DOI does not exist until Zenodo mints one. Set API_DOI below when it does; the citations, CITATION.cff and
index.json follow on the next build. Nothing prints a placeholder before then.

Standard library only; the data a function needs (the cases) is passed in, so a test can fix every input.
"""
from __future__ import annotations

import json
import re
from collections import namedtuple

ORG = "Sustainable Urban Systems Lab"
REPO_URL = "https://github.com/Eddy3D-Dev/AIJ-Data-Validation"
SITE = "https://aij.eddy3d.com"
TITLE = ("AIJ Urban Wind Environment benchmark, Cases A-M: cleaned wind-tunnel and field data, "
         "geometry and validation API")
ABSTRACT = ("Cleaned wind-tunnel and field data of the AIJ Urban Wind Environment benchmark, Cases A-M, with their "
            "geometry and Eddy3D's validation scores, served as static JSON, CSV and STL files.")
KEYWORDS = ["computational fluid dynamics", "CFD validation", "wind tunnel", "urban wind environment", "pedestrian wind",
            "Architectural Institute of Japan"]
LICENSE = "CC-BY-4.0"
API_AUTHORS = [("Karadag", "Ilker"), ("Kastner", "Patrick")]    # who made this API; the lab publishes it
API_DOI = None        # the DOI Zenodo mints for this API's releases; None until it exists

# The release a citation names: VERSION, its date in CHANGELOG.md, and the build's data version (SHA-256 of the data).
Release = namedtuple("Release", "version date data_version")

# The data paper, and the guidelines it builds on (CITATION.cff lists the second as a reference).
PAPER = {
    "authors": [("Kikumoto", "H."), ("Okaze", "T."), ("Yoshie", "R."), ("Tachibana", "T."), ("Ishihara", "T."),
                ("Nonomura", "Y."), ("Kiyota", "N."), ("Kondo", "H."), ("Mochida", "A."), ("Tominaga", "Y.")],
    "year": 2026,
    "title": ("Comprehensive Experimental Database for Validating CFD Simulations in Urban Wind Environment: "
              "Benchmark Cases Curated by the Architectural Institute of Japan"),
    "journal": "Japan Architectural Review", "volume": 9, "issue": 1, "pages": "e70083",
    "doi": "10.1002/2475-8876.70083",
}
GUIDELINES = {
    "authors": [("Tominaga", "Y."), ("Mochida", "A."), ("Yoshie", "R."), ("Kataoka", "H."), ("Nozu", "T."),
                ("Yoshikawa", "M."), ("Shirasawa", "T.")],
    "year": 2008,
    "title": "AIJ guidelines for practical applications of CFD to pedestrian wind environment around buildings",
    "journal": "Journal of Wind Engineering and Industrial Aerodynamics", "volume": 96, "pages": "1749-1761",
    "doi": "10.1016/j.jweia.2008.02.058",
}

# The Zenodo record of each case: its title, and its date where this repository states one. The DOI is the case's own
# (aijdata.CASES[id]["doi"]); the authors are the case's people (case_people). All records are from 2025.
ZENODO_YEAR = 2025
ZENODO = {
    "A": ("AIJ UWE Benchmark Dataset – Case A (112): Wind Tunnel Experiment for Flow around a 1:1:2 Shape Building Model", "2025-03-19"),
    "B": ("AIJ UWE Benchmark Dataset – Case B (144): Wind Tunnel Experiment for Flow around a 1:4:4 Shape Building Model", "2025-05-14"),
    "C": ("AIJ UWE Benchmark Dataset – Case C (Blocks): Wind Tunnel Experiment for Flow within Simple Building Blocks", "2025-05-14"),
    "D": ("AIJ UWE Benchmark Dataset – Case D (Highrise): Wind Tunnel Experiment for Flow around a High-rise Building in City Blocks", "2025-05-14"),
    "E": ("AIJ UWE Benchmark Dataset – Case E (Niigata): Wind Tunnel Experiment for Flow within an Actual Urban Area in Niigata", "2025-05-16"),
    "F": ("AIJ UWE Benchmark Dataset – Case F (Shinjuku): Wind Tunnel Experiment and Field Observation for Flow within an Actual Urban Area in Shinjuku", None),
    "G": ("AIJ UWE Benchmark Dataset – Case G (Tree): Field Observation for Flow behind Tree Belt", None),
    "H": ("AIJ UWE Benchmark Dataset – Case H (112C): Wind Tunnel Experiment for Flow and Dispersion around a 1:1:2 Shape Building Model", None),
    "I": ("AIJ UWE Benchmark Dataset – Case I (CubeC): Wind Tunnel Experiment for Flow and Dispersion around a Cubic Building Model", None),
    "J": ("AIJ UWE Benchmark Dataset – Case J (112CT): Wind Tunnel Experiment for Flow and Dispersion Around a 1:1:2 Shape Building Model under Non-isothermal Conditions", None),
    "K": ("AIJ UWE Benchmark Dataset – Case K (ArraysC): Wind and Concentration Measurements in Cube Arrays with Point-source Dispersion", None),
    "L": ("AIJ UWE Benchmark Dataset – Case L (ArraysCT): Wind Tunnel Experiment for Flow and Dispersion around Cube Arrays with a Line-source under Non-isothermal Conditions", None),
    "M": ("AIJ UWE Benchmark Dataset – Case M (TPU): Wind Tunnel Experiment and Field Observation for Flow and Dispersion within TPU Campus", None),
}


# ----------------------------------------------------------------------------- addresses

def pinned_url(version):
    """The index of one release's frozen API: the address the API is cited by. GitHub Pages answers 404 for the folder
    itself (there is no index document), so the address names the file."""
    return f"{SITE}/api/{version}/index.json"


def tag_url(version):
    return f"{REPO_URL}/releases/tag/v{version}"


def doi_url(doi):
    return f"https://doi.org/{doi}"


# ----------------------------------------------------------------------------- building blocks

def _apa_names(pairs):
    """[(family, initials)] -> 'A, B., C, D., & E, F.' (APA 7: ampersand before the last author)."""
    names = [f"{family}, {initials}" for family, initials in pairs]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + ", & " + names[-1]


def _tex(text):
    """Text for a BibTeX string: the characters TeX reads as commands escaped, the en dash as TeX writes it."""
    for old, new in (("–", "--"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")):
        text = text.replace(old, new)
    return text


def _bibtex(kind, key, fields):
    """One entry. Every value is quoted, with braces only where a name or title must stay whole: a value never starts
    with a double brace, which Jekyll would read as Liquid in a page."""
    for name, value in fields:
        if '"' in value or not value.strip():
            raise ValueError(f"BibTeX field {name} of {key} is empty or holds a double quote: {value!r}")
    width = max(len(name) for name, _ in fields)
    body = ",\n".join(f'  {name.ljust(width)} = "{value}"' for name, value in fields)
    return f"@{kind}{{{key},\n{body}\n}}"


def _year(date):
    return int(date[:4])


# ----------------------------------------------------------------------------- the API

def api_apa(rel):
    where = doi_url(API_DOI) if API_DOI else pinned_url(rel.version)
    names = _apa_names([(family, _initials(given)) for family, given in API_AUTHORS])
    return f"{names} ({_year(rel.date)}). {TITLE} (Version {rel.version}) [Data set]. {ORG}. {where}"


def api_bibtex(rel):
    fields = [("author", " and ".join(f"{family}, {given}" for family, given in API_AUTHORS)), ("title", "{" + _tex(TITLE) + "}"), ("year", str(_year(rel.date))),
              ("version", rel.version), ("publisher", ORG)]
    if API_DOI:
        fields.append(("doi", API_DOI))
    fields += [("url", pinned_url(rel.version)),
               ("note", f"Data set; data version {rel.data_version[:12]}")]
    return _bibtex("misc", "aijuwe_api_" + rel.version.replace(".", "_"), fields)


def api_csl(rel):
    y, m, d = (int(x) for x in rel.date.split("-"))
    item = {"id": "aijuwe-api-" + rel.version, "type": "dataset", "title": TITLE,
            "author": [{"family": family, "given": given} for family, given in API_AUTHORS],
            "issued": {"date-parts": [[y, m, d]]}, "version": rel.version, "publisher": ORG, "URL": pinned_url(rel.version),
            "note": f"Data version {rel.data_version[:12]}"}
    if API_DOI:
        item["DOI"] = API_DOI
    return item


def api(rel):
    """cite.api of index.json."""
    return {"title": TITLE, "version": rel.version, "url": pinned_url(rel.version), "release_url": tag_url(rel.version),
            "doi": API_DOI, "apa": api_apa(rel), "bibtex": api_bibtex(rel), "csl_json": api_csl(rel)}


# ----------------------------------------------------------------------------- the data paper

def paper_apa():
    p = PAPER
    return (f"{_apa_names(p['authors'])} ({p['year']}). {p['title']}. {p['journal']}, {p['volume']}({p['issue']}), "
            f"{p['pages']}. {doi_url(p['doi'])}")


def paper_bibtex():
    p = PAPER
    return _bibtex("article", f"kikumoto{p['year']}", [
        ("author", " and ".join(f"{family}, {initials}" for family, initials in p["authors"])),
        ("title", "{" + _tex(p["title"]) + "}"), ("journal", p["journal"]), ("year", str(p["year"])),
        ("volume", str(p["volume"])), ("number", str(p["issue"])), ("pages", p["pages"]), ("doi", p["doi"])])


def guidelines_apa():
    g = GUIDELINES
    return f"{_apa_names(g['authors'])} ({g['year']}). {g['title']}. {g['journal']}, {g['volume']}, {g['pages']}. {doi_url(g['doi'])}"


# ----------------------------------------------------------------------------- one case

def case_people(meta):
    """[(family, given)] of the persons a case's record names: its data collectors, then its editors, as the Zenodo record
    lists them. An entry that is not a person's name ('K. Fujii, Y. Asami, Y. Iwasa et al. (the original 1978
    investigation; the readme names no data collectors)', Case F) is not an author of the record and is skipped."""
    out = []
    for entry in meta["people"]["data_collectors"] + meta["people"]["editors_distributors"]:
        name = re.split(r"\s*\(", entry, maxsplit=1)[0].strip()
        parts = name.split()
        if "et al" in name or "," in name or len(parts) < 2:
            continue
        person = (parts[-1], " ".join(parts[:-1]))
        if person not in out:
            out.append(person)
    return out


def _initials(given):
    return " ".join(p[0] + "." for p in given.split())


def _record(cid, meta):
    if cid not in ZENODO:
        raise KeyError(f"scripts/citation.py ZENODO has no record for Case {cid}")
    if not meta.get("doi"):
        raise KeyError(f"Case {cid} has no DOI to cite")
    people = case_people(meta)
    if not people:
        raise KeyError(f"Case {cid} names no person to cite as an author")
    return ZENODO[cid][0], ZENODO[cid][1], people


def case_apa(cid, meta):
    title, _, people = _record(cid, meta)
    return (f"{_apa_names([(f, _initials(g)) for f, g in people])} ({ZENODO_YEAR}). {title} [Data set]. Zenodo. "
            f"{doi_url(meta['doi'])}")


def case_bibtex(cid, meta):
    title, _, people = _record(cid, meta)
    return _bibtex("misc", f"aijuwe_case_{cid.lower()}", [
        ("author", " and ".join(f"{f}, {g}" for f, g in people)), ("title", "{" + _tex(title) + "}"),
        ("year", str(ZENODO_YEAR)), ("publisher", "Zenodo"), ("doi", meta["doi"]), ("url", doi_url(meta["doi"])),
        ("note", "Data set")])


def case(cid, meta):
    """citation of cases/{id}.json."""
    return {"apa": case_apa(cid, meta), "bibtex": case_bibtex(cid, meta)}


# ----------------------------------------------------------------------------- Markdown

def _fenced(label, lang, text):
    return [f"**{label}**", "", "```" + lang, text, "```", ""]


def site_include(rel):
    """docs/_includes/cite.md: the Cite section of the About page."""
    L = ["<!-- Generated by scripts/build_api.py from scripts/citation.py. -->", "", "### This API", ""]
    L += _fenced("APA", "text", api_apa(rel)) + _fenced("BibTeX", "bibtex", api_bibtex(rel))
    L += ["### Data paper", ""] + _fenced("APA", "text", paper_apa()) + _fenced("BibTeX", "bibtex", paper_bibtex())
    L += ["### AIJ guidelines", ""] + _fenced("APA", "text", guidelines_apa())
    L += ["### A single case", "", "Each case's Data page has its own citation; see [Cases]({{ '/cases/' | relative_url }})."]
    return "\n".join(L) + "\n"


def case_section(cid, meta):
    """The Cite section at the end of a case's Data page: lines."""
    c = case(cid, meta)
    return (["### Cite", ""] + _fenced("APA", "text", c["apa"]) + _fenced("BibTeX", "bibtex", c["bibtex"])
            + ["API: see [About]({{ '/about/#cite' | relative_url }})."])


README_CITE = re.compile(r"<!--cite-->\n.*?\n<!--/cite-->", re.S)


def readme_block(rel):
    L = ["<!--cite-->", ""]
    L += _fenced("API, APA", "text", api_apa(rel)) + _fenced("API, BibTeX", "bibtex", api_bibtex(rel))
    L += [f"Data paper: Kikumoto et al. ({PAPER['year']}), [doi:{PAPER['doi']}]({doi_url(PAPER['doi'])}).",
          f"AIJ guidelines: Tominaga et al. ({GUIDELINES['year']}), [doi:{GUIDELINES['doi']}]({doi_url(GUIDELINES['doi'])}).", "",
          "Cases: each case's dataset DOI is on its Data page and in `/api/cases/{id}.json`.", "", "<!--/cite-->"]
    return "\n".join(L)


def readme_with_cite(text, rel):
    if not README_CITE.search(text):
        raise ValueError("README.md has no <!--cite--> ... <!--/cite--> block")
    return README_CITE.sub(lambda m: readme_block(rel), text, count=1)


# ----------------------------------------------------------------------------- CITATION.cff and .zenodo.json

def _y(value):
    """A YAML scalar: JSON strings are YAML double-quoted strings."""
    return json.dumps(value, ensure_ascii=False)


def _cff_person(family, given):
    return [f"      - family-names: {_y(family)}", f"        given-names: {_y(given)}"]


def _cff_article(p):
    L = ["  - type: article", f"    title: {_y(p['title'])}", "    authors:"]
    for family, given in p["authors"]:
        L += _cff_person(family, given)
    L += [f"    journal: {_y(p['journal'])}", f"    volume: {p['volume']}"]
    if "issue" in p:
        L.append(f"    issue: {p['issue']}")
    if "-" in p["pages"]:
        start, end = p["pages"].split("-")
        L += [f"    start: {start}", f"    end: {end}"]
    else:
        L.append(f"    start: {_y(p['pages'])}")
    return L + [f"    year: {p['year']}", f"    doi: {_y(p['doi'])}"]


def cff(rel, cases):
    """CITATION.cff. GitHub's "Cite this repository" cites the dataset it describes (the API of this release); the data
    paper, the guidelines and one Zenodo dataset per case are its references. `version` and `date-released` stay at
    the left margin, where scripts/release.py check reads them."""
    L = ["# Generated by scripts/build_api.py from scripts/citation.py; GitHub's \"Cite this repository\" reads this file.",
         "cff-version: 1.2.0",
         'message: "If you use this dataset, please cite it using the metadata from this file."',
         "type: dataset",
         f"title: {_y(TITLE)}",
         f"version: {_y(rel.version)}",
         f"date-released: {_y(rel.date)}"]
    if API_DOI:
        L.append(f"doi: {_y(API_DOI)}")
    L += ["authors:"]
    for family, given in API_AUTHORS:
        L += _cff_person(family, given)
    L += [f"repository-code: {_y(REPO_URL)}",
          f"url: {_y(pinned_url(rel.version))}",
          f"license: {LICENSE}",
          f"abstract: {_y(ABSTRACT)}",
          "keywords:"] + [f"  - {k}" for k in KEYWORDS]
    L += ["references:"] + _cff_article(PAPER) + _cff_article(GUIDELINES)
    for cid in sorted(cases):
        title, date, people = _record(cid, cases[cid])
        L += ["  - type: data", f"    title: {_y(title)}", "    authors:"]
        for family, given in people:
            L += _cff_person(family, given)
        L += ["    publisher:", '      name: "Zenodo"', f"    year: {ZENODO_YEAR}"]
        if date:
            L.append(f"    date-released: {date}")
        L += [f"    doi: {_y(cases[cid]['doi'])}", f"    license: {LICENSE}"]
    return "\n".join(L) + "\n"


def zenodo_json(cases):
    """.zenodo.json: the metadata Zenodo's GitHub integration puts on the record it makes of a release. The version is
    the release tag's, which Zenodo takes itself."""
    d = {
        "title": TITLE,
        "description": ABSTRACT,
        "upload_type": "dataset",
        "creators": [{"name": f"{family}, {given}", "affiliation": ORG} for family, given in API_AUTHORS],
        "license": LICENSE.lower(),
        "keywords": KEYWORDS,
        "access_right": "open",
        "related_identifiers": [{"relation": "isDescribedBy", "identifier": PAPER["doi"], "scheme": "doi"}]
        + [{"relation": "isDerivedFrom", "identifier": cases[c]["doi"], "scheme": "doi"} for c in sorted(cases)],
    }
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"
