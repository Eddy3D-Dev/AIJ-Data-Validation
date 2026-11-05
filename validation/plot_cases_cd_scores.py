"""Validation figure: how well each model follows the tunnel across the configurations of AIJ UWE Cases C and D.

  figures/cases-cd-scores.png
      One row per configuration (Case C: centre block x WD; Case D: WD, and the split-fibre points), one dot per
      model.  Left: the correlation coefficient C.C. with the tunnel (higher is better).  Right: the error S.E.
      (lower is better).  The grey box behind a row is the range of the CFD codes the AIJ working group ran on the
      same configuration (AIJ 2016, BOOK_C and BOOK_D below).  The scatter figures show every point of one model;
      this one puts every configuration, both models and the AIJ codes on one scale.

C.C. is Pearson's R and S.E. the root-mean-square difference about the 1:1 line, over the normalised pedestrian-height
speed of the configuration's points.  The AIJ book never defines S.E.; RMS difference is the reading that reproduces
its numbers (our OpenFOAM |U| in Case C: 0.23-0.33 against the book's 0.20-0.35; a regression standard error gives
0.12-0.19) and that moves with bias the way the book's does (Fig. 3-1-9: 0.24 -> 0.14 once the 2k term is added).

What is compared with what, row by row, so a dot and a box are the same quantity:
  Case C   speeds over the approach speed at the measuring height z = 0.02 m (the book's "inflow velocity at the same
           height"; clean/cases/C/approach_flow.csv), not over U_H.  The book's Table 3-1-3 is the mean |U| speed
           with no 2k term, so the box is drawn against OpenFOAM |U| (hollow) and the ML surrogate (|U_mean|); the
           filled OpenFOAM dot is the scalar speed sqrt(|U|^2 + 2k) that a thermistor reads, which the book shows to
           score better (Fig. 3-1-9) and does not tabulate.
  Case D   speeds over U_H.  The book's thermistor rows (Figs. 3-2-14 to 3-2-16) carry the 2k correction, so the filled
           OpenFOAM dot is the scalar speed; its split-fibre row (Figs. 3-2-10 to 3-2-12) is |U| against the measured |U|.

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
from matplotlib.patches import Patch

import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
CLEAN = os.path.join(os.path.dirname(HERE), "clean", "cases")
WDS = [0.0, 22.5, 45.0]
CONFIGS = ["0D", "1D", "2D"]

# Architectural Institute of Japan (2016), "AIJ Benchmarks for Validation of CFD Simulations Applied to Pedestrian Wind
# Environment around Buildings", ISBN 978-4-8189-5001-6 (c) AIJ, a paid download that is not stored here.  Only the
# range per row is kept: ((C.C. min, max), (S.E. min, max)) over the codes the AIJ working group ran, steady RANS all.
# Case C, Table 3-1-3, per wind direction the centre block 0D, 1D, 2D: organisations A (own code), B (STAR-CD, standard
# and modified k-eps, 0 deg only), C (STREAM), D (FLUENT), so five runs at 0 deg and three at 22.5 and 45 deg.
BOOK_C = {
    0.0: [((0.83, 0.90), (0.20, 0.27)), ((0.85, 0.90), (0.22, 0.27)), ((0.76, 0.93), (0.23, 0.30))],
    22.5: [((0.89, 0.90), (0.22, 0.25)), ((0.89, 0.91), (0.24, 0.27)), ((0.77, 0.86), (0.27, 0.32))],
    45.0: [((0.91, 0.94), (0.22, 0.25)), ((0.87, 0.90), (0.29, 0.35)), ((0.91, 0.93), (0.24, 0.33))],
}
# Case D, the basic run of codes M, T and O: Figs. 3-2-10 to 3-2-12 (split fibre, 0 deg) and 3-2-14 to 3-2-16 (thermistor,
# corrected with the calculated k).  The book's further runs of each code vary one setting (domain, ground law, model).
BOOK_D = {
    ("thermistor", 0.0): ((0.689, 0.799), (0.205, 0.217)),
    ("thermistor", 22.5): ((0.813, 0.862), (0.219, 0.239)),
    ("thermistor", 45.0): ((0.833, 0.869), (0.227, 0.230)),
    ("split_fibre", 0.0): ((0.847, 0.905), (0.062, 0.105)),
}


def read(name):
    with io.open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ml_json(case):
    with io.open(os.path.join(RESULTS, f"case{case}_ml.json"), encoding="utf-8") as f:
        return json.load(f)


def approach_U(z):
    with io.open(os.path.join(CLEAN, "C", "approach_flow.csv"), encoding="utf-8") as f:
        return {float(r["z"]): float(r["U"]) for r in csv.DictReader(f)}[z]


# the pairs hold speed/U_H with U_H = U(0.2 m); the book's Case C ratio is over U(0.02 m), the height of every point
C_RESCALE = approach_U(0.2) / approach_U(0.02)


def score(obs, pred, ref_r=None, scale=1.0):
    """(C.C., S.E.) of one configuration; `ref_r` is the fixture's R for the same points."""
    o, p = np.array(obs, float) * scale, np.array(pred, float) * scale
    r = float(np.corrcoef(o, p)[0, 1])
    if ref_r is not None:
        assert abs(r - ref_r) < 1e-9, (r, ref_r)
    return r, float(np.sqrt(np.mean((p - o) ** 2)))


