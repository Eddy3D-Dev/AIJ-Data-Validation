"""Where the tunnel measured: the measurement lines and planes of every AIJ UWE case, as groups and as a figure.

Every row of clean/cases/<X>/points.csv belongs to exactly one GROUP: a set of points the tunnel took along one line or
in one plane (a vertical section, a horizontal plane, a set of vertical profiles). The groups are DERIVED from the
coordinates, not listed point by point: a group is a rule over (x, y, z) (and, where one table holds two instruments, the
instrument), written once per case below with the numbers of the tunnel's own drawings (MP_*.png) and the data paper
(sections 3.1 to 3.13). The same groups colour the scatter dots of the agreement figures and draw the layout figure, so
a dot in one figure is found in the other by its colour and its letter.

Public names (other scripts import them; keep them stable):

  rows(case)                      the cleaned point table of a case, as dicts {x, y, z, instrument, config, point_id, measured, ...}
  groups(case)                    [Group]: letter, label, short, kind, colour, members (row indices), the lines and planes
  classify(case, row, instrument=None)   the index of the group a row belongs to; raises unless exactly one rule matches
  grouped_colours(case, rows, instrument=None)   one colour per row, for the scatter dots of an agreement figure
  legend_handles(case, instrument=None)   handles for fig.legend / ps.finish: a circled letter in the group colour per group
  legend_rows(case, neutral)      the same for the agreement figures of the district cases: the neutral entries on one row, the letters under them
  flow_dirs(case, instrument)     the unit vectors the wind blows toward, per wind direction, from directions.csv
  e_new_buildings()               the three buildings the after state of Case E adds, as footprints and heights
  layout_figure(case, geometry=None)      the figure of cases A, B, G to L: (a) elevation x-z, (b) plan x-y, groups lettered and coloured
  district_figure(case)           the figure of the district cases C, D, E, F, M: (a) plan of the points on the buildings, (b) the strip
                                  under or beside it (elevation, or the heights at the points of F)
  check_group_palette()           the group colours are the plotstyle cycle, and tell apart under every colour vision

Contract of a new case: add one function `_groups_<x>(ctx)` returning a list of Spec, register it in SPECS, give the case a UNITS
entry. The tests in test_layout.py then cover the new case as soon as it is in SPECS (add its expected sizes to EXPECTED and TOTAL
there). geometry(case, configuration) reads the boxes of A-D and G-L; a triangle mesh (E, F, M) is drawn undirected: roofs fill the
plan of E, the vertical facets give the outlines of F and M and the silhouette of M, winding is never read.

The district cases (C, D, E, F, M) measure at one height or a few on a plan, so their groups are Specs of kind 'points': C the
streets round the centre block, D the instrument and the place near the tower, E the distance to the three new buildings, F the
tunnel planes and the field anemometers, M the distance from the release point. district_figure() draws them.

The module is standard library only up to `layout_figure`; matplotlib is imported when a figure is drawn, so the group
tests run anywhere. Group kinds:

  profiles   vertical lines (x, y fixed, z varies): dotted verticals in the elevation, one dot per line in the plan;
             `trace` marks the groups that are a vertical SECTION (one y): a dotted line at that y in the plan
  plane      a horizontal plane (z fixed): a dotted horizontal in the elevation, dots and an outline in the plan
  points     points of a district case, grouped by where they stand or what read them: dots in the plan (district_figure)
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
    "C": ("D", 0.20, "D = 0.2 m"),
    "D": ("H", 0.25, "H = 0.25 m = 100 m full scale"),
    "E": ("m", 1.0, "full scale, 1:250"),
    "F": ("m", 1.0, "full scale, 1:800"),
    "M": ("m", 1.0, "full scale, 1:600"),
}

# What the points do not show and the geometry would hide: the published half, the part of the geometry outside the frame.
NOTES = {
    "A": "points published for y ≤ 0",
    "B": "points published for y ≤ 0",
    "G": "belt 74 m long, y = ±37 m",
    "K": "9 × 9 cubes, cut at the frame",
    "L": "9 × 14 cubes, cut at the frame",
    "C": "the 120 points are the same in all nine configurations",
    "D": "plan cut at ±0.26 m of the 1.4 m array of 82 blocks",
    "E": "z = 2 m, 16 wind directions",
    "F": "heights above ground = z − 10 m",
    "M": "points 3 m above the local ground; R the reference point on the roof of the main building",
}

# What a district figure shows that the groups do not say.
TAILS = {
    "C": "Centre block absent (0D), D or 2D high; wind directions 0°, 22.5° and 45°.",
    "D": "The split fibre stands at 33 of the 78 places of the thermistors; open dots: the 12 places where the thermistor read nothing; wind directions 0°, 22.5° and 45°.",
    "E": "Dark footprints: the three buildings added in the after state.",
    "F": "SMB and KDD: the reference buildings. The field anemometers stand at the places of the tunnel points.",
    "M": "Star: release point; R: reference point; dotted circles: 100 m and 300 m from the release point.",
}

# The gas release, from clean/cases/<X>/geometry.json: ('point', (x, y, z)) or ('line', (x0, y0), (x1, y1)) on the floor.
SOURCES = {
    "H": [("point", (0.05, 0.0, 0.0))],
    "I": [("point", (0.0, 0.0, 0.1))],
    "J": [("point", (0.04, 0.0, 0.0))],
    "K": [("point", (-0.15, 0.0, 0.0))],
    "L": [("line", (-0.15, -0.51), (-0.15, 0.51))],
    "M": [("point", (-82.14, 61.98, 32.4))],     # LC_caseM.csv Gas_source (-0.1369, 0.1033, 0.054 m) x 600, in the release frame (x north, y west)
}
MAST = (-66.9, -3.72, 72.9)                      # Case M reference point R, LC_caseM.csv Reference (-0.1115, -0.0062, 0.1215 m) x 600: the roof of the main building, 41 m above the ground
DISC_F = 725.0      # radius of the disc of Case F's model: the bounding box of geometry.json, 0.90625 m model x 800
TOWERS = {"SMB": (-17.5, 96.0, 225.0), "KDD": (85.8, -347.1, 180.0)}   # Case F reference buildings: the workbook's 'Points' sheet, roofs in the STL (QUESTIONS.md QF6)


# ----------------------------------------------------------------------------- the table

_ROWS: dict[str, list[dict]] = {}
_NUMERIC = ("x", "y", "z", "wind_direction_deg")
VALUES = ("U", "V", "W", "k", "Vs", "velocity_ratio", "C", "T")     # a row with none of these is a place the instrument was set up at and read nothing


def rows(case):
    """The cleaned point table of `case` (clean/cases/<case>/points.csv) as dicts; coordinates are floats."""
    if case not in _ROWS:
        out = []
        with io.open(os.path.join(CASES_DIR, case, "points.csv"), encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                d = {k: r[k] for k in ("case_id", "config", "instrument", "point_id")}
                for k in _NUMERIC:
                    d[k] = float(r[k]) if r[k] != "" else math.nan
                d["measured"] = any(r[k] != "" for k in VALUES)
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


# ----------------------------------------------------------------------------- the district cases: groups of points

def _pts(label, short, test):
    return Spec("points", label, short, test)


def _groups_c(ctx):
    """C: 120 points on z = 0.1 D in the streets round the centre block, at the same places in all nine configurations: the street
    on each of the four sides of the block (|x| or |y| within the block's half side, D/2) and the four crossings beyond its corners."""
    h = ctx.unit / 2
    beside = lambda r, c: abs(r["y"]) <= h + TOL     # noqa: E731  the streets west and east of the block
    along = lambda r, c: abs(r["x"]) <= h + TOL      # noqa: E731  the streets north and south of it
    return [_pts("street x < 0 beside the centre block", "street x < 0", lambda r, c: beside(r, c) and r["x"] < 0),
            _pts("street x > 0 beside the centre block", "street x > 0", lambda r, c: beside(r, c) and r["x"] > 0),
            _pts("street y > 0 beside the centre block", "street y > 0", lambda r, c: along(r, c) and r["y"] > 0),
            _pts("street y < 0 beside the centre block", "street y < 0", lambda r, c: along(r, c) and r["y"] < 0),
            _pts("crossings beyond the corners of the centre block", "crossings", lambda r, c: not beside(r, c) and not along(r, c))]


def _groups_d(ctx):
    """D: 78 thermistor points on z/H = 0.02 round the tower (at WD 0, 22.5 and 45) and 33 split-fibre points at the places of the
    thermistors on the +y side (WD 0). The thermistors are grouped by the column of blocks they stand in (x, from geometry.json: blocks at
    x/H in [-0.8, -0.4], [-0.2, 0.2] and [0.5, 0.9]): the site of the removed central block, the two streets along y beside it (-0.4 < x/H < -0.2
    and 0.2 < x/H < 0.5), and the streets along x further out."""
    H = ctx.unit
    th, sf = (lambda r: r["instrument"] == "thermistor"), (lambda r: r["instrument"] == "split_fibre")
    site = lambda r: abs(r["x"]) <= 0.2 * H + TOL                                              # noqa: E731
    beside = lambda r: -0.4 * H < r["x"] < -0.2 * H or 0.2 * H < r["x"] < 0.5 * H              # noqa: E731
    return [_pts("split-fibre probe, WD 0", "split fibre", lambda r, c: sf(r)),
            _pts("thermistor on the site of the central block, |x/H| ≤ 0.2", "thermistor, central site", lambda r, c: th(r) and site(r)),
            _pts("thermistor in the streets along y beside it", "thermistor, streets along y", lambda r, c: th(r) and beside(r)),
            _pts("thermistor in the streets along x further out", "thermistor, streets along x", lambda r, c: th(r) and not site(r) and not beside(r))]


E_NEAR = 30.0     # Case E: a point is "near" a new building when it is within this many metres of its footprint (half the height of the 60 m building)
_E_NEW = []


def e_new_buildings():
    """The buildings the 'after' state adds, [(x0, x1, y0, y1, height)] tallest first: the triangles of geometry_ac_3dm.stl that
    geometry_bc_3dm.stl lacks, joined where they share a vertex (the 60 m building and the two of 18 m)."""
    if not _E_NEW:
        def tris(name):
            return read_stl(os.path.join(CASES_DIR, "E", name))
        key = lambda t: tuple(sorted(tuple(round(c, 3) for c in v) for v in t))    # noqa: E731
        before = {key(t) for t in tris("geometry_bc_3dm.stl")}
        new = [t for t in tris("geometry_ac_3dm.stl") if key(t) not in before]
        parent = {}

        def find(a):
            while parent.setdefault(a, a) != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for t in new:
            vs = [tuple(round(c, 2) for c in v) for v in t]
            for v in vs[1:]:
                parent[find(vs[0])] = find(v)
        parts = {}
        for t in new:
            parts.setdefault(find(tuple(round(c, 2) for c in t[0])), []).append(t)
        for ts in parts.values():
            xs, ys, zs = ([v[i] for t in ts for v in t] for i in range(3))
            _E_NEW.append((min(xs), max(xs), min(ys), max(ys), max(zs)))
        _E_NEW.sort(key=lambda b: (-b[4], b[0]))
    return _E_NEW


def _e_dist(r, b):
    return math.hypot(max(b[0] - r["x"], 0.0, r["x"] - b[1]), max(b[2] - r["y"], 0.0, r["y"] - b[3]))


def _groups_e(ctx):
    """E: 80 points on z = 2 m, the same in the before and after states and in 16 wind directions: the points within 30 m of the
    60 m building that the after state adds, those within 30 m of the two 18 m buildings, and the others."""
    tall, *low = e_new_buildings()
    near_tall = lambda r: _e_dist(r, tall) <= E_NEAR + TOL                       # noqa: E731
    near_low = lambda r: min(_e_dist(r, b) for b in low) <= E_NEAR + TOL         # noqa: E731
    return [_pts("within 30 m of the 60 m building", "near 60 m building", lambda r, c: near_tall(r)),
            _pts("within 30 m of the two 18 m buildings", "near 18 m buildings", lambda r, c: near_low(r)),
            _pts("elsewhere", "elsewhere", lambda r, c: not near_tall(r) and not near_low(r))]


F_RAISE = 10.0      # the readme: the model stands 10 m above the tunnel floor, so a height above ground is z - 10 m


def _groups_f(ctx):
    """F: 13 points, the same places for every instrument and wind direction: the tunnel's thermistor planes 5, 9 and 20 m above
    ground (z = 15, 19 and 30 m of the tunnel frame; 9, 13 and 13 of the points) and the field's cup anemometers at 3 to 11 m."""
    th = lambda r: r["instrument"] == "thermistor"       # noqa: E731
    plane = lambda h: (lambda r, c: th(r) and _near(r["z"] - F_RAISE, h))
    return [Spec("plane", "tunnel plane 5 m above ground", "tunnel 5 m", plane(5.0)),
            Spec("plane", "tunnel plane 9 m above ground", "tunnel 9 m", plane(9.0)),
            Spec("plane", "tunnel plane 20 m above ground", "tunnel 20 m", plane(20.0)),
            _pts("field cup anemometers, 3 to 11 m above ground", "field cup anemometers", lambda r, c: r["instrument"] == "cup_anemometer")]


M_NEAR, M_FAR = 100.0, 300.0     # Case M: near field within 100 m of the release point, far field beyond 300 m


def _groups_m(ctx):
    """M: 15 points 3 m above the ground, the same in the tunnel at WD 175, 180 and 185 and in the 18 field runs: by distance from the release point."""
    sx, sy, _ = SOURCES["M"][0][1]
    dist = lambda r: math.hypot(r["x"] - sx, r["y"] - sy)    # noqa: E731
    return [_pts("near field, within 100 m of the release point", "near field", lambda r, c: dist(r) < M_NEAR),
            _pts("mid field, 100 to 300 m from the release point", "mid field", lambda r, c: M_NEAR <= dist(r) <= M_FAR),
            _pts("far field, beyond 300 m", "far field", lambda r, c: dist(r) > M_FAR)]


SPECS = {"A": _groups_a, "B": _groups_b, "C": _groups_c, "D": _groups_d, "E": _groups_e, "F": _groups_f, "G": _groups_g, "H": _groups_h,
         "I": _groups_i, "J": _groups_j, "K": _groups_k, "L": _groups_l, "M": _groups_m}


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
    text = f"Case {case}, measurement {'points' if case in DISTRICT else 'lines and planes'}: {what}. Positions in " + (
        "metres, full scale" if sym == "m" else f"multiples of {sym}")
    if case in ZOOM:
        lo, hi = ZOOM[case][0] / unit, ZOOM[case][1] / unit
        text += f"; panels c and d: x/{sym} = {'-' if lo < 0 else ''}{_g(lo)} to {_g(hi)}"
    return text + "." + (" " + TAILS[case] if case in TAILS else "")


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


def legend_rows(case, neutral):
    """(handles, ncols) for the legend of an agreement figure of a district case: the neutral entries (markers, 1:1, factor of two) on
    the first row and the circled letters of the case's groups on the second. ultraplot fills a legend by rows, so each row is padded
    with blank entries to the length of the longer one."""
    from matplotlib.lines import Line2D
    letters = legend_handles(case)
    n = max(len(neutral), len(letters))
    blank = Line2D([], [], ls="none", label=" ")
    return list(neutral) + [blank] * (n - len(neutral)) + letters + [blank] * (n - len(letters)), n


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


# ----------------------------------------------------------------------------- the district figure (cases C, D, E, F, M)

DISTRICT = ("C", "D", "E", "F", "M")
NUM_PT = 5.8                      # the point numbers beside the dots
LEFT_D = 0.84                     # the left margin of a district figure: tick labels and the axis arrows

# What each plan shows: window (x0, x1, y0, y1) [m of the case frame], width [in], tick step [m], dot area [pt^2], whether the dots carry the
# tunnel's point numbers, the strip that goes with it ('elevation' under the plan; 'heights' to its right), and the cluster link [m]
# (two points of a group closer than this belong to one patch of it) with the padding of the patch [m].
VIEWS = {
    "C": dict(win=(-0.58, 0.58, -0.58, 0.58), width=5.2, step=0.1, dot=17.0, numbers=False, strip="elevation", link=0.06, pad=0.025),
    "D": dict(win=(-0.26, 0.26, -0.26, 0.26), width=5.2, step=0.05, dot=26.0, numbers=True, strip="elevation", link=0.04, pad=0.0125),
    "E": dict(win=(-160.0, 160.0, -160.0, 160.0), width=5.8, step=50.0, dot=16.0, numbers=True, strip=None, link=0.0, pad=0.0),
    "F": dict(win=(-340.0, 340.0, -570.0, 430.0), width=3.5, step=100.0, dot=8.0, numbers=True, strip="heights", link=0.0, pad=0.0),
    "M": dict(win=(-140.0, 300.0, -150.0, 130.0), width=6.65, step=50.0, dot=30.0, numbers=True, strip="elevation", link=0.0, pad=0.0),
}


def flow_dirs(case, instrument=None):
    """{wind direction: (flow_dir_x, flow_dir_y)} of clean/cases/<case>/directions.csv: the unit vector the wind blows toward in the case frame."""
    out = {}
    with io.open(os.path.join(CASES_DIR, case, "directions.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if instrument in (None, r["instrument"]):
                out.setdefault(float(r["wind_direction_deg"]), (float(r["flow_dir_x"]), float(r["flow_dir_y"])))
    return dict(sorted(out.items()))


def wall_segments(tris):
    """The plan outline of a triangle mesh: every vertical facet projects to a segment, which is all the outline of a building needs; no winding is read."""
    segs = set()
    for t in tris:
        (x1, y1, _), (x2, y2, _), (x3, y3, _) = t
        if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-6:
            pts = sorted({(round(a, 2), round(b, 2)) for a, b, _ in t})
            if len(pts) == 2:
                segs.add((pts[0], pts[1]))
    return sorted(segs)


def roof_polygons(tris):
    """The triangles that have area in plan and stand above the ground, as plan polygons: roofs fill the footprints; walls project to nothing."""
    return [((x1, y1), (x2, y2), (x3, y3)) for (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) in tris
            if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) > 1e-6 and max(z1, z2, z3) > 0.05]


def skyline(tris, x0, x1, n=420):
    """The upper envelope of a triangle mesh projected on the x-z plane, at n positions from x0 to x1: terrain and buildings as one silhouette."""
    import numpy as np
    t = np.asarray(tris, float)
    xs = np.linspace(x0, x1, n)
    top = np.zeros(n)
    for a, b in ((0, 1), (1, 2), (2, 0)):
        xa, za, xb, zb = t[:, a, 0], t[:, a, 2], t[:, b, 0], t[:, b, 2]
        lo, hi = np.minimum(xa, xb), np.maximum(xa, xb)
        run = np.where(xb != xa, xb - xa, 1.0)
        for i, x in enumerate(xs):
            hit = (lo <= x) & (x <= hi)
            if hit.any():
                z = np.where(xb != xa, za + (zb - za) * (x - xa) / run, np.maximum(za, zb))
                top[i] = max(top[i], float(z[hit].max()))
    return xs, top


def clusters(pts, link):
    """Patches of `pts` [(x, y)]: points within `link` of a point of the patch belong to it. Returns [(x0, x1, y0, y1)] of each patch."""
    parent = list(range(len(pts)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for i, p in enumerate(pts):
        for j in range(i):
            if math.hypot(p[0] - pts[j][0], p[1] - pts[j][1]) <= link + TOL:
                parent[find(i)] = find(j)
    patches = {}
    for i, p in enumerate(pts):
        patches.setdefault(find(i), []).append(p)
    out = [(min(q[0] for q in v), max(q[0] for q in v), min(q[1] for q in v), max(q[1] for q in v)) for v in patches.values()]
    return sorted(out)


def _facing(box, centre, pad):
    """Where a patch's letter sits: the middle of the side of its padded box, or the corner, that faces away from `centre`."""
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = cx - centre[0], cy - centre[1]
    n = math.hypot(dx, dy)
    ux, uy = (dx / n, dy / n) if n > 1e-9 else (0.0, 1.0)
    sx = -1 if ux < -0.38 else 1 if ux > 0.38 else 0
    sy = -1 if uy < -0.38 else 1 if uy > 0.38 else 0
    return (cx if sx == 0 else x0 - pad if sx < 0 else x1 + pad), (cy if sy == 0 else y0 - pad if sy < 0 else y1 + pad)


def _round_box(x0, x1, y0, y1, r, n=10):
    """The outline of the points within r of the box (x0, x1, y0, y1): a rounded rectangle, as a closed polygon."""
    out = []
    for cx, cy, a0 in ((x1, y1, 0.0), (x0, y1, 90.0), (x0, y0, 180.0), (x1, y0, 270.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((round(cx + r * math.cos(a), 6), round(cy + r * math.sin(a), 6)))
    return out


def _ticks(ax, lo, hi, step, axis, sym, unit, inch, ink):
    """Tick marks and labels outside the frame of a plan, at multiples of `step` [m]; labelled in multiples of the case's unit, or in metres."""
    k = math.ceil(lo / step - 1e-9)
    while k * step <= hi + 1e-9:
        t = round(k * step, 6)
        lab = mult(t / unit, sym) if sym != "m" else f"{t:g}"
        if axis == "x":
            y0 = ax.get_ylim()[0]
            ax.plot([t, t], [y0, y0 - 0.05 * inch], color=ink, lw=0.7, clip_on=False, solid_capstyle="butt")
            ax.text(t, y0 - 0.08 * inch, lab, fontsize=TICK_PT, color=ink, ha="center", va="top", clip_on=False)
        else:
            x0 = ax.get_xlim()[0]
            ax.plot([x0, x0 - 0.05 * inch], [t, t], color=ink, lw=0.7, clip_on=False, solid_capstyle="butt")
            ax.text(x0 - 0.08 * inch, t, lab, fontsize=TICK_PT, color=ink, ha="right", va="center_baseline", clip_on=False)
        k += 1


def _district_geometry(case):
    """What the plan of a district case draws: boxes (C, D; the tallest is the subject), roof polygons (E), wall segments (F, M), and the
    triangles themselves where the strip needs a silhouette (M)."""
    g = {"boxes": [], "polys": [], "segs": [], "tris": None}
    if case == "C":
        g["boxes"] = geometry("C", "2D").boxes
    elif case == "D":
        g["boxes"] = geometry("D").boxes
    else:
        path = os.path.join(CASES_DIR, case, "geometry_ac.stl" if case == "E" else "geometry.stl")
        tris = read_stl(path)
        if case == "E":
            g["polys"] = roof_polygons(tris)
        else:
            g["segs"] = wall_segments(tris)
            g["tris"] = tris if case == "M" else None
    return g


def district_figure(case):
    """The measurement points of a district case (C, D, E, F, M): (a) the plan with the buildings, the points coloured and lettered by group,
    ticks in multiples of the case's unit (metres for E, F, M), the wind or north; (b) the strip: under the plan the elevation (C, D: the blocks
    and the plane of the points; M: the silhouette of terrain and buildings with the points 3 m above the ground, the release point and the
    reference mast), or beside it, for F, the heights above ground at each point. Returns the matplotlib figure; write it with plotstyle.save()."""
    import numpy as np
    import plotstyle as ps
    from matplotlib.collections import LineCollection, PolyCollection
    from matplotlib.figure import Figure
    from matplotlib.patches import Polygon, Rectangle

    check_group_palette()
    ps.apply()
    gs, tab = groups(case), rows(case)
    sym, unit, note = UNITS[case]
    v = VIEWS[case]
    ink, ref, surface = ps.INK, ps.REFERENCE, ps.SURFACE
    geo = _district_geometry(case)
    renderer = _renderer()
    x0, x1, y0, y1 = v["win"]
    W = v["width"]
    scale = W / (x1 - x0)                                   # inches per metre, in x and y alike
    inch = 1.0 / scale
    H_plan = (y1 - y0) * scale
    place = {}                                              # the point number at each place
    for r in tab:
        place[(round(r["x"], 6), round(r["y"], 6))] = int(r["point_id"])
    where = {g.letter: sorted({(round(tab[i]["x"], 6), round(tab[i]["y"], 6)) for i in g.members}) for g in gs}
    strip = v["strip"]

    # ---------------------------------------------------------------- the strip under the plan (elevation): sizes
    stations, labels, row_of, z_view, band = [], {}, {}, 0.0, 0.0
    if strip == "elevation":
        z_top = max([hi[2] for _, hi in geo["boxes"]] or [0.0])
        if case == "M":
            xs_sky, top_sky = skyline(geo["tris"], x0, x1)
            z_top = max(float(top_sky.max()), MAST[2])
        z_view = round(z_top * 1.06, 6)
        stations = sorted({p[0] for g in gs for p in where[g.letter] if x0 <= p[0] <= x1})
        labels = {x: (str(place[next(p for p in place if p[0] == x)]) if case == "M" else mult(x / unit, sym)) for x in stations}
        x_in = {x: (x - x0) * scale for x in stations}
        row_of, n_rows = _pack([(x_in[x], _text_size(renderer, labels[x], TICK_PT)[0]) for x in stations], 0.05)
        band = n_rows * ROW_IN + 0.10
    h_strip = (z_view * scale + band) if strip == "elevation" else 0.0

    # ---------------------------------------------------------------- the figure
    handles = legend_handles(case, short=False)
    chars = sum(len(h.get_label()) for h in handles)
    ncols = len(handles) if chars <= 92 else 2 if len(handles) > 2 else 1
    leg_h = 0.26 * math.ceil(len(handles) / ncols) + 0.10
    bottom = 0.14 + leg_h + 0.30
    below_plan = 0.62                                        # tick labels and the axis arrows
    y_strip = bottom + 0.42                                  # the letters under the elevation frame
    y_plan = (y_strip + h_strip + 0.80) if strip == "elevation" else bottom + below_plan
    fig_h = y_plan + H_plan + 0.95                           # the title, and the wind or north above the plan
    fig = Figure(figsize=(FIG_WIDTH, fig_h), dpi=ps.DPI)
    fig.patch.set_facecolor(surface)

    def frame(xin, yin, w, h):
        a = fig.add_axes([xin / FIG_WIDTH, yin / fig_h, w / FIG_WIDTH, h / fig_h])
        a.set_facecolor("none")
        a.set_xticks([])
        a.set_yticks([])
        for sp in a.spines.values():
            sp.set_linewidth(0.8)
            sp.set_color(ink)
        return a

    ax = frame(LEFT_D, y_plan, W, H_plan)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ring_r = 0.082 * inch

    # ---------------------------------------------------------------- plan: the buildings
    seen = set()
    top_z = max([hi[2] for _, hi in geo["boxes"]] or [0.0])
    for lo, hi in geo["boxes"]:
        k = (round(lo[0], 6), round(lo[1], 6))
        if k in seen:
            continue
        seen.add(k)
        ax.add_patch(Rectangle((lo[0], lo[1]), hi[0] - lo[0], hi[1] - lo[1], facecolor=ps.FOOTPRINT_FOCUS if hi[2] == top_z else ps.FOOTPRINT,
                               edgecolor=ink, linewidth=0.7, zorder=2))
    if case in ("C", "D"):                                      # the subject of the case, named where it stands
        ax.text(0.0, 0.0, "centre\nblock" if case == "C" else "tower", fontsize=TICK_PT, color=ink, ha="center", va="center", zorder=7)
    if geo["polys"]:
        ax.add_collection(PolyCollection(geo["polys"], facecolors=ps.FOOTPRINT, edgecolors=ps.FOOTPRINT, linewidths=0.2, zorder=2))
        for b in e_new_buildings():
            ax.add_patch(Rectangle((b[0], b[2]), b[1] - b[0], b[3] - b[2], facecolor=ps.FOOTPRINT_FOCUS, edgecolor=ink, linewidth=0.8, zorder=2.5))
    if geo["segs"]:
        ax.add_collection(LineCollection(geo["segs"], colors=ref, linewidths=0.3, zorder=2))

    # ---------------------------------------------------------------- plan: what makes the groups, drawn
    pad = v["pad"]
    if case in ("C", "D"):
        for g in gs:
            if case == "D" and g.letter == "A":
                continue                                                 # the split fibre stands among the thermistors: its markers say it
            for box in clusters(where[g.letter], v["link"]):
                bx0, bx1, by0, by1 = box[0] - pad, box[1] + pad, box[2] - pad, box[3] + pad
                ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, facecolor=g.colour, alpha=0.08, edgecolor="none", zorder=1.5))
                ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, facecolor="none", edgecolor=g.colour, linewidth=1.0, linestyle=DOTTED, zorder=4))
                ax_, ay_ = _facing(box, (0.0, 0.0), pad)
                _ring(ax, ax_ + (0.5 * ring_r if ax_ > bx1 - 1e-9 else -0.5 * ring_r if ax_ < bx0 + 1e-9 else 0.0), ay_ + (
                    0.5 * ring_r if ay_ > by1 - 1e-9 else -0.5 * ring_r if ay_ < by0 + 1e-9 else 0.0), ring_r, g.letter, g.colour)
    if case == "E":
        tall, *low = e_new_buildings()
        for b, letter in ((tall, "A"), (low[0], "B"), (low[1], "B")):
            g = gs["ABC".index(letter)]
            poly = _round_box(b[0], b[1], b[2], b[3], E_NEAR)
            ax.add_patch(Polygon(poly, closed=True, facecolor=g.colour, alpha=0.07, edgecolor="none", zorder=1.5))
            ax.add_patch(Polygon(poly, closed=True, facecolor="none", edgecolor=g.colour, linewidth=1.0, linestyle=DOTTED, zorder=4))
        for b, txt, up in ((tall, "60 m", 0.5), (low[0], "18 m", 0.2), (low[1], "18 m", 0.8)):
            ax.text((b[0] + b[1]) / 2, b[2] + up * (b[3] - b[2]), txt, fontsize=TICK_PT, color=ink, ha="center", va="center", zorder=7)
    if case == "M":
        sx, sy, sz = SOURCES["M"][0][1]
        for r, name in ((M_NEAR, "100 m"), (M_FAR, "300 m")):
            th = np.linspace(0.0, 2 * math.pi, 241)
            ax.plot(np.round(sx + r * np.cos(th), 6), np.round(sy + r * np.sin(th), 6), color=ref, lw=0.9, ls=DOTTED, zorder=4)

    # ---------------------------------------------------------------- plan: the points
    dot = v["dot"]
    mini = {"A": (-1, 1), "B": (1, 1), "C": (-1, -1), "D": (1, -1)}     # Case F: up to four symbols per place, one corner for each group
    for g in gs:
        px, py = [p[0] for p in where[g.letter]], [p[1] for p in where[g.letter]]
        if case == "D" and g.letter == "A":
            ax.scatter(px, py, s=72.0, facecolor="none", edgecolor=g.colour, linewidth=1.3, zorder=5)
        elif case == "F":
            d = 0.042 * inch
            ax.scatter([a + mini[g.letter][0] * d for a in px], [b + mini[g.letter][1] * d for b in py], s=dot * (1.7 if g.letter == "D" else 1.0),
                       marker="D" if g.letter == "D" else "o", color=g.colour, edgecolor=_dark(g.colour), linewidth=0.25, zorder=6)
        else:
            read = {p for p in where[g.letter] if any(tab[i]["measured"] for i in g.members if (round(tab[i]["x"], 6), round(tab[i]["y"], 6)) == p)}
            ax.scatter([p[0] for p in where[g.letter] if p in read], [p[1] for p in where[g.letter] if p in read], s=dot, color=g.colour,
                       edgecolor=_dark(g.colour), linewidth=0.25, zorder=6)
            ax.scatter([p[0] for p in where[g.letter] if p not in read], [p[1] for p in where[g.letter] if p not in read], s=dot, facecolor=surface,
                       edgecolor=g.colour, linewidth=1.0, zorder=6)       # a place where the instrument stood and read nothing
    if v["numbers"]:
        off = {"C": 0.04, "D": 0.07, "E": 0.035, "F": 0.10, "M": 0.05}[case]
        for (px, py), n in sorted(place.items()):
            if x0 <= px <= x1 and y0 <= py <= y1:
                ax.text(px + off * inch, py + 0.02 * inch, str(n), fontsize=NUM_PT, color=ink, ha="left", va="bottom", zorder=7)

    # ---------------------------------------------------------------- plan: letters, release point, mast, towers
    def ring_at(letter, x, y):
        _ring(ax, x, y, ring_r, letter, gs["ABCDEFG".index(letter)].colour)
    if case == "D":
        ring_at("A", 0.0, 0.1375 + 0.0)
    if case == "E":
        tall, *low = e_new_buildings()
        ring_at("A", tall[0] - E_NEAR * 0.7071, tall[3] + E_NEAR * 0.7071)
        ring_at("B", low[1][1] + E_NEAR * 0.7071, low[1][3] + E_NEAR * 0.7071)
        far = min(where["C"])
        ring_at("C", far[0] - 0.17 * inch, far[1])
    if case == "M":
        sx, sy, sz = SOURCES["M"][0][1]
        ax.plot([sx], [sy], marker="*", ms=9.5, color=ink, mec=surface, mew=0.4, zorder=9, ls="none")
        ax.plot([MAST[0]], [MAST[1]], marker="s", ms=5.5, color=surface, mec=ink, mew=1.0, zorder=9, ls="none")
        ax.text(MAST[0] - 0.09 * inch, MAST[1] - 0.05 * inch, "R", fontsize=LABEL_PT, color=ink, ha="right", va="top", zorder=9, fontweight="bold")
        ax.text(sx + 0.10 * inch, sy, "source", fontsize=TICK_PT, color=ink, ha="left", va="center_baseline", zorder=9)
        for r, ang, letter in ((M_NEAR, 30.0, "A"), (M_FAR, -22.0, "B")):
            a = math.radians(ang)
            ring_at(letter, sx + r * math.cos(a), sy + r * math.sin(a))
        ring_at("C", 0.5 * (min(where["C"])[0] + max(where["C"])[0]) + 0.0, 0.5 * (where["C"][0][1] + where["C"][1][1]) + 22.0)
    if case == "F":
        for name, (tx, ty, tz) in TOWERS.items():
            ax.plot([tx], [ty], marker="s", ms=5.5, color=surface, mec=ink, mew=1.0, zorder=9, ls="none")
            ax.text(tx + 0.09 * inch, ty, f"{name}", fontsize=LABEL_PT, color=ink, ha="left", va="center_baseline", zorder=9, fontweight="bold")

    # ---------------------------------------------------------------- plan: wind, north, ticks, axes
    gx, gy = x1 - 0.55 * inch, y1 + 0.30 * inch
    L = 0.36 * inch
    if case in ("C", "D"):                                  # the three wind directions as a fan of arrows from one point, centred 0.3 in above the plan
        fl = flow_dirs(case, "thermistor")
        ys_ = [L * fy for fx, fy in fl.values()]
        gy -= 0.5 * (min(ys_ + [0.0]) + max(ys_ + [0.0]))
        for wd, (fx, fy) in fl.items():
            _arrow(ax, (gx, gy), (gx + L * fx, gy + L * fy), 0.07 * inch, 0.028 * inch, ref, 0.8, z=3)
            ax.text(gx + L * fx + 0.05 * inch, gy + L * fy, f"{wd:g}°", fontsize=TICK_PT, color=ref, ha="left", va="center_baseline", clip_on=False)
        ax.text(gx - 0.06 * inch, gy, "WD", fontsize=TICK_PT, color=ref, ha="right", va="center_baseline", clip_on=False)
    elif case == "M":                                       # the frame has north along +x and west along +y; the wind of the tunnel runs from 175 to 185 degrees
        _arrow(ax, (x0 + 0.25 * inch, y1 + 0.30 * inch), (x0 + 0.25 * inch + L, y1 + 0.30 * inch), 0.07 * inch, 0.028 * inch, ref, 0.8, z=3)
        ax.text(x0 + 0.25 * inch + L + 0.06 * inch, y1 + 0.30 * inch, "wind, WD 175° to 185°", fontsize=TICK_PT, color=ref, ha="left", va="center_baseline", clip_on=False)
        gx, gy = x1 - 0.55 * inch, y1 + 0.10 * inch
        _arrow(ax, (gx, gy), (gx + 0.26 * inch, gy), 0.07 * inch, 0.028 * inch, ink, 0.9, z=3)
        _arrow(ax, (gx, gy), (gx, gy + 0.26 * inch), 0.07 * inch, 0.028 * inch, ink, 0.9, z=3)
        ax.text(gx + 0.30 * inch, gy, "N", fontsize=LABEL_PT, color=ink, ha="left", va="center_baseline", clip_on=False)
        ax.text(gx, gy + 0.30 * inch, "W", fontsize=LABEL_PT, color=ink, ha="center", va="bottom", clip_on=False)
    else:
        gx = x1 - 0.1 * inch
        _arrow(ax, (gx, y1 + 0.06 * inch), (gx, y1 + 0.40 * inch), 0.07 * inch, 0.028 * inch, ink, 0.9, z=3)
        ax.text(gx + 0.07 * inch, y1 + 0.40 * inch, "N", fontsize=LABEL_PT, color=ink, ha="left", va="center_baseline", clip_on=False)
    _ticks(ax, x0, x1, v["step"], "x", sym, unit, inch, ink)
    _ticks(ax, y0, y1, v["step"], "y", sym, unit, inch, ink)
    xa, ya = x0 - 0.74 * inch, y0 - 0.50 * inch
    _arrow(ax, (xa, ya), (xa + 0.30 * inch, ya), 0.07 * inch, 0.028 * inch, ink, 0.9)
    _arrow(ax, (xa, ya), (xa, ya + 0.30 * inch), 0.07 * inch, 0.028 * inch, ink, 0.9)
    ax.text(xa + 0.34 * inch, ya, "x", fontsize=LABEL_PT, ha="left", va="center_baseline", color=ink, clip_on=False)
    ax.text(xa, ya + 0.34 * inch, "y", fontsize=LABEL_PT, ha="center", va="bottom", color=ink, clip_on=False)
    ax.text(0.0, 1.0 + 0.06 / H_plan, "a", transform=ax.transAxes, fontsize=12, fontweight="bold", ha="left", va="bottom", color=ink)
    ax.text(0.20 / W, 1.0 + 0.065 / H_plan, "Plan", transform=ax.transAxes, fontsize=LABEL_PT + 1, ha="left", va="bottom", color=ink)

    # ---------------------------------------------------------------- strip under the plan: the elevation (C, D, M)
    if strip == "elevation":
        ae = frame(LEFT_D, y_strip, W, h_strip)
        ae.set_xlim(x0, x1)
        ae.set_ylim(0.0, z_view + band / scale)
        ae.plot([x0, x1], [0, 0], color=ink, lw=1.2, zorder=3, solid_capstyle="butt")
        if case == "M":
            ae.add_patch(Polygon([(x0, 0.0)] + [(round(float(a), 6), round(float(b), 6)) for a, b in zip(xs_sky, top_sky)] + [(x1, 0.0)], closed=True,
                                 facecolor=ps.FOOTPRINT, edgecolor=ink, linewidth=0.6, zorder=2))
        seen = set()
        for lo, hi in geo["boxes"]:
            k = (round(lo[0], 6), round(hi[0], 6), round(hi[2], 6))
            if k not in seen and hi[0] >= x0 and lo[0] <= x1:
                seen.add(k)
                ae.add_patch(Rectangle((lo[0], lo[2]), hi[0] - lo[0], hi[2] - lo[2], facecolor=ps.FOOTPRINT_FOCUS if hi[2] == top_z else ps.FOOTPRINT,
                                       edgecolor=ink, linewidth=0.7, zorder=2))
        if case == "C":
            ae.plot([-unit / 2, unit / 2], [unit, unit], color=ink, lw=0.8, ls=DOTTED, zorder=3)
            ae.text(0.0, 1.5 * unit, "centre block\n0D, 1D or 2D", fontsize=TICK_PT, color=ink, ha="center", va="center", zorder=7)
        if case == "D":
            ae.text(0.0, 0.6 * z_top, "tower", fontsize=TICK_PT, color=ink, ha="center", va="center", zorder=7)
        zs = sorted({round(r["z"], 6) for r in tab})
        if case != "M":
            xl, xr = min(stations), max(stations)
            ae.plot([xl, xr], [zs[0], zs[0]], color=ref, lw=1.0, ls=DOTTED, zorder=5)
            ae.text(xr + 0.12 * inch, zs[0] + 0.04 * inch, f"z = {_g(zs[0] / unit)} {sym}", fontsize=LABEL_PT, color=ink, ha="left", va="bottom", zorder=8,
                    bbox=dict(boxstyle="square,pad=0.08", facecolor=surface, edgecolor="none"))
        for x in stations:
            top = z_view + (row_of[x_in[x]] * ROW_IN + 0.04) * inch
            ae.plot([x, x], [0, top], color=ref, lw=0.9, ls=DOTTED, zorder=4, dash_capstyle="round")
            ae.text(x, top, labels[x], fontsize=TICK_PT, color=ink, ha="center", va="bottom", zorder=7, bbox=dict(boxstyle="square,pad=0.05", facecolor=surface, edgecolor="none"))
        used = []
        for rank, g in enumerate(gs):
            spots = sorted({(round(r["x"], 6), round(r["z"], 6)) for r in (tab[i] for i in g.members) if x0 <= r["x"] <= x1})
            ae.scatter([s_[0] for s_ in spots], [s_[1] for s_ in spots], s=_area(11.0, rank) * (2.2 if case == "M" else 1.0), color=g.colour,
                       edgecolor=_dark(g.colour), linewidth=0.25, zorder=6 + 0.1 * rank)
            for x in sorted({s_[0] for s_ in spots}):
                if all(abs(x_in[x] - u) > 0.24 for u in used):
                    used.append(x_in[x])
                    _ring(ae, x, -0.15 * inch, ring_r, g.letter, g.colour)
                    break
        if case == "M":
            sx, sy, sz = SOURCES["M"][0][1]
            ae.plot([sx], [sz], marker="*", ms=9.5, color=ink, mec=surface, mew=0.4, zorder=9, ls="none")
            ae.plot([MAST[0]], [MAST[2]], marker="s", ms=5.5, color=surface, mec=ink, mew=1.0, zorder=9, ls="none")
            ae.text(MAST[0] + 0.09 * inch, MAST[2], "R", fontsize=LABEL_PT, color=ink, ha="left", va="center_baseline", zorder=9, fontweight="bold")
        ae.text(0.0, 1.0 + 0.06 / h_strip, "b", transform=ae.transAxes, fontsize=12, fontweight="bold", ha="left", va="bottom", color=ink)
        ae.text(0.20 / W, 1.0 + 0.065 / h_strip, "Elevation", transform=ae.transAxes, fontsize=LABEL_PT + 1, ha="left", va="bottom", color=ink)
        xa, ya = x0 - 0.74 * inch, -0.10 * inch
        _arrow(ae, (xa, ya), (xa + 0.30 * inch, ya), 0.07 * inch, 0.028 * inch, ink, 0.9)
        _arrow(ae, (xa, ya), (xa, ya + 0.30 * inch), 0.07 * inch, 0.028 * inch, ink, 0.9)
        ae.text(xa + 0.34 * inch, ya, "x", fontsize=LABEL_PT, ha="left", va="center_baseline", color=ink, clip_on=False)
        ae.text(xa, ya + 0.34 * inch, "z", fontsize=LABEL_PT, ha="center", va="bottom", color=ink, clip_on=False)

    # ---------------------------------------------------------------- strip beside the plan: the heights at the points of F
    if strip == "heights":
        ids = sorted({place[p] for p in place})
        k_in, slot, left_pad = 0.125, 0.162, 0.52           # inches per metre of height; between two points; room for the plane labels
        w_s = left_pad + slot * len(ids) + 0.12
        h_s = 22.0 * k_in
        xs_in = LEFT_D + W + 0.40
        ah = frame(xs_in, y_plan + H_plan - h_s, w_s, h_s)
        ah.set_xlim(0.0, w_s)
        ah.set_ylim(0.0, h_s)
        ah.plot([0.0, w_s], [0, 0], color=ink, lw=1.2, zorder=3, solid_capstyle="butt")
        slot_x = {n: left_pad + slot * (i + 0.5) for i, n in enumerate(ids)}
        for n in ids:
            ah.plot([slot_x[n]] * 2, [0, h_s - 0.06], color=ref, lw=0.9, ls=DOTTED, zorder=4, dash_capstyle="round")
            ah.text(slot_x[n], -0.05, str(n), fontsize=NUM_PT, color=ink, ha="center", va="top", clip_on=False)
        ah.text(left_pad + 0.5 * slot * len(ids), -0.24, "point", fontsize=TICK_PT, color=ink, ha="center", va="top", clip_on=False)
        for g in gs:
            if g.letter == "D":
                continue
            h = {"A": 5.0, "B": 9.0, "C": 20.0}[g.letter]
            ah.plot([left_pad, w_s - 0.04], [h * k_in] * 2, color=g.colour, lw=1.1, ls=DOTTED, zorder=5, dash_capstyle="round")
            _ring(ah, 0.14, h * k_in, 0.082, g.letter, g.colour)
            ah.text(0.26, h * k_in, f"{h:g} m", fontsize=TICK_PT, color=ink, ha="left", va="center_baseline", zorder=8)
        for rank, g in enumerate(gs):
            spots = sorted({(place[(round(tab[i]["x"], 6), round(tab[i]["y"], 6))], round(tab[i]["z"], 6)) for i in g.members})
            xs_ = [slot_x[n] + (0.058 if g.letter == "D" else 0.0) for n, _ in spots]
            hs_ = [(z - F_RAISE) * k_in for _, z in spots]
            ah.scatter(xs_, hs_, s=(13.0 if g.letter != "D" else 15.0), marker="D" if g.letter == "D" else "o", color=g.colour, edgecolor=_dark(g.colour),
                       linewidth=0.25, zorder=6 + 0.1 * rank)
        for hh in (0, 10, 20):
            ah.plot([0.0, -0.05], [hh * k_in] * 2, color=ink, lw=0.7, clip_on=False)
            ah.text(-0.08, hh * k_in, f"{hh}", fontsize=TICK_PT, color=ink, ha="right", va="center_baseline", clip_on=False)
        ah.text(0.0, 1.0 + 0.06 / h_s, "b", transform=ah.transAxes, fontsize=12, fontweight="bold", ha="left", va="bottom", color=ink)
        ah.text(0.22 / w_s, 1.0 + 0.065 / h_s, "Heights above ground [m]", transform=ah.transAxes, fontsize=LABEL_PT + 1, ha="left", va="bottom", color=ink)
        side = 2.2                                           # the whole model disc, with the window of the plan
        ao = frame(xs_in + 0.5 * (w_s - side), y_plan + H_plan - h_s - 0.85 - side, side, side)
        ao.set_xlim(-DISC_F * 1.05, DISC_F * 1.05)
        ao.set_ylim(-DISC_F * 1.05, DISC_F * 1.05)
        ao.add_collection(LineCollection(geo["segs"], colors=ref, linewidths=0.12, zorder=2))
        th = np.linspace(0.0, 2 * math.pi, 361)
        ao.plot(np.round(DISC_F * np.cos(th), 6), np.round(DISC_F * np.sin(th), 6), color=ink, lw=0.8, zorder=3)
        ao.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="none", edgecolor=ink, linewidth=0.9, linestyle=DOTTED, zorder=4))
        ao.text(0.0, 1.0 + 0.06 / side, "c", transform=ao.transAxes, fontsize=12, fontweight="bold", ha="left", va="bottom", color=ink)
        ao.text(0.22 / side, 1.0 + 0.065 / side, f"Model disc, radius {DISC_F:g} m", transform=ao.transAxes, fontsize=LABEL_PT + 1, ha="left", va="bottom", color=ink)

    # ---------------------------------------------------------------- title, scale note, legend
    fig.text(0.5, 1 - 0.30 / fig_h, f"AIJ UWE Case {case} — measurement points", ha="center", va="center", fontsize=13, fontweight="bold", color=ink)
    scale_txt = note + ("; " + NOTES[case] if case in NOTES else "")
    fig.text((LEFT_D + W) / FIG_WIDTH, (bottom - 0.12) / fig_h, scale_txt, ha="right", va="top", fontsize=LABEL_PT + 0.4, color=ink)
    fig.legend(handles=handles, loc="lower center", ncols=ncols, frameon=False, fontsize=LABEL_PT + 1.4, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.5, handletextpad=0.5, columnspacing=1.8, labelspacing=0.55, borderaxespad=0.15)
    return fig
