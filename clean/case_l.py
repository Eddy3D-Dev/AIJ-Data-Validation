"""Case L (ArraysCT) — 9 x 14 cube array, floor line source, unstable non-isothermal boundary layer.

Zenodo 10.5281/zenodo.15487637 (Yoshie, Katada). build(B, prov) is called by clean/build.py with the build module as B
and returns (points, approach flow, geometry, inflow, frame, transform, extra).

RS_caseL.csv is the workbook's 'All measuring points' sheet rounded to the printed decimals; its temperature column
is headed 'T(K)' but holds degrees Celsius. The point table is built from the workbook at full precision.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

import jkl_common as X

check = X.check

META = {
    "id": "L", "title": "Case L — 9 x 14 cube array, floor line source, non-isothermal",
    "folder": "raw/cases/case-l", "zenodo_concept": "10.5281/zenodo.15487637", "zenodo_version": None,
    "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    "collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Koudai Katada (Tokyo Polytechnic University)"],
    "citation": "Yoshie, R., Nomura, K., Katada, K., Jiang, G. (2012). Non-isothermal large eddy simulation of pollutant and thermal dispersion in urban street canyons. 22nd National Symposium on Wind Engineering, 61-66 (in Japanese). https://doi.org/10.14887/kazekosymp.22.0.61.0; Jiang, G., Yoshie, R. (2018). Large-eddy simulation of flow and pollutant dispersion in a 3D urban street model located in an unstable boundary layer. Build. Environ. 142, 47-57. https://doi.org/10.1016/j.buildenv.2018.06.015",
}

# stated by the readme / data paper section 3.12 (verified or contradicted in the checks)
H, U_H_STATED, Q_GAS, ROWS, COLS = 0.06, 1.34, 8.33e-6, 14, 9
PITCH, X_FIRST, Y_FIRST = 0.12, -0.96, -0.51
SOURCE_X = -0.15                    # centre of the line source, 0.15 m windward of the origin wall, between rows 7 and 8
SOURCE_README = (0.037, 1.2)        # x, y size of the source area (readme)
KELVIN = 273.15
# workbook column of each published quantity ('All measuring points'); the CSV decimals of each
WB = {"U": 5, "V": 6, "W": 7, "su": 8, "sv": 9, "sw": 10, "k": 11, "T": 12, "T_rms": 13, "uT": 14, "vT": 15, "wT": 16, "C": 17, "c_rms": 18,
      "uc": 19, "vc": 20, "wc": 21, "uv": 22, "uw": 23, "tc": 24}
CSV_COL = {"U": "U", "V": "V", "W": "W", "su": "u_rms", "sv": "v_rms", "sw": "w_rms", "k": "k", "T": "T", "T_rms": "t_rms", "uT": "ut", "vT": "vt", "wT": "wt", "C": "C", "c_rms": "c_rms",
           "uc": "uc", "vc": "vc", "wc": "wc", "uv": "uv", "uw": "uw", "tc": "tc"}
DECIMALS = {"U": 2, "V": 2, "W": 2, "su": 3, "sv": 3, "sw": 3, "k": 4, "T": 2, "T_rms": 3, "uT": 4, "vT": 4, "wT": 4, "C": 2, "c_rms": 3, "uc": 4, "vc": 4, "wc": 4, "uv": 4, "uw": 4, "tc": 4}


def _solids(path):
    """{solid name: triangles} of an ASCII STL that holds several solids."""
    out, name, cur = {}, None, []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("solid"):
                name = s.split(None, 1)[1] if len(s.split(None, 1)) > 1 else ""
                out[name] = []
                cur = []
            elif s.startswith("vertex"):
                cur.append(tuple(float(t) for t in s.split()[1:4]))
                if len(cur) == 3:
                    out[name].append(tuple(cur))
                    cur = []
    return out


def build(B, prov):
    c = "L"
    folder = os.path.join(B.REPO, META["folder"])
    f = {n: os.path.join(folder, n) for n in ("RS_caseL.csv", "AF_caseL.csv", "BD_caseL.stl", "LF_caseL.xlsx", "readme_caseL.md", "MP-y_caseL.png", "MP-z_caseL.png")}
    prov[c] = list(f.values())
    B.DIRECTION_BASIS[c] = ("definition: +x streamwise (BD_caseL.stl: 14 rows along x, the line source 0.15 m upwind of the origin wall); checks WD0_flow_is_along_x, concentration_peaks_on_the_source_line", "settled")
    wb = X.read_xlsx(f["LF_caseL.xlsx"])
    sh = wb["All measuring points"]
    K = {" ".join(k_.split()): v_ for k_, v_ in X.labelled_constants(sh, 27, 28).items()}
    uH, thf, dth, c0, Hwb, thH = K["<uH> (m/s)"], K["<θf > (oC)"], K["<Δθ> (oC)"], K["<C0> (ppm)"], K["H (m)"], K["<θH> (oC)"]
    wrows = [r for r in sh[3:] if isinstance(r[1], float)]
    if len(wrows) != 344 or abs(Hwb - H) > 1e-12:
        raise SystemExit("Case L: the workbook's 'All measuring points' sheet no longer has the layout the builder reads")
    B.log(f"[L] LF_caseL.xlsx: H = {Hwb} m, <uH> = {uH} m/s, <θf> = {thf:.4f} degC, <θH> = {thH:.4f} degC, <Δθ> = {dth:.4f} degC, <θ0> = {K['<θ0> (oC)']:.4f} degC, <θbuild> = {K['<θbuild> (oC)']:.4f} degC, "
          f"<θgas> = {K['<θgas> (oC)']} degC, Rb = {K['Rb']}, C0 = {c0:.6f} ppm = Cgas {K['Cgas (ppm)']:.0f} ppm x q {K['q (m3/s)']:.5g} m3/s / (<uH> H^2)")
    header, rows = B.read_csv_rows(f["RS_caseL.csv"])
    idx = {h: i for i, h in enumerate(header)}
    B.log(f"[L] RS_caseL.csv header (bare): {header}; the header says T(K) but the values are DEGREES CELSIUS (12.85 .. 29.86; AF_caseL.csv's T is in kelvin, 283 .. 295); uc, vc, wc m/s ppm; tc K ppm")
    csv = pd.DataFrame([{n: B.num(r[idx[n]]) for n in header} for r in rows])
    W = {q_: np.array([r[j_] for r in wrows], float) for q_, j_ in WB.items()}
    wxyz = np.array([[r[1] / 1000.0, r[2] / 1000.0, r[3] / 1000.0] for r in wrows])
    pts = pd.DataFrame([B.row(case_id=c, instrument="split_fibre", point_id=int(csv["No."].iloc[i]), x=csv.x.iloc[i], y=csv.y.iloc[i], z=csv.z.iloc[i], U=W["U"][i], V=W["V"][i], W=W["W"][i],
                              uu=W["su"][i] * W["su"][i], vv=W["sv"][i] * W["sv"][i], ww=W["sw"][i] * W["sw"][i], k=W["k"][i], uv=W["uv"][i], uw=W["uw"][i], C=W["C"][i], c_rms=W["c_rms"][i], concentration_ratio=W["C"][i] / c0,
                              T=W["T"][i], T_rms=W["T_rms"][i], uc=W["uc"][i], vc=W["vc"][i], wc=W["wc"][i], uT=W["uT"][i], vT=W["vT"][i], wT=W["wT"][i]) for i in range(len(csv))], columns=B.POINT_COLUMNS)
    pts = X.tidy(pts)
    B.log("[L] transform: workbook values (x, y, z mm -> m; the CSV is these rounded); T = the workbook's <θ> in degC (the CSV's 'T(K)' column is already degC); rms squared to variances; "
          "vw not published -> NaN; <θ'c'> (CSV 'tc') and Usc (the vector magnitude of the mean velocity, workbook only) are not carried")

    # ---- approach flow: the workbook's 'Inflow' sheet (25 heights, x = -0.4 m), CSV = its rounding
    inf = [r for r in wb["Inflow"][3:] if isinstance(r[1], float)]
    h2, ar = B.read_csv_rows(f["AF_caseL.csv"])
    a2 = {n: i for i, n in enumerate(h2)}
    afc = pd.DataFrame([{n: B.num(r[a2[n]]) for n in h2} for r in ar])
    afw = pd.DataFrame([{"x": r[1] / 1000.0, "z": r[3] / 1000.0, "U": r[5], "V": r[6], "W": r[7], "uu": r[8] ** 2, "vv": r[9] ** 2, "ww": r[10] ** 2, "uv": r[17], "uw": r[18], "k": r[11],
                         "T": r[12], "T_rms": r[13], "uT": r[14], "vT": r[15], "wT": r[16]} for r in inf]).sort_values("z", kind="mergesort").reset_index(drop=True)
    afl = pd.DataFrame({"case_id": c, "z": afw.z, "U": afw.U, "uu": afw.uu, "vv": afw.vv, "ww": afw.ww, "k": afw.k})
    B.write_csv(os.path.join(B.HERE, "cases", c, "approach_flow_full.csv"), afw)
    B.log("[L] approach flow: workbook 'Inflow' sheet, 25 heights at x = -0.4 m, sorted ascending in z (the CSV lists 0.32 m first); T in degC; AF_caseL.csv has T in kelvin and no k; "
          "the full profile (V, W, uv, uw, T, heat fluxes) is cases/L/approach_flow_full.csv")

    # ---- geometry: the published STL
    solids = _solids(f["BD_caseL.stl"])
    btris, stris = solids["buildings"], solids["line_source"]
    bst = B.stl_stats(btris)
    shells = B.shells_from_tris(btris, tol=1e-6)
    boxes = []
    for s_ in shells:
        p_ = np.array([v for t in s_ for v in t])
        lo, hi = p_.min(axis=0), p_.max(axis=0)
        corners = {tuple(np.round([x_, y_, z_], 6)) for x_ in (lo[0], hi[0]) for y_ in (lo[1], hi[1]) for z_ in (lo[2], hi[2])}
        if any(tuple(np.round(v, 6)) not in corners for v in p_):
            raise SystemExit("Case L: a shell of BD_caseL.stl is not a box")
        boxes.append({"min": [round(float(v), 9) for v in lo], "max": [round(float(v), 9) for v in hi]})
    boxes.sort(key=lambda b_: (b_["min"][0], b_["min"][1]))
    analytic = X.cube_boxes(ROWS, COLS, X_FIRST, Y_FIRST, H, PITCH)
    analytic.sort(key=lambda b_: (b_["min"][0], b_["min"][1]))
    sst = B.stl_stats(stris)
    geo = [("default", boxes, "the 126 closed shells of BD_caseL.stl ('buildings' solid: 1,512 triangles, no open edge; the 126 bottom faces are wound inward), each reduced to its box (identical to the 14 x 9 grid of 0.06 m cubes on a 0.12 m pitch); "
                              "the 'line_source' solid (a flat 0.04 m x 1.02 m patch at z = 0) is not a building and is described in the frame")]
    B.log(f"[L] geometry: BD_caseL.stl = 'buildings' {bst['triangles']} triangles, {len(shells)} shells, watertight {bst['watertight']}, signed volume {bst['signed_volume']}, bbox {bst['bbox_min']}..{bst['bbox_max']}; "
          f"'line_source' {sst['triangles']} triangles, bbox {sst['bbox_min']}..{sst['bbox_max']}")

    # ---- checks
    n = len(pts)
    loc = pts.groupby(["x", "y"]).z.apply(lambda s_: tuple(sorted(s_)))
    census = {}
    for k_, v_ in loc.value_counts().items():
        census[len(k_)] = census.get(len(k_), 0) + int(v_)
    check(B, c, "row_count_and_layout_match_the_data_paper", n == 344 and census == {8: 27, 4: 14, 3: 24} and 27 * 8 + 14 * 4 + 24 * 3 == 344, rows=n, locations_by_number_of_heights=census,
          note="data paper section 3.12: 8 heights (4 .. 150 mm) at 27 locations on the road near the source, 4 heights (70 .. 150 mm) at 14 locations on the blocks, 3 heights (4 .. 30 mm) at 24 locations around: 216 + 56 + 72 = 344")
    check(B, c, "point_ids_unique_and_contiguous", sorted(pts.point_id) == list(range(1, 345)))
    dxyz = float(np.max(np.abs(wxyz - csv[["x", "y", "z"]].to_numpy())))
    check(B, c, "csv_and_workbook_list_the_same_344_points_in_the_same_order", dxyz < 1e-9 and not pts.duplicated(["x", "y", "z"]).any(), max_abs_diff_xyz_m=dxyz, note="workbook X, Y, Z are millimetres")
    meas = ["U", "V", "W", "uu", "vv", "ww", "k", "uv", "uw", "C", "c_rms", "T", "T_rms", "uc", "vc", "wc", "uT", "vT", "wT"]
    check(B, c, "no_sentinels_or_nan_in_measured_columns", not pts[["x", "y", "z"] + meas].isna().any().any())
    res = {q_: X.within_half_unit(csv[CSV_COL[q_]].to_numpy(), W[q_], DECIMALS[q_]) for q_ in WB}
    check(B, c, "csv_equals_workbook_rounded", all(v_[1] == 0 for v_ in res.values()), per_column={CSV_COL[q_]: {"decimals": DECIMALS[q_], "max_abs_diff": v_[0], "cells_beyond_half_a_unit": v_[1]} for q_, v_ in res.items()},
          note="every CSV column, including 'T(K)', is the workbook value rounded to the printed decimals")
    wk = float(np.max(np.abs(W["k"] - 0.5 * (W["su"] ** 2 + W["sv"] ** 2 + W["sw"] ** 2))))
    check(B, c, "k_equals_half_sum_of_variances", wk < 1e-9, max_abs_error=wk, note="workbook k = 0.5 (sigma_u^2 + sigma_v^2 + sigma_w^2)")
    Tc = csv["T"]
    check(B, c, "RS_T_column_is_celsius_although_headed_K", float(Tc.max()) < 100.0 and float(afc["T"].min()) > 200.0 and bool(np.all(np.abs(W["T"] - Tc.to_numpy()) <= 0.005 + 1e-9)),
          RS_T_min_max=[float(Tc.min()), float(Tc.max())], AF_T_min_max=[float(afc["T"].min()), float(afc["T"].max())], floor_degC=thf, air_at_H_degC=thH,
          note="RS_caseL.csv 'T(K)' = 12.85 .. 29.86 equals the workbook's <θ> (deg.) to 0.005; AF_caseL.csv 'T(K)' = 283 .. 295 is kelvin (the same workbook's Inflow <θ> + 273.15). Read as kelvin the points would be 260 K colder than the floor's 318 K")
    afT = X.within_half_unit(afc["T"].to_numpy()[::-1], afw["T"].to_numpy() + KELVIN, 2)
    check(B, c, "AF_T_in_kelvin_equals_workbook_inflow_degC_plus_273.15", afT[1] == 0 and len(afc) == len(afw), max_abs_diff_K=afT[0], rows=len(afc))
    nm = {"x/H": float(np.max(np.abs(np.array([r[31] for r in wrows]) * H - wxyz[:, 0]))), "u": float(np.max(np.abs(np.array([r[35] for r in wrows]) * uH - W["U"]))), "k": float(np.max(np.abs(np.array([r[41] for r in wrows]) * uH ** 2 - W["k"]))),
          "theta": float(np.max(np.abs(np.array([r[42] for r in wrows]) * dth + thf - W["T"]))), "c": float(np.max(np.abs(np.array([r[47] for r in wrows]) * c0 - W["C"]))),
          "u'c'": float(np.max(np.abs(np.array([r[49] for r in wrows]) * uH * c0 - W["uc"]))), "u'v'": float(np.max(np.abs(np.array([r[52] for r in wrows]) * uH ** 2 - W["uv"]))),
          "theta'c'": float(np.max(np.abs(np.array([r[54] for r in wrows]) * dth * c0 - W["tc"]))), "w'theta'": float(np.max(np.abs(np.array([r[46] for r in wrows]) * uH * dth - W["wT"])))}
    check(B, c, "workbook_normalised_columns_reproduce_its_dimensional_columns", max(nm.values()) < 1e-9, max_abs_diff=nm, note="with H = 0.06 m, <uH> = 1.339415 m/s, <θf>, <Δθ> and <C0> of the workbook's own constant cells")
    usc = float(np.max(np.abs(np.array([r[4] for r in wrows]) - np.sqrt(W["U"] ** 2 + W["V"] ** 2 + W["W"] ** 2))))
    check(B, c, "workbook_Usc_is_the_vector_magnitude_of_the_mean_velocity", usc < 1e-9, max_abs_diff=usc, note="so it is derived, not measured, and is not carried (unlike Case K's <usc>, which is never below |U|)")
    # reference scales
    c0f = K["Cgas (ppm)"] * K["q (m3/s)"] / (uH * H ** 2)
    c0_paper = 1e6 * Q_GAS / (U_H_STATED * H ** 2)
    check(B, c, "c0_from_Cgas_q_UH_H_equals_workbook", abs(c0f / c0 - 1) < 1e-5, c0_workbook_ppm=c0, c0_formula_ppm=c0f, rel_diff=c0f / c0 - 1, c0_from_the_rounded_readme_values_ppm=c0_paper,
          note="c0 = q / (U_H H^2) with q = 8.33333e-6 m3/s (500 cc/min), U_H = 1.339415 m/s, H = 0.06 m; the readme's rounded q = 8.33e-6 and U_H = 1.34 give 1726.8 ppm (-0.08 %)")
    check(B, c, "temperatures_in_workbook_agree_with_data_paper", abs(thH - 14.8) < 0.1 and abs(dth - 30.3) < 0.1 and abs(dth - (thf - thH)) < 1e-6 and abs(K["<θgas> (oC)"] - 35.0) < 1e-9,
          theta_f_degC=thf, theta_H_degC=thH, delta_theta=dth, paper="theta_H = 14.8 degC, delta Theta = 30.3 degC, gas 35 degC; readme T_f = 45.0 degC")
    Rb = 9.80665 * H * (thH - thf) / ((K["<θ0> (oC)"] + KELVIN) * uH ** 2)
    check(B, c, "bulk_richardson_number_recomputed", abs(Rb / K["Rb"] - 1) < 0.05, Rb_workbook=K["Rb"], Rb_recomputed=Rb, readme=-0.04, formula="g H (theta_H - theta_f) / (theta_0 U_H^2)",
          note="the readme gives -0.04; the workbook -0.035; the formula -0.034")
    check(B, c, "readme_building_surface_temperature_is_the_air_temperature_at_H", abs(K["<θbuild> (oC)"] - 14.8) < 1.0, warn=True, readme_T_b_degC=14.8, workbook_theta_build_degC=K["<θbuild> (oC)"], workbook_theta_H_degC=thH,
          note="the readme calls T_b = 14.8 degC the building surface temperature; that is the approach-flow air temperature at H (<θH> = 14.75, also the readme's T_0); the workbook gives the building surface as <θbuild> = 42.2 degC (QUESTIONS.md QL2)")
    # geometry
    same = len(boxes) == len(analytic) == 126 and all(np.allclose(a_["min"], b_["min"], atol=1e-9) and np.allclose(a_["max"], b_["max"], atol=1e-9) for a_, b_ in zip(boxes, analytic))
    check(B, c, "BD_caseL_stl_is_126_cubes_on_a_0.12_m_pitch", same, shells=len(shells), cube_edge_m=H, pitch_m=PITCH, rows_x_columns=[ROWS, COLS], bbox_min=bst["bbox_min"], bbox_max=bst["bbox_max"],
          note="14 rows along x (x = -0.96 .. 0.66) by 9 columns across y (-0.51 .. 0.51); the data paper's '9 rows by 14 columns' counts the other way round; origin = windward wall of row 9")
    check(B, c, "BD_caseL_stl_buildings_solid_has_no_open_edge_and_the_analytic_volume", bst["edges_boundary"] == 0 and bst["edges_non_manifold"] == 0 and bst["bodies"] == 126 and abs(bst["signed_volume"] - 126 * H ** 3) < 1e-9,
          triangles=bst["triangles"], bodies=bst["bodies"], open_edges=bst["edges_boundary"], signed_volume_m3=bst["signed_volume"], analytic_volume_m3=126 * H ** 3,
          note="every edge is used by two triangles and the signed volume equals 126 H^3; unlike Cases D and E nothing needs repairing, except the bottom faces (next check)")
    check(B, c, "BD_caseL_stl_bottom_faces_are_wound_inward", bst["inconsistent_triangles"] == 252 and bst["watertight"] is False, warn=True, inconsistent_triangles=bst["inconsistent_triangles"], bodies=bst["bodies"],
          note="the two bottom triangles (z = 0) of each of the 126 cubes are wound against the other ten, so the file is closed but not consistently wound; the plane z = 0 adds nothing to the signed volume, which is why the volume and the open-edge count do not show it. The served geometry.stl is the 126 boxes, outward")
    inside = X.inside_count(pts, boxes)
    ctrl = X.inside_count(pts, boxes, (0.06, 0.0, 0.0))
    check(B, c, "no_sensor_inside_building", inside == 0, inside=inside, points=n)
    check(B, c, "control_shifted_points_are_detected_inside", ctrl > 0, inside_after_shift=ctrl, shift_m=[0.06, 0, 0])
    sx = (min(v[0] for t in stris for v in t), max(v[0] for t in stris for v in t))
    sy = (min(v[1] for t in stris for v in t), max(v[1] for t in stris for v in t))
    check(B, c, "source_patch_in_stl_matches_readme", abs((sx[1] - sx[0]) - SOURCE_README[0]) < 0.001 and abs((sy[1] - sy[0]) - SOURCE_README[1]) < 0.01, warn=True, stl_size_x_y_m=[sx[1] - sx[0], sy[1] - sy[0]], readme_size_x_y_m=list(SOURCE_README),
          stl_centre_x_m=(sx[0] + sx[1]) / 2, stl_y_range_m=list(sy), note="the STL patch is 0.04 m x 1.02 m (the width of the array) centred at x = -0.15 m; the readme and data paper give 0.037 m x 1.2 m (the tunnel width); QUESTIONS.md QL3")
    upper = [k_ for k_, v_ in loc.items() if len(v_) == 4]
    over = [k_ for k_ in upper if any(b_["min"][0] - 1e-9 <= k_[0] <= b_["max"][0] + 1e-9 and b_["min"][1] - 1e-9 <= k_[1] <= b_["max"][1] + 1e-9 for b_ in boxes)]
    on_row8 = [k_ for k_ in over if -0.12 - 1e-9 <= k_[0] <= -0.06 + 1e-9]
    check(B, c, "the_14_block_locations_are_over_roofs", len(upper) == 14 and len(over) == 14 and len(on_row8) == 9, upper_locations=len(upper), over_a_roof_footprint=len(over), on_the_roof_of_row_8=len(on_row8),
          note="the 14 locations with 4 heights (70 .. 150 mm, above the 60 mm roofs) are a 3 x 3 grid at H/2 spacing over the roof of the central cube of row 8 (x in [-0.12, -0.06]) and the roof centres of rows 7, 9, 10, 11 and 12; the points are above the roofs, none inside a cube")
    ys, zs = sorted(pts.y.unique()), sorted(pts.z.unique())
    check(B, c, "layout_matches_MP_drawings", ys == [-0.18, -0.12, -0.06, -0.03, 0.0, 0.03, 0.06, 0.12, 0.18] and zs == [0.004, 0.01, 0.03, 0.05, 0.07, 0.09, 0.11, 0.15], y_values=ys, z_values=zs)
    peak = pts.loc[pts.C.idxmax()]
    check(B, c, "concentration_peaks_on_the_source_line", abs(peak.x - SOURCE_X) < 1e-9 and peak.z <= 0.0041, peak_point_id=int(peak.point_id), peak_xyz=[float(peak.x), float(peak.y), float(peak.z)], C_ppm=float(peak.C),
          note="the line source lies at x = -0.15 m across the whole width; the highest mean concentration is the lowest point on that line (4 mm)")
    check(B, c, "WD0_flow_is_along_x", bool((afl.U > 0).all()) and float(pts.U[pts.z >= 0.09].mean()) > 0 and float(((pts.x - SOURCE_X) * pts.C).sum()) > 0, mean_U_at_z_at_least_0_09=float(pts.U[pts.z >= 0.09].mean()),
          C_weighted_mean_x_minus_source=float(((pts.x - SOURCE_X) * pts.C).sum() / pts.C.sum()), note="U > 0 in the approach flow and above the array; the plume is carried toward +x")
    # y-mirror pairs
    d = pts.assign(kx=pts.x.round(4), ky=pts.y.round(4), kz=pts.z.round(4))
    pos = d[d.ky > 0].set_index(["kx", "ky", "kz"])
    neg = d[d.ky < 0].assign(ky=lambda t: -t.ky).set_index(["kx", "ky", "kz"])
    j = pos.join(neg, lsuffix="_p", rsuffix="_n", how="inner")
    rel = lambda a: float(np.mean(np.abs(j[a + "_p"] - j[a + "_n"])) / np.mean(np.abs(j[a + "_p"])))   # noqa: E731
    top = j[j.index.get_level_values("kz") >= 0.15]
    check(B, c, "y_mirror_pairs_agree", max(rel("U"), rel("k")) < 0.1, warn=True, pairs=len(j), rel_mean_abs_diff_U=rel("U"), rel_mean_abs_diff_k=rel("k"), rel_mean_abs_diff_C=rel("C"), mean_abs_diff_T_K=float(np.mean(np.abs(j.T_p - j.T_n))),
          at_z_0_15_above_the_array={"pairs": len(top), "U_p_minus_U_n_mean_m_s": float((top.U_p - top.U_n).mean()), "T_p_minus_T_n_mean_K": float((top["T_p"] - top["T_n"]).mean())},
          note="the array and the line source are y-symmetric, but the +y and -y points of the same (x, |y|, z) differ by this much, also at z = 0.15 m, 0.09 m above the roofs, where the array's own asymmetry hardly reaches: the tunnel flow has a lateral gradient (U lower, T higher at +y); not a repeatability estimate")
    # line source: tracer flux per unit width through x stations against q / W
    qW = Q_GAS * 1e6 / 1.2
    rat = {}
    for x_ in (-0.03, 0.09, 0.21, 0.33):
        def flux(y_):
            s_ = pts[(pts.x == x_) & (pts.y == y_)].sort_values("z")
            if len(s_) < 8:
                return None
            g_ = (s_.U * s_.C + s_.uc).to_numpy()
            return X.trapezoid(np.r_[g_[0], g_], np.r_[0.0, s_.z.to_numpy()])
        street = [v_ for v_ in (flux(0.06), flux(-0.06)) if v_ is not None]
        col = flux(0.0)
        if col is not None and street:
            rat[x_] = 0.5 * (col + float(np.mean(street))) / qW
    check(B, c, "line_source_flux_is_recovered_in_the_cross_sections", len(rat) == 4 and all(0.67 < v_ < 1.5 for v_ in rat.values()), flux_over_q_per_width_by_x=rat, q_per_width_ppm_m2_s=qW,
          note="(U C + u'c') integrated over z <= 0.15 m on the cube-column line (y = 0) and the street lines (y = +-0.06, equal widths), averaged, over q / 1.2 m: 0.86 .. 1.0 at four stations; the column line alone carries 0.2 .. 0.4 of it and the street lines 1.3 .. 1.9. This fixes q, the unit ppm and the 1.2 m source width independently of c0")
    # signs of the turbulent fluxes in an unstable boundary layer: heat flows up (w'theta' > 0), the air cools with height, momentum flows down (u'w' < 0)
    t_drop = bool((afw.sort_values("z")["T"].diff().dropna() < 0).all())
    check(B, c, "turbulent_flux_signs_are_those_of_an_unstable_layer", bool((afw.wT > 0).all()) and t_drop and float((afw.uw < 0).mean()) >= 0.9 and float((pts.wT > 0).mean()) >= 0.9 and float((pts.uw.dropna() < 0).mean()) >= 0.8,
          approach_flow_wT_positive_fraction=float((afw.wT > 0).mean()), approach_flow_T_decreases_with_height=t_drop, approach_flow_uw_negative_fraction=float((afw.uw < 0).mean()),
          points_wT_positive_fraction=float((pts.wT > 0).mean()), points_uw_negative_fraction=float((pts.uw < 0).mean()), note="w'theta' > 0 (upward heat flux over the heated floor), T falls with z, u'w' < 0: the signs the published columns must have if they are in the usual convention")
    # inflow
    u_at_H = float(np.interp(math.log(H), np.log(afl.z), afl.U))
    check(B, c, "U_H_from_profile_matches_stated", abs(u_at_H - U_H_STATED) < 0.05 and abs(u_at_H - uH) < 0.01, U_H_profile=u_at_H, U_H_stated=U_H_STATED, U_H_workbook=uH)
    afd = {"U": ("U", 2), "u_rms": ("su", 3), "t_rms": ("T_rms", 3), "uv": ("uv", 4), "uw": ("uw", 4)}
    wafc = {"U": [r[5] for r in inf], "u_rms": [r[8] for r in inf], "t_rms": [r[13] for r in inf], "uv": [r[17] for r in inf], "uw": [r[18] for r in inf]}
    afres = {k_: X.within_half_unit(afc[k_].to_numpy(), np.array(wafc[k_]), d_[1]) for k_, d_ in afd.items()}
    check(B, c, "approach_flow_csv_equals_workbook_inflow_rounded", all(v_[1] == 0 for v_ in afres.values()) and len(inf) == len(afc) == 25, rows=len(inf), per_column={k_: {"max_abs_diff": v_[0], "cells_beyond_half_a_unit": v_[1]} for k_, v_ in afres.items()})
    fit = B.log_law_fit(afl.z, afl.U, 0.02, 0.32)
    inflow = {"U_H_m_s": round(u_at_H, 4), "U_H_stated_m_s": U_H_STATED, "U_H_workbook_m_s": uH, "H_m": H, "turbulence_intensity_at_H": round(float(np.sqrt(afl[np.isclose(afl.z, H)].uu.iloc[0])) / u_at_H, 4),
              "log_law": {**fit, "error_at_H_rel": round(B.log_law_U(fit, H) / u_at_H - 1, 4), "note": "unstably stratified: a neutral log law is only a rough description (see rms_residual_rel)"},
              "power_law": B.power_law_fit(afl.z, afl.U, 0.02, 0.32), "method": f"least squares, kappa = {B.KAPPA}, z = 0.02 .. 0.32 m (about 5 H) on the workbook's Inflow sheet (CSV = its rounding)",
              "stratification": {"floor_temperature_degC": round(thf, 4), "air_temperature_at_H_degC": round(thH, 4), "delta_theta_K": round(dth, 4), "approach_mean_temperature_degC": round(K["<θ0> (oC)"], 4), "gas_temperature_degC": K["<θgas> (oC)"],
                                 "building_mean_surface_temperature_degC_workbook": round(K["<θbuild> (oC)"], 4), "bulk_Richardson_number_workbook": K["Rb"], "profile": "cases/L/approach_flow_full.csv (T, T_rms, uT, vT, wT per height)"}}
    unc = sum(1 for sh_ in wb.values() for row_ in sh_ for v_ in row_ if isinstance(v_, str) and ("ncertaint" in v_ or "Ue(" in v_))
    check(B, c, "workbook_carries_no_expanded_uncertainty", unc == 0, warn=True, cells_mentioning_uncertainty=unc, sheets=list(wb), note="the data paper says the legacy file of Case J lists the expanded uncertainty; Case L's workbook does not (nor does K's)")

    frame = {"origin": "bottom centre of the windward wall of the 9th row (of 14) of the central column: x = 0 is that wall, y = 0 the centre line of the central column", "x": "+x streamwise (the wind blows toward +x); row k spans x in [0.12 (k-9), 0.12 (k-9) + 0.06]; 14 rows from x = -0.96 to 0.66",
             "y": "+y lateral; 9 columns, column centres at y = 0, +-0.12, ... +-0.48 (1.02 m of the 1.2 m tunnel)", "z": "+z up from the model floor (10 mm above the tunnel floor, data paper); cube tops at 0.06; heated floor at z = 0",
             "length_scale": "model metres (the sources state no model:full scale ratio); cube H = 0.06 m",
             "source": "floor line source across the tunnel between rows 7 and 8, centre x = -0.15 m; readme 0.037 m x 1.2 m, BD_caseL.stl patch 0.04 m x 1.02 m; 100 % ethylene, 500 cc/min (8.33e-6 m3/s) at 35 degC",
             "temperature": "T is degC (the CSV's 'T(K)' is degC); T_rms and heat fluxes are in K"}
    transform = {"coordinate_scale": 1.0, "lateral_sign": 1, "origin_shift_m": [0, 0, 0], "turbulence": "rms squared to variance", "temperature": "none for the points (the CSV is degC under a K header); AF: K -> degC (workbook)",
                 "note": "values from the workbook at full precision (the CSV is these rounded); no coordinate or sign change"}
    normalisation = {"concentration": {"c0_ppm": round(c0, 6), "definition": "c0 = Cgas q / (U_H H^2), Cgas = 1e6 ppm, q = 8.33333e-6 m3/s, U_H = 1.339415 m/s, H = 0.06 m", "source": "LF_caseL.xlsx cell <C0> (ppm); recomputed in check c0_from_Cgas_q_UH_H_equals_workbook",
                                      "rounded_readme_values_ppm": round(c0_paper, 3)},
                     "velocity": {"U_H_m_s": uH, "height_m": H}, "temperature": {"theta_f_degC": round(thf, 6), "delta_theta_K": round(dth, 6), "definition": "(T - T_f) / delta_theta"}}
    extra = {"normalisation": normalisation,
             "known_issues": {"RS_T_unit": "RS_caseL.csv 'T(K)' holds degrees Celsius (AF_caseL.csv's 'T(K)' is kelvin); the table carries degC for both",
                              "stl_bottom_faces": "BD_caseL.stl: the two bottom triangles (z = 0) of each of the 126 cubes (252 triangles) are wound inward; the served geometry.stl is the 126 boxes, outward",
                              "readme_file_names": "the readme's file list names AF_caseK.csv and RS_caseK.csv; the files are AF_caseL.csv and RS_caseL.csv",
                              "readme_building_temperature": "the readme's 'building surface temperature T_b = 14.8 degC' is the air temperature at H; the workbook's <θbuild> is 42.2 degC",
                              "source_size": "readme and data paper 0.037 m x 1.2 m; BD_caseL.stl patch 0.04 m x 1.02 m",
                              "not_mirror_symmetric": "the +y and -y halves differ in U, T and C by far more than a repeatability: the tunnel flow has a lateral gradient",
                              "no_expanded_uncertainty": "the workbook carries none",
                              "csv_rounding": "the CSV is the workbook rounded to 2-4 decimals (heat flux 4 dp); the table carries the workbook values",
                              "af_order": "AF_caseL.csv lists the profile from the top (z = 0.32 m) down; the table is ascending",
                              "data_paper_columns_rows": "the data paper's '9 rows by 14 columns' is 14 rows along x by 9 columns across y"},
             "not_carried": {"tc": "<θ'c'> (CSV 'tc', K ppm): temperature-concentration covariance; no column in the schema (QUESTIONS.md QL5)", "Usc": "workbook 'Usc' = |mean velocity| (derived)"},
             "extra_files": {"approach_flow_full": {"file": "cases/L/approach_flow_full.csv", "columns": list(afw.columns), "units": ["m", "m", "m/s", "m/s", "m/s", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "m2/s2", "degC", "K", "K m/s", "K m/s", "K m/s"],
                                                    "rows": len(afw), "source": "LF_caseL.xlsx 'Inflow' (x = -0.4 m)"}},
             "source_patch_stl": {"bbox_min": sst["bbox_min"], "bbox_max": sst["bbox_max"], "triangles": sst["triangles"]},
             "line_source_flux_over_q_per_width": {str(k_): round(v_, 3) for k_, v_ in rat.items()},
             "mirror_pairs": {"pairs": len(j), "rel_mean_abs_diff": {"U": rel("U"), "k": rel("k"), "C": rel("C")}},
             "layout": {"locations_by_number_of_heights": census}}
    return pts, afl, geo, X.sig(inflow, 10), frame, transform, X.sig(extra, 10)
