"""Where the tunnel measured: the measurement lines and planes of every AIJ UWE case, as groups and as a figure.

Every row of clean/cases/<X>/points.csv belongs to exactly one GROUP: a set of points the tunnel took along one line or
in one plane (a vertical section, a horizontal plane, a set of vertical profiles). The groups are DERIVED from the
coordinates, not listed point by point: a group is a rule over (x, y, z) (and, where one table holds two instruments, the
instrument), written once per case below with the numbers of the tunnel's own drawings (MP_*.png) and the data paper
(sections 3.1 to 3.13). The same groups colour the scatter dots of the agreement figures and draw the layout figure, so
a dot in one figure is found in the other by its colour and its letter.

Public names (other scripts import them; keep them stable):

  rows(case)                      the cleaned point table of a case, as dicts {x, y, z, instrument, config, point_id, ...}
  groups(case)                    [Group]: letter, label, short, kind, colour, members (row indices), the lines and planes
  classify(case, row, instrument=None)   the index of the group a row belongs to; raises unless exactly one rule matches
  grouped_colours(case, rows, instrument=None)   one colour per row, for the scatter dots of an agreement figure
  legend_handles(case, instrument=None)   handles for fig.legend / ps.finish: a circled letter in the group colour per group
  layout_figure(case, geometry=None)      the figure: (a) elevation x-z, (b) plan x-y, groups lettered and coloured
  check_group_palette()           the group colours are the plotstyle cycle, and tell apart under every colour vision

Phase-2 contract (the district cases C, D, E, F, M): add one function `_groups_<x>(ctx)` returning a list of Spec, register
it in SPECS, give the case a UNITS entry, and, for a case whose geometry is not a set of boxes, pass the geometry to
layout_figure(case, geometry=Geometry(tris=read_stl(path)), wind=False). The tests in test_layout.py then cover the
new case as soon as it is in SPECS (add its expected sizes to EXPECTED and TOTAL there). geometry(case, configuration) reads the boxes
of A-D and G-L; a triangle mesh is drawn undirected: roofs and floors fill the plan, walls the elevation, winding is never read.

The module is standard library only up to `layout_figure`; matplotlib is imported when a figure is drawn, so the group
tests run anywhere. Group kinds:

  profiles   vertical lines (x, y fixed, z varies): dotted verticals in the elevation, one dot per line in the plan;
             `trace` marks the groups that are a vertical SECTION (one y): a dotted line at that y in the plan
  plane      a horizontal plane (z fixed): a dotted horizontal in the elevation, dots and an outline in the plan
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CASES_DIR = os.path.join(REPO, "clean", "cases")

TOL = 1e-6   # coordinates match within a micrometre (model scale) or a micrometre of a full-scale metre; the table is rounded to 1e-9

# The plotstyle categorical cycle in the order the groups take it: blue, vermillion, green, reddish purple, sky blue, then ink
# and the cycle's yellow, which only the cases with six or seven groups reach. check_group_palette() ties these to plotstyle.
GROUP_COLOURS = ("#0072b2", "#d55e00", "#009e73", "#cc79a7", "#56b4e9", "#1a1a1a", "#f0e442")
MAX_GROUPS = len(GROUP_COLOURS)

# length unit of each case: (symbol, metres, scale note). The symbols are the data paper's: A uses b, the rest H.
UNITS = {
    "A": ("b", 0.08, "b = 0.08 m, H = 2b"),
    "B": ("H", 0.20, "H = 0.2 m"),
    "G": ("H", 7.0, "H = 7 m, full scale"),
    "H": ("H", 0.20, "H = 0.2 m"),
    "I": ("H", 0.10, "H = 0.1 m"),
    "J": ("H", 0.16, "H = 0.16 m"),
    "K": ("H", 0.06, "H = 0.06 m"),
    "L": ("H", 0.06, "H = 0.06 m"),
}

# What the points do not show and the geometry would hide: the published half, the part of the geometry outside the frame.
NOTES = {
    "A": "points published for y ≤ 0",
    "B": "points published for y ≤ 0",
    "G": "belt 74 m long, y = ±37 m",
    "K": "9 × 9 cubes, cut at the frame",
    "L": "9 × 14 cubes, cut at the frame",
}

# The gas release, from clean/cases/<X>/geometry.json: ('point', (x, y, z)) or ('line', (x0, y0), (x1, y1)) on the floor.
SOURCES = {
    "H": [("point", (0.05, 0.0, 0.0))],
    "I": [("point", (0.0, 0.0, 0.1))],
    "J": [("point", (0.04, 0.0, 0.0))],
    "K": [("point", (-0.15, 0.0, 0.0))],
    "L": [("line", (-0.15, -0.51), (-0.15, 0.51))],
}


# ----------------------------------------------------------------------------- the table

_ROWS: dict[str, list[dict]] = {}
_NUMERIC = ("x", "y", "z", "wind_direction_deg")


def rows(case):
    """The cleaned point table of `case` (clean/cases/<case>/points.csv) as dicts; coordinates are floats."""
    if case not in _ROWS:
        out = []
        with io.open(os.path.join(CASES_DIR, case, "points.csv"), encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                d = {k: r[k] for k in ("case_id", "config", "instrument", "point_id")}
                for k in _NUMERIC:
                    d[k] = float(r[k]) if r[k] != "" else math.nan
                out.append(d)
        _ROWS[case] = out
    return _ROWS[case]


def _key(x, y):
    return (round(x, 6), round(y, 6))


class Ctx:
    """What a rule may ask besides the row itself: the case, its length unit, the heights measured at a location."""

    def __init__(self, case):
        self.case = case
        self.sym, self.unit, _ = UNITS[case]
        self._heights = {}
        for r in rows(case):
            self._heights.setdefault(_key(r["x"], r["y"]), set()).add(round(r["z"], 6))

    def heights(self, row):
        """The z values at the row's (x, y) over the whole table: how many heights its vertical profile has."""
        return self._heights[_key(row["x"], row["y"])]