def case_c():
    """[(row label, ML score, OpenFOAM scalar score, AIJ box, OpenFOAM |U| score)], centre block major, WD minor."""
    ml, of, ref = read("caseC_ml_pairs.csv"), read("caseC_openfoam12_realizableKE_pairs.csv"), ml_json("C")
    rows = []
    for i, cfg in enumerate(CONFIGS):
        for wd in WDS:
            tag = f"WD{wd:g}_CB{cfg}"
            m = [r for r in ml if r["set"] == tag]
            o = [r for r in of if r["config"] == cfg and float(r["wind_direction_deg"]) == wd]
            assert len(m) == len(o) == 120, (tag, len(m), len(o))
            meas = [r["measured_over_UH"] for r in o]
            rows.append((f"{cfg} {wd:g}°",
                         score([r["observed_over_UH"] for r in m], [r["predicted_over_UH"] for r in m],
                               ref[f"speed.thermistor.{tag}"]["R"], C_RESCALE),
                         score(meas, [r["scalar_over_UH"] for r in o], scale=C_RESCALE),
                         BOOK_C[wd][i],
                         score(meas, [r["vector_over_UH"] for r in o], scale=C_RESCALE)))
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
                     score([r["measured_over_UH"] for r in o], [r["scalar_over_UH"] for r in o]),
                     BOOK_D[("thermistor", wd)], None))
        if wd == 0:   # the 33 split-fibre points, a different instrument, at WD 0 only
            m = [r for r in ml if r["set"] == "WD0_splitFibre_Umag"]
            o = [r for r in of if r["instrument"] == "split_fibre"]
            assert len(m) == len(o) == 33, (len(m), len(o))
            rows.append(("0°, split fibre, 33 points",
                         score([r["observed_over_UH"] for r in m], [r["predicted_over_UH"] for r in m]),
                         score([r["measured_over_UH"] for r in o], [r["vector_over_UH"] for r in o]),
                         BOOK_D[("split_fibre", 0.0)], None))
    return rows


SECTIONS = [("Case C: 3 × 3 blocks, 120 points per row", case_c()),
            ("Case D: 100 m tower among 82 low blocks, 66 thermistor points per row", case_d())]
cc_all = [s[0] for _, rows in SECTIONS for _, ml, of, box, alt in rows for s in (ml, of, alt) if s]
se_all = [s[1] for _, rows in SECTIONS for _, ml, of, box, alt in rows for s in (ml, of, alt) if s]
CC_LIM, SE_LIM = (min(0.0, np.floor(min(cc_all) * 5) / 5), 1.0), (0.0, 0.1 * np.ceil(max(se_all) * 11))   # a tick of headroom on each

style.apply()
fig, axs = uplt.subplots(array=[[1, 2], [3, 4]], hratios=[len(SECTIONS[0][1]) + 1, len(SECTIONS[1][1]) + 1],
                         refwidth=2.9, refaspect=1.0, sharex=False, sharey=False, wspace=1.5, hspace=5.5)
for s, (heading, rows) in enumerate(SECTIONS):
    y = np.arange(len(rows))
    for c, (lim, name) in enumerate([(CC_LIM, "C.C. [–]"), (SE_LIM, "S.E. [–]")]):
        ax = axs[2 * s + c]
        for i, (label, ml, of, box, alt) in enumerate(rows):
            ax.fill_betweenx([i - 0.34, i + 0.34], *box[c], color=style.FOOTPRINT, linewidth=0, zorder=1)
            if alt:
                ax.scatter([alt[c]], [i], s=34, facecolor="none", edgecolor=style.OPENFOAM, linewidth=1.1, zorder=4)
            ax.scatter([of[c]], [i], s=34, color=style.OPENFOAM, edgecolor=style.SURFACE, linewidth=0.5, zorder=5)
            ax.scatter([ml[c]], [i], s=40, marker="D", color=style.ML, edgecolor=style.SURFACE, linewidth=0.5, zorder=5)
        ax.format(xlim=lim, ylim=(len(rows) - 0.5, -0.5), ygrid=False, yminorticks=[], xlabel=name,
                  yticks=y, yticklabels=[r[0] for r in rows] if c == 0 else [])
        ax.format(abc=False)
        if c == 0:
            ax.format(ltitle=heading)
style.finish(fig, "AIJ UWE Cases C and D · agreement with the wind tunnel, one row per configuration",
             collabels=["Correlation with the wind tunnel (C.C.)\nhigher is better", "Error (S.E.)\nlower is better"],
             handles=[Line2D([], [], ls="none", marker="o", markersize=6.5, markerfacecolor=style.OPENFOAM, markeredgecolor=style.SURFACE,
                             label="Eddy3D OpenFOAM 12 (realizable k-ε)"),
                      Line2D([], [], ls="none", marker="o", markersize=6.5, markerfacecolor="none", markeredgecolor=style.OPENFOAM,
                             label="OpenFOAM 12, mean |U| only (Case C)"),
                      Line2D([], [], ls="none", marker="D", markersize=6.5, markerfacecolor=style.ML, markeredgecolor=style.SURFACE,
                             label="Eddy3D ML surrogate (Yel-2.0)"),
                      Patch(facecolor=style.FOOTPRINT, label="AIJ benchmark CFD codes, range (AIJ 2016)")], ncols=1)
style.save(fig, "cases-cd-scores.png")
for s, (heading, rows) in enumerate(SECTIONS):
    for label, ml, of, box, alt in rows:
        a = f" | |U| C.C. {alt[0]:+.2f} S.E. {alt[1]:.3f}" if alt else ""
        print(f"{heading[:6]} {label:28s} OpenFOAM C.C. {of[0]:+.2f} S.E. {of[1]:.3f}{a} | ML C.C. {ml[0]:+.2f} S.E. {ml[1]:.3f}"
              f" | AIJ C.C. {box[0][0]:.2f}-{box[0][1]:.2f} S.E. {box[1][0]:.2f}-{box[1][1]:.2f}")
