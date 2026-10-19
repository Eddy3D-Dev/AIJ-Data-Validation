r"""The nomenclature of the site: the one place that says what a symbol, a table column and a score mean.

Math is written in LaTeX between double dollar signs, `$$c_0 = \dfrac{q}{U_H H^2}$$`, on every page and in every README. `$$` is the one
delimiter that both renderers read: GitHub (README.md, clean/*.md, docs/**/*.md viewed in the repository) shows `$$...$$` as inline math
inside a sentence and as display math on lines of its own, and kramdown, which builds the site, knows no other math delimiter (it turns
`$$...$$` into `\(...\)` and `\[...\]`, which the MathJax of docs/_includes/head_custom.html typesets). The two renderers differ in what
they let a formula contain and where it may stand, so a formula here and everywhere else follows these rules (scripts/check_markdown.py
enforces them):

  * no `*` or `~` (GitHub pairs them as emphasis or strike-through before it looks for math): `\ast`, `\cdot`, `\times`;
  * no backslash before punctuation (`\{ \, \; \\ \| \_ \%`: GitHub drops the backslash): `\lbrace`, `\lvert`, `\thinspace`, `\text{ }`;
  * a subscript's underscore follows a letter or a digit (`U_H`), never a brace or a bracket (`\mathrm{Re}_H`): GitHub reads such an
    underscore as the start of emphasis and a later `_{` as its end. `\mathrm{Re_H}` is the same formula;
  * no pipe (it ends a table cell): `\lvert x \rvert`, `\mid`; no `<` or `>` (`\lt`, `\gt`, `\le`, `\ge`), no `&`, no `{{` or `{%`;
  * the opening `$$` stands at the start of a line or after a space or `(`, and the closing `$$` is not followed by a letter, a digit or `_`
    (GitHub then reads no math); never inside a heading, a link text, `<summary>` or a block of raw HTML.

The symbols are the dataset's own (clean/SCHEMA.md, the Data pages), with three choices made here because two meanings met on one letter:
the hit rate of VDI 3783-9 is $\mathrm{HR}$ (VDI calls it q, and q is the tracer release rate of the experiment, in $c_0$); its tolerances
are $\delta_{\mathrm{rel}}$ and $\delta_{\mathrm{abs}}$ (VDI: D and W, but D is also the block size of Case C and W the vertical velocity);
and $\theta'$ is the temperature fluctuation (as in the data paper) while $\theta$ without a prime is the floor-referenced temperature the
solves are scored on.

scripts/build_api.py writes three texts from the entries below, so a definition cannot differ from page to page:

    docs/_includes/nomenclature.md          every symbol, column and score, as bullet points in a closed <details>: under a table of quantities or columns
    docs/_includes/nomenclature-scores.md   the scores as bullet points, and the quantities they are computed on: under a table of scores
    docs/_includes/metrics.md               the scores in full, with their formulas: the Metrics section of the Method page

and the same texts between `<!--nomenclature full-->`, `<!--nomenclature scores-->` or `<!--nomenclature metrics-->` and
`<!--/nomenclature-->` in the README files, which GitHub renders without Jekyll. Standard library only.
"""
from __future__ import annotations

import re

OPEN = False        # True: the nomenclature under a table is open, not closed (one switch for every page and README)

# ----------------------------------------------------------------------------- columns -> symbols

# The cleaned table's column (clean/SCHEMA.md section 1) -> its symbol. A column that is not here is an identifier, not a quantity
# (`point_id`, `config`, `instrument`, `campaign`, `run`, `x`, `y`, `z`, `wind_direction_deg`); it stays in code font.
COLUMN_TEX = {
    "U": "U", "V": "V", "W": "W",
    "uu": r"\overline{u'u'}", "vv": r"\overline{v'v'}", "ww": r"\overline{w'w'}",
    "uv": r"\overline{u'v'}", "uw": r"\overline{u'w'}", "vw": r"\overline{v'w'}",
    "k": "k", "Vs": r"V_{\mathrm{s}}",
    "velocity_ratio": r"U/U_{\mathrm{ref}}", "velocity_ratio_sd": r"\sigma_{U/U_{\mathrm{ref}}}", "k_ratio": r"k/U_{\mathrm{ref}}^2",
    "C": "C", "c_rms": r"c_{\mathrm{rms}}", "concentration_ratio": r"c^\ast",
    "T": "T", "T_rms": r"T_{\mathrm{rms}}",
    "uc": r"\overline{u'c'}", "vc": r"\overline{v'c'}", "wc": r"\overline{w'c'}",
    "uT": r"\overline{u'\theta'}", "vT": r"\overline{v'\theta'}", "wT": r"\overline{w'\theta'}",
}