@dataclass(frozen=True)
class Spec:
    """One group, as a rule. `test(row, ctx)` is true for the rows in it; the rules of a case must not overlap."""
    kind: str                      # 'profiles' or 'plane'
    label: str                     # for the layout figure's legend
    short: str                     # for an agreement figure's legend
    test: Callable[[dict, "Ctx"], bool]
    trace: bool = False            # profiles in one vertical section: draw its trace (a line at y) in the plan


def _g(v):
    return f"{abs(v):.4g}" if abs(v) > 1e-12 else "0"


def _near(a, b):
    return abs(a - b) < TOL


def _section(ctx, *ys, extra=None, name="vertical profiles"):
    """Vertical profiles in the plane(s) y = ys (a pair +-y when two values): the tunnel's vertical section."""
    sym, unit = ctx.sym, ctx.unit
    vals = sorted({abs(v) / unit for v in ys})
    pm = len(ys) > 1 and len(vals) == 1
    txt = ("±" if pm else "") + (_g(vals[0]) if len(vals) == 1 else ", ".join(_g(v / unit) for v in sorted(ys)))
    at = f"y/{sym} = {txt}"
    kw = (lambda r, c: any(_near(r["y"], v) for v in ys) and (extra is None or extra(r, c)))
    return Spec("profiles", f"{name}, {at}", f"section {at}", kw, trace=True)


def _plane(ctx, z, *, off_section=True, extra=None, name="plane"):
    """A horizontal plane z = const. Where a vertical section crosses it, the points ON the section belong to the section."""
    sym = ctx.sym
    at = f"z/{sym} = {_g(z / ctx.unit)}"
    return Spec("plane", f"{name} {at}", f"{name} {at}",
                lambda r, c: _near(r["z"], z) and (not off_section or not _near(r["y"], 0.0)) and (extra is None or extra(r, c)))


def _only(instrument):
    return lambda r, c: r["instrument"] == instrument


# ----------------------------------------------------------------------------- the rules, one case at a time

def _groups_a(ctx):
    """A: 186 points on the vertical section y/b = 0 and on the horizontal planes z/b = 0.125 and 1.25 (y <= 0 published)."""
    return [_section(ctx, 0.0), _plane(ctx, 0.01), _plane(ctx, 0.10)]


def _groups_b(ctx):
    """B: 224 points on the vertical section y/H = 0 and on the horizontal plane z/H = 1/16 (0.0125 m), y <= 0 published."""
    return [_section(ctx, 0.0), _plane(ctx, 0.0125)]


def _groups_g(ctx):
    """G: seven lines behind the belt, at 0.25H, 0.5H, 1H, 2H, 3H, 4H and 5H (H = 7 m), four sonic heights each."""
    out = []
    for x in (1.75, 3.5, 7.0, 14.0, 21.0, 28.0, 35.0):
        at = f"x/H = {_g(x / ctx.unit)}"
        out.append(Spec("profiles", f"vertical profile, {at}", f"profile {at}", (lambda r, c, x=x: _near(r["x"], x))))
    return out


def _groups_h(ctx):
    """H: the section y/H = 0 and the planes z/H = 0.0625, 0.25 and 0.5, each read by the sonic probe and the analyser."""
    return [_section(ctx, 0.0), _plane(ctx, 0.0125), _plane(ctx, 0.05), _plane(ctx, 0.10)]


def _groups_i(ctx):
    """I: the concentration section y/H = 0 and ground plane z/H = 0; the velocity section y/H = 0 and plane z/H = 0.5."""
    c, v = "hydrocarbon_analyser", "ldv"
    return [_quantity(_section(ctx, 0.0, extra=_only(c)), "concentration", "conc."),
            _quantity(_plane(ctx, 0.0, extra=_only(c)), "concentration", "conc."),
            _quantity(_section(ctx, 0.0, extra=_only(v)), "velocity", "vel."),
            _quantity(_plane(ctx, 0.05, extra=_only(v)), "velocity", "vel.")]


def _quantity(spec, quantity, abbreviation):
    """`spec` with the measured quantity in front of its labels: 'concentration, vertical profiles, y/H = 0'."""
    return Spec(spec.kind, f"{quantity}, {spec.label}", f"{abbreviation} {spec.short}", spec.test, spec.trace)


def _groups_j(ctx):
    """J: the section y/H = 0 and the planes z/H = 0.025 (0.004 m) and 0.25 (0.04 m)."""
    return [_section(ctx, 0.0), _plane(ctx, 0.004), _plane(ctx, 0.04)]


def _groups_k(ctx):
    """K: vertical sections at y/H = 0, +-1, +-2 and +-3 through the 9 x 9 cube array (cube H = 0.06 m)."""
    return [_section(ctx, 0.0), _section(ctx, 0.06, -0.06), _section(ctx, 0.12, -0.12), _section(ctx, 0.18, -0.18)]


def _groups_l(ctx):
    """L: 65 vertical profiles in three classes (data paper 3.12.1): 27 near the source in the street, 8 heights between
    4 and 150 mm; 14 above the roofs of the blocks, 4 heights between 70 and 150 mm; 24 in the surrounding streets, 3 heights
    between 4 and 30 mm. The class of a profile is how many heights it has."""
    def n(k):
        return lambda r, c: len(c.heights(r)) == k
    return [Spec("profiles", "street profiles near the source, 8 heights", "near source", n(8)),
            Spec("profiles", "profiles above the roofs, 4 heights", "above roofs", n(4)),
            Spec("profiles", "street profiles around, 3 heights", "surrounding", n(3))]


SPECS = {"A": _groups_a, "B": _groups_b, "G": _groups_g, "H": _groups_h, "I": _groups_i, "J": _groups_j, "K": _groups_k,
         "L": _groups_l}


# ----------------------------------------------------------------------------- groups

