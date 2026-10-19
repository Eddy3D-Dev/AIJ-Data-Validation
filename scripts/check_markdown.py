#!/usr/bin/env python3
"""Check that this repository's Markdown renders the same on GitHub and in the Jekyll site (kramdown).

    python scripts/check_markdown.py             # every Markdown file the repository publishes (see PATTERNS)
    python scripts/check_markdown.py FILE...     # just these
    python scripts/check_markdown.py --self-test # the rules against small good and bad examples

Standard library only. build_all.sh runs it after the generated pages are written, so the pages and the includes
the build produces are checked, not only the hand-written files. It exits 1 on any finding, which CI turns into a
red build.

The two renderers disagree in small ways, and a page that reads well in one can break in the other. Each rule is
one such disagreement, or a mistake neither renderer forgives:

  list-start       a list item directly under a paragraph line (a blank line must come first)
  block-start      a table, heading, code fence or quote directly under a paragraph line
  table-end        a text line directly under a table (GitHub makes it another row)
  nested-list      a nested item indented less than its parent's text (a 2-space child of "1. x" is not a child)
  table-columns    a table row with another number of cells than its header
  table-code-pipe  a pipe inside a code span in a table row (GitHub splits the cell, kramdown does not)
  pipe-line        a block that starts with a pipe (kramdown turns it into a table)
  pipe-text        a paragraph or list item whose first line holds an unescaped pipe (kramdown turns it into a table)
  html-markdown    Markdown inside a block of HTML (kramdown prints it raw unless the tag says markdown="1";
                   GitHub needs a blank line between the tag and the Markdown)
  fence            a code fence that is never closed
  setext           a text line directly above --- or === (it becomes a heading, not a rule)
  bare-url         https://... in running text (GitHub links it, kramdown does not)
  heading          "#Title" without the space GitHub requires
  ial              a kramdown {: ...} line with a blank line on both sides (it attaches to nothing)
  link             a relative link or image whose file, page or heading does not exist
  front-matter     docs pages: an unquoted value holding ": " (a YAML error), no title, a parent that is no page
  liquid           docs pages: a Liquid tag this checker cannot follow, or an include not set off by blank lines
  math-form        a formula between $$ ... $$ that GitHub or kramdown would read differently: a * ~ | < > & or ` in it, a
                   backslash before punctuation (GitHub drops it), a space inside the dollar signs, a Liquid delimiter
  math-place       a formula where GitHub reads none: after a letter, a quote, a bracket, a slash or a code span, before a
                   letter, a digit or an underscore, in a heading, a link text, a <summary> or a block of raw HTML
  math-open        a $$ that closes nothing, or a display formula that is never closed
  stray-dollar     a single $ in running text (GitHub may pair it with another and read math)
  plain-math       a symbol or formula written as plain text (U_H, c0, c*, |U|, sqrt(...)); scripts/mathtext.py writes the LaTeX
  nomenclature     a table of scores without the scores' nomenclature under it, a table of symbols without the nomenclature
                   (scripts/nomenclature.py): an include in docs pages, a <!--nomenclature ...--> block elsewhere

Files under docs/ are Jekyll pages (kramdown with GFM input, as GitHub Pages builds them); every other file is
rendered by GitHub alone, so only the rules that concern GitHub apply to it.
"""
from __future__ import annotations

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mathtext as MT  # noqa: E402
import nomenclature as N  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")

# What the repository publishes as Markdown. raw/ holds the collectors' files exactly as published: not ours to edit.
PATTERNS = ["README.md", "CHANGELOG.md", "clean/*.md", "papers/*.md", "validation/*.md", "docs/*.md", "docs/**/*.md"]

BLOCK_TAGS = ("address article aside blockquote caption center details dialog div dl dt dd fieldset figcaption figure "
              "footer form h1 h2 h3 h4 h5 h6 header iframe li main nav noscript ol p pre section summary table tbody "
              "td tfoot th thead tr ul script style").split()
