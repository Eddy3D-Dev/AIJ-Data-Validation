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
    (r"c(?:0|₀)", "c_0"), (r"C0", "C_0"), (r"z(?:0|₀)", "z_0"), (r"U0", "U_0"), (r"uH", "u_H"), (r"C(?:mu|μ)", r"C_\mu"), (rf"U{US}[xyz]", None), (rf"θ{US}H", r"\theta_H"), (rf"θ{US}f", r"\theta_f"),
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
            return tex or (rf"{mt.group(1)}_{{\mathrm{{rms}}}}" if mt.groups() else s.replace("\\", ""))
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


@rule("temperature-difference", rf"{B}(?P<a>T{US}f|T{US}H|T{US}b|θ{US}H|θ{US}f)\s*{MINUS}\s*(?P<b>T{US}f|T{US}H|T{US}b|T|θ{US}H|θ{US}f){E}")
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


@rule("identifier", rf"{B}(?:velocity{US}ratio{US}sd|velocity{US}ratio|concentration{US}ratio|k{US}ratio|p{US}rgh){E}")
def _identifier(mt):
    return "c", mt.group(0).replace("\\", "")


# ----------------------------------------------------------------------------- the workbook's names, coordinates, powers of ten

@rule("variance-from-rms", rf"{B}(?P<v>uu|vv|ww)\s*=\s*(?P<c>[uvw]){US}rms\^2{E}")
def _variance_from_rms(mt):
    return "m", rf"{N.COLUMN_TEX[mt['v']]} = {mt['c']}_{{\mathrm{{rms}}}}^2"


@rule("bare-columns", rf"{B}(?:uu|vv|ww|uv|uw|vw|uc|vc|wc|uT|vT|wT){E}")
def _bare_columns(mt):
    return "m", N.COLUMN_TEX[mt.group(0)]


@rule("kinetic-energy", r"½\(uu\+vv\+ww\)")
def _kinetic_energy(mt):
    return "m", r"\tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)"


@rule("workbook-squares", r"<(?P<c>[uvw])'2>")
def _workbook_squares(mt):
    return "m", rf"\overline{{{mt['c']}'^2}}"


@rule("workbook-speed", r"<usc>")
def _workbook_speed(mt):
    return "m", r"\langle u_{\mathrm{sc}}\rangle"


@rule("workbook-sigma", rf"{B}(?:sigma|σ){US}(?P<s>usc|u|v|w){E}")
def _workbook_sigma(mt):
    return "m", r"\sigma_{\mathrm{usc}}" if mt["s"] == "usc" else rf"\sigma_{mt['s']}"


SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
SGN = r"[-−+±]"
UNIT = r"(?:\s(?:kg/s|m/s|mm|cm|m)(?![\w/²³]))"
TERM = rf"(?:{SGN}?(?:{NUM}(?:/{NUM})?(?:\s?[HDb](?![\w/]))?°?|[HD](?:/{NUM})?(?![\w/]))|{SGN}[xyz](?![\w/])){UNIT}?"      # 0.25, 1/16 H, 2b, 22.5°, H/16, -x, 0.2 m
SEPARATOR = r"(?:,?\sand\s|,\s|\sx\s|\s\.\.\.?\s|\s…\s|\sto\s)"
VALUES = rf"{TERM}(?:(?:\sx\s{TERM})+|(?:,\s{TERM}){{2,}}|(?:,\s{TERM})*,?\sand\s{TERM}|(?:\s\.\.\.?\s|\s…\s|\sto\s){TERM})?"     # a value, a list of three or more, "a, b and c", a range
RELATION = r"(?:=|<|>|≤|≥|≈)"
TERM_RX = re.compile(rf"(?P<s>{SGN})?(?P<v>{NUM}(?:/{NUM})?|[HD](?:/{NUM})?|[xyz])(?:(?P<sp>\s?)(?P<h>[HDb]))?(?P<deg>°)?(?:\s(?P<u>kg/s|m/s|mm|cm|m))?")
SEPARATOR_RX = re.compile(rf"({SEPARATOR})")
RELATION_TEX = {"=": "=", "<": r"\lt", ">": r"\gt", "≤": r"\le", "≥": r"\ge", "≈": r"\approx"}


