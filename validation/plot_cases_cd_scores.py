"""Validation figure: how well each model follows the tunnel across the configurations of AIJ UWE Cases C and D.

  figures/cases-cd-scores.png
      One row per configuration (Case C: centre block x WD; Case D: WD, and the split-fibre points), one dot per
      model.  Left: the correlation coefficient C.C. with the tunnel (higher is better).  Right: the error S.E.
      (lower is better).  The scatter figures show every point of one model; this one puts every configuration
      and both models on one scale, so the weak rows read off at a glance.

C.C. is Pearson's R and S.E. the root-mean-square difference, both over the normalised pedestrian-height speed
of the configuration's points.  OpenFOAM is the scalar speed sqrt(|U|^2 + 2k)/U_H against the thermistor Vs (the
split-fibre points: |U|/U_H against the measured |U|); the ML surrogate is |U_mean|/U_H, as in its own figure.

Inputs: validation/results/case{C,D}_ml_pairs.csv and case{C,D}_openfoam12_realizableKE_pairs.csv, the snapshots
plot_ml_surrogate.py and plot_case_{c,d}_openfoam.py write.  Each ML R is asserted against the fixture's own score
in case{C,D}_ml.json, so the figure cannot drift from the tables.
"""
from __future__ import annotations

import csv
import io
import json
import os

import numpy as np
import ultraplot as uplt
from matplotlib.lines import Line2D

import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
WDS = [0.0, 22.5, 45.0]
CONFIGS = ["0D", "1D", "2D"]


def read(name):
    with io.open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ml_json(case):
    with io.open(os.path.join(RESULTS, f"case{case}_ml.json"), encoding="utf-8") as f:
        return json.load(f)


def score(obs, pred, ref_r=None):
    """(C.C., S.E.) of one configuration; `ref_r` is the fixture's R for the same points."""
    o, p = np.array(obs, float), np.array(pred, float)
    r = float(np.corrcoef(o, p)[0, 1])
    if ref_r is not None:
        assert abs(r - ref_r) < 1e-9, (r, ref_r)
    return r, float(np.sqrt(np.mean((p - o) ** 2)))


def case_c():
    """[(row label, ML score, OpenFOAM score)], centre block major, WD minor."""
    ml, of, ref = read("caseC_ml_pairs.csv"), read("caseC_openfoam12_realizableKE_pairs.csv"), ml_json("C")
    rows = []
    for cfg in CONFIGS:
        for wd in WDS:
            tag = f"WD{wd:g}_CB{cfg}"
            m = [r for r in ml if r["set"] == tag]
            o = [r for r in of if r["config"] == cfg and float(r["wind_direction_deg"]) == wd]
            assert len(m) == len(o) == 120, (tag, len(m), len(o))
            rows.append((f"{cfg} {wd:g}°",
                         score([r["observed_over_UH"] for r in m], [r["predicted_over_UH"] for r in m], ref[f"speed.thermistor.{tag}"]["R"]),
                         score([r["measured_over_UH"] for r in o], [r["scalar_over_UH"] for r in o])))
    return rows


def case_d():
    ml, of, ref = read("caseD_ml_pairs.csv"), read("caseD_openfoam12_realizableKE_pairs.csv"), ml_json("D")
    rows = []
    for wd in WDS:
        tag = f"WD{wd:g}"
        m = [r for r in ml if r["set"] == tag]
        o = [r for r in of if r["instrument"] == "thermistor" and float(r["wind_direction_deg"]) == wd]
        assert len(m) == len(o) == 66, (tag, len(m), len(o))
        rows.append((f"{wd:g}°",
                     score([r["observed_over_UH"] for r in m], [r["predicted_over_UH"] for r in m], ref[f"speed.thermistor.{tag}"]["R"]),
                     score([r["measured_over_UH"] for r in o], [r["scalar_over_UH"] for r in o])))
        if wd == 0:   # the 33 split-fibre points, a different instrument, at WD 0 only
            m = [r for r in ml if r["set"] == "WD0_splitFibre_Umag"]
            o = [r for r in of if r["instrument"] == "split_fibre"]
            assert len(m) == len(o) == 33, (len(m), len(o))
            rows.append(("0°, split fibre, 33 points",
                         score([r["observed_over_UH"] for r in m], [r["predicted_over_UH"] for r in m]),
                         score([r["measured_over_UH"] for r in o], [r["vector_over_UH"] for r in o])))
    return rows


SECTIONS = [("Case C: 3 × 3 blocks, 120 points per row", case_c()),
            ("Case D: 100 m tower among 82 low blocks, 66 thermistor points per row", case_d())]
se_max = max(s[1] for _, rows in SECTIONS for _, ml, of in rows for s in (ml, of))
cc_min = min(s[0] for _, rows in SECTIONS for _, ml, of in rows for s in (ml, of))
CC_LIM, SE_LIM = (min(0.0, np.floor(cc_min * 5) / 5), 1.0), (0.0, 0.1 * np.ceil(se_max * 11))   # a tick of headroom on each

style.apply()
fig, axs = uplt.subplots(array=[[1, 2], [3, 4]], hratios=[len(SECTIONS[0][1]) + 1, len(SECTIONS[1][1]) + 1],
                         refwidth=2.9, refaspect=1.0, sharex=False, sharey=False, wspace=1.5, hspace=5.5)
for s, (heading, rows) in enumerate(SECTIONS):
    last = s == len(SECTIONS) - 1
    y = np.arange(len(rows))
    for c, (lim, name) in enumerate([(CC_LIM, "C.C. [–]"), (SE_LIM, "S.E. [–]")]):
        ax = axs[2 * s + c]
        for i, (label, ml, of) in enumerate(rows):
            ax.scatter([of[c]], [i], s=34, color=style.OPENFOAM, edgecolor=style.SURFACE, linewidth=0.5, zorder=4)
            ax.scatter([ml[c]], [i], s=40, marker="D", color=style.ML, edgecolor=style.SURFACE, linewidth=0.5, zorder=4)
        ax.format(xlim=lim, ylim=(len(rows) - 0.5, -0.5), ygrid=False, yminorticks=[], xlabel=name,
                  yticks=y, yticklabels=[r[0] for r in rows] if c == 0 else [])
        ax.format(abc=False)
        if c == 0:
            ax.format(ltitle=heading)
style.finish(fig, "AIJ UWE Cases C and D · agreement with the wind tunnel, one row per configuration",
             collabels=["Correlation with the wind tunnel (C.C.)\nhigher is better", "Error (S.E.)\nlower is better"],
             handles=[Line2D([], [], ls="none", marker="o", markersize=6.5, markerfacecolor=style.OPENFOAM, markeredgecolor=style.SURFACE,
                             label="Eddy3D OpenFOAM 12 (realizable k-ε)"),
                      Line2D([], [], ls="none", marker="D", markersize=6.5, markerfacecolor=style.ML, markeredgecolor=style.SURFACE,
                             label="Eddy3D ML surrogate (Yel-2.0)")], ncols=1)
style.save(fig, "cases-cd-scores.png")
for s, (heading, rows) in enumerate(SECTIONS):
    for label, ml, of in rows:
        print(f"{heading[:6]} {label:28s} OpenFOAM C.C. {of[0]:+.2f} S.E. {of[1]:.3f} | ML C.C. {ml[0]:+.2f} S.E. {ml[1]:.3f}")