RISKY = re.compile(r"[*~|<>&$`]|\\[^A-Za-z\s]|\{\{|\{%|(?<![A-Za-z0-9])_(?!\s)")


def m(tex):
    """One inline formula as it is written in Markdown. A formula that GitHub or kramdown would read differently (see the rules above) is an error."""
    if RISKY.search(tex):
        raise ValueError(f"a formula that GitHub or kramdown would read differently: {tex!r}")
    return f"$${tex}$$"


def column_symbols(columns):
    """A list of columns as symbols: `$$U$$, $$V$$, $$\\overline{u'u'}$$, ...`; a column that is no quantity stays in code font."""
    return ", ".join(m(COLUMN_TEX[c]) if c in COLUMN_TEX else f"`{c}`" for c in columns)


# ----------------------------------------------------------------------------- the formulas of the scores (each written once)

O, P = r"\overline{o}", r"\overline{p}"
REL, ABS = r"\delta_{\mathrm{rel}}", r"\delta_{\mathrm{abs}}"
FB = rf"2({O}-{P})/({O}+{P})"
HIT_REL, HIT_ABS = rf"\lvert p_i-o_i\rvert/\lvert o_i\rvert \le {REL}", rf"\lvert p_i-o_i\rvert \le {ABS}"
PAIR = ("a pair is the measured value " + m("o_i") + " and the modelled value " + m("p_i") + " at one point; " + m(O) + " and " + m(P)
        + " are the means over the pairs")

# ----------------------------------------------------------------------------- the entries: (symbol, column, meaning, unit)