def terms(text):
    """The LaTeX of a value, a list or a range of values: `0.25`, `-2 to 5`, `0.02 .. 2H`, `1/16 H`, `0.20 m`, `±1`."""
    out = []
    for piece in SEPARATOR_RX.split(text):
        if SEPARATOR_RX.fullmatch(piece):
            key = "and" if piece.strip().endswith("and") else piece.strip()
            out.append({",": r",\thinspace ", "to": r"\text{ to }", "and": r"\text{ and }", "x": r"\thinspace\times\thinspace "}.get(key, r"\thinspace\ldots\thinspace "))
            continue
        mt = TERM_RX.fullmatch(piece)
        out.append({None: "", "-": "-", "−": "-", "+": "+", "±": r"\pm "}[mt["s"]] + mt["v"]
                   + ((r"\thinspace " if mt["sp"] else "") + mt["h"] if mt["h"] else "")
                   + (r"^\circ" if mt["deg"] else "")
                   + (rf"\thinspace\mathrm{{{mt['u']}}}" if mt["u"] else ""))
    return "".join(out)


LHS_TEX = {"dx": r"\mathrm{d}x", "WD": r"\mathrm{WD}", "Rb": "R_b"}


@rule("coordinate-relation", rf"{B}(?P<lhs>{BAR}?[xyz](?:\s?/\s?[HbD])?{BAR}?|dx|(?:{NUM}\s?)?[HbD](?:\sx\s(?:{NUM}\s?)?[HbD])*|WD|R|Q|Rb)(?P<rest>(?:\s{RELATION}\s{VALUES})+)(?![\w\"”])")
def _coordinate_relation(mt):
    lhs = mt["lhs"].replace("\\", "").replace(" ", "")
    if lhs in LHS_TEX:
        lhs = LHS_TEX[lhs]
    elif re.fullmatch(rf"(?:{NUM})?[HbD](?:x(?:{NUM})?[HbD])*", lhs):
        lhs = r"\thinspace\times\thinspace ".join(re.sub(rf"^({NUM})\s?([HbD])$", lambda g: g[1] + (r"\thinspace " if re.match(rf"{NUM}\s[HbD]$", item) else "") + g[2], item)
                                                  for item in mt["lhs"].split(" x "))
    elif lhs.startswith("|"):
        lhs = rf"\lvert {lhs.strip('|')}\rvert"
    parts = re.split(rf"\s({RELATION})\s", mt["rest"])
    return "m", lhs + "".join(f" {RELATION_TEX[rel]} {terms(rhs)}" for rel, rhs in zip(parts[1::2], parts[2::2]))


@rule("coordinate-interval", rf"{B}(?P<c>[xyz](?:,\s[xyz])*)\s(?:in|∈)\s\[(?P<a>{TERM}),\s(?P<b>{TERM})\](?:\s(?P<u>mm|cm|m)(?![\w/²³]))?")
def _coordinate_interval(mt):
    unit = rf"\thinspace\mathrm{{{mt['u']}}}" if mt["u"] else ""
    return "m", rf"{mt['c'].replace(', ', r',\thinspace ')} \in \lbrack {terms(mt['a'])},\thinspace {terms(mt['b'])}\rbrack{unit}"


@rule("reynolds-number", rf"{B}Re\s≈\s(?P<n>\d{{1,3}}(?:,\d{{3}})+|{NUM})(?:\s×\s10(?P<e>[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+))?{E}")
def _reynolds_number(mt):
    return "m", r"\mathrm{Re} \approx " + mt["n"].replace(",", r"\thinspace ") + (rf" \times 10^{{{mt['e'].translate(SUPER)}}}" if mt["e"] else "")


@rule("atom-multiple", rf"{B}(?P<atom>{ATOM})\s=\s(?P<n>{NUM})\s?H(?![\w/])")
def _atom_multiple(mt):
    return "m", f"{atom(mt['atom'])} = {mt['n']}" + (r"\thinspace H" if " " in mt["n"] or mt.group(0).endswith(" H") else "H")


@rule("field-at", rf"{B}(?P<f>[UkC])\((?P<c>[xyz])\s=\s(?P<v>{VALUES})\)")
def _field_at(mt):
    return "m", f"{mt['f']}({mt['c']} = {terms(mt['v'])})"


@rule("coordinate-triple", rf"{B}x,\s?y,?\s(?:and\s)?z{E}")
def _coordinate_triple(mt):
    sep = re.findall(r",\s?|,?\sand\s", mt.group(0))
    return "mm", [("m", "x"), ("t", sep[0]), ("m", "y"), ("t", sep[1]), ("m", "z")]


@rule("coordinate-ratio", rf"{B}(?P<c>[xyz])\s?/\s?(?P<d>[HbD]|Z{US}?R){E}")
def _coordinate_ratio(mt):
    return "m", f"{mt['c']}/{atom(mt['d']) or mt['d']}"


@rule("direction", r"(?<!\w)[+−][xyz](?![\w/])")
def _direction(mt):
    return "m", mt.group(0).replace("−", "-")