OPEN_TAG = re.compile(r"^\s{0,3}<(" + "|".join(BLOCK_TAGS) + r")\b([^>]*)>", re.I)
CLOSE_TAG = re.compile(r"^\s{0,3}</(" + "|".join(BLOCK_TAGS) + r")\s*>", re.I)
MARKDOWN_ATTR = re.compile(r"""markdown\s*=\s*["']?(1|block|span)""", re.I)
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])(\s+)\S")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
TABLE_DELIM = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
IAL = re.compile(r"^\s*\{:[^}]*\}\s*$")
RULE = re.compile(r"^\s{0,3}(-{3,}|={3,})\s*$")
LIQUID_URL = re.compile(r"\{\{\s*'([^']*)'\s*\|\s*relative_url\s*\}\}")
LIQUID_INCLUDE = re.compile(r"^\s*\{%-?\s*include\s+([^\s%]+)((?:\s+[\w-]+=(?:\"[^\"]*\"|'[^']*'|[^\s%]+))*)\s*-?%\}\s*$")
MD_IN_HTML = [(re.compile(p), what) for p, what in (
    (r"\*\*[^*\s][^*]*\*\*", "**bold**"), (r"(?<![\w*])\*[^*\s][^*]*\*(?![\w*])", "*emphasis*"),
    (r"`[^`]+`", "`code`"), (r"!?\[[^\]\n]*\]\([^)\n]+\)", "[link](url)"), (r"^\s*#{1,6}\s+\S", "# heading"),
    (r"^\s*[-*+]\s+\S", "- list item"), (r"^\s*\d+[.)]\s+\S", "1. list item"), (r"^\s*\|.*\|\s*$", "| table |"))]
URL = re.compile(r"https?://[^\s<>)\]]+")
CODE_SPAN = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)")
TABLE_CODE_PIPE = ("table-code-pipe: a pipe inside a code span in a table row splits the cell on GitHub, and "
                   "kramdown prints an escaped one with its backslash; write <code>x&#124;y</code> or avoid the pipe")
HTML_FIX = 'kramdown prints it raw unless the tag says markdown="1", and GitHub renders it only after a blank line'
DROP = -1      # the line number of a line that comes from an include: its own file reports its problems


def mask_code(line):
    """The line with every inline code span blanked out (same length), so its content is never read as Markdown."""
    return re.sub(r"(`+)(?:(?!\1).)+?\1", lambda m: " " * len(m.group(0)), line)


def split_cells(row):
    """The cells of a table row: split on pipes that are neither escaped nor inside a code span."""
    row = row.strip()
    cells, cur, i, tick = [], "", 0, False
    while i < len(row):
        ch = row[i]
        if ch == "\\" and i + 1 < len(row):
            cur += row[i:i + 2]
            i += 2
            continue
        tick ^= ch == "`"
        if ch == "|" and not tick:
            cells.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    cells.append(cur)
    if row.startswith("|"):
        cells = cells[1:]
    if row.endswith("|") and not row.endswith("\\|") and cells:
        cells = cells[:-1]
    return cells


def heading_id(text):
    """The id kramdown (GFM input) and GitHub give a heading: lower case, only letters, digits, hyphens and
    underscores, spaces as hyphens."""
    text = re.sub(r"<[^>]+>|\{:[^}]*\}|[`*]", "", text.strip()).strip()
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def parse_front_matter(lines):
    """(front matter {key: value as written} or None, lines it covers, [(line, message)])."""
    if not lines or lines[0].strip() != "---":
        return None, 0, []
    errors, fm = [], {}
    for n, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fm, n, errors
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if m:
            key, val = m.groups()
            fm[key] = val
            if val and val[0] not in "\"'[{|>&*!" and (": " in val or " #" in val or val.endswith(":")):
                errors.append((n, f"front-matter: the unquoted value of '{key}' holds ': ' or ' #' (a YAML error); quote it"))
    return fm, len(lines), errors + [(1, "front-matter: no closing ---")]


class Site:
    """The docs pages and what they publish, to check links written as {{ '/path/' | relative_url }}."""

    def __init__(self):
        self.pages = {}       # url -> {"ids": set of heading ids, "path": file}
        self.titles = set()
        for path in sorted(glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True)):
            rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
            if rel.startswith(("_includes/", "api/")):
                continue
            with open(path, encoding="utf-8") as f:
                lines = f.read().split("\n")
            fm, n, _ = parse_front_matter(lines)
            if fm is None:
                continue
            url = fm.get("permalink") or "/" + re.sub(r"(^|/)index$", "", rel[:-3])
            url = url if url.endswith("/") else url + "/"
            ids, seen = set(), {}
            for line in lines[n:]:
                if HEADING.match(line):
                    base = heading_id(re.sub(r"^\s*#+\s*", "", line))
                    ids.add(base if not seen.get(base) else f"{base}-{seen[base]}")
                    seen[base] = seen.get(base, 0) + 1
                ids.update(re.findall(r'\bid="([^"]+)"', line))
            self.pages[url] = {"ids": ids, "path": rel}
            self.titles.add(fm.get("title", "").strip("\"'"))
            for old in re.findall(r"^\s*-\s*(/\S+)\s*$", "\n".join(lines[:n]), re.M):      # redirect_from
                self.pages.setdefault(old if old.endswith("/") else old + "/", {"ids": set(), "path": rel})

    def resolve(self, target):
        """None if {{ target | relative_url }}, with an optional #fragment, exists; else why not."""
        path, _, frag = target.partition("#")
        path = path.split("?")[0]
        if path.startswith(("/api/", "/assets/")) or path == "/llms.txt":
            return None if os.path.exists(os.path.join(DOCS, path.lstrip("/"))) else f"{path} is not a file under docs/"
        page = self.pages.get(path if path.endswith("/") else path + "/")
        if page is None:
            return f"{path} is not a page of this site"
        return f"{path} has no heading or id '{frag}'" if frag and frag not in page["ids"] else None


