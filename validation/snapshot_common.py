"""What the Case G, K, J and L scripts (plot_cases_gk_openfoam.py, plot_cases_jl_umf.py) share: finding Eddy3D's studies, writing
a snapshot (LF text, no absolute paths, the SHA-256 of every file it came from), the pairs files, and the scatter panels.

Same method as plot_cases_hi_openfoam.py for Cases H and I: the measured side of every pair is the cleaned table
(clean/cases/<id>/points.csv, the legacy workbook at full precision), the modelled side is the probe the Eddy3D fixture wrote at the
tunnel's own coordinates, and every score is computed FROM THE PAIRS by dispersion_metrics.py. The snapshots are refreshed from the
studies only where they exist (EDDY3D_VAL, C:/Eddy3DVal or ~/Eddy3DVal); everywhere else, the build included, the committed
snapshots are checked against the committed pairs and the figures are drawn from them.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os

import numpy as np

import dispersion_metrics as DM
import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RESULTS = os.path.join(HERE, "results")
SPECIES = [("sct03", "Sct 0.3"), ("sct05", "Sct 0.5"), ("sct07", "Sct 0.7")]


def validation_root(*folders):
    """The first of EDDY3D_VAL, C:/Eddy3DVal, ~/Eddy3DVal that holds every one of `folders`, or None."""
    for p in (os.environ.get("EDDY3D_VAL"), r"C:/Eddy3DVal", os.path.expanduser("~/Eddy3DVal")):
        if p and all(os.path.isdir(os.path.join(p, f)) for f in folders):
            return p
    return None


def write_lf(dest, text):
    with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_lf(src):
    with io.open(src, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def sha256(path):
    """SHA-256 of a file as it is stored, in 1 MB reads (the UMF probe files are 10 to 22 MB)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_table(case):
    with io.open(os.path.join(REPO, "clean", "cases", case, "points.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(v):
    return float(v) if v not in ("", None) else math.nan


def write_pairs(path, fields, rows):
    """A pairs file: LF, the header, then one line per row; NaN is an empty cell and a float is written by repr()."""
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if (isinstance(v, (float, np.floating)) and math.isnan(v)) else repr(float(v)) if isinstance(v, (float, np.floating)) else v)
                        for k, v in r.items()})


def read_pairs(path):
    return DM.read_pairs(path)


def column(rows, key):
    return np.array([p[key] for p in rows], float)


def is_score(v):
    return isinstance(v, dict) and "Fb" in v and "R" in v


def raw_table(name):
    """A benchmark CSV as published (raw/cases/<name>): headers cut at the unit, -999.9 = NaN; the fixtures' own measured side."""
    with io.open(os.path.join(REPO, "raw", "cases", name), encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        head = [h.split("(")[0].split("[")[0].strip() for h in next(rd)]
        rows = [r for r in rd if any(c.strip() for c in r)]
    return {h: np.array([math.nan if abs(float(r[i]) + 999.9) < 1e-6 else float(r[i]) for r in rows]) for i, h in enumerate(head)}


def non_scores(fixture, drop=()):
    """The fixture's results.json without its scores (those are recomputed) and without the keys starting with `drop`."""
    return {k: v for k, v in fixture.items() if not is_score(v) and not k.startswith(tuple(drop))}


def write_json(path, res):
    write_lf(path, json.dumps(res, indent=1, ensure_ascii=False, allow_nan=False) + "\n")


def read_json(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def same_score(got, want):
    if isinstance(want, dict):
        return DM.same(got, want)
    return abs(got - want) <= 1e-9 * max(1.0, abs(want))


def check_snapshot(res_path, scores):
    """The committed scores are what the committed pairs give: fail otherwise (scores = {key: dict or number} from the pairs)."""
    res = read_json(res_path)
    for key, want in scores.items():
        assert same_score(res[key], want), (os.path.basename(res_path), key, res[key], want)


def mirror_mean(points, values, tol=1e-6):
    """Each point's value averaged with its mirror's across y = 0 (its own value when y = 0); NaN where the mirror is absent.
    Scoring the measurement against THIS is the ceiling of a y-symmetric model (CubeArrayCase.MirrorMean in the Eddy3D fixture)."""
    pts = np.asarray(points, float)
    out = np.full(len(pts), math.nan)
    for i, (x, y, z) in enumerate(pts):
        j = np.where((abs(pts[:, 0] - x) < tol) & (abs(pts[:, 1] + y) < tol) & (abs(pts[:, 2] - z) < tol))[0]
        if len(j):
            out[i] = 0.5 * (values[i] + values[j[0]])
    return out


# ----------------------------------------------------------------------------- figures

def panel(ax, o, p, color, log=False, xlab=None, ylab=None, hollow=None, decades=5):
    """Measured o against modelled p with the 1:1 line (and the factor-of-two band where the values do not change sign); returns
    how many pairs are drawn. `hollow` is a boolean array (over the finite pairs' original order) of points drawn open. `color` is
    one colour, or one colour per pair (layout.grouped_colours: the group of the line or plane each point was measured on)."""
    o, p = np.asarray(o, float), np.asarray(p, float)
    ok = np.isfinite(o) & np.isfinite(p)
    open_ = np.zeros(len(o), bool) if hollow is None else np.asarray(hollow, bool)
    per_point = not isinstance(color, str)
    col = np.asarray(color, dtype=object) if per_point else np.zeros(len(o), dtype=object)
    o, p, open_, col = o[ok], p[ok], open_[ok], col[ok]
    if log:                                   # a log axis shows the positive pairs only; the statistics use all of them
        keep = (o > 0) & (p > 0)
        o, p, open_, col = o[keep], p[keep], open_[keep], col[keep]
        hi = 10 ** math.ceil(math.log10(max(o.max(), p.max())))
        lo = max(10 ** math.floor(math.log10(min(o.min(), p.min()))), hi * 10.0 ** -decades)     # `decades` at most; pairs below are not drawn
        shown = (o >= lo) & (p >= lo)
        o, p, open_, col = o[shown], p[shown], open_[shown], col[shown]
        ax.format(xscale="log", yscale="log")
    else:
        lo, hi = float(min(o.min(), p.min())), float(max(o.max(), p.max()))
        pad = 0.08 * (hi - lo) if hi > lo else 0.1
        lo, hi = lo - pad, hi + pad
    style.one_to_one(ax, lo, hi, factor_two=bool(log or (o > 0).all()))
    s = 9 if len(o) > 300 else 14
    ax.scatter(o[~open_], p[~open_], s=s, color=list(col[~open_]) if per_point else color, edgecolor=style.SURFACE, linewidth=0.25, alpha=0.9, zorder=3)
    if open_.any():
        ax.scatter(o[open_], p[open_], s=s + 6, facecolor="none", edgecolor=list(col[open_]) if per_point else color, linewidth=0.8, zorder=4)
    ax.format(xlim=(lo, hi), ylim=(lo, hi), xlabel=xlab, ylabel=ylab)
    return len(o)


def stats_text(m, n_shown=None):
    fb = "n/a" if m["Fb"] is None else f"{m['Fb']:+.2f}"      # undefined when the signed means differ in sign (dispersion_metrics.py)
    r = "n/a" if m["R"] is None else f"{m['R']:+.2f}"
    t = f"R {r}\nFAC2 {m['Fac2']:.2f}\nFB {fb}\nn {m['Count']}"
    if n_shown is not None and n_shown != m["Count"]:
        t += f" ({n_shown} shown)"
    return t
