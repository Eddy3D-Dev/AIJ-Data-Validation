"""Grid uncertainty of the OpenFOAM fixtures of Cases A and E: one figure per case, answering one question.

  figures/case-a-openfoam-grid.png   How much of a point's value is the mesh?  Measured against modelled U, V, W and k on the
                                     second of four meshes (cell scale 1.00), each point with that mesh's band; hollow where the
                                     point has none.
  figures/case-e-openfoam-grid.png   The same for sqrt(|U|^2 + 2k) at z = 2 m, before and after construction.

The band (validation/snapshot_grid.py) is Roache's grid convergence index of the 1.00 mesh where the four-mesh ladder converges
monotonically at the point, half the spread of the three meshes where it oscillates, and none where the change grows under
refinement. Inputs: validation/results/grid/case{A,E}_openfoam12_realizableKE.{csv,json}, the study's own measured and modelled
values. The study ran the fixture with the eddy-viscosity cap lifted (the eddy3d-of12-nutcap-lifted configuration), so its values
are not the served run's, which keeps OpenFOAM's cap.

Colours (plotstyle.py): the dots take the colour of the line, plane or group they were measured on, as in the agreement figures.
"""
from __future__ import annotations

import csv
import io
import json
import math
import os

import numpy as np
import ultraplot as uplt

import layout
import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, "results", "grid")


def read(case):
    base = os.path.join(GRID, f"case{case}_openfoam12_realizableKE")
    with io.open(base + ".csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with io.open(base + ".json", encoding="utf-8") as f:
        return rows, json.load(f)


def num(v):
    return float(v) if v not in ("", None) else math.nan


def points(rows):
    return [{"x": float(r["x"]), "y": float(r["y"]), "z": float(r["z"])} for r in rows]


def fac2_range(scores):
    v = [s["Fac2"] for s in scores if s]
    return f"FAC2 {min(v):.2f}–{max(v):.2f}, {len(v)} meshes"


def panel(ax, o, p, b, colours, factor_two, scores):
    """One measured-against-modelled panel with a vertical bar of +-band per point; returns nothing, draws everything."""
    ok = np.isfinite(o) & np.isfinite(p)
    o, p, b, colours = o[ok], p[ok], b[ok], np.array(colours, dtype=object)[ok]
    has = np.isfinite(b)
    # The limits are the data's, as in the agreement figures: the few bars wider than the panel run off its edge.
    lo = float(min(o.min(), p.min()))
    hi = float(max(o.max(), p.max()))
    pad = 0.08 * (hi - lo) if hi > lo else 0.1
    lo, hi = lo - pad, hi + pad
    style.one_to_one(ax, lo, hi, factor_two=factor_two)
    ax.vlines(o[has], (p - b)[has], (p + b)[has], colors=list(colours[has]), linewidth=0.7, zorder=2)
    ax.scatter(o[has], p[has], s=15, color=list(colours[has]), edgecolor=style.SURFACE, linewidth=0.35, zorder=3)
    ax.scatter(o[~has], p[~has], s=15, facecolor="none", edgecolor=list(colours[~has]), linewidth=0.8, zorder=3)
    style.stats(ax, f"band ±{np.median(b[has]):.3f} median\n{int(has.sum())}/{len(b)} with band\n{fac2_range(scores)}", halo="auto")
    ax.format(xlim=(lo, hi), ylim=(lo, hi))


def legend_entries():
    return [style.line(style.REFERENCE, "band, second mesh", lw=0.7),
            style.marker(style.REFERENCE, "no band", filled=False),
            style.line(style.REFERENCE, "1:1", lw=1.0), style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")]


# ----------------------------------------------------------------------------- Case A
QUANTITIES = [("U", "U/U$_H$"), ("V", "V/U$_H$"), ("W", "W/U$_H$"), ("k", "k/U$_H^2$")]

style.apply()
rows, summary = read("A")
colours = layout.grouped_colours("A", points(rows))
fig, axs = uplt.subplots(nrows=1, ncols=4, refwidth=2.0, refaspect=1, share=False, wspace=4.2)
for col, (q, _) in enumerate(QUANTITIES):
    o = np.array([num(r[f"{q}_meas"]) for r in rows])
    p = np.array([num(r[f"{q}_model"]) for r in rows])
    b = np.array([num(r[f"{q}_band"]) for r in rows])
    panel(axs[col], o, p, b, colours, q == "k" or bool((o[np.isfinite(o)] > 0).all()), summary["scores_on_each_grid"][q])
    axs[col].format(xlabel="Tunnel [–]", ylabel="Eddy3D [–]" if col == 0 else None)
style.finish(fig, "AIJ UWE Case A — grid uncertainty, OpenFOAM 12 (cap lifted)",
             handles=[*layout.legend_handles("A"), *legend_entries()], ncols=3, toplabels=[label for _, label in QUANTITIES])
style.save(fig, "case-a-openfoam-grid.png")

# ----------------------------------------------------------------------------- Case E
STATES = [("bc", "before", "Before construction"), ("ac", "after", "After construction")]

rows, summary = read("E")
fig2, axs2 = uplt.subplots(nrows=1, ncols=2, refwidth=2.6, refaspect=1, share=False, wspace=4.2)
for i, (state, label, title) in enumerate(STATES):
    sel = [r for r in rows if r["config"] == state]
    o = np.array([num(r["measured_ratio"]) for r in sel])
    p = np.array([num(r["scalar_ratio"]) for r in sel])
    b = np.array([num(r["scalar_band"]) for r in sel])
    panel(axs2[i], o, p, b, layout.grouped_colours("E", points(sel)), True, summary["scores_on_each_grid"][f"{label}, √(|U|²+2k)"])
    axs2[i].format(xlabel="Tunnel velocity ratio [–]", ylabel="Eddy3D √(|U|²+2k)/U$_{ref}$ [–]" if i == 0 else None,
                   title=f"{title}, wind from SW")
legend = layout.legend_rows("E", legend_entries())
style.finish(fig2, "AIJ UWE Case E — grid uncertainty, OpenFOAM 12 (cap lifted), z = 2 m",
             handles=legend[0], ncols=legend[1])
style.save(fig2, "case-e-openfoam-grid.png")
