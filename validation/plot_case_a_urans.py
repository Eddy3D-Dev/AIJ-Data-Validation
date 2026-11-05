"""Case A: the served steady run (RANS) and the same solver run transient (URANS), score by score.

  figures/case-a-openfoam-rans-urans.png
      One panel per metric (R, FAC2, FB, hit rate), one row per quantity (U, V, W, k), the two runs as two marks joined by a
      line: which run scores better, and by how much, at a glance. The scores are the ones the case page's table prints.

Inputs, all in this repository: validation/results/caseA_openfoam12_realizableKE.json (the served run) and
validation/results/submissions/eddy3d-of12-sst-urans/A.json (the transient run, scored as a submission).
"""
from __future__ import annotations

import io
import json
import os

import ultraplot as uplt
from matplotlib.lines import Line2D

import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
QUANTITIES = [("velocity.U", "U"), ("velocity.V", "V"), ("velocity.W", "W"), ("k", "k")]
# metric, panel title, axis limits, the value a perfect model scores
METRICS = [("R", "R", (0.0, 1.05), 1.0), ("Fac2", "FAC2", (0.0, 1.05), 1.0), ("Fb", "FB", (-1.6, 0.6), 0.0), ("HitRate", "Hit rate", (0.0, 1.05), 1.0)]


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


rans = read(os.path.join(RESULTS, "caseA_openfoam12_realizableKE.json"))
urans = read(os.path.join(RESULTS, "submissions", "eddy3d-of12-sst-urans", "A.json"))["scores"]

style.apply()
fig, axs = uplt.subplots(ncols=4, refwidth=1.7, refaspect=1.1, sharey=True, wspace="1.2em")
ys = list(range(len(QUANTITIES)))[::-1]
for i, (ax, (m, title, lim, best)) in enumerate(zip(axs, METRICS)):
    ax.axvline(best, color=style.REFERENCE, lw=0.8, ls="--", zorder=1)
    for y, (key, _) in zip(ys, QUANTITIES):
        a, b = rans[key].get(m), urans[key].get(m)
        if a is not None and b is not None:
            ax.plot([a, b], [y, y], color=style.OPENFOAM, lw=1.2, alpha=0.6, zorder=2)
        if a is not None:
            ax.scatter([a], [y], s=34, facecolor=style.SURFACE, edgecolor=style.OPENFOAM, linewidth=1.3, zorder=3)
        if b is not None:
            ax.scatter([b], [y], s=34, marker="s", color=style.OPENFOAM, edgecolor=style.SURFACE, linewidth=0.4, zorder=4)
    ax.format(title=title, xlim=lim, ylim=(-0.6, len(QUANTITIES) - 0.4), yticks=ys,
              yticklabels=[f"${lab}$" for _, lab in QUANTITIES] if i == 0 else [], ylabel="", xlabel="", gridminor=False)
style.finish(fig, "AIJ UWE Case A — steady and transient OpenFOAM 12, score by score",
             handles=[style.marker(style.OPENFOAM, "RANS: realizable k-ε, log-law inlet (served)", filled=False),
                      Line2D([], [], ls="none", marker="s", markersize=6.5, color=style.OPENFOAM, label="URANS: SST k-ω, measured inlet"),
                      style.line(style.REFERENCE, "a perfect model", lw=0.8, ls="--")], ncols=3)
style.save(fig, "case-a-openfoam-rans-urans.png")
