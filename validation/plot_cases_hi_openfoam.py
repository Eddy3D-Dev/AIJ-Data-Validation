"""Validation figures for AIJ UWE Cases H and I (building / cube with a point source) solved with Eddy3D / OpenFOAM.

Three figures, each answering one question:

  case-h-openfoam-agreement.png,
  case-i-openfoam-agreement.png     Does the model agree with the tunnel?  Measured against modelled U, W, k and the
                      dimensionless concentration c*, one figure per case, with the 1:1 line and the factor-of-two band.
  case-i-openfoam-closures.png      Does the turbulence closure matter?  Case I under standard k-epsilon, realizable
                      k-epsilon and k-omega SST on the same mesh: U, k and c*.

Inputs, all in this repository: the cleaned measurement tables clean/cases/{H,I}/points.csv, and the per-point pairs
validation/results/case{H,I}_openfoam12_*_pairs.csv built from them and from the probes the Eddy3D fixtures
TestAijCaseHContainerE2E and TestAijCubeContainerE2E wrote (validation/results/*_probes*.csv, snapshots of the reference
probe files under C:/Eddy3DVal/aij_{H,I}_*_L3, refreshed from there when that folder exists; set EDDY3D_VAL for another
location). The scores in validation/results/case{H,I}_openfoam12_*.json are computed FROM THE PAIRS by
validation/dispersion_metrics.py, the implementation that reproduces the fixtures' own scores for Cases A and B to 1e-9; this
script recomputes them on every run and fails if the file disagrees.

Normalisation: each side by its own reference, as in Case E. Measured velocities by the tunnel's U_H (H: 3.226 m/s, the workbook's,
so the measured ratio is the workbook's own; I: 1.7 m/s), modelled ones by the U_H the solve was driven with (H: 3.23 m/s, the readme's;
I: 1.7 m/s); k by U_H^2. Concentration: the cleaned table's concentration_ratio C / c0 (H: c0 = 45.18 ppm, I: 39.22 ppm) against the
model's c* = c U_H H^2 / Q (full scale, Q = 1 kg/s, as the fixtures define it). The measured values are the cleaned tables', which
are the legacy workbooks' (the CSVs quantise H's velocities on two planes), so the scores differ from the fixtures' own, which
were computed against the CSVs, in the third digit. Case H's vertical-plane V is in the unified sign (positive toward +y).

Probe frame. The fixtures solve the case turned so that the wind blows along world +y, at 1:100 (H) and 1:60 (I):
world = scale x (-Y, X, Z) of the case frame, so U = U_y, V = -U_x, W = U_z.

Colours follow plotstyle.py: the OpenFOAM model is its engine colour (OPENFOAM); reference geometry (1:1 line,
factor-of-two band) is recessive grey.
"""
from __future__ import annotations

import csv
import io
import json
import math
import os

import numpy as np
import ultraplot as uplt

import dispersion_metrics as DM
import layout
import plotstyle as style

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RESULTS = os.path.join(HERE, "results")
SPECIES = [("sct03", "Sct 0.3"), ("sct05", "Sct 0.5"), ("sct07", "Sct 0.7")]

# (case, study folder under the validation root, closure id used in the file names, U_H of the tunnel [m/s], U_H the solve was driven with
#  [m/s], model scale, full-scale H the solve used [m], title)
RUNS = [
    ("H", "aij_H_realizableKE_L3", "realizableKE", 3.226, 3.23, 100.0, 20.0, "Case H · 1:1:2 building, floor source"),
    ("I", "aij_I_realizableKE_L3", "realizableKE", 1.7, 1.7, 60.0, 6.0, "Case I · cube, roof source"),
    ("I", "aij_I_kEpsilon_L3", "kEpsilon", 1.7, 1.7, 60.0, 6.0, "Case I · cube, standard k-ε"),
    ("I", "aij_I_kOmegaSST_L3", "kOmegaSST", 1.7, 1.7, 60.0, 6.0, "Case I · cube, k-ω SST"),
]
PAIR_FIELDS = ["instrument", "point_id", "x", "y", "z", "U_meas", "V_meas", "W_meas", "U_model", "V_model", "W_model", "k_meas", "k_model",
               "cstar_meas", "cstar_sct03", "cstar_sct05", "cstar_sct07"]


