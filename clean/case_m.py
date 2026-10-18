"""Case M — tracer-gas release on the TPU Atsugi campus (wind tunnel 1/600 + 18 field runs).

One module per case: META is this case's entry of build.CASES, build(B, prov) returns what build_A..build_E
return (points, approach flow, geometry, inflow, frame, transform, extra), directions(B, pts) the rows of
directions.csv. B is the clean/build.py module; nothing of it is duplicated here.

Sources (raw/cases/case-m/, the Zenodo files as published): RS-WT_caseM.csv (tunnel velocity and concentration,
2 dp / 1 dp), RS-FO_caseM.csv (18 field runs, concentration in ppq), LC_caseM.csv and MP_caseM.png (points, source,
reference point), AF_caseM.csv, BD_caseM.stl (model scale) and LF_caseM.xlsx, the legacy workbook, which holds the
same tunnel and field numbers at full precision (read here with the standard library: openpyxl is not in the build
environment and xlrd 2.x cannot read .xlsx).
"""
from __future__ import annotations

import math
import os
import re
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

SCALE = 600.0               # model 1:600 (readme, data paper 3.13.1); the case frame is FULL scale
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
PPQ = 1e-9                  # 1 ppq = 1e-15 volume fraction = 1e-9 ppm

META = {
    "title": "Case M — flow and dispersion within the TPU Atsugi campus", "folder": "raw/cases/case-m",
    "zenodo_concept": "10.5281/zenodo.15487857", "zenodo_version": None,   # the readme and the data paper name one DOI
    "scale": 600, "status": "released", "status_note": None,
    "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    "collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Takumi Tachibana (Wind Engineering Institute)"],
    "citation": ("Tachibana, T., Yoshie, R., Nakayama, S., Kishida, T., Miyashita, K., Sasaki, R. (2022). Comparison between field measurement and wind tunnel "
                 "experiments of gas dispersion in an urban area and verification of similarity law. Journal of Wind Engineering 47(3), 39-52 (in Japanese). "
                 "http://dx.doi.org/10.5359/jwe.47.39"),
}


def _xlsx(path):
    """{sheet name (stripped): {row: {col: value}}} of an .xlsx with the standard library; 0-based rows and columns."""
    z = zipfile.ZipFile(path)
    ss = [("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"]))) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
    rid = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", NS):
        root = ET.fromstring(z.read("xl/" + rid[s.get("{%s}id" % NS["r"])].lstrip("/").replace("xl/", "")))
        rows = {}
        for c in root.iter("{%s}c" % NS["m"]):
            m = re.match(r"([A-Z]+)(\d+)", c.get("r"))
            col = 0
            for ch in m.group(1):
                col = col * 26 + ord(ch) - 64
            v = c.find("m:v", NS)
            t = c.get("t")
            if t == "s":
                val = ss[int(v.text)]
            elif v is None:
                continue
            elif t in ("str", "e"):
                val = v.text
            else:
                val = float(v.text)
            rows.setdefault(int(m.group(2)) - 1, {})[col - 1] = val
        out[s.get("name").strip()] = rows
    return out


def _surface_z(T: np.ndarray, x: float, y: float):
    """Elevations of every triangle surface met by the vertical line through (x, y), ascending, and the sign of each facet's normal z."""
    a, b, c = T[:, 0, :2], T[:, 1, :2], T[:, 2, :2]
    d = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(d) > 1e-12
    dd = np.where(ok, d, 1.0)
    l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / dd
    l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / dd
    l3 = 1.0 - l1 - l2
    ins = ok & (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
    z = (l1 * T[:, 0, 2] + l2 * T[:, 1, 2] + l3 * T[:, 2, 2])[ins]
    nz = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])[:, 2][ins]
    o = np.argsort(z, kind="mergesort")
    return z[o], np.sign(nz[o])


def _orientation(T: np.ndarray):
    """(horizontal facets facing down, facing up): outward normals of a terrain-plus-buildings surface point up on every ground and roof facet."""
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(n, axis=1)
    flat = (ln > 0) & (np.abs(n[:, 2]) > 0.9999 * ln)
    return int((flat & (n[:, 2] < 0)).sum()), int((flat & (n[:, 2] > 0)).sum())