def expand_includes(lines, errors, base_dir):
    """[(line number, text)] with each {% include x.md %} line replaced by the included file's lines (numbered DROP)."""
    out = []
    for n, line in enumerate(lines, start=1):
        m = LIQUID_INCLUDE.match(line)
        if not m:
            out.append((n, line))
            continue
        name = m.group(1)
        path = os.path.join(base_dir, "_includes", name)
        if not os.path.isfile(path):
            errors.append((n, f"liquid: include {name} does not exist"))
        elif name in N.INCLUDES.values():
            if (out and out[-1][1].strip()) or (n < len(lines) and lines[n].strip()):
                errors.append((n, f"liquid: {{% include {name} %}} needs a blank line before and after it"))
            out.append((n, "<!--nomenclature-->"))        # the include is checked as a file of its own
        elif not name.endswith(".md"):
            out.append((n, ""))                      # an HTML include (version label, JSON-LD, a figure): no Markdown in it
        else:
            if (out and out[-1][1].strip()) or (n < len(lines) and lines[n].strip()):
                errors.append((n, f"liquid: {{% include {name} %}} needs a blank line before and after it"))
            with open(path, encoding="utf-8") as f:
                out += [(DROP, x) for x in f.read().rstrip("\n").split("\n")]
    return out


def md_in_html(text):
    """What Markdown syntax the text of an HTML block holds, or None."""
    inner = re.sub(r"<[^>]+>", "", mask_code(text))
    if not inner.strip():
        return None
    return next((what for pat, what in MD_IN_HTML if pat.search(inner)), None)


