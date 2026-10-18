#!/usr/bin/env python3
"""Check that every citation of this repository says the same thing, and that none is broken.

    python scripts/check_citation.py              # check this checkout
    python scripts/check_citation.py --self-test  # copy it, break the copy in several ways, require each to be caught

What is compared: cite.api of docs/api/index.json (the alias and the release's frozen copy), the citation of every
docs/api/cases/{id}.json, docs/_includes/cite.md, the <!--cite--> block of README.md, the Cite section of every case's
Data page, CITATION.cff and .zenodo.json.

  1. title, version, year and pinned address agree across all of them (read out of each file on its own);
  2. each file is what scripts/citation.py renders for the release the API names (a stale or hand-edited file differs);
  3. every BibTeX entry is brace- and quote-balanced and has the fields its type needs, none empty;
  4. no citation holds a placeholder: TBD, TODO, null, None, an empty field, 'doi:' followed by nothing.

build_api.py runs check() as part of its verification; build_all.sh runs this script after the build.
Standard library only (aijdata and citation are, too).
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aijdata as D  # noqa: E402
import citation as C  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APA_API = re.compile(r"^(?P<org>.+?)\. \((?P<year>\d{4})\)\. (?P<title>.+) \(Version (?P<version>[^)]+)\) \[Data set\]\. (?P<url>\S+)$")
FENCE = re.compile(r"```(\w+)\n(.*?)\n```", re.S)
ENTRY = re.compile(r"^@(\w+)\{([^,\s]+),\n(.*?)\n\}$", re.S | re.M)
FIELD = re.compile(r'^\s*(\w+)\s*=\s*"(.*)",?$', re.M)
REQUIRED = {"misc": ("author", "title", "year", "publisher"), "article": ("author", "title", "journal", "year", "volume", "number", "pages", "doi")}
PLACEHOLDER = re.compile(r"\bTBD\b|\bTODO\b|\bXXX\b|\bnull\b|\bNone\b|\bundefined\b|\bdoi:[ \t]*(?:$|[,;)\]}])|=\s*\"\s*\"|\(\s*\)|\[\s*\]|\{\s*\}", re.M)


def _read(root, rel):
    with io.open(os.path.join(root, rel), encoding="utf-8", newline="") as f:
        return f.read()


def bibtex_problems(label, text):
    """Why a run of BibTeX entries is not usable, or []."""
    out = []
    if text.count("{") != text.count("}"):
        out.append(f"{label}: {text.count('{')} opening and {text.count('}')} closing braces")
    if text.count('"') % 2:
        out.append(f"{label}: an unclosed double quote")
    entries = ENTRY.findall(text)
    if not entries or len(entries) != text.count("\n@") + text.startswith("@"):
        out.append(f"{label}: {len(entries)} well-formed entries for {text.count(chr(64))} '@'")
    for kind, key, body in entries:
        fields = dict(FIELD.findall(body))
        for name in REQUIRED.get(kind, ("author", "title")):
            if not fields.get(name, "").strip():
                out.append(f"{label}: entry {key} has no {name}")
        if kind == "misc" and not (fields.get("url") or fields.get("doi")):
            out.append(f"{label}: entry {key} has neither url nor doi")
    return out


def _facts_apa(source, apa, problems):
    m = APA_API.match(apa)
    if not m:
        problems.append(f"{source}: not an APA line of the form 'Author. (Year). Title (Version x) [Data set]. address'")
        return []
    return [(source, "APA title", m["title"]), (source, "APA version", m["version"]), (source, "APA year", m["year"])] + (
        [] if C.API_DOI else [(source, "APA address", m["url"])])    # with a DOI the line gives the DOI's address instead


def _facts_bibtex(source, bib):
    f = dict(FIELD.findall(bib))
    title = f.get("title", "")
    return [(source, "BibTeX title", title[1:-1] if title.startswith("{") and title.endswith("}") else title),
            (source, "BibTeX version", f.get("version")), (source, "BibTeX year", f.get("year")), (source, "BibTeX address", f.get("url"))]


def _cff_value(cff, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", cff, re.M)
    return json.loads(m.group(1)) if m else None


def check(root=REPO):
    """[problem] for the checkout at `root`."""
    problems, texts = [], {}

    def get(rel):
        try:
            texts[rel] = _read(root, rel)
        except OSError:
            problems.append(f"{rel} does not exist")
        return texts.get(rel)

    version_file = get("VERSION")
    index_text = get("docs/api/index.json")
    if version_file is None or index_text is None:
        return problems
    index = json.loads(index_text)
    rel = C.Release(index["versions"]["release"], index["release"]["date"], index["versions"]["data"])
    if version_file.strip() != rel.version:
        problems.append(f"VERSION is {version_file.strip()}, docs/api/index.json is release {rel.version}")
    expect = {"title": C.TITLE, "version": rel.version, "year": rel.date[:4], "address": C.pinned_url(rel.version)}

    facts, citations = [], []        # (source, name, value); (label, text) to scan
    trees = {"docs/api/index.json": index_text}
    own = f"docs/api/{rel.version}/index.json"
    if get(own) is not None:
        trees[own] = texts[own]
    for path, text in trees.items():
        cite = json.loads(text).get("cite", {}).get("api")
        if cite is None:
            problems.append(f"{path}: no cite.api")
            continue
        if cite != C.api(rel):
            problems.append(f"{path}: cite.api is not what scripts/citation.py renders for release {rel.version}")
        facts += [(path, "cite.api title", cite.get("title")), (path, "cite.api version", cite.get("version")),
                  (path, "cite.api address", cite.get("url")),
                  (path, "CSL-JSON year", str(cite.get("csl_json", {}).get("issued", {}).get("date-parts", [[None]])[0][0]))]
        facts += _facts_apa(path + " cite.api.apa", cite.get("apa", ""), problems) + _facts_bibtex(path + " cite.api.bibtex", cite.get("bibtex", ""))
        problems += bibtex_problems(path + " cite.api.bibtex", cite.get("bibtex", ""))
        citations += [(path + " cite.api." + k, cite.get(k) if isinstance(cite.get(k), str) else json.dumps(cite.get(k)))
                      for k in ("title", "apa", "bibtex", "csl_json")]

    for cid in sorted(D.CASES):
        path = f"docs/api/cases/{cid}.json"
        if get(path) is None:
            continue
        got = json.loads(texts[path]).get("citation")
        if got != C.case(cid, D.CASES[cid]):
            problems.append(f"{path}: citation is not what scripts/citation.py renders from the case's record")
        if got:
            problems += bibtex_problems(path + " citation.bibtex", got.get("bibtex", ""))
            citations += [(f"{path} citation.{k}", got.get(k, "")) for k in ("apa", "bibtex")]
        slug = D.CASES[cid]["slug"]
        page = get(f"docs/cases/{slug}/data.md")
        if page is not None and "\n".join(C.case_section(cid, D.CASES[cid])) not in page:
            problems.append(f"docs/cases/{slug}/data.md: its Cite section is not what scripts/citation.py renders")
        if page is not None:
            citations.append((f"docs/cases/{slug}/data.md", "\n".join(C.case_section(cid, D.CASES[cid]))))

    cite_md = get("docs/_includes/cite.md")
    readme = get("README.md")
    block = C.README_CITE.search(readme).group(0) if readme and C.README_CITE.search(readme) else None
    if readme is not None and block is None:
        problems.append("README.md has no <!--cite--> ... <!--/cite--> block")
    for label, text, exact in (("docs/_includes/cite.md", cite_md, cite_md == C.site_include(rel) if cite_md else None),
                               ("README.md cite block", block, readme == C.readme_with_cite(readme, rel) if block else None)):
        if text is None:
            continue
        if not exact:
            problems.append(f"{label} is not what scripts/citation.py renders for release {rel.version}")
        fences = FENCE.findall(text)
        apa = next((b for lang, b in fences if lang == "text"), "")
        bib = next((b for lang, b in fences if lang == "bibtex"), "")
        facts += _facts_apa(label + " APA", apa, problems) + _facts_bibtex(label + " BibTeX", bib)
        problems += bibtex_problems(label + " BibTeX", "\n".join(b for lang, b in fences if lang == "bibtex"))
        citations.append((label, text))

    cff = get("CITATION.cff")
    if cff is not None:
        if cff != C.cff(rel, D.CASES):
            problems.append(f"CITATION.cff is not what scripts/citation.py renders for release {rel.version}")
        facts += [("CITATION.cff", "title", _cff_value(cff, "title")), ("CITATION.cff", "version", _cff_value(cff, "version")),
                  ("CITATION.cff", "year", (_cff_value(cff, "date-released") or "")[:4]),
                  ("CITATION.cff", "address", _cff_value(cff, "url"))]
        if "preferred-citation" in cff:
            problems.append("CITATION.cff: preferred-citation would make GitHub cite the paper, not this dataset")
        citations.append(("CITATION.cff", cff))
    zenodo = get(".zenodo.json")
    if zenodo is not None:
        if zenodo != C.zenodo_json(D.CASES):
            problems.append(".zenodo.json is not what scripts/citation.py renders")
        facts.append((".zenodo.json", "title", json.loads(zenodo).get("title")))
        citations.append((".zenodo.json", zenodo))

    for source, name, value in facts:
        key = next((k for k in expect if name.lower().endswith(k)), None)
        if key and value != expect[key]:
            problems.append(f"{source}: {name} is {value!r}, expected {expect[key]!r}")
    for label, text in citations:
        for m in PLACEHOLDER.finditer(text):
            problems.append(f"{label}: placeholder or empty field {m.group(0)!r}")
    return problems


# ----------------------------------------------------------------------------- the negative control

def _sources(root):
    found = ["VERSION", "README.md", "CITATION.cff", ".zenodo.json", "docs/_includes/cite.md", "docs/api/index.json"]
    found += [os.path.relpath(p, root).replace(os.sep, "/") for pattern in ("docs/api/*/index.json", "docs/api/cases/*.json", "docs/cases/*/data.md")
              for p in glob.glob(os.path.join(root, pattern))]
    return sorted(set(found))


def self_test(root=REPO):
    """Copy the citation files, check the copy (it must pass), then break it one way at a time: each break must be caught."""
    with tempfile.TemporaryDirectory() as tmp:
        for rel in _sources(root):
            if os.path.isfile(os.path.join(root, rel)):
                os.makedirs(os.path.dirname(os.path.join(tmp, rel)) or tmp, exist_ok=True)
                shutil.copyfile(os.path.join(root, rel), os.path.join(tmp, rel))
        base = check(tmp)
        if base:
            print("check_citation self-test: the copy of this checkout already has problems:\n  " + "\n  ".join(base[:5]))
            return 1
        version = _read(tmp, "VERSION").strip()
        pinned = C.pinned_url(version)

        def edit(rel, fn):
            with io.open(os.path.join(tmp, rel), encoding="utf-8", newline="") as f:
                original = f.read()
            changed = fn(original)
            if changed == original:
                raise SystemExit(f"self-test mutation of {rel} changed nothing")
            with io.open(os.path.join(tmp, rel), "w", encoding="utf-8", newline="") as f:
                f.write(changed)
            return original

        def put_back(rel, original):
            with io.open(os.path.join(tmp, rel), "w", encoding="utf-8", newline="") as f:
                f.write(original)

        mutations = [
            ("the version in the README block", "README.md", lambda s: s.replace(f"api/{version}/", "api/9.9.9/", 1)),
            ("the version in CITATION.cff", "CITATION.cff", lambda s: s.replace(f'version: "{version}"', 'version: "9.9.9"', 1)),
            ("the pinned address in index.json", "docs/api/index.json", lambda s: s.replace(pinned, pinned.replace(version, "9.9.9"), 1)),
            ("the title in .zenodo.json", ".zenodo.json", lambda s: s.replace("Cases A-M", "Cases A-L", 1)),
            ("a closing brace of the About page's BibTeX", "docs/_includes/cite.md", lambda s: s.replace("}\n```", "\n```", 1)),
            ("an empty field in the About page's BibTeX", "docs/_includes/cite.md", lambda s: re.sub(r'publisher = "[^"]*"', 'publisher = ""', s, count=1)),
            ("a placeholder in the README block", "README.md", lambda s: s.replace("Data paper:", "Data paper: TBD", 1)),
            ("a case DOI in a Data page", "docs/cases/case-a/data.md", lambda s: s.replace("10.5281/zenodo.15050147", "10.5281/zenodo.0000000")),
        ]
        failed = 0
        for what, rel, fn in mutations:
            original = edit(rel, fn)
            found = check(tmp)
            put_back(rel, original)
            print(f"  {'caught' if found else 'MISSED'}: {what}" + (f" ({found[0][:90]})" if found else ""))
            failed += not found
        if check(tmp):
            print("check_citation self-test: the copy no longer passes after the mutations were undone")
            return 1
        print(f"check_citation self-test: {len(mutations) - failed} of {len(mutations)} faults caught")
        return 1 if failed else 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    problems = check()
    for p in problems:
        print("PROBLEM:", p)
    print("check_citation:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
