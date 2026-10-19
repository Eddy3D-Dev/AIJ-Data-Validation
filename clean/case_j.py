"""Case J (112CT) — 1:1:2 building, floor tracer source, unstable non-isothermal boundary layer.

Zenodo 10.5281/zenodo.15447887 (Yoshie, Tanaka, Kobayashi). build(B, prov) is called by clean/build.py with the
build module as B; it returns what build_A .. build_E return: (points, approach flow, geometry, inflow, frame,
transform, extra).

Where the numbers come from: RS_caseJ.csv is the legacy workbook's non-dimensional values rounded to 3-4 decimals and
multiplied back by the workbook's reference scales (checked cell for cell below), so the point table is rebuilt from
LF_caseJ.xlsx at full precision and the CSV is the cross-check, as Case E does.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

import jkl_common as X

check = X.check

META = {
    "id": "J", "title": "Case J — 1:1:2 building, floor source, non-isothermal",
    "folder": "raw/cases/case-j", "zenodo_concept": "10.5281/zenodo.15447887", "zenodo_version": None,
    "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    "collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Hideyuki Tanaka (Takenaka Corporation)", "Tsuyoshi Kobayashi (Tokyo Polytechnic University)"],
    "citation": "Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. https://doi.org/10.1007/978-4-431-55912-2_9",
}

# stated by the readme / data paper section 3.10 (each is verified or contradicted in the checks)
B_WIDTH, HEIGHT = 0.08, 0.16
U_H_STATED, Q_GAS, GAS_FRACTION, RE_PAPER, RE_README = 1.46, 9.17e-6, 0.05, 1.6e4, 43000
SOURCE_X = 0.25 * HEIGHT            # 0.25 H from the leeward wall (x = 0)
KELVIN = 273.15

# workbook column of each published quantity (measurement sheets: the value; the cell to its right is Ue)
WB_COL = {"U": 4, "V": 6, "W": 8, "su": 10, "sv": 12, "sw": 14, "uu": 16, "vv": 18, "ww": 20, "k": 22,
          "T": 24, "T_rms": 26, "uT": 28, "vT": 30, "wT": 32, "C": 34, "c_rms": 36}
# the CSV is round(round(workbook ratio, P) * scale, d): P = 3 for the mean velocity, 4 for everything else
CSV_ROUNDING = {"U": 3, "V": 3, "W": 3, "u_rms": 4, "v_rms": 4, "w_rms": 4, "k": 4, "T": 4, "t_rms": 4, "ut": 4, "vt": 4, "wt": 4, "C": 4, "c_rms": 4}
CSV_DECIMALS = {"U": 2, "V": 2, "W": 2, "u_rms": 3, "v_rms": 3, "w_rms": 3, "k": 4, "T": 2, "t_rms": 3, "ut": 4, "vt": 4, "wt": 4, "C": 3, "c_rms": 3}
AF_COL = {"U": 4, "V": 6, "W": 8, "su": 10, "sv": 12, "sw": 14, "uu": 16, "vv": 18, "ww": 20, "uv": 22, "uw": 24, "k": 26, "T": 28, "T_rms": 30, "uT": 32, "vT": 34, "wT": 36}


def _letter(j: int) -> str:
    return chr(65 + j) if j < 26 else "A" + chr(65 + j - 26)


def _key(x, y, z):
    return (round(x, 5), round(y, 5), round(z, 5))


def build(B, prov):
    c = "J"
    folder = os.path.join(B.REPO, META["folder"])
    f = {n: os.path.join(folder, n) for n in ("RS_caseJ.csv", "AF_caseJ.csv", "BD-ST_caseJ.csv", "LF_caseJ.xlsx", "readme_caseJ.md", "MP-y_caseJ.png", "MP-z_caseJ.png")}
    prov[c] = list(f.values())
    B.DIRECTION_BASIS[c] = ("definition: +x streamwise (MP drawings: building x in [-0.08, 0], source at x = +0.04); checks WD0_flow_is_along_x, concentration_peaks_at_the_source, lateral_sign_*", "settled")
    wb = X.read_xlsx(f["LF_caseJ.xlsx"])

    # ---------------------------------------------------------------- the workbook's reference scales
    K = X.labelled_constants(wb["Experimental Condition"], 1, 4)
    uH, thf, dth, c0, H = K["<uH> (m/s)"], K["<θf > (oC)"], K["<Δθ> (oC)"], K["(Co)"], K["H (m)"]
    B.log(f"[J] LF_caseJ.xlsx 'Experimental Condition': H = {H} m, <uH> = {uH} m/s, <θf> = {thf} degC, <θH> = {K['<θH> (oC)']:.6f} degC, <Δθ> = {dth} degC, "
          f"<θ0> = {K['<θ0> (oC)']} degC, <θbuild> = {K['<θbuild> (oC)']:.6f} degC, <θgas> = {K['<θgas> (oC)']} degC, Rb = {K['Rb']:.6f}, c0 = {c0:.6f} ppm")
    assert abs(H - HEIGHT) < 1e-12

    hdr = wb["xz-plane(Unstable state)"][27]
    if not (str(hdr[WB_COL["U"]]).startswith("<u>") and "k'" in str(hdr[WB_COL["k"]]) and str(hdr[WB_COL["C"]]).startswith("<c>") and "θ" in str(hdr[WB_COL["T"]])):
        raise SystemExit("Case J: the workbook's measurement sheets no longer have the layout the builder reads")
    sheets = ["xz-plane(Unstable state)", "xy-plane(Unstable state)", "xy-plane2(Unstable state)"]
    wrows = []                                    # (sheet, 1-based row, cells)
    for s in sheets:
        for i, r in enumerate(wb[s]):
            if i >= 29 and isinstance(r[1], float):
                wrows.append((s, i + 1, r))
    wbd, shared, shared_maxdiff = {}, 0, 0.0
    for s, i, r in wrows:
        k = _key(r[1] * H, r[2] * H, r[3] * H)
        if k in wbd:
            shared += 1
            shared_maxdiff = max(shared_maxdiff, max(abs(wbd[k][1][j] - r[j]) for j in range(4, 38)))
        else:
            wbd[k] = (s, r)

    # ---------------------------------------------------------------- the published CSV
    header, rows = B.read_csv_rows(f["RS_caseJ.csv"])
    idx = {h: i for i, h in enumerate(header)}
    B.log(f"[J] RS_caseJ.csv header (bare): {header}; published units: x, y, z m; U, V, W, rms m/s; k m2/s2; T KELVIN; t_rms K; ut, vt, wt m/s K; C, c_rms ppm")
    csv = pd.DataFrame([{n: B.num(r[idx[n]]) for n in header} for r in rows])
    miss = [k for k in zip(csv.x.round(5), csv.y.round(5), csv.z.round(5)) if k not in wbd]
    if miss:
        raise SystemExit(f"Case J: {len(miss)} locations of RS_caseJ.csv are not in the workbook, first {miss[0]}")
    recs = [wbd[k][1] for k in zip(csv.x.round(5), csv.y.round(5), csv.z.round(5))]
    W = lambda name: np.array([r[WB_COL[name]] for r in recs], float)          # noqa: E731  workbook ratio per CSV row
    Ue = lambda name: np.array([r[WB_COL[name] + 1] for r in recs], float)     # noqa: E731
    out = []
    for n, r in enumerate(recs):
        out.append(B.row(case_id=c, instrument="split_fibre", point_id=int(csv["No."].iloc[n]), x=csv.x.iloc[n], y=csv.y.iloc[n], z=csv.z.iloc[n],
                         U=r[4] * uH, V=r[6] * uH, W=r[8] * uH, uu=r[16] * uH ** 2, vv=r[18] * uH ** 2, ww=r[20] * uH ** 2, k=r[22] * uH ** 2,
                         C=r[34] * c0, c_rms=r[36] * c0, concentration_ratio=r[34],
                         T=thf + r[24] * dth, T_rms=r[26] * dth, uT=r[28] * uH * dth, vT=r[30] * uH * dth, wT=r[32] * uH * dth))
    B.log("[J] transform: every value is the workbook's non-dimensional value x its reference scale (U, V, W, sigma x <uH>; variances, k x <uH>^2; "
          "T = <θf> + ratio x <Δθ> in degC, so the CSV's Kelvin is converted; heat fluxes x <uH><Δθ>; C, c_rms x c0), i.e. the CSV before its rounding")
    B.log("[J] u, v, w variances are the workbook's <u'2> columns (the quantity k is built from), not sigma^2: the two columns disagree in some rows (check published_variance_vs_published_sigma_squared)")
    B.log("[J] uv, uw, vw: not published for the 444 points (only the approach flow has uv, uw) -> NaN; uc, vc, wc: not measured -> NaN")
    pts = X.tidy(pd.DataFrame(out, columns=B.POINT_COLUMNS))

    # ---------------------------------------------------------------- approach flow (published CSV = station x = -0.4 m)
    h2, ar = B.read_csv_rows(f["AF_caseJ.csv"])
    a2 = {n: i for i, n in enumerate(h2)}
    afc = pd.DataFrame([{n: B.num(r[a2[n]]) for n in h2} for r in ar])
    afl = pd.DataFrame({"case_id": c, "z": afc.z, "U": afc.U, "uu": afc.u_rms ** 2, "vv": afc.v_rms ** 2, "ww": afc.w_rms ** 2, "k": afc.k})
    B.log("[J] approach flow: AF_caseJ.csv, 20 heights at x = -0.4 m (x/H = -2.5), rms squared; V, W, uv, uw, T and the heat fluxes go to cases/J/approach_flow_full.csv")
    inf = wb["Unstable Inflow"]
    stations = {}
    for i, r in enumerate(inf):
        if i >= 5 and isinstance(r[1], float):
            stations.setdefault(round(r[1], 6), []).append(r)
    full = []
    for xs, rr in sorted(stations.items()):
        for r in rr:
            full.append({"x": round(xs * H, 9), "z": round(r[3] * H, 9), "U": r[4] * uH, "V": r[6] * uH, "W": r[8] * uH,
                         "uu": r[16] * uH ** 2, "vv": r[18] * uH ** 2, "ww": r[20] * uH ** 2, "uv": r[22] * uH ** 2, "uw": r[24] * uH ** 2, "k": r[26] * uH ** 2,
                         "T": thf + r[28] * dth, "T_rms": r[30] * dth, "uT": r[32] * uH * dth, "vT": r[34] * uH * dth, "wT": r[36] * uH * dth})
    full = pd.DataFrame(full)
    full_path = os.path.join(B.HERE, "cases", c, "approach_flow_full.csv")
    B.write_csv(full_path, full)

    # ---------------------------------------------------------------- building surface temperature
    hb, br = B.read_csv_rows(f["BD-ST_caseJ.csv"])
    bd = pd.DataFrame([{"x": B.num(r[0]), "y": B.num(r[1]), "z": B.num(r[2]), "T": B.num(r[3]) - KELVIN} for r in br])
    wbs = {_key(r[1] * H, r[2] * H, r[3] * H): r[4] for r in wb["Experimental Condition"][20:] if isinstance(r[1], float)}
    keys = [_key(x, y, z) for x, y, z in bd[["x", "y", "z"]].itertuples(index=False)]
    bd_diff = max(abs(t - wbs[k]) for k, t in zip(keys, bd["T"])) if all(k in wbs for k in keys) else math.inf
    bd_path = os.path.join(B.HERE, "cases", c, "surface_temperature.csv")
    B.write_csv(bd_path, bd)
    B.log(f"[J] BD-ST_caseJ.csv: {len(bd)} points on the building surface, Kelvin -> degC; written to cases/J/surface_temperature.csv (boundary data for a CFD model, not a table row)")

    # ---------------------------------------------------------------- geometry and source
    boxes = [{"min": [-B_WIDTH, -B_WIDTH / 2, 0.0], "max": [0.0, B_WIDTH / 2, HEIGHT]}]
    geo = [("default", boxes, "generated from the readme's stated dimensions b = 0.08 m, H = 2b = 0.16 m; the building spans x in [-0.08, 0] (leeward wall at the origin), y in [-0.04, 0.04] (MP-y_caseJ.png, MP-z_caseJ.png)")]

    # ---------------------------------------------------------------- checks
    n = len(pts)
    check(B, c, "row_count_matches_source", n == 444 and len(wbd) == 443, rows=n, workbook_rows=len(wrows), distinct_locations=len(wbd),
          note="the workbook's three sheets list 465 rows; 22 locations lie in two sheets (z/H = 0.025 and 0.25 on y = 0), leaving 443 distinct locations")
    check(B, c, "point_ids_unique_and_contiguous", sorted(pts.point_id) == list(range(1, 445)))
    check(B, c, "workbook_sheets_agree_where_they_share_a_location", shared == 22 and shared_maxdiff == 0.0, locations_in_two_sheets=shared, max_abs_diff_normalised=shared_maxdiff)
    dups = csv[csv.duplicated(["x", "y", "z"], keep=False)]
    same = bool(len(dups) == 2 and (dups.drop(columns="No.").nunique() == 1).all())
    check(B, c, "one_location_is_published_twice_with_identical_values", same, point_ids=[int(v) for v in dups["No."]], xyz=dups[["x", "y", "z"]].iloc[0].tolist() if len(dups) else None,
          note="No. 1 and No. 153 are the same row: the CSV merges the 22 shared locations but keeps this one twice. Both are kept here under their own numbers; a score over the table counts that point twice")
    check(B, c, "no_sentinels_or_nan_in_measured_columns", not pts[["x", "y", "z", "U", "V", "W", "uu", "vv", "ww", "k", "T", "T_rms", "uT", "vT", "wT", "C", "c_rms"]].isna().any().any())
    # the CSV is the workbook, rounded: exact reproduction, with the rounding that was applied
    scale = {"U": uH, "V": uH, "W": uH, "u_rms": uH, "v_rms": uH, "w_rms": uH, "k": uH ** 2, "T": dth, "t_rms": dth, "ut": uH * dth, "vt": uH * dth, "wt": uH * dth, "C": c0, "c_rms": c0}
    wcol = {"U": "U", "V": "V", "W": "W", "u_rms": "su", "v_rms": "sv", "w_rms": "sw", "k": "k", "T": "T", "t_rms": "T_rms", "ut": "uT", "vt": "vT", "wt": "wT", "C": "C", "c_rms": "c_rms"}
    res, bad_cols, resolution = {}, [], {}
    for col, p in CSV_ROUNDING.items():
        off = thf + KELVIN if col == "T" else 0.0
        d, nbad = X.rounded_match(csv[col].to_numpy(), W(wcol[col]), CSV_DECIMALS[col], scale[col], off, pre_round=p)
        res[col] = {"ratio_decimals": p, "csv_decimals": CSV_DECIMALS[col], "cells_differing": nbad, "max_abs_diff": d}
        resolution[col] = scale[col] * 10.0 ** -p
        if nbad:
            bad_cols.append(col)
    # negative control: one decimal less (or more) on the ratio must NOT reproduce the CSV
    ctrl_d, ctrl_bad = X.rounded_match(csv["wt"].to_numpy(), W("wT"), 4, uH * dth, 0.0, pre_round=3)
    check(B, c, "csv_equals_workbook_ratio_rounded_then_rescaled", not bad_cols, cells_per_column=len(csv), columns_not_reproduced=bad_cols, per_column=res,
          control_one_decimal_coarser_cells_differing=ctrl_bad,
          note="CSV = round(round(workbook ratio, 3 for U V W or 4 otherwise) x reference scale, printed decimals): zero cells differ in 14 columns. The published heat fluxes therefore sit on a grid of 0.0049 K m/s and k on 0.00021 m2/s2; the table carries the workbook values")
    kerr = np.abs(pts.k - 0.5 * (pts.uu + pts.vv + pts.ww)).to_numpy()
    check(B, c, "workbook_variance_columns_give_k", float(np.max(kerr / pts.k.to_numpy())) < 2e-4, max_abs_error=float(kerr.max()), max_rel_error=float(np.max(kerr / pts.k.to_numpy())),
          note="k = (<u'2>+<v'2>+<w'2>)/2 from the workbook's variance columns, to the 5 significant digits those columns carry")
    sig2 = {n_: (W(wcol_) * uH) ** 2 for n_, wcol_ in (("uu", "su"), ("vv", "sv"), ("ww", "sw"))}
    dsig = {n_: float(np.max(np.abs(pts[n_].to_numpy() - v))) for n_, v in sig2.items()}
    rel = {n_: float(np.max(np.abs(pts[n_].to_numpy() / v - 1))) for n_, v in sig2.items()}
    over1 = int(((np.abs(pts.uu.to_numpy() / sig2["uu"] - 1) > 0.01) | (np.abs(pts.vv.to_numpy() / sig2["vv"] - 1) > 0.01) | (np.abs(pts.ww.to_numpy() / sig2["ww"] - 1) > 0.01)).sum())
    check(B, c, "published_variance_vs_published_sigma_squared", max(rel.values()) < 0.005, warn=True, max_abs_diff_m2_s2=dsig, max_rel_diff=rel, rows_with_a_component_differing_by_more_than_1_percent=over1,
          note="the workbook's <u'2>, <v'2>, <w'2> are not always sigma^2 of the sigma columns (the CSV carries only the sigma). The table uses the variance columns, which reproduce k; a reader squaring the CSV's rms differs from them by the amounts listed")
    check(B, c, "csv_and_workbook_coordinates_agree", float(np.max(np.abs(np.array([[r[1] * H, r[2] * H, r[3] * H] for r in recs]) - csv[["x", "y", "z"]].to_numpy()))) < 1e-9)

    # reference scales
    c0_formula = GAS_FRACTION * Q_GAS / (uH * H ** 2) * 1e6
    c0_readme = GAS_FRACTION * Q_GAS / (U_H_STATED * H ** 2) * 1e6
    check(B, c, "c0_from_q_gas_fraction_UH_H_equals_workbook", abs(c0_formula / c0 - 1) < 1e-6, c0_workbook_ppm=c0, c0_formula_ppm=c0_formula, c0_with_readme_UH_1_46_ppm=c0_readme,
          c0_without_the_5_percent_ppm=c0_formula / GAS_FRACTION,
          note="c0 = (5 % ethylene) x q / (U_H H^2) with U_H = 1.4581 m/s (the readme rounds it to 1.46). Dividing by q/(U_H H^2) alone would give a c0 twenty times larger; the data paper states no c0 for Case J (QUESTIONS.md QJ2)")
    check(B, c, "concentration_ratio_is_C_over_c0", float(np.max(np.abs(pts.concentration_ratio * c0 - pts.C) / np.maximum(pts.C, 1.0))) < 1e-8, note="to the 10 significant digits the table carries")
    thH = K["<θH> (oC)"]
    check(B, c, "temperatures_in_workbook_agree_with_readme", abs(thf + KELVIN - 318.95) < 1e-9 and abs(thH + KELVIN - 285.32) < 5e-3 and abs(K["<θgas> (oC)"] + KELVIN - 303.55) < 1e-9 and abs(dth - (thf - thH)) < 0.05,
          T_floor_K=thf + KELVIN, T_H_K=thH + KELVIN, T_gas_K=K["<θgas> (oC)"] + KELVIN, delta_theta_workbook=dth, theta_f_minus_theta_H=thf - thH, readme="T_f = 318.95 K, T_b = 285.32 K (the readme's 'T_b' is the approach flow at building height, not the building), gas 303.55 K")
    Rb = 9.80665 * H * (thH - thf) / ((K["<θ0> (oC)"] + KELVIN) * uH ** 2)
    check(B, c, "bulk_richardson_number_recomputed", abs(Rb / K["Rb"] - 1) < 0.01, Rb_workbook=K["Rb"], Rb_recomputed=Rb, readme=-0.086, formula="g H (theta_H - theta_f) / (theta_0 U_H^2), theta_0 = <θ0> of the workbook")
    Re = U_H_STATED * H / 1.43e-5
    check(B, c, "reynolds_number_readme_vs_paper", abs(RE_README / Re - 1) < 0.1, warn=True, Re_from_UH_H_nu_1_43e_5=Re, Re_data_paper=RE_PAPER, Re_readme=RE_README,
          note="U_H H / nu = 1.6e4 as the data paper states; the readme's 43,000 is Case H's value (3.23 m/s x 0.2 m). Listed in QUESTIONS.md QJ3")

    # geometry, frame and source
    inside = X.inside_count(pts, boxes)
    ctrl = X.inside_count(pts, boxes, (0.04, 0.0, 0.0))
    check(B, c, "no_sensor_inside_building", inside == 0, inside=inside, points=n)
    check(B, c, "control_shifted_points_are_detected_inside", ctrl > 0, inside_after_shift=ctrl, shift_m=[0.04, 0, 0])
    xyzmin, xyzmax = [float(pts[a].min()) for a in "xyz"], [float(pts[a].max()) for a in "xyz"]
    check(B, c, "extents_sane", xyzmin[0] >= -0.17 and xyzmax[0] <= 0.33 and abs(xyzmin[1]) <= 0.17 and xyzmax[1] <= 0.17 and 0.0 < xyzmin[2] and xyzmax[2] <= 0.29, bbox_min=xyzmin, bbox_max=xyzmax,
          note="MP-y_caseJ.png: x -0.16 .. 0.32, z 0.004 .. 0.28; MP-z_caseJ.png: y -0.16 .. 0.16")
    plane = {"y=0": int((pts.y == 0).sum()), "z=0.004": int((pts.z == 0.004).sum()), "z=0.04": int((pts.z == 0.04).sum())}
    check(B, c, "points_lie_on_the_three_planes_of_the_data_paper", plane == {"y=0": 153, "z=0.004": 109, "z=0.04": 205}, rows_per_plane=plane, note="y/H = 0, z/H = 0.025 and 0.25 (data paper section 3.10); the planes share points on y = 0")
    # the source: where C peaks
    peak = pts.loc[pts.C.idxmax()]
    dist = float(math.hypot(peak.x - SOURCE_X, peak.y))
    check(B, c, "concentration_peaks_at_the_source", dist < 1e-9 and peak.z <= 0.0041, peak_point_id=int(peak.point_id), peak_xyz=[float(peak.x), float(peak.y), float(peak.z)], C_ppm=float(peak.C), source_xy=[SOURCE_X, 0.0],
          note="the source is 0.25 H = 0.04 m beyond the leeward wall (readme); the highest mean concentration is the point 4 mm above it, where the flow is reversed (U < 0)")
    up = pts[(pts.x <= -0.1) & (pts.y == 0.0)]
    afU = float(np.interp(math.log(HEIGHT), np.log(afl.z), afl.U))
    check(B, c, "WD0_flow_is_along_x", bool((afl.U > 0).all()) and float(up.U.mean()) > 0 and float((pts.C * (pts.x - SOURCE_X)).sum()) > 0, approach_flow_U_positive_rows=int((afl.U > 0).sum()), mean_U_upwind_of_building=float(up.U.mean()),
          C_weighted_mean_x_minus_source=float((pts.C * (pts.x - SOURCE_X)).sum() / pts.C.sum()), note="U > 0 in the approach flow, and the plume is carried toward +x")
    side = pts[(np.isclose(pts.y, -0.05)) & (pts.x <= -0.08) & (pts.z <= 0.04)]
    wake = pts[(np.isclose(pts.y, -0.05) | np.isclose(pts.y, -0.07)) & (pts.x >= 0.04) & np.isclose(pts.z, 0.04)]
    check(B, c, "lateral_sign_V_negative_on_the_windward_y_negative_side_and_positive_in_the_wake", bool((side.V < 0).all()) and bool((wake.V > 0).all()) and len(side) > 0 and len(wake) > 0,
          side_V=side.V.tolist(), wake_V=wake.V.tolist(), note="beside the upstream half of the y < 0 side the flow turns away from the centreline (V < 0); behind the building it closes toward it (V > 0): V is positive toward +y as in Cases A and D")
    check(B, c, "building_surface_temperature_matches_workbook", bd_diff < 1e-9 and len(bd) == 121, points=len(bd), max_abs_diff_degC=bd_diff, mean_surface_degC=float(bd["T"].mean()), workbook_theta_build=K["<θbuild> (oC)"])
    check(B, c, "building_surface_temperature_mean_equals_workbook_theta_build", abs(float(bd["T"].mean()) - K["<θbuild> (oC)"]) < 1e-9,
          mean_surface_degC=float(bd["T"].mean()), workbook_theta_build=K["<θbuild> (oC)"], abs_difference_degC=abs(float(bd["T"].mean()) - K["<θbuild> (oC)"]), points=len(bd))
    on_surface = bool(np.all((bd.x >= -0.08 - 1e-9) & (bd.x <= 1e-9) & (bd.y.abs() <= 0.04 + 1e-9) & (bd.z <= HEIGHT + 1e-9) & ((np.isclose(bd.x, -0.08) | np.isclose(bd.x, 0.0) | np.isclose(bd.y.abs(), 0.04) | np.isclose(bd.z, HEIGHT)))))
    check(B, c, "building_surface_points_lie_on_the_building_faces", on_surface, points=len(bd), bbox_min=[float(bd[a].min()) for a in "xyz"], bbox_max=[float(bd[a].max()) for a in "xyz"])

    # signs of the turbulent fluxes in an unstable boundary layer: heat flows up (w'theta' > 0), the air cools with height, momentum flows down (u'w' < 0)
    st = full.sort_values(["x", "z"])
    t_drop = bool(all((g_["T"].diff().dropna() < 0).all() for _, g_ in st.groupby("x")))
    check(B, c, "turbulent_flux_signs_are_those_of_an_unstable_layer", bool((full.wT > 0).all()) and t_drop and float((full.uw < 0).mean()) >= 0.9 and float((pts.wT > 0).mean()) >= 0.9,
          approach_flow_wT_positive_fraction=float((full.wT > 0).mean()), approach_flow_T_decreases_with_height_at_every_station=t_drop, approach_flow_uw_negative_fraction=float((full.uw < 0).mean()),
          points_wT_positive_fraction=float((pts.wT > 0).mean()), note="w'theta' > 0 (upward heat flux over the heated floor), T falls with z, u'w' < 0: the signs the published columns must have if they are in the usual convention")
    # inflow
    afk = {"U": afc.U, "V": afc.V, "W": afc.W, "u_rms": afc.u_rms, "v_rms": afc.v_rms, "w_rms": afc.w_rms, "uv": afc.uv, "uw": afc.uw, "k": afc.k, "t_rms": afc.t_rms, "ut": afc.ut, "vt": afc.vt, "wt": afc.wt}
    st1 = stations[min(stations)]
    afw = {"U": [r[4] for r in st1], "V": [r[6] for r in st1], "W": [r[8] for r in st1], "u_rms": [r[10] for r in st1], "v_rms": [r[12] for r in st1], "w_rms": [r[14] for r in st1],
           "uv": [r[22] for r in st1], "uw": [r[24] for r in st1], "k": [r[26] for r in st1], "t_rms": [r[30] for r in st1], "ut": [r[32] for r in st1], "vt": [r[34] for r in st1], "wt": [r[36] for r in st1]}
    afs = {"U": uH, "V": uH, "W": uH, "u_rms": uH, "v_rms": uH, "w_rms": uH, "uv": uH ** 2, "uw": uH ** 2, "k": uH ** 2, "t_rms": dth, "ut": uH * dth, "vt": uH * dth, "wt": uH * dth}
    afd = {"U": 2, "V": 2, "W": 2, "u_rms": 3, "v_rms": 3, "w_rms": 3, "uv": 4, "uw": 4, "k": 4, "t_rms": 3, "ut": 3, "vt": 3, "wt": 3}
    pfound, afbad = {}, []
    for col in afk:
        for p in (3, 4, 5, 6):
            d, nb = X.rounded_match(afk[col], afw[col], afd[col], afs[col], 0.0, pre_round=p)
            if nb == 0:
                pfound[col] = p
                break
        else:
            afbad.append(col)
    tK = X.rounded_match(afc["T"], [r[28] for r in st1], 2, dth, thf + KELVIN, pre_round=4)
    check(B, c, "approach_flow_csv_is_workbook_station_x_minus_2.5H_rounded", not afbad and len(st1) == len(afc) and tK[1] == 0 and set(stations) == {-2.5, 0.0, 2.5}, rows=len(afc), ratio_decimals_that_reproduce_the_csv=pfound, columns_not_reproduced=afbad,
          stations_x_over_H=sorted(stations), note="AF_caseJ.csv is the first of the workbook's three empty-tunnel stations (x/H = -2.5, 0, +2.5); the other two are in cases/J/approach_flow_full.csv")
    u_at_H = float(np.interp(math.log(HEIGHT), np.log(afl.z), afl.U))
    check(B, c, "U_H_from_profile_matches_stated", abs(u_at_H - U_H_STATED) < 0.05 and abs(u_at_H - uH) < 0.01, U_H_profile=u_at_H, U_H_stated=U_H_STATED, U_H_workbook=uH)
    st_u = {str(xs): {"U_over_UH_at_z_eq_H": float(np.interp(math.log(1.0), np.log([r[3] for r in rr]), [r[4] for r in rr])), "U_over_UH_at_z_eq_0.01875H": rr[0][4]} for xs, rr in sorted(stations.items())}
    fit = B.log_law_fit(afl.z, afl.U, 0.02, 2 * HEIGHT)
    inflow = {"U_H_m_s": round(u_at_H, 4), "U_H_stated_m_s": U_H_STATED, "U_H_workbook_m_s": uH, "H_m": HEIGHT,
              "log_law": {**fit, "error_at_H_rel": round(B.log_law_U(fit, HEIGHT) / u_at_H - 1, 4), "note": "unstably stratified: a neutral log law is only a rough description (see rms_residual_rel)"},
              "power_law": B.power_law_fit(afl.z, afl.U, 0.02, 2 * HEIGHT), "method": f"least squares, kappa = {B.KAPPA}, z = 0.02 .. 2H on AF_caseJ.csv",
              "turbulence_intensity_at_H": round(float(afc[np.isclose(afc.z, HEIGHT)].u_rms.iloc[0]) / u_at_H, 4),
              "stratification": {"floor_temperature_degC": thf, "air_temperature_at_H_degC": round(thH, 4), "delta_theta_K": dth, "approach_mean_temperature_degC": K["<θ0> (oC)"], "gas_temperature_degC": K["<θgas> (oC)"],
                                 "building_mean_surface_temperature_degC": round(K["<θbuild> (oC)"], 4), "bulk_Richardson_number": round(K["Rb"], 5), "profile": "cases/J/approach_flow_full.csv (T, T_rms, uT, vT, wT per height)"},
              "streamwise_change_without_building": {"note": "the workbook's empty-tunnel profiles at x/H = -2.5, 0, +2.5 do not coincide: U/U_H at z = H and at the lowest height", **st_u}}
    check(B, c, "empty_tunnel_profile_is_the_same_at_all_three_stations", abs(st_u["0.0"]["U_over_UH_at_z_eq_0.01875H"] / st_u["-2.5"]["U_over_UH_at_z_eq_0.01875H"] - 1) < 0.1, warn=True, **{f"x_over_H_{k}": v for k, v in st_u.items()},
          note="U at z = 0.019 H is 0.33 U_H at x/H = -2.5 but 0.58 at x/H = 0 (the building's own position), 0.50 at +2.5; the CSV, and any inlet taken from it, is the upstream profile only")

    # expanded uncertainty carried by the workbook (no column for it in the table)
    ue_scale = {"U": uH, "V": uH, "W": uH, "su": uH, "sv": uH, "sw": uH, "uu": uH ** 2, "vv": uH ** 2, "ww": uH ** 2, "k": uH ** 2, "T": dth, "T_rms": dth,
                "uT": uH * dth, "vT": uH * dth, "wT": uH * dth, "C": c0, "c_rms": c0}
    unit = {"U": "m/s", "V": "m/s", "W": "m/s", "su": "m/s", "sv": "m/s", "sw": "m/s", "uu": "m2/s2", "vv": "m2/s2", "ww": "m2/s2", "k": "m2/s2", "T": "K", "T_rms": "K", "uT": "K m/s", "vT": "K m/s", "wT": "K m/s", "C": "ppm", "c_rms": "ppm"}
    ue_rows = [(s, i, r) for s, i, r in wrows]
    seed = wb["xy-plane2(Unstable state)"][30][WB_COL["wT"] + 1]            # second data row: the first cell of the fill series
    fill = [(s, i) for s, i, r in ue_rows if r[WB_COL["wT"] + 1] >= 1.0]
    frac_ok = all(abs((r[WB_COL["wT"] + 1] - round(r[WB_COL["wT"] + 1])) - (seed - round(seed))) < 1e-9 for s, i, r in ue_rows if r[WB_COL["wT"] + 1] >= 1.0)
    uncertainty = {}
    for q_, col in WB_COL.items():
        vals = [r[col + 1] * ue_scale[q_] for s, i, r in ue_rows if not (q_ == "wT" and r[col + 1] >= 1.0)]
        uncertainty[q_] = {**X.stats(vals), "unit": unit[q_], "workbook_columns": f"{_letter(col)} value, {_letter(col + 1)} Ue"}
        if q_ == "wT":
            uncertainty[q_]["excluded_fill_series_cells"] = len(fill)
    cz = np.array([[r[WB_COL["C"]], r[WB_COL["C"] + 1]] for s, i, r in ue_rows])
    n_below = int((cz[:, 0] <= cz[:, 1]).sum())
    uncertainty["C"]["rows_where_mean_C_does_not_exceed_its_own_Ue"] = n_below
    uncertainty["C"]["fraction_of_rows"] = round(n_below / len(ue_rows), 3)
    big = cz[cz[:, 0] * c0 > 20.0]
    uncertainty["C"]["relative_Ue_median_where_C_above_20_ppm"] = round(float(np.median(big[:, 1] / big[:, 0])), 4)
    check(B, c, "expanded_uncertainty_cells_are_valid", len(fill) == 0, warn=True, cells_that_are_an_excel_fill_series=len(fill), sheet="xy-plane2(Unstable state)", column=_letter(WB_COL["wT"] + 1), same_fractional_part=frac_ok,
          seed=float(seed), first_rows=[i for s, i in fill[:4]], note="the Ue column of <w'θ'> in the sheet xy-plane2 reads 1.0037, 2.0037, 3.0037 ... 193.0037: the cell 0.00374 dragged down with Excel's fill handle (+1 per row), so the real expanded uncertainty of w'θ' at z/H = 0.25 is lost for those rows; excluded from the summary")
    check(B, c, "mean_concentration_exceeds_its_expanded_uncertainty_everywhere", n_below == 0, warn=True, rows=len(ue_rows), rows_where_C_does_not_exceed_Ue=n_below, csv_point_ids_with_C_exactly_zero=[int(v) for v in pts.point_id[pts.C == 0.0]], median_Ue_C_ppm=uncertainty["C"]["median"], median_Ue_C_over_c0=round(uncertainty["C"]["median"] / c0, 4),
          note="Ue of the mean concentration is about 1 ppm (0.08 c0) plus roughly 5 % of the value; far from the plume C is below it. Four CSV rows read exactly 0.0 (the analyser baseline)")

    frame = {"origin": "the building's leeward (downwind) wall centre on the ground; x = 0 is the leeward wall", "x": "+x streamwise (the wind blows toward +x); building x in [-0.08, 0]; floor source at x = +0.04 m (0.25 H beyond the leeward wall)",
             "y": "+y lateral; building y in [-0.04, 0.04]; the z/H = 0.025 plane is measured on the y <= 0 side only, the z/H = 0.25 plane on both", "z": "+z up; roof at 0.16; heated floor at z = 0",
             "length_scale": "model metres (the sources state no model:full scale ratio); b = 0.08 m, H = 0.16 m",
             "source": "5 mm diameter floor outlet at (0.04, 0, 0); 5 % ethylene in air at 30.4 degC, 9.17e-6 m3/s (readme, data paper section 3.10)"}
    transform = {"coordinate_scale": 1.0, "lateral_sign": 1, "origin_shift_m": [0, 0, 0], "temperature": "K -> degC (workbook values; the CSV is in Kelvin)",
                 "note": "values from the workbook at full precision (the CSV is these ratios rounded; checked); variances from the workbook's <u'2> columns; no coordinate or sign change"}
    normalisation = {"concentration": {"c0_ppm": round(c0, 6), "definition": "c0 = (gas fraction 0.05) x q / (U_H H^2), q = 9.17e-6 m3/s, U_H = 1.4581 m/s, H = 0.16 m", "source": "LF_caseJ.xlsx 'Experimental Condition' cell (Co); recomputed in check c0_from_q_gas_fraction_UH_H_equals_workbook",
                                      "without_gas_fraction_ppm": round(c0_formula / GAS_FRACTION, 4)},
                     "velocity": {"U_H_m_s": uH, "height_m": HEIGHT}, "temperature": {"theta_f_degC": thf, "delta_theta_K": dth, "definition": "(T - T_f) / delta_theta"}}
    extra = {"normalisation": normalisation,
             "known_issues": {"csv_unit_of_T": "RS_caseJ.csv, AF_caseJ.csv and BD-ST_caseJ.csv give temperature in KELVIN; the table carries degC (T) and K (T_rms, a difference)",
                              "duplicate_row": "RS_caseJ.csv No. 1 and No. 153 are the same row (-0.16, 0, 0.004)",
                              "published_resolution": "the CSV is the workbook's ratios rounded to 1e-3 (U, V, W) or 1e-4: heat fluxes sit on a 0.0049 K m/s grid, k on 0.00021 m2/s2; the table uses the workbook values",
                              "fill_series_uncertainty": f"workbook sheet xy-plane2, column {_letter(WB_COL['wT'] + 1)} (Ue of the w'theta' flux): {len(fill)} cells are 0.0037 + a running integer, not an uncertainty",
                              "readme_reynolds_number": "readme 43,000, data paper 1.6e4 (U_H H / nu); 43,000 is Case H's",
                              "no_shear_stresses_at_points": "uv, uw, vw are published only for the approach flow",
                              "c0_includes_gas_fraction": "c0 = 12.283 ppm contains the 5 % ethylene fraction of the released gas; q / (U_H H^2) alone is 245.7 ppm; the data paper states no c0 for J (QUESTIONS.md QJ2)",
                              "variance_vs_sigma": "the workbook's <u'2>, <v'2>, <w'2> differ from the squares of its sigma columns by up to 3 % in single rows; the table uses the variances, which reproduce k (QUESTIONS.md QJ4)",
                              "expanded_uncertainty": "the workbook lists an expanded uncertainty beside every quantity (summary in extra_measurements.expanded_uncertainty); the mean concentration does not exceed its own (about 1 ppm) at 197 of 465 rows",
                              "inflow_stations": "the empty-tunnel profile at x/H = 0 and +2.5 differs from the published one at x/H = -2.5 near the ground (cases/J/approach_flow_full.csv; QUESTIONS.md QJ5)",
                              "readme_T_b": "the readme's T_b = 285.32 K is the approach-flow air temperature at z = H, not the building (121 measured surface points: 22.0 .. 28.9 degC, cases/J/surface_temperature.csv)"},
             "expanded_uncertainty": {"where": "LF_caseJ.xlsx, sheets xz-plane(Unstable state), xy-plane(Unstable state), xy-plane2(Unstable state) and Unstable Inflow: every measured quantity has a 'Measurement' column and an 'Expanded Uncertainty: Ue' column beside it, in the workbook's non-dimensional units; the table has no column for it. per_quantity is in physical units over the 465 workbook rows of the three measurement sheets (columns are the table's names, su/sv/sw = the rms columns)",
                                      "coverage_factor": "not stated in the workbook (ISO/IEC Guide 98-3 per the data paper)", "per_quantity": uncertainty},
             "resolution_of_published_ratios": {k: float(v) for k, v in resolution.items()},
             "extra_files": {"surface_temperature": {"file": "cases/J/surface_temperature.csv", "columns": ["x", "y", "z", "T"], "units": ["m", "m", "m", "degC"], "rows": len(bd), "source": "BD-ST_caseJ.csv (Kelvin there)"},
                             "approach_flow_full": {"file": "cases/J/approach_flow_full.csv", "columns": list(full.columns), "units": ["m", "m", "m/s", "m/s", "m/s", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "degC", "K", "K m/s", "K m/s", "K m/s"],
                                                    "rows": len(full), "source": "LF_caseJ.xlsx 'Unstable Inflow' (three stations x = -0.4, 0, +0.4 m, no building)"}},
             "csv_vs_workbook_rounding": res}
    return pts, afl, geo, X.sig(inflow, 10), frame, transform, X.sig(extra, 10)