_VELOCITY = [
    (m("U") + ", " + m("V") + ", " + m("W"), "`U`, `V`, `W`",
     "mean velocity along " + m("+x") + ", " + m("+y") + ", " + m("+z") + "; " + m("V") + " is positive toward " + m("+y") + " in every case", "m/s"),
    (m(r"\lvert\mathbf{U}\rvert"), "", "magnitude of the mean velocity vector, " + m(r"\sqrt{U^2+V^2+W^2}"), "m/s"),
    (m(r"V_{\mathrm{s}}"), "`Vs`", "mean omnidirectional scalar speed of a thermistor (never a vector magnitude)", "m/s"),
    (m(r"\overline{u'u'}") + ", " + m(r"\overline{v'v'}") + ", " + m(r"\overline{w'w'}"), "`uu`, `vv`, `ww`",
     "velocity variances (overbar: time average, prime: fluctuation about it)", "m²/s²"),
    (m(r"\overline{u'v'}") + ", " + m(r"\overline{u'w'}") + ", " + m(r"\overline{v'w'}"), "`uv`, `uw`, `vw`", "Reynolds shear stresses", "m²/s²"),
    (m(r"k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)"), "`k`", "turbulent kinetic energy", "m²/s²"),
    (m(r"U/U_{\mathrm{ref}}"), "`velocity_ratio`",
     "mean speed over the case's reference speed (" + m(r"V_{\mathrm{s}}/U_{\mathrm{ref}}") + " for a thermistor)", "—"),
    (m(r"\sigma_{U/U_{\mathrm{ref}}}"), "`velocity_ratio_sd`", "standard deviation of `velocity_ratio` over the observations behind a field value (Case F)", "—"),
    (m(r"k/U_{\mathrm{ref}}^2"), "`k_ratio`", "turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)", "—"),
]
_SCALARS = [
    (m("C"), "`C`", "mean tracer-gas concentration as published (volume fraction " + m(r"\times 10^6") + " of the released gas diluted in air)", "ppm"),
    (m(r"c_{\mathrm{rms}}"), "`c_rms`", "root mean square of the concentration fluctuation", "ppm"),
    (m("c_0"), "",
     "reference concentration, defined for each case on its Data page: " + m(r"c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}") + " (" + m("U_R H_R^2")
     + " in the denominator in Case M)", "ppm"),
    (m(r"c^\ast"), "`concentration_ratio`",
     "dimensionless concentration " + m(r"c^\ast = C/c_0") + "; the value of a solve is " + m(r"c\thinspace U_H H^2/Q") + " for its mean concentration "
     + m("c") + " and its source strength " + m("Q"), "—"),
    (m(r"\mathrm{Sc_t}"), "", "turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)", "—"),
    (m("T") + ", " + m(r"T_{\mathrm{rms}}"), "`T`, `T_rms`", "mean air temperature as published (Cases J and L) and the root mean square of its fluctuation", "°C, K"),
    (m(r"\overline{u'c'}") + ", " + m(r"\overline{v'c'}") + ", " + m(r"\overline{w'c'}"), "`uc`, `vc`, `wc`", "turbulent concentration fluxes", "ppm·m/s"),
    (m(r"\overline{u'\theta'}") + ", " + m(r"\overline{v'\theta'}") + ", " + m(r"\overline{w'\theta'}"), "`uT`, `vT`, `wT`",
     "turbulent heat fluxes (" + m(r"\theta'") + ": the temperature fluctuation)", "K·m/s"),
    (m(r"\theta = \dfrac{T_f - T}{T_f - T_H}"), "",
     "floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at " + m("H") + "; " + m("T_f")
     + " is the floor temperature and " + m("T_H") + " the temperature of the approach flow at " + m("H"), "—"),
]
_SCALES = [
    (m("H") + ", " + m("b") + ", " + m("D"), "",
     "height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by", "m"),
    (m("U_H"), "", "reference speed: the mean approach-flow speed at the height " + m("H") + " (each Data page gives the value used)", "m/s"),
    (m("U_R") + ", " + m("H_R") + ", " + m("Z_R"), "",
     "reference speed and height of a workbook: Case E, " + m("U_R") + " at " + m("Z_R") + " = 250 m full scale (1 m in the model); Case M, " + m("U_R") + " and " + m("H_R")
     + " at the reference point of the tunnel and of each field run", "m/s, m"),
    (m(r"U_{\mathrm{ref}}") + ", " + m(r"L_{\mathrm{ref}}"), "",
     "reference speed and length of a case's normalisation: " + m("U_H") + " and " + m("H") + " (" + m("U_R") + " and " + m("H_R")
     + " in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)", "m/s, m"),
    (m("U_b"), "", "Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table", "m/s"),
    (m("q") + ", " + m(r"c_{\mathrm{gas}}"), "",
     "tracer release of the experiment: volume flow of the released gas, and its tracer content (" + m("10^6") + " ppm when pure); " + m("Q")
     + " is the source strength given to a solve", "m³/s, ppm"),
    (m("R_b"), "", "bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)", "—"),
    (m(r"\mathrm{Re_H}") + ", " + m(r"\mathrm{Re_D}"), "", "Reynolds numbers " + m(r"U_H H/\nu") + " and " + m(r"U_H D/\nu") + " (" + m(r"\nu") + ": kinematic viscosity of air)", "—"),
    (m(r"u_\ast") + ", " + m("z_0") + ", " + m(r"\kappa"), "", "friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)", "m/s, mm, —"),
    (m(r"\mathrm{WD}"), "`wind_direction_deg`",
     "wind direction (each frame says how it is counted); " + m(r"\mathrm{WD_R}") + " is the mean direction of a field run at its reference point (Case M)", "°"),
    (m("x") + ", " + m("y") + ", " + m("z"), "`x`, `y`, `z`",
     "coordinates in the case's frame (" + m("+x") + ", " + m("+y") + " and " + m("+z") + " are the positive directions; each Data page says which way " + m("+x")
     + " points), " + m("z") + " up from the floor of the tunnel or from the ground", "m"),
    (m(r"\mathrm{d}x"), "", "lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of " + m("H") + " (" + m("H/64") + ")", "m"),
    (m("L_r"), "", "reattachment length behind the building, read from a wake line at ground level; reported as " + m("L_r/H"), "m"),
]
# The scores, as bullets: each begins with its own symbol. validation/dispersion_metrics.py is where they are computed.
_SCORES = [
    m("n") + ", the number of pairs scored: the points at which the measured and the modelled value both exist; " + PAIR,
    m(rf"R = \dfrac{{\sum_i (o_i-{O})(p_i-{P})}}{{\sqrt{{\sum_i (o_i-{O})^2 \sum_i (p_i-{P})^2}}}}") + ", Pearson's correlation coefficient of the pairs",
    m("R^2") + ", the square of " + m("R") + ": the share of the variance of the measured values that a straight-line fit to the modelled values "
    "explains, between 0 and 1. It drops the sign of " + m("R") + ", so an anti-correlated model can score a high " + m("R^2") + "; read it beside " + m("R"),
    m(r"\mathrm{FAC2}") + ", the fraction of pairs with " + m(r"0.5 \le p_i/o_i \le 2") + ". The ratio keeps its sign, so a model of the other sign than the "
    "measurement is a miss; for a concentration, a pair with both values at or below the detection limit also counts",
    m(rf"\mathrm{{FB}} = \dfrac{{{O}-{P}}}{{0.5\thinspace({O}+{P})}}") + ", the fractional bias, positive when the model under-predicts. It is undefined (shown as —) "
    "for a signed component unless the measured and the modelled mean are both positive; " + m("R") + ", " + m(r"\mathrm{FAC2}") + ", the hit rate and " + m("n") + " stay",
    m(r"\mathrm{HR}") + ", the hit rate: the fraction of pairs with " + m(HIT_REL) + " or " + m(HIT_ABS) + ", with " + m(rf"{REL} = 0.25") + " and " + m(ABS) + " equal to "
    + m(r"0.05\thinspace U_H") + " for a velocity component, to the detection limit for a concentration, and absent for " + m("k")
    + ". VDI 3783-9 calls the hit rate " + m("q") + " and the tolerances " + m("D") + " and " + m("W") + "; on this site those letters keep their other meanings",
]
# In the API's validation.json and named on the Method page, not in a table of the site.
_API_NOTE = ("NMSE, NAD, MG and VG are in `validation/results/*.json` and in the API's `validation.json`. NMSE and NAD divide by the means like "
             + m(r"\mathrm{FB}") + ", so they are undefined for a signed component unless the measured and the modelled mean are both positive")