def check_text(text, path="<text>", jekyll=False, site=None, base_dir=DOCS):
    """[(line, message)] for one file's text. `jekyll` selects the docs-page rules."""
    errors, lines = [], text.split("\n")
    if jekyll:
        fm, n, errs = parse_front_matter(lines)
        errors += errs
        page = fm is not None and "_includes" not in path.replace(os.sep, "/").split("/")
        if page and site is not None:
            if not fm.get("title"):
                errors.append((1, "front-matter: no title (the page would be missing from the navigation)"))
            for key in ("parent", "grand_parent"):
                value = fm.get(key, "").strip("\"'")
                if value and value not in site.titles:
                    errors.append((1, f"front-matter: {key} '{value}' is the title of no page"))
        body = [(first, x) for first, x in zip(range(n + 1, len(lines) + 1), lines[n:])]
        numbered = []
        for src, line in expand_includes([x for _, x in body], errors, base_dir):
            numbered.append((src + n if src != DROP else DROP, line))
    else:
        numbered = list(enumerate(lines, start=1))

    in_fence, fence_mark, fence_line = False, "", 0
    prev = "blank"            # blank, para, list, table, html, heading, ial, rule
    raw_close, raw_stack = None, []                       # inside a raw HTML block: its tag, and the open tags of it
    list_stack, table_cols, quote_prev = [], None, False
    i = 0
    while i < len(numbered):
        n, line = numbered[i]
        if jekyll:
            line = LIQUID_URL.sub(lambda m: "SITEURL:" + m.group(1), line)
            if re.search(r"\{%|\{\{", line):
                errors.append((n, "liquid: a Liquid tag this checker cannot follow: " + line.strip()[:60]))
                line = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", "", line)
        quoted = False
        qm = re.match(r"^\s{0,3}>\s?", line)
        if qm and not in_fence and raw_close is None:
            line, quoted = line[qm.end():], True
        if quoted != quote_prev and not in_fence:
            if quoted and prev == "para":
                errors.append((n, "block-start: a quote directly under a paragraph line"))
            prev, list_stack, table_cols = "blank", [], None
        quote_prev = quoted
        text_ = line.strip()
        i += 1

        if in_fence:                                           # inside a fenced code block
            f = FENCE.match(line)
            if f and f.group(1)[0] == fence_mark[0] and len(f.group(1)) >= len(fence_mark) and not text_.strip("`~"):
                in_fence, prev = False, "html"
            continue
        if raw_close is not None:                              # inside a block of raw HTML
            what = md_in_html(line)
            if what:
                errors.append((n, f'html-markdown: {what} inside a block of HTML ({HTML_FIX})'))
            for closing, name in re.findall(r"<(/?)(\w+)[^>]*>", line):
                if name.lower() == raw_close:
                    raw_stack.append(name) if not closing else (raw_stack.pop() if raw_stack else None)
            if (jekyll and not raw_stack) or (not jekyll and not text_):
                raw_close, prev = None, "html" if jekyll else "blank"
            continue
        f = FENCE.match(line)
        if f:
            if prev == "para":
                errors.append((n, "block-start: a code fence directly under a paragraph line"))
            in_fence, fence_mark, fence_line = True, f.group(1), n
            continue
        if not text_:
            prev, table_cols = "blank", None
            continue
        if re.match(r"^\s*<!--", line):                        # a comment is a block of HTML up to -->
            while "-->" not in numbered[i - 1][1] and i < len(numbered):
                i += 1
            prev = "html"
            continue
        if CLOSE_TAG.match(line):
            prev = "html"
            continue
        o = OPEN_TAG.match(line)
        if o and prev in ("blank", "html", "heading", "ial", "rule"):
            name, attrs = o.group(1).lower(), o.group(2)
            md = jekyll and bool(MARKDOWN_ATTR.search(attrs))       # GitHub ignores the attribute
            if re.search(r"</%s\s*>" % name, line[o.end():], re.I):          # opens and closes on this line
                what = None if md else md_in_html(line)
                if what:
                    errors.append((n, f'html-markdown: {what} inside a block of HTML ({HTML_FIX})'))
                prev = "html"
            elif jekyll and md:
                prev = "html"                                   # the content is Markdown: read on as Markdown
            else:
                raw_close = name
                raw_stack = [name] if jekyll else []
                what = md_in_html(line[o.end():])
                if what:
                    errors.append((n, f'html-markdown: {what} inside a block of HTML ({HTML_FIX})'))
                prev = "html"
            continue
        if IAL.match(line):
            following = numbered[i][1].strip() if i < len(numbered) else ""
            if prev in ("blank", "html", "ial") and not following and not text_.startswith("{:toc"):
                errors.append((n, "ial: a {: ...} line with a blank line on both sides attaches to nothing"))
            prev = "ial" if prev in ("blank", "html", "heading", "ial") else prev
            continue

        indent = len(line) - len(line.lstrip(" "))
        item = LIST_ITEM.match(line)
        following = re.sub(r"^\s{0,3}>\s?", "", numbered[i][1]) if i < len(numbered) and quoted else (numbered[i][1] if i < len(numbered) else "")
        if "|" in line and not item and TABLE_DELIM.match(LIQUID_URL.sub("U", following)):     # a table starts
            if prev == "para":
                errors.append((n, "block-start: a table directly under a paragraph line (a blank line must come first)"))
            header, delim = split_cells(line), split_cells(following)
            if len(header) != len(delim):
                errors.append((n, f"table-columns: the header has {len(header)} cells, its delimiter row {len(delim)}"))
            table_cols, prev = len(header), "table"
            i += 1
            continue
        if prev == "table":
            if "|" in line:                                    # another row
                cells = split_cells(line)
                if len(cells) != table_cols:
                    errors.append((n, f"table-columns: {len(cells)} cells in a table whose header has {table_cols}"))
                if any("|" in m.group(2) for m in CODE_SPAN.finditer(line)):
                    errors.append((n, TABLE_CODE_PIPE))
                continue
            if not (item or HEADING.match(line) or RULE.match(line)):
                errors.append((n, "table-end: a text line directly under a table (GitHub makes it a row); add a blank line"))
                prev = "para"
                continue
            prev = "blank"                                     # another block ends the table: read the line as that block
        if text_.startswith("|") and prev in ("blank", "heading", "html", "ial", "rule"):
            errors.append((n, "pipe-line: a block that starts with a pipe is a table to kramdown; start the line differently"))
        if (jekyll and not text_.startswith("|") and (item or prev in ("blank", "heading", "html", "ial", "rule"))
                and "|" in re.sub(r"\\\|", "", mask_code(line))):
            errors.append((n, "pipe-text: a block whose first line has a pipe is a table to kramdown; write \\| (GitHub shows a plain pipe)"))
        if HEADING.match(line):
            if prev == "para":
                errors.append((n, "block-start: a heading directly under a paragraph line"))
            prev, list_stack = "heading", []
            continue
        if re.match(r"^\s{0,3}#{1,6}[^#\s]", line):
            errors.append((n, "heading: '#Title' needs a space after the #"))
        if RULE.match(line):
            if prev == "para":
                errors.append((n, "setext: text directly above a ---/=== line turns into a heading; add a blank line"))
            prev, list_stack = "rule", []
            continue
        if item:
            width = len(item.group(1)) + len(item.group(2)) + len(item.group(3))
            if prev == "para":
                errors.append((n, "list-start: a list item directly under a paragraph line (a blank line must come first)"))
            while list_stack and list_stack[-1][0] > indent:
                list_stack.pop()
            if list_stack and list_stack[-1][0] < indent < list_stack[-1][1]:
                errors.append((n, f"nested-list: indented {indent}, less than the parent item's text at {list_stack[-1][1]}"))
            if list_stack and list_stack[-1][0] == indent:
                list_stack.pop()
            list_stack.append((indent, width))
            prev = "list"
            continue
        # plain text
        if prev == "list" or (prev == "blank" and list_stack and indent >= list_stack[-1][1]):
            prev = "list"                                      # a continuation of a list item
        else:
            prev, list_stack = "para", []

    if in_fence:
        errors.append((fence_line, "fence: this code fence is never closed"))
    errors += check_links_and_urls(numbered, path, jekyll, site)
    errors += check_math(numbered, jekyll)
    errors += check_plain_math(numbered)
    raw = list(zip(range(1, len(lines) + 1), lines))
    if jekyll:
        raw = raw[parse_front_matter(lines)[1]:]
    errors += check_legends(raw, path, jekyll)
    return sorted({e for e in errors if e[0] != DROP})