@dataclass
class Group:
    letter: str
    label: str
    short: str
    kind: str
    colour: str
    trace: bool
    members: list = field(default_factory=list)     # row indices into rows(case)
    xs: list = field(default_factory=list)          # distinct x, y, z of the members, rounded to a micrometre
    ys: list = field(default_factory=list)
    zs: list = field(default_factory=list)

    @property
    def n(self):
        return len(self.members)


_CTX: dict[str, Ctx] = {}
_GROUPS: dict[str, list] = {}


def _ctx(case):
    if case not in _CTX:
        _CTX[case] = Ctx(case)
    return _CTX[case]


def specs(case):
    if case not in SPECS:
        raise KeyError(f"no measurement groups for case {case}: add _groups_{case.lower()} to layout.SPECS")
    out = SPECS[case](_ctx(case))
    assert 1 <= len(out) <= MAX_GROUPS, (case, len(out))
    return out


def classify(case, row, instrument=None):
    """The index of the group `row` ({x, y, z[, instrument]}) belongs to. Raises unless exactly one rule matches it.
    A coordinate the row lacks is NaN, which no rule matches (Case G's pairs carry x and z only: its rules read x)."""
    r = {"x": math.nan, "y": math.nan, "z": math.nan, "instrument": None}
    r.update(row)
    if instrument is not None:
        r["instrument"] = instrument
    hit = [i for i, s in enumerate(specs(case)) if s.test(r, _ctx(case))]
    if len(hit) != 1:
        raise ValueError(f"case {case}: ({r['x']}, {r['y']}, {r['z']}, {r['instrument']}) matches groups {hit}, not exactly one")
    return hit[0]


def groups(case):
    """The groups of `case` with their members, in letter order (A, B, ...)."""
    if case not in _GROUPS:
        sp, ctx = specs(case), _ctx(case)
        gs = [Group("ABCDEFG"[i], s.label, s.short, s.kind, GROUP_COLOURS[i], s.trace) for i, s in enumerate(sp)]
        for i, r in enumerate(rows(case)):
            hit = [j for j, s in enumerate(sp) if s.test(r, ctx)]
            if len(hit) != 1:
                raise ValueError(f"case {case} row {i} (point {r['point_id']}, {r['instrument']}): groups {hit}, not exactly one")
            gs[hit[0]].members.append(i)
        tab = rows(case)
        for g in gs:
            for axis, name in (("x", "xs"), ("y", "ys"), ("z", "zs")):
                setattr(g, name, sorted({round(tab[i][axis], 6) for i in g.members}))
        _GROUPS[case] = gs
    return _GROUPS[case]


def caption(case):
    """The figure caption of case-<x>-layout.png: the groups by letter, then the unit the positions are in."""
    sym, unit, _ = UNITS[case]
    gs = groups(case)
    if all(g.kind == "profiles" and len(g.xs) == 1 for g in gs) and len(gs) > 3:       # Case G: seven lines, one x each
        what = f"{gs[0].letter} to {gs[-1].letter} vertical profiles, x/{sym} = " + ", ".join(_g(g.xs[0] / unit) for g in gs)
    else:
        what = "; ".join(f"{g.letter} {g.label}" for g in gs)
    text = f"Case {case}, measurement lines and planes: {what}. Positions in multiples of {sym}"
    if case in ZOOM:
        lo, hi = ZOOM[case][0] / unit, ZOOM[case][1] / unit
        text += f"; panels c and d: x/{sym} = {'-' if lo < 0 else ''}{_g(lo)} to {_g(hi)}"
    return text + "."


def grouped_colours(case, rows_, instrument=None):
    """One colour per row of an agreement figure's scatter: `rows_` are dicts with x, y, z (and instrument, or pass it)."""
    gs = groups(case)
    return [gs[classify(case, r, instrument)].colour for r in rows_]


def grouped_index(case, rows_, instrument=None):
    """The group index per row, for scripts that draw one scatter call per group."""
    return [classify(case, r, instrument) for r in rows_]


# ----------------------------------------------------------------------------- geometry

@dataclass
class Geometry:
    """What the figure draws of the case: axis-aligned boxes (lo, hi) and/or triangles (3 x (x, y, z)); `focus` boxes are the subject."""
    boxes: list = field(default_factory=list)
    tris: list = field(default_factory=list)
    focus: bool = True


def geometry(case, configuration=None):
    """The boxes of clean/cases/<case>/geometry.json (cases A-D and G-L publish them) of one configuration (the first when None);
    a case without boxes raises KeyError: pass geometry=Geometry(tris=read_stl(...)) to layout_figure."""
    with io.open(os.path.join(CASES_DIR, case, "geometry.json"), encoding="utf-8") as f:
        meta = json.load(f)
    files = [e for e in meta["files"] if configuration in (None, e.get("configuration"))]
    boxes = files[0].get("boxes") if files else None
    if not boxes:
        raise KeyError(f"case {case} publishes no boxes (configuration {configuration}): pass geometry=Geometry(tris=read_stl(...)) to layout_figure")
    return Geometry(boxes=[(tuple(b["min"]), tuple(b["max"])) for b in boxes], focus=len(boxes) == 1)


def read_stl(path):
    """The triangles of an ASCII STL as ((x, y, z) x 3), in file order. Neither the facet normals nor the winding are read: the
    figure projects every triangle undirected (the plan fills roofs and floors, the elevation every wall), so a mesh whose
    winding or closure is wrong draws the same."""
    tris, cur = [], []
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            t = line.split()
            if t and t[0] == "vertex":
                cur.append((float(t[1]), float(t[2]), float(t[3])))
                if len(cur) == 3:
                    tris.append(tuple(cur))
                    cur = []
    return tris