NMSE = rf"\mathrm{{NMSE}} = \dfrac{{\overline{{(o-p)^2}}}}{{{O}\thinspace {P}}}"
NAD = rf"\mathrm{{NAD}} = \dfrac{{\overline{{\lvert o-p\rvert}}}}{{{O}+{P}}}"
MG, VG = r"\mathrm{MG} = \exp\overline{(\ln o-\ln p)}", r"\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}"
_SCORES_API = [
    m(NMSE) + ", the normalised mean square error",
    m(NAD) + ", the normalised absolute difference",
    m(MG) + ", the geometric mean bias",
    m(VG) + ", the geometric variance",
]
_SOURCES = ("The scores " + m(r"\mathrm{FB}") + ", " + m(r"\mathrm{FAC2}") + ", " + m(r"\mathrm{NMSE}") + ", " + m(r"\mathrm{NAD}") + ", " + m(r"\mathrm{MG}") + " and "
            + m(r"\mathrm{VG}") + " follow Chang & Hanna (2004); the hit rate follows VDI 3783-9")
_DETECTION = ("The detection limit of a concentration is one value per case, " + m("10^{-3}") + " of the largest measured value. It sets " + m(ABS)
              + " of the hit rate and the both-below rule of " + m(r"\mathrm{FAC2}") + ", and floors the values in " + m(r"\mathrm{MG}") + " and " + m(r"\mathrm{VG}") + ".")
_QUANTITIES = [
    m("U") + ", " + m("V") + " and " + m("W") + " (mean velocity components) over " + m("U_H"),
    m("k") + " (turbulent kinetic energy) over " + m("U_H^2"),
    "the speed " + m(r"\lvert\mathbf{U}\rvert") + " and " + m(r"\sqrt{\lvert\mathbf{U}\rvert^2+2k}") + ", against a thermistor's " + m(r"V_{\mathrm{s}}"),
    m(r"c^\ast = C/c_0") + " (dimensionless concentration) at turbulent Schmidt numbers " + m(r"\mathrm{Sc_t}") + " of 0.3, 0.5 and 0.7",
    m(r"\theta") + " (floor-referenced temperature)",
]
# The legend under a table of scores: one line per score.
_LEGEND = [
    m("n") + " — number of pairs of a measured value " + m("o_i") + " and a modelled value " + m("p_i") + " at one point",
    m("R") + " — Pearson correlation coefficient of the pairs",
    m("R^2") + " — square of " + m("R") + ": share of the measured variance a linear fit to the model explains",
    m(r"\mathrm{FAC2}") + " — fraction of pairs with " + m(r"0.5 \le p_i/o_i \le 2"),
    m(r"\mathrm{FB}") + " — fractional bias " + m(FB) + ", positive when the model is low",
    m(r"\mathrm{HR}") + " (hit rate) — fraction of pairs with " + m(HIT_REL) + " or " + m(HIT_ABS) + ", where " + m(rf"{REL} = 0.25") + " and "
    + m(rf"{ABS} = 0.05\thinspace U_H") + " for a velocity component",
]
_LEGEND_API = [
    m(NMSE) + " — normalised mean square error",
    m(NAD) + " — normalised absolute difference",
    m(MG) + " — geometric mean bias",
    m(VG) + " — geometric variance",
]
_LEGEND_NOTES = [
    "The ratio of " + m(r"\mathrm{FAC2}") + " keeps its sign, so a model of the other sign than the measurement is a miss; " + m(r"\mathrm{FB}") + ", " + m(r"\mathrm{NMSE}")
    + " and " + m(r"\mathrm{NAD}") + " divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive",
    "VDI 3783-9 calls the hit rate " + m("q") + " and the tolerances " + m("D") + " and " + m("W") + "; on this site those letters keep their other meanings (" + m("q")
    + " the tracer release rate, " + m("D") + " the block size of Case C, " + m("W") + " the vertical velocity)",
]