MATH = re.compile(r"\$\$(.+?)\$\$")
CODE_MASK = re.compile(r"(`+)(?:(?!\1).)+?\1")
SCORE_WORDS = re.compile(r"\bFAC2\b|\bFB\b|\b[Hh]it rate\b")
GENERATED_TABLES = {"validation-matrix.md": "scores", "cases-table.md": "full", "cases-frames.md": "full", "case-gallery.md": "full"}   # includes that hold a table
INCLUDE_KIND = {name: kind for kind, name in N.INCLUDES.items()}
NOT_PROSE = re.compile(r"^\s*(?:<|#|\{%|\{:|\||\[[^\]]+\]:)")


def prose_lines(numbered):
    """[(line number, text)] of the lines that are Markdown prose: not in a code fence, a comment, a block of HTML or a heading, no Liquid."""
    out, in_fence, in_comment = [], False, False
    for n, raw in numbered:
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or n == DROP:
            continue
        if "<!--" in raw or in_comment:
            in_comment = "-->" not in raw
            continue
        out.append((n, raw))
    return out


def check_math(numbered, jekyll):
    """The math rules: how a formula is written (math-form), where it stands (math-place), that it is closed (math-open, stray-dollar)."""
    errors, display = [], None
    for n, line in prose_lines(numbered):
        text = line.strip()
        if display is not None:
            if text == "$$":
                display = None
            elif N.RISKY.search(text):
                errors.append((n, "math-form: a display formula may not hold a * ~ | < > & or backtick, or a backslash before punctuation"))
            continue
        if text == "$$":
            display = n
            continue
        if "$" not in line:
            continue
        masked = CODE_MASK.sub(lambda mt: "\x01" * len(mt.group(0)), line)
        if text.startswith("<"):
            if "$$" in masked and not (jekyll and text.startswith('<figcaption markdown="span">')):
                errors.append((n, "math-place: a formula inside a block of raw HTML (GitHub shows it as written, and kramdown too)"))
            continue
        if text.startswith("#"):
            if "$" in masked:
                errors.append((n, "math-place: a formula in a heading (its anchor and the table of contents would hold LaTeX); write it as text"))
            continue
        if re.search(r"\[[^\]]*\$\$[^\]]*\]\(", masked):
            errors.append((n, "math-place: a formula inside a link text (GitHub reads none); put it beside the link"))
        for mt in MATH.finditer(masked):
            inner, a, b = mt.group(1), mt.start(), mt.end()
            if inner != inner.strip():
                errors.append((n, "math-form: a space inside the dollar signs (GitHub reads no math)"))
            elif N.RISKY.search(inner):
                errors.append((n, f"math-form: {inner[:50]!r} holds a * ~ | < > & or backtick, a backslash before punctuation or a Liquid delimiter; "
                                  "use \\ast, \\cdot, \\lvert, \\le, \\lbrace, \\thinspace"))
            before, after = masked[:a], masked[b:]
            if before and not (before[-1] in " \t(|" or before.endswith("**")):
                errors.append((n, f"math-place: a formula after {before[-1]!r} (GitHub reads math only after a space or a parenthesis): {inner[:30]!r}"))
            if after and re.match(r"[A-Za-z0-9_]", after[0]):
                errors.append((n, f"math-place: a formula before {after[0]!r} (GitHub reads no math before a letter, a digit or an underscore): {inner[:30]!r}"))
        rest = MATH.sub("", masked)
        if "$$" in rest:
            errors.append((n, "math-open: a $$ that closes nothing on its line"))
        elif "$" in rest:
            errors.append((n, "stray-dollar: a single $ in text (GitHub pairs two as math); write \\$ or reword"))
    if display is not None:
        errors.append((display, "math-open: this display formula ($$ on a line of its own) is never closed"))
    return errors