def validation_root():
    for p in (os.environ.get("EDDY3D_VAL"), r"C:/Eddy3DVal", os.path.expanduser("~/Eddy3DVal")):
        if p and os.path.isdir(os.path.join(p, "aij_H_realizableKE_L3")):
            return p
    return None


def stem(case, closure):
    return f"case{case}_openfoam12_{closure}"


def path(case, closure, what):
    return os.path.join(RESULTS, f"{stem(case, closure)}{what}")


def write_lf(dest, text):
    with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_lf(src):
    with io.open(src, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def clean_table(case):
    with io.open(os.path.join(REPO, "clean", "cases", case, "points.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(v):
    return float(v) if v not in ("", None) else math.nan


def read_probe(src, scale):
    """Rows of a fixture probe file in the CASE frame, in the file's order (which is the reference table's)."""
    out = []
    with io.open(src, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            g = lambda k: float(r[k]) if k in r and r[k] != "" else math.nan  # noqa: E731
            out.append({"X": g("y") / scale, "Y": -g("x") / scale, "Z": g("z") / scale, "U": g("U_y"), "V": -g("U_x"), "W": g("U_z"), "k": g("k"),
                        "sct03": g("c_sct03"), "sct05": g("c_sct05"), "sct07": g("c_sct07")})
    return out


def export_pairs(case, closure, uh_t, uh_m, h_full, probes):
    """Pairs of one solve: the cleaned table's measured values against the probes at the same points, normalised."""
    table = clean_table(case)
    byid = {}
    for r in table:
        byid.setdefault(int(r["point_id"]), {})[r["instrument"]] = r
    ids = sorted(byid)
    if case == "H":      # one probe per point number: RS_caseH.csv's row order
        probe_for = {i: probes["reference"][i - 1] for i in ids}
    else:                # RS-w_caseI.csv then RS-c_caseI.csv, the cleaned table's numbering 1-91 and 92-630
        wind = [i for i in ids if "ldv" in byid[i]]
        conc = [i for i in ids if "hydrocarbon_analyser" in byid[i]]
        probe_for = {**{i: probes["referenceWind"][n] for n, i in enumerate(wind)}, **{i: probes["referenceConc"][n] for n, i in enumerate(conc)}}
    fields = PAIR_FIELDS if case == "I" else [f for f in PAIR_FIELDS if f != "instrument"]
    rows = []
    for i in ids:
        d = byid[i]
        vel = d.get("split_fibre") or d.get("ldv")
        con = d.get("hydrocarbon_analyser")
        p = probe_for[i]
        x, y, z = (float((vel or con)[c]) for c in "xyz")
        assert abs(p["X"] - x) < 6e-3 and abs(p["Y"] - y) < 6e-3 and abs(p["Z"] - z) < 6e-3, (case, closure, i, (x, y, z), (p["X"], p["Y"], p["Z"]))
        r = {"instrument": (vel or con)["instrument"], "point_id": i, "x": x, "y": y, "z": z}
        for q in "UVW":
            r[f"{q}_meas"] = fnum(vel[q]) / uh_t if vel else math.nan
            r[f"{q}_model"] = p[q] / uh_m
        r["k_meas"] = fnum(vel["k"]) / uh_t ** 2 if vel else math.nan
        r["k_model"] = p["k"] / uh_m ** 2
        r["cstar_meas"] = fnum(con["concentration_ratio"]) if con else math.nan
        for sp, _ in SPECIES:
            r[f"cstar_{sp}"] = p[sp] * uh_m * h_full ** 2      # the fixtures: c* = c U_H H^2 / Q with Q = 1 kg/s, full scale
        rows.append(r)
    with io.open(path(case, closure, "_pairs.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if (isinstance(v, float) and math.isnan(v)) else repr(v) if isinstance(v, float) else v) for k, v in r.items()})
    return rows


def read_pairs(case, closure):
    return DM.read_pairs(path(case, closure, "_pairs.csv"))


def column(pairs, key):
    return np.array([p[key] for p in pairs], float)


# the fixture's regions of Case H (model frame: building x in [-0.1, 0], H = 0.2): above the roof, upstream, beside, near and far wake
H_REGIONS = {
    "aboveRoof": lambda p: p["z"] > 0.2,
    "upstream": lambda p: p["z"] <= 0.2 and p["x"] < -0.1,
    "beside": lambda p: p["z"] <= 0.2 and -0.1 <= p["x"] <= 0.0,
    "nearWake": lambda p: p["z"] <= 0.2 and 0.0 < p["x"] <= 0.2,
    "farWake": lambda p: p["z"] <= 0.2 and p["x"] > 0.2,
}


def scores_from_pairs(case, pairs):
    """Every score of a run, from its pairs. Keys follow the fixtures' results.json."""
    out = {}
    for q, key in (("U", "velocity.U"), ("V", "velocity.V"), ("W", "velocity.W")):
        out[key] = DM.velocity(column(pairs, f"{q}_meas"), column(pairs, f"{q}_model"))
    out["k"] = DM.turbulence(column(pairs, "k_meas"), column(pairs, "k_model"))
    cm = column(pairs, "cstar_meas")
    out["cstar.peakMeasured"] = float(np.nanmax(cm))
    for sp, _ in SPECIES:
        cp = column(pairs, f"cstar_{sp}")
        out[f"cstar.c_{sp}"] = DM.concentration(cm, cp)
        out[f"cstar.c_{sp}.peakAtReferencePoints"] = float(np.nanmax(cp[np.isfinite(cm)]))
    if case == "H":
        for name, inside in H_REGIONS.items():
            sel = [p for p in pairs if inside(p)]
            out[f"region.{name}.U"] = DM.velocity(column(sel, "U_meas"), column(sel, "U_model"))
            out[f"region.{name}.k"] = DM.turbulence(column(sel, "k_meas"), column(sel, "k_model"))
    return out


def write_results(case, closure, fixture, uh_t, uh_m, pairs):
    """The results snapshot: the fixture's solver-side numbers as written, every score recomputed from the pairs."""
    keep = {k: v for k, v in fixture.items() if not (isinstance(v, dict) and "Fb" in v and "R" in v)}
    keep = {k: v for k, v in keep.items() if not k.startswith(("cstar.", "approachProfile0.5HUpstream", "recirculation.measured", "roofCentre0.15H.measured", "approachProfile.measured"))}
    res = {**keep, "UhTunnel": uh_t, "UhModel": uh_m, "pairs": os.path.basename(path(case, closure, "_pairs.csv")),
           "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS_*.csv, differ in the third digit",
           **scores_from_pairs(case, pairs)}
    write_lf(path(case, closure, ".json"), json.dumps(res, indent=1, ensure_ascii=False, allow_nan=False) + "\n")


def snapshot(root):
    """Refresh every snapshot from the Eddy3D solves: probe files, pairs, results."""
    os.makedirs(RESULTS, exist_ok=True)
    for case, study, closure, uh_t, uh_m, scale, h_full, _ in RUNS:
        src = os.path.join(root, study)
        probes = {}
        names = ["reference"] if case == "H" else ["referenceWind", "referenceConc"]
        for n in names:
            text = read_lf(os.path.join(src, f"{n}.probe.csv"))
            tag = "" if case == "H" else ("_wind" if n == "referenceWind" else "_conc")
            write_lf(path(case, closure, f"_probes{tag}.csv"), text)
            probes[n] = read_probe(os.path.join(src, f"{n}.probe.csv"), scale)
        pairs = export_pairs(case, closure, uh_t, uh_m, h_full, probes)
        with io.open(os.path.join(src, "results.json"), encoding="utf-8-sig") as f:
            fixture = json.load(f)
        write_results(case, closure, fixture, uh_t, uh_m, DM.read_pairs(path(case, closure, "_pairs.csv")))
        print(f"snapshot {stem(case, closure)}: {len(pairs)} pairs")


def raw_table(name):
    """A benchmark CSV as published: headers bare, -999.9 = NaN."""
    with io.open(os.path.join(REPO, "raw", "cases", name), encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        head = [h.split("(")[0].split("[")[0].strip() for h in next(rd)]
        rows = [r for r in rd if any(c.strip() for c in r)]
    return {h: np.array([math.nan if abs(float(r[i]) + 999.9) < 1e-6 else float(r[i]) for r in rows]) for i, h in enumerate(head)}


def fixture_control(root):
    """The metrics implementation against the fixtures' OWN scores: the raw CSVs scored the way the fixtures score them, with the
    probes of the same solves, must give results.json to 1e-9. (The cleaned tables differ from the CSVs, so the scores of the pairs
    differ in the third digit; this is what proves the metrics are the fixtures'.)"""
    for case, study, closure, uh_t, uh_m, scale, h_full, _ in RUNS:
        with io.open(os.path.join(root, study, "results.json"), encoding="utf-8-sig") as f:
            fx = json.load(f)
        h_model = h_full / scale
        if case == "H":
            rs = raw_table("case-h/RS_caseH.csv")
            pr = read_probe(os.path.join(root, study, "reference.probe.csv"), scale)
            uh = 3.23
            tf = 5.83e-6
            wind = (rs["U"], rs["W"], rs["k"], rs["x"], rs["z"], pr, rs["<c>"], pr)
            sets = {"wind": (rs["U"], rs["W"], rs["k"], pr), "conc": (rs["<c>"], pr)}
            region = {"x": rs["x"], "z": rs["z"]}
        else:
            rw, rc = raw_table("case-i/RS-w_caseI.csv"), raw_table("case-i/RS-c_caseI.csv")
            pw = read_probe(os.path.join(root, study, "referenceWind.probe.csv"), scale)
            pc = read_probe(os.path.join(root, study, "referenceConc.probe.csv"), scale)
            uh, tf = 1.7, 400e-6 / 60 * 0.1
            sets = {"wind": (rw["U"], rw["W"], rw["k"], pw), "conc": (rc["C"], pc)}
        u, w_, k, pw_ = sets["wind"]
        col = lambda pr, key: np.array([r[key] for r in pr])  # noqa: E731
        got = {"velocity.U": DM.velocity(u / uh, col(pw_, "U") / uh), "velocity.W": DM.velocity(w_ / uh, col(pw_, "W") / uh),
               "k": DM.turbulence(k / uh ** 2, col(pw_, "k") / uh ** 2)}
        ppm, pcn = sets["conc"]
        cs = ppm * 1e-6 * uh * h_model ** 2 / tf
        for sp, _ in SPECIES:
            got[f"cstar.c_{sp}"] = DM.concentration(cs, col(pcn, sp) * uh * h_full ** 2)
        if case == "H":
            for name, inside in H_REGIONS.items():
                sel = np.array([inside({"x": a, "z": b}) for a, b in zip(rs["x"], rs["z"])])
                got[f"region.{name}.U"] = DM.velocity((u / uh)[sel], (col(pw_, "U") / uh)[sel])
                got[f"region.{name}.k"] = DM.turbulence((k / uh ** 2)[sel], (col(pw_, "k") / uh ** 2)[sel])
        for key, mine in got.items():
            assert DM.same(mine, fx[key], fixture=True), (stem(case, closure), key, {m: (mine[m], fx[key][m]) for m in mine if not DM.same({m: mine[m]}, {m: fx[key][m]})})
        print(f"fixture control {stem(case, closure)}: {len(got)} scores reproduced from the raw CSVs and the fixture's probes")


def parity(root):
    """The recomputed headline scores next to the fixtures' own (a diagnostic: the measured side moved from the CSVs to the workbooks)."""
    for case, study, closure, *_ in RUNS:
        with io.open(os.path.join(root, study, "results.json"), encoding="utf-8-sig") as f:
            fx = json.load(f)
        with io.open(path(case, closure, ".json"), encoding="utf-8") as f:
            mine = json.load(f)
        for key in ("velocity.U", "velocity.W", "k", "cstar.c_sct05"):
            a, b = fx[key], mine[key]
            print(f"{stem(case, closure)} {key}: R {a['R']:+.4f} -> {b['R']:+.4f}  FAC2 {a['Fac2']:.4f} -> {b['Fac2']:.4f}  FB {a['Fb']:+.4f} -> {'n/a' if b['Fb'] is None else format(b['Fb'], '+.4f')}  n {a['Count']} -> {b['Count']}")


def check_results_match_pairs():
    """The committed scores are what the committed pairs give: fail otherwise."""
    for case, _, closure, *_ in RUNS:
        with io.open(path(case, closure, ".json"), encoding="utf-8") as f:
            res = json.load(f)
        for key, want in scores_from_pairs(case, read_pairs(case, closure)).items():
            got = res[key]
            if isinstance(want, dict):
                assert DM.same(got, want), (stem(case, closure), key, got, want)
            else:
                assert abs(got - want) <= 1e-9 * max(1.0, abs(want)), (stem(case, closure), key, got, want)


root = validation_root()
if root:
    fixture_control(root)
    snapshot(root)
    parity(root)
check_results_match_pairs()

# ----------------------------------------------------------------------------- figure 1
style.apply()


def panel(ax, o, p, colours, log=False, xlab=None, ylab=None):
    """Measured o against modelled p with the 1:1 line (and the factor-of-two band where the values do not change sign); returns how many are drawn.
    `colours`: one colour per pair, the group of the tunnel's line or plane the point was measured on (layout.py)."""
    ok = np.isfinite(o) & np.isfinite(p)
    o, p, colours = o[ok], p[ok], colours[ok]
    if log:                                   # a log axis shows the positive pairs only; the statistics use all of them
        keep = (o > 0) & (p > 0)
        o, p, colours = o[keep], p[keep], colours[keep]
        hi = 10 ** math.ceil(math.log10(max(o.max(), p.max())))
        lo = max(10 ** math.floor(math.log10(min(o.min(), p.min()))), hi * 1e-5)     # five decades at most; pairs below are not drawn
        shown = (o >= lo) & (p >= lo)
        o, p, colours = o[shown], p[shown], colours[shown]
        ax.format(xscale="log", yscale="log")
    else:
        lo, hi = float(min(o.min(), p.min())), float(max(o.max(), p.max()))
        pad = 0.08 * (hi - lo) if hi > lo else 0.1
        lo, hi = lo - pad, hi + pad
    style.one_to_one(ax, lo, hi, factor_two=bool(log or (o > 0).all()))
    ax.scatter(o, p, s=9 if len(o) > 300 else 14, color=list(colours), edgecolor=style.SURFACE, linewidth=0.25, alpha=0.9, zorder=3)
    ax.format(xlim=(lo, hi), ylim=(lo, hi), xlabel=xlab, ylabel=ylab)
    return len(o)


def stats_text(m, n_shown=None, extra=""):
    fb = "n/a" if m["Fb"] is None else f"{m['Fb']:+.2f}"      # undefined when the signed means differ in sign (dispersion_metrics.py)
    t = f"R {m['R']:+.2f}\nFAC2 {m['Fac2']:.2f}\nFB {fb}\nn {m['Count']}"
    if n_shown is not None and n_shown != m["Count"]:
        t += f" ({n_shown} shown)"
    return t + extra


def res(case, closure):
    with io.open(path(case, closure, ".json"), encoding="utf-8") as f:
        return json.load(f)


QUANTITIES = [("U", "U_meas", "U_model", "velocity.U", "U/U$_H$"), ("W", "W_meas", "W_model", "velocity.W", "W/U$_H$"),
              ("k", "k_meas", "k_model", "k", "k/U$_H^2$"), ("c", "cstar_meas", "cstar_sct05", "cstar.c_sct05", "c* = C/c$_0$ (Sct 0.5)")]
# One figure per case, so each case's Validation page shows its own points only.
for case, _, closure, *_rest in (RUNS[0], RUNS[1]):
    title = _rest[-1]
    pairs, rs = read_pairs(case, closure), res(case, closure)
    colours = np.array(layout.grouped_colours(case, pairs), dtype=object)      # the line or plane of the tunnel each point was measured on
    fig, axs = uplt.subplots(nrows=1, ncols=4, refwidth=2.0, refaspect=1, share=False, wspace=4.2)
    for col, (tag, mk, pk, key, label) in enumerate(QUANTITIES):
        ax = axs[col]
        shown = panel(ax, column(pairs, mk), column(pairs, pk), colours, log=(tag == "c"), xlab="Tunnel [–]", ylab="Eddy3D [–]" if col == 0 else None)
        extra = ""
        if tag == "c":
            extra = "\nFAC2 Sct 0.3 / 0.7: " + " / ".join(f"{rs[f'cstar.c_{sp}']['Fac2']:.2f}" for sp in ("sct03", "sct07"))
        style.stats(ax, stats_text(rs[key], shown if tag == "c" else None, extra), loc=(0.40, 0.36) if tag == "c" else (0.05, 0.80), halo="auto")
    style.finish(fig, f"AIJ UWE {title} — Eddy3D (OpenFOAM 12, realizable k-ε) vs wind tunnel",
                 handles=[*layout.legend_handles(case), style.line(style.REFERENCE, "1:1", lw=1.0),
                          style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")],
                 ncols=3, toplabels=[q[4] for q in QUANTITIES])
    style.save(fig, f"case-{case.lower()}-openfoam-agreement.png")

# ----------------------------------------------------------------------------- figure 2
QI = [("U", "U_meas", "U_model", "velocity.U", "U/U$_H$"), ("k", "k_meas", "k_model", "k", "k/U$_H^2$"),
      ("c", "cstar_meas", "cstar_sct05", "cstar.c_sct05", "c* = C/c$_0$ (Sct 0.5)")]
fig2, axs2 = uplt.subplots(nrows=3, ncols=3, refwidth=2.0, refaspect=1, share=False, wspace=4.2, hspace=2.6)
closures = [RUNS[2], RUNS[1], RUNS[3]]
for row, (case, _, closure, *_rest) in enumerate(closures):
    pairs, rs = read_pairs(case, closure), res(case, closure)
    colours = np.array(layout.grouped_colours(case, pairs), dtype=object)
    for col, (tag, mk, pk, key, label) in enumerate(QI):
        ax = axs2[row, col]
        shown = panel(ax, column(pairs, mk), column(pairs, pk), colours, log=(tag == "c"), xlab="Tunnel [–]" if row == 2 else None, ylab="Eddy3D [–]" if col == 0 else None)
        style.stats(ax, stats_text(rs[key], shown if tag == "c" else None), loc=(0.40, 0.36) if tag == "c" else (0.05, 0.80), halo="auto")
style.finish(fig2, "AIJ UWE Case I — three turbulence closures on one mesh (OpenFOAM 12) vs wind tunnel",
             handles=[*layout.legend_handles("I"), style.line(style.REFERENCE, "1:1", lw=1.0), style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")],
             ncols=3, toplabels=[q[4] for q in QI], leftlabels=["standard k-ε", "realizable k-ε", "k-ω SST"])
style.save(fig2, "case-i-openfoam-closures.png")
