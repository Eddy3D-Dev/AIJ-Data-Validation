"""Field maps of Eddy3D's solves on the measurement planes, with the tunnel's (or field's) points drawn on them:

  figures/case-{x}-{engine}-field-plan.png       a horizontal plane of measured points, near the ground
  figures/case-{x}-{engine}-field-section.png    the vertical plane through the points, y = 0

Three panels on one plane, one question each:
  a  u (along x) over the case's speed: where the flow is fast, slow or reversed;
  b  the same u, with iso-lines every 0.1 and the edge of the reversed flow (u = 0) dashed: its shape, read off by number;
  c  the in-plane speed with streamlines: where the air goes.
Each measured point is a dot coloured by the MEASURED value on the panel's own colour scale, so a dot that stands out from the
field around it is a point the model misses. a and b take the measured u, c the measured in-plane speed (or the scalar speed
where only that was measured, Case F). Case F has no measured u and Case G no lateral component, so their dots sit on the panels
whose quantity was measured. Case F's wind blows from NNW across the map, so its a and b show the component along the wind.
Planes narrower than 1.8 : 1 put the three panels side by side, the rest stack them.

Inputs, all in this repository: the planes sampled from the solves (validation/results/planes/case{X}-{plane}.json, written by
extract_planes.py, which holds the frame, the speed and the check against the served pairs) and the pairs files beside them.
Colours follow plotstyle.py: ultraplot's diverging BuRd, centred on 0 for u and on the reference speed for the speed (blue below,
red above); buildings white with an ink outline; reference lines ink, thin.
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import sys

import numpy as np
import ultraplot as uplt
from matplotlib.collections import LineCollection
from matplotlib.colors import TwoSlopeNorm

import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
PLANES = os.path.join(RESULTS, "planes")
OF12 = "Eddy3D (OpenFOAM 12, realizable k-ε)"
UMF = "Eddy3D (OpenFOAM 12, urbanMicroclimateFoam, realizable k-ε)"

# case: engine in the file name, model label, rows kept, measured columns (u, lateral, vertical, scalar speed), the speed
# scale of c (lo, hi, centre), what the speed is divided by, and the planes: (file stem, kind, title of the plane)
CASES = {
    "A": ("openfoam", OF12, None, ("U_meas", "V_meas", "W_meas", None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("z0p01", "plan", "z = 0.01 m (z/H = 0.06)"), ("y0", "section", "centre plane y = 0")]),
    "F": ("openfoam", OF12 + ", wind from NNW", lambda r: r["frame"] == "agl" and r["source"] == "tunnel", (None, None, None, "observed"),
          (0.0, 0.6, 0.3), "U_{500}", [("z14", "plan", "9 m above the ground (z = 14 m)")]),
    "G": ("openfoam", OF12 + ", conifer crown", lambda r: r["arm"] == "conifer", ("U_meas", None, None, None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("y0", "section", "vertical plane through the masts")]),
    "H": ("openfoam", OF12, None, ("U_meas", "V_meas", "W_meas", None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("z0p0125", "plan", "z = 0.0125 m (z/H = 0.06)"), ("y0", "section", "centre plane y = 0")]),
    "I": ("openfoam", OF12, lambda r: r["instrument"] == "ldv", ("U_meas", "V_meas", "W_meas", None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("y0", "section", "centre plane y = 0")]),
    "J": ("umf", UMF, None, ("U_meas", "V_meas", "W_meas", None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("z0p04", "plan", "z = 0.04 m (z/H = 0.25)"), ("y0", "section", "centre plane y = 0")]),
    "K": ("openfoam", OF12, None, ("U_meas", "V_meas", "W_meas", None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("z0p01", "plan", "z = 0.01 m (z/H = 0.17)"), ("y0", "section", "centre plane y = 0")]),
    "L": ("umf", UMF, None, ("U_meas", "V_meas", "W_meas", None), (0.0, 1.5, 1.0), "U_\\mathrm{H}",
          [("z0p01", "plan", "z = 0.01 m (z/H = 0.17)"), ("y0", "section", "centre plane y = 0")]),
    "M": ("openfoam", OF12 + ", tunnel WD 180", None, ("U_meas", "V_meas", "W_meas", None), (0.0, 1.2, 0.6), "U_\\mathrm{R}",
          [("z35p5", "plan", "pedestrian level of the campus (z = 35.5 m above the tunnel floor)")]),
}
U_LIM = {"F": (-0.6, 0.6)}          # u's colour scale where the default (-1, 1.5) would wash the map out
ALONG = {"F": 157.5}                # Case F: a and b show the component along the wind (the bearing it blows toward, from north)
ROW = 1.8                           # planes narrower than this (width / height) put their panels side by side
STEP = 0.1        # iso-lines of panel b


def fnum(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return math.nan
    return f


def read_plane(case, stem):
    with io.open(os.path.join(PLANES, f"case{case}-{stem}.json"), encoding="utf-8") as f:
        d = json.load(f)
    arr = lambda k: np.array([[math.nan if v is None else v for v in row] for row in d[k]], dtype=float)  # noqa: E731
    even = lambda v: np.linspace(v[0], v[-1], len(v))  # noqa: E731  the stored axes are rounded; streamplot wants them exactly even
    return d, even(d["x"]), even(d["a"]), arr("u"), arr("s")


def measured(case, d, cols, keep):
    """The pairs on the plane: in-plane coordinates and the measured u, in-plane speed (or scalar speed)."""
    p = d["plane"]
    zcol = "z_probe" if case == "F" else "z"
    with io.open(os.path.join(RESULTS, d["pairs"]), encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if keep is None or keep(r)]
    tol = 0.5 if case == "M" else 1e-6
    on = [r for r in rows if abs(fnum(r[zcol] if p["axis"] == "z" else r.get("y", 0.0) or 0.0) - p["value"]) <= tol]
    a_col = "y" if p["axis"] == "z" else zcol
    xs = np.array([fnum(r["x"]) for r in on])
    As = np.array([fnum(r[a_col]) for r in on])
    ucol, vcol, wcol, scol = cols
    u = np.array([fnum(r[ucol]) for r in on]) if ucol else np.full(len(on), math.nan)
    second = vcol if p["axis"] == "z" else wcol
    if scol:
        speed = np.array([fnum(r[scol]) for r in on])
    elif second:
        speed = np.hypot(u, np.array([fnum(r[second]) for r in on]))
    else:
        speed = np.full(len(on), math.nan)
    return xs, As, u, speed


def draw(case, stem, kind, where):
    engine, model, keep, cols, (mlo, mhi, mc), uname, _ = CASES[case]
    d, gx, ga, U, S = read_plane(case, stem)
    L, Lname = d["L"], d["Lname"]
    scale = (lambda v: np.asarray(v) / L) if Lname != "1 m" else (lambda v: np.asarray(v))
    X, A = np.meshgrid(scale(gx), scale(ga))
    mag = np.hypot(U, S)
    uq = "u"
    if case in ALONG:                   # x east, y north: project on the wind
        b = math.radians(ALONG[case])
        U_a = U * math.sin(b) + S * math.cos(b)
        uq = r"u_\mathrm{wind}"
    else:
        U_a = U
    xs, As, mu, mspeed = measured(case, d, cols, keep)
    xs, As = scale(xs), scale(As)
    seg = np.array(d["outline"], dtype=float).reshape(-1, 2, 2)
    if len(seg):
        seg = scale(seg)

    horizontal = d["plane"]["axis"] == "z"
    xl = "x/H [–]" if Lname == "H" else "x [m]"
    al = ("y/H [–]" if horizontal else "z/H [–]") if Lname == "H" else ("y [m]" if horizontal else "z [m]")
    xr, ar = X.max() - X.min(), A.max() - A.min()
    row = xr / ar < ROW
    style.apply()
    if row:
        fig, axs = uplt.subplots(nrows=1, ncols=3, refwidth=2.7, refaspect=xr / ar, sharex=True, sharey=True, wspace="1.8em")
    else:
        fig, axs = uplt.subplots(nrows=3, ncols=1, refwidth=4.4, refaspect=xr / ar, sharex=True, sharey=True, hspace="1em")
    ulim = U_LIM.get(case, (-1.0, 1.5))
    panels = [(U_a, mu, ulim, 0.0, rf"${uq}/{uname}$ [–]"), (U_a, mu, ulim, 0.0, rf"${uq}/{uname}$ [–]"),
              (mag, mspeed, (mlo, mhi), mc, rf"$|\mathbf{{u}}|/{uname}$ [–]")]
    for k, (ax, (F, M, (lo, hi), c, lab)) in enumerate(zip(axs, panels)):
        norm = TwoSlopeNorm(vcenter=c, vmin=lo, vmax=hi)
        Fm = np.ma.masked_invalid(F)
        m = ax.pcolormesh(X, A, Fm, cmap="BuRd", norm=norm, shading="gouraud", rasterized=True, discrete=False)
        if k == 1:
            levels = [v for v in np.round(np.arange(lo, hi + 1e-9, STEP), 6) if abs(v) > 1e-9]
            ax.contour(X, A, Fm, levels=levels, colors=style.INK, linewidths=0.45, alpha=0.5, linestyles="-", zorder=2, labels=False)
            ax.contour(X, A, Fm, levels=[0.0], colors=style.INK, linewidths=1.3, linestyles="--", zorder=3, labels=False)
        if k == 2:
            ax.streamplot(X[0], A[:, 0], np.nan_to_num(U), np.nan_to_num(S), color=style.INK, linewidth=0.5,
                          density=(2.4, float(np.clip(2.4 * ar / xr, 0.6, 2.4)) if not row else 1.6), arrowsize=0.6, zorder=2)
        if len(seg):
            ax.add_collection(LineCollection(seg, colors=style.INK, linewidths=1.2, zorder=5))
        good = np.isfinite(M)
        if good.any():
            ax.scatter(xs[good], As[good], c=M[good], cmap="BuRd", norm=norm, s=16, edgecolor=style.INK, linewidth=0.55, zorder=6)
        ax.colorbar(m, loc="b" if row else "r", label=lab, width=0.12, length=0.95)
        last = row or k == 2
        ax.format(xlim=(X.min(), X.max()), ylim=(A.min(), A.max()), aspect="equal", grid=False,
                  xlabel=xl if last else "", xticklabels=None if last else [], ylabel=al if (k == 0 or not row) else "", yticklabels=None if (k == 0 or not row) else [])
    style.finish(fig, f"AIJ UWE Case {case} — {where}",
                 handles=[style.marker(style.MEASURED, "Measured (dot colour: measured value)"), style.line(style.INK, f"{model}: streamlines", lw=0.6),
                          style.line(style.INK, f"${uq}$ = 0, edge of the reversed flow", lw=1.3, ls="--")], ncols=3 if row else 1)
    style.save(fig, f"case-{case.lower()}-{engine}-field-{kind}.png")


for case, spec in CASES.items():
    if sys.argv[1:] and case not in sys.argv[1:]:
        continue
    for stem, kind, where in spec[-1]:
        draw(case, stem, kind, where)
