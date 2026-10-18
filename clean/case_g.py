"""Case G — field observation of the flow behind the Tsuiji-matsu tree belt (Izumo, Japan).

    META   the clean/build.py CASES["G"] entry
    build(B, prov)   B is the clean/build.py module; returns what build_A..build_E return:
                     (points, approach flow, geometry, inflow, frame, transform, extra)

Source files (raw/cases/case-g/, Zenodo 10.5281/zenodo.15589666): RS_caseG.csv (28 points, U/UH and k/UH^2),
AF_caseG.csv (the approach profile, U/Ub and k/Ub^2), LF_caseG.xls (legacy workbook, the same 28 values at full
precision, plus the inflow notes of the Guidebook), MP-y_caseG.png (the measurement points), readme_caseG.md.

Case G is a FIELD observation: full-scale metres, no model, and nothing is published in m/s. The table carries
the published normalised quantities (velocity_ratio = U/UH, k_ratio = k/UH^2) and nothing else.
"""
from __future__ import annotations

import math
import os
import re

import numpy as np
import pandas as pd

from case_ghi_common import directions_table

H_TREE, WIDTH, DEPTH, GAP = 7.0, 74.0, 2.0, 1.2          # readme / data paper section 3.7
LINES_OVER_H = [0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]       # readme: measurement lines behind the tree
HEIGHTS = [1.5, 3.0, 4.5, 6.0]                            # data paper section 3.7 (the readme says 1.5, 3, 6, 9)
ALPHA_STATED = 0.22                                       # readme: power-law index of the approach flow

META = {
    "title": "Case G — flow behind a tree belt (field observation)", "folder": "raw/cases/case-g",
    "zenodo_concept": "10.5281/zenodo.15589666", "zenodo_version": None,   # the readme names only this record
    "H": H_TREE, "width": WIDTH, "depth": DEPTH, "gap": GAP, "scale": None, "full_scale": True,
    "contact": "Yoshihide Tominaga <tominaga@abe.niit.ac.jp>",
    "collectors": ["Yasuo Kurotani (Shimane University)", "Nobuyoshi Kiyota (Hiroshima Institute of Technology)"],
    "citation": "Kurotani, Y., Kiyota, N., Kobayashi, S. (2001). Windbreak effect of Tsuijimatsu in Izumo Part. 2. Summaries of technical papers of Annual Meeting, Architectural Institute of Japan, D-2 Environmental engineering II, 745-746 (in Japanese).",
    "normalisation": ("velocity_ratio = U/UH and k_ratio = k/UH^2, UH = the mean wind speed at the tree height z = 7 m, measured during "
                      "each measurement period and interpolated with the approach flow's power law (index 0.22); no absolute speed is "
                      "published. The approach-flow table carries U/Ub and k/Ub^2 instead (Ub = U at 9 m, a different day): "
                      "divide by UH/Ub = 0.946 (power law) to put it on the table's normalisation."),
}

INSTRUMENT = "sonic_anemometer"
QUANTITY = {INSTRUMENT: ["velocity_ratio", "k_ratio"]}


def _box():
    return {"min": [-DEPTH, -WIDTH / 2, GAP], "max": [0.0, WIDTH / 2, H_TREE]}


def flow(cfg, inst, wd):
    return (1.0, 0.0,
            "definition: the readme puts the measurement lines BEHIND the belt, on +x of its leeward face (MP_caseG.png); "
            "the field wind direction relative to the belt normal is not published",
            "unverified — field data: the angle between the wind and the belt normal is not published (QUESTIONS.md QG3)")


def directions(B, pts):
    return directions_table("G", pts, QUANTITY, flow)