@rule("frame-map", rf"{B}(?P<a>[UVW])\s=\s(?P<s>[-−]?)U{US}(?P<b>[xyz]){E}")
def _frame_map(mt):
    return "m", f"{mt['a']} = {'-' if mt['s'] else ''}U_{mt['b']}"


@rule("power-law-profile", r"\(z/H\)\^\(1/7\)")
def _power_law_profile(mt):
    return "m", "(z/H)^{1/7}"


@rule("multiples-of", r"(?<=multiples of )[HbD](?![\w/])")
def _multiples_of(mt):
    return "m", mt.group(0)


@rule("grid-spacing", rf"{B}H/(?P<n>{NUM}){E}")
def _grid_spacing(mt):
    return "m", f"H/{mt['n']}"


@rule("multiple-of-H", rf"{B}(?P<n>{NUM})(?:–(?P<n2>{NUM}))?\s?H(?![\w/])")
def _multiple_of_h(mt):
    n = mt["n"] + (rf"\text{{–}}{mt['n2']}" if mt["n2"] else "")
    return "m", rf"{n}\thinspace H" if " " in mt.group(0) else f"{n}H"


POWER_OPERATOR = {"×": r"\times", "·": r"\cdot"}


@rule("power-of-ten", rf"{B}(?:(?:(?P<m>{NUM})\s?)?(?P<x>[×·])\s?)?10(?P<e>[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+|\^-?\d+)(?P<dx>\sdx(?![\w]))?{E}")
def _power_of_ten(mt):
    exponent = mt["e"].translate(SUPER).lstrip("^")
    lead = (f"{mt['m']} " if mt["m"] else "") + POWER_OPERATOR[mt["x"]] + " " if mt["x"] else ""
    return "m", f"{lead}10^{{{exponent}}}" + (r"\thinspace\mathrm{d}x" if mt["dx"] else "")


@rule("plus-minus-scale", r"±(?P<s>[HD])(?![\w/])")
def _plus_minus_scale(mt):
    return "m", rf"\pm {mt['s']}"


@rule("signed-angle", r"(?<!\w)[+−]θ(?![\w′])")
def _signed_angle(mt):
    return "m", mt.group(0).replace("−", "-").replace("θ", r"\theta")


@rule("difference-magnitude", rf"{BAR}Δ(?P<q>Vs|U)?{BAR}")
def _difference_magnitude(mt):
    return "m", r"\lvert\Delta" + {None: "", "Vs": r" V_{\mathrm{s}}", "U": " U"}[mt["q"]] + r"\rvert"


@rule("residual-field", rf"{B}(?P<f>p|epsilon)(?=\s\d\.\de[-+]\d\d)")
def _residual_field(mt):
    return "m", "p" if mt["f"] == "p" else r"\varepsilon"


@rule("turbulent-dissipation", rf"{B}epsilon\s*=\s*C(?:mu|μ)\^0\.5\s+k\s+dU/dz{E}")
def _turbulent_dissipation(mt):
    return "m", r"\varepsilon = C_\mu^{0.5}\thinspace k\thinspace \mathrm{d}U/\mathrm{d}z"


@rule("turbulent-length", rf"{B}u{ST}\^2/sqrt\(C(?:mu|μ)\)")
def _turbulent_length(mt):
    return "m", r"u_\ast^2/\sqrt{C_\mu}"


@rule("log-ratio", r"log₂\(model / tunnel\)")
def _log_ratio(mt):
    return "m", r"\log_2(\text{model}/\text{tunnel})"


@rule("log-decade", rf"{B}log₁₀(?!\w)")
def _log_decade(mt):
    return "m", r"\log_{10}"


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


BARE = {"U", "V", "W", "k", "T", "Vs", "x", "y", "z"}


def to_markdown(text, escape, lead=False, bare=False):
    """A plain-text string as Markdown: the text between formulas through `escape`, a formula as $$...$$. `bare`: the string is a whole table
    cell, so one symbol alone is a symbol."""
    parts = [("m", N.COLUMN_TEX.get(text.strip(), text.strip()))] if bare and text.strip() in BARE else segments(text, lead=lead)
    return "".join(N.m(s) if kind == "m" else f"`{s}`" if kind == "c" else escape(s) for kind, s in parts)


# ----------------------------------------------------------------------------- the files written by hand

CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
SKIP = re.compile(r"\$\$.+?\$\$|!?\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|<https?://[^>]+>|<[^>\n]+>|\{\{.*?\}\}|\{%.*?%\}|\{:[^}]*\}")
SUBSUP = [(re.compile(p), r) for p, r in (
    (r"(?<![A-Za-z0-9_])([UTHL])<sub>(H|R|f|r|b)</sub>(?:<sup>2</sup>|²)", r"\1_\2^2"),
    (r"(?<![A-Za-z0-9_])([UTHL])<sub>(H|R|f|r|b)</sub>", r"\1_\2"),
)]


FIGURE = re.compile(r"\{%-?\s*include figure\.html\b")
CAPTION = re.compile(r'(caption=")([^"]*)(")')


def caption(line):
    """The caption of a `{% include figure.html ... caption="..." %}` line (Markdown for kramdown, as the include sets it in a figcaption), or None."""
    mt = FIGURE.match(line.strip()) and CAPTION.search(line)
    return mt.group(2) if mt else None


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
        elif FIGURE.match(s):
            line = CAPTION.sub(lambda mt: mt.group(1) + _line(mt.group(2)) + mt.group(3), line)
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


MERGE = re.compile(r"\$\$([^$]+?)\$\$ = \$\$(\d+(?:\.\d+)?(?:\\thinspace )?H)\$\$")


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
    return MERGE.sub(r"$$\1 = \2$$", "".join(out))


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
    (rf"{B}(?:uu|vv|ww|uv|uw|vw|uc|vc|wc|uT|vT|wT){E}", "uu, vv, ww, uv, uw, vw, uc, uT"), (rf"{B}[xyz]\s?/\s?[HbD]{E}", "x/H"), (rf"{B}H/\d", "H/64"),
    (rf"{B}[xyz]\s[=<>≤≥]\s[-−+±]?[\dHDxyz]", "a coordinate (z = 0.1)"), (rf"{B}[xyz]\sin\s\[", "a coordinate interval"),
    (r"10\^-?\d|10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]", "a power of ten"), (rf"{B}C(?:mu|μ){E}", "Cmu"), (rf"{B}U0{E}", "U0"), (r"\(z/H\)\^", "a power law"),
    (rf"<[uvw]'2>|<usc>|{B}sigma_|{B}θ{US}[Hf]|{B}uH{E}", "a workbook name"),
    (rf"{B}(?:WD|[HbR]|Rb|dx)\s=\s[-−+]?\d", "a scale or a score (H = 0.2 m)"),
    (r"multiples of [HbD](?![\w/])", "multiples of H"), (r"log[₂₁]", "log"), (r"(?<![\w'\"‘“])[+−][xyz](?![\w/])", "+x"),
)]


