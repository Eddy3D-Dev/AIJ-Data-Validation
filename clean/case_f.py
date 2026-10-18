"""Case F — flow within an actual urban area in Shinjuku (wind tunnel 1/800 + field cup anemometers).

One module per case: META is this case's entry of build.CASES, build(B, prov) returns what build_A..build_E
return (points, approach flow, geometry, inflow, frame, transform, extra), directions(B, pts) the rows of
directions.csv. B is the clean/build.py module (its readers, row(), check(), STL helpers); nothing of it is
duplicated here.

Sources (raw/cases/case-f/, the Zenodo files as published): RS-WT_caseF.csv (tunnel, thermistor, model-scale
metres), RS-FO_caseF.csv (field, cup anemometers, full-scale metres, with the standard deviation of the
10-minute means), AF_caseF.csv, MP_caseF.csv/.png, BD_caseF.stl (model scale), LF_CaseF.xls (the legacy workbook:
it carries the tunnel and field values normalised by the roof anemometers, which the CSVs re-normalise).
"""
from __future__ import annotations

import math
import os
import re
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pandas as pd

SCALE = 800.0                       # model 1:800 (readme, data paper 3.6.2); the case frame is FULL scale
GROUND_OFFSET = 10.0                # readme: z of the point files is height above the tunnel floor; ground = z - 10 m
SMB_SECTOR = ("NW", "NNW", "N", "NNE", "NE")   # directions normalised by the SMB roof anemometer (readme); the rest by KDD
HEIGHT_CONFIG = {5.0: "h5", 9.0: "default", 20.0: "h20"}   # tunnel plane above ground (m) -> config; 9 m is the benchmark plane
NOT_RUN = ("E", "ESE", "WSW", "W")  # directions the tunnel did not run (readme)

META = {
    "title": "Case F — flow within an actual urban area in Shinjuku", "folder": "raw/cases/case-f",
    "zenodo_concept": "10.5281/zenodo.15589621", "zenodo_version": None,   # the readme and the data paper name one DOI
    "scale": 800, "status": "provisional",
    "status_note": ("Case F: coordinates, ratios and inflow are released and pass every check. What stays provisional: 16 field values of "
                    "point 14 whose published direction labels disagree with the legacy workbook (this release follows the workbook; "
                    "QUESTIONS.md QF1), one tunnel value with no workbook counterpart (QF2), and the vertical reference of the geometry "
                    "(QF4)."),
    "contact": "Tsubasa Okaze <okaze.t.f356@m.isct.ac.jp>",
    "collectors": ["K. Fujii, Y. Asami, Y. Iwasa et al. (the original 1978 investigation, reference 59 of the data paper; the Zenodo readme names no data collectors)"],
    "citation": ("Fujii, K., Asami, Y., Iwasa, Y. et al. (1978). Wind in Shinjuku Sub-Central Area — Comparison Between Field Measurement and "
                 "Wind Tunnel Experiment. Proceedings of the 5th Symposium on Wind Resistance of Structures, 91-98 (in Japanese). "
                 "Also cite the data paper: Kikumoto, H. et al. (2026). Japan Architectural Review 9(1), e70083, section 3.6. https://doi.org/10.1002/2475-8876.70083"),
}