def build(B, prov):
    c = "G"
    folder = os.path.join(B.REPO, META["folder"])
    rs, af, lf = (os.path.join(folder, n) for n in ("RS_caseG.csv", "AF_caseG.csv", "LF_caseG.xls"))
    prov[c] = [rs, af, lf, os.path.join(folder, "readme_caseG.md"), os.path.join(folder, "MP-y_caseG.png")]

    header, rows = B.read_csv_rows(rs)
    B.log(f"[G] RS_caseG.csv header (bare): {header}; no point numbers, no variances: only U/UH and k/UH^2 (both published as ratios)")
    ix = {h: i for i, h in enumerate(header)}
    csv_rows = [(B.num(r[ix["X"]]), B.num(r[ix["Z"]]), B.num(r[ix["U/UH"]]), B.num(r[ix["k/UH^2"]])) for r in rows]

    # the workbook holds the same 28 values at full precision (the CSV rounds U/UH to 3 dp and k/UH^2 to 4 dp)
    wb = B.xls(lf)
    sh = wb.sheet_by_name("results")
    xh = [float(sh.cell_value(3, k)) for k in range(2, 9)]
    u_wb = {(i, float(sh.cell_value(r, 1))): float(sh.cell_value(r, 2 + i)) for i in range(7) for r in range(4, 8)}
    k_wb = {(i, float(sh.cell_value(r, 1))): float(sh.cell_value(r, 2 + i)) for i in range(7) for r in range(12, 16)}
    out, mx_u, mx_k, mx_x = [], 0.0, 0.0, 0.0
    for n, (x, z, u, k) in enumerate(csv_rows, start=1):
        i = int(np.argmin([abs(x - h * H_TREE) for h in xh]))
        mx_x = max(mx_x, abs(x - xh[i] * H_TREE))
        uw, kw = u_wb[(i, z)], k_wb[(i, z)]
        mx_u, mx_k = max(mx_u, abs(u - uw)), max(mx_k, abs(k - kw))
        out.append(B.row(case_id=c, instrument=INSTRUMENT, campaign="field", point_id=n, x=x, y=0.0, z=z, velocity_ratio=uw, k_ratio=kw))
    log_note = ("[G] transform: U/UH and k/UH^2 taken from LF_caseG.xls 'results' (full precision); RS_caseG.csv agrees to its own rounding "
                f"(max |dU/UH| {mx_u:.1e}, max |dk/UH^2| {mx_k:.1e}); the workbook's X/H x 7 m reproduces the CSV's X (max |dx| {mx_x:.1e} m); "
                "point numbers are the CSV's row order (1-28); y = 0 (the vertical section at the centre of the belt)")
    B.log(log_note)
    pts = pd.DataFrame(out, columns=B.POINT_COLUMNS)

    h, ar = B.read_csv_rows(af)
    ai = {n: i for i, n in enumerate(h)}
    afl = pd.DataFrame([{"case_id": c, "z": B.num(r[ai["Z"]]), "U": B.num(r[ai["U/Ub"]]), "uu": math.nan, "vv": math.nan, "ww": math.nan,
                         "k": B.num(r[ai["k/Ub^2"]])} for r in ar])
    B.log("[G] approach flow: AF_caseG.csv, 4 heights, U/Ub and k/Ub^2 carried as published: the U and k columns of this case's "
          "approach-flow table are DIMENSIONLESS (Ub = U at 9 m = 1); no absolute speed is published")

    # the workbook's Geometry sheet carries the Guidebook's inflow notes as text
    notes = [str(wb.sheet_by_name("Geometry").cell_value(r, 1)) for r in range(14, 21)]
    K_txt = next((t for t in notes if t.startswith("K=")), "")
    K_wb = float(re.search(r"K=([0-9.]+)", K_txt).group(1)) if K_txt else math.nan
    B.log(f"[G] workbook 'Geometry' sheet inflow notes: {[t for t in notes if t.strip()]}")

    box = _box()
    geo = [("default", [box], "generated from the readme's stated dimensions (74 m along y, 2 m along x, 7 m high, 1.2 m bottom gap), "
            "centred on y = 0 with its leeward face at x = 0 (MP_caseG.png). A porous canopy: the data paper gives a "
            "shading rate of 81 % after pruning (section 3.7); the box is its envelope")]

    # ---- checks
    B.check(c, "row_count_7_lines_x_4_heights", len(pts) == 28, rows=len(pts), expected=28, source="readme / data paper section 3.7")
    B.check(c, "point_ids_are_the_csv_row_order_1_to_28", sorted(pts.point_id) == list(range(1, 29)),
            rows=len(pts), min_point_id=int(pts.point_id.min()), max_point_id=int(pts.point_id.max()), distinct_point_ids=int(pts.point_id.nunique()))
    xs = sorted(pts.x.unique())
    B.check(c, "measurement_lines_are_the_readme_multiples_of_H", all(abs(a - h * H_TREE) < 1e-9 for a, h in zip(xs, LINES_OVER_H)) and len(xs) == 7,
            lines_m=xs, expected_m=[h * H_TREE for h in LINES_OVER_H], note="readme: 0.25H, 0.5H, 1.0H, 2.0H, 3.0H, 4.0H, 5.0H behind the tree, H = 7 m")
    zs = sorted(pts.z.unique())
    B.check(c, "heights_are_1.5_3_4.5_6_as_the_paper_and_the_drawing_say", zs == HEIGHTS, heights_m=zs,
            note="the readme lists the heights of the lee measurement as 1.5, 3.0, 6.0, 9.0 m (a copy of the approach-flow heights); the CSV, the workbook, "
                 "MP_caseG.png and the data paper (section 3.7) all say 1.5, 3, 4.5, 6 m. QUESTIONS.md QG1")
    inside_envelope = int(B.points_in_boxes(pts[["x", "y", "z"]].to_numpy(), [box]).sum())
    B.check(c, "no_sensor_inside_the_canopy_envelope", inside_envelope == 0, points=len(pts), inside=inside_envelope)
    shifted = np.column_stack([pts.x.to_numpy() - 3.0, pts.y.to_numpy(), pts.z.to_numpy()])
    B.check(c, "control_points_shifted_3m_upwind_are_detected_inside", int(B.points_in_boxes(shifted, [box]).sum()) == 4,
            inside_after_shift=int(B.points_in_boxes(shifted, [box]).sum()), shift_m=[-3.0, 0, 0], note="the 0.25H line (x = 1.75 m, four heights) lands at x = -1.25 m inside the belt; the other lines land at x >= 0.5 m, outside")
    cells = pts[["x", "y", "z", "velocity_ratio", "k_ratio"]]
    B.check(c, "no_sentinels_or_nan", not cells.isna().any().any(), cells=int(cells.size), nan_cells=int(cells.isna().sum().sum()), min_value=float(cells.min().min()))
    B.check(c, "csv_agrees_with_workbook_to_the_csv_rounding", mx_u <= 5.0e-4 + 1e-9 and mx_k <= 5.0e-5 + 1e-9 and mx_x < 1e-9, max_abs_dU_over_UH=mx_u,
            max_abs_dk_over_UH2=mx_k, max_abs_dx_m=mx_x, note="RS_caseG.csv rounds U/UH to 3 dp and k/UH^2 to 4 dp; the workbook is the value released here")

    # approach flow
    z, U, k = afl.z.to_numpy(), afl.U.to_numpy(), afl.k.to_numpy()
    B.check(c, "approach_flow_unity_at_9m_by_definition", bool(np.isclose(U[z == 9.0], 1.0).all()) and len(afl) == 4, U_over_Ub_at_9m=float(U[z == 9.0][0]))
    pl = B.power_law_fit(z, U, 1.5, 9.0)
    B.check(c, "approach_flow_power_law_index_matches_the_stated_0.22", abs(pl["alpha"] - ALPHA_STATED) < 0.03, fitted=pl["alpha"], stated=ALPHA_STATED, fit=pl,
            note="4 heights published to 2 dp, so the fitted index carries about +/-0.01 of rounding alone")
    uh_pl = (H_TREE / 9.0) ** ALPHA_STATED
    uh_li = B.interp_log(z, U, H_TREE)
    B.check(c, "UH_over_Ub_from_the_stated_power_law_and_from_the_profile_agree_within_1pct", abs(uh_pl / uh_li - 1) < 0.01, UH_over_Ub_power_law_022=uh_pl,
            UH_over_Ub_log_interpolation=uh_li, UH_over_Ub_fitted_index=(H_TREE / 9.0) ** pl["alpha"])

    # the lee side against the approach flow, on the table's normalisation (U/UH)
    app_u = (pts.z.to_numpy() / H_TREE) ** ALPHA_STATED              # U/UH of the approach flow at the point's height
    shelter = pts.velocity_ratio.to_numpy() / app_u
    B.check(c, "belt_shelters_every_point_below_the_approach_speed", bool((shelter < 1.0).all()), max_ratio_to_approach=float(shelter.max()),
            min_ratio_to_approach=float(shelter.min()), ratio_at_5H=[round(float(v), 3) for v in shelter[pts.x.to_numpy() == 35.0]],
            note="U/UH divided by the approach flow's U/UH at the same height (power law 0.22): every lee point is slower")
    far = pts[pts.x == 35.0]
    # turbulence: approach k/UH^2 against the lee k/UH^2 at 5H
    k_app_UH2 = np.interp(far.z.to_numpy(), z, k) / uh_pl ** 2
    k_ratio_far = far.k_ratio.to_numpy() / k_app_UH2
    B.check(c, "far_lee_turbulence_recovers_to_at_least_half_the_approach_flow", bool((k_ratio_far > 0.5).all()), warn=True,
            k_over_UH2_at_5H=[round(float(v), 4) for v in far.k_ratio], k_over_UH2_approach=[round(float(v), 4) for v in k_app_UH2],
            ratio=[round(float(v), 3) for v in k_ratio_far], heights_m=far.z.tolist(),
            note="the approach profile (120 min record, 28 Dec 2000) has k/UH^2 = 0.26-0.31 at these four heights; five tree heights behind the belt (10 min records, 26 Dec 2000) it is 0.040-0.072, "
                 "3-8 times lower, at every height. Different days and averaging times; not resolvable from the files. QUESTIONS.md QG2")
    ub_implied = math.sqrt(K_wb / float(k[z == 9.0][0])) if K_wb == K_wb else math.nan
    B.check(c, "workbook_inflow_K_is_3.02_and_implies_Ub_3.9_ms", abs(K_wb - 3.02) < 1e-9, K_m2_s2=K_wb, k_over_Ub2_at_9m=float(k[z == 9.0][0]), implied_Ub_m_s=ub_implied,
            note="DERIVED, not published: if the Guidebook's inflow K = 3.02 m2/s2 is the k at 9 m, Ub = sqrt(K / 0.2) = 3.89 m/s. QUESTIONS.md QG4")

    inflow = {"U_ref": "Ub = mean wind speed of the approach flow at 9.0 m (not published in m/s)", "z_ref_m": 9.0, "U_ref_basis": "AF_caseG.csv is U/Ub and k/Ub^2",
              "UH_over_Ub_power_law_0.22": round(uh_pl, 6), "UH_over_Ub_log_interpolation": round(uh_li, 6),
              "power_law": pl, "power_law_index_stated": ALPHA_STATED,
              "lee_normalisation": "RS_caseG.csv: UH = mean speed at 7 m during each measurement period (interpolated with the approach flow's power law)",
              "approach_date": "28 Dec 2000 (120 min, 5 Hz, 1.5/3/6/9 m)", "lee_date": "26 Dec 2000 (10 min or more, 5 Hz, 1.5/3/4.5/6 m)",
              "workbook_inflow_notes": {"U(z)": "Ub (z/Hb)^0.22", "K_m2_s2": K_wb, "implied_Ub_m_s_if_K_is_k_at_9m": round(ub_implied, 4), "status": "derived, unverified"}}
    frame = {"origin": "the leeward face of the tree belt at ground level, on the vertical section through the belt's centre (MP_caseG.png)",
             "x": "+x downwind: the belt occupies x in [-2, 0] m and the measurement lines lie behind it at x = 1.75 ... 35 m",
             "y": "+y along the belt (74 m long, y in [-37, 37]); every point is on y = 0, the centre section",
             "z": "+z up from the ground; the belt spans z in [1.2, 7] (1.2 m bottom gap); points at z = 1.5, 3, 4.5, 6 m",
             "wind_direction_rotation": "single direction: the wind blows toward +x (perpendicular to the belt); the field angle is not published",
             "length_scale": "FULL-scale metres: a field observation, no model"}
    transform = {"coordinate_scale": 1.0, "lateral_sign": 1, "origin_shift_m": [0, 0, 0],
                 "note": "U/UH and k/UH^2 from the workbook at full precision; coordinates as published; approach flow as published (U/Ub, k/Ub^2)"}
    known = {"readme_heights": {"readme": [1.5, 3.0, 6.0, 9.0], "table": zs}, "k_far_lee_vs_approach": {"ratio_at_5H": [round(float(v), 3) for v in k_ratio_far]}}
    return pts, afl, geo, inflow, frame, transform, {"known_issues": known}