def leftovers(line):
    """[(column, what)] of the plain-text math that one line of Markdown still holds outside code, links, HTML and formulas. A figure include is
    read by its caption."""
    cap = caption(line)
    if cap is not None:
        line = cap
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
        ('(uu = u_rms^2) so A and B share one column; uv and wT',
         r"($$\overline{u'u'} = u_{\mathrm{rms}}^2$$) so A and B share one column; $$\overline{u'v'}$$ and $$\overline{w'\theta'}$$"),
        ('plane y/H = 0, z/H = 1/16 and z/b = 0.125, y/H = ±1',
         r"plane $$y/H = 0$$, $$z/H = 1/16$$ and $$z/b = 0.125$$, $$y/H = \pm 1$$"),
        ('x/H = -2 to 5 and |x/H| ≤ 0.2 and x/H = 0.25, 0.5, 1',
         r"$$x/H = -2\text{ to }5$$ and $$\lvert x/H\rvert \le 0.2$$ and $$x/H = 0.25,\thinspace 0.5,\thinspace 1$$"),
        ('z = 0.02 .. 2H, z = 0.019 H is, z = H/16 plane, z = -1 m, z = 0.1 D',
         r"$$z = 0.02\thinspace\ldots\thinspace 2H$$, $$z = 0.019\thinspace H$$ is, $$z = H/16$$ plane, $$z = -1\thinspace\mathrm{m}$$, $$z = 0.1\thinspace D$$"),
        ('z in [1.2, 7] m; x, y ∈ [−0.04, 0.04]',
         r"$$z \in \lbrack 1.2,\thinspace 7\rbrack\thinspace\mathrm{m}$$; $$x,\thinspace y \in \lbrack -0.04,\thinspace 0.04\rbrack$$"),
        ('street x < 0; y ≤ 0 half; y = -x to; z ≈ 32 m',
         r"street $$x \lt 0$$; $$y \le 0$$ half; $$y = -x$$ to; $$z \approx 32\thinspace\mathrm{m}$$"),
        ('frame +x, +y and +z up; x, y, z in m',
         r"frame $$+x$$, $$+y$$ and $$+z$$ up; $$x$$, $$y$$, $$z$$ in m"),
        ('limit 10^-3, 9 × 10⁻¹⁶, volume fraction × 10⁶ and 10⁻⁴ dx',
         r"limit $$10^{-3}$$, $$9 \times 10^{-16}$$, volume fraction $$\times 10^{6}$$ and $$10^{-4}\thinspace\mathrm{d}x$$"),
        ('epsilon = Cmu^0.5 k dU/dz (Cmu = 0.09) and u*^2/sqrt(Cmu)',
         r"$$\varepsilon = C_\mu^{0.5}\thinspace k\thinspace \mathrm{d}U/\mathrm{d}z$$ ($$C_\mu$$ = 0.09) and $$u_\ast^2/\sqrt{C_\mu}$$"),
        ('(z/H)^(1/7) with U0 = 4 m/s',
         r"$$(z/H)^{1/7}$$ with $$U_0$$ = 4 m/s"),
        ("<u'2> and sigma_u, <usc> / sigma_usc",
         r"$$\overline{u'^2}$$ and $$\sigma_u$$, $$\langle u_{\mathrm{sc}}\rangle$$ / $$\sigma_{\mathrm{usc}}$$"),
        ('mean |ΔVs| and |ΔU| and |Δ|',
         r"mean $$\lvert\Delta V_{\mathrm{s}}\rvert$$ and $$\lvert\Delta U\rvert$$ and $$\lvert\Delta\rvert$$"),
        ('log₂(model / tunnel) and log₁₀ of c*',
         r"$$\log_2(\text{model}/\text{tunnel})$$ and $$\log_{10}$$ of $$c^\ast$$"),
        ('residuals U_x 1.0e-04, p 3.0e-05, epsilon 1.0e-03 and p_rgh',
         r"residuals $$U_x$$ 1.0e-04, $$p$$ 3.0e-05, $$\varepsilon$$ 1.0e-03 and `p_rgh`"),
        ('U = U_y, V = -U_x',
         r"$$U = U_y$$, $$V = -U_x$$"),
        ('Re ≈ 1.1 × 10⁵ and Re ≈ 17,000',
         r"$$\mathrm{Re} \approx 1.1 \times 10^{5}$$ and $$\mathrm{Re} \approx 17\thinspace 000$$"),
        ('x = -0.15, 100 % ethylene; z = 15, 19 and 30 m',
         r"$$x = -0.15$$, 100 % ethylene; $$z = 15,\thinspace 19\text{ and }30\thinspace\mathrm{m}$$"),
        ('L_r = 3.39 H at dx = 1.6 m (H/10), 4–6 H and (10 H)',
         r"$$L_r = 3.39\thinspace H$$ at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ ($$H/10$$), $$4\text{–}6\thinspace H$$ and ($$10\thinspace H$$)"),
        ('k (= ½(uu+vv+ww) here); +θ and −θ',
         r"$$k$$ (= $$\tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ here); $$+\theta$$ and $$-\theta$$"),
        ('across a span of ±H and ±250 m',
         r'across a span of $$\pm H$$ and ±250 m'),
        ('H = 0.06 m, pitch 0.12 m; H = 2b = 0.16 m; 0.25 H = 0.05 m; Tower 0.25H x 0.25H x H = 62.5 x 62.5 x 250 mm',
         r'$$H = 0.06\thinspace\mathrm{m}$$, pitch 0.12 m; $$H = 2b = 0.16\thinspace\mathrm{m}$$; $$0.25\thinspace H = 0.05\thinspace\mathrm{m}$$; Tower $$0.25H\thinspace\times\thinspace 0.25H\thinspace\times\thinspace H = 62.5\thinspace\times\thinspace 62.5\thinspace\times\thinspace 250\thinspace\mathrm{mm}$$'),
        ('at WD = 0° and WD = 22.5° and 45°, R = -0.910, Q = 1 kg/s, Rb = -0.086 but N = 0, E = 90',
         r'at $$\mathrm{WD} = 0^\circ$$ and $$\mathrm{WD} = 22.5^\circ\text{ and }45^\circ$$, $$R = -0.910$$, $$Q = 1\thinspace\mathrm{kg/s}$$, $$R_b = -0.086$$ but N = 0, E = 90'),
        ('the difference θ_H − θ_f and T_b - T_f',
         r'the difference $$\theta_H - \theta_f$$ and $$T_b - T_f$$'),
        ('Positions in multiples of H and in multiples of b.', r'Positions in multiples of $$H$$ and in multiples of $$b$$.'),
        ('a second case x = 0 and y = 0',
         r"a second case $$x = 0$$ and $$y = 0$$"),
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
