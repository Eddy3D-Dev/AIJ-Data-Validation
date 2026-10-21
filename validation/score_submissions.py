"""Score a solver's values at the published probe points, the way the served Eddy3D results are scored.

    python validation/score_submissions.py submissions/my-solver            # a submission folder: checks it, scores every case
    python validation/score_submissions.py submissions/my-solver --out DIR  # ... and writes DIR/<case>.json (default: prints only)
    python validation/score_submissions.py --check submissions/my-solver    # the folder's layout only
    python validation/score_submissions.py --self-test                      # every served run re-scored from its pairs: 1e-9

Run from a checkout of the repository; nothing to install beyond pyproject.toml (NumPy; uv sync). The measured side is the
cleaned table (clean/cases/<id>/points.csv), the scores are validation/dispersion_metrics.py, the transcription of
Eddy3D's MetaFOAM.DispersionMetrics that scores every served result, so a score from here agrees with a served score
to 1e-9 (--self-test proves it on every served run; scripts/build_all.sh runs it). scripts/build_api.py imports this
module to score the folders under submissions/ in the build, so a submission scores in CI exactly as here.

A submission folder is submissions/<slug>/submission.yaml (flat `key: value`; solver, version, url, author, licence,
contact, inlet, mesh, turbulence_model or ml_description, compute; optional example, units, notes) and
cases/<id>/probes.csv: the key columns of the served cases/<id>/probes.csv (point_id, and config, campaign, instrument,
run, wind_direction_deg as the case has them) plus any of the value columns U V W speed k cstar theta T.

Conventions, the same as docs/validation/method.md and the fixtures:
  - velocities over U_ref, k over U_ref^2 (units: normalised, the default: the file already is; si: divided here);
  - U, V, W, the speed |U| and the thermistor bracket are scored as signed velocities (FAC2's ratio carries the sign; hit rate D = 0.25, W = 0.05);
  - k by the plain definitions (hit rate D = 0.25 only);
  - a thermistor, cup or sonic reading (a mean scalar speed) is scored twice, against |U| (vs.vector) and sqrt(|U|^2 + 2k) (vs.scalar);
  - c* with one detection limit per case, 1e-3 of the largest measured value;
  - theta = (T_floor - T)/(T_floor - T_H), scored like a positive velocity.
A user row joins every measured row that agrees on the key columns the user's file has, so a file without `instrument`
scores against every instrument at that point. A score is computed per group (one configuration and wind direction).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import dispersion_metrics as DM  # noqa: E402

KEY_COLUMNS = ["config", "campaign", "instrument", "run", "wind_direction_deg", "point_id"]
GROUP_COLUMNS = ["config", "campaign", "run", "wind_direction_deg"]   # a group is one configuration and wind direction; its instruments pool
VALUE_COLUMNS = ["U", "V", "W", "speed", "k", "cstar", "theta", "T"]
UNITS = ("normalised", "si")

# The reference speed the measured side is divided by, per case: the case's own U_H where the table is in m/s; none where the
# table already holds ratios (E, F, G). Case M's tunnel run is normalised by the paper's U_R at the reference mast.
U_REF = {
    "A": (4.491, "U_H, the approach speed at the building height H = 0.16 m"),
    "B": (5.133, "U_H, the approach speed at the slab height H = 0.20 m"),
    "C": (3.654, "U_H = U(z = D = 0.20 m) of the approach flow"),
    "D": (6.65, "U_H, the approach speed at the tower height"),
    "E": (None, "the table holds Vs/U(15.9 m) (U(15.9 m) = 3.935 m/s); give ratios"),
    "F": (None, "the table holds the mean speed over U(500 m); give ratios over your own U(500 m) of the approach flow"),
    "G": (None, "the table holds U/U_H and k/U_H^2 with U_H the wind at the tree height (7 m); give ratios over your own U(7 m) upwind"),
    "H": (3.226, "U_H, the approach speed at the building height H = 0.2 m"),
    "I": (1.7, "U_H, the approach speed at the cube height"),
    "J": (1.4581, "U_H, the approach speed at the building height (the tunnel's units)"),
    "K": (2.33, "the stated U_H"),
    "L": (1.339415, "U_H, the approach speed at the cube height (the tunnel's units)"),
    "M": (4.08, "U_R, the tunnel's speed at the reference mast (the field rows carry their own U_R per run)"),
}
THETA = {
    "J": {"T_floor_degC": 318.95 - 273.15, "delta_T_K": 318.95 - 285.32, "meaning": "T_floor = 318.95 K, T_H = 285.32 K (the approach air at the building height)"},
    "L": {"T_floor_degC": 45.009118949967807, "delta_T_K": 30.256731727745589, "meaning": "T_floor = 45.01 degC, T_floor - T_H = 30.26 K (the workbook's values at full precision)"},
}
CONVENTIONS = ("velocities and the speed over U_ref, k over U_ref^2 (Cases E, F and G publish ratios already); U, V, W, |U| and the thermistor "
               "bracket scored as signed velocities (FAC2's ratio keeps the sign; hit rate D = 0.25, W = 0.05); k by the plain definitions (D = 0.25 only); "
               "a thermistor, cup or sonic reading (a mean scalar speed) scored against |U| (vs.vector) and sqrt(|U|^2 + 2k) (vs.scalar), the two ends "
               "of its bracket; c* = C/c0 with one detection limit per case, 1e-3 of the largest measured value; theta = (T_floor - T)/(T_floor - T_H) "
               "scored like a positive velocity. The same conventions score the served Eddy3D results (docs/validation/method.md).")


def theta_score(o, p):
    """The floor-referenced temperature fraction: positive, hit rate with D = 0.25 and W = 0.05 (plot_cases_jl_umf.py theta_score)."""
    return DM.evaluate(o, p, DM.D_HIT, DM.W_VELOCITY)


# key in results.json -> (label, the measured family, the scorer)
QUANTITIES = [
    ("velocity.U", "U", "vector", DM.velocity), ("velocity.V", "V", "vector", DM.velocity), ("velocity.W", "W", "vector", DM.velocity),
    ("speed", "|U|", "vector", DM.velocity),
    ("k", "k", "k", DM.turbulence),
    ("vs.scalar", "√(|U|²+2k)", "thermistor_bracket", DM.velocity), ("vs.vector", "|U|", "thermistor_bracket", DM.velocity),
    ("cstar", "c*", "concentration", DM.concentration),
    ("theta", "θ", "theta", theta_score),
]


def scoring_block(case):
    """What cases/{id}.json serves under `scoring`: the constants this module scores the case with."""
    u, meaning = U_REF[case]
    return {
        "U_ref_m_s": u, "U_ref_meaning": meaning, "theta": THETA.get(case),
        "scored_as": {"vector": "U, V, W and the speed |U| against the split-fibre, LDV or hot-wire components (velocity.U, velocity.V, velocity.W, speed)",
                      "k": "the turbulent kinetic energy (k)",
                      "thermistor_bracket": "a mean scalar speed (thermistor, cup or sonic anemometer) against |U| (vs.vector) and sqrt(|U|^2 + 2k) (vs.scalar)",
                      "concentration": "the dimensionless concentration c* = C/c0 (cstar)",
                      "theta": "the floor-referenced temperature fraction (theta)"},
        "value_columns": VALUE_COLUMNS, "key_columns": KEY_COLUMNS, "conventions": CONVENTIONS,
        "tool": "uv run python validation/score_submissions.py <folder>, from a checkout of the repository (pyproject.toml)",
    }


# ----------------------------------------------------------------------------- tables

def read_table(text):
    """Rows of a CSV: numbers as float, empty cells as None, other text as text."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        d = {}
        for k, v in r.items():
            if k is None:
                continue
            v = (v or "").strip()
            if v == "":
                d[k] = None
            else:
                try:
                    d[k] = float(v)
                except ValueError:
                    d[k] = v
        out.append(d)
    return out