def check_plain_math(numbered):
    """Plain-text symbols and formulas that scripts/mathtext.py knows how to write as LaTeX (plain-math)."""
    errors, display = [], False
    for n, line in prose_lines(numbered):
        if line.strip() == "$$":
            display = not display
            continue
        if display or (NOT_PROSE.match(line) and not line.lstrip().startswith("|")):
            continue
        for col, what in MT.leftovers(line):
            errors.append((n, f"plain-math: {what} written as plain text; write it between $$ ... $$ (python scripts/mathtext.py --write FILE converts it)"))
    return errors


def check_legends(raw, path, jekyll):
    """Every table of scores has the scores' nomenclature under it, every other table that shows a symbol has the whole nomenclature, and a
    generated table that a page includes has the one that belongs to it. Docs pages write an include, the other files a block that the build fills."""
    rel = os.path.relpath(path, REPO).replace(os.sep, "/") if os.path.isabs(path) else path
    if rel.startswith("docs/_includes/") or rel.startswith("docs/api/"):
        return []
    errors, in_fence, in_block, i = [], False, False, 0

    def legend_after(k):
        while k < len(raw) and (not raw[k][1].strip() or IAL.match(raw[k][1])):
            k += 1
        text = raw[k][1].strip() if k < len(raw) else ""
        mt = re.match(r"^\{%-?\s*include\s+([\w.-]+)", text)
        if jekyll and mt and mt.group(1) in INCLUDE_KIND:
            return INCLUDE_KIND[mt.group(1)]
        mt = re.match(r"^<!--nomenclature (full|scores)-->$", text)
        return mt.group(1) if mt else None

    where = ("an include line {% include nomenclature-scores.md %} or {% include nomenclature.md %}" if jekyll
             else "a block <!--nomenclature scores--> or <!--nomenclature full-->, then <!--/nomenclature-->, which scripts/build_api.py fills")
    while i < len(raw):
        n, line = raw[i]
        if FENCE.match(line):
            in_fence = not in_fence
        mt = re.match(r"^<!--nomenclature (full|scores|metrics)-->$", line.strip())
        if mt:
            in_block = True
        elif line.strip() == "<!--/nomenclature-->":
            in_block = False
        if in_fence or in_block:
            i += 1
            continue
        inc = re.match(r"^\{%-?\s*include\s+([\w.-]+)", line.strip()) if jekyll else None
        if inc and inc.group(1) in GENERATED_TABLES:
            if legend_after(i + 1) != GENERATED_TABLES[inc.group(1)]:
                errors.append((n, f"nomenclature: the table of {inc.group(1)} needs the {GENERATED_TABLES[inc.group(1)]} nomenclature under it: {where}"))
        elif "|" in line and i + 1 < len(raw) and TABLE_DELIM.match(raw[i + 1][1]):
            j = i + 2
            while j < len(raw) and raw[j][1].strip() and "|" in raw[j][1]:
                j += 1
            text = "\n".join(x for _, x in raw[i:j])
            need = "scores" if SCORE_WORDS.search(text) else "full" if "$$" in text else None
            if need and legend_after(j) != need:
                errors.append((n, f"nomenclature: this table shows {'scores' if need == 'scores' else 'a symbol'}; the {need} nomenclature goes under it: {where}"))
            i = j
            continue
        i += 1
    return errors