def approach_flow(case):
    """[(z, U)] of the approach flow in the case frame, ascending in z (clean/cases/<case>/approach_flow.csv)."""
    out = []
    with io.open(os.path.join(CASES_DIR, case, "approach_flow.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["U"] != "":
                out.append((float(r["z"]), float(r["U"])))
    return sorted(out)


def mult(v, sym):
    """`v` in multiples of the unit `sym`, as the thesis labels its lines: 0 -> '0', 2 -> '2H', 0.25 -> 'H/4', -0.375 -> '-3H/8', 1.9 -> '1.9H'."""
    f = Fraction(v).limit_denominator(25)
    if abs(float(f) - v) < 1e-6 and f.denominator in (1, 2, 3, 4, 5, 6, 8, 12, 16, 25):
        n, d = abs(f.numerator), f.denominator
        if n == 0:
            return "0"
        head = "-" if f < 0 else ""
        return f"{head}{'' if n == 1 else n}{sym}" + (f"/{d}" if d > 1 else "")
    return f"{v:.3g}{sym}"


# ----------------------------------------------------------------------------- the figure

FIG_WIDTH = 7.6        # inches: the width of the figure; every length below is inches too, so the text keeps its size
AX_WIDTH = 6.65        # the widest the two panels get
LEFT, RIGHT = 0.62, 0.30
TICK_PT, LABEL_PT, LETTER_PT = 7.2, 7.6, 7.4
ROW_IN = 0.15          # height of one row of station labels
DOT = (11.0, 7.0, 4.0, 2.6)   # marker area [pt^2] by density class: few, some, many, very many points
DOTTED = (0, (1.0, 2.2))


def check_group_palette():
    """The group colours are plotstyle's cycle (then ink and yellow) and every pair differs by MIN_DELTA_E under every vision."""
    import itertools
    import plotstyle as ps
    from matplotlib.colors import to_hex
    import ultraplot as uplt
    cycle = [to_hex(d["color"]) for d in uplt.Cycle("colorblind")]
    assert list(GROUP_COLOURS[:5]) == [cycle[0], cycle[1], cycle[2], cycle[3], cycle[5]], (GROUP_COLOURS, cycle)
    assert GROUP_COLOURS[5] == ps.INK and GROUP_COLOURS[6] == cycle[4], GROUP_COLOURS
    for a, b in itertools.combinations(GROUP_COLOURS, 2):
        for v in ps.VISIONS:
            assert ps.delta_e(a, b, v) >= 15.0, (a, b, v, ps.delta_e(a, b, v))


def _dots(rank, of):
    """A dotted line style that interleaves with `of` other lines drawn over the same path: dot k of every `of`."""
    return (3.2 * rank, (1.0, 3.2 * of - 1.0))


def _area(dot, rank):
    """Marker area of the group of the given rank: the first group's dots are the largest, later ones sit smaller on top."""
    return dot * max(2.0 * 0.62 ** rank, 0.4)


def _dark(colour, f=0.62):
    from matplotlib.colors import to_rgb
    return tuple(round(c * f, 4) for c in to_rgb(colour))


class GroupHandle:
    """A legend handle for one group: a circled letter in the group's colour. Built by legend_handles()."""
    def __init__(self, letter, colour, label):
        self.letter, self.colour, self._label = letter, colour, label

    def get_label(self):
        return self._label


_HANDLER_DONE = []


def _letter_handler():
    """Register how a legend draws a GroupHandle (once)."""
    if _HANDLER_DONE:
        return
    from matplotlib.legend import Legend
    from matplotlib.legend_handler import HandlerBase
    from matplotlib.patches import Ellipse
    from matplotlib.text import Text

    class _H(HandlerBase):
        def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
            cx, cy = xdescent + width / 2.0, ydescent + height / 2.0
            d = fontsize * 1.28
            ring = Ellipse((cx, cy), d, d, facecolor="white", edgecolor=orig_handle.colour, linewidth=1.5, transform=trans)
            txt = Text(cx, cy - 0.02 * fontsize, orig_handle.letter, ha="center", va="center", fontsize=fontsize * 0.78,
                       fontweight="bold", color="#1a1a1a", transform=trans)
            return [ring, txt]

    Legend.update_default_handler_map({GroupHandle: _H()})
    _HANDLER_DONE.append(1)


def legend_handles(case, instrument=None, short=True, prefix=None):
    """Handles for fig.legend / plotstyle.finish: one circled letter per group, labelled with the group's short (or long) text,
    after `prefix` ('H: section y/H = 0') where one figure draws several cases. `instrument` keeps the groups of that instrument only."""
    _letter_handler()
    keep = _groups_of(case, instrument)
    return [GroupHandle(g.letter, g.colour, (f"{prefix}: " if prefix else "") + (g.short if short else g.label)) for g in keep]


def _groups_of(case, instrument=None):
    gs = groups(case)
    if instrument is None:
        return gs
    sp = specs(case)
    probe = [i for i, g in enumerate(gs) if any(rows(case)[m]["instrument"] == instrument for m in g.members)]
    return [gs[i] for i in probe]


def _renderer():
    """An Agg renderer at 1200 dpi, to measure text in inches before the figure exists."""
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    fig = Figure(dpi=1200)
    return FigureCanvasAgg(fig).get_renderer()


def letters_above(ax, case, xs):
    """Circled group letters above the top edge of `ax` at the data x positions `xs`, one per group of `case` in letter order;
    two letters closer than a twentieth of the axis are moved 5 pt apart so that their rings do not touch."""
    import plotstyle as ps
    lo, hi = ax.get_xlim()
    dx = [0.0] * len(xs)
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] < 0.05 * (hi - lo):
            dx[i - 1], dx[i] = dx[i - 1] - 5.0, dx[i] + 5.0
    for g, x, off in zip(groups(case), xs, dx):
        ax.annotate(g.letter, xy=(x, 1.0), xycoords=ax.get_xaxis_transform(), xytext=(off, 9), textcoords="offset points", ha="center",
                    va="center", fontsize=LETTER_PT, fontweight="bold", color=ps.INK, annotation_clip=False,
                    bbox=dict(boxstyle="circle,pad=0.28", facecolor=ps.SURFACE, edgecolor=g.colour, linewidth=1.5))


def _text_size(renderer, s, size, weight="normal"):
    from matplotlib.font_manager import FontProperties
    w, h, d = renderer.get_text_width_height_descent(s, FontProperties(size=size, weight=weight), False)
    return w / renderer.dpi, h / renderer.dpi


def _pack(items, gap):
    """Rows for labels centred at x [in] of width w [in]: the lowest row where one fits clear of the others. items: [(x, w)]."""
    rows_, end = [], []
    for x, w in sorted(items):
        for r, e in enumerate(end):
            if x - w / 2 >= e + gap:
                end[r] = x + w / 2
                rows_.append((x, r))
                break
        else:
            end.append(x + w / 2)
            rows_.append((x, len(end) - 1))
    return {x: r for x, r in rows_}, len(end)


def _spread(ys, gap):
    """Positions as near as possible to `ys` that are at least `gap` apart, in the order of `ys`."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = [0.0] * len(ys)
    prev = -1e9
    for i in order:
        out[i] = max(ys[i], prev + gap)
        prev = out[i]
    # centre each pushed run on what it wanted: shift the whole set back by half the mean displacement
    shift = sum(out[i] - ys[i] for i in range(len(ys))) / (2.0 * len(ys))
    return [round(v - shift, 6) for v in out]


def _arrow(ax, p0, p1, head, half, colour, lw, z=4):
    """An arrow as a line and a filled triangle (head, half in data units): arrows from FancyArrowPatch differ between CPUs."""
    from matplotlib.patches import Polygon
    x0, y0 = round(p0[0], 6), round(p0[1], 6)
    x1, y1 = round(p1[0], 6), round(p1[1], 6)
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    bx, by = x1 - ux * head, y1 - uy * head
    ax.plot([x0, bx], [y0, by], color=colour, lw=lw, solid_capstyle="butt", zorder=z, clip_on=False)
    ax.add_patch(Polygon([(x1, y1), (bx - uy * half, by + ux * half), (bx + uy * half, by - ux * half)], closed=True,
                         facecolor=colour, edgecolor="none", zorder=z, clip_on=False))


def _ring(ax, x, y, r, letter, colour, z=8):
    from matplotlib.patches import Circle
    ax.add_patch(Circle((round(x, 6), round(y, 6)), r, facecolor="white", edgecolor=colour, linewidth=1.5, zorder=z, clip_on=False))
    ax.text(round(x, 6), round(y, 6), letter, ha="center", va="center_baseline", fontsize=LETTER_PT, fontweight="bold", color="#1a1a1a",
            zorder=z + 1, clip_on=False)


# One panel pair (elevation above plan) shows a window of x. The first pair shows everything; a case whose data spans a
# hundred building heights (I) gets a second pair on the near field, where its lines are a tenth of a height apart.
ZOOM = {"I": (-0.2, 0.5)}


class _View:
    """The members of one group inside an x window: what a panel pair draws of it."""

    def __init__(self, g, tab, win):
        self.g = g
        self.idx = [i for i in g.members if win is None or win[0] - TOL <= tab[i]["x"] <= win[1] + TOL]
        self.xs = sorted({round(tab[i]["x"], 6) for i in self.idx})
        self.ys = sorted({round(tab[i]["y"], 6) for i in self.idx})
        self.zs = sorted({round(tab[i]["z"], 6) for i in self.idx})


class _Pair:
    """Sizes of one panel pair, all in inches except the data limits; made before the figure exists, so its height is known."""

    def __init__(self, case, gs, tab, geo, win, renderer, wind=True):
        sym, unit, _ = UNITS[case]
        self.win, self.sym, self.unit, self.wind = win, sym, unit, wind
        self.views = [v for v in (_View(g, tab, win) for g in gs) if v.idx]
        vs = self.views
        x_lo, x_hi = min(v.xs[0] for v in vs), max(v.xs[-1] for v in vs)
        y_lo, y_hi, z_hi = min(v.ys[0] for v in vs), max(v.ys[-1] for v in vs), max(v.zs[-1] for v in vs)
        if win is not None:
            x_lo, x_hi = win
        reach = 0.15 * (x_hi - x_lo)      # a long building (the 74 m belt of G) is cut where it is this far from the points in y
        y_d = (y_lo, y_hi)
        for lo, hi in geo.boxes if geo.focus else []:
            if win is None or (hi[0] >= x_lo - TOL and lo[0] <= x_hi + TOL):
                x_lo, x_hi = min(x_lo, lo[0]), max(x_hi, hi[0])
                y_lo, y_hi, z_hi = min(y_lo, max(lo[1], y_d[0] - reach)), max(y_hi, min(hi[1], y_d[1] + reach)), max(z_hi, hi[2])
        z_hi = max([z_hi] + [1.6 * max(hi[2] for _, hi in geo.boxes)] if geo.boxes else [z_hi])
        self.boxes = [(lo, hi) for lo, hi in geo.boxes if hi[0] >= x_lo - TOL and lo[0] <= x_hi + TOL]
        self.tris = []
        if geo.tris:          # a mesh sets the height of the elevation up to a third of the width of the window
            import numpy as np
            t = np.asarray(geo.tris, float)
            self.tris = t[(t[:, :, 0].max(axis=1) >= x_lo - TOL) & (t[:, :, 0].min(axis=1) <= x_hi + TOL)]
            if len(self.tris):
                z_hi = max(z_hi, min(float(self.tris[:, :, 2].max()), (x_hi - x_lo) / 3.0))
        self.x_lo, self.x_hi, self.z_hi = x_lo, x_hi, z_hi
        span = x_hi - x_lo
        planes = [v for v in vs if v.g.kind == "plane"]
        self.pad_l = 0.80 if wind else 0.35
        self.pad_r = 0.55 + max([_text_size(renderer, v.g.short, LABEL_PT)[0] for v in planes if self.labelled(v)] + [0.0])
        n_pts = len({(round(tab[i]["x"], 6), round(tab[i]["y"], 6), round(tab[i]["z"], 6)) for v in vs for i in v.idx})
        self.dot = DOT[0 if n_pts < 150 else 1 if n_pts < 400 else 2 if n_pts < 900 else 3]
        self.z_view = z_hi * 1.08
        y_pad = max(0.2 * (y_hi - y_lo), 0.07 * (span + (self.pad_l + self.pad_r) / 14.0))
        self.y_a, self.y_b = y_lo - y_pad, y_hi + y_pad
        self.scale = round(min((AX_WIDTH - self.pad_l - self.pad_r) / span, 3.0 / self.z_view, 3.6 / (self.y_b - self.y_a)), 4)
        self.ax_w = self.pad_l + self.pad_r + span * self.scale
        self.stations = sorted({x for v in vs if v.g.kind == "profiles" for x in v.xs})
        self.labels = {x: mult(x / unit, sym) for x in self.stations}
        self.x_in = {x: self.pad_l + (x - x_lo) * self.scale for x in self.stations}
        self.row_of, n_rows = _pack([(self.x_in[x], _text_size(renderer, self.labels[x], TICK_PT)[0]) for x in self.stations], 0.05)
        self.band = (n_rows * ROW_IN + 0.10) if self.stations else 0.0
        self.h_e = self.z_view * self.scale + self.band
        self.h_p = (self.y_b - self.y_a) * self.scale

    def labelled(self, v):
        """A plane's label is written beside it unless the plane is a small part of the window (then its letter and the legend say it)."""
        return (v.xs[-1] - v.xs[0]) >= 0.2 * (self.x_hi - self.x_lo) if hasattr(self, "x_hi") else True


def layout_figure(case, geometry=None, zoom=None, wind=True):
    """The measurement layout of `case`: (a) elevation x-z with the vertical profiles and the planes, (b) plan x-y with every
    measured position; groups lettered and coloured as in grouped_colours(). Drawn in the thesis style: line art, dotted
    sample lines labelled in multiples of the unit, circled letters, axis arrows, the approach flow as arrows at the left,
    the unit in a note. `zoom` = (x0, x1) [m] adds a pair of panels on that window (default ZOOM[case]; False for none). `wind=False`
    leaves out the approach flow and the wind arrow, for a case whose wind blows from many directions (E, F, M).
    Returns the matplotlib figure; write it with plotstyle.save()."""
    import plotstyle as ps
    from matplotlib.figure import Figure

    check_group_palette()
    ps.apply()
    gs, tab = groups(case), rows(case)
    sym, unit, note = UNITS[case]
    geo = geometry or globals()["geometry"](case)
    zoom = ZOOM.get(case) if zoom is None else (zoom or None)
    renderer = _renderer()
    pairs = [_Pair(case, gs, tab, geo, win, renderer, wind) for win in [None] + ([zoom] if zoom else [])]
    handles = legend_handles(case, short=False)
    chars = sum(len(h.get_label()) for h in handles)
    ncols = len(handles) if chars <= 92 else 2 if len(handles) > 2 else 1
    leg_h = 0.26 * math.ceil(len(handles) / ncols) + 0.10
    bottom, gap_panels, gap_pairs, top = 0.14 + leg_h + 0.30, 0.78, 0.62, 0.62
    fig_h = bottom + sum(p.h_p + gap_panels + p.h_e for p in pairs) + gap_pairs * (len(pairs) - 1) + top
    fig = Figure(figsize=(FIG_WIDTH, fig_h), dpi=ps.DPI)
    fig.patch.set_facecolor(ps.SURFACE)
    y = bottom
    for k in reversed(range(len(pairs))):      # the first pair is the top one, so the bottom one is placed first
        p = pairs[k]
        _draw_pair(fig, fig_h, case, p, tab, geo, y, "abcd"[2 * k:2 * k + 2])
        y += p.h_p + gap_panels + p.h_e + gap_pairs
    ax_w = pairs[-1].ax_w
    fig.text(0.5, 1 - 0.30 / fig_h, f"AIJ UWE Case {case} — measurement lines and planes", ha="center", va="center", fontsize=13,
             fontweight="bold", color=ps.INK)
    scale_txt = note + ("; " + NOTES[case] if case in NOTES else "")
    fig.text((LEFT + pairs[0].ax_w) / FIG_WIDTH, (bottom - 0.12) / fig_h, scale_txt, ha="right", va="top", fontsize=LABEL_PT + 0.4, color=ps.INK)
    fig.legend(handles=handles, loc="lower center", ncols=ncols, frameon=False, fontsize=LABEL_PT + 1.4, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.5, handletextpad=0.5, columnspacing=1.8, labelspacing=0.55, borderaxespad=0.15)
    return fig


def _draw_pair(fig, fig_h, case, p, tab, geo, bottom, letters):
    """Draw one panel pair of the layout figure; `bottom` is the lower edge of its plan panel, in inches from the figure's bottom."""
    import plotstyle as ps
    from matplotlib.patches import Rectangle

    ink, ref = ps.INK, ps.REFERENCE
    body = ps.FOOTPRINT_FOCUS if geo.focus else ps.FOOTPRINT
    sym, unit = p.sym, p.unit
    scale, vs = p.scale, p.views
    inch = 1.0 / scale                      # one inch in data units, in both panels

    def axes_at(b, h):
        a = fig.add_axes([LEFT / FIG_WIDTH, b / fig_h, p.ax_w / FIG_WIDTH, h / fig_h])
        a.set_facecolor("none")
        a.set_xticks([])
        a.set_yticks([])
        for sp in a.spines.values():
            sp.set_linewidth(0.8)
            sp.set_color(ink)
        return a

    gap = 0.78
    ax_p = axes_at(bottom, p.h_p)
    ax_e = axes_at(bottom + p.h_p + gap, p.h_e)
    x0v, x1v = p.x_lo - p.pad_l / scale, p.x_hi + p.pad_r / scale
    ax_e.set_xlim(x0v, x1v)
    ax_e.set_ylim(0.0, p.z_view + p.band / scale)
    ax_p.set_xlim(x0v, x1v)
    ax_p.set_ylim(p.y_a, p.y_b)
    z_view = p.z_view
    planes = [v for v in vs if v.g.kind == "plane"]

    # -------------------------------------------------------------------------- elevation
    ax_e.plot([x0v, x1v], [0, 0], color=ink, lw=1.2, zorder=3, solid_capstyle="butt")
    seen = set()
    for lo, hi in p.boxes:
        k = (round(lo[0], 6), round(hi[0], 6), round(hi[2], 6))
        if k in seen:
            continue
        seen.add(k)
        ax_e.add_patch(Rectangle((lo[0], lo[2]), hi[0] - lo[0], hi[2] - lo[2], facecolor=body, edgecolor=ink, linewidth=0.8, zorder=2))
    if len(p.tris):      # a triangle mesh: every triangle projected undirected, so the walls fill the elevation and roofs and floors the plan
        from matplotlib.collections import PolyCollection
        ax_e.add_collection(PolyCollection(p.tris[:, :, [0, 2]], facecolors=body, edgecolors=body, linewidths=0.25, zorder=2))
    af = [(z, u) for z, u in approach_flow(case) if z <= z_view] if p.wind else []
    if af:
        n = min(len(af), 8)
        af = [af[i] for i in sorted({round(j * (len(af) - 1) / max(n - 1, 1)) for j in range(n)})]
        umax = max(u for _, u in af)
        xb = x0v + 0.14 * inch
        ax_e.plot([xb, xb], [0, z_view], color=ref, lw=0.7, zorder=3)
        tips = []
        for z, u in af:
            length = 0.50 * (u / umax) * inch
            _arrow(ax_e, (xb, z), (xb + length, z), 0.07 * inch, 0.028 * inch, ref, 0.8, z=3)
            tips.append((xb + length, z))
        ax_e.plot([t[0] for t in tips], [t[1] for t in tips], color=ref, lw=0.8, zorder=3)
        ax_e.text(xb + 0.02 * inch, z_view + 0.04 * inch, "U(z)", fontsize=TICK_PT, color=ref, ha="left", va="bottom")
    # planes: a dotted horizontal over the plane's extent, its letter (and label) at the right end, lifted off the ground line
    for v in planes:
        g, z = v.g, v.zs[0]
        ax_e.plot([v.xs[0], v.xs[-1]], [z, z], color=g.colour, lw=1.3, ls=DOTTED, zorder=5, dash_capstyle="round", clip_on=False)
        xe, ze = v.xs[-1] + 0.16 * inch, max(z, 0.12 * inch)
        _ring(ax_e, xe, ze, 0.082 * inch, g.letter, g.colour)
        if p.labelled(v):
            ax_e.text(xe + 0.15 * inch, ze, g.short, fontsize=LABEL_PT, color=ink, ha="left", va="center_baseline", zorder=8,
                      bbox=dict(boxstyle="square,pad=0.08", facecolor=ps.SURFACE, edgecolor="none"))
    # vertical profiles: a dotted line up to its label, the dots where it was sampled, smaller on top where groups share a spot
    share = {}
    for v in vs:
        for x in v.xs if v.g.kind == "profiles" else []:
            share.setdefault(x, []).append(v.g.letter)
    share = {x: {l: (i, len(ls)) for i, l in enumerate(ls)} for x, ls in share.items()}
    used_letter = []
    for gi, v in enumerate(vs):
        g = v.g
        if g.kind != "profiles":
            continue
        for x in v.xs:
            top = z_view + (p.row_of[p.x_in[x]] * ROW_IN + 0.04) * inch
            ax_e.plot([x, x], [0, top], color=g.colour, lw=1.1, ls=_dots(*share[x][g.letter]), zorder=4, dash_capstyle="round")
        spots = sorted({(round(tab[i]["x"], 6), round(tab[i]["z"], 6)) for i in v.idx})
        ax_e.scatter([s[0] for s in spots], [s[1] for s in spots], s=_area(p.dot, _rank(vs, v)), color=g.colour,
                     edgecolor=_dark(g.colour), linewidth=0.25, zorder=6 + 0.1 * _rank(vs, v))
        for x in v.xs:      # the letter under the frame, at a station of this group that no other letter sits near
            if all(abs(p.x_in[x] - u) > 0.24 for u in used_letter):
                used_letter.append(p.x_in[x])
                _ring(ax_e, x, -0.15 * inch, 0.082 * inch, g.letter, g.colour)
                break
    for x in p.stations:
        ax_e.text(x, z_view + (p.row_of[p.x_in[x]] * ROW_IN + 0.04) * inch, p.labels[x], fontsize=TICK_PT, color=ink, ha="center",
                  va="bottom", zorder=7, bbox=dict(boxstyle="square,pad=0.05", facecolor=ps.SURFACE, edgecolor="none"))
    for s in SOURCES.get(case, []):
        sx = s[1][0] if s[0] == "point" else s[1][0]
        sz = s[1][2] if s[0] == "point" else 0.0
        if p.x_lo - TOL <= sx <= p.x_hi + TOL:
            ax_e.plot([sx], [sz], marker="*", ms=8.5, color=ink, mec=ps.SURFACE, mew=0.4, zorder=9, ls="none", clip_on=False)

    # -------------------------------------------------------------------------- plan
    seen = set()
    for lo, hi in p.boxes:
        k = (round(lo[0], 6), round(lo[1], 6))
        if k in seen:
            continue
        seen.add(k)
        ax_p.add_patch(Rectangle((lo[0], lo[1]), hi[0] - lo[0], hi[1] - lo[1], facecolor=body, edgecolor=ink, linewidth=0.8, zorder=2))
    if len(p.tris):
        from matplotlib.collections import PolyCollection
        ax_p.add_collection(PolyCollection(p.tris[:, :, [0, 1]], facecolors=body, edgecolors=body, linewidths=0.25, zorder=2))
    same = {}          # planes with one outline share it: their dotted outlines take turns
    for v in planes:
        same.setdefault((v.xs[0], v.xs[-1], v.ys[0], v.ys[-1]), []).append(v.g.letter)
    rings, spots = [], []     # letters at the end of a feature (group, x, y, x of the letter); letters above a single dot
    for v in vs:
        g = v.g
        pts = sorted({(round(tab[i]["x"], 6), round(tab[i]["y"], 6)) for i in v.idx})
        if g.kind == "plane":
            w, h = v.xs[-1] - v.xs[0], v.ys[-1] - v.ys[0]
            ax_p.add_patch(Rectangle((v.xs[0], v.ys[0]), w, h, facecolor=g.colour, alpha=0.07, edgecolor="none", zorder=1.5))
            rank = [(i, len(ls)) for ls in same.values() for i, l in enumerate(ls) if l == g.letter][0]
            ax_p.add_patch(Rectangle((v.xs[0], v.ys[0]), w, h, facecolor="none", edgecolor=g.colour, linewidth=1.1, linestyle=_dots(*rank),
                                     zorder=4, clip_on=False))
            rings.append([g, v.xs[-1], 0.5 * (v.ys[0] + v.ys[-1]), v.xs[-1] + 0.20 * inch, 0.0])
        elif g.trace:
            for yv in v.ys:
                ax_p.plot([v.xs[0], v.xs[-1]], [yv, yv], color=g.colour, lw=1.1, ls=DOTTED, zorder=4, dash_capstyle="round")
                rings.append([g, v.xs[-1], yv, v.xs[-1] + 0.20 * inch, 0.0])
        elif len(pts) == 1:
            spots.append((g, pts[0][0], pts[0][1]))
        else:
            far = max(pts)
            rings.append([g, far[0], far[1], p.x_hi + 0.20 * inch, 0.0])
        k = _rank(vs, v)
        ax_p.scatter([q[0] for q in pts], [q[1] for q in pts], s=_area(p.dot, k), color=g.colour, edgecolor=_dark(g.colour), linewidth=0.2,
                     zorder=6 + 0.1 * k)
    # the letters that end features side by side are pushed apart, in the order of their features
    rings.sort(key=lambda r: r[3])
    clusters, cur = [], []
    for r in rings:
        if cur and abs(r[3] - cur[-1][3]) >= 0.45 * inch:
            clusters.append(cur)
            cur = []
        cur.append(r)
    if cur:
        clusters.append(cur)
    for c in clusters:
        for r, yp in zip(c, _spread([r[2] for r in c], 0.22 * inch)):
            r[4] = yp
    for g, xr, yr, xe, yp in rings:
        if abs(yp - yr) > 0.02 * inch or xe - xr > 0.25 * inch:
            ax_p.plot([xr, xe], [yr, yp], color=g.colour, lw=0.7, zorder=4)
        _ring(ax_p, xe, yp, 0.082 * inch, g.letter, g.colour)
    for g, xs_, ys_ in spots:
        _ring(ax_p, xs_, ys_ + 0.17 * inch, 0.082 * inch, g.letter, g.colour)
    for s in SOURCES.get(case, []):
        if s[0] == "point":
            if p.x_lo - TOL <= s[1][0] <= p.x_hi + TOL:
                ax_p.plot([s[1][0]], [s[1][1]], marker="*", ms=8.5, color=ink, mec=ps.SURFACE, mew=0.4, zorder=9, ls="none", clip_on=False)
        else:
            ax_p.plot([s[1][0], s[2][0]], [s[1][1], s[2][1]], color=ink, lw=2.2, zorder=3, solid_capstyle="butt")
    if p.wind:
        xw = x0v + 0.14 * inch
        yw = p.y_b - 0.22 * inch
        _arrow(ax_p, (xw, yw), (xw + 0.50 * inch, yw), 0.07 * inch, 0.028 * inch, ref, 0.8, z=3)
        ax_p.text(xw + 0.02 * inch, yw + 0.05 * inch, "U", fontsize=TICK_PT, color=ref, ha="left", va="bottom")

    # -------------------------------------------------------------------------- titles and axis arrows
    if p.win is None:
        names = ("Elevation", "Plan")
    else:
        names = tuple(f"{n}, x/{sym} = {mult(p.win[0] / unit, sym).replace(sym, '')} to {mult(p.win[1] / unit, sym).replace(sym, '')}"
                      for n in ("Elevation", "Plan"))
    for ax, name, h, letter in ((ax_e, names[0], p.h_e, letters[0]), (ax_p, names[1], p.h_p, letters[1])):
        ax.text(0.0, 1.0 + 0.06 / h, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", ha="left", va="bottom", color=ink)
        ax.text(0.0 + 0.20 / p.ax_w, 1.0 + 0.065 / h, name, transform=ax.transAxes, fontsize=LABEL_PT + 1, ha="left", va="bottom", color=ink)
    for ax, up in ((ax_e, "z"), (ax_p, "y")):
        xa, ya = x0v - 0.40 * inch, ax.get_ylim()[0] - 0.10 * inch
        _arrow(ax, (xa, ya), (xa + 0.30 * inch, ya), 0.07 * inch, 0.028 * inch, ink, 0.9)
        _arrow(ax, (xa, ya), (xa, ya + 0.30 * inch), 0.07 * inch, 0.028 * inch, ink, 0.9)
        ax.text(xa + 0.34 * inch, ya, "x", fontsize=LABEL_PT, ha="left", va="center_baseline", color=ink, clip_on=False)
        ax.text(xa, ya + 0.34 * inch, up, fontsize=LABEL_PT, ha="center", va="bottom", color=ink, clip_on=False)


def _rank(vs, v):
    """The index of the view's group: the first group's dots are the largest, later ones sit smaller on top."""
    return "ABCDEFG".index(v.g.letter)
