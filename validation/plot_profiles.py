"""Vertical profiles of the streamwise velocity, measured points against the modelled line, for every case measured on
vertical lines beyond Cases A and B (validation/plot_cases_ab_openfoam.py draws those two):

  figures/case-{g,h,i,j,k,l}-openfoam-profiles.png
      U/U_H against z/H on the centre plane y = 0 (Case G: the field's seven masts) at up to four stations spread along
      the measured lines, each offset by 1 so they do not overplot.

Inputs: the pairs snapshots validation/results/case{id}_<engine>_pairs.csv, the values the API serves per point. Cases J
and L are solved with urbanMicroclimateFoam, the OpenFOAM 12 solver for non-isothermal flow; Case G shows the conifer
arm of the drag sweep, Case I the realizable k-epsilon run.
"""
from __future__ import annotations

import csv
import io
import math
import os

import numpy as np
import ultraplot as uplt

import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

# case: (engine, row filter, what the model line is), and H in the pairs' length unit (cases/{id}.json configuration.H_m)
H_M = {"G": 7.0, "H": 0.2, "I": 0.1, "J": 0.16, "K": 0.06, "L": 0.06}
CASES = {
    "G": ("openfoam12_realizableKE", lambda r: r["arm"] == "conifer", "Eddy3D (OpenFOAM 12, realizable k-ε), conifer crown"),
    "H": ("openfoam12_realizableKE", None, "Eddy3D (OpenFOAM 12, realizable k-ε)"),
    "I": ("openfoam12_realizableKE", lambda r: r["instrument"] == "ldv", "Eddy3D (OpenFOAM 12, realizable k-ε)"),
    "J": ("umf_realizableKE", None, "Eddy3D (OpenFOAM 12, urbanMicroclimateFoam, realizable k-ε)"),
    "K": ("openfoam12_realizableKE", None, "Eddy3D (OpenFOAM 12, realizable k-ε)"),
    "L": ("umf_realizableKE", None, "Eddy3D (OpenFOAM 12, urbanMicroclimateFoam, realizable k-ε)"),
}
MIN_HEIGHTS = 4      # a station is drawn when it has at least this many heights
STATIONS = 4


def num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return math.nan
    return f


def rows_of(case, engine, keep):
    with io.open(os.path.join(RESULTS, f"case{case}_{engine}_pairs.csv"), encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if keep is None or keep(r)]
    return [r for r in rows if ("y" not in r or abs(num(r["y"])) < 1e-6) and math.isfinite(num(r["U_meas"])) and math.isfinite(num(r["U_model"]))]


def stations_of(rows):
    """Up to STATIONS stations with enough heights, spread from the first to the last."""
    by = {}
    for r in rows:
        by.setdefault(round(num(r["x"]), 6), []).append(r)
    xs = sorted(x for x, rs in by.items() if len({round(num(r["z"]), 6) for r in rs}) >= MIN_HEIGHTS)
    if len(xs) <= STATIONS:
        return [(x, by[x]) for x in xs]
    pick = sorted({xs[round(i * (len(xs) - 1) / (STATIONS - 1))] for i in range(STATIONS)})
    return [(x, by[x]) for x in pick]


style.apply()
for case, (engine, keep, model_label) in CASES.items():
    H = H_M[case]
    stations = stations_of(rows_of(case, engine, keep))
    fig, axs = uplt.subplots(nrows=1, ncols=1, refwidth=4.2, refaspect=1.25, share=False)
    ax = axs[0]
    lohi, zmax, centres = [], 0.0, []
    for j, (x, rs) in enumerate(stations):
        rs = sorted(rs, key=lambda r: num(r["z"]))
        z = np.array([num(r["z"]) / H for r in rs])
        um = np.array([num(r["U_meas"]) for r in rs])
        up = np.array([num(r["U_model"]) for r in rs])
        off = j * 1.0                      # offset each station so they do not overplot
        ax.plot(up + off, z, color=style.OPENFOAM, lw=1.8, zorder=3)
        ax.scatter(um + off, z, s=22, color=style.MEASURED, edgecolor=style.SURFACE, linewidth=0.5, zorder=4)
        lo_, hi_ = float(np.nanmin(np.concatenate([up, um]))) + off, float(np.nanmax(np.concatenate([up, um]))) + off
        lohi += [lo_, hi_]
        centres.append((lo_ + hi_) / 2)
        zmax = max(zmax, float(z.max()))
    top = max(1.18 * zmax, 1.25)            # the roof (or tree-top) line always shows
    for (x, _), xc in zip(stations, centres):
        ax.text(xc, top * 0.975, f"x/H = {x / H:+.2f}", ha="center", va="top", fontsize=8.5, color=style.REFERENCE, zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", facecolor=style.SURFACE, edgecolor="none"))
    roof = "tree height, z = H" if case == "G" else "roof height, z = H"
    ax.axhline(1.0, color=style.REFERENCE, lw=0.8, ls="--", zorder=1)
    ax.format(xlabel="U/U$_H$ [–], offset by 1 per station", ylabel="z/H [–]", ylim=(0, top),
              xlim=(min(lohi) - 0.3, max(lohi) + 0.3), abc=False)
    style.finish(fig, f"AIJ UWE Case {case} — vertical profiles" + (" behind the tree belt" if case == "G" else " on the centre plane (y = 0)"),
                 handles=[style.marker(style.MEASURED, "Field" if case == "G" else "Wind tunnel"), style.line(style.OPENFOAM, model_label),
                          style.line(style.REFERENCE, roof, lw=0.8, ls="--")], ncols=1)
    style.save(fig, f"case-{case.lower()}-openfoam-profiles.png")
    print(case, [round(x / H, 2) for x, _ in stations])
