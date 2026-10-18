r"""Plain-text math -> LaTeX, for the text of the site: the symbols and formulas that the case data and the old pages wrote as `U_H^2`,
`C / c0, c0 = q / (U_ref L_ref^2)`, `uu, vv, ww` or `√(|U|²+2k)`.

    python scripts/mathtext.py --self-test        # the rules against examples
    python scripts/mathtext.py FILE...            # the conversion of hand-written Markdown FILEs as a diff; changes nothing
    python scripts/mathtext.py --write FILE...    # the same, written to the files

The served data keeps its plain strings (the API, clean/manifest.json and llms.txt are parsed by their consumers), so the generator converts
at the moment a string becomes a page (`to_markdown`, called by scripts/build_api.py), and the files written by hand were converted once
(`markdown`). scripts/check_markdown.py calls `leftovers` on every line, so a plain-text form that this module knows cannot come back.
Which formula becomes which LaTeX, and what a formula may contain, is in scripts/nomenclature.py.

The rules do not touch a bare letter in a sentence: `U`, `V`, `W`, `k` or `C` read as symbols only inside a formula (`U/U_H`), in a list of the
cleaned table's columns (`U, V, W and k`), as a whole table cell, or at the head of a score label ("V, sign flipped"). "Case C", "wind from W"
and "k-ε" are words. Standard library only.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nomenclature as N  # noqa: E402

B = r"(?<![\w\\\"“'‘])"          # not inside a word or an identifier, not a quoted name
E = r"(?![\w\"”])"
US, ST, BAR = r"\\?_", r"\\?\*", r"\\?\|"       # an underscore, an asterisk, a pipe: plain, or escaped for Markdown
SQ = r"(?:\^2|²)"
NUM = r"\d+(?:\.\d+)?"
MINUS = r"(?:−|\s-\s)"

# ----------------------------------------------------------------------------- atoms: one symbol each (regex -> LaTeX)

ATOMS = [      # scales and the other symbols that carry an index or a Greek letter
    (rf"U(?:{US})?H", "U_H"), (rf"U(?:{US})?R", "U_R"), (rf"H{US}R", "H_R"), (rf"Z(?:{US})?R", "Z_R"), (rf"U(?:{US})?b", "U_b"), (rf"U{US}D", "U_D"),
    (rf"U{US}ref", r"U_{\mathrm{ref}}"), (rf"L{US}ref", r"L_{\mathrm{ref}}"),
    (rf"([uvw]){US}rms", None), (rf"T{US}f", "T_f"), (rf"T{US}H", "T_H"), (rf"T{US}b", "T_b"), (rf"T{US}rms", r"T_{\mathrm{rms}}"), (rf"c{US}rms", r"c_{\mathrm{rms}}"),
    (rf"Re{US}H", r"\mathrm{Re_H}"), (rf"Re{US}D", r"\mathrm{Re_D}"), (rf"L{US}r", "L_r"), (rf"WD{US}R", r"\mathrm{WD_R}"),
    (r"c(?:0|₀)", "c_0"), (r"C0", "C_0"), (r"z(?:0|₀)", "z_0"),
]
ATOM = "(?:" + "|".join(f"(?:{rx})" for rx, _ in ATOMS) + ")"
SYMBOL = rf"(?:{BAR}U(?:{US}mean)?{BAR}|Vs|Ve|H|{ATOM}|[UVWkC])"                       # what may stand over a reference scale
DEN = rf"(?:{ATOM}|U\({NUM}\s?m\))"
COLUMN = (rf"(?:velocity{US}ratio{US}sd|velocity{US}ratio|concentration{US}ratio|k{US}ratio|c{US}rms|T{US}rms|uu|vv|ww|uv|uw|vw|uc|vc|wc|uT|vT|wT|Vs"
          rf"|c{ST}|θ|[UVWkCT])")
SEP = r"(?:,?\s+and\s+|,?\s+or\s+|,\s*)"


def atom(s):
    """The LaTeX of one atom as it is written (`U\\_H`, `UH`, `c₀`), or None."""
    for rx, tex in ATOMS:
        mt = re.fullmatch(rx, s)
        if mt:
            return tex or rf"{mt.group(1)}_{{\mathrm{{rms}}}}"
    return None


def column(s):
    s = s.replace("\\", "")
    return r"\theta" if s == "θ" else N.COLUMN_TEX["concentration_ratio" if s == "c*" else s]


def over(s):
    """The LaTeX of what stands over a scale: |U|, Vs, U, V, W, k, C, H or a scale."""
    t = atom(s)
    if t or s == "H":
        return t or s
    if s == "Ve":
        return "V_e"
    s = s.replace("\\", "")
    if s == "|U_mean|":
        return r"\lvert\mathbf{U_{\mathrm{mean}}}\rvert"
    return r"\lvert\mathbf{U}\rvert" if s == "|U|" else N.COLUMN_TEX[s]


def under(s):
    """The LaTeX of a denominator: an atom or U at a height."""
    t = atom(s.strip())
    if t:
        return t
    return rf"U({re.fullmatch(rf'U\(({NUM})\s?m\)', s.strip()).group(1)}\text{{ m}})"


def power(g):
    return "^2" if g else ""


# ----------------------------------------------------------------------------- the rules

RULES = []      # [(name, compiled regex, handler(match) -> ("m", LaTeX) | ("t", text) | ("mm", [(kind, text)...]) | None)]


def rule(name, rx):
    def deco(fn):
        RULES.append((name, re.compile(rx), fn))
        return fn
    return deco


GAS = r"(?:(?P<gas>[cC]gas|0\.05)\s*(?:·\s*)?)?"
Q_OVER = rf"q\s*/\s*\(\s*(?P<u>[uU](?:{US})?H|U(?:{US})?R|U{US}ref)\s+(?P<h>H{US}R|H|L{US}ref)\s*{SQ}\s*\)"


def q_over(g, display):
    gas = {None: "", "cgas": r"c_{\mathrm{gas}}\thinspace ", "Cgas": r"c_{\mathrm{gas}}\thinspace ", "0.05": r"0.05\thinspace "}[g.groupdict().get("gas")]
    u, h = atom(g["u"]) or "U_H", atom(g["h"]) or g["h"]
    return rf"\dfrac{{{gas}q}}{{{u} {h}^2}}" if display else rf"q/({u} {h}^2)"


@rule("c0-definition", rf"{B}(?P<lhs>[cC](?:0|₀)){E}\s*=\s*{GAS}{Q_OVER}")
def _c0_definition(mt):
    return "m", rf"{atom(mt['lhs'])} = " + q_over(mt, True)


@rule("q-over-scales", rf"{B}{GAS}{Q_OVER}")
def _q_over_scales(mt):
    gas = {None: "", "cgas": r"c_{\mathrm{gas}}\thinspace ", "Cgas": r"c_{\mathrm{gas}}\thinspace ", "0.05": r"0.05\thinspace "}[mt["gas"]]
    return "m", gas + q_over(mt, False)


@rule("release-rate", rf"{B}q(?=\s=\s[-−]?\d){E}")
def _release_rate(mt):
    return "m", "q"


@rule("cstar-model", rf"{B}c{ST}\s*=\s*c\s+(?P<u>U(?:{US})?H|U(?:{US})?R)\s+(?P<h>H{US}R|H)\s*{SQ}\s*/\s*Q{E}")
def _cstar_model(mt):
    return "m", rf"c^\ast = c\thinspace {atom(mt['u'])} {atom(mt['h']) or mt['h']}^2/Q"


@rule("model-concentration", rf"{B}c\s+(?P<u>U(?:{US})?H|U(?:{US})?R)\s+(?P<h>H{US}R|H)\s*{SQ}\s*/\s*Q{E}")
def _model_concentration(mt):
    return "m", rf"c\thinspace {atom(mt['u'])} {atom(mt['h']) or mt['h']}^2/Q"


@rule("reattachment", rf"{B}L{US}r\s*/\s*H{E}")
def _reattachment(mt):
    return "m", "L_r/H"


@rule("k-over-scale", rf"{B}k(?=\s(?:by|over)\s{ATOM}){E}")
def _k_over_scale(mt):
    return "m", "k"


@rule("cstar-ratio", rf"{B}c{ST}\s*=\s*C\s*/\s*c(?:0|₀){E}")
def _cstar_ratio(mt):
    return "m", r"c^\ast = C/c_0"


@rule("C-over-c0", rf"{B}C\s*/\s*c(?:0|₀){E}")
def _c_over_c0(mt):
    return "m", "C/c_0"


@rule("theta", rf"{B}θ\s*=\s*\(\s*T{US}f\s*{MINUS}\s*T\s*\)\s*/\s*\(\s*T{US}f\s*{MINUS}\s*T{US}H\s*\)")
def _theta(mt):
    return "m", r"\theta = (T_f - T)/(T_f - T_H)"


@rule("speed", rf"{B}(?:√|sqrt)\(\s*{BAR}U{BAR}\s*{SQ}\s*\+\s*2\s*k\s*\)(?:\s*/\s*(?P<den>{DEN}))?")
def _speed(mt):
    return "m", r"\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}" + (f"/{under(mt['den'])}" if mt["den"] else "")


@rule("ratio", rf"{B}(?P<num>{SYMBOL})\s*/\s*(?P<den>{DEN})(?P<exp>{SQ})?{E}")
def _ratio(mt):
    return "m", f"{over(mt['num'])}/{under(mt['den'])}{power(mt['exp'])}"


@rule("height-ratio", rf"{B}z\s*/\s*Z(?:{US})?R{E}")
def _height_ratio(mt):
    return "m", "z/Z_R"


@rule("components", rf"{B}U/V/W(?:/k)?{E}")
def _components(mt):
    return "m", mt.group(0)


@rule("magnitude", rf"{B}{BAR}U(?P<mean>{US}mean)?{BAR}")
def _magnitude(mt):
    return "m", r"\lvert\mathbf{U_{\mathrm{mean}}}\rvert" if mt["mean"] else r"\lvert\mathbf{U}\rvert"


@rule("U-at-height", rf"{B}U\((?P<h>{NUM})\s?m\)")
def _u_at_height(mt):
    return "m", rf"U({mt['h']}\text{{ m}})"


@rule("tolerances", rf"{B}(?:D\s=\s0\.25|W\s=\s0\.05(?:\sU{US}H)?){E}")
def _tolerances(mt):
    s = mt.group(0)
    if s.startswith("D"):
        return "m", rf"{N.REL} = 0.25"
    return "m", rf"{N.ABS} = 0.05" + (r"\thinspace U_H" if "U" in s else "")


@rule("temperature-difference", rf"{B}(?P<a>T{US}f|T{US}H|T{US}b)\s*{MINUS}\s*(?P<b>T{US}f|T{US}H|T{US}b|T){E}")
def _temperature_difference(mt):
    return "m", f"{atom(mt['a'])} - {atom(mt['b']) or 'T'}"


@rule("fluctuations", r"⟨?(?P<a>[uvwcθ])′(?P<b>[uvwcθ]|²)′?⟩?")
def _fluctuations(mt):
    a, b = (r"\theta" if x == "θ" else x for x in (mt["a"], mt["b"]))
    return "m", rf"\overline{{{a}'{'^2' if b == '²' else b + chr(39)}}}"


@rule("averages", r"⟨(?P<a>[uvwcθ])(?:_(?P<i>[A-Za-z]+))?⟩")
def _averages(mt):
    a = r"\theta" if mt["a"] == "θ" else mt["a"]
    i = mt["i"]
    return "m", rf"\langle {a}{('_' + i if len(i) == 1 else r'_{\mathrm{' + i + '}}') if i else ''}\rangle"


@rule("columns", rf"{B}(?P<list>{COLUMN}(?:{SEP}{COLUMN})+){E}")
def _columns(mt):
    items = re.split(f"({SEP})", mt["list"])
    names = items[::2]
    if len(names) < 3 and all(len(i) == 1 for i in names):
        return None
    return "mm", [("m", column(i)) if k % 2 == 0 else ("t", i) for k, i in enumerate(items)]


@rule("columns-spaced", rf"{B}(?P<list>{COLUMN}(?:\s{COLUMN}){{3,}}){E}")
def _columns_spaced(mt):
    items = re.split(r"(\s)", mt["list"])
    return "mm", [("m", column(i)) if k % 2 == 0 else ("t", i) for k, i in enumerate(items)]


@rule("case-quantity", r"(?<=[A-M] — )[UVWk]" + E)
def _case_quantity(mt):
    return "m", mt.group(0)


@rule("identifier", rf"{B}(?:velocity{US}ratio{US}sd|velocity{US}ratio|concentration{US}ratio|k{US}ratio){E}")
def _identifier(mt):
    return "c", mt.group(0).replace("\\", "")


@rule("atom", rf"{B}(?P<atom>{ATOM})(?P<exp>{SQ})?{E}")
def _atom(mt):
    return "m", atom(mt["atom"]) + power(mt["exp"])


@rule("bare", rf"{B}(?<!\bor )(?<!SW, )(?<!SE, )(?<!NW, )(?<!NE, )(?<!\+x, )(?<!/ )[UVWk](?![\w\"”])(?![-–]\s?(?:ε|ω|epsilon|omega))")
def _bare(mt):
    return "m", mt.group(0)


@rule("friction-velocity", rf"{B}u{ST}{E}")
def _friction_velocity(mt):
    return "m", r"u_\ast"


@rule("concentration-ratio", rf"{B}c{ST}(?![A-Za-z0-9_*])")
def _concentration_ratio(mt):
    return "m", r"c^\ast"


@rule("schmidt", rf"{B}Sct{E}")
def _schmidt(mt):
    return "m", r"\mathrm{Sc_t}"


@rule("scalar-speed", rf"{B}Vs{E}")
def _scalar_speed(mt):
    return "m", r"V_{\mathrm{s}}"


@rule("temperature", r"(?<![\w+−±⟨Δ′])θ(?![\w′])(?!\s\+\s180)")
def _temperature(mt):
    return "m", r"\theta"


@rule("von-karman", rf"(?:κ|{B}kappa{E})(?=\s=\s0\.41)")
def _von_karman(mt):
    return "m", r"\kappa"


@rule("kinematic-viscosity", rf"{B}U(?:{US})?H\sH\s/\snu{E}")
def _reynolds(mt):
    return "m", r"U_H H/\nu"


@rule("speed-of-components", r"√\(\s*U²\s*\+\s*V²\s*\+\s*W²\s*\)")
def _speed_of_components(mt):
    return "m", r"\sqrt{U^2+V^2+W^2}"


@rule("unit-powers", r"(?<![A-Za-z0-9_])(?P<unit>[ms])\s?\^(?P<n>[23])(?![0-9])|(?<![A-Za-z0-9_])m3(?=/s)")
def _unit_powers(mt):
    return "t", "m³" if mt["unit"] is None else mt["unit"] + {"2": "²", "3": "³"}[mt["n"]]


# ----------------------------------------------------------------------------- converting a piece of text

def allowed(before, after):
    """May a formula stand between these two pieces of text? GitHub reads `$$...$$` as math only after a space, a parenthesis or the start of a
    line (or inside **), and not before a letter, a digit or an underscore."""
    if before and not (before[-1] in " \t(" or before.endswith("**")):
        return False
    return not (after and re.match(r"[A-Za-z0-9_]", after[0]))


def segments(text, lead=False, before="", after=""):
    """[("t", plain text) | ("m", LaTeX) | ("c", a column name)] for a string of plain text. `lead`: the text opens a score label ("V, sign flipped", "k (resolved)"),
    so a symbol at its head is a symbol. `before` and `after` are the text that stands around it on the page: a formula that GitHub would not
    read there (see `allowed`) stays as it was written."""
    parts, pos = [], 0          # [(kind, content, source text)]
    if lead:
        mt = re.match(rf"(?P<s>{BAR}U{BAR}|Vs|[UVWk]|θ|c{ST})(?=,| \(|$)", text)
        if mt:
            s = mt["s"].replace("\\", "")
            tex = {"θ": r"\theta", "c*": N.COLUMN_TEX["concentration_ratio"], "|U|": r"\lvert\mathbf{U}\rvert"}.get(s) or N.COLUMN_TEX[s]
            parts.append(("m", tex, mt["s"]))
            pos = mt.end()
    while True:
        found = sorted(((mt.start(), -mt.end(), i, mt) for i, (_, rx, _) in enumerate(RULES) for mt in [rx.search(text, pos)] if mt),
                       key=lambda f: f[:3])
        chosen = None
        for _, _, i, mt in found:            # the leftmost match, the longest; a rule that declines leaves the place to the next
            res = RULES[i][2](mt)
            if res is not None:
                chosen = (mt, res)
                break
        if chosen is None:
            break
        mt, res = chosen
        parts.append(("t", text[pos:mt.start()], text[pos:mt.start()]))
        if res[0] == "mm":                   # a list: one formula per item, the source on the first
            parts += [(k, c, c if k == "t" else "") for k, c in res[1]]
            parts[-len(res[1])] = (res[1][0][0], res[1][0][1], mt.group(0))
        else:
            parts.append((res[0], res[1], mt.group(0)))
        pos = mt.end()
    parts.append(("t", text[pos:], text[pos:]))
    k = 1
    while k < len(parts) - 1:                # two formulas with a slash between them are one formula
        if parts[k - 1][0] == "m" and parts[k][1] == "/" and parts[k + 1][0] == "m":
            parts[k - 1:k + 2] = [("m", parts[k - 1][1] + "/" + parts[k + 1][1], parts[k - 1][2] + "/" + parts[k + 1][2])]
        else:
            k += 1
    out = []
    for i, (kind, content, src) in enumerate(parts):
        if kind == "m":
            prev = before + "".join(q[2] for q in parts[:i])
            nxt = "".join(q[2] for q in parts[i + 1:]) + after
            if not allowed(prev, nxt) and src:
                kind, content = "t", src     # GitHub would read no math here: the text stays as it was written
        if out and out[-1][0] == kind == "t":
            out[-1] = ("t", out[-1][1] + content)
        elif content:
            out.append((kind, content))
    return out


BARE = {"U", "V", "W", "k", "T", "Vs"}


def to_markdown(text, escape, lead=False, bare=False):
    """A plain-text string as Markdown: the text between formulas through `escape`, a formula as $$...$$. `bare`: the string is a whole table
    cell, so one symbol alone is a symbol."""
    parts = [("m", N.COLUMN_TEX[text.strip()])] if bare and text.strip() in BARE else segments(text, lead=lead)
    return "".join(N.m(s) if kind == "m" else f"`{s}`" if kind == "c" else escape(s) for kind, s in parts)


# ----------------------------------------------------------------------------- the files written by hand

CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
SKIP = re.compile(r"\$\$.+?\$\$|!?\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|<https?://[^>]+>|<[^>\n]+>|\{\{.*?\}\}|\{%.*?%\}|\{:[^}]*\}")
SUBSUP = [(re.compile(p), r) for p, r in (
    (r"(?<![A-Za-z0-9_])([UTHL])<sub>(H|R|f|r|b)</sub>(?:<sup>2</sup>|²)", r"\1_\2^2"),
    (r"(?<![A-Za-z0-9_])([UTHL])<sub>(H|R|f|r|b)</sub>", r"\1_\2"),
)]


def markdown(text):
    """The Markdown of a file written by hand with its plain-text math converted. Code, links, HTML, headings, front matter and formulas
    already there stay as they are; a table cell that is one bare symbol is converted."""
    out, fence, front = [], None, False
    for n, line in enumerate(text.split("\n")):
        s = line.strip()
        if n == 0 and s == "---":
            front = True
        elif front:
            front = s != "---"
        elif fence:
            if re.match(r"^\s*" + fence[0] + "{" + str(len(fence)) + r",}\s*$", line):
                fence = None
        elif re.match(r"^\s*(`{3,}|~{3,})", line):
            fence = re.match(r"^\s*(`{3,}|~{3,})", line).group(1)
        elif s and not s.startswith(("#", "<", "{%", "{:")) and not re.match(r"^\|?\s*:?-{3,}", s):
            line = _row(line) if s.startswith("|") else _line(line)
        out.append(line)
    return "\n".join(out)


def _row(line):
    """A table row: each cell by itself, so that a cell that is one bare symbol is a symbol."""
    cells, cur, i, tick = [], "", 0, False
    liquid = [(mt.start(), mt.end()) for mt in re.finditer(r"\{\{.*?\}\}|\{%.*?%\}", line)]
    while i < len(line):
        ch = line[i]
        if any(a <= i < b for a, b in liquid):
            cur += ch
            i += 1
            continue
        if ch == "\\" and i + 1 < len(line):
            cur += line[i:i + 2]
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
    return "|".join(_cell(c, first=k == 1) for k, c in enumerate(cells))


def _cell(raw, first):
    lead, body = len(raw) - len(raw.lstrip()), raw.strip()
    if body in BARE:
        return raw[:lead] + N.m(N.COLUMN_TEX[body]) + raw[lead + len(body):]
    return _line(raw, lead=first)


def _line(line, lead=False):
    for rx, r in SUBSUP:
        line = rx.sub(r, line)
    spans = sorted((mt.start(), mt.end()) for rx in (CODE, SKIP) for mt in rx.finditer(line))
    merged = []
    for a, b in spans:
        if merged and a < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    out, pos = [], 0
    for a, b in merged + [(len(line), len(line))]:
        out.append(_piece(line, pos, a, lead and pos == 0))
        out.append(line[a:b])
        pos = b
    return "".join(out)


def _piece(line, a, b, lead):
    text = line[a:b]
    if not text:
        return text
    stripped = text.lstrip()
    head = text[:len(text) - len(stripped)]
    if lead and stripped:
        text, keep = stripped, head
    else:
        keep = ""
    return keep + "".join(N.m(t) if kind == "m" else f"`{t}`" if kind == "c" else t
                          for kind, t in segments(text, lead=lead and bool(keep + text), before=line[:a] + keep, after=line[b:]))


# ----------------------------------------------------------------------------- what is left

LEFT = [(re.compile(rx), what) for rx, what in (
    (rf"{B}U(?:{US})?[HRb]{E}", "U_H, U_R, U_b"), (rf"{B}[UL]{US}ref{E}", "U_ref, L_ref"), (rf"{B}H{US}R{E}", "H_R"),
    (rf"{B}c(?:0|₀){E}", "c0"), (rf"{B}C0{E}", "C0"), (rf"{B}c{ST}", "c*"), (rf"{B}u{ST}{E}", "u*"), (rf"{B}z(?:0|₀){E}", "z0"),
    (rf"{B}T{US}(?:f|H|b|rms){E}", "T_f, T_H, T_rms"), (rf"{B}c{US}rms{E}", "c_rms"), (rf"{B}Re{US}[HD]{E}", "Re_H, Re_D"),
    (rf"{B}L{US}r{E}", "L_r"), (rf"{B}(?![ms]{SQ})[A-Za-z]{SQ}", "a squared symbol"), (r"√", "a square root"), (rf"{B}Sct{E}", "Sct"),
    (r"κ\s=\s0\.41", "kappa"), (rf"{BAR}U{BAR}", "|U|"), (rf"{B}D\s=\s0\.25{E}", "D = 0.25"), (rf"{B}W\s=\s0\.05", "W = 0.05"),
)]


def leftovers(line):
    """[(column, what)] of the plain-text math that one line of Markdown still holds outside code, links, HTML and formulas."""
    line = CODE.sub(lambda mt: " " * len(mt.group(0)), line)
    line = SKIP.sub(lambda mt: " " * len(mt.group(0)), line)
    return sorted((mt.start(), what) for rx, what in LEFT for mt in rx.finditer(line))


# ----------------------------------------------------------------------------- self test

def _plain(s):
    return "".join(N.m(t) if k == "m" else f"`{t}`" if k == "c" else t for k, t in segments(s))


def self_test():
    cases = [
        ("C / c0, c0 = q / (U_ref L_ref^2) as the benchmark defines it",
         r"$$C/c_0$$, $$c_0 = \dfrac{q}{U_{\mathrm{ref}} L_{\mathrm{ref}}^2}$$ as the benchmark defines it"),
        ("c0 = cgas q / (UH H^2) = 45.18 ppm (45.2 in the paper)",
         r"$$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ = 45.18 ppm (45.2 in the paper)"),
        ("c0 = 0.05 q / (U_H H^2) = 12.283 ppm", r"$$c_0 = \dfrac{0.05\thinspace q}{U_H H^2}$$ = 12.283 ppm"),
        ("concentration ratio = C / c0, c0 = q / (U_R H_R^2): 132.5 ppm",
         r"concentration ratio = $$C/c_0$$, $$c_0 = \dfrac{q}{U_R H_R^2}$$: 132.5 ppm"),
        ("velocities by U_H, k by U_H^2", r"velocities by $$U_H$$, $$k$$ by $$U_H^2$$"),
        ("c* = C/c0 (c0 = q/(U_H H^2) = 429.2 ppm)", r"$$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_H H^2}$$ = 429.2 ppm)"),
        ("the modelled c* = c U_H H^2 / Q for", r"the modelled $$c^\ast = c\thinspace U_H H^2/Q$$ for"),
        ("U, V, W, uu, vv, ww, k, C, c_rms, concentration_ratio",
         r"$$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$, $$C$$, $$c_{\mathrm{rms}}$$, $$c^\ast$$"),
        ("U, W, k and c*", r"$$U$$, $$W$$, $$k$$ and $$c^\ast$$"),
        ("Case C, D and E", "Case C, D and E"),
        ("wind from E, ESE, WSW or W", "wind from E, ESE, WSW or W"),
        ("k-ε and k is low, k-omega too", "k-ε and $$k$$ is low, k-omega too"),
        ("E, ESE, WSW, W and U is a symbol", "E, ESE, WSW, W and $$U$$ is a symbol"),
        ("FB is not defined for V and W (their", "FB is not defined for $$V$$ and $$W$$ (their"),
        ("the modelled √(|U|²+2k)/U_H and |U|", r"the modelled $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U_H$$ and $$\lvert\mathbf{U}\rvert$$"),
        ("Vs / U(15.9 m)", r"$$V_{\mathrm{s}}/U(15.9\text{ m})$$"),
        ("θ = (T_f − T)/(T_f − T_H)", r"$$\theta = (T_f - T)/(T_f - T_H)$$"),
        ("hit rate D = 0.25, W = 0.05 U_H", r"hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$"),
        ("m^2/s^2 and 5.83e-6 m3/s", "m²/s² and 5.83e-6 m³/s"),
        ("Friction velocity u* (m/s), z₀ (mm), Re_H", r"Friction velocity $$u_\ast$$ (m/s), $$z_0$$ (mm), $$\mathrm{Re_H}$$"),
        ("Case F: U_H, UH = 4.94 m/s", r"Case F: $$U_H$$, $$U_H$$ = 4.94 m/s"),
        ("U/U\\_H and k/U\\_H^2", r"$$U/U_H$$ and $$k/U_H^2$$"),
        ("T_f - T_H = 33.63 K", "$$T_f - T_H$$ = 33.63 K"),
        ("the flux u′θ′ and ⟨θ′c′⟩", r"the flux $$\overline{u'\theta'}$$ and $$\overline{\theta'c'}$$"),
        ("concentration\\_ratio = C / c0 and k_ratio", r"`concentration_ratio` = $$C/c_0$$ and `k_ratio`"),
    ]
    for src, want in cases:
        got = _plain(src)
        assert got == want, (src, got, want)
    ident = lambda s: s    # noqa: E731
    assert to_markdown("k", ident, bare=True) == "$$k$$" and to_markdown("kg", ident, bare=True) == "kg"
    assert to_markdown("V, sign flipped (control)", ident, lead=True) == "$$V$$, sign flipped (control)"
    assert to_markdown("k (resolved)", ident, lead=True) == "$$k$$ (resolved)"
    assert to_markdown("c*, Sct 0.3", ident, lead=True) == r"$$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3"
    assert to_markdown("C to E", ident, lead=True) == "C to E"
    md = "# U_H\n\nSee `U_H` and [U_H](x.md) and U\\_H, with U\\_H^2.\n\n| U | k |\n|---|---|\n| U\\_H | 1 |\n\n```\nU_H\n```\n"
    want = ("# U_H\n\nSee `U_H` and [U_H](x.md) and $$U_H$$, with $$U_H^2$$.\n\n| $$U$$ | $$k$$ |\n|---|---|\n| $$U_H$$ | 1 |\n\n```\nU_H\n```\n")
    assert markdown(md) == want, markdown(md)
    assert [w for _, w in leftovers("a U_H and `U_H` and $$U_H$$")] == ["U_H, U_R, U_b"]
    print("mathtext self-test: OK")


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    import difflib
    write = "--write" in argv
    for path in (a for a in argv if not a.startswith("-")):
        with open(path, encoding="utf-8", newline="") as f:
            old = f.read()
        new = markdown(old)
        if write:
            if new != old:
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new)
        else:
            sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True), path, path + " (converted)", n=0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
