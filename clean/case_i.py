"""Case I — wind-tunnel flow and dispersion around a cube with a point source at the centre of its roof.

    META   the clean/build.py CASES["I"] entry
    build(B, prov)   B is the clean/build.py module; returns what build_A..build_E return

Source files (raw/cases/case-i/, Zenodo 10.5281/zenodo.15430018): RS-w_caseI.csv (91 laser-Doppler points: U V W k),
RS-c_caseI.csv (539 concentration points: C), AF_caseI.csv, LF_caseI.xlsx (legacy workbook), four MP-*.png drawings.

The two point files are two different point sets (wind: y = 0 plane and z = 0.5 H plane; concentration: y = 0 plane and
the ground plane) with no point numbers. They are merged by STACKING, one row per (instrument, point), exactly as Case D
stacks its thermistor and split-fibre points: the wind rows come first, numbered 1-91 in the file's order, the
concentration rows next, numbered 92-630 in the file's order, so a point_id names one location. 17 locations carry both
a wind and a concentration value; they stay two rows (two instruments). The table carries the WORKBOOK's values
(9 significant digits; the CSVs round to 3 dp / 1 dp).
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

from case_ghi_common import directions_table, number, read_xlsx, sheet_rows

SIDE, H_CUBE = 0.10, 0.10                                  # readme: a cube of 0.1 m per side (= H)
SOURCE = (0.0, 0.0, H_CUBE)                                # readme: circular outlet at the centre of the roof
D_OUT_MM, GAS_CC_MIN, GAS_FRACTION, M_STATED = 6.0, 400.0, 0.10, 0.14
UH_STATED = 1.7
ROUND_3DP = 5.0e-4 + 1e-9

META = {
    "title": "Case I — flow and dispersion around a cube (roof point source)", "folder": "raw/cases/case-i",
    "zenodo_concept": "10.5281/zenodo.15430018", "zenodo_version": None,        # the readme names only this record
    "b": SIDE, "H": H_CUBE, "U_H_stated": UH_STATED, "Re_H": 11000, "scale": None,
    "contact": "Yoshihide Tominaga <tominaga@abe.niit.ac.jp>",
    "collectors": ["Hiroaki Kondo (National Institute of Advanced Industrial Science and Technology)", "Katsuhiko Mutou (National Institute of Advanced Industrial Science and Technology)",
                   "Akihiro Hori (National Institute for Environmental Studies)"],
    "citation": "Japan Society for Atmospheric Environment (2013). Guidelines for Atmospheric Environment Assessment Methods Using CFD Models (DiMCFD). Japan Society for Atmospheric Environment (in Japanese).",
    "normalisation": ("velocity by U_H = 1.7 m/s (the readme; the approach flow at z = H = 0.1 m is 1.697 m/s), concentration_ratio = C / c0 with c0 = 39.2235 ppm (the workbook; "
                      "the paper rounds it to 39.2) = q / (U_H H^2) for q = the ETHANE flow, 10 % of the 400 cc/min released (6.67e-7 m3/s), not the 6.67e-6 m3/s the paper quotes for the mixture."),
}

INSTRUMENT_W, INSTRUMENT_C = "ldv", "hydrocarbon_analyzer"
QUANTITY = {INSTRUMENT_W: ["U", "V", "W"], INSTRUMENT_C: ["C"]}


def flow(cfg, inst, wd):
    return (1.0, 0.0, "measured: U < 0 in the recirculation behind the cube's leeward face and U, W > 0 over the roof (checks WD0_*); the source is on the roof", "settled")


def directions(B, pts):
    return directions_table("I", pts, QUANTITY, flow)


def build(B, prov):
    c = "I"
    folder = os.path.join(B.REPO, META["folder"])
    rsw, rsc, af, lf = (os.path.join(folder, n) for n in ("RS-w_caseI.csv", "RS-c_caseI.csv", "AF_caseI.csv", "LF_caseI.xlsx"))
    prov[c] = [rsw, rsc, af, lf, os.path.join(folder, "readme_caseI.md")] + [os.path.join(folder, f"MP-{n}_caseI.png") for n in ("y-w", "z-w", "y-c", "z-c")]

    # ---- the CSVs
    hw, rw = B.read_csv_rows(rsw)
    hc, rc = B.read_csv_rows(rsc)
    B.log(f"[I] RS-w_caseI.csv header (bare): {hw}; RS-c_caseI.csv header (bare): {hc}; both with a UTF-8 BOM; no point numbers, no variances, no concentration rms")
    iw, ic = {h: i for i, h in enumerate(hw)}, {h: i for i, h in enumerate(hc)}
    cw = pd.DataFrame([{n: B.num(r[iw[n]]) for n in ("x", "y", "z", "U", "V", "W", "k")} for r in rw])
    cc = pd.DataFrame([{n: B.num(r[ic[n]]) for n in ("x", "y", "z", "C")} for r in rc])

    # ---- the workbook
    wb = read_xlsx(lf)
    vm = wb["Velocity measurement"]
    uh_wb = number(vm[(0, 2)])
    wv = pd.DataFrame([[number(x) for x in v[1:12]] for r, v in sheet_rows(vm, first=2, ncols=12) if isinstance(v[1], float)],
                      columns=["x", "y", "z", "U", "V", "W", "TKE", "Ur", "Vr", "Wr", "TKEr"])
    cm = wb["Concentration_measurement"]
    c0 = number(cm[(0, 5)])
    wc = pd.DataFrame([[number(x) for x in v[1:6]] for r, v in sheet_rows(cm, first=2, ncols=7) if isinstance(v[1], float)], columns=["x", "y", "z", "C", "Cr"])
    n_wc_text = sum(1 for r, v in sheet_rows(cm, first=2, ncols=7) if not isinstance(v[1], float))
    B.log(f"[I] workbook: 'Velocity measurement' {len(wv)} rows (UH = {uh_wb} m/s), 'Concentration_measurement' {len(wc)} rows (C0 = {c0} ppm; {n_wc_text} stray non-numeric row(s) ignored)")
    key = lambda d: list(zip(d.x.round(4), d.y.round(4), d.z.round(4)))  # noqa: E731
    wv["key"], wc["key"] = key(wv), key(wc)
    cw["key"], cc["key"] = key(cw), key(cc)

    def first_by_key(w):
        seen, rows_ = set(), []
        for r in w.itertuples():
            if r.key not in seen:
                seen.add(r.key)
                rows_.append(r)
        return {r.key: r for r in rows_}

    fw = first_by_key(wv)
    # the concentration CSV keeps its 13 repeated locations; map each CSV row to the n-th workbook row with that key
    occ = {}
    cc_wb = []
    wc_by = {}
    for r in wc.itertuples():
        wc_by.setdefault(r.key, []).append(r)
    for r in cc.itertuples():
        i = occ.get(r.key, 0)
        occ[r.key] = i + 1
        cc_wb.append(wc_by[r.key][i])

    # ---- rows. V on the y = 0 plane is numerically zero in the workbook (|V| < 4e-6 m/s): a symmetry value, not a measurement -> NaN
    out, vy0 = [], 0
    for n, r in enumerate(cw.itertuples(), start=1):
        w = fw[r.key]
        v = w.V
        if r.y == 0.0:
            vy0 += 1
            v = math.nan
        out.append(B.row(case_id=c, instrument=INSTRUMENT_W, point_id=n, x=r.x, y=r.y, z=r.z, U=w.U, V=v, W=w.W, k=w.TKE))
    for n, (r, w) in enumerate(zip(cc.itertuples(), cc_wb), start=len(cw) + 1):
        out.append(B.row(case_id=c, instrument=INSTRUMENT_C, point_id=n, x=r.x, y=r.y, z=r.z, C=w.C, concentration_ratio=w.C / c0))
    B.log("[I] transform: one row per (instrument, point); wind rows (ldv: U V W k) numbered 1-91 and concentration rows (hydrocarbon_analyzer: C, C/c0) numbered 92-630, each in its CSV's row order; "
          f"values from the workbook (the CSVs agree to their 3 dp / 1 dp rounding); V on the y = 0 plane ({vy0} points) set to NaN: the workbook has |V| < 4e-6 m/s there, a symmetry value, not a measurement")
    pts = pd.DataFrame(out, columns=B.POINT_COLUMNS)
    W_, C_ = pts[pts.instrument == INSTRUMENT_W], pts[pts.instrument == INSTRUMENT_C]

    # ---- approach flow: AF_caseI.csv carries stray cells from the spreadsheet; the workbook's 'Inflow boundary layer' sheet is the source
    ah, ar = B.read_csv_rows(af)
    ai = {n: i for i, n in enumerate(ah)}
    af_rows = [(B.num(r[ai["z"]]), B.num(r[ai["U"]]), B.num(r[ai["k"]])) for r in ar if not math.isnan(B.num(r[ai["z"]]))]
    stray = [r for r in ar if math.isnan(B.num(r[ai["z"]]))]
    ib = wb["Inflow boundary layer"]
    wa = pd.DataFrame([[number(x) for x in v[3:11]] for r, v in sheet_rows(ib, first=3, ncols=11) if isinstance(v[6], float)],
                      columns=["z_mm", "z", "zH", "U", "UoUH", "p17", "k", "koUH2"])
    afl = pd.DataFrame([{"case_id": c, "z": r.z, "U": r.U, "uu": math.nan, "vv": math.nan, "ww": math.nan, "k": r.k} for r in wa.itertuples()])
    B.log(f"[I] approach flow: AF_caseI.csv holds {len(af_rows)} data rows and {len(stray)} stray row(s) with spreadsheet leftovers ({[r[2] for r in stray]}) that a naive reader takes for data; "
          f"the workbook's 'Inflow boundary layer' sheet is the source ({len(afl)} heights, z in metres)")

    boxes = [{"min": [-SIDE / 2, -SIDE / 2, 0.0], "max": [SIDE / 2, SIDE / 2, H_CUBE]}]
    geo = [("default", boxes, "generated from the readme's stated 0.1 m cube centred on the origin (MP-y-c_caseI.png, MP-z-c_caseI.png); x, y in [-0.05, 0.05], z in [0, 0.1]. "
            "The 6 mm roof outlet at (0, 0, 0.1) is not part of the body")]

    # ---- checks: the tables
    B.check(c, "csv_row_counts_91_wind_and_539_concentration", len(cw) == 91 and len(cc) == 539, wind=len(cw), concentration=len(cc), workbook_wind_rows=len(wv), workbook_concentration_rows=len(wc))
    B.check(c, "point_ids_1_to_630_unique", sorted(pts.point_id) == list(range(1, 631)) and len(W_) == 91 and len(C_) == 539)
    dropped_w = len(wv) - len(fw)
    ident = all(max(abs(a - b) for a, b in zip((r.U, r.V, r.W, r.TKE), (fw[r.key].U, fw[r.key].V, fw[r.key].W, fw[r.key].TKE))) == 0 for r in wv.itertuples() if r.key in fw)
    B.check(c, "workbook_wind_rows_not_in_the_csv_are_exact_copies", dropped_w == 4 and ident and set(fw) == set(cw.key), workbook_rows=len(wv), csv_rows=len(cw), duplicates_dropped_by_the_csv=dropped_w,
            note="the four y = 0, z = 0.05 points shared by the vertical-plane and the z/H = 0.5 plane listings appear twice in the workbook, identical, and once in the CSV")
    mu = {q: float(np.max(np.abs(np.array([getattr(fw[r.key], a) for r in cw.itertuples()]) - cw[q].to_numpy()))) for q, a in (("U", "U"), ("V", "V"), ("W", "W"), ("k", "TKE"))}
    B.check(c, "wind_csv_agrees_with_the_workbook_to_3dp", max(mu.values()) <= ROUND_3DP, max_abs_diff=mu, rows=len(cw))
    cmx = float(max(abs(a.C - b.C) for a, b in zip(cc.itertuples(), cc_wb)))
    B.check(c, "concentration_csv_agrees_with_the_workbook_to_1dp", cmx < 1e-9 and len(wc) in (539, 540), rows=len(cc), max_abs_diff_ppm=cmx, workbook_rows=len(wc))
    B.check(c, "concentration_is_published_to_0.1_ppm_so_the_plume_edge_is_coarse", bool(np.allclose(C_.C * 10, np.round(C_.C * 10), atol=1e-6)) and float(C_.C.min()) == 0.1, min_ppm=float(C_.C.min()),
            values_below_1_ppm=int((C_.C < 1).sum()), values_at_or_below_0_5_ppm=int((C_.C <= 0.5).sum()), negatives=int((C_.C < 0).sum()),
            note="every value is a multiple of 0.1 ppm: a 0.4 ppm value carries +/-12 % of quantisation alone; none is zero or negative, unlike Case H")
    vmax0 = float(wv[wv.y == 0].V.abs().max())
    vmin1 = float(wv[wv.y != 0].V.abs().min())
    B.check(c, "V_on_the_y0_plane_is_numerically_zero_not_measured", vmax0 < 1e-5 and vmin1 > 1e-2 and int((cw.y == 0).sum()) == 53, max_abs_V_on_y0_m_s=vmax0, points_on_y0=int((cw.y == 0).sum()),
            min_abs_V_off_y0_m_s=vmin1, max_abs_V_off_y0_m_s=float(wv[wv.y != 0].V.abs().max()), csv_value_on_y0=sorted(set(cw[cw.y == 0].V)),
            note="53 of 91 points: the workbook's V there is 1e-9..4e-6 m/s (an LDA's noise is 1e-2); the CSV prints 0. Set to NaN so that scoring V does not count 53 symmetry values as measurements. QUESTIONS.md QI2")
    B.check(c, "k_is_not_decomposable_no_variances_published", W_[["uu", "vv", "ww"]].isna().all().all(), note="only the TKE is published; k cannot be checked against variances (Cases A, B, D can)")
    kr = float(np.max(np.abs(wv.TKEr * UH_STATED ** 2 - wv.TKE)))
    ur = float(np.max(np.abs(wv.Ur * UH_STATED - wv.U)))
    B.check(c, "velocity_sheet_ratios_use_UH_1.7", kr < 1e-9 and ur < 1e-9 and abs(uh_wb - UH_STATED) < 1e-12, max_abs_diff_k=kr, max_abs_diff_U=ur, UH_velocity_sheet=uh_wb)
    UH_in = float(wa.U[np.isclose(wa.z, H_CUBE)].iloc[0])
    UH_in_implied = float((wa.U / wa.UoUH).median())
    B.check(c, "inflow_sheet_normalises_with_1.697_not_1.7", abs(UH_in_implied / UH_in - 1) < 1e-4 and abs(UH_in / UH_STATED - 1) < 0.005, U_at_z_H_m_s=UH_in, UH_implied_by_the_inflow_sheet_ratios=UH_in_implied,
            UH_velocity_sheet=UH_STATED, difference_pct=100 * (UH_in / UH_STATED - 1),
            note="the 'Inflow boundary layer' sheet divides by the measured U(0.1 m) = 1.6969, the 'Velocity measurement' sheet by 1.7: a 0.18 % difference between two normalisations in one workbook")
    uh_spread = float((wa.U / wa.UoUH).max() - (wa.U / wa.UoUH).min())
    kk = float(np.max(np.abs(wa.koUH2 - wa.k / UH_in_implied ** 2)))
    B.check(c, "inflow_sheet_k_ratio_is_k_over_the_same_UH_1.697", uh_spread < 1e-6 and kk < 1e-9, max_abs_diff=kk, UH_implied=UH_in_implied, spread_of_the_implied_UH=uh_spread)
    caf = np.array(af_rows)
    B.check(c, "approach_flow_csv_agrees_with_the_workbook_profile_and_carries_stray_cells", len(af_rows) == len(wa) == 12 and float(np.max(np.abs(caf[:, 0] - wa.z.to_numpy()))) < 1e-9
            and float(np.max(np.abs(caf[:, 1] - wa.U.to_numpy()))) <= ROUND_3DP and float(np.max(np.abs(caf[:, 2] - wa.k.to_numpy()))) <= 5.0e-5 + 1e-9 and len(stray) == 2,
            rows=len(af_rows), stray_rows=len(stray), stray_cells=[r[2] for r in stray], max_abs_diff_U=float(np.max(np.abs(caf[:, 1] - wa.U.to_numpy()))), max_abs_diff_k=float(np.max(np.abs(caf[:, 2] - wa.k.to_numpy()))),
            note="AF_caseI.csv ends in 53 rows of ',,' and two cells '0.5*' and '1.5*' (axis labels of a chart); the whitespace rows are blank, the two cells are rows a reader that does not test z for a number accepts")

    # ---- source and normalisation
    q_eth = GAS_CC_MIN * GAS_FRACTION / 6e7
    c0_calc = 1e6 * q_eth / (UH_STATED * H_CUBE ** 2)
    B.check(c, "c0_is_the_ethane_flow_over_UH_H2", abs(c0 / c0_calc - 1) < 5e-4 and abs(c0 / 39.2 - 1) < 1e-3, c0_workbook_ppm=c0, c0_recomputed_ppm=c0_calc, c0_paper_ppm=39.2, ethane_flow_m3_s=q_eth,
            mixture_flow_m3_s=GAS_CC_MIN / 6e7, c0_if_the_mixture_flow_were_used_ppm=1e6 * (GAS_CC_MIN / 6e7) / (UH_STATED * H_CUBE ** 2),
            note="the paper writes 'ethane released at 6.67e-6 m3/s' (the 10 % mixture); c0 = 39.2 ppm needs the 6.67e-7 m3/s of pure ethane (10 times more would be 392 ppm). The workbook's 39.2235 = 666.8/17 uses 1/60 rounded to 0.01667")
    cr = float(np.max(np.abs(wc.Cr - wc.C / c0)))
    B.check(c, "workbook_C_over_C0_column_is_C_over_39.2235", cr < 1e-9, max_abs_diff=cr)
    ve = GAS_CC_MIN / 6e7 / (math.pi * (D_OUT_MM / 2000) ** 2)
    B.check(c, "release_momentum_ratio_Ve_over_UH_is_0.14", abs(ve / UH_STATED / M_STATED - 1) < 0.02, Ve_m_s=ve, M=ve / UH_STATED, M_stated=M_STATED, note="400 cc/min through a 6 mm outlet, over UH = 1.7 m/s")

    # ---- geometry and frame
    xyz = pts[["x", "y", "z"]].drop_duplicates().to_numpy()
    B.check(c, "no_sensor_inside_the_cube", int(B.points_in_boxes(xyz, boxes).sum()) == 0, points=len(xyz), points_on_a_face_plane=int((np.isclose(np.abs(xyz[:, 0]), SIDE / 2) | np.isclose(np.abs(xyz[:, 1]), SIDE / 2)).sum()),
            note="points at x = -0.05 and 0.0 lie over the roof (z >= 0.115), none inside")
    ctrl = B.points_in_boxes(xyz - np.array([0.1, 0.0, 0.0]), boxes)
    B.check(c, "control_points_shifted_0.1m_upwind_are_detected_inside", int(ctrl.sum()) > 3, inside_after_shift=int(ctrl.sum()), shift_m=[-0.1, 0, 0], note="the x = 0.065 and 0.1 concentration lines land inside the cube")
    bb = [pts.x.min(), pts.x.max(), pts.y.min(), pts.y.max(), pts.z.min(), pts.z.max()]
    B.check(c, "extents_sane", bb[0] >= -0.15 - 1e-9 and bb[1] <= 2.7 + 1e-9 and bb[2] >= -0.44 - 1e-9 and bb[3] <= 0.4 + 1e-9 and bb[4] >= 0 and bb[5] <= 0.5 + 1e-9, bbox=bb,
            note="MP-y-c_caseI.png: x to 2.7 m, z to 0.42 m; MP-z-c_caseI.png: y -0.44 .. 0.4")
    behind = W_[(W_.y == 0) & (W_.x.between(0.065, 0.15)) & (W_.z <= 0.05)]
    over = W_[(W_.y == 0) & (W_.x.between(-0.05, 0.0)) & (W_.z >= 0.115) & (W_.z <= 0.2)]
    B.check(c, "WD0_flow_reverses_behind_the_cube_and_speeds_up_over_the_roof", bool((behind.U < 0).all()) and len(behind) >= 6 and bool((over.W > 0).all()) and bool((over.U > 0).all()),
            points_behind=len(behind), mean_U_behind_m_s=float(behind.U.mean()), points_over_roof=len(over), mean_W_over_roof_m_s=float(over.W.mean()),
            note="y = 0, 0.065 <= x <= 0.15, z <= 0.05: U < 0 (the wake); over the roof W > 0 and U > 0: the wind blows toward +x and the cube sits at x in [-0.05, 0.05]")
    off = W_[(W_.y != 0) & W_.V.notna() & (W_.x <= -0.05 + 1e-9)]
    B.check(c, "lateral_sign_V_positive_toward_plus_y", len(off) >= 4 and bool((np.sign(off.V) == np.sign(off.y)).all()), points=len(off), sign_agreement=float((np.sign(off.V) == np.sign(off.y)).mean()),
            xs=sorted(set(off.x)), note="at and upwind of the windward face the flow diverges around the cube, so V has the sign of y")
    peak = C_.loc[C_.C.idxmax()]
    B.check(c, "concentration_peak_is_just_above_the_roof_outlet_downwind", float(peak.z) >= H_CUBE and float(peak.x) == 0.065, peak_ppm=float(peak.C), at=[float(peak.x), float(peak.y), float(peak.z)], peak_over_c0=float(peak.C / c0),
            note="the first station past the cube (x = 0.065), z = 0.12 m, 2 cm above the roof plane: the plume leaves the roof and is carried down the leeward face")
    dup = C_[C_.duplicated(["x", "y", "z"], keep=False)]
    gaps = [abs(g.C.iloc[0] - g.C.iloc[1]) / g.C.mean() for _, g in dup.groupby(["x", "y", "z"])]
    B.check(c, "thirteen_ground_centreline_locations_measured_twice", len(gaps) == 13 and all(len(g) == 2 for _, g in dup.groupby(["x", "y", "z"])), locations=len(gaps), mean_relative_difference=float(np.mean(gaps)),
            max_relative_difference=float(np.max(gaps)), max_abs_difference_ppm=float(max(abs(g.C.iloc[0] - g.C.iloc[1]) for _, g in dup.groupby(["x", "y", "z"]))),
            note="(x, 0, 0): the y = 0 plane and the z = 0 plane share these points and the CSV keeps both values under their own point numbers: a free repeatability estimate (unlike the wind points, whose repeats are identical copies)")
    # tracer flux through the planes, separable approximation (C(y,z) = C(0,z) C(y,0)/C(0,0)); U(z) from the approach profile
    q_ppm = q_eth * 1e6
    ratios = {}
    for xs in sorted(C_.x.unique()):
        g = C_[C_.x == xs]
        lat = g[g.z == 0].groupby("y").C.mean()
        ver = g[g.y == 0].groupby("z").C.mean()
        if len(lat) < 5 or len(ver) < 5:
            continue
        gy = np.trapezoid(lat.values, lat.index.values) / lat.loc[0.0]
        fz = np.trapezoid(ver.values * np.interp(ver.index.values, wa.z.to_numpy(), wa.U.to_numpy()), ver.index.values)
        ratios[float(xs)] = float(fz * gy / q_ppm)
    far = ratios[2.7]
    B.check(c, "tracer_flux_through_x_2.7_is_0.8_to_1.3_of_the_release", 0.8 < far < 1.3, flux_over_release=far, ratio_by_x={str(k): round(v, 3) for k, v in ratios.items()}, release_ppm_m3_s=q_ppm,
            method="separable: C(y, z) = C(0, z) x C(y, 0)/C(0, 0), U(z) from the approach profile, trapezoid; the plume is wider at the ground than aloft, which this overestimates",
            note="an INDEPENDENT test of the release rate against the concentrations: the ratio falls from 3.6 at x = 0.065 m (the separable form fails near the source) to 1.16 at x = 2.7 m")

    # ---- approach-flow fits
    pl = B.power_law_fit(wa.z, wa.U, 0.02, 2 * H_CUBE)
    pl_all = B.power_law_fit(wa.z, wa.U, 0.02, 0.5)
    dev = np.abs(wa.UoUH.to_numpy() / wa.p17.to_numpy() - 1)
    B.check(c, "approach_profile_follows_the_1_over_7_power_law_within_5_percent", float(dev.max()) < 0.05 + 1e-9, max_rel_deviation=float(dev.max()), fitted_index_z_0p02_to_0p2=pl["alpha"], fitted_index_z_0p02_to_0p5=pl_all["alpha"], stated_index=1 / 7,
            note="the workbook's own (z/H)^(1/7) column against the measured U/UH, z = 0.02 .. 0.7 m; the least-squares index is 0.12 (the profile is flatter than 1/7 near the ground)")
    fit = B.log_law_fit(wa.z, wa.U, 0.02, 0.4)
    fit["error_at_H_rel"] = round(B.log_law_U(fit, H_CUBE) / UH_in - 1, 4)
    ti = float(np.sqrt(2 * wa.k[np.isclose(wa.z, H_CUBE)].iloc[0] / 3) / UH_in)
    inflow = {"U_H_m_s": round(UH_in, 6), "U_H_stated_m_s": UH_STATED, "H_m": H_CUBE, "z_ref_m": H_CUBE, "U_ref_basis": "the measured U at z = H; the 'Velocity measurement' sheet and every ratio of the points use 1.7",
              "turbulence_intensity_at_H_isotropic_estimate": round(ti, 4), "log_law": fit, "power_law": pl, "power_law_one_seventh_stated": "paper: 'followed a 1/7 power-law profile'",
              "method": f"least squares, kappa = {B.KAPPA}, z = 0.02 .. 0.4 m on the workbook's 12-point profile",
              "c0_ppm": c0, "c0_paper_ppm": 39.2, "tunnel": "20 m long, 3.0 x 2.0 m cross-section (paper section 3.9)",
              "note": "the approach-flow table's uu, vv, ww are empty: only k is published; set wind speed 3.2 (the workbook's first cell, Japanese label) is the tunnel setting"}
    frame = {"origin": "the centre of the cube on the ground plane (MP-y-c_caseI.png, MP-z-c_caseI.png)",
             "x": "+x streamwise (the wind blows toward +x): the cube occupies x in [-0.05, 0.05]; wind points x = -0.15 .. 0.25, concentration points x = 0.065 .. 2.7",
             "y": "+y lateral; the cube spans y in [-0.05, 0.05]; wind points on y = 0 and on the plane z = 0.05 at |y| <= 0.15, concentration points on y = 0 and on the ground at |y| <= 0.44",
             "z": "+z up; roof at z = 0.1 m; the source (6 mm outlet) at (0, 0, 0.1)", "source": "ethane, 10 % in the mixture, 400 cc/min through a 6 mm circular outlet at the roof centre (M = 0.14)",
             "length_scale": "model metres (the source states no model:full scale ratio; Eddy3D solves it at 1:60)"}
    transform = {"coordinate_scale": 1.0, "lateral_sign": 1, "origin_shift_m": [0, 0, 0], "c0_ppm": c0,
                 "note": "values from the workbook; one row per instrument, wind rows 1-91 and concentration rows 92-630; V on the y = 0 plane set to NaN; coordinates as published"}
    src = {"x_m": 0.0, "y_m": 0.0, "z_m": H_CUBE, "diameter_mm": D_OUT_MM, "gas": "ethane, 10 % in the mixture", "flow_cc_per_min_mixture": GAS_CC_MIN, "ethane_flow_m3_s": q_eth, "release_velocity_m_s": ve, "momentum_ratio": ve / UH_STATED}
    known = {"V_on_y0": {"points": int((cw.y == 0).sum()), "treated_as": "not measured (NaN)"}, "af_csv_stray_cells": [r[2] for r in stray], "concentration_quantum_ppm": 0.1,
             "UH_1.7_vs_1.697": {"velocity_sheet": UH_STATED, "inflow_sheet": round(UH_in, 6)}, "paper_mixture_flow_vs_ethane_flow": {"paper_m3_s": 6.67e-6, "ethane_m3_s": q_eth}}
    return pts, afl, geo, inflow, frame, transform, {"known_issues": known, "source": src, "plume_flux_over_release_x_2.7": round(far, 4)}
