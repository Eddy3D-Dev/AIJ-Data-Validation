"""Case H — wind-tunnel flow and dispersion around a 1:1:2 building with a point source on the floor behind it.

    META   the clean/build.py CASES["H"] entry
    build(B, prov)   B is the clean/build.py module; returns what build_A..build_E return

Source files (raw/cases/case-h/, Zenodo 10.5281/zenodo.15429871): RS_caseH.csv (876 rows: velocity, k and concentration
in m/s, m2/s2 and ppm), AF_caseH.csv (the approach profile), LF_caseH.xlsx (legacy workbook: the same points in
ratios, 905 rows, and the normalisation), MP-y_caseH.png / MP-z_caseH.png (the measurement points).

The table carries the WORKBOOK's values (ratios at full precision x the workbook's uH = 3.226 m/s), not the CSV's:
on two of the four planes the CSV's mean velocities are the workbook ratios rounded to 0.01 before the scaling
(checks below). The CSV decides which points exist and how they are numbered.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

from case_ghi_common import directions_table, number, read_xlsx, sheet_rows

B_W, H_B = 0.10, 0.20                                     # readme: 0.10 m (width, depth), 0.20 m (height)
X0, X1 = -0.10, 0.0                                       # MP-y_caseH.png: the building spans x in [-0.1, 0]; its leeward face is x = 0
SOURCE = (0.05, 0.0, 0.0)                                 # readme: 0.25 H from the leeward wall, on the floor
SHEETS = ["y=0H", "z=0.5H", "z=0.25H", "z=0.0625H"]
BLOCK_END = [(220, "y=0H"), (390, "z=0.5H"), (546, "z=0.25H")]   # which sheet the CSV's point numbers come from, by number
SHEET_COLS = ["n", "x_mm", "y_mm", "z_mm", "xH", "yH", "zH", "u", "v", "w", "urms", "vrms", "wrms", "k", "uref_u", "uref_v", "uref_w", "c", "cC0", "sc", "scC0"]
ROUND_2DP = 0.0051                                        # a value published to 2 dp is within 0.005 of the exact one

META = {
    "title": "Case H — flow and dispersion around a 1:1:2 building (floor point source)", "folder": "raw/cases/case-h",
    "zenodo_concept": "10.5281/zenodo.15429871", "zenodo_version": None,    # the readme names only this record
    "b": B_W, "H": H_B, "U_H_stated": 3.23, "Re_H": 43000, "scale": None,
    "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    "collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Takumi Tachibana (Wind Engineering Institute)"],
    "citation": "Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. https://doi.org/10.1007/978-4-431-55912-2_9",
    "normalisation": ("velocity by U_H = 3.226 m/s (the approach flow at z = H = 0.2 m; 3.23 in the readme and the paper), k by U_H^2; concentration_ratio = C / c0 with "
                      "c0 = cgas q / (U_H H^2) = 1e6 ppm x 5.83e-6 m3/s / (3.226 m/s x 0.2^2 m2) = 45.18 ppm (the workbook; the paper rounds it to 45.2). "
                      "The workbook's reference speed U0 = 5.279 m/s is the free stream, not U_H."),
}

INSTRUMENT_V, INSTRUMENT_C = "split_fibre", "hydrocarbon_analyser"
QUANTITY = {INSTRUMENT_V: ["U", "V", "W"], INSTRUMENT_C: ["C"]}


def flow(cfg, inst, wd):
    return (1.0, 0.0, "measured: U < 0 in the recirculation behind the leeward face and W < 0 down the windward face (checks WD0_*); the point source sits behind the building",
            "settled")


def directions(B, pts):
    return directions_table("H", pts, QUANTITY, flow)


def _sheet(cells):
    rr = [v[:21] for r, v in sheet_rows(cells, first=2, ncols=21) if isinstance(v[0], float)]
    return pd.DataFrame([[number(x) for x in v] for v in rr], columns=SHEET_COLS)


def _block(no):
    return next((s for end, s in BLOCK_END if no <= end), "z=0.0625H")


def build(B, prov):
    c = "H"
    folder = os.path.join(B.REPO, META["folder"])
    rs, af, lf = (os.path.join(folder, n) for n in ("RS_caseH.csv", "AF_caseH.csv", "LF_caseH.xlsx"))
    prov[c] = [rs, af, lf, os.path.join(folder, "readme_caseH.md"), os.path.join(folder, "MP-y_caseH.png"), os.path.join(folder, "MP-z_caseH.png")]

    header, rows = B.read_csv_rows(rs)
    B.log(f"[H] RS_caseH.csv header (bare): {header}; the published header misspells w_rms as 'w_rsm'; unmeasured = -999.9 (50 rows of velocity and 50 of concentration)")
    ix = {h: i for i, h in enumerate(header)}
    g = lambda r, n: B.num(r[ix[n]])  # noqa: E731
    csv = pd.DataFrame([{"No": int(g(r, "No.")), "x": g(r, "x"), "y": g(r, "y"), "z": g(r, "z"), "U": g(r, "U"), "V": g(r, "V"), "W": g(r, "W"),
                         "u_rms": g(r, "u_rms"), "v_rms": g(r, "v_rms"), "w_rms": g(r, "w_rsm"), "k": g(r, "k"), "c": g(r, "<c>"), "c_rms": g(r, "c_rms")} for r in rows])

    # ---- the workbook
    wb = read_xlsx(lf)
    par = {str(v[1]).strip(): v for _, v in sheet_rows(wb["Parameter for normalization"])}
    uH, U0, q_m3s, cgas, c0 = (number(par[k][3]) for k in ("uH", "U0", "q", "cgas", "c0"))
    sit = {str(v[1]).strip(): v[2] for _, v in sheet_rows(wb["Measurement situation"])}
    flow_cc = number(sit["Gas flow rate[cc/min]"])
    d_mm = number(sit["Gas exit diameter[mm]"])
    B.log(f"[H] workbook normalisation: U0 = {U0} m/s (free stream), uH = {uH} m/s, q = {q_m3s} m3/s ({flow_cc} cc/min), cgas = {cgas:.0f} ppm, c0 = {c0} ppm; gas exit {d_mm} mm")
    wpts = []
    for sname in SHEETS:
        d = _sheet(wb[sname])
        d["sheet"] = sname
        wpts.append(d)
    W = pd.concat(wpts, ignore_index=True)
    # two labelling slips in the workbook that the CSV does not share
    relabel = (W.sheet == "z=0.0625H") & (W.x_mm == 400.0) & W.u.isna() & W.c.notna()      # concentration-only rows labelled x = 400 (every other plane: 380)
    W.loc[relabel, "x_mm"] = 380.0
    z13 = (W.z_mm == 13.0)                                                                      # 12.5 mm typed as 13 in the y = 0 plane at x = 380 / 400
    W.loc[z13, "z_mm"] = 12.5
    W["key"] = list(zip(W.x_mm.round(1), W.y_mm.round(1), W.z_mm.round(1)))
    B.log(f"[H] workbook {len(W)} rows in 4 sheets (y=0H {int((W.sheet == 'y=0H').sum())}, z=0.5H {int((W.sheet == 'z=0.5H').sum())}, z=0.25H {int((W.sheet == 'z=0.25H').sum())}, "
          f"z=0.0625H {int((W.sheet == 'z=0.0625H').sum())}); {int(relabel.sum())} concentration-only rows of the z=0.0625H sheet are labelled x = 400 mm and are read as x = 380 mm "
          f"(the CSV's x; every other plane puts the concentration line at 380 and the velocity line at 400); {int(z13.sum())} rows carry z = 13 mm for 12.5 mm")
    by_key = {}
    for i, k in enumerate(W.key):
        by_key.setdefault(k, []).append(i)

    # ---- map every CSV row to one workbook row
    used, pick = {}, []
    for r in csv.itertuples():
        cand = by_key.get((round(r.x * 1000, 1), round(r.y * 1000, 1), round(r.z * 1000, 1)), [])
        cand = [i for i in cand if i not in used]
        want = _block(r.No)
        best = next((i for i in cand if W.sheet[i] == want), cand[0] if cand else None)
        if best is not None:
            used[best] = r.No
        pick.append(best)
    csv["wb"] = pick
    matched = csv.wb.notna()
    M = W.loc[csv.wb[matched].astype(int)].reset_index(drop=True)
    C = csv[matched].reset_index(drop=True)
    dropped = W.loc[[i for i in W.index if i not in used]]
    B.log(f"[H] mapped {int(matched.sum())} of {len(csv)} CSV rows to workbook rows by coordinates; {len(dropped)} workbook rows have no CSV row (checked below: exact copies of mapped rows)")

    # ---- values released: workbook ratios x uH (variances = (rms x uH)^2, k x uH^2); concentration as published in ppm
    out = []
    for r, m in zip(C.itertuples(), M.itertuples()):
        if not math.isnan(m.u):
            sign = -1.0 if m.sheet == "y=0H" else 1.0      # the vertical-plane sheet's V is positive toward -y (checks vertical_plane_V_*)
            out.append(B.row(case_id=c, instrument=INSTRUMENT_V, point_id=r.No, x=r.x, y=r.y, z=r.z, U=m.u * uH, V=sign * m.v * uH, W=m.w * uH,
                             uu=(m.urms * uH) ** 2, vv=(m.vrms * uH) ** 2, ww=(m.wrms * uH) ** 2, k=m.k * uH ** 2))
        if not math.isnan(m.c):
            out.append(B.row(case_id=c, instrument=INSTRUMENT_C, point_id=r.No, x=r.x, y=r.y, z=r.z, C=m.c, c_rms=m.sc, concentration_ratio=m.c / c0))
    B.log("[H] transform: one row per (instrument, point): split_fibre rows carry U V W uu vv ww k, hydrocarbon_analyser rows carry C c_rms concentration_ratio; the CSV's "
          "-999.9 and the workbook's blanks mean the instrument was not run on that line, and such rows are omitted; point_id = the CSV's No.; values = workbook x uH; V of the vertical-plane sheet (point numbers 1-220) is multiplied by -1 (checks vertical_plane_V_*)")
    pts = pd.DataFrame(out, columns=B.POINT_COLUMNS)

    # ---- approach flow (the workbook's 'inflow' sheet; the CSV carries it rounded)
    ih = [v for r, v in sheet_rows(wb["inflow"], first=2, ncols=20) if isinstance(v[0], float)]
    inf = pd.DataFrame([[number(x) for x in v] for v in ih], columns=["n", "x_mm", "y_mm", "z_mm", "xH", "yH", "zH", "u", "v", "w", "urms", "vrms", "wrms", "urms_v", "urms_w", "wrms_u", "uw", "uv", "uw_w", "k"])
    afl = pd.DataFrame([{"case_id": c, "z": r.z_mm, "U": r.u * uH, "uu": (r.urms * uH) ** 2, "vv": (r.vrms * uH) ** 2, "ww": (r.wrms * uH) ** 2, "k": r.k * uH ** 2} for r in inf.itertuples()])
    z_unit_gap = float(np.max(np.abs(inf.z_mm.to_numpy() - inf.zH.to_numpy() * H_B)))
    B.log(f"[H] approach flow: the workbook's 'inflow' sheet, {len(afl)} heights at x = {inf.x_mm.iloc[0] / 1000} m, y = 0, ratios x uH; the sheet's column headed 'z(mm)' is in METRES (z/H x H reproduces it to {z_unit_gap:.0e}), x is in mm; AF_caseH.csv is the same rounded. The approach-flow "
          "table has no column for the profile's uw and uv, which are therefore not carried")
    ah, ar = B.read_csv_rows(af)
    aix = {n: i for i, n in enumerate(ah)}

    boxes = [{"min": [X0, -B_W / 2, 0.0], "max": [X1, B_W / 2, H_B]}]
    geo = [("default", boxes, "generated from the readme's stated dimensions 0.10 x 0.10 x 0.20 m (width, depth, height); x in [-0.1, 0], y in [-0.05, 0.05], leeward face at x = 0 (MP-y_caseH.png, MP-z_caseH.png). "
            "The floor source (4 mm hole at x = 0.05 m, y = 0) is not part of the body")]

    # ---- checks: the published tables
    V, Cc = pts[pts.instrument == INSTRUMENT_V], pts[pts.instrument == INSTRUMENT_C]
    B.check(c, "csv_876_rows_numbered_1_to_876", len(csv) == 876 and sorted(csv.No) == list(range(1, 877)), rows=len(csv))
    B.check(c, "every_csv_row_maps_to_one_workbook_row", int(matched.sum()) == 876 and len(set(used)) == 876, mapped=int(matched.sum()), workbook_rows=len(W))
    dx = float(np.max(np.abs(C.x.to_numpy() * 1000 - M.x_mm.to_numpy()))), float(np.max(np.abs(C.y.to_numpy() * 1000 - M.y_mm.to_numpy()))), float(np.max(np.abs(C.z.to_numpy() * 1000 - M.z_mm.to_numpy())))
    B.check(c, "csv_coordinates_equal_the_workbooks_in_mm", max(dx) < 1e-6, max_abs_diff_mm_xyz=list(dx), note="after the two workbook slips above: x = 400 -> 380 (18 + 1 concentration-only rows), z = 13 -> 12.5")
    def twin_gap(d):
        gaps = []
        for t in M[M.key == d.key].itertuples():
            same = max(0.0 if (math.isnan(getattr(d, q)) and math.isnan(getattr(t, q))) else abs(getattr(d, q) - getattr(t, q)) for q in ("u", "w", "urms", "vrms", "wrms", "k", "c"))
            sv = -1.0 if t.sheet != d.sheet and "y=0H" in (t.sheet, d.sheet) else 1.0
            gaps.append(max(same, abs(d.v - sv * t.v)))
        return min(gaps) if gaps else math.inf
    cp = [twin_gap(d) for d in dropped.itertuples()]
    B.check(c, "workbook_rows_without_a_csv_row_are_exact_copies_of_csv_rows", max(cp) < 1e-9 and len(dropped) == 29, dropped=len(dropped), max_abs_diff_to_the_kept_row=float(max(cp)),
            by_sheet={s: int((dropped.sheet == s).sum()) for s in SHEETS},
            note="the y = 0 centre-line points appear in the y=0H sheet and again in each horizontal-plane sheet, identical in every quantity except V, whose sign is opposite (next check); the CSV keeps the repeat only on the z=0.5H plane")
    vel_missing = csv[csv.U.isna()]
    c_missing = csv[csv.c.isna()]
    B.check(c, "unmeasured_rows_are_two_whole_lines_not_the_building_interior", len(vel_missing) == 50 and set(vel_missing.x) == {0.38} and len(c_missing) == 50 and set(c_missing.x) == {0.4}
            and bool((M.u.isna().to_numpy() == csv[matched].U.isna().to_numpy()).all()) and bool((M.c.isna().to_numpy() == csv[matched].c.isna().to_numpy()).all()),
            velocity_unmeasured=len(vel_missing), at_x_velocity_unmeasured=sorted(set(vel_missing.x)), concentration_unmeasured=len(c_missing), at_x_concentration_unmeasured=sorted(set(c_missing.x)),
            note="the concentration line is x = 0.38 m (no velocity) and the velocity line x = 0.40 m (no concentration): two probes on adjacent lines. -999.9 is therefore not 'inside the building'")
    # V on the y = 0 line: the vertical-plane sheet against the horizontal-plane sheets
    y0 = W[(W.y_mm == 0) & W.v.notna()]
    vert = {(r.x_mm, r.z_mm): r.v for r in y0[y0.sheet == "y=0H"].itertuples()}
    pairs_v = [(vert[(r.x_mm, r.z_mm)], r.v, r.sheet, r.x_mm, r.z_mm) for r in y0[y0.sheet != "y=0H"].itertuples() if (r.x_mm, r.z_mm) in vert]
    sum_gap = max(abs(a + b) for a, b, *_ in pairs_v)
    diff_gap = max(abs(a - b) for a, b, *_ in pairs_v)
    big = [(a, b) for a, b, *_ in pairs_v if abs(a) > 0.05]
    nb = []
    for sname in ("z=0.5H", "z=0.25H", "z=0.0625H"):
        s_ = W[(W.sheet == sname) & W.v.notna()]
        for (xm, zm), gg in s_.groupby(["x_mm", "z_mm"]):
            a0, p25, m25 = gg[gg.y_mm == 0].v, gg[gg.y_mm == 25.0].v, gg[gg.y_mm == -25.0].v
            if len(a0) and len(p25) and len(m25) and (xm, zm) in vert:
                nb.append((float(a0.iloc[0]), vert[(xm, zm)], 0.5 * float(p25.iloc[0] + m25.iloc[0])))
    r_hp = float(np.corrcoef([t[0] for t in nb], [t[2] for t in nb])[0, 1])
    r_vp = float(np.corrcoef([t[1] for t in nb], [t[2] for t in nb])[0, 1])
    B.check(c, "vertical_plane_V_is_the_exact_negative_of_the_horizontal_planes_V_at_the_shared_points", len(pairs_v) >= 38 and sum_gap < 1e-12 and diff_gap > 0.1,
            shared_points=len(pairs_v), max_abs_v_sum=sum_gap, max_abs_v_difference=diff_gap, largest_pair=[round(max(big, key=lambda t: abs(t[0]))[0], 4), round(max(big, key=lambda t: abs(t[0]))[1], 4)] if big else None,
            note="y = 0 points shared by the y=0H sheet and a horizontal-plane sheet agree in U, W, k and C to the last digit and carry V of opposite sign (e.g. 0.00206 against -0.00206). Not noise: a sign convention")
    B.check(c, "horizontal_planes_V_is_continuous_with_its_neighbours_so_the_vertical_plane_V_is_the_flipped_one", r_hp > 0.5 and r_vp < -0.5, corr_horizontal_y0_vs_mean_of_y_pm_25mm=r_hp, corr_vertical_y0_vs_the_same=r_vp, points=len(nb),
            note="at the shared points, V at y = 0 against the mean of V at y = +/-25 mm of the same horizontal plane: positive for the horizontal sheets, negative for the vertical one. With the lateral-sign check below (horizontal planes: V has the sign of y upwind) the horizontal convention is the one released")
    # CSV vs workbook, per sheet
    def maxdiff(q, wq, p, sheets):
        sel = (M.sheet.isin(sheets) & M[wq].notna()).to_numpy() & C[q].notna().to_numpy()
        return float(np.max(np.abs(C[q][sel].to_numpy() - M[wq][sel].to_numpy() * uH ** p)))
    full = ["y=0H", "z=0.0625H"]
    coarse = ["z=0.5H", "z=0.25H"]
    uvw_full = max(maxdiff(q, w, 1, full) for q, w in (("U", "u"), ("V", "v"), ("W", "w")))
    uvw_coarse = max(maxdiff(q, w, 1, coarse) for q, w in (("U", "u"), ("V", "v"), ("W", "w")))
    sel_f = [((M.sheet.isin(full) & M[w].notna()).to_numpy() & C[q].notna().to_numpy(), q, w) for q, w in (("U", "u"), ("V", "v"), ("W", "w"))]
    uH_implied = float(sum((C[q][m_].to_numpy() * M[w][m_].to_numpy()).sum() for m_, q, w in sel_f) / sum((M[w][m_].to_numpy() ** 2).sum() for m_, q, w in sel_f))
    B.check(c, "csv_velocity_is_workbook_ratio_x_uH_to_2dp_on_the_y0_and_z_0.0625H_planes", uvw_full <= ROUND_2DP + 0.0005, max_abs_diff_m_s=uvw_full, planes=full, uH=uH, uH_implied_by_the_csv=uH_implied,
            note="2 dp rounding (0.005) plus the CSV having been scaled with 3.2257 rather than 3.226 (up to 0.0005 at 4.4 m/s). V compared in the workbook's own sign: the CSV carries the same V as the workbook")
    unrounded_misses, rounded_max = 0, 0.0
    for q, w in (("U", "u"), ("V", "v"), ("W", "w")):
        sel = (M.sheet.isin(coarse) & M[w].notna()).to_numpy() & C[q].notna().to_numpy()
        cq, mq = C[q][sel].to_numpy(), M[w][sel].to_numpy()
        unrounded_misses += int((np.abs(cq - mq * uH) > ROUND_2DP).sum())
        rounded_max = max(rounded_max, float(np.max(np.abs(cq - np.round(mq, 2) * uH))))
    B.check(c, "csv_velocity_on_the_z_0.5H_and_z_0.25H_planes_is_the_ratio_rounded_to_0.01_then_scaled", rounded_max <= ROUND_2DP and uvw_coarse > ROUND_2DP and unrounded_misses > 100,
            max_abs_diff_to_rounded_ratio_m_s=rounded_max, max_abs_diff_to_full_precision_m_s=uvw_coarse, values_beyond_2dp_rounding_of_the_full_precision=unrounded_misses, quantum_m_s=0.01 * uH, planes=coarse,
            note="the CSV's U, V, W on these two planes sit on a 0.0323 m/s grid (+/-0.016 m/s, up to 15 % of a 0.1 m/s value); the workbook is released instead")
    rms_d = max(maxdiff(q, w, 1, SHEETS) for q, w in (("u_rms", "urms"), ("v_rms", "vrms"), ("w_rms", "wrms")))
    k_d = maxdiff("k", "k", 2, SHEETS)
    B.check(c, "csv_rms_and_k_agree_with_the_workbook_to_their_rounding", rms_d <= 0.0025 and k_d <= 0.006, max_abs_diff_rms_m_s=rms_d, max_abs_diff_k_m2_s2=k_d,
            note="on the two coarse planes the workbook's rms/uH and k/uH^2 were rounded to 3 dp before the scaling (+/-0.0016 m/s, +/-0.005 m2/s2)")
    sel_c = C.c.notna().to_numpy()
    c_d = float(np.max(np.abs(C.c[sel_c].to_numpy() - M.c[sel_c].to_numpy())))
    s_d = float(np.max(np.abs(C.c_rms[sel_c].to_numpy() - M.sc[sel_c].to_numpy())))
    B.check(c, "csv_concentration_agrees_with_the_workbook_to_3dp", c_d <= 5.0e-4 + 1e-9 and s_d <= 5.0e-4 + 1e-9, rows=int(sel_c.sum()), max_abs_diff_c_ppm=c_d, max_abs_diff_c_rms_ppm=s_d)
    kerr = float(np.max(np.abs(V.k - 0.5 * (V.uu + V.vv + V.ww))))
    B.check(c, "k_equals_half_sum_of_variances", kerr < 1e-3, max_abs_error=kerr, rows=len(V), note="the workbook's k/uH^2 against its own rms/uH, to the workbook's rounding (5 dp in the ratios)")
    B.check(c, "no_nan_in_the_released_rows", not V[["x", "y", "z", "U", "V", "W", "uu", "vv", "ww", "k"]].isna().any().any() and not Cc[["x", "y", "z", "C", "c_rms", "concentration_ratio"]].isna().any().any(),
            velocity_rows=len(V), concentration_rows=len(Cc))
    B.check(c, "826_velocity_rows_and_826_concentration_rows", len(V) == 826 and len(Cc) == 826, velocity_rows=len(V), concentration_rows=len(Cc), note="876 points, 50 without velocity, 50 without concentration")

    # ---- normalisation: the workbook against the readme, the paper and itself
    c0_calc = cgas * q_m3s / (uH * H_B ** 2)
    B.check(c, "c0_is_cgas_q_over_uH_H2", abs(c0_calc / c0 - 1) < 1e-6 and abs(c0 / 45.2 - 1) < 2e-3, c0_workbook_ppm=c0, c0_recomputed_ppm=c0_calc, c0_paper_ppm=45.2, uH=uH, q_m3_s=q_m3s, H_m=H_B,
            note="the paper (section 3.8) states 45.2 ppm; the workbook's formula with its own uH gives 45.18")
    B.check(c, "release_rate_350_cc_per_min_is_5.83e-6_m3_s", abs(flow_cc / 6e7 / q_m3s - 1) < 1e-3, workbook_cc_per_min=flow_cc, m3_s_from_it=flow_cc / 6e7, readme_m3_s=5.83e-6)
    wc = W[W.c.notna()]
    c0_col = float((wc.c / wc.cC0).median())
    c0_spread = float((wc.c / wc.cC0).max() - (wc.c / wc.cC0).min())
    B.check(c, "workbook_C_over_c0_column_uses_one_c0_within_1e-4_of_the_stated_45.18", c0_spread < 1e-9 and abs(c0_col / c0 - 1) < 1e-4, c0_implied_by_the_column=c0_col, c0_parameter_sheet=c0, relative_difference=c0_col / c0 - 1,
            note="the column <c>/Co divides by 45.17727 (uH = 3.22618) while the parameter sheet says 45.17979; released here with the parameter sheet's value")
    AF = pd.DataFrame([{n: B.num(r[aix[n]]) for n in ah} for r in ar])
    afU_r = float(np.max(np.abs(AF["U"].to_numpy() - np.round(inf.u.to_numpy(), 2) * uH)))
    afU_f = float(np.max(np.abs(AF["U"].to_numpy() - afl.U.to_numpy())))
    afr = float(np.max(np.abs(AF["u_rms"].to_numpy() - np.sqrt(afl.uu.to_numpy()))))
    afk = float(np.max(np.abs(AF["k"].to_numpy() - afl.k.to_numpy())))
    B.check(c, "approach_flow_csv_is_the_workbook_profile_with_U_rounded_to_0.01_before_the_scaling", len(AF) == len(afl) == 17 and float(np.max(np.abs(AF["z"].to_numpy() - afl.z.to_numpy()))) < 1e-9
            and afU_r <= ROUND_2DP and afr <= 0.0025 and afk <= 0.006, rows=len(AF), max_abs_diff_U_to_rounded_ratio=afU_r, max_abs_diff_U_to_full_precision=afU_f, max_abs_diff_urms=afr, max_abs_diff_k=afk,
            note="like the z = 0.5H and 0.25H planes, the CSV's U is round(u/uH, 2) x uH (a 0.032 m/s grid); the workbook is released")
    B.check(c, "inflow_sheet_z_column_headed_mm_is_in_metres", z_unit_gap < 1e-9, max_abs_diff_m=z_unit_gap, note="z/H x H = the column's value, so it is metres although the header says mm; x(mm) in the same sheet is millimetres")
    UH_prof = B.interp_log(afl.z, afl.U, H_B)
    B.check(c, "U_H_from_the_profile_is_the_workbook_uH_and_the_stated_3.23", abs(UH_prof - uH) < 1e-9 and abs(float(AF["U"][np.isclose(AF["z"], H_B)].iloc[0]) - 3.23) < 1e-9 and abs(uH - 3.23) < 0.005,
            U_H_workbook=uH, U_H_profile=UH_prof, U_H_csv=float(AF["U"][np.isclose(AF["z"], H_B)].iloc[0]), U_H_stated=3.23, uH_over_U0=uH / U0)

    # ---- geometry and frame
    xyz = pts.drop_duplicates(["instrument", "point_id"])[["x", "y", "z"]].to_numpy()
    n_in = int(B.points_in_boxes(xyz, boxes).sum())
    B.check(c, "no_sensor_inside_building", n_in == 0, inside=n_in, points=len(xyz), note="no point lies inside the body; points ON the roof plane z = H: none")
    ctrl = B.points_in_boxes(xyz + np.array([0.05, 0.0, 0.0]), boxes)
    B.check(c, "control_points_shifted_0.05m_downwind_are_detected_inside", int(ctrl.sum()) > 5, inside_after_shift=int(ctrl.sum()), shift_m=[0.05, 0, 0])
    bb = [pts.x.min(), pts.x.max(), pts.y.min(), pts.y.max(), pts.z.min(), pts.z.max()]
    B.check(c, "extents_sane", bb[0] >= -0.2 - 1e-9 and bb[1] <= 0.4 + 1e-9 and abs(bb[2]) <= 0.2 + 1e-9 and bb[3] <= 0.2 + 1e-9 and bb[4] > 0 and bb[5] <= 0.3 + 1e-9, bbox=bb, note="MP-y_caseH.png: x -0.2 .. 0.4, z 0.01 .. 0.3; MP-z_caseH.png: y -0.2 .. 0.2")
    cmax = Cc.loc[Cc.C.idxmax()]
    B.check(c, "concentration_peak_sits_at_the_source_x_0.05_0.25H_behind_the_leeward_face", abs(cmax.x - SOURCE[0]) < 1e-9 and abs(cmax.y) < 1e-9 and abs(cmax.z - 0.01) < 1e-9,
            peak_ppm=float(cmax.C), at=[float(cmax.x), float(cmax.y), float(cmax.z)], peak_over_c0=float(cmax.C / c0),
            note="the lowest point above the hole; the frame (leeward face at x = 0) and the readme's 0.25 H are consistent")
    behind = V[(V.y == 0) & (V.z <= 0.1) & (V.x > 0) & (V.x <= 0.075)]
    B.check(c, "WD0_flow_reverses_behind_the_leeward_face", bool((behind.U < 0).all()) and len(behind) >= 20, points=len(behind), mean_U_m_s=float(behind.U.mean()),
            note="y = 0, z <= 0.1, 0 < x <= 0.075: U < 0 at every point (the wake's recirculation), so the wind blows toward +x and the leeward face is x = 0")
    down = V[(V.y == 0) & (V.x.between(-0.125, -0.11 + 1e-9)) & (V.z.between(0.05, 0.1 + 1e-9))]
    B.check(c, "WD0_downwash_on_the_windward_face", bool((down.W < 0).all()) and len(down) >= 4, points=len(down), mean_W_m_s=float(down.W.mean()), note="x = -0.125 and -0.11 m (just upwind of the windward face), z = 0.05 and 0.1 m: W < 0, the stagnation flow runs down; at z = 0.15 m (0.75 H) it turns up (W = +0.10, +0.04)")
    up_side = V[(V.x <= -0.15 + 1e-9) & (V.z == 0.0125) & (V.y.abs() >= 0.1 - 1e-9)]
    B.check(c, "lateral_sign_V_positive_toward_plus_y", bool((np.sign(up_side.V) == np.sign(up_side.y)).all()) and len(up_side) >= 8, points=len(up_side), sign_agreement=float((np.sign(up_side.V) == np.sign(up_side.y)).mean()),
            note="upwind of the building at z = 0.0125 m, |y| >= 0.1: the flow diverges around it, so V has the sign of y; same convention as Cases A, B, D")
    # the 14 repeated locations
    dup = V[V.duplicated(["x", "y", "z"], keep=False)].sort_values(["x", "z", "point_id"])
    pairs = [(gg.U.to_numpy(), gg.V.to_numpy(), gg.W.to_numpy(), gg.k.to_numpy()) for _, gg in dup.groupby(["x", "y", "z"])]
    dc = Cc[Cc.duplicated(["x", "y", "z"], keep=False)]
    cgaps = [abs(g2.C.iloc[0] - g2.C.iloc[1]) for _, g2 in dc.groupby(["x", "y", "z"])]
    vgap = max(float(np.max(np.abs(p[i][0] - p[i][1]))) for p in pairs for i in range(4))
    B.check(c, "the_y0_z0.5H_line_appears_twice_as_exact_copies_once_V_is_flipped", len(pairs) == 13 and all(len(p[0]) == 2 for p in pairs) and len(dc) == 26 and vgap < 1e-12 and max(cgaps) < 1e-12,
            velocity_locations=len(pairs), concentration_locations=len(dc) // 2, max_abs_gap_UVWk=vgap, max_abs_gap_C_ppm=float(max(cgaps)),
            point_ids=[[int(i) for i in gg.point_id] for _, gg in dup.groupby(["x", "y", "z"])][:3],
            note="the y = 0, z = 0.1 line is in the y=0H sheet and again in the z=0.5H sheet (14 x locations; x = 0.38 has no velocity, x = 0.40 no concentration): the rows are one record twice, not two measurements, so they give no repeatability. Both rows are kept under their own point numbers (the CSV's), which double-counts 13 + 13 values")
    z16 = V[np.isclose(V.z, 0.0125)]
    mir = {(round(a, 4), round(b, 4)): u for a, b, u in z16[["x", "y", "U"]].to_numpy()}
    d = [abs(u - mir[(a, round(-b, 4))]) for (a, b), u in mir.items() if b > 0 and (a, round(-b, 4)) in mir]
    B.check(c, "z_0.0625H_plane_y_mirror_pairs_give_the_repeatability_of_U", len(d) >= 100, pairs=len(d), mean_abs_dU_m_s=float(np.mean(d)), mean_abs_dU_over_UH=float(np.mean(d) / uH),
            note="the building is y-symmetric, so U(x, y) and U(x, -y) are two measurements of one value")
    # plume flux through the farthest concentration plane, separable approximation
    lat = Cc[(Cc.x == 0.38) & np.isclose(Cc.z, 0.0125)].groupby("y").C.mean()
    ver = Cc[(Cc.x == 0.38) & (Cc.y == 0)].groupby("z").C.mean()
    vel = V[(V.x == 0.4) & (V.y == 0)].groupby("z").U.mean()
    gy = np.trapezoid(lat.values, lat.index.values) / lat.loc[0.0]
    fz = np.trapezoid(ver.values * np.interp(ver.index.values, vel.index.values, vel.values), ver.index.values)
    flux = float(fz * gy)
    q_ppm = cgas * q_m3s
    B.check(c, "tracer_flux_through_x_0.38_is_0.6_to_1.3_of_the_release", 0.6 < flux / q_ppm < 1.3, flux_over_release=flux / q_ppm, flux_ppm_m3_s=flux, release_ppm_m3_s=q_ppm,
            lateral_integral_limits_m=[float(lat.index.min()), float(lat.index.max())], c_at_lateral_edge_over_centre=float(lat.iloc[0] / lat.loc[0.0]),
            method="separable: C(y, z) = C(0, z) x C(y, 0.0125)/C(0, 0.0125); U(z) from the velocity line x = 0.4 at y = 0; trapezoid from the lowest point up to z = 0.3 m",
            note="an INDEPENDENT test of q against the concentrations; the lateral line stops at |y| = 0.2 m where C is still 32 % of the centreline value, so a deficit is expected")
    # baseline
    up = Cc[Cc.x < -0.1]
    B.check(c, "upwind_concentration_is_the_analyser_offset_not_tracer", float(up.C.abs().median()) < 0.2 and float(up.C.max()) < 1.0, upwind_points=len(up), median_abs_ppm=float(up.C.abs().median()),
            mean_ppm=float(up.C.mean()), min_ppm=float(Cc.C.min()), negative_values=int((Cc.C < 0).sum()), peak_ppm=float(Cc.C.max()),
            note="the source is behind the building, so upwind C is zero in truth; the analyser reads +/-0.1 ppm and 97 of 826 values are negative. Log-based statistics (MG, VG) need a floor")

    # ---- approach-flow fits
    fit1 = B.log_law_fit(afl.z, afl.U, 0.02, 2 * H_B)
    fit1["error_at_H_rel"] = round(B.log_law_U(fit1, H_B) / UH_prof - 1, 4)
    pl = B.power_law_fit(afl.z, afl.U, 0.02, 2 * H_B)
    ti = float(np.sqrt(afl[np.isclose(afl.z, H_B)].uu.iloc[0]) / UH_prof)
    inflow = {"U_H_m_s": round(uH, 6), "U_H_stated_m_s": 3.23, "H_m": H_B, "U0_free_stream_m_s": U0, "uH_over_U0": round(uH / U0, 6), "profile_x_m": inf.x_mm.iloc[0] / 1000,
              "turbulence_intensity_at_H": round(ti, 4), "log_law": fit1, "power_law": pl,
              "method": f"least squares, kappa = {B.KAPPA}, z = 0.02 .. 2H on the workbook's 17-point inflow profile",
              "c0_ppm": c0, "c0_paper_ppm": 45.2, "note": "the approach-flow table's uu, vv, ww are (rms x uH)^2; the profile's uw and uv are in the workbook and the CSV but have no column in the approach-flow table"}
    frame = {"origin": "the centre of the building's leeward face on the ground plane (MP-y_caseH.png, MP-z_caseH.png)",
             "x": "+x streamwise (the wind blows toward +x): the building occupies x in [-0.1, 0]; points at x = -0.2 .. 0.4 m",
             "y": "+y lateral; the building spans y in [-0.05, 0.05]; the z = 0.0625H plane covers y in [-0.2, 0.2], the others y in [0, 0.2] and the y = 0 line",
             "z": "+z up; roof at z = 0.2 m; points at z = 0.01 .. 0.3 m", "source": "the 4 mm floor hole at (0.05, 0, 0), i.e. 0.25 H behind the leeward face",
             "length_scale": "model metres (the source states no model:full scale ratio; Eddy3D solves it at 1:100)"}
    transform = {"coordinate_scale": 1.0, "lateral_sign": "-1 for point numbers 1-220 (the vertical-plane sheet), +1 elsewhere", "origin_shift_m": [0, 0, 0], "uH_m_s": uH, "c0_ppm": c0,
                 "note": "U, V, W, rms and k = the workbook's ratios x uH (uH^2 for k), V of point numbers 1-220 multiplied by -1; variances = (rms x uH)^2; concentration as published; one row per instrument; the x = 400 mm label of 18 concentration-only rows is read as 380 mm"}
    src = {"x_m": SOURCE[0], "y_m": 0.0, "z_m": 0.0, "diameter_mm": d_mm, "gas": "ethylene (C2H4), 100 %", "flow_cc_per_min": flow_cc, "flow_m3_s": q_m3s, "position": "0.25 H from the leeward wall, on the floor"}
    known = {"w_rms_header_typo": "w_rsm", "csv_quantised_planes": coarse, "unmeasured_lines": {"velocity": 0.38, "concentration": 0.40},
             "negative_concentrations": int((Cc.C < 0).sum()), "duplicated_locations": {"velocity": len(pairs), "concentration": len(dc) // 2},
             "V_sign_flipped_for_point_numbers": [1, 220]}
    return pts, afl, geo, inflow, frame, transform, {"known_issues": known, "source": src, "plume_flux_over_release_x_0.38": round(flux / q_ppm, 4)}