def _rhu(x: float, nd: int) -> float:
    """round half up (the sources' spreadsheets); Python's round() is half-even on the binary value."""
    return float(Decimal(repr(round(x, 12))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def _legacy(B, wb):
    """{(point, direction): {other, target, mplus, mean, mminus, sd}} from the workbook's 'Results (No.1-No.15)' sheet."""
    sh = wb.sheet_by_name("Results (No.1-No.15)")
    out = {}
    for r in range(sh.nrows):
        for c0 in (0, 7):
            v = sh.cell_value(r, c0)
            m = re.fullmatch(r"No\.\s*(\d+)", v) if isinstance(v, str) else None
            if not m:
                continue
            for rr in range(r + 3, r + 19):
                wd = sh.cell_value(rr, c0)
                if wd not in B.COMPASS:
                    raise SystemExit(f"Case F workbook: unexpected direction label {wd!r} in block {v!r}")
                cells = [B.num(sh.cell_value(rr, c0 + i)) for i in range(1, 7)]
                out[(int(m.group(1)), wd)] = dict(zip(("other", "target", "mplus", "mean", "mminus", "sd"), cells))
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
    """(horizontal facets facing down, facing up) — outward normals of a terrain-plus-buildings surface point up on every ground and roof facet."""
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(n, axis=1)
    flat = (ln > 0) & (np.abs(n[:, 2]) > 0.9999 * ln)
    return int((flat & (n[:, 2] < 0)).sum()), int((flat & (n[:, 2] > 0)).sum())


def _open_edges(T: np.ndarray, tol: float = 1e-7):
    """Vertices of the edges used by exactly one triangle (the same welding tolerance as B.stl_stats)."""
    seen = {}
    for t in T:
        k = [tuple(np.round(p / tol).astype(np.int64)) for p in t]
        for u, v in ((k[0], k[1]), (k[1], k[2]), (k[2], k[0])):
            e = (u, v) if u <= v else (v, u)
            seen[e] = seen.get(e, 0) + 1
    return np.array([[c * tol for c in v] for e, n in seen.items() if n == 1 for v in e])


def build(B, prov):
    c = "F"
    folder = os.path.join(B.REPO, META["folder"])
    P = {n: os.path.join(folder, n) for n in ("RS-WT_caseF.csv", "RS-FO_caseF.csv", "AF_caseF.csv", "MP_caseF.csv", "MP_caseF.png",
                                               "BD_caseF.stl", "LF_CaseF.xls", "readme_caseF.md")}
    prov[c] = list(P.values())
    wb = B.xls(P["LF_CaseF.xls"])
    leg = _legacy(B, wb)

    # ------------------------------------------------------------------ the three tables of values
    h, rows = B.read_csv_rows(P["RS-WT_caseF.csv"])
    ix = {n: i for i, n in enumerate(h)}
    B.log(f"[F] RS-WT_caseF.csv header (bare): {h}; tunnel coordinates are MODEL-scale metres (1/800), U/R normalised by the approaching speed at 500 m full scale")
    wt = []
    for r in rows:
        g = lambda n: B.num(r[ix[n]])
        wt.append(dict(no=int(g("No.")), x=g("x"), y=g("y"), z=g("z"), wd=r[ix["WD"]].strip(), ur=g("U/R")))
    h, rows = B.read_csv_rows(P["RS-FO_caseF.csv"])
    ix = {n: i for i, n in enumerate(h)}
    B.log(f"[F] RS-FO_caseF.csv header (bare): {h}; field coordinates are FULL-scale metres, sigma_U/R = standard deviation of the 10-minute means")
    fo = {}
    fo_xyz = {}
    for r in rows:
        g = lambda n: B.num(r[ix[n]])
        fo[(int(g("No.")), r[ix["WD"]].strip())] = (g("U/R"), g("sigma_U/R"))
        fo_xyz[int(g("No."))] = (g("x"), g("y"), g("z"))
    points = sorted(fo_xyz)

    # ---- the reference conversion: the CSVs re-normalise the workbook (roof anemometers) by a factor per sector
    def sector(wd):
        return "SMB" if wd in SMB_SECTOR else "KDD"

    ratios = {s: [fo[k][0] / leg[k]["mean"] for k in fo if sector(k[1]) == s and leg[k]["mean"] > 0] for s in ("SMB", "KDD")}
    f0 = {s: float(np.median(v)) for s, v in ratios.items()}
    shifts = {}
    for no in points:
        counts = {}
        for s in range(-2, 3):
            counts[s] = sum(abs(fo[(no, d)][0] - f0[sector(d)] * leg[(no, B.COMPASS[(i + s) % 16])]["mean"]) <= 0.012 for i, d in enumerate(B.COMPASS))
        best = max(counts, key=lambda s: (counts[s], -abs(s)))
        shifts[no] = (best, counts)
    shifted = [no for no in points if shifts[no][0] != 0]
    aligned = [no for no in points if shifts[no][0] == 0]
    # exact conversion factors from the aligned points: f must satisfy round_half_up(f * workbook mean, 2) = CSV mean and
    # round_half_up(f * workbook sd, 3) = CSV sigma on every row, which bounds it to an interval
    fint = {}
    for s in ("SMB", "KDD"):
        lo, hi = 0.0, 10.0
        for no in aligned:
            for d in B.COMPASS:
                if sector(d) != s:
                    continue
                ur, sig = fo[(no, d)]
                m, sd = leg[(no, d)]["mean"], leg[(no, d)]["sd"]
                if m > 0:
                    lo, hi = max(lo, (ur - 0.005) / m), min(hi, (ur + 0.005) / m)
                if sd > 0:
                    lo, hi = max(lo, (sig - 0.0005) / sd), min(hi, (sig + 0.0005) / sd)
        fint[s] = (lo, hi)
    f = {s: round((lo + hi) / 2, 5) for s, (lo, hi) in fint.items()}
    B.log(f"[F] field values = round_half_up(f x workbook value): factors from the workbook's roof-anemometer normalisation to the 500 m reference, "
          f"f_SMB in [{fint['SMB'][0]:.5f}, {fint['SMB'][1]:.5f}], f_KDD in [{fint['KDD'][0]:.5f}, {fint['KDD'][1]:.5f}]; used {f}")
    B.log(f"[F] direction alignment of the field series against the workbook (best shift in directions, matches of 16): " +
          ", ".join(f"{no}:{shifts[no][0]:+d} ({shifts[no][1][shifts[no][0]]}/16)" for no in points))

    # ---- field rows; the shifted point's 16 rows are re-derived from the workbook with the same rule
    published14 = []
    out = []
    for no in points:
        x, y, z = fo_xyz[no]
        for i, d in enumerate(B.COMPASS):
            ur, sig = fo[(no, d)]
            if no in shifted:
                m, sd = leg[(no, d)]["mean"], leg[(no, d)]["sd"]
                published14.append({"point": no, "direction": d, "published_U_R": ur, "published_sigma": sig,
                                    "used_U_R": _rhu(f[sector(d)] * m, 2), "used_sigma": _rhu(f[sector(d)] * sd, 3)})
                ur, sig = _rhu(f[sector(d)] * m, 2), _rhu(f[sector(d)] * sd, 3)
            out.append(B.row(case_id=c, instrument="cup_anemometer", campaign="field", point_id=no, wind_direction=d, wind_direction_deg=i * 22.5,
                             x=x, y=y, z=z, velocity_ratio=ur, velocity_ratio_sd=sig))
    for no in shifted:
        B.log(f"[F] transform: field point {no}: the published rows carry the workbook's value of the NEXT direction clockwise (shift {shifts[no][0]:+d}); "
              f"re-derived from LF_CaseF.xls as round_half_up(f x workbook value) for all 16 directions (published values kept in manifest known_issues)")
    # ---- tunnel rows
    for t in wt:
        hgt = round(t["z"] * SCALE - GROUND_OFFSET, 6)
        if hgt not in HEIGHT_CONFIG:
            raise SystemExit(f"Case F tunnel height {hgt} m above ground is not one of 5 / 9 / 20")
        out.append(B.row(case_id=c, instrument="thermistor", config=HEIGHT_CONFIG[hgt], point_id=t["no"], wind_direction=t["wd"],
                         wind_direction_deg=B.COMPASS.index(t["wd"]) * 22.5, x=t["x"] * SCALE, y=t["y"] * SCALE, z=t["z"] * SCALE, velocity_ratio=t["ur"]))
    B.log(f"[F] transform: tunnel x, y, z model metres x {SCALE:g} -> full-scale metres; config = height above ground by the readme's rule (z - {GROUND_OFFSET:g} m): "
          "9 m -> default (the benchmark plane, shared with the field), 5 m -> h5, 20 m -> h20; compass name -> wind_direction_deg = 22.5 x index (N = 0)")
    pts = pd.DataFrame(out, columns=B.POINT_COLUMNS)
    T_ = pts[pts.instrument == "thermistor"]
    F_ = pts[pts.instrument == "cup_anemometer"]

    # ------------------------------------------------------------------ approach flow
    h, ar = B.read_csv_rows(P["AF_caseF.csv"])
    ai = {n: i for i, n in enumerate(h)}
    afl = pd.DataFrame([{"case_id": c, "z": B.num(r[ai["z"]]) * SCALE, "U": B.num(r[ai["U"]]), "uu": B.num(r[ai["u_rms"]]) ** 2,
                         "vv": math.nan, "ww": math.nan, "k": math.nan} for r in ar])
    B.log("[F] approach flow: AF_caseF.csv, 18 heights, z model metres x 800 -> full scale (10 ... 400 m); u_rms squared to uu; U in the tunnel's m/s; no v, w, k published")
    inf = wb.sheet_by_name("Inflow")
    wbi = np.array([[float(inf.cell_value(r, 1)), float(inf.cell_value(r, 3)), float(inf.cell_value(r, 4))] for r in range(2, 22)])   # z [m], U/UR, k/UR^2

    # ------------------------------------------------------------------ geometry: BD_caseF.stl is model scale and wound inward
    raw = B.read_ascii_stl(P["BD_caseF.stl"])
    Tm = np.array(raw) * SCALE
    down0, up0 = _orientation(Tm)
    s_raw = B.stl_stats([tuple(tuple(v * SCALE for v in p) for p in t) for t in raw])
    tris = [tuple(tuple(float(v) for v in p) for p in t) for t in Tm]
    if down0 > up0:
        tris = [(a, c_, b) for a, b, c_ in tris]
    T = np.array(tris)
    down1, up1 = _orientation(T)
    s_geo = B.stl_stats(tris)
    B.log(f"[F] geometry: BD_caseF.stl is MODEL scale (bbox ±0.90625 m = ±725 m full scale; the lowest elevation is the tunnel floor); scaled x {SCALE:g}; "
          f"every horizontal ground/roof facet faces DOWN as published ({down0} down, {up0} up), i.e. the whole surface is wound inward: all triangles reversed "
          f"({down1} down, {up1} up now); stats {s_geo}")
    served, closed = B.close_terrain(tris, digits=7)
    s_served = B.stl_stats(served)
    B.log(f"[F] geometry served: closed with a base slab ({closed}); stats {s_served}")
    geo = [("default", None, served, "BD_caseF.stl (Zenodo; terrain + buildings of Nov 1978) scaled x800 from model to full-scale metres and re-wound outward; "
            f"{s_geo['triangles']:,} triangles, open along the rim of the 725 m disc ({s_geo['edges_boundary']} boundary edges at z = 0, the tunnel floor); closed here with a base slab: "
            f"vertical walls from the rim down to z = {B.BASE_Z:g} m and a bottom cap at z = {B.BASE_Z:g} m ({closed['base_triangles']:,} added triangles)"
            + (f"; {closed['degenerate_removed']} zero-area triangles are removed and the neighbour across each is split" if closed["degenerate_removed"] else ""))]

    # ------------------------------------------------------------------ checks
    cnt = {k: int(v) for k, v in T_.groupby("config").size().items()}
    check = B.check
    check(c, "row_counts", len(T_) == 264 and len(F_) == 208 and cnt == {"default": 156, "h20": 79, "h5": 29}, tunnel=len(T_), field=len(F_), tunnel_by_plane=cnt,
          note="tunnel 156 = 13 points x 12 directions on the 9 m plane, 79 rows at 20 m, 29 at 5 m; field 208 = 13 points x 16 directions")
    check(c, "point_numbers_1_to_15_without_4_and_12", points == [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15] and sorted(T_.point_id.unique()) == points,
          points=points, note="readme: absent points 4 and 12; the workbook and MP_caseF.png also hold points 16-36 (later construction stages), not in this dataset")
    dirs_t = sorted(T_.wind_direction.unique(), key=B.COMPASS.index)
    check(c, "tunnel_ran_12_directions_field_has_16", set(B.COMPASS) - set(dirs_t) == set(NOT_RUN) and F_.wind_direction.nunique() == 16, tunnel=dirs_t,
          not_run=sorted(set(B.COMPASS) - set(dirs_t), key=B.COMPASS.index))
    check(c, "key_is_unique", not pts.duplicated(["config", "instrument", "point_id", "wind_direction_deg"]).any())
    check(c, "no_nan_in_ratios", not pts.velocity_ratio.isna().any() and not F_.velocity_ratio_sd.isna().any())
    # coordinates: tunnel x 800 equals the field's, MP csv equals the tunnel's, the workbook's Points sheet equals the field's
    td = T_.drop_duplicates("point_id").set_index("point_id")[["x", "y"]]
    fd = pd.DataFrame(fo_xyz, index=["x", "y", "z"]).T
    check(c, "tunnel_coordinates_x800_equal_field_coordinates", float((td - fd.loc[td.index, ["x", "y"]]).abs().max().max()) < 1e-6,
          max_abs_diff_m=float((td - fd.loc[td.index, ["x", "y"]]).abs().max().max()), note="the field and the tunnel share one point set; the 1/800 scale is confirmed by the points themselves")
    mh, mr = B.read_csv_rows(P["MP_caseF.csv"])
    mi = {n: j for j, n in enumerate(mh)}
    mp = {r[mi["No"]]: (B.num(r[mi["x"]]), B.num(r[mi["y"]])) for r in mr}
    dm = max(max(abs(mp[str(no)][0] * SCALE - fd.loc[no, "x"]), abs(mp[str(no)][1] * SCALE - fd.loc[no, "y"])) for no in points)
    pt = wb.sheet_by_name("Points")
    wbp = {int(pt.cell_value(r, 1)): (pt.cell_value(r, 2), pt.cell_value(r, 3), pt.cell_value(r, 4)) for r in range(2, 35) if isinstance(pt.cell_value(r, 1), float)}
    dw = max(max(abs(wbp[no][0] - fd.loc[no, "x"]), abs(wbp[no][1] - fd.loc[no, "y"])) for no in points)
    check(c, "mp_csv_and_workbook_points_agree_with_the_tables", dm < 1e-6 and dw < 1e-9, mp_csv_x800_max_diff_m=dm, workbook_points_max_diff_m=dw,
          note="MP_caseF.csv (model metres), LF_CaseF.xls 'Points' (full-scale metres), RS-WT and RS-FO give one set of 13 coordinates")
    # heights
    zt = sorted(T_.z.unique())
    check(c, "tunnel_planes_are_15_19_30_m_above_the_floor", np.allclose(zt, [15, 19, 30]), z_m=zt, note="= 5 / 9 / 20 m above ground by the readme's rule 'subtract 10 m'; the paper says heights equivalent to 5, 9 and 20 m")
    above = sorted({round(v - GROUND_OFFSET, 6) for v in F_.z})
    check(c, "field_anemometer_heights_within_the_papers_3_to_9_m", max(above) <= 9.0, warn=True, heights_above_ground_m=above,
          points_at_11_m=sorted(F_[np.isclose(F_.z - GROUND_OFFSET, 11)].point_id.unique()),
          note="data paper 3.6.2: 'the measurement height ranged from 3 to 9 m above the ground level'; by the readme's rule points 13 and 14 sit at 11 m (QUESTIONS.md QF7)")

    # ---- the field series against the workbook
    n_all = sum(1 for k in fo)
    rule = sum(abs(_rhu(f[sector(d)] * leg[(no, d)]["mean"], 2) - fo[(no, d)][0]) < 1e-9 and abs(_rhu(f[sector(d)] * leg[(no, d)]["sd"], 3) - fo[(no, d)][1]) < 1e-9
               for no in aligned for d in B.COMPASS)
    check(c, "field_csv_is_the_workbook_times_one_factor_per_sector", rule == 16 * len(aligned) and all(lo <= hi for lo, hi in fint.values()), rows_reproduced=rule, of=16 * len(aligned),
          f_SMB=f["SMB"], f_SMB_interval=fint["SMB"], f_KDD=f["KDD"], f_KDD_interval=fint["KDD"],
          note="U/R_field = round(f x workbook mean, 2) and sigma = round(f x workbook S.D., 3), f = U(roof anemometer) / U(500 m): 0.94 for NW-NE (SMB, G.L.+237 m), 0.963 for the other directions (KDD, G.L.+187 m)")
    check(c, "field_direction_alignment_matches_the_workbook_except_one_point", shifted == [14] and all(shifts[no][1][0] == 16 for no in aligned) and shifts[14][0] == 1 and shifts[14][1][1] == 16,
          shifted_points=shifted, matches_by_shift_point14=shifts[14][1], note="every direction of point 14 holds the workbook's value of the next direction clockwise; the other 12 points match 16/16 unshifted")
    tmap = T_[T_.config == "default"].set_index(["point_id", "wind_direction"]).velocity_ratio
    common = [d for d in B.COMPASS if d not in NOT_RUN]
    a14 = np.array([tmap[(14, d)] for d in common])
    pub = np.array([fo[(14, d)][0] for d in common])
    new = np.array([F_[(F_.point_id == 14) & (F_.wind_direction == d)].velocity_ratio.iloc[0] for d in common])
    r_pub, r_new = float(np.corrcoef(a14, pub)[0, 1]), float(np.corrcoef(a14, new)[0, 1])
    r_other = {no: float(np.corrcoef([tmap[(no, d)] for d in common], [F_[(F_.point_id == no) & (F_.wind_direction == d)].velocity_ratio.iloc[0] for d in common])[0, 1]) for no in aligned}
    check(c, "point_14_workbook_alignment_correlates_with_the_tunnel_like_the_other_points", r_new >= min(r_other.values()) and r_pub < min(r_other.values()), R_tunnel_field_published_alignment=r_pub,
          R_workbook_alignment=r_new, R_other_points_min=min(r_other.values()), R_other_points_max=max(r_other.values()),
          note="R between the 12 tunnel directions and the field at point 14: below every other point as published, inside their range after the realignment. Supporting evidence only; which file is right is QUESTIONS.md QF1")
    # ---- the tunnel series against the workbook ('Target' = the 9 m plane)
    t9 = T_[T_.config == "default"]
    dev, nolegacy, within = [], [], 0
    for r_ in t9.itertuples():
        tg = leg[(r_.point_id, r_.wind_direction)]["target"]
        if math.isnan(tg):
            nolegacy.append((int(r_.point_id), r_.wind_direction, float(r_.velocity_ratio)))
            continue
        fs = f[sector(r_.wind_direction)]
        dev.append(r_.velocity_ratio - fs * tg)
        within += abs(dev[-1]) <= 0.005 * fs + 0.0005
    s1 = wb.sheet_by_name("Sheet1")
    s1v = {(int(s1.cell_value(r, 0)), s1.cell_value(r, 4)): s1.cell_value(r, 5) for r in range(1, s1.nrows)}
    check(c, "tunnel_9m_plane_is_the_workbook_target_column_times_the_same_factors", len(dev) == 155 and max(abs(d) for d in dev) < 0.014 and len(nolegacy) == 1, rows_compared=len(dev), within_rounding=int(within),
          max_abs_dev=float(max(abs(d) for d in dev)), median_f_SMB=float(np.median([r_.velocity_ratio / leg[(r_.point_id, r_.wind_direction)]["target"] for r_ in t9.itertuples() if r_.wind_direction in SMB_SECTOR and not math.isnan(leg[(r_.point_id, r_.wind_direction)]["target"])])),
          median_f_KDD=float(np.median([r_.velocity_ratio / leg[(r_.point_id, r_.wind_direction)]["target"] for r_ in t9.itertuples() if r_.wind_direction not in SMB_SECTOR and not math.isnan(leg[(r_.point_id, r_.wind_direction)]["target"])])),
          note="the workbook rounds to 2 dp (half-width 0.005 x f) and the CSV carries 3 dp; 155 of 156 rows within 0.014, all but 25 within the rounding alone")
    check(c, "tunnel_point_8_SW_has_no_workbook_value", not nolegacy or nolegacy[0][:2] == (8, "SW"), warn=True, csv_row=nolegacy, workbook_Sheet1_value=s1v.get((8, "SW")), workbook_Results_target=None,
          note="RS-WT has U/R = 0.474 for (8, SW) at 9 m; the workbook's 'Results' sheet is blank there and its flat 'Sheet1' table says 0.63 (x 0.963 = 0.607). QUESTIONS.md QF2")
    # 'Other' column: 109 values, two sets of extra heights in the CSV; none reproduces
    other = {k: v["other"] for k, v in leg.items() if not math.isnan(v["other"])}
    extra_rows = T_[T_.config != "default"]
    hit, both = 0, 0
    for r_ in extra_rows.itertuples():
        o = other.get((r_.point_id, r_.wind_direction))
        if o is not None:
            both += 1
            hit += abs(r_.velocity_ratio - f[sector(r_.wind_direction)] * o) <= 0.005 * f[sector(r_.wind_direction)] + 0.0005
    esb = sorted(k[0] for k in other if k[1] == "ESE")
    check(c, "workbook_other_column_is_not_the_5_or_20_m_data", hit < 0.2 * both and len(other) == 109, warn=True, workbook_other_values=len(other), csv_5_20m_rows=len(extra_rows), pairs_compared=both, pairs_reproduced=int(hit),
          points_with_an_ESE_other_value=esb, note="'Other' has 9 values at ESE although the readme says E, ESE, WSW and W were not run; it reproduces neither the 5 m nor the 20 m rows. QUESTIONS.md QF3")
    # workbook band asymmetry and sigma quantisation
    asym = [(k, round(v["mplus"] - v["mean"] - (v["mean"] - v["mminus"]), 3)) for k, v in sorted(leg.items()) if abs(v["mplus"] - v["mean"] - (v["mean"] - v["mminus"])) > 0.0201]
    low = max(abs(v["sd"] - (v["mean"] - v["mminus"])) for v in leg.values())
    check(c, "csv_sigma_is_the_workbooks_lower_half_width_which_is_not_symmetric_in_10_rows", low < 1e-9 and len(asym) == 10, warn=True, rows_with_asymmetric_band=[f"{k[0]}/{k[1]}: {a:+.2f}" for k, a in asym],
          note="the workbook's last column equals Mean - (Mean-S.D.); Mean+S.D. differs from Mean+that by up to 0.11 in 10 rows. QUESTIONS.md QF10")
    sg = {s: [fo[(no, d)][1] for no in aligned for d in B.COMPASS if sector(d) == s] for s in ("SMB", "KDD")}
    lat = {s: float(np.max(np.abs(np.array(v) / (f[s] / 100) - np.round(np.array(v) / (f[s] / 100))))) for s, v in sg.items()}
    levels = {s: int(len(set(np.round(np.array(v) / (f[s] / 100)).astype(int)))) for s, v in sg.items()}
    check(c, "sigma_is_quantised_at_f_over_100", all(v < 0.06 for v in lat.values()), max_distance_to_lattice_in_steps=lat, distinct_levels=levels, step_SMB=round(f["SMB"] / 100, 5), step_KDD=round(f["KDD"] / 100, 5),
          note="sigma = f x (S.D. rounded to 0.01): the published sigma resolves 0.0094 / 0.0096 in steps, 4-20 % of its value; a tolerance below one step measures the rounding")

    # ---- the three planes against each other (vertical order); info, a tunnel profile can be non-monotonic near buildings
    pv = T_.pivot_table(index=["point_id", "wind_direction"], columns="config", values="velocity_ratio")
    b59 = pv.dropna(subset=["h5", "default"])
    c209 = pv.dropna(subset=["h20", "default"])
    inv5, inv20 = b59[b59.h5 >= b59["default"]], c209[c209.h20 <= c209["default"]]
    check(c, "vertical_order_of_the_tunnel_planes_5_9_20", len(b59) == 29 and len(c209) == 79 and len(inv5) <= 5 and len(inv20) <= 1, pairs_5_vs_9=len(b59), five_m_not_below_nine_m=[f"{a}/{b}" for a, b in inv5.index],
          pairs_20_vs_9=len(c209), twenty_m_not_above_nine_m=[f"{a}/{b}" for a, b in inv20.index], median_ratio_5_over_9=float((b59.h5 / b59["default"]).median()), median_ratio_20_over_9=float((c209.h20 / c209["default"]).median()),
          note="info: U/R mostly rises with height (median 20 m / 9 m = 1.41, 5 m / 9 m = 0.85) but 4 of 29 pairs have the 5 m value above the 9 m one (one exactly equal, 0.173) and one 20 m value (13/SSW) is below the 9 m one")

    # ---- geometry and frame
    ground = {}
    for no in points:
        zs, _ = _surface_z(T, fd.loc[no, "x"], fd.loc[no, "y"])
        ground[no] = zs.tolist()
    pz = {z: pts[np.isclose(pts.z, z)].drop_duplicates("point_id") for z in sorted(pts.z.unique())}
    inside = {float(z): int(B.points_under_roof(g[["x", "y"]].to_numpy(), float(z), tris).sum()) for z, g in pz.items()}
    xy = fd.loc[points, ["x", "y"]].to_numpy()
    ctrl = int(B.points_under_roof(B.rot_xy(xy, 45.0), 19.0, tris).sum())
    check(c, "no_sensor_inside_a_building", sum(inside.values()) == 0, inside_by_height_z=inside, points_by_height={float(z): len(g) for z, g in pz.items()},
          note="every (x, y, z) of the tunnel and the field lies above the surface of BD_caseF.stl at its own (x, y)")
    check(c, "control_points_rotated_45deg_land_inside_buildings", ctrl >= 1, inside_after_rotation=ctrl,
          note="the 13 points stand in open plazas and wide streets (rotations of 20 deg or less leave all of them in the open): this test resolves a frame error of 45 deg, not a small one; the reference-building test below resolves 10 deg")
    g5 = {no: g for no, g in ground.items()}
    check(c, "stl_ground_under_every_point_is_z_5_m", all(len(g) == 1 and abs(g[0] - 5.0) < 1e-6 for g in g5.values()), ground_z_m=sorted({round(g[0], 6) for g in g5.values()}),
          note="the readme says the point heights are above a ground at z = 10 m (z - 10 = 5 / 9 / 20 m); the STL's terrain under all 13 points is at 5 m, so the planes are 10 / 14 / 25 m above it. QUESTIONS.md QF4")
    # the two reference buildings: roof heights decide which is SMB and which KDD
    ref = {}
    for r in (35, 36):   # the two building rows of the workbook's 'Points' sheet: C = KDD Building, D = Shinjuku-Mitsui Building (SMB)
        ref[str(pt.cell_value(r, 1))] = (float(pt.cell_value(r, 2)), float(pt.cell_value(r, 3)), str(pt.cell_value(r, 5)))
    roofs = {n: float(_surface_z(T, x, y)[0].max()) for n, (x, y, _) in ref.items()}
    mpn = {n: tuple(v * SCALE for v in mp[n]) for n in ("SMB", "KDD")}
    smb_wb = next(n for n, v in ref.items() if "SMB" in v[2])
    kdd_wb = next(n for n, v in ref.items() if "KDD" in v[2])
    check(c, "roofs_at_the_reference_points_differ_by_45_m_as_SMB_and_KDD_do", abs((roofs[smb_wb] - roofs[kdd_wb]) - 45.0) < 0.5, roof_z_at_workbook_SMB_m=roofs[smb_wb], roof_z_at_workbook_KDD_m=roofs[kdd_wb],
          stated_roof_elevations_GL_m={"SMB": 210, "KDD": 165}, note="the workbook's SMB (-17.5, 96.0) is the taller building by exactly the 45 m the readme gives (210 - 165); both roofs stand 15 m above their G.L. elevation in the STL (5 m terrain + the readme's 10 m)")
    tall = lambda rot: int(sum(float(_surface_z(T, *(B.rot_xy(np.array([v[:2]]), rot)[0]))[0].max(initial=0.0)) >= 150.0 for v in ref.values()))
    check(c, "reference_points_stand_on_the_two_tall_roofs", tall(0.0) == 2 and tall(10.0) < 2, tall_roofs_at_the_two_reference_points=tall(0.0), tall_roofs_after_a_10deg_rotation=tall(10.0),
          note="the workbook's two roof-anemometer positions (full-scale m) fall on roofs of 225 m and 180 m in the scaled STL; rotated by 10 deg they no longer do: this fixes the frame, the 1/800 scale and the x/y orientation to a few metres")
    check(c, "mp_csv_labels_SMB_and_KDD_agree_with_the_workbook", np.allclose(mpn["SMB"], ref[smb_wb][:2], atol=0.01) and np.allclose(mpn["KDD"], ref[kdd_wb][:2], atol=0.01), warn=True,
          mp_csv_SMB_xy_m=mpn["SMB"], mp_csv_KDD_xy_m=mpn["KDD"], workbook_SMB_xy_m=ref[smb_wb][:2], workbook_KDD_xy_m=ref[kdd_wb][:2],
          note="MP_caseF.csv names the two reference points the other way round from the workbook, the STL roof heights and MP_caseF.png (D = SMB, C = KDD). QUESTIONS.md QF6")
    check(c, "published_stl_is_wound_inward", down0 > 0.99 * (down0 + up0) and up1 > 0.99 * (down1 + up1), warn=True, facing_down_as_published=down0, facing_up_as_published=up0, facing_up_after_reversal=up1,
          note="all ground and roof facets face down in the file (stored normals agree with the winding); reversed here so normals point into the air")
    nrm = np.cross(Tm[:, 1] - Tm[:, 0], Tm[:, 2] - Tm[:, 0])
    ln = np.linalg.norm(nrm, axis=1)
    ws = np.where((ln > 0) & (np.abs(nrm[:, 2]) < 1e-6 * np.maximum(ln, 1e-30)))[0]
    sample = ws[:: max(1, len(ws) // 400)]
    inw = amb = 0
    for i in sample:
        cen = Tm[i].mean(0)
        nn = nrm[i, :2] / np.linalg.norm(nrm[i, :2])
        side = []
        for sgn in (1.0, -1.0):
            z_ = _surface_z(Tm, cen[0] + sgn * 0.4 * nn[0], cen[1] + sgn * 0.4 * nn[1])[0]
            side.append(len(z_) > 0 and float(z_.max()) > cen[2] + 1e-6)
        inw += side[0] and not side[1]
        amb += side[0] == side[1]
    check(c, "walls_are_wound_inward_too", inw > 0.95 * len(sample), warn=True, walls_sampled=len(sample), normal_points_into_the_solid=int(inw), ambiguous=int(amb))
    bx = s_geo["bbox_min"], s_geo["bbox_max"]
    rmax = float(np.hypot(T[:, :, 0], T[:, :, 1]).max())
    check(c, "stl_disc_radius_is_725_m_not_800", abs(rmax - 725.0) < 0.01, warn=True, radius_m=rmax, bbox=[bx[0], bx[1]],
          note="readme: 'radius = 800 m equivalent', data paper: 'diameter of 1600 m'; the STL is a 725 m disc (0.90625 m model). QUESTIONS.md QF5")
    rim = _open_edges(T)
    rr, rz = np.hypot(rim[:, 0], rim[:, 1]), rim[:, 2]
    zero_area = int((np.linalg.norm(np.cross(Tm[:, 1] - Tm[:, 0], Tm[:, 2] - Tm[:, 0]), axis=1) < 1e-9).sum())
    check(c, "stl_closed_except_the_rim", s_geo["edges_non_manifold"] == 0 and s_geo["edges_boundary"] == 812 and rr.min() > 724.99 and rr.max() < 725.01 and np.abs(rz).max() < 1e-6, boundary_edges=s_geo["edges_boundary"],
          non_manifold_edges=s_geo["edges_non_manifold"], boundary_vertex_radius_m=[float(rr.min()), float(rr.max())], boundary_vertex_z_m=[float(rz.min()), float(rz.max())], zero_area_facets=zero_area,
          note="all 812 boundary edges lie on the 725 m circle at z = 0 (the surface is terrain + buildings, open at the rim); counted on the published file: the served geometry closes the rim with a base slab and removes the zero-area facets (T-junction fillers)")

    check(c, "served_geometry_is_one_closed_outward_body", s_served["watertight"] and s_served["bodies"] == 1 and s_served["edges_boundary"] == 0 and s_served["bbox_min"][2] == B.BASE_Z
          and closed["base_triangles"] == 3 * s_geo["edges_boundary"], bodies=s_served["bodies"], boundary_edges=s_served["edges_boundary"], base_triangles=closed["base_triangles"], signed_volume_m3=s_served["signed_volume"],
          note=f"the surface above the floor is unchanged except {closed['degenerate_removed']} zero-area triangles; the base slab adds a skirt of 2 triangles per rim edge and a bottom cap of 1 per rim edge")

    # ---- the wind-direction sense: compass FROM-directions. Upwind roughness is the independent evidence.
    north = [no for no in points if fd.loc[no, "y"] >= 150.0]
    def quad(df, names):
        return float(df[df.point_id.isin(north) & df.wind_direction.isin(names)].velocity_ratio.mean())
    ev = {nm: (quad(d, ("NW", "N", "NNE", "NE")), quad(d, ("SE", "S", "SSW", "SW"))) for nm, d in (("tunnel_9m", t9), ("field", F_))}
    faster = sum(float(t9[(t9.point_id == no) & t9.wind_direction.isin(("SE", "S", "SSW", "SW"))].velocity_ratio.mean()) > float(t9[(t9.point_id == no) & t9.wind_direction.isin(("NW", "N", "NNE", "NE"))].velocity_ratio.mean()) for no in north)
    check(c, "northern_points_see_faster_flow_for_the_S_labels_than_for_the_N_labels", all(b > a for a, b in ev.values()) and faster >= 0.7 * len(north), mean_U_R_north_labels_vs_south_labels=ev, points_faster_from_S=int(faster), of=len(north),
          note="the points in the dense low-rise area north of y = 150 m (MP_caseF.png) read higher when the label is S (open plaza and towers upwind) than N (low-rise upwind): the labels are FROM-directions, as is the reference-building choice (SMB for NW-NE). Not a solved field; a solved field decides NNW alone (directions.csv, QUESTIONS.md QF9)")

    # ---- inflow
    UR = [float(r_.U) / wbi[i, 1] for i, r_ in enumerate(afl.itertuples())]
    z_ok = max(abs(afl.z.iloc[i] - wbi[i, 0]) for i in range(len(afl)))
    fitp = B.power_law_fit(afl.z, afl.U, 10.0, 400.0)
    check(c, "approach_flow_heights_match_the_workbook_inflow_sheet", z_ok < 1e-9, max_abs_diff_z_m=z_ok, note="AF_caseF.csv z x 800 equals the workbook's z[m] column for the 18 heights it shares (10 ... 400 m)")
    check(c, "reference_speed_implied_by_the_profile_is_10_65_not_10", abs(float(np.mean(UR)) - 10.648) < 0.05 and abs(float(np.mean(UR)) - 10.0) > 0.5, warn=True, UR_mean=float(np.mean(UR)), UR_min=float(min(UR)), UR_max=float(max(UR)), UR_paper=10.0,
          note="U(z) / (U/UR)(z) from the 18 shared heights gives U(500 m) = 10.65 m/s; the data paper says 10 m/s at 500 m, which is the profile's value at 400 m (10.0). QUESTIONS.md QF8")
    check(c, "power_law_exponent_near_the_papers_one_quarter", abs(fitp["alpha"] - 0.25) < 0.05, alpha=fitp["alpha"], paper_alpha=0.25, window_m=[10, 400])
    inflow = {"U_ref_m_s": round(float(np.mean(UR)), 3), "z_ref_m": 500.0,
              "U_ref_basis": "the tunnel's approaching speed at the boundary-layer height 500 m (full scale = 0.625 m model): AF_caseF.csv stops at 400 m (U = 10.0 m/s); the workbook's profile U/UR(400 m) = 0.94 puts UR = 10.65 m/s. The data paper states 10 m/s. The velocity ratios are dimensionless; the choice matters only when they are turned into m/s.",
              "U_ref_range_over_the_18_heights_m_s": [round(min(UR), 3), round(max(UR), 3)], "U_ref_paper_m_s": 10.0, "U_at_400_m_m_s": float(afl.U.iloc[-1]),
              "workbook_profile_U_over_UR": {"z_m": wbi[:, 0].tolist(), "U_over_UR": wbi[:, 1].tolist(), "k_over_UR2": [round(v, 9) for v in wbi[:, 2]]},
              "power_law": fitp, "power_law_paper_exponent": 0.25, "log_law": {**B.log_law_fit(afl.z, afl.U, 10.0, 400.0), "note": "an urban boundary layer over a 725 m model: a power law is the paper's description (exponent 1/4); the log-law fit is listed for completeness"},
              "method": "least squares on the 18 published heights (z full-scale metres, U in the tunnel's m/s); k is published only as k/UR^2 in the workbook (UR ambiguous, not carried to approach_flow.csv)"}
    normalisation = {"quantity": "velocity_ratio = U / U_ref, U_ref = the approaching mean wind speed at 500 m (the boundary-layer height), full scale; field values were converted to it by the tunnel (readme)",
                     "U_ref_m_s": "10 (data paper) or 10.65 (profile implied); see inflow",
                     "conversion_from_the_workbook": {"SMB sector (NW, NNW, N, NNE, NE; roof anemometer G.L.+237 m)": {"factor": f["SMB"], "interval": list(fint["SMB"])},
                                                      "KDD sector (all other directions; roof anemometer G.L.+187 m)": {"factor": f["KDD"], "interval": list(fint["KDD"])},
                                                      "meaning": "workbook ratio x factor = CSV ratio; factor = U(roof anemometer) / U(500 m) from the N (SMB) or S (KDD) tunnel test (readme); the factors themselves are not stated in the sources (QUESTIONS.md QF8)"},
                     "velocity_ratio_sd": "standard deviation of the 10-minute mean ratios behind one field value (cup anemometer, only 10-minute means above 5 m/s at the reference); published to 3 dp, quantised at f/100",
                     "field_height": "z of each field row is the anemometer height above the tunnel floor (13 ... 21 m); the tunnel planes are 15, 19 and 30 m"}
    frame = {"origin": "centre of the reproduced district, in the tunnel's floor plane (MP_caseF.png 'Origin')", "x": "+x EAST (compass rose in MP_caseF.png)", "y": "+y NORTH",
             "z": f"+z up from the TUNNEL FLOOR, full scale; the readme's rule is height above ground = z - {GROUND_OFFSET:g} m (the model was raised, QUESTIONS.md QF4); tunnel planes at z = 15 / 19 / 30 m, field anemometers at z = 13 ... 21 m",
             "wind_direction_rotation": "compass FROM-direction (N = 0, E = 90): N blows toward -y; flow_dir = (-sin WD, -cos WD). Not defined in the readme; the reference-building choice (SMB for NW-NE) and the upwind-roughness check support it, and at NNW a solved field corroborates it (status 'corroborated by a solved field'; the other directions stay 'unverified').",
             "length_scale": "FULL-scale metres (model 1:800): the tunnel's model-scale coordinates and the STL are multiplied by 800; the field's are published in full scale"}
    transform = {"coordinate_scale": SCALE, "lateral_sign": 1, "origin_shift_m": [0, 0, 0], "geometry_scale": SCALE,
                 "note": "tunnel x, y, z x800; field coordinates unchanged; U/R and sigma as published except the 16 field rows of point 14 (re-derived from the workbook); STL x800 and re-wound outward"}
    known = {
        "field_point_14_directions_shifted": {"summary": "RS-FO_caseF.csv: the 16 rows of point 14 hold the workbook's value of the next direction clockwise (N holds NNE, ..., NNW holds N); this release uses the workbook's alignment (QUESTIONS.md QF1)",
                                              "rows": published14},
        "tunnel_8_SW_9m": {"published_U_R": nolegacy[0][2] if nolegacy else None, "workbook_Sheet1": s1v.get((8, "SW")), "workbook_Results": None},
        "workbook_other_column": {"values": len(other), "ESE_points": esb},
        "mp_csv_reference_labels_swapped": {"mp_csv_SMB_xy_m": list(mpn["SMB"]), "mp_csv_KDD_xy_m": list(mpn["KDD"]), "workbook_SMB_xy_m": list(ref[smb_wb][:2]), "workbook_KDD_xy_m": list(ref[kdd_wb][:2])},
        "stl": {"raw_model_scale_stats": s_raw, "as_published": {"horizontal_facets_down": down0, "horizontal_facets_up": up0}, "terrain_z_under_the_points_m": 5.0, "disc_radius_m": rmax},
        "workbook_band_asymmetry_rows": [f"{k[0]}/{k[1]}: {a:+.2f}" for k, a in asym],
    }
    extra = {"known_issues": known, "normalisation": normalisation, "conversion_factors": {"SMB": f["SMB"], "KDD": f["KDD"]}}
    return pts, afl, geo, inflow, frame, transform, extra


# The one direction a solved field has decided (Eddy3D, OpenFOAM 12, realizable k-epsilon, 2,143,488 cells, wind from NNW, 2026-10-18): the solved field correlates R 0.935 with the
# tunnel's 9 m column labelled NNW and R 0.077 with its column labelled SSE, the opposite wind, at the 13 points (R 0.945 and 0.102 probed at the STL's ground plus 9 m).
SOLVED_DIRECTION = "NNW"


def directions(B, pts):
    rows = []
    for (cfg, inst, wd, wname), g in pts.groupby(["config", "instrument", "wind_direction_deg", "wind_direction"], sort=True):
        r = math.radians(wd)
        fx, fy = -math.sin(r), -math.cos(r)
        basis = ("convention: compass FROM-direction, +y north (MP_caseF.png rose); supported by the reference-building choice (SMB for NW-NE) and by the upwind-roughness check "
                 "northern_points_see_faster_flow_for_the_S_labels_than_for_the_N_labels; the readme does not define it")
        status = "unverified (convention + data corroboration, not a solved field) — QUESTIONS.md QF9"
        if wname == SOLVED_DIRECTION:
            basis += ("; the solved Eddy3D field for the wind from this direction correlates R 0.935 with the tunnel's 9 m column for this label and R 0.077 with its column for the "
                      "opposite label (SSE), so it corroborates the FROM reading (R 0.945 and 0.102 at the STL's ground plus 9 m)")
            status = "corroborated by a solved field — QUESTIONS.md QF9"
        rows.append({"case_id": "F", "config": cfg, "instrument": inst, "wind_direction_deg": wd, "wind_direction": wname,
                     "flow_dir_x": round(fx, 9) + 0.0, "flow_dir_y": round(fy, 9) + 0.0, "rows": int(len(g)), "measured": int(g["velocity_ratio"].notna().sum()),
                     "sense_basis": basis, "status": status})
    return pd.DataFrame(rows)