def check_links_and_urls(numbered, path, jekyll, site):
    """Relative links that point nowhere, and URLs left bare in running text."""
    errors, in_fence, in_comment = [], False, False
    base = os.path.dirname(path) if os.path.isabs(path) else REPO
    for n, raw in numbered:
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "<!--" in raw or in_comment:
            in_comment = "-->" not in raw
            continue
        line = LIQUID_URL.sub(lambda m: "SITEURL:" + m.group(1), raw) if jekyll else raw
        masked = mask_code(line)
        targets = [m.group(1) for m in re.finditer(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)", masked)]
        targets += re.findall(r"""(?:href|src)=["']([^"']+)["']""", masked)
        targets += [m.group(1) for m in re.finditer(r"^\s*\[[^\]]+\]:\s*(\S+)", masked)]
        for t in targets:
            if not t or t.startswith(("http://", "https://", "mailto:", "#", "data:", "tel:")) or "{{" in t or "{%" in t:
                continue
            if t.startswith("SITEURL:"):
                msg = site.resolve(t[len("SITEURL:"):]) if site is not None else None
                if msg:
                    errors.append((n, f"link: {msg}"))
                continue
            target = t.split("#")[0].split("?")[0]
            full = os.path.join(REPO, target.lstrip("/")) if target.startswith("/") else os.path.normpath(os.path.join(base, target))
            if target and not os.path.exists(full):
                errors.append((n, f"link: {t} does not exist (relative to {os.path.relpath(base, REPO) or '.'})"))
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", masked)         # images first: a badge is an image inside a link
        text = re.sub(r"\[[^\]]*\]\([^)]*\)|<https?://[^>]+>|<[^>]+>|\[[^\]]+\]:\s*\S+", "", text)
        for m in URL.finditer(text):
            errors.append((n, f"bare-url: {m.group(0)[:60]} in running text; write [text](url) or <url>"))
    return errors


def files(args):
    if args:
        return [os.path.abspath(a) for a in args]
    found = set()
    for pattern in PATTERNS:
        found.update(glob.glob(os.path.join(REPO, pattern), recursive=True))
    return sorted(p for p in found if not p.startswith(os.path.join(DOCS, "api") + os.sep))


def self_test():
    github = [
        ("text\n\n- a\n- b\n", []),
        ("text\n- a\n", ["list-start"]),
        ("text\n| a | b |\n|---|---|\n| 1 | 2 |\n", ["block-start"]),
        ("| a | b |\n|---|---|\n| 1 | 2 |\n\ntext\n", []),
        ("| a | b |\n|---|---|\n| 1 | 2 |\ntext\n", ["table-end"]),
        ("| a | b |\n|---|---|\n| 1 | 2 |\n## Next\n", []),
        ("| a | b |\n|---|---|\n| 1 |\n", ["table-columns"]),
        ("| a | b |\n|---|---|\n| `x|y` | 2 |\n", ["table-code-pipe"]),
        ("```\ncode\n", ["fence"]),
        ("```\ncode\n```\n", []),
        ("Title\n---\n", ["setext"]),
        ("see https://example.org/x for more\n", ["bare-url"]),
        ("see [x](https://example.org/x) and <https://example.org/y> and `https://z.org`\n", []),
        ("1. one\n  - two\n", ["nested-list"]),
        ("1. one\n   - two\n", []),
        ("- a\n  - b\n- c\n", []),
        ("#Title\n", ["heading"]),
        ("a paragraph\n\n|d| is low\n", ["pipe-line"]),
        ("a paragraph\n|d| is low\n", []),
        ("<div>\n**bold**\n</div>\n", ["html-markdown"]),
        ("<div>\n\n**bold**\n\n</div>\n", []),                 # GitHub renders it when set off by blank lines
        ("see [x](nonexistent-file.md)\n", ["link"]),
        ("text\n> quote\n", ["block-start"]),
        ("the speed $$U_H$$ and $$k/U_H^2$$ and $$\\lvert x \\rvert$$.\n", []),
        ("a paragraph with $$c_0 = \\dfrac{q}{U_H H^2}$$ in it\n\n$$\nc_0 = \\dfrac{q}{U_H H^2}\n$$\n", []),
        ("the star $$c^*$$ here\n", ["math-form"]),
        ("the bar $$|x|$$ here\n", ["math-form"]),
        ("the braces $$\\{a\\}$$ here\n", ["math-form"]),
        ("a space $$ x $$ inside\n", ["math-form"]),
        ("after a letter a$$x$$ and \"$$x$$\" quoted and ($$x$$) and [$$x$$] and 2$$x$$\n", ["math-place"]),
        ("a formula $$x$$s and $$x$$2 before letters\n", ["math-place"]),
        ("[the link $$x$$](https://example.org)\n", ["math-place"]),
        ("## A heading with $$x$$\n", ["math-place"]),
        ("<td>a cell with $$x$$</td>\n", ["math-place"]),
        ("an open $$x pair\n", ["math-open"]),
        ("$$\nx\n", ["math-open"]),
        ("costs $5 and $6\n", ["stray-dollar"]),
        ("code `$$x$$` and `$BASE` stay\n", []),
        ("the speed U_H and c0 and U\\_H^2\n", ["plain-math"]),
        ("the speed `U_H` and [U_H](README.md) stay in code and links\n", []),
        ("| R | FAC2 |\n|---|---|\n| 1 | 2 |\n", ["nomenclature"]),
        ("| R | FAC2 |\n|---|---|\n| 1 | 2 |\n\n<!--nomenclature scores-->\n\n<!--/nomenclature-->\n", []),
        ("| Symbol |\n|---|\n| $$U_H$$ |\n", ["nomenclature"]),
        ("| Symbol |\n|---|\n| $$U_H$$ |\n\n<!--nomenclature full-->\n\n<!--/nomenclature-->\n", []),
        ("| Symbol |\n|---|\n| $$U_H$$ |\n\n<!--nomenclature scores-->\n\n<!--/nomenclature-->\n", ["nomenclature"]),
    ]
    jekyll = [
        ("<div>\n**bold**\n</div>\n", ["html-markdown"]),
        ('<div markdown="1">\n**bold**\n</div>\n', []),
        ('<details markdown="block">\n  <summary>s</summary>\n\n- a\n- b\n\n</details>\n', []),
        ('<details open markdown="block">\n  <summary>\n    Contents\n  </summary>\n  {: .text-delta }\n1. TOC\n{:toc}\n</details>\n', []),
        ('<figure class="f">\n<img src="README.md" alt="y">\n<figcaption><strong>F.</strong> c</figcaption>\n</figure>\n', []),
        ("---\ntitle: a: b\n---\ntext\n", ["front-matter"]),
        ('---\ntitle: "a: b"\n---\ntext\n', []),
        ("text\n\n{: .note }\ntext\n", []),
        ("text\n\n{: .note }\n\ntext\n", ["ial"]),
        ("text\n\n> a\n>\n> - x\n> - y\n", []),
        ("text\n\n> a\n> - x\n", ["list-start"]),
        ("text\n\n- Split-fibre |d|: FB +0.07\n", ["pipe-text"]),
        ("text\n\n> speed, not |mean velocity vector|.\n", ["pipe-text"]),
        ("text\n\n- Split-fibre \\|d\\|: FB +0.07\n- the code `a|b` stays\n", []),
        ("text\n\nfirst line\nsecond |d| line\n", []),
        ("[x]({{ '/nowhere/' | relative_url }})\n", []),     # no Site given: the link rule needs the site's pages
        ('text\n\n{% include figure.html name="x.png" alt="a | b" caption="<strong>F.</strong> c" %}\n\ntext\n', []),   # an HTML include with parameters
        ('text\n\n{% include nowhere.html name="x.png" %}\n\ntext\n', ["liquid"]),
        ('<figure class="f">\n<figcaption markdown="span">caption $$U_H$$</figcaption>\n</figure>\n', []),
        ('<figure class="f">\n<figcaption>caption $$U_H$$</figcaption>\n</figure>\n', ["math-place"]),
        ("| R | FAC2 |\n|---|---|\n| 1 | 2 |\n\n{% include nomenclature-scores.md %}\n\ntext\n", []),
        ("| R | FAC2 |\n|---|---|\n| 1 | 2 |\n{: .scores }\n\n{% include nomenclature-scores.md %}\n\ntext\n", []),
        ("| R | FAC2 |\n|---|---|\n| 1 | 2 |\n\ntext\n", ["nomenclature"]),
        ("| Symbol |\n|---|\n| $$U_H$$ |\n\n{% include nomenclature.md %}\n\ntext\n", []),
        ("text\n\n{% include validation-matrix.md %}\n\ntext\n", ["nomenclature"]),
        ("text\n\n{% include validation-matrix.md %}\n\n{% include nomenclature-scores.md %}\n\ntext\n", []),
    ]
    for cases, is_jekyll in ((github, False), (jekyll, True)):
        for text, want in cases:
            got = sorted({m.split(":")[0] for _, m in check_text(text, "self-test.md", jekyll=is_jekyll)})
            assert got == sorted(want), (text, got, want)
    print("check_markdown self-test: OK")


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    site, problems = Site(), 0
    paths = files([a for a in argv if not a.startswith("-")])
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for n, msg in check_text(text, path, jekyll=path.startswith(DOCS + os.sep), site=site):
            print(f"{rel}:{n}: {msg}")
            problems += 1
    print(f"check_markdown: {len(paths)} files, {problems} finding(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
