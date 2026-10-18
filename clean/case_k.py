"""Case K (ArraysC) — 9 x 9 cube array with a floor point source, isothermal.

Zenodo 10.5281/zenodo.15448050 (Yoshie, Tachibana). build(B, prov) is called by clean/build.py with the build module
as B and returns (points, approach flow, geometry, inflow, frame, transform, extra).

RS_caseK.csv has no point numbers and is the workbook's 'Measurement data' sheet rounded to 3 decimals (velocities)
and 2 decimals (concentration) with k recomputed from the rounded rms values; the point table is built from the
workbook at full precision and the CSV is the cross-check.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

import jkl_common as X

check = X.check

META = {
    "id": "K", "title": "Case K — 9 x 9 cube array, floor point source",
    "folder": "raw/cases/case-k", "zenodo_concept": "10.5281/zenodo.15448050", "zenodo_version": None,
    "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    "collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Takumi Tachibana (Wind Engineering Institute)"],
    "citation": "Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. https://doi.org/10.1007/978-4-431-55912-2_9",
}

# stated by the readme / data paper section 3.11 (verified or contradicted in the checks)
H, U_H_STATED, Q_GAS, ROWS, COLS = 0.06, 2.33, 3.6e-6, 9, 9
SOURCE = (-0.15, 0.0)               # 0.15 m windward of the origin, between rows 2 and 3, on the centre line
PITCH, X_FIRST, Y_FIRST = 0.12, -0.36, -0.51   # row 1 starts 3 pitches upwind of the origin wall; 9 columns centred on y = 0


def build(B, prov):
    c = "K"
    folder = os.path.join(B.REPO, META["folder"])
    f = {n: os.path.join(folder, n) for n in ("RS_caseK.csv", "AF_caseK.csv", "LF_caseK.xlsx", "readme_caseK.md", "MP-y_caseK.png", "MP-z_caseK.png")}
    hcsv = os.path.join(B.REPO, "raw", "cases", "case-h", "AF_caseH.csv")
    prov[c] = list(f.values())
    B.DIRECTION_BASIS[c] = ("definition: +x streamwise (MP drawings: rows along x, the source 0.15 m upwind of the origin wall); checks WD0_flow_is_along_x, concentration_peaks_at_the_source", "settled")
    wb = X.read_xlsx(f["LF_caseK.xlsx"])
    sh = wb["Measurement data"]
    ref = X.labelled_constants(sh, 16, 17)
    H_wb = UH_wb = C0_wb = Cgas_wb = q_wb = None
    for k_, v_ in ref.items():
        kk = " ".join(k_.split())
        if kk.startswith("Reference height"):
            H_wb = v_
        elif kk.startswith("Reference velocity"):
            UH_wb = v_
        elif kk.startswith("Standard concentation"):
            C0_wb = v_
        elif kk.startswith("release gas"):
            Cgas_wb = v_
        elif kk.startswith("Gas flow rate"):
            q_wb = v_
    wrows = [r for r in sh[3:] if isinstance(r[1], float)]
    if len(wrows) != 203 or None in (H_wb, UH_wb, C0_wb):
        raise SystemExit("Case K: the workbook's 'Measurement data' sheet no longer has the layout the builder reads")
    B.log(f"[K] LF_caseK.xlsx 'Measurement data': reference height H = {H_wb} m, reference velocity UH = {UH_wb} m/s, release concentration {Cgas_wb} ppm, q = {q_wb} m3/s, C0 = {C0_wb:.6f} ppm — "
          "NOT the readme's cube (H = 0.06 m, U_H = 2.33 m/s); the workbook's normalised columns use H = 0.2 m (Case H's building) and a different reference velocity")

    header, rows = B.read_csv_rows(f["RS_caseK.csv"])
    idx = {h: i for i, h in enumerate(header)}
    B.log(f"[K] RS_caseK.csv header (bare): {header}; the published header has a space before every unit ('x (m)'); NO point-number column; published units m, m/s, m2/s2, ppm")
    csv = pd.DataFrame([{n: B.num(r[idx[n]]) for n in header} for r in rows])
    w = pd.DataFrame([{"x": r[1] / 1000.0, "y": r[2] / 1000.0, "z": r[3] / 1000.0, "usc": r[4], "susc": r[5], "U": r[6], "V": r[7], "W": r[8], "su": r[9], "sv": r[10], "sw": r[11], "k": r[12], "C": r[13], "sc": r[14],
                      "xH": r[19], "yH": r[20], "zH": r[21], "uscUH": r[22], "uUH": r[24], "kUH2": r[30], "cC0": r[31], "scC0": r[32]} for r in wrows])
    c0 = Q_GAS / (U_H_STATED * H ** 2) * 1e6                    # the data paper's definition, with the cube's own H and U_H
    B.log(f"[K] point_id = row order of RS_caseK.csv (1..203; the workbook has none either). concentration_ratio = C / c0 with c0 = q / (U_H H^2) = {c0:.4f} ppm, "
          f"U_H = 2.33 m/s and H = 0.06 m as the readme and data paper state them; the workbook's own C0 = {C0_wb:.4f} ppm belongs to H = 0.2 m, UH = 4.94 m/s (QUESTIONS.md QK1)")
    pts = pd.DataFrame([B.row(case_id=c, instrument="split_fibre", point_id=i + 1, x=round(r.x, 9), y=round(r.y, 9), z=round(r.z, 9), U=r.U, V=r.V, W=r.W, uu=r.su * r.su, vv=r.sv * r.sv, ww=r.sw * r.sw, k=r.k,
                                   C=r.C, c_rms=r.sc, concentration_ratio=r.C / c0) for i, r in enumerate(w.itertuples())], columns=B.POINT_COLUMNS)
    pts = X.tidy(pts)
    B.log("[K] transform: workbook values (x, y, z mm -> m; the CSV is these rounded); rms squared to variances; uv, uw, vw, uc..wT, T: not published for the points -> NaN; <usc> and its sd (workbook only) are not carried")

    # ---- approach flow (published CSV: one station, x = -0.493 m; identical to Case H's file)
    h2, ar = B.read_csv_rows(f["AF_caseK.csv"])
    a2 = {n: i for i, n in enumerate(h2)}
    afc = pd.DataFrame([{n: B.num(r[a2[n]]) for n in h2} for r in ar])
    afl = pd.DataFrame({"case_id": c, "z": afc.z, "U": afc.U, "uu": afc.u_rms ** 2, "vv": afc.v_rms ** 2, "ww": afc.w_rms ** 2, "k": afc.k})
    full = pd.DataFrame({"x": afc.x, "z": afc.z, "U": afc.U, "V": afc.V, "W": afc.W, "uu": afc.u_rms ** 2, "vv": afc.v_rms ** 2, "ww": afc.w_rms ** 2, "uv": afc.uv, "uw": afc.uw, "k": afc.k})
    B.write_csv(os.path.join(B.HERE, "cases", c, "approach_flow_full.csv"), full)
    B.log("[K] approach flow: AF_caseK.csv, 17 heights at x = -0.493 m, rms squared; V, W, uv, uw also in cases/K/approach_flow_full.csv")

    boxes = X.cube_boxes(ROWS, COLS, X_FIRST, Y_FIRST, H, PITCH)
    geo = [("default", boxes, "generated: 81 cubes of 0.06 m on a 0.12 m pitch (street width = H, plan area ratio 25 %), 9 rows along x from x = -0.36 m (row 4 starts at the origin) and 9 columns centred on y = 0; "
                              "the pitch is read from MP-y_caseK.png / MP-z_caseK.png and bounded by the points and the source position (checks)")]

    # ---- checks
    n = len(pts)
    check(B, c, "row_count_matches_source", n == 203 and len(csv) == 203 and len(wrows) == 203, rows=n, csv_rows=len(csv), workbook_rows=len(wrows), note="the readme and data paper give no count; the data paper says 'approximately 30 points at eight heights' (QUESTIONS.md QK4)")
    same_xyz = float(np.max(np.abs(w[["x", "y", "z"]].to_numpy() - csv[["x", "y", "z"]].to_numpy())))
    check(B, c, "csv_and_workbook_list_the_same_203_points_in_the_same_order", same_xyz < 1e-9 and not pts.duplicated(["x", "y", "z"]).any(), max_abs_diff_xyz_m=same_xyz, note="workbook x, y, z are millimetres in the data sheet")
    check(B, c, "no_sentinels_or_nan_in_measured_columns", not pts[["x", "y", "z", "U", "V", "W", "uu", "vv", "ww", "k", "C", "c_rms"]].isna().any().any() and bool((pts.C > 0).all()))
    rnd = {}
    for a, b_, d in (("U", "U", 3), ("V", "V", 3), ("W", "W", 3), ("u_rms", "su", 3), ("v_rms", "sv", 3), ("w_rms", "sw", 3), ("C", "C", 2), ("c_rms", "sc", 2)):
        rnd[a] = X.within_half_unit(csv[a].to_numpy(), w[b_].to_numpy(), d)
    krecomp = np.round(0.5 * (csv.u_rms ** 2 + csv.v_rms ** 2 + csv.w_rms ** 2), 3)
    kcsv_ties = int((np.abs(krecomp - csv.k) > 1e-9).sum())
    kwb = float(np.max(np.abs(w.k - 0.5 * (w.su ** 2 + w.sv ** 2 + w.sw ** 2))))
    check(B, c, "csv_equals_workbook_rounded", all(v[1] == 0 for v in rnd.values()), per_column={k_: {"max_abs_diff": v[0], "cells_beyond_half_a_unit": v[1], "decimals": d} for (k_, v), d in zip(rnd.items(), (3, 3, 3, 3, 3, 3, 2, 2))},
          note="velocities and rms to 3 decimals, C and c_rms to 2")
    check(B, c, "csv_k_is_recomputed_from_the_rounded_rms_not_the_measured_k", kcsv_ties == 0 and float(np.max(np.abs(csv.k - w.k))) > 1e-4, cells_where_csv_k_differs_from_half_sum_of_the_rounded_rms=kcsv_ties,
          max_abs_diff_csv_k_vs_workbook_k=float(np.max(np.abs(csv.k - w.k))), note="CSV k = round(0.5 (u_rms^2 + v_rms^2 + w_rms^2), 3) of the ROUNDED rms; the workbook's k is the unrounded half-sum and is what the table carries")
    check(B, c, "k_equals_half_sum_of_variances", kwb < 1e-9, max_abs_error=kwb, note="workbook k = 0.5 (sigma_u^2 + sigma_v^2 + sigma_w^2) at full precision")
    nrm = {"x/H*H_wb": float(np.max(np.abs(w.xH * H_wb - w.x))), "u/UH*UH_wb": float(np.max(np.abs(w.uUH * UH_wb - w.U))), "k/UH2*UH2": float(np.max(np.abs(w.kUH2 * UH_wb ** 2 - w.k))),
           "c/C0*C0": float(np.max(np.abs(w.cC0 * C0_wb - w.C))), "usc/UH*UH": float(np.max(np.abs(w.uscUH * UH_wb - w.usc)))}
    check(B, c, "workbook_normalised_columns_use_H_0.2_and_UH_4.94", max(nrm.values()) < 1e-9, max_abs_diff=nrm, H_workbook=H_wb, UH_workbook=UH_wb, C0_workbook_ppm=C0_wb,
          note="every normalised column of the workbook reproduces its dimensional column exactly with H = 0.2 m, UH = 4.94009 m/s and C0 = 18.218 ppm, none of which is the cube's H = 0.06 m / U_H = 2.33 m/s")
    c0_wb_formula = q_wb / (UH_wb * H_wb ** 2) * 1e6 * (Cgas_wb / 1e6)
    check(B, c, "workbook_C0_is_q_over_UH_H2_with_its_own_H_and_UH", abs(c0_wb_formula / C0_wb - 1) < 1e-9, C0_workbook_ppm=C0_wb, C0_recomputed_ppm=c0_wb_formula, c0_used_here_ppm=c0, ratio_used_over_workbook=c0 / C0_wb,
          ratio_of_the_two_definitions_equals=(UH_wb / U_H_STATED) * (H_wb / H) ** 2,
          note="the table's concentration_ratio uses the data paper's cube definition (c0 = 429.18 ppm); multiply it by c0 / C0_workbook = 23.56 to get the workbook's <c>/C0")
    # velocity reference
    u_at_H = float(np.interp(math.log(H), np.log(afl.z), afl.U))
    check(B, c, "U_H_from_profile_matches_stated", abs(u_at_H - U_H_STATED) < 0.05, warn=True, U_H_profile_log_interpolated=u_at_H, U_H_stated=U_H_STATED, z_m=H,
          note="the profile (Case H's, measured at x = -0.493 m) gives 2.24 m/s at z = 0.06 m, 4 % below the stated 2.33; the stated value is used for c0")
    afh = pd.read_csv(hcsv, encoding="utf-8-sig")
    afh.columns = [x_.split("(")[0].strip() for x_ in afh.columns]
    same_af = len(afh) == len(afc) and all(np.allclose(afh[col_].to_numpy(), afc[col_].to_numpy()) for col_ in ("x", "y", "z", "U", "V", "W", "u_rms", "v_rms", "w_rms", "k", "uw", "uv"))
    check(B, c, "approach_flow_is_case_Hs_file", same_af, rows=len(afc), note="AF_caseK.csv equals AF_caseH.csv row for row (data paper: the approach flow was the same as in Case H, whose H = 0.2 m is the 'H' of the workbook)")
    iw = [r for r in wb["Inflow"][2:] if isinstance(r[3], float)]
    uref = afl[np.isclose(afl.z, 0.2)].U.iloc[0]
    implied = {n_: [float(a_ / b_) for a_, b_ in zip(col_.to_numpy(), [r[j_] for r in iw])] for n_, col_, j_ in (("U", afc.U, 7), ("u_rms", afc.u_rms, 10), ("v_rms", afc.v_rms, 11), ("w_rms", afc.w_rms, 12))}
    span = {n_: [round(min(v_), 4), round(max(v_), 4)] for n_, v_ in implied.items()}
    check(B, c, "approach_flow_csv_agrees_with_workbook_inflow_sheet_to_2_percent", len(iw) == len(afc) and bool(np.allclose([r[3] for r in iw], afc.z)) and all(min(v_) > 0.98 * uref and max(v_) < 1.02 * uref for v_ in implied.values()),
          rows=len(iw), reference_implied_by_csv_over_workbook_ratio_m_s=span, U_at_z_0_2_m=float(uref),
          note="the 'Inflow' sheet divides by uH = U(0.2 m) = 3.23 m/s; CSV / ratio spans 3.21 .. 3.27 m/s for U and 3.21 .. 3.24 for the rms: the ratios and the CSV are not one rounding of each other (as in Case C). Sheet units: x, y in mm, z in METRES although headed 'z(mm)'")
    # geometry
    # the pitch: where would the cubes have to be for no point to lie inside one (rows start at x = 0 at every pitch, columns centred on y = 0)
    scan = {p_: X.inside_count(pts, X.cube_boxes(15, 17, -7 * p_, -8 * p_ - H / 2, H, p_)) for p_ in (0.09, 0.10, 0.11, 0.115, 0.12, 0.13, 0.14, 0.15)}
    inside = X.inside_count(pts, boxes)
    ctrl = X.inside_count(pts, boxes, (0.06, 0.0, 0.0))
    check(B, c, "no_sensor_inside_building", inside == 0, inside=inside, points=n)
    check(B, c, "control_shifted_points_are_detected_inside", ctrl > 0, inside_after_shift=ctrl, shift_m=[0.06, 0, 0])
    ok_window = [p_ for p_, v in scan.items() if v == 0]
    check(B, c, "points_bound_the_pitch_between_0.11_and_0.14", bool(ok_window) and 0.12 in ok_window and 0.11 not in ok_window and 0.14 not in ok_window, points_inside_cubes_by_pitch=scan, pitches_with_none_inside=ok_window,
          note="points fall inside the cubes at pitches 0.11 m or less and 0.14 m or more, and at none of 0.115, 0.12, 0.13: the pitch lies between 0.11 and 0.14 m; the drawings read 0.12 m (street = H = 0.06 m); the source at x = -0.15 m lies between rows 2 and 3 for any pitch in 0.105 .. 0.15 m")
    src_ok = (-2 * PITCH + H) <= SOURCE[0] <= -PITCH
    check(B, c, "source_lies_in_the_street_between_rows_2_and_3", src_ok, source_x=SOURCE[0], street_x=[-2 * PITCH + H, -PITCH])
    check(B, c, "volume_and_count_of_the_cube_array", len(boxes) == 81 and abs(sum((b_["max"][0] - b_["min"][0]) * (b_["max"][1] - b_["min"][1]) * (b_["max"][2] - b_["min"][2]) for b_ in boxes) - 81 * H ** 3) < 1e-12,
          cubes=len(boxes), bbox_min=[min(b_["min"][i] for b_ in boxes) for i in range(3)], bbox_max=[max(b_["max"][i] for b_ in boxes) for i in range(3)], plan_area_ratio=H * H / PITCH ** 2,
          note="readme: 9 rows by 9 columns (81 cubes); the array is 1.02 m wide in the 1.2 m tunnel")
    ys, zs = sorted(pts.y.unique()), sorted(pts.z.unique())
    check(B, c, "layout_matches_MP_drawings", ys == [-0.18, -0.12, -0.06, 0.0, 0.06, 0.12, 0.18] and zs == [0.004, 0.01, 0.03, 0.05, 0.07], y_values=ys, z_values=zs,
          note="MP-y_caseK.png: y/H = 0, +-1, +-2, +-3; five heights from 4 mm to 70 mm; z > 0.5 H only on y = 0 and +-1 H")
    peak = pts.loc[pts.C.idxmax()]
    check(B, c, "concentration_peaks_at_the_source", math.hypot(peak.x - SOURCE[0], peak.y - SOURCE[1]) < 1e-9 and peak.z <= 0.0041, peak_point_id=int(peak.point_id), peak_xyz=[float(peak.x), float(peak.y), float(peak.z)], C_ppm=float(peak.C),
          note="the highest mean concentration is the point 4 mm above the outlet at (-0.15, 0, 0) (readme: 0.15 m windward of the origin), where the flow is reversed")
    up = pts[pts.x < -0.1]
    check(B, c, "WD0_flow_is_along_x", bool((afl.U > 0).all()) and float(pts.U[pts.z >= 0.05].mean()) > 0 and float(((pts.x - SOURCE[0]) * pts.C).sum()) > 0,
          mean_U_at_z_at_least_0_05=float(pts.U[pts.z >= 0.05].mean()), C_weighted_mean_x_minus_source=float(((pts.x - SOURCE[0]) * pts.C).sum() / pts.C.sum()), note="U > 0 in the approach flow and above the street; the plume is carried toward +x")
    # y-mirror pairs
    d = pts.assign(kx=pts.x.round(4), ky=pts.y.round(4), kz=pts.z.round(4))
    pos = d[d.ky > 0].set_index(["kx", "ky", "kz"])
    neg = d[d.ky < 0].assign(ky=lambda t: -t.ky).set_index(["kx", "ky", "kz"])
    j = pos.join(neg, lsuffix="_p", rsuffix="_n", how="inner")
    rel = lambda a, b_: float(np.mean(np.abs(j[a + "_p"] - b_ * j[a + "_n"])) / np.mean(np.abs(j[a + "_p"])))   # noqa: E731
    even_v = float(np.mean(np.abs(j.V_p + j.V_n)) / 2)
    odd_v = float(np.mean(np.abs(j.V_p - j.V_n)) / 2)
    check(B, c, "y_mirror_pairs_agree_in_U_and_k", rel("U", 1) < 0.1 and rel("k", 1) < 0.1, pairs=len(j), rel_mean_abs_diff_U=rel("U", 1), rel_mean_abs_diff_k=rel("k", 1), rel_mean_abs_diff_W=rel("W", 1),
          note="the array and the source are y-symmetric; the +y and -y points of the same (x, |y|, z) agree to this much in the velocity statistics")
    check(B, c, "y_mirror_pairs_agree_in_C", rel("C", 1) < 0.1, warn=True, pairs=len(j), rel_mean_abs_diff_C=rel("C", 1),
          note="the mean concentration is not mirror-symmetric: the +y and -y values of the same point differ by this fraction on average, so it is not a repeatability estimate")
    check(B, c, "lateral_velocity_is_an_offset_not_an_antisymmetric_field", odd_v > even_v, warn=True, mean_even_part_m_s=even_v, mean_odd_part_m_s=odd_v, approach_flow_mean_V_m_s=float(afc.V.mean()), pairs=len(j),
          note="in a y-symmetric flow V is odd in y; here the even part (a cross-flow offset of about 2 degrees, also present in the empty-tunnel profile) is three times the odd part, so the data cannot confirm the sign of V; it is carried as published, +y by the frame")
    # mass balance: the tracer flux through the sampled part of three cross-sections against q
    q_ppm = Q_GAS * 1e6
    ratios = {}
    for x_ in (-0.03, 0.09, 0.21):
        line = {}
        for y_ in sorted(pts.y.unique()):
            s_ = pts[(pts.x == x_) & (pts.y == y_)].sort_values("z")
            if len(s_):
                f_ = (s_.U * s_.C).to_numpy()
                line[y_] = X.trapezoid(np.r_[f_[0], f_], np.r_[0.0, s_.z.to_numpy()])
        ratios[x_] = X.trapezoid([line[y_] for y_ in sorted(line)], sorted(line)) / q_ppm
    check(B, c, "tracer_flux_through_cross_sections_is_of_the_order_of_q", all(0.25 < v < 2.0 for v in ratios.values()), flux_over_q_by_x=ratios, q_ppm_m3_s=q_ppm,
          note="integral of U C over the sampled points (y = -0.18 .. 0.18, z <= 0.07 m, trapezoid, mean flow only) over q = 3.6e-6 m3/s x 1e6: a lower bound, because the plume above z = 0.07 m and the turbulent flux are not sampled and only 3 of 7 lines reach z = 0.07; it fixes the unit and the dilution of C (a ppm / fraction or 5 % error would be x10 or more)")
    unc = sum(1 for sh_ in wb.values() for row_ in sh_ for v_ in row_ if isinstance(v_, str) and ("ncertaint" in v_ or "Ue(" in v_))
    check(B, c, "workbook_carries_no_expanded_uncertainty", unc == 0, warn=True, cells_mentioning_uncertainty=unc, sheets=list(wb), note="only Case J's workbook lists the expanded uncertainty (data paper section 3.10)")
    fit = B.log_law_fit(afl.z, afl.U, 0.02, 0.6)
    inflow = {"U_H_m_s": round(u_at_H, 4), "U_H_stated_m_s": U_H_STATED, "H_m": H, "U_at_z_0.2m_m_s": float(afl[np.isclose(afl.z, 0.2)].U.iloc[0]),
              "turbulence_intensity_at_z_0.2": round(float(afc[np.isclose(afc.z, 0.2)].u_rms.iloc[0]) / float(afl[np.isclose(afl.z, 0.2)].U.iloc[0]), 4),
              "log_law": {**fit, "error_at_H_rel": round(B.log_law_U(fit, H) / u_at_H - 1, 4)}, "power_law": B.power_law_fit(afl.z, afl.U, 0.02, 0.6),
              "method": f"least squares, kappa = {B.KAPPA}, z = 0.02 .. 0.6 m (10 H) on AF_caseK.csv: the profile is Case H's, tabulated for a 0.2 m building, so the window is a choice",
              "note": "the file is the approach flow of Case H (identical rows); the workbook normalises it with uH = U(0.2 m) = 3.23 m/s and H = 0.2 m"}
    frame = {"origin": "bottom centre of the windward wall of the 4th row of the central column: x = 0 is that wall, y = 0 the centre line of the central column", "x": "+x streamwise (the wind blows toward +x); 9 rows, row k spans x in [0.12 (k-4), 0.12 (k-4) + 0.06]",
             "y": "+y lateral; 9 columns, column centres at y = 0, +-0.12, ... +-0.48", "z": "+z up; cube tops at 0.06",
             "length_scale": "model metres (the sources state no model:full scale ratio); cube H = 0.06 m",
             "source": "5 mm diameter floor outlet at (-0.15, 0, 0), 100 % ethylene, 3.6e-6 m3/s; between rows 2 and 3 on the centre line",
             "point_numbers": "RS_caseK.csv publishes none; point_id is the row order of the file"}
    transform = {"coordinate_scale": 1.0, "lateral_sign": 1, "origin_shift_m": [0, 0, 0], "turbulence": "rms squared to variance",
                 "note": "values from the workbook at full precision (x, y, z there in mm); the CSV is these rounded; no sign change"}
    normalisation = {"concentration": {"c0_ppm": round(c0, 6), "definition": "c0 = q / (U_H H^2), q = 3.6e-6 m3/s, U_H = 2.33 m/s, H = 0.06 m (readme and data paper section 3.11)", "workbook_C0_ppm": round(C0_wb, 6),
                                      "workbook_definition": "C0 = q / (UH H^2) with H = 0.2 m and UH = 4.94009 m/s (LF_caseK.xlsx, 'Measurement data' cells R7:R11)", "ratio_c0_over_workbook_C0": round(c0 / C0_wb, 6),
                                      "to_get_the_workbook_ratio": "multiply concentration_ratio by c0 / workbook_C0"},
                     "velocity": {"U_H_m_s": U_H_STATED, "height_m": H, "workbook_UH_m_s": UH_wb, "workbook_H_m": H_wb}}
    extra = {"normalisation": normalisation,
             "known_issues": {"workbook_reference": "LF_caseK.xlsx normalises with H = 0.2 m, UH = 4.94009 m/s and C0 = 18.218 ppm, not the cube's H = 0.06 m and U_H = 2.33 m/s; the table uses the cube's",
                              "no_point_numbers": "RS_caseK.csv has no point-number column; point_id here is the row order",
                              "csv_k": "the CSV's k is recomputed from the rounded rms values; the table carries the workbook's k",
                              "inflow_is_case_H": "AF_caseK.csv is Case H's approach-flow file, measured at x = -0.493 m",
                              "workbook_units": "workbook x, y are millimetres in both data sheets, z is millimetres in 'Measurement data' but metres in 'Inflow'",
                              "usc_not_carried": "the workbook's <usc> and sigma_usc ('Velocity magnitute') are not in the table (QUESTIONS.md QK2)",
                              "lateral_velocity": "V is dominated by a cross-flow offset (about 0.06 m/s); its sign cannot be checked from the data",
                              "data_paper_text": "data paper section 3.11 describes 'approximately 30 points at eight heights downwind of the line source'; Case K has 203 points at five heights and a point source (QUESTIONS.md QK4)"},
             "usc": {"workbook_columns": "E (<usc>, m/s) and F (sigma_usc), sheet 'Measurement data'", "ratio_to_vector_magnitude": "1.03 .. 3.9 (median 1.19) of |U|, never below it; not sqrt(|U|^2 + 2k) either",
                     "note": "a mean scalar speed of the instantaneous velocity, apparently; no column of the schema holds it (Vs is a thermistor speed)"},
             "extra_files": {"approach_flow_full": {"file": "cases/K/approach_flow_full.csv", "columns": list(full.columns), "units": ["m", "m", "m/s", "m/s", "m/s", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "m2/s2"], "rows": len(full), "source": "AF_caseK.csv"}},
             "layout": {"y_values_m": ys, "z_values_m": zs, "rows_per_y": {str(k_): int(v) for k_, v in pts.groupby("y").size().items()}},
             "pitch_scan_points_inside_cubes": {str(k_): v for k_, v in scan.items()},
             "tracer_flux_over_q": {str(k_): round(v, 3) for k_, v in ratios.items()}}
    return pts, afl, geo, X.sig(inflow, 10), frame, transform, X.sig(extra, 10)