# ----------------------------------------------------------------------------- the three texts

def _meta(column, unit):
    """` (columns `x`, `y`; m/s)`: the table columns an entry stands for and its unit, or nothing."""
    parts = []
    if column:
        parts.append(("columns " if column.count("`") > 2 else "column ") + column)
    if unit:
        parts.append(", ".join("dimensionless" if u.strip() == "—" else u.strip() for u in unit.split(",")))
    return " (" + "; ".join(parts) + ")" if parts else ""


def _bullets(rows):
    """The entries as bullet points: `- symbols (columns; unit) — meaning`."""
    return [f"- {s}{_meta(c, u)} — {t}" for s, c, t, u in rows]


def _details(summary, body):
    return [f'<details{" open" if OPEN else ""} markdown="block">', f"  <summary>{summary}</summary>", ""] + body + ["", "</details>"]


def metrics():
    """Every score with its formula: the Metrics section of the Method page and the README, and the last group of the nomenclature."""
    return [f"- {t}." for t in _SCORES + [_API_NOTE] + _SCORES_API] + ["- " + _DETECTION, f"- {_SOURCES}."]


def full():
    """Every symbol, column and score, as bullet points in a <details>."""
    L = ["**Geometry, reference scales and release**", ""] + _bullets(_SCALES)
    L += ["", "**Velocity and turbulence**", ""] + _bullets(_VELOCITY)
    L += ["", "**Concentration and temperature**", ""] + _bullets(_SCALARS)
    L += ["", "**Scores**", ""] + [f"- {t}" for t in _LEGEND + _LEGEND_API + _LEGEND_NOTES] + ["- " + _DETECTION, f"- {_SOURCES}."]
    L += ["", "**Quantities scored**", ""] + [f"- {t}" for t in _QUANTITIES]
    return _details("Nomenclature: symbols, columns and scores", L)


def scores():
    """The scores as bullet points, and the quantities they are computed on: under a table of scores."""
    return (["**Nomenclature**", ""] + [f"- {t}" for t in _LEGEND] + ["", "**Quantities scored**", ""] + [f"- {t}" for t in _QUANTITIES])


KINDS = {"full": full, "scores": scores, "metrics": metrics}
# The file a docs page includes for each kind.
INCLUDES = {"full": "nomenclature.md", "scores": "nomenclature-scores.md", "metrics": "metrics.md"}
GENERATED = "<!-- Generated by scripts/build_api.py from scripts/nomenclature.py. -->"


def include_text(kind):
    """The text of docs/_includes/<INCLUDES[kind]>."""
    return "\n".join([GENERATED, ""] + KINDS[kind]()) + "\n"


# A block of a README file: the same text between markers, for the files GitHub renders without Jekyll.
BLOCK = re.compile(r"<!--nomenclature (full|scores|metrics)-->\n.*?\n<!--/nomenclature-->", re.S)


def block(kind):
    return "\n".join([f"<!--nomenclature {kind}-->", ""] + KINDS[kind]() + ["", "<!--/nomenclature-->"])


def with_blocks(text):
    """`text` with each README block rewritten from the entries."""
    return BLOCK.sub(lambda mt: block(mt.group(1)), text)