def read_table_file(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return read_table(f.read())


def clean_points(case):
    return read_table_file(os.path.join(REPO, "clean", "cases", case, "points.csv"))


def _key(row, columns):
    out = []
    for c in columns:
        v = row.get(c)
        if v is None or v == "":
            out.append("")
        elif c in ("wind_direction_deg", "point_id"):
            out.append(f"{float(v):.6g}")
        else:
            out.append(str(v))
    return tuple(out)


def _num(v):
    try:
        return float(v) if v not in (None, "") else math.nan
    except (TypeError, ValueError):
        return math.nan


# ----------------------------------------------------------------------------- the two sides of a pair

def measured_values(row, scoring):
    """What the benchmark measured at this row, in the scored units: U V W speed (vector), k, Vs (the scalar speed), cstar, theta."""
    u = scoring.get("U_ref_m_s")
    out = {}
    if row.get("U") is not None and u:
        U, V, W = (_num(row.get(c)) for c in "UVW")
        out.update({"U": U / u, "V": V / u, "W": W / u, "speed": math.sqrt(U * U + V * V + W * W) / u})
    if row.get("k") is not None and u:
        out["k"] = _num(row["k"]) / (u * u)
    elif row.get("k_ratio") is not None:
        out["k"] = _num(row["k_ratio"])
    if row.get("Vs") is not None and u:
        out["Vs"] = _num(row["Vs"]) / u
    elif row.get("velocity_ratio") is not None:
        out["Vs"] = _num(row["velocity_ratio"])
    if row.get("concentration_ratio") is not None:
        out["cstar"] = _num(row["concentration_ratio"])
    th = scoring.get("theta")
    if th and row.get("T") is not None:
        out["theta"] = (th["T_floor_degC"] - _num(row["T"])) / th["delta_T_K"]
    return out


def families(measured):
    """The scored_as families a measured row belongs to."""
    fam = []
    if "U" in measured:
        fam.append("vector")
    if "Vs" in measured:
        fam.append("thermistor_bracket")
    if "cstar" in measured:
        fam.append("concentration")
    if "theta" in measured:
        fam.append("theta")
    return fam


def model_values(row, scoring, units, u_ref=None):
    """The user's values at a row, in the scored units: U V W speed rms k cstar theta (NaN where not given)."""
    u = u_ref or scoring.get("U_ref_m_s")
    if units == "si" and not u:
        raise ValueError("units: si needs a reference speed: the case states none (its data are ratios); give normalised values")
    U, V, W, speed, k, cstar, theta, T = (_num(row.get(c)) for c in VALUE_COLUMNS)
    if units == "si":
        U, V, W, speed, k = U / u, V / u, W / u, speed / u, k / (u * u)
    if math.isnan(speed) and not (math.isnan(U) or math.isnan(V) or math.isnan(W)):
        speed = math.sqrt(U * U + V * V + W * W)
    rms = math.sqrt(speed * speed + 2 * k) if not (math.isnan(speed) or math.isnan(k)) else math.nan
    th = scoring.get("theta")
    if math.isnan(theta) and th and not math.isnan(T):
        theta = (th["T_floor_degC"] - T) / th["delta_T_K"]
    return {"U": U, "V": V, "W": W, "speed": speed, "rms": rms, "k": k, "cstar": cstar, "theta": theta}


_NO_MODEL = {"U": math.nan, "V": math.nan, "W": math.nan, "speed": math.nan, "rms": math.nan, "k": math.nan, "cstar": math.nan, "theta": math.nan}
_PAIR = {"velocity.U": ("U", "U"), "velocity.V": ("V", "V"), "velocity.W": ("W", "W"), "speed": ("speed", "speed"), "k": ("k", "k"),
         "vs.scalar": ("Vs", "rms"), "vs.vector": ("Vs", "speed"), "cstar": ("cstar", "cstar"), "theta": ("theta", "theta")}


def _pairs_of(quantity, measured, model):
    m, p = _PAIR[quantity]
    return measured.get(m), model[p]


def group_key(row, varying):
    parts = []
    for c in varying:
        v = row.get(c)
        if v in (None, ""):
            continue
        parts.append(f"wd{float(v):g}" if c == "wind_direction_deg" else str(v))
    return ".".join(parts)


# ----------------------------------------------------------------------------- scoring

def score(case, measured_rows, model_rows, engine="mine", units="normalised", u_ref=None):
    """Every quantity the user's file allows, per group (configuration and wind direction), with the coverage of each."""
    if units not in UNITS:
        raise ValueError(f"units must be one of {UNITS}")
    scoring = scoring_block(case)
    user_keys = [c for c in KEY_COLUMNS if model_rows and c in model_rows[0]]
    if "point_id" not in user_keys:
        raise ValueError("the file needs a point_id column (copy cases/{id}/probes.csv and add your values)")
    given = [c for c in VALUE_COLUMNS if model_rows and c in model_rows[0]]
    if not given:
        raise ValueError(f"the file has none of the value columns {' '.join(VALUE_COLUMNS)}")
    varying = [c for c in GROUP_COLUMNS if len({_key(r, [c]) for r in measured_rows}) > 1]

    by_key = {}
    for r in measured_rows:
        by_key.setdefault(_key(r, user_keys), []).append(r)
    joined = {}            # measured row id -> (measured row, model values)
    unmatched = 0
    for u in model_rows:
        hits = by_key.get(_key(u, user_keys), [])
        if not hits:
            unmatched += 1
        mv = model_values(u, scoring, units, u_ref)
        for m in hits:
            joined[id(m)] = (m, mv)

    groups = {}
    for m in measured_rows:
        g = group_key(m, varying)
        groups.setdefault(g, {"group": {c: m.get(c) for c in varying}, "measured": [], "joined": []})
        groups[g]["measured"].append(m)
        if id(m) in joined:
            groups[g]["joined"].append(joined[id(m)])

    out_groups, flat, coverage, headline = [], {}, {}, {}
    for g, grp in groups.items():
        scores, cov = {}, {}
        for key, label, family, fn in QUANTITIES:
            n_measured = sum(1 for m in grp["measured"] if _pairs_of(key, measured_values(m, scoring), _NO_MODEL)[0] is not None)
            o, p = [], []
            for m, mv in grp["joined"]:
                ob, pr = _pairs_of(key, measured_values(m, scoring), mv)
                if ob is not None:
                    o.append(ob)
                    p.append(pr)
            o, p = np.asarray(o, float), np.asarray(p, float)
            ok = np.isfinite(o) & np.isfinite(p)
            if not ok.any():
                continue
            scores[key] = fn(o, p)
            cov[key] = {"scored": int(ok.sum()), "measured": n_measured}
            fk = f"{g}/{key}" if g else key
            flat[fk], coverage[fk] = scores[key], cov[key]
            headline[(f"{g}: " if g else "") + label] = fk
        if scores:
            out_groups.append({"key": g, "group": grp["group"], "points_measured": len(grp["measured"]), "scores": scores, "coverage": cov})
    return {
        "case": case, "engine": engine,
        "units_given": units, "U_ref_m_s": u_ref or scoring.get("U_ref_m_s"), "U_ref_meaning": scoring.get("U_ref_meaning"),
        "conventions": CONVENTIONS,
        "value_columns_given": given, "key_columns_given": user_keys, "model_rows": len(model_rows), "model_rows_unmatched": unmatched,
        "groups": out_groups, "headline": headline, "scores": flat, "coverage": coverage,
    }


# ----------------------------------------------------------------------------- a submission folder

REQUIRED = ["solver", "version", "url", "author", "licence", "contact", "inlet", "mesh", "compute"]
ONE_OF = ("turbulence_model", "ml_description")
OPTIONAL = ["example", "units", "notes", "turbulence_model", "ml_description"]
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
CASE = re.compile(r"^[A-M]$")


def read_yaml(text):
    """shortcut: flat key: value only (no nesting, no lists); upgrade to PyYAML (pin it in pyproject.toml) if a submission ever needs structure."""
    out = {}
    for n, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if ":" not in s:
            raise ValueError(f"line {n}: not `key: value`")
        k, v = s.split(":", 1)
        v = v.strip()
        if " #" in v and not (v.startswith('"') or v.startswith("'")):
            v = v.split(" #", 1)[0].strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        elif v.lower() in ("true", "false"):
            v = v.lower() == "true"
        elif re.fullmatch(r"-?\d+", v):
            v = int(v)
        elif re.fullmatch(r"-?\d+\.\d*|-?\d*\.\d+", v):
            v = float(v)
        out[k.strip()] = v
    return out


def check_folder(folder):
    """(problems, meta, {case: rows}) for a submission folder; problems is empty when it is a valid submission."""
    problems, meta, cases = [], {}, {}
    slug = os.path.basename(os.path.abspath(folder))
    if not SLUG.match(slug):
        problems.append(f"folder name {slug!r} is not a slug (lower-case letters, digits and hyphens, 2 to 64 characters)")
    y = os.path.join(folder, "submission.yaml")
    if not os.path.isfile(y):
        return problems + ["submission.yaml is missing"], meta, cases
    with io.open(y, encoding="utf-8") as f:
        try:
            meta = read_yaml(f.read())
        except ValueError as e:
            return problems + [f"submission.yaml: {e}"], meta, cases
    for k in REQUIRED:
        if k not in meta or meta[k] in ("", None):
            problems.append(f"submission.yaml: {k} is missing")
    if not any(meta.get(k) for k in ONE_OF):
        problems.append("submission.yaml: give turbulence_model (a CFD solver) or ml_description (a learned model)")
    unknown = sorted(set(meta) - set(REQUIRED) - set(OPTIONAL))
    if unknown:
        problems.append(f"submission.yaml: unknown keys {unknown}")
    if meta.get("units", "normalised") not in UNITS:
        problems.append("submission.yaml: units must be normalised or si")
    if "example" in meta and not isinstance(meta["example"], bool):
        problems.append("submission.yaml: example must be true or false")
    cdir = os.path.join(folder, "cases")
    if not os.path.isdir(cdir):
        return problems + ["cases/ is missing"], meta, cases
    for case in sorted(os.listdir(cdir)):
        if case.startswith("."):
            continue
        if not CASE.match(case):
            problems.append(f"cases/{case}: not a case id (A to M)")
            continue
        p = os.path.join(cdir, case, "probes.csv")
        if not os.path.isfile(p):
            problems.append(f"cases/{case}/probes.csv is missing")
            continue
        with io.open(p, encoding="utf-8-sig") as f:
            text = f.read()
        header = next(csv.reader(io.StringIO(text)), [])
        if "point_id" not in header:
            problems.append(f"cases/{case}/probes.csv: no point_id column")
        if not any(c in VALUE_COLUMNS for c in header):
            problems.append(f"cases/{case}/probes.csv: none of the value columns {' '.join(VALUE_COLUMNS)}")
        extra = [c for c in header if c not in KEY_COLUMNS + VALUE_COLUMNS + ["x", "y", "z", "scored_as"]]
        if extra:
            problems.append(f"cases/{case}/probes.csv: unknown columns {extra}")
        rows = read_table(text)
        if not rows:
            problems.append(f"cases/{case}/probes.csv: no rows")
        cases[case] = rows
    if not cases and not problems:
        problems.append("cases/ holds no case")
    return problems, meta, cases


def score_folder(folder, out_dir=None, points=None):
    """{case: result} of a submission folder (raises on a problem); the results go to out_dir/<case>.json when given (LF, no NaN)."""
    problems, meta, cases = check_folder(folder)
    if problems:
        raise SystemExit(f"{folder}: " + "; ".join(problems))
    slug = os.path.basename(os.path.abspath(folder))
    results = {}
    for case, rows in cases.items():
        measured = points[case] if points else clean_points(case)
        res = score(case, measured, rows, engine=slug, units=meta.get("units", "normalised"))
        if res["model_rows_unmatched"]:
            raise SystemExit(f"{folder}/cases/{case}/probes.csv: {res['model_rows_unmatched']} row(s) match no published point (check the key columns)")
        if not res["scores"]:
            raise SystemExit(f"{folder}/cases/{case}/probes.csv: nothing could be scored")
        results[case] = res
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            with io.open(os.path.join(out_dir, f"{case}.json"), "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(res, indent=1, ensure_ascii=False, allow_nan=False) + "\n")
    return meta, results


def print_results(results):
    for case, res in results.items():
        print(f"Case {case}:")
        for key, s in res["scores"].items():
            c = res["coverage"][key]
            r = "   —  " if s["R"] is None else f"{s['R']:+.3f}"
            fb = "   —  " if s["Fb"] is None else f"{s['Fb']:+.3f}"
            print(f"  {key:36s} R {r}  FAC2 {s['Fac2']:.3f}  FB {fb}  HR {s['HitRate']:.3f}  n {s['Count']} ({c['scored']}/{c['measured']} points)")


# ----------------------------------------------------------------------------- self-test: every served run from its pairs

COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
SCT = ("sct03", "sct05", "sct07")
# Case E's served scores were computed by the Eddy3D fixture from the published CSV, whose ratios round the workbook's (the point
# table here is the workbook at full precision; docs/validation/method.md says so): its means agree to 1e-7, so 1e-6 is the claim there.
TOLERANCE = {"E": 1e-6}
NOT_COVERED = ("controls (sign flips, mirrored frames, ceilings, reversed wind), subsets (comparable heights, points above two cells, without the "
               "near-source points, at or above 30 mm, by plane over all planes), re-normalisations by an imposed reference speed, Case M's field "
               "comparison, Case D's split-fibre |U| (the fixture rounded it from the published CSV), and the ML surrogate's runs, whose pairs carry no point ids")


def _half_k(scalar, vector):
    """k from the two ends of the thermistor bracket: sqrt(|U|^2 + 2k)^2 - |U|^2 = 2k."""
    return None if scalar is None or vector is None else (scalar * scalar - vector * vector) / 2


def _rows_hik(pairs, sp, extra=()):
    return [{"point_id": r["point_id"], **({"instrument": r["instrument"]} if "instrument" in r else {}),
             "U": r["U_model"], "V": r["V_model"], "W": r["W_model"], "k": r["k_model"], "cstar": r[f"cstar_{sp}"],
             **{k: r[v] for k, v in extra}} for r in pairs]


def _served_runs(api):
    """[(run_id, served result, user rows, {key here: served score key})]: one entry per served run this module reproduces."""
    out = []
    with io.open(os.path.join(api, "index.json"), encoding="utf-8") as f:
        case_ids = json.load(f)["case_ids"]
    for case in case_ids:
        with io.open(os.path.join(api, "cases", case, "validation.json"), encoding="utf-8") as f:
            val = json.load(f)
        for res in val["results"]:
            if res["pairs"] is None or res["engine"] == "ml-surrogate":
                continue
            pairs = read_table_file(os.path.join(api, *res["pairs"]["path"].split("/")))
            cfg, rid = res["configuration"], res["run_id"]
            if case in "AB":
                rows = [{"point_id": r["point_id"], "U": r["U_model"], "V": r["V_model"], "W": r["W_model"]} for r in pairs]
                want = ({"velocity.U": "velocity.U.all"} if res["engine"] == "fluidx3d" else
                        {"velocity.U": "velocity.U", "velocity.V": "velocity.V", "velocity.W": "velocity.W"})
                out.append((rid, res, rows, want))
            elif case == "C":
                rows = [{"config": r["config"], "wind_direction_deg": r["wind_direction_deg"], "point_id": r["point_id"],
                         "speed": r["vector_over_UH"], "k": _half_k(r["scalar_over_UH"], r["vector_over_UH"])} for r in pairs if r["config"] == cfg]
                want = {}
                for wd, lab in ((0.0, "wd-0"), (22.5, "wd22_5"), (45.0, "wd45")):
                    want[f"{cfg}.wd{wd:g}/vs.scalar"], want[f"{cfg}.wd{wd:g}/vs.vector"] = f"vs.{lab}.scalar", f"vs.{lab}.vector"
                out.append((rid, res, rows, want))
            elif case == "D":
                rows = []
                for r in pairs:
                    d = {"instrument": r["instrument"], "wind_direction_deg": r["wind_direction_deg"], "point_id": r["point_id"],
                         "speed": r["vector_over_UH"], "k": _half_k(r["scalar_over_UH"], r["vector_over_UH"])}
                    if r["instrument"] == "split_fibre":
                        d.update({"U": r["U_model"], "V": r["V_model"], "W": r["W_model"], "k": None})
                    rows.append(d)
                want = {"wd0/velocity.U": "splitfibre.U"}
                for wd in (0, 22.5, 45):
                    want[f"wd{wd:g}/vs.scalar"], want[f"wd{wd:g}/vs.vector"] = f"vs.{wd:g}.corrected", f"vs.{wd:g}.uncorrected"
                out.append((rid, res, rows, want))
            elif case == "E":
                rows = [{"config": r["config"], "wind_direction_deg": 22.5 * COMPASS.index(r["wind_direction"]), "point_id": r["point_id"],
                         "speed": r["vector_ratio"], "k": _half_k(r["scalar_ratio"], r["vector_ratio"])} for r in pairs]
                wd = 22.5 * COMPASS.index(cfg)
                want = {f"{st}.wd{wd:g}/vs.scalar": f"vr.{st}.{cfg}.rms" for st in ("bc", "ac")}
                want.update({f"{st}.wd{wd:g}/vs.vector": f"vr.{st}.{cfg}.Umag" for st in ("bc", "ac")})
                out.append((rid, res, rows, want))
            elif case == "F":
                plane = {"5": "h5", "9": "default", "20": "h20"}
                rows = []
                for r in pairs:
                    if r["frame"] != cfg:
                        continue
                    tunnel = r["source"] == "tunnel"
                    rows.append({"config": plane[f"{r['plane_m']:g}"] if tunnel else "default", "campaign": "wind_tunnel" if tunnel else "field",
                                 "wind_direction_deg": 337.5, "point_id": r["point_id"], "speed": r["Umag_model"], "k": _half_k(r["rms_model"], r["Umag_model"])})
                want = {}
                for p, c in plane.items():
                    want[f"{c}.wind_tunnel.wd337.5/vs.vector"], want[f"{c}.wind_tunnel.wd337.5/vs.scalar"] = f"tunnel.{p}m.Umag", f"tunnel.{p}m.rms"
                want.update({"default.field.wd337.5/vs.vector": "field.Umag", "default.field.wd337.5/vs.scalar": "field.rms"})
                out.append((rid, res, rows, want))
            elif case == "G":
                rows = [{"point_id": r["point_id"], "speed": r["U_model"], "k": r["k_model"]} for r in pairs if r["arm"] == cfg]
                out.append((rid, res, rows, {"vs.vector": "score.U.ownApproach", "vs.scalar": "score.rms.ownApproach", "k": "score.k.ownApproach"}))
            elif case in ("H", "I", "K"):
                for sp in SCT:
                    out.append((f"{rid}.{sp}", res, _rows_hik(pairs, sp),
                                {"velocity.U": "velocity.U", "velocity.V": "velocity.V", "velocity.W": "velocity.W", "k": "k", "cstar": f"cstar.c_{sp}"}))
            elif case == "J":
                for sp in SCT:
                    out.append((f"{rid}.{sp}", res, _rows_hik(pairs, sp, [("theta", "theta_model")]),
                                {"velocity.U": "velocity.U", "velocity.V": "velocity.V", "velocity.W": "velocity.W", "k": "k", "theta": "theta", "cstar": f"cstar.c_{sp}"}))
            elif case == "L":
                for sp in SCT:
                    out.append((f"{rid}.{sp}", res, _rows_hik(pairs, sp, [("theta", "theta_model"), ("speed", "S_model")]),
                                {"velocity.U": "velocity.U", "velocity.V": "velocity.V", "velocity.W": "velocity.W", "speed": "speed", "k": "k",
                                 "theta": "theta", "cstar": f"cstar.c_{sp}"}))
            elif case == "M":
                rows = []
                for r in pairs:
                    base = {"campaign": "wind_tunnel", "wind_direction_deg": 180, "point_id": r["point_id"]}
                    rows.append({**base, "instrument": "split_fibre", "U": r["U_model"], "V": r["V_model"], "W": r["W_model"], "speed": r["speed_model"], "k": r["k_model"]})
                    rows.append({**base, "instrument": "hydrocarbon_analyser", "cstar": r[f"cstar_{cfg}"]})
                g = "wind_tunnel.wd180"
                out.append((rid, res, rows, {f"{g}/velocity.U": "velocity.U", f"{g}/velocity.V": "velocity.V", f"{g}/velocity.W": "velocity.W",
                                             f"{g}/speed": "velocity.magnitude", f"{g}/k": "k", f"{g}/cstar": "cstar"}))
    return out


def self_test(api=None):
    """Every served run, re-scored from its pairs through score(): the headline scores come back to 1e-9 (Case E 1e-6), or it fails."""
    api = api or os.path.join(REPO, "docs", "api")
    points = {}
    checked, runs = 0, 0
    for rid, res, rows, want in _served_runs(api):
        case = res["run_id"][0]
        if case not in points:
            points[case] = read_table_file(os.path.join(api, "cases", case, "points.csv"))
        got = score(case, points[case], rows, engine=res["engine"])
        assert got["model_rows_unmatched"] == 0, (rid, "rows without a measured point")
        for mine, theirs in want.items():
            assert mine in got["scores"], (rid, mine, sorted(got["scores"]))
            assert theirs in res["headline"].values(), (rid, theirs)
            a, b = got["scores"][mine], res["scores"][theirs]
            assert DM.same(a, b, tol=TOLERANCE.get(case, 1e-9), fixture=True), (rid, mine, theirs, a, b)
            checked += 1
        runs += 1
    assert checked > 150, checked
    print(f"score_submissions: {checked} headline scores of {runs} served runs reproduced from their pairs to 1e-9 (Case E: 1e-6); not covered: {NOT_COVERED}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folder", nargs="?", help="a submission folder: submission.yaml and cases/<id>/probes.csv")
    ap.add_argument("--out", help="write <case>.json here (what the build writes under validation/results/submissions/<slug>/)")
    ap.add_argument("--check", action="store_true", help="the folder's layout only; no scoring")
    ap.add_argument("--self-test", action="store_true", help="re-score every served run from its pairs and compare")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.folder:
        ap.error("give a submission folder, or --self-test")
    problems, meta, cases = check_folder(a.folder)
    for p in problems:
        print(f"PROBLEM: {p}")
    if problems:
        raise SystemExit(1)
    print(f"{a.folder}: {meta['solver']} {meta['version']}, cases {', '.join(cases)}" + (" (example)" if meta.get("example") else ""))
    if a.check:
        return
    _, results = score_folder(a.folder, a.out)
    print_results(results)
    if a.out:
        print(f"written: {a.out}/<case>.json")
    print("ok: a valid submission; open a pull request that adds the folder under submissions/ (CONTRIBUTING.md)")


if __name__ == "__main__":
    main()