def build(B, prov):
    c = "M"
    folder = os.path.join(B.REPO, META["folder"])
    P = {n: os.path.join(folder, n) for n in ("RS-WT_caseM.csv", "RS-FO_caseM.csv", "AF_caseM.csv", "LC_caseM.csv", "MP_caseM.png", "BD_caseM.stl", "LF_caseM.xlsx", "readme_caseM.md")}
    prov[c] = list(P.values())
    wbk = _xlsx(P["LF_caseM.xlsx"])
    check = B.check

    # ------------------------------------------------------------------ the legacy workbook (full precision)
    mp = wbk["Measurement  Point".strip()]
    pts_xyz = {int(r[18]): (r[19], r[20], r[21]) for r in mp.values() if isinstance(r.get(18), float) and 1 <= r[18] <= 15}
    special = {str(r[18]).strip().replace("\n", " "): (r[19], r[20], r[21]) for r in mp.values() if isinstance(r.get(18), str) and isinstance(r.get(19), float)}
    wt = wbk["Wind tunnel experiment"]
    pars = {r[0]: r for r in wt.values() if isinstance(r.get(0), str)}           # H, UH, r, q, C0 ... : the experiment's parameters
    H_R, U_R, D_src, q_wt, C0 = (pars[k][2] for k in ("H", "UH", "r", "q", "C0"))
    hdr = [int(re.sub(r"\D", "", str(wt[2][i]))) for i in (7, 13, 15, 17)]       # wind directions of the column groups: u v w ... | 175 | 180 | 185
    first, normalised, in_norm = [], [], False
    for ri in sorted(wt):
        r = wt[ri]
        in_norm = in_norm or r.get(6) == "Normalized values"
        if isinstance(r.get(6), float) and 1 <= r[6] <= 15 and isinstance(r.get(7), float):
            (normalised if in_norm else first).append(r)
    tun = {int(r[6]): r for r in first}
    norm_tab = {int(r[6]): r for r in normalised}
    fm = wbk["Field Measurement"]
    runs = {}
    star = {}
    seen_norm = False
    for ri in sorted(fm):
        r = fm[ri]
        if isinstance(r.get(2), str) and "Normalized Concentration" in r[2]:
            seen_norm = True
        if isinstance(r.get(1), float) and isinstance(r.get(2), float):
            if seen_norm:
                star[int(r[1])] = [r[2 + p] for p in range(15)]
            else:
                runs[int(r[1])] = {"C_ppq": [r[2 + p] for p in range(15)], "U_R": r[18], "WD_R": r[19], "q": r[20]}
    H_field = 41.0                                                              # 'Reference Hight H [m]' of the sheet, once, in run 1's row
    for run, v in runs.items():
        v["c0_ppq"] = v["q"] / (v["U_R"] * H_field ** 2) * 1e15

    # ------------------------------------------------------------------ rows
    h, rows = B.read_csv_rows(P["RS-WT_caseM.csv"])
    ix = {n: i for i, n in enumerate(h)}
    B.log(f"[M] RS-WT_caseM.csv header (bare): {h}; -999.9 = not measured (velocities at 175 and 185 deg); coordinates MODEL-scale metres (1/600), z above the tunnel floor")
    csv_wt = {(int(B.num(r[ix['No.']])), int(B.num(r[ix['WD']]))): {n: B.num(r[ix[n]]) for n in h if n not in ("No.", "WD")} for r in rows}
    out = []
    for p in range(1, 16):
        x, y, z = (v * SCALE for v in pts_xyz[p])
        r = tun[p]
        uu, vv, ww = r[10] ** 2, r[11] ** 2, r[12] ** 2
        out.append(B.row(case_id=c, instrument="split_fibre", point_id=p, wind_direction_deg=180.0, x=x, y=y, z=z, U=r[7], V=r[8], W=r[9], uu=uu, vv=vv, ww=ww, k=0.5 * (uu + vv + ww)))
        for wd, ci in ((175, 13), (180, 15), (185, 17)):
            out.append(B.row(case_id=c, instrument="hydrocarbon_analyser", point_id=p, wind_direction_deg=float(wd), x=x, y=y, z=z, C=r[ci], c_rms=r[ci + 1], concentration_ratio=r[ci] / C0))
    B.log(f"[M] source: LF_caseM.xlsx 'Wind tunnel experiment' (full precision; RS-WT_caseM.csv is the same numbers rounded to 2 dp / 1 dp, checked): <u>, <v>, <w>, sigma_u, sigma_v, sigma_w at 180 deg "
          f"(split fibre) and <c>, sigma_c at 175, 180 and 185 deg (hydrocarbon analyser). sigma -> variance (sigma^2); k = (uu+vv+ww)/2 from those (the CSV's k is half the sum of the 2-dp RMS values)")
    B.log(f"[M] transform: tunnel x, y, z model metres x {SCALE:g} -> full-scale metres; velocities in the tunnel's m/s, concentration in the tunnel's ppm (not scaled); concentration_ratio = C / c0, c0 = q / (U_R H_R^2) = {C0:.6f} ppm (workbook C0)")
    for run in sorted(runs):
        v = runs[run]
        for p in range(1, 16):
            x, y, z = (a * SCALE for a in pts_xyz[p])
            out.append(B.row(case_id=c, instrument="sorbent_gc_ecd", campaign="field", run=str(run), point_id=p, wind_direction_deg=v["WD_R"], x=x, y=y, z=z,
                             C=v["C_ppq"][p - 1] * PPQ, concentration_ratio=v["C_ppq"][p - 1] / v["c0_ppq"]))
    B.log("[M] source: LF_caseM.xlsx 'Field Measurement' (RS-FO_caseM.csv is the same concentrations and the run conditions rounded). transform: C in PARTS PER QUADRILLION (1e-15) -> ppm x 1e-9; "
          "concentration_ratio = C / c0 with the RUN's own c0 = q_run / (U_R,run x 41 m^2); wind_direction_deg = the run's mean wind direction at the reference point (WD_R); points = the tunnel's 15 (x600)")
    pts = pd.DataFrame(out, columns=B.POINT_COLUMNS)
    SF = pts[pts.instrument == "split_fibre"]
    HA = pts[pts.instrument == "hydrocarbon_analyser"]
    FD = pts[pts.instrument == "sorbent_gc_ecd"]

    # ------------------------------------------------------------------ approach flow (workbook, full precision)
    af = wbk["Approaching flow"]
    arows = [r for ri, r in sorted(af.items()) if isinstance(r.get(1), float) and isinstance(r.get(3), float)]
    afl = pd.DataFrame([{"case_id": c, "z": r[3] * SCALE, "U": r[4], "uu": r[7] ** 2, "vv": r[8] ** 2, "ww": r[9] ** 2, "k": 0.5 * (r[7] ** 2 + r[8] ** 2 + r[9] ** 2)} for r in arows])
    B.log(f"[M] approach flow: LF_caseM.xlsx 'Approaching flow' ({len(arows)} heights at x = {arows[0][1]} m, y = 0, z above the tunnel floor), z x {SCALE:g} -> full scale; sigma -> variance; k = (uu+vv+ww)/2; the published V, W and <u'w'> are not carried")
    ah, ar = B.read_csv_rows(P["AF_caseM.csv"])
    aix = {n: i for i, n in enumerate(ah)}

    # ------------------------------------------------------------------ geometry: model scale, wound inward
    raw = B.read_ascii_stl(P["BD_caseM.stl"])
    Tm = np.array(raw)
    down0, up0 = _orientation(Tm)
    s_raw = B.stl_stats(raw)
    tris = [tuple(tuple(float(v) * SCALE for v in p) for p in t) for t in raw]
    if down0 > up0:
        tris = [(a, c_, b) for a, b, c_ in tris]
    T = np.array(tris)
    down1, up1 = _orientation(T)
    s_geo = B.stl_stats(tris)
    B.log(f"[M] geometry: BD_caseM.stl is MODEL scale (bbox x ±0.9 m, y ±0.6 m, z 0 ... 0.1082 m; z = 0 is the tunnel floor); scaled x {SCALE:g}; horizontal ground/roof facets face DOWN as published "
          f"({down0} down, {up0} up): the surface is wound inward, all triangles reversed ({down1} down, {up1} up now); stats {s_geo}")
    geo = [("default", None, tris, f"BD_caseM.stl (Zenodo; terrain + buildings of the Atsugi campus) scaled x{SCALE:g} from model to full-scale metres and re-wound outward; {s_geo['triangles']} triangles, one shell, "
            f"{s_geo['edges_boundary']} boundary and {s_geo['edges_non_manifold']} non-manifold edges; z = 0 is the tunnel floor, the campus ground lies at z ~ 32 m")]

    # ------------------------------------------------------------------ checks: rows and cross-checks with the CSVs
    check(c, "workbook_column_groups_are_180_then_175_180_185", hdr == [180, 175, 180, 185], column_group_wind_directions=hdr)
    check(c, "row_counts", len(SF) == 15 and len(HA) == 45 and len(FD) == 270, split_fibre=len(SF), hydrocarbon_analyser=len(HA), sorbent_gc_ecd=len(FD),
          note="15 points: velocity at 180 deg; concentration at 175, 180, 185 deg; 18 field runs x 15 points")
    lh, lr = B.read_csv_rows(P["LC_caseM.csv"])
    li = {n: i for i, n in enumerate(lh)}
    lc = {r[li["No."]]: (B.num(r[li["x"]]), B.num(r[li["y"]]), B.num(r[li["Elevation"]]), r[li["Remarks"]]) for r in lr}
    dl = max(max(abs(lc[str(p)][0] - pts_xyz[p][0]), abs(lc[str(p)][1] - pts_xyz[p][1]), abs(lc[str(p)][2] - pts_xyz[p][2])) for p in range(1, 16))
    dl = max(dl, max(max(abs(lc[n][i] - special[w][i]) for i in range(3)) for n, w in (("Gas_source", "Tracer gas source"), ("Reference", "Reference point"), ("Origin", "Origin point (Ground surface)"))))
    check(c, "lc_csv_equals_the_workbook_points_at_4_dp", dl < 5.1e-5 and all(lc[str(p)][3].startswith("ground_surface+3m") for p in range(1, 16)), max_abs_diff_model_m=dl,
          remarks=sorted({lc[str(p)][3] for p in range(1, 16)}), note="LC_caseM.csv (4 dp) against the workbook's 'Measurement Point' sheet; the table carries the workbook's 8-digit coordinates (identical to RS-WT_caseM.csv)")
    xr = max(abs(csv_wt[(p, 180)]["x"] - pts_xyz[p][0]) for p in range(1, 16)) + max(abs(csv_wt[(p, 180)]["z"] - pts_xyz[p][2]) for p in range(1, 16))
    check(c, "rs_wt_coordinates_equal_the_workbook", xr < 1e-6, max_abs_diff_model_m=xr)
    check(c, "key_is_unique", not pts.duplicated(["config", "instrument", "point_id", "wind_direction_deg"]).any(), note="the 18 runs' mean directions WD_R are all different, which keeps the row key unique")
    dev = {n: 0.0 for n in ("U", "V", "W", "u_rms", "v_rms", "w_rms")}
    for p in range(1, 16):
        r = tun[p]
        cs = csv_wt[(p, 180)]
        for n, i in (("U", 7), ("V", 8), ("W", 9), ("u_rms", 10), ("v_rms", 11), ("w_rms", 12)):
            dev[n] = max(dev[n], abs(cs[n] - r[i]))
    dC = max(abs(csv_wt[(p, wd)][n] - tun[p][ci + j]) for p in range(1, 16) for wd, ci in ((175, 13), (180, 15), (185, 17)) for j, n in ((0, "C"), (1, "c_rms")))
    check(c, "tunnel_csv_is_the_workbook_rounded", max(dev.values()) <= 0.005 + 1e-9 and dC <= 0.05 + 1e-9, max_abs_diff_velocity_m_s=max(dev.values()), max_abs_diff_concentration_ppm=dC,
          note="RS-WT_caseM.csv rounds velocities and rms to 0.01 m/s and concentrations to 0.1 ppm; the workbook's values are carried")
    kd = max(abs(csv_wt[(p, 180)]["k"] - 0.5 * (csv_wt[(p, 180)]["u_rms"] ** 2 + csv_wt[(p, 180)]["v_rms"] ** 2 + csv_wt[(p, 180)]["w_rms"] ** 2)) for p in range(1, 16))
    kw = max(abs(csv_wt[(p, 180)]["k"] - SF[SF.point_id == p].k.iloc[0]) for p in range(1, 16))
    check(c, "csv_k_is_half_the_sum_of_the_2dp_rms_values_not_of_the_workbook_values", kd <= 5.1e-4 and kw > 1e-3, max_abs_k_csv_minus_half_sum_of_csv_rms_squared=kd, max_abs_k_csv_minus_k_from_workbook_sigmas=kw,
          note="RS-WT's k differs from (sigma_u^2 + sigma_v^2 + sigma_w^2)/2 of the full-precision workbook values by up to 0.005 m^2/s^2 (2.1 % of k at point 6); k here is computed from the workbook values")
    unm = sum(1 for p in range(1, 16) for wd in (175, 185) for n in ("U", "V", "W", "u_rms", "v_rms", "w_rms", "k") if math.isnan(csv_wt[(p, wd)][n]))
    check(c, "velocities_unmeasured_at_175_and_185", unm == 15 * 2 * 7, sentinel_cells=unm, note="-999.9 in all 7 velocity columns at 175 and 185 deg: velocity only at 180 deg, so no split_fibre rows exist for the other two")
    mx = max([abs(norm_tab[p][j] - tun[p][j] / U_R) for p in tun for j in (7, 8, 9, 10, 11, 12)] + [abs(norm_tab[p][j] - tun[p][j] / C0) for p in tun for j in (13, 14, 15, 16, 17, 18)])
    check(c, "workbook_normalised_table_is_value_over_UR_and_C0", mx < 1e-9, max_abs_diff=mx, U_R=U_R, C0=C0, note="'Normalized values' block of the workbook: <u>/UH ... and <c>/C0")
    c0_calc = q_wt / (U_R * H_R ** 2) * 1e6
    check(c, "c0_is_q_over_UR_HR2", abs(c0_calc - C0) < 1e-9 and abs(C0 / 133.0 - 1) < 0.005, c0_ppm=C0, q_m3_s=q_wt, U_R_m_s=U_R, H_R_m=H_R, c0_with_H_R_41_over_600=q_wt / (U_R * (41 / 600) ** 2) * 1e6, c0_data_paper_ppm=133.0,
          note="the workbook (and the paper's 1.33e2 ppm) use H_R = 0.068 m, 41 m / 600 = 0.06833 m would give 131.2 ppm (-1 %)")
    check(c, "tracer_flow_is_150_cc_per_min_and_exit_velocity_0.09_m_s", abs(q_wt - 150e-6 / 60) < 1e-12 and abs(q_wt / (math.pi * (D_src / 2) ** 2) - 0.09) < 0.005, q_m3_s=q_wt, exit_velocity_m_s=q_wt / (math.pi * (D_src / 2) ** 2),
          note="readme: ethylene at 100 %, 6 mm outlet, 150 cc/min = 2.5e-6 m^3/s, 0.09 m/s; the workbook labels the 6 mm 'r' (radius) but it is the diameter")
    neg = [(p, wd, round(tun[p][ci], 4)) for p in tun for wd, ci in ((175, 13), (180, 15), (185, 17)) if tun[p][ci] < 0]
    floor = sorted({round(tun[p][ci + 1], 2) for p in tun for wd, ci in ((175, 13), (180, 15), (185, 17)) if abs(tun[p][ci]) < 1.0})
    check(c, "tunnel_concentration_has_a_zero_offset_and_an_rms_floor", len(neg) == 2 and min(floor) > 7.0, warn=True, negative_means_ppm=neg, c_rms_where_the_mean_is_below_1_ppm=floor,
          note=f"two published means are negative (point 12) and wherever the mean is below 1 ppm the rms is still {min(floor):.1f} to {max(floor):.1f} ppm ({min(floor) / C0:.3f} to {max(floor) / C0:.2f} c0): an analyser baseline or rare puffs; kept as published")
    # field
    fh, fr = B.read_csv_rows(P["RS-FO_caseM.csv"])
    fi = {n: i for i, n in enumerate(fh)}
    mxC = max(abs(B.num(r[fi["C"]]) - runs[int(B.num(r[fi["Run"]]))]["C_ppq"][int(B.num(r[fi["No."]])) - 1]) for r in fr)
    dU = max(abs(B.num(r[fi["U_R"]]) - runs[int(B.num(r[fi["Run"]]))]["U_R"]) for r in fr)
    dW = max(abs(B.num(r[fi["WD_R"]]) - runs[int(B.num(r[fi["Run"]]))]["WD_R"]) for r in fr)
    dq = max(abs(B.num(r[fi["q"]]) / runs[int(B.num(r[fi["Run"]]))]["q"] - 1) for r in fr)
    check(c, "field_csv_agrees_with_the_workbook", len(fr) == 270 and mxC == 0 and dU < 0.0034 and dW < 0.034 and dq < 0.003, rows=len(fr), concentration_max_abs_diff_ppq=mxC, U_R_max_abs_diff=dU, WD_R_max_abs_diff_deg=dW, q_max_rel_diff=dq,
          note="the CSV rounds U_R to 0.01 m/s (the workbook's values are thirds), WD_R to 0.1 deg and q to 3 significant digits; the workbook values are carried")
    cs = max(abs(star[run][p] - runs[run]["C_ppq"][p] / runs[run]["c0_ppq"]) for run in runs for p in range(15))
    check(c, "workbook_field_C_star_is_C_over_the_runs_c0", cs < 1e-9, max_abs_diff=cs, H_R_field_m=H_field, note="'Normalized Concentration' block: C* = C / c0, c0 = q / (U_H H^2) with each run's q and U_H and H = 41 m")
    qs = [v["q"] for v in runs.values()]
    check(c, "field_tracer_flow_matches_5_L_per_min_of_200_ppm", abs(np.mean(qs) / (5e-3 / 60 * 200e-6) - 1) < 0.03, mean_q_m3_s=float(np.mean(qs)), q_range=[min(qs), max(qs)], expected_m3_s=5e-3 / 60 * 200e-6,
          note="readme: PMCH 200 ppm at 5 L/min = 1.667e-8 m^3/s of pure tracer; the runs' q average 1.2 % above it")
    wds = sorted(v["WD_R"] for v in runs.values())
    check(c, "runs_cover_78_to_200_deg_and_11_of_18_are_within_5_deg_of_180", wds[0] == 78.0 and wds[-1] == 200.7 and sum(abs(w - 180) <= 5 for w in wds) == 11, WD_R_min_max=[wds[0], wds[-1]], within_5deg_of_180=sum(abs(w - 180) <= 5 for w in wds),
          U_R_range_m_s=[min(v["U_R"] for v in runs.values()), max(v["U_R"] for v in runs.values())],
          note="only the runs near 180 deg are comparable with the tunnel's 175-185 deg; runs at 78-144 deg and the weak-wind runs 1, 2 and 9 (U_R 1.4-1.8 m/s) are far from the tunnel's regime")
    bg = {p: (min(v["C_ppq"][p - 1] for v in runs.values()), float(np.median([v["C_ppq"][p - 1] for v in runs.values()])), max(v["C_ppq"][p - 1] for v in runs.values())) for p in (11, 12, 13, 14, 15)}
    c0s = [v["c0_ppq"] for v in runs.values()]
    flo = [(bg[12][0] / max(c0s), bg[12][2] / min(c0s))]
    check(c, "field_concentration_has_a_floor_near_10_ppq", 8 <= bg[12][0] and bg[12][2] <= 11 and all(b[0] <= 9 for b in bg.values()), warn=True, min_median_max_ppq_by_point=bg,
          note=f"point 12 reads 9-11 ppq in all 18 runs whatever the wind; points 11, 13, 14, 15 bottom out at 8-9 ppq: an ambient PMCH background or the detection floor, not subtracted: 10 ppq is {10 / max(c0s):.4f} to {10 / min(c0s):.4f} of the runs' c0 (c0 = {min(c0s):.0f} to {max(c0s):.0f} ppq). QUESTIONS.md QM3")
    # frame
    xs, ys = special["Tracer gas source"][:2]
    def centroid(df):
        d = df[(df.x - xs * SCALE) > 0.03 * SCALE]
        w = d.C.clip(lower=0)
        return float(((d.y - ys * SCALE) * w).sum() / w.sum())
    cen = {wd: centroid(HA[HA.wind_direction_deg == wd]) for wd in (175.0, 180.0, 185.0)}
    runs_c = {run: centroid(FD[FD.run == str(run)]) for run in runs}
    sel = [run for run in runs if runs[run]["WD_R"] >= 170]
    rf = float(np.corrcoef([runs[r]["WD_R"] for r in runs], [runs_c[r] for r in runs])[0, 1])
    rf170 = float(np.corrcoef([runs[r]["WD_R"] for r in sel], [runs_c[r] for r in sel])[0, 1])
    check(c, "plume_moves_toward_minus_y_as_the_wind_direction_grows", cen[175.0] > cen[180.0] > cen[185.0] and rf < -0.5 and rf170 < -0.5, tunnel_lateral_centroid_of_the_downwind_plume_m=cen, field_runs_R_WD_vs_centroid=rf, field_runs_WD_ge_170_R=rf170,
          note="C-weighted lateral offset (y - y_source, full-scale m) of the points more than 18 m downwind of the source: it moves toward -y as WD grows in the tunnel AND across the field runs (so both share one frame); WD = 180 blows toward +x (the approach profile is measured at x = -0.498 m with U > 0)")
    # geometry
    ground = {}
    for p in range(1, 16):
        zs, _ = _surface_z(T, *(v * SCALE for v in pts_xyz[p][:2]))
        ground[p] = zs.tolist()
    dh = {p: pts_xyz[p][2] * SCALE - g[0] for p, g in ground.items()}
    check(c, "every_point_is_3_m_above_the_stl_ground", all(len(g) == 1 for g in ground.values()) and max(abs(v - 3.0) for v in dh.values()) < 0.12, height_above_stl_ground_m=[round(dh[p], 3) for p in range(1, 16)],
          max_abs_dev_from_3_m=max(abs(v - 3.0) for v in dh.values()), note="LC_caseM.csv: 'ground_surface+3m (in full scale)'; the STL's terrain under each point is a single surface (open air, no roof above)")
    shifted = {p: _surface_z(T, *(v * SCALE + 12.0 for v in pts_xyz[p][:2]))[0].tolist() for p in range(1, 16)}
    cnt_off = sum((not shifted[p]) or abs(pts_xyz[p][2] * SCALE - shifted[p][0] - 3.0) > 0.12 for p in range(1, 16))
    check(c, "control_points_shifted_12_m_leave_the_3_m_above_ground_relation", cnt_off >= 5, points_off_after_shift=int(cnt_off), note="the terrain relief makes the 3 m relation fail at >= 5 of 15 points after a 12 m shift in x and y: the check resolves a frame error of that size")
    gs = special["Tracer gas source"]
    sg = _surface_z(T, gs[0] * SCALE, gs[1] * SCALE)[0]
    ref_xyz = special["Reference point"]
    sr = _surface_z(T, ref_xyz[0] * SCALE, ref_xyz[1] * SCALE)[0]
    og = special["Origin point (Ground surface)"]
    check(c, "tracer_source_sits_on_the_stl_ground_not_on_a_roof", len(sg) == 1 and abs(gs[2] * SCALE - sg[0]) < 0.12, warn=True, source_z_m=gs[2] * SCALE, stl_surface_z_at_source_m=sg.tolist(), local_ground_for_neighbouring_points_m=[round(ground[1][0], 3), round(ground[2][0], 3)],
          readme="Ethylene ... released ... on a rooftop (tunnel); PMCH released from 1.5 m height (field)", note="the workbook, LC_caseM.csv ('ground_surface') and the STL put the tunnel source at ground level; the readme says rooftop. QUESTIONS.md QM1")
    roof = float(sr.max())
    check(c, "reference_point_is_41_m_above_ground_and_8_m_above_the_main_roof", len(sr) == 1 and abs((ref_xyz[2] * SCALE) - roof - 8.0) < 0.5, warn=True, reference_z_m=ref_xyz[2] * SCALE, stl_roof_z_under_reference_m=roof, anemometer_above_roof_m=ref_xyz[2] * SCALE - roof,
          roof_above_local_ground_m=roof - (ref_xyz[2] * SCALE - 41.0), tallest_surface_in_stl_m=float(T[:, :, 2].max()), local_ground_at_origin_m=og[2] * SCALE,
          tallest_surface_above_origin_ground_m=float(T[:, :, 2].max()) - og[2] * SCALE,
          note="LC_caseM.csv puts R at ground+41 m; the STL's main-building roof under it is ~33 m above the same ground, so H_R = 41 m is the anemometer height, not the building height; Table 1 of the paper says Hmax = 41 m while the tallest STL surface is ~32 m above the origin's ground. QUESTIONS.md QM2")
    # approach flow
    dafc = {n: 0.0 for n in ("U", "V", "W", "u_rms", "v_rms", "w_rms", "uw")}
    for i, r in enumerate(arows):
        for n, j in (("U", 4), ("V", 5), ("W", 6), ("u_rms", 7), ("v_rms", 8), ("w_rms", 9), ("uw", 10)):
            dafc[n] = max(dafc[n], abs(B.num(ar[i][aix[n]]) - r[j]))
    check(c, "approach_flow_csv_is_the_workbook_rounded", len(ar) == len(arows) == 40 and max(dafc.values()) <= 0.005 + 1e-9, max_abs_diff=dafc, heights=len(arows))
    zs_af = np.array([r[3] for r in arows])
    UU = np.array([r[4] for r in arows])
    fit = B.power_law_fit(zs_af, UU, 0.02, 0.5)
    check(c, "power_law_exponent_is_the_papers_0.27", abs(fit["alpha"] - 0.27) < 0.01, alpha=fit["alpha"], paper_alpha=0.27, window_model_m=[0.02, 0.5], note="category IV of the AIJ loads recommendation (data paper 3.13.1)")
    gz = _surface_z(T, arows[0][1] * SCALE, arows[0][2] * SCALE)[0] / SCALE      # model metres
    below = int((zs_af < float(gz[0]) - 1e-9).sum())
    check(c, "approach_flow_heights_below_the_stl_ground_at_the_profile_station", below == 0, warn=True, stl_ground_at_profile_m_model=float(gz[0]), heights_below_it=below, of=len(zs_af),
          note=f"the profile station x = {arows[0][1]} m stands on the model's upwind taper at {float(gz[0]):.4f} m above the floor: the lowest {below} of the {len(zs_af)} heights lie below that ground, so z is height above the EMPTY tunnel floor, not above the model's terrain. QUESTIONS.md QM5")
    UR_at_R = float(np.interp(ref_xyz[2], zs_af, UU))
    check(c, "profile_speed_at_the_reference_height_vs_UR", abs(UR_at_R / U_R - 1) < 0.05, profile_U_at_R_height_m_s=UR_at_R, U_R_m_s=U_R, rel_diff=UR_at_R / U_R - 1, note="info: the profile at z = 0.1215 m reads 3.9 m/s, U_R = 4.08 m/s was measured at R above the model (3.6 % higher)")
    # stl orientation / quality
    check(c, "published_stl_is_wound_inward", down0 > 0.95 * (down0 + up0) and up1 > 0.95 * (down1 + up1), warn=True, facing_down_as_published=down0, facing_up_as_published=up0, facing_up_after_reversal=up1,
          note="all but 34 of the 3,152 horizontal ground/roof facets face down in the file (stored normals agree with the winding); reversed here so normals point into the air")
    check(c, "stl_open_edges_counted", s_geo["edges_boundary"] == 21 and s_geo["edges_non_manifold"] == 7, warn=True, boundary_edges=s_geo["edges_boundary"], non_manifold_edges=s_geo["edges_non_manifold"],
          note="the surface is one shell; 21 boundary edges and 7 non-manifold edges (the latter on building roofs) are kept as published")
    check(c, "stl_domain_is_1_8_by_1_2_m_model", np.allclose(s_geo["bbox_min"][:2], [-540, -360]) and np.allclose(s_geo["bbox_max"][:2], [540, 360]), bbox_full_scale_m=[s_geo["bbox_min"], s_geo["bbox_max"]],
          note="the STL is a 1080 m x 720 m rectangle (terrain with the upwind taper); the buildings fill the ~300 m radius (0.5 m model) of the readme")
    # ------------------------------------------------------------------ inflow, normalisation, frame
    inflow = {"U_R_m_s": U_R, "H_R_m_model": H_R, "z_R_above_floor_m_model": ref_xyz[2], "U_at_R_height_from_profile_m_s": round(UR_at_R, 4), "profile_station_x_m_model": arows[0][1],
              "power_law": {**fit, "paper_alpha": 0.27, "note": "category IV, alpha = 0.27"}, "log_law": {**B.log_law_fit(zs_af, UU, 0.02, 0.5), "note": "listed for completeness; the paper describes the profile as a power law"},
              "turbulence_intensity_u_at_R_height": round(float(np.interp(ref_xyz[2], zs_af, np.array([r[7] for r in arows]) / UU)), 4),
              "method": "least squares on the workbook's 40 heights (z model metres, U in the tunnel's m/s) at x = -0.498 m; the case frame multiplies z by 600"}
    normalisation = {"concentration_ratio": "C / c0, c0 = q / (U_R H_R^2): the volume fraction of pure tracer at which the release would be diluted by a flow of U_R through an area H_R^2 (data paper 3.13.1)",
                     "tunnel": {"q_m3_s": q_wt, "U_R_m_s": U_R, "H_R_m": H_R, "c0_ppm": C0, "c0_paper_ppm": 133.0, "tracer": "C2H4, 100 %, 6 mm outlet"},
                     "field": {"H_R_m": H_field, "c0": f"per run: q_run / (U_R,run x 41^2) = {min(c0s):.0f} ... {max(c0s):.0f} ppq; see extra_measurements.field_runs", "tracer": "PMCH (C7F14), 200 ppm at 5 L/min"},
                     "velocity": "U, V, W and the rms values are the tunnel's m/s; divide by U_R = 4.08 m/s (the speed at the reference point R, rooftop of the main building) for the dimensionless form; no velocity ratio is tabulated",
                     "concentration_units": "tunnel C in ppm of the hydrocarbon analyser's reading; field C in ppq (parts per quadrillion, 1e-15) in the sources, ppm (x 1e-9) in points.csv"}
    frame = {"origin": "centre of the tunnel turntable on the floor plane (MP_caseM.png 'Origin'; its ground surface is at z = 33.07 m)", "x": "+x NORTH (compass rose of MP_caseM.png: N at +x)", "y": "+y WEST (W at +y); the frame is right-handed",
             "z": "+z up from the TUNNEL FLOOR, full scale; the campus ground lies at z ~ 32 m (terrain 3.6 ... 36 m); every point is 3 m above the local ground",
             "wind_direction_rotation": "meteorological FROM-direction (N = 0, E = 90, S = 180): 180 deg blows toward +x (north); flow_dir = (-cos WD, +sin WD), so WD > 180 turns the wind toward -y. Measured: the plume's lateral centroid moves toward -y as WD grows in the tunnel (175 -> 185 deg) and across the field runs, and the compass rose of MP_caseM.png agrees.",
             "length_scale": "FULL-scale metres (model 1:600): tunnel coordinates and the STL are multiplied by 600; velocities and concentrations are NOT scaled"}
    transform = {"coordinate_scale": SCALE, "lateral_sign": 1, "origin_shift_m": [0, 0, 0], "geometry_scale": SCALE,
                 "note": "workbook values at full precision (CSVs are the rounded copy); x, y, z x600; sigma -> variance; k = half the sum of the variances; field ppq -> ppm (x 1e-9); STL x600 and re-wound outward"}
    known = {
        "field_units": "Field concentrations are in ppq (1e-15) in RS-FO_caseM.csv and the workbook, tunnel concentrations in ppm: a factor 1e9 apart before normalisation",
        "tracer_release": {"readme_tunnel": "on a rooftop", "workbook_and_LC_csv": "ground surface", "readme_field": "1.5 m above ground, 5 L/min", "source_xyz_model_m": list(gs[:3]), "stl_surface_z_at_source_model_m": sg.tolist()},
        "reference_point": {"H_R_m": 41.0, "z_model_m": ref_xyz[2], "stl_roof_z_model_m": roof / SCALE, "anemometer_above_roof_full_scale_m": ref_xyz[2] * SCALE - roof},
        "field_background": {"min_median_max_ppq_by_point_11_to_15": {str(k): list(v) for k, v in bg.items()}},
        "tunnel_concentration_offset": {"negative_means": neg, "c_rms_floor_ppm": floor},
        "approach_flow_below_ground": {"stl_ground_at_profile_station_model_m": float(gz[0]), "heights_below": below},
        "stl": {"raw_model_scale_stats": s_raw, "as_published": {"horizontal_facets_down": down0, "horizontal_facets_up": up0}},
    }
    field_runs = [{"run": run, "U_R_m_s": runs[run]["U_R"], "WD_R_deg": runs[run]["WD_R"], "q_m3_s": runs[run]["q"], "c0_ppq": runs[run]["c0_ppq"], "c0_ppm": runs[run]["c0_ppq"] * PPQ} for run in sorted(runs)]
    extra = {"known_issues": known, "normalisation": normalisation, "field_runs": field_runs, "plume_lateral_centroid_m": {"tunnel_by_WD": {str(k): v for k, v in cen.items()}, "field_by_run": {str(k): v for k, v in runs_c.items()}}}
    return pts, afl, geo, inflow, frame, transform, extra


def directions(B, pts):
    rows = []
    for (cfg, inst, wd, wname), g in pts.groupby(["config", "instrument", "wind_direction_deg", "wind_direction"], sort=True):
        r = math.radians(wd)
        fx, fy = -math.cos(r), math.sin(r)
        q = "U" if inst == "split_fibre" else "C"
        rows.append({"case_id": "M", "config": cfg, "instrument": inst, "wind_direction_deg": wd, "wind_direction": wname, "flow_dir_x": round(fx, 9) + 0.0, "flow_dir_y": round(fy, 9) + 0.0,
                     "rows": int(len(g)), "measured": int(g[q].notna().sum()),
                     "sense_basis": "measured: the plume's lateral centroid moves toward -y as WD grows (tunnel 175 -> 185 deg, and across the 18 field runs); compass rose of MP_caseM.png (N = +x, W = +y) agrees; WD is the meteorological FROM-direction",
                     "status": "settled"})
    return pd.DataFrame(rows)
