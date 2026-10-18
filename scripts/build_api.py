"""Generate the static API under docs/api/ (and the generated site pages) from the cleaned data.

    python scripts/build_api.py            # build, then verify
    python scripts/build_api.py --check    # verify what is on disk; build nothing

Requirements: requirements.lock at the repository root (one pinned environment for every build here).

GitHub Pages serves docs/ at <site>/; every API file is a plain GET of a static file. The build is a pure
function of the repository: the same inputs give byte-identical outputs (no timestamps, no commit hashes),
so CI can rebuild and diff. Inputs:

- clean/                      the cleaned point tables (aijdata.load_points)
- the case folders            approach-flow profiles, Case D's STL, Case E's 3dm (aijdata)
- validation/results/         snapshots of the Eddy3D fixtures' results.json and per-point pairs, one entry
                              per run in RUNS below
- validation/figures/         the figures and geometry renders the site shows (1200 dpi masters)

Outputs: docs/api/** (the API), docs/assets/{figures,geometry}/ (the masters, copied), docs/assets/web/ (a 1600 px
copy of each, which the pages and the README embed, linked to its master), docs/_data/figures.json (their sizes, for
the include docs/_includes/figure.html), the figure blocks of README.md (between its <!--fig ...--> markers), docs/cases/<slug>.md and
docs/cases/<slug>/{data,validation}.md (three pages per case), docs/_includes/{case-gallery,cases-table,
cases-frames,validation-matrix,known-issues-fm,api-changelog}.md, docs/_includes/{version-label,dataset-jsonld}.html and
docs/llms.txt. Every JSON document names its JSON Schema in `$schema`; the schemas are in scripts/api_schemas.py
and are enforced here before anything is reported OK.

The API is served twice, by the same code. Each release is a frozen copy of the whole API under docs/api/<release>/
(<release> is VERSION), every URL inside it pointing back into it; docs/api/ itself is the latest alias, the same
files addressed without the release. docs/api/versions.json, the one file that belongs to neither, lists every
release. A build rewrites the copy of VERSION and the alias and never touches another release's copy (released
copies are immutable: scripts/release.py check compares them with their tags). A release from before the layout
(LEGACY_RELEASES) is not regenerated. verify() checks every tree on its own, that the alias is the newest release
file for file, and the registry.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import io
import json
import os
import re
import shutil
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aijdata as D  # noqa: E402
import api_schemas as S  # noqa: E402
import release as R  # noqa: E402

REPO = D.REPO
DOCS = os.path.join(REPO, "docs")
API_ROOT = os.path.join(DOCS, "api")   # the latest alias, versions.json, and one frozen <release>/ tree per release
ASSETS = os.path.join(DOCS, "assets")
WEB = os.path.join(ASSETS, "web")      # the 1600 px copies the pages and the README show; the 1200 dpi masters stay the downloads
DATA_FILES = os.path.join(DOCS, "_data")
WEB_WIDTH = 1600
FIGURES = os.path.join(REPO, "validation", "figures")
FIGURE_INFO = {}                       # file name -> what a page needs to embed the figure; filled by copy_assets()
RESULTS_DIR = os.path.join(REPO, "validation", "results")

REPO_URL = "https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ"
SITE = "https://sustainableurbansystems.com/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ"
LIVE_BASE = SITE + "/api"         # the unversioned alias: always the newest release
RAW_BASE = "https://raw.githubusercontent.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/main/docs/api"
SCHEMA_VERSION = "2.3.0"
RELEASE = R.version()             # the repository's release (VERSION); the API names it, it does not set it
RELEASE_DATE = R.release_date()
PINNED_BASE = f"{LIVE_BASE}/{RELEASE}"   # this release, frozen: nothing under it changes once the release is tagged
RELEASE_BASE = f"{RAW_BASE.replace('/main/', f'/v{RELEASE}/')}/{RELEASE}"   # the same frozen files, raw, at the tag

# Releases that predate the versioned layout. They are never regenerated. Their tree under docs/api/<release>/ is
# the tag's files with only their addresses rewritten (scripts/host_release.py); without one, the registry lists the
# tag and its raw files instead. Both values are the ones the release's own docs/api/index.json carries
# (git show v2.0.0:docs/api/index.json).
LEGACY_RELEASES = {
    "2.0.0": {"schema_version": "2.2.0", "data_version": "5af8c81571e452c1925b3efe58c698908066f64886eba5efd9b2f0348ecdc019"},
}

# State of the tree being written (see use_tree): build() writes the release tree, then the latest alias.
TREE = None              # "release" | "latest"
API = None               # the tree's directory
API_BASE = None          # the URL every document in the tree uses for its own files
FALLBACK_BASE = None     # the same tree, raw from the repository

CHANGELOG = [
    {"version": "2.3.0", "date": "2026-10-18", "changes": [
        "Added: release-numbered paths. Every release is a frozen copy of the whole API under `/api/<release>/` (for example "
        "`/api/3.0.0/index.json`, `/api/3.0.0/cases/F.json`). Every URL to a file of the API inside a copy points into the same copy "
        "(versions.json, served only at the unversioned path, aside), so a client that starts there never leaves it, and "
        "nothing under it changes once the release is tagged. The unversioned "
        "`/api/` paths are unchanged and always equal the newest release (the `latest` alias).",
        "Added: `/api/versions.json` (schema `versions`), the list of every release, newest first: version, date, status "
        "(`latest` or `superseded`), schema_version, data_version, base_url, tag, release page and changelog. Release 2.0.0 "
        "predates the layout and is not regenerated: `/api/2.0.0/` holds the files of its tag byte for byte, with only their "
        "own addresses rewritten into the copy (scripts/host_release.py derives it and the release check re-derives it).",
        "Added to index.json: `tree` (`release` in a frozen copy, `latest` in the alias), `release_base_url` (the frozen copy "
        "of `versions.release`; equal to `base_url` inside that copy) and `versions_url`. In a frozen copy `base_url` and "
        "`fallback_base_url` name that copy, and `release.base_url` (the raw files at the release tag) now ends in the "
        "release number; paths below it are unchanged.",
        "Added: Cases F to M, thirteen cases in all (the `case_ids` of index.json): their cases.json entries, `cases/{id}.json`, "
        "points, approach flow, geometry (STL) and validation documents, and `pairs` files for the runs that exist. Six of them "
        "(F, G, J, K, L, M) have no validation run yet: every engine is `pending` and `results` is empty. `cases.json` and "
        "`validation.json` list thirteen cases (the schemas fixed the length at five).",
        "Added: the point table's columns of schema 2.0.0 (the cleaned release) are served in `points.json` and `points.csv`: "
        "`campaign` and `run`, `uv` `uw` `vw`, `C` `c_rms` `concentration_ratio`, `T` `T_rms`, `uc` `vc` `wc`, `uT` `vT` `wT`, "
        "`velocity_ratio_sd` and `k_ratio`; `instrument` takes the new values `cup_anemometer`, `sonic_anemometer`, `ldv`, "
        "`hydrocarbon_analyser` and `sorbent_gc_ecd`. A document lists only the columns a case has.",
        "Added: two engines, `openfoam12-kEpsilon` and `openfoam12-kOmegaSST`, which exist for Case I only (the closures other than "
        "realizable k-epsilon, solved on one mesh). `engines` in `cases.json` and `cases/{id}.json` lists an engine only for the "
        "cases it applies to.",
        "Why MINOR: nothing is renamed or removed. Every unversioned URL and field keeps its meaning; the layout, the cases, "
        "documents, a schema, columns, engines and three index.json fields are additions.",
    ]},
    {"version": "2.2.0", "date": "2026-10-18", "changes": [
        "Added: `versions.release`, the semantic version of the published data and API (the repository's VERSION; "
        "tag vX.Y.Z; rules in CHANGELOG.md), and `release` with its date, tag, release page and `base_url`, the raw "
        "files of exactly that release (the tag never moves). `schema_version` stays the version of this JSON contract.",
    ]},
    {"version": "2.1.0", "date": "2026-10-15", "changes": [
        "Correction: index.json gave each templated endpoint (cases/{id}.json, schemas/{name}.schema.json, ...) its "
        "URI template under `url`, which is not a URL and answered 404 when followed. A templated endpoint now says "
        "`templated: true` and lists every concrete file under `urls`; `url` is given only for single-file "
        "endpoints, and no URL anywhere contains a brace. llms.txt lists the concrete files the same way.",
    ]},
    {"version": "2.0.0", "date": "2026-10-15", "changes": [
        "Breaking: cases/{id}.json `gotchas` is renamed `known_issues`.",
        "Breaking: `licence` is replaced by `license`, the SPDX identifier CC-BY-4.0; index.json `licence_detail` is `license_detail`.",
        "Breaking: `generated_from` and `generated_at` are removed. `data_version`, a SHA-256 over every served measurement, "
        "geometry and score file, changes when, and only when, the data does; the build is reproducible byte for byte.",
        "Breaking: links to JSON resources are named `url` (was `file`, `endpoint`, `endpoint_json`); file downloads are objects "
        "with `url`, `path`, `media_type`, `bytes` and `sha256` (points `csv`, approach-flow `csv`, run `pairs`, geometry files, "
        "the archive, and every entry of index.json `files`).",
        "Breaking: a validation result's `figures` is a list of {url, caption}.",
        "Added: validation.json, every case and engine in one table with each run's headline scores.",
        "Added: cases/{id}/pairs/{engine}.csv, the per-point measured and modelled values behind every scored run, so any score "
        "can be recomputed; linked from each result as `pairs`.",
        "Added: cases/{id}/approach_flow.csv, the measured approach-flow profile in SI units.",
        "Added: schemas/{name}.schema.json, the JSON Schema (draft 2020-12) of every document, named by its `$schema` and "
        "embedded in openapi.json.",
        "Added: `run_id` on every validation result; geometry renders and captions in geometry.json.",
        "Added: download URLs carry `?v=<SHA-256 prefix>`, so a changed file has a new URL and no cache serves a stale copy.",
        "Added: /llms.txt at the site root, and schema.org Dataset metadata on the home page.",
    ]},
    {"version": "1.0.0", "date": "2026-10-14", "changes": ["First release."]},
]
COMPATIBILITY = ("Semantic versioning, twice. `versions.release` versions what is served (MAJOR: a file, field or "
                 "column renamed or removed, or a unit or frame changed; MINOR: something added; PATCH: a value "
                 "corrected). Every release is also a frozen copy of the whole API under `/api/<release>/` whose files never "
                 "change (`release_base_url`; all releases in versions.json), and the unversioned /api/ paths always equal "
                 "the newest release: pin an analysis to a release by using that release's base URL. "
                 "`schema_version` versions this JSON contract: within a major version it only adds new fields, "
                 "endpoints and runs, clients must ignore fields they do not know, and a field is renamed or removed "
                 "only in a new major version, which the changelog names. `data_version` is a fingerprint, not a "
                 "version: the SHA-256 of the served data.")
CACHING = ("GitHub Pages sends JSON with a 10-minute max-age and CSV and ZIP files with a 186-day max-age. Every "
           "download URL therefore carries ?v=<first 12 hex digits of the file's SHA-256>: the server ignores the "
           "query, and a changed file gets a new URL. Fetch the JSON documents for the current URLs; check "
           "downloads against `sha256`.")

CASE_SPAN = f"{D.CASE_IDS[0]}-{D.CASE_IDS[-1]}"   # "A-M"

ENGINES = [
    {"id": "openfoam12-realizableKE", "name": "OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)", "kind": "RANS"},
    {"id": "openfoam12-kEpsilon", "name": "OpenFOAM 12, standard k-epsilon (Eddy3D Outdoor)", "kind": "RANS"},
    {"id": "openfoam12-kOmegaSST", "name": "OpenFOAM 12, k-omega SST (Eddy3D Outdoor)", "kind": "RANS"},
    {"id": "openlb", "name": "OpenLB (Eddy3D LBM)", "kind": "LBM"},
    {"id": "fluidx3d", "name": "FluidX3D (Eddy3D GPU LBM)", "kind": "LBM"},
    {"id": "ml-surrogate", "name": "Eddy3D ML wind surrogate (pedestrian height)", "kind": "surrogate"},
]
# "scored" says a run exists and its scores are served, NOT that it agrees; how well it agrees is in the numbers.
STATUS_MEANING = {
    "scored": "a validation run exists and its scores are in cases/{id}/validation.json; whether it agrees is in the numbers",
    "running": "the solve is in progress; no scores yet",
    "pending": "not run yet",
    "not comparable": ("the engine cannot produce the measured quantity at the measured location: OpenLB at the resolution "
                       "this hardware runs, FluidX3D without a ground wall function; the measurement behind each is on the "
                       "Validation page"),
}
# The closures other than realizable k-epsilon were solved for Case I alone: they are listed for the cases they apply to
# (ENGINE_STATUS has no entry for them elsewhere) and left out of the all-cases matrix.
CLOSURE_VARIANTS = {"openfoam12-kEpsilon", "openfoam12-kOmegaSST"}
_NOT_RUN = {"openfoam12-realizableKE": "pending", "openlb": "pending", "fluidx3d": "pending", "ml-surrogate": "pending"}
ENGINE_STATUS = {
    "A": {"openfoam12-realizableKE": "scored", "openlb": "scored", "fluidx3d": "scored", "ml-surrogate": "scored"},
    "B": {"openfoam12-realizableKE": "scored", "openlb": "scored", "fluidx3d": "scored", "ml-surrogate": "scored"},
    "C": {"openfoam12-realizableKE": "scored", "openlb": "not comparable", "fluidx3d": "not comparable", "ml-surrogate": "scored"},
    "D": {"openfoam12-realizableKE": "scored", "openlb": "not comparable", "fluidx3d": "not comparable", "ml-surrogate": "scored"},
    "E": {"openfoam12-realizableKE": "scored", "openlb": "not comparable", "fluidx3d": "not comparable", "ml-surrogate": "scored"},
    # Cases F to M: Eddy3D's fixtures for F, G, J, K, L and M are written and their solves are queued, so every engine is
    # pending there; H and I have OpenFOAM runs (I under three closures). Nothing else has been run on F to M.
    "F": dict(_NOT_RUN),
    "G": dict(_NOT_RUN),
    "H": {**_NOT_RUN, "openfoam12-realizableKE": "scored"},
    "I": {**_NOT_RUN, "openfoam12-realizableKE": "scored", "openfoam12-kEpsilon": "scored", "openfoam12-kOmegaSST": "scored"},
    "J": dict(_NOT_RUN),
    "K": dict(_NOT_RUN),
    "L": dict(_NOT_RUN),
    "M": dict(_NOT_RUN),
}
ENGINE_STATUS = {c: {e["id"]: st[e["id"]] for e in ENGINES if e["id"] in st} for c, st in ENGINE_STATUS.items()}   # in ENGINES order
QUEUED = "Eddy3D's fixture for this case is written and its solves are queued; no result exists yet."


def case_engines(case):
    """The engines that apply to a case, in ENGINES order: those with a status for it."""
    return [e for e in ENGINES if e["id"] in ENGINE_STATUS[case]]


MATRIX_ENGINES = [e for e in ENGINES if e["id"] not in CLOSURE_VARIANTS]

# ----------------------------------------------------------------------------- runs
# Every validation run snapshotted in validation/results/: its case, engine and configuration, the scores
# to quote (label -> key in its results.json), its per-point pairs and what their columns are, the
# figures that show it, and how to reproduce it. A results file that is not listed here is an error.

PAIRS_AB = ("point_id; x, y, z in m (case frame); U, V, W measured (_meas) and modelled (_model), each divided by U_H; "
            "V in the unified sign (positive toward +y)")
PAIRS_ML = ("set (the scored subset); x_tunnel, y_tunnel in m (case frame); x_scene, y_scene in m (the scaled scene the "
            "surrogate was given); observed_over_UH and predicted_over_UH, the speeds divided by U_H (Case E: by U at 15.9 m)")


def run(case, engine, configuration, results, headline, figures, reproduce, pairs, pairs_columns):
    return {"case": case, "engine": engine, "configuration": configuration, "results": results, "headline": headline,
            "figures": figures, "reproduce": reproduce, "pairs": pairs, "pairs_columns": pairs_columns,
            "run_id": f"{case}.{engine}" + (f".{configuration}" if configuration else "")}


PAIRS_H = ("point_id (the table's, the CSV's No.); x, y, z in m (case frame); U, V, W and k measured (_meas: the cleaned workbook values) and modelled (_model), "
           "velocities divided by U_H (measured by the tunnel's 3.226 m/s, modelled by the 3.23 m/s the solve was driven with), k by U_H^2, V in the unified sign "
           "(positive toward +y); cstar_meas, the measured concentration ratio C/c0 (c0 = 45.18 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled "
           "c* = c U_H H^2 / Q for turbulent Schmidt numbers 0.3, 0.5 and 0.7 (one row per published point, empty where the quantity was not measured)")
PAIRS_I = ("instrument (ldv or hydrocarbon_analyser), point_id (the table's: wind points 1-91, concentration points 92-630); x, y, z in m (case frame); U, V, W and k "
           "measured (_meas: the cleaned workbook values; V is empty on the y = 0 plane) and modelled (_model), velocities by U_H = 1.7 m/s, k by U_H^2; cstar_meas, "
           "the measured C/c0 (c0 = 39.22 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled c* for turbulent Schmidt numbers 0.3, 0.5 and 0.7 (a wind row has "
           "no concentration columns and a concentration row no velocity columns)")
_HI_REPRO = "Eddy3D fixture {fixture} (numerics level 3, 3000 iterations); figures validation/plot_cases_hi_openfoam.py; scores recomputed from the pairs by validation/dispersion_metrics.py"
_HI_HEADLINE = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k", "c*, Sct 0.3": "cstar.c_sct03", "c*, Sct 0.5": "cstar.c_sct05", "c*, Sct 0.7": "cstar.c_sct07"}
_FOAM_A_B = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k"}
_FOAM_C = {f"WD {wd} {q}": f"vs.{lab}.{key}" for wd, lab in (("0°", "wd-0"), ("22.5°", "wd22_5"), ("45°", "wd45"))
           for q, key in (("√(|U|²+2k)", "scalar"), ("|U|", "vector"))}
_ML_REPRO = "Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot_ml_surrogate.py"
RUNS = [
    *[run(c, "openfoam12-realizableKE", None, f"case{c}_openfoam12_realizableKE.json", _FOAM_A_B,
          ["cases-ab-openfoam-agreement.png", "cases-ab-openfoam-profiles.png"],
          f"Eddy3D fixture TestAijCase{c}ContainerE2E; figures validation/plot_cases_ab_openfoam.py",
          f"case{c}_openfoam12_realizableKE_pairs.csv", PAIRS_AB) for c in ("A", "B")],
    *[run("C", "openfoam12-realizableKE", cb, f"caseC_openfoam12_realizableKE_{cb}.json", _FOAM_C,
          ["case-c-openfoam-agreement.png", "case-c-openfoam-bias-map.png"],
          f"Eddy3D fixture TestAijCaseC{cb}ContainerE2E; figures validation/plot_case_c_openfoam.py",
          "caseC_openfoam12_realizableKE_pairs.csv",
          "config (0D/1D/2D), wind_direction_deg, point_id; x, y, z in m (case frame); measured_over_UH, the thermistor "
          "Vs/U_H; scalar_over_UH, the modelled sqrt(|U|^2 + 2k)/U_H; vector_over_UH, the modelled |U|/U_H (all nine "
          "configurations in one file)") for cb in ("0D", "1D", "2D")],
    *[run(c, "openlb", None, f"case{c}_openlb.json",
          {"U": "velocity.U", "U, points ≥ 2 dx": "velocity.U.aboveTwoCells", "V": "velocity.V", "W": "velocity.W",
           "k (resolved)": "k.resolved", "V, lateral sign flipped (control)": "control.V.lateralSignFlipped"},
          ["cases-ab-engine-comparison.png"],
          f"Eddy3D fixture TestAijCase{c}OpenLbContainerE2E (OpenLB eddy3dWind, CPU image, dx = 1.6 m); "
          "figure validation/plot_cases_ab_engines.py", f"case{c}_openlb_pairs.csv", PAIRS_AB) for c in ("A", "B")],
    # FluidX3D is scored on the heights where its own empty-domain control holds the imposed log law within 5 %
    # (its bounce-back ground has no roughness wall function); the approach flow alone is the control to beat.
    # Case B's V is not a headline: every comparable point lies on the centre plane, where mean V is zero.
    *[run(c, "fluidx3d", None, f"case{c}_fluidx3d.json",
          {"U, comparable heights": "velocity.U.comparable",
           **({"V, comparable heights": "velocity.V.comparable"} if c == "A" else {}),
           "W, comparable heights": "velocity.W.comparable", "U, all points": "velocity.U.all",
           "U, approach flow alone (control)": "negativeControl.noBuilding.components.U.control"},
          ["cases-ab-engine-comparison.png"],
          f"Eddy3D fixture TestAijCase{c}FluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D "
          f"GPU lattice Boltzmann, D3Q19 Smagorinsky LES, dx = H/64, {'40 + 200' if c == 'A' else '100 + 500'} H/U_H "
          "spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot_cases_ab_engines.py",
          f"case{c}_fluidx3d_pairs.csv", PAIRS_AB) for c in ("A", "B")],
    run("D", "openfoam12-realizableKE", None, "caseD_openfoam12_realizableKE.json",
        {"WD 0°, thermistor Vs · √(|U|²+2k)": "vs.0.corrected", "WD 0°, thermistor Vs · |U|": "vs.0.uncorrected",
         "WD 0°, split fibre |U|": "splitfibre.speed", "WD 0°, split fibre U": "splitfibre.U",
         "WD 22.5°, thermistor Vs · √(|U|²+2k)": "vs.22.5.corrected", "WD 22.5°, thermistor Vs · |U|": "vs.22.5.uncorrected",
         "WD 22.5°, rotation sense mirrored (control)": "vs.22.5.mirrored.corrected",
         "WD 45°, thermistor Vs · √(|U|²+2k)": "vs.45.corrected", "WD 45°, thermistor Vs · |U|": "vs.45.uncorrected",
         "WD 45°, rotation sense mirrored (control)": "vs.45.mirrored.corrected"},
        ["case-d-openfoam-agreement.png"],
        "Eddy3D fixture TestAijCaseDContainerE2E (EDDY3D_AIJD_HEADINGS=0,22.5,45); figure "
        "validation/plot_case_d_openfoam.py", "caseD_openfoam12_realizableKE_pairs.csv",
        "instrument (thermistor / split_fibre), wind_direction_deg, point_id; x, y, z in m (model frame); "
        "measured_over_UH, the thermistor's Vs or the split fibre's |U| over U_H; scalar_over_UH and vector_over_UH, "
        "the modelled sqrt(|U|^2 + 2k) and |U| over U_H; for the split fibre also U, V, W measured (_meas) and "
        "modelled (_model) over U_H"),
    run("E", "openfoam12-realizableKE", "SW", "caseE_openfoam12_realizableKE.json",
        {"before, √(|U|²+2k)": "vr.bc.SW.rms", "before, |U|": "vr.bc.SW.Umag", "after, √(|U|²+2k)": "vr.ac.SW.rms",
         "after, |U|": "vr.ac.SW.Umag", "no-construction ceiling control": "noConstruction.SW"},
        ["case-e-openfoam-agreement.png", "case-e-openfoam-bias-map.png"],
        "Eddy3D fixture TestAijCaseEContainerE2E (EDDY3D_AIJ_E_DIRECTIONS=SW, tabulated inlet); figures "
        "validation/plot_case_e_openfoam.py", "caseE_openfoam12_realizableKE_pairs.csv",
        "config (bc before / ac after construction), wind_direction, point_id; x, y, z in full-scale m (+x east, +y north); "
        "measured_ratio, the tunnel's velocity ratio; scalar_ratio and vector_ratio, the modelled sqrt(|U|^2 + 2k) and |U| "
        "over the model's own U at 15.9 m"),
    run("A", "ml-surrogate", None, "caseA_ml.json",
        {"|U| (z = 0.01 m plane)": "speed.vectorMagnitude", "|U|, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseA_ml_pairs.csv", PAIRS_ML),
    run("B", "ml-surrogate", None, "caseB_ml.json",
        {"|U| (z = H/16 plane)": "speed.vectorMagnitude", "|U|, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseB_ml_pairs.csv", PAIRS_ML),
    run("C", "ml-surrogate", None, "caseC_ml.json",
        {"Vs, 9 configurations": "speed.thermistor", "Vs, 2D WD 0, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseC_ml_pairs.csv", PAIRS_ML),
    run("D", "ml-surrogate", None, "caseD_ml.json",
        {"Vs, thermistor, 3 WD": "speed.thermistor", "|U|, split fibre, WD 0": "speed.vectorMagnitude",
         "Vs, WD 0, lattice cut at ±250 m": "halfExtent250.forward", "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseD_ml_pairs.csv", PAIRS_ML),
    run("E", "ml-surrogate", None, "caseE_ml.json",
        {"Vs/U(15.9 m), 16 WD, bc + ac": "speed.thermistor", "after construction": "speed.thermistor.after",
         "after − before": "delta.afterMinusBefore", "after, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseE_ml_pairs.csv", PAIRS_ML),
    # Cases H and I (Eddy3D's solves, scored against the cleaned tables): the closures other than realizable k-epsilon are separate engine ids
    run("H", "openfoam12-realizableKE", None, "caseH_openfoam12_realizableKE.json", _HI_HEADLINE, ["cases-hi-openfoam-agreement.png"],
        _HI_REPRO.format(fixture="TestAijCaseHContainerE2E (realizable k-ε, 1:100)"), "caseH_openfoam12_realizableKE_pairs.csv", PAIRS_H),
    run("I", "openfoam12-realizableKE", None, "caseI_openfoam12_realizableKE.json", _HI_HEADLINE, ["cases-hi-openfoam-agreement.png", "case-i-openfoam-closures.png"],
        _HI_REPRO.format(fixture="TestAijCubeContainerE2E (realizable k-ε, 1:60)"), "caseI_openfoam12_realizableKE_pairs.csv", PAIRS_I),
    run("I", "openfoam12-kEpsilon", None, "caseI_openfoam12_kEpsilon.json", _HI_HEADLINE, ["case-i-openfoam-closures.png"],
        _HI_REPRO.format(fixture="TestAijCubeContainerE2E (standard k-ε, 1:60)"), "caseI_openfoam12_kEpsilon_pairs.csv", PAIRS_I),
    run("I", "openfoam12-kOmegaSST", None, "caseI_openfoam12_kOmegaSST.json", _HI_HEADLINE, ["case-i-openfoam-closures.png"],
        _HI_REPRO.format(fixture="TestAijCubeContainerE2E (k-ω SST, 1:60)"), "caseI_openfoam12_kOmegaSST_pairs.csv", PAIRS_I),
]

# One caption per validation figure, used on the case pages and served with each result.
FIGURE_CAPTIONS = {
    "cases-ab-openfoam-agreement.png": ("Cases A and B, OpenFOAM 12 (realizable k-ε): measured against modelled U, V, W and k at "
                                        "every measured point, normalised by U_H, with the 1:1 line and the factor-of-two band."),
    "cases-ab-openfoam-profiles.png": ("Cases A and B, OpenFOAM 12: centre-plane vertical profiles of U/U_H at the measurement "
                                       "stations, measured points against the modelled line."),
    "case-c-openfoam-agreement.png": ("Case C, OpenFOAM 12: measured Vs/U_H against the modelled √(|U|²+2k)/U_H (filled) and "
                                      "|U|/U_H (hollow), one panel per configuration (centre block × wind direction)."),
    "case-c-openfoam-bias-map.png": ("Case C, OpenFOAM 12: log₂(model / tunnel) of the scalar speed at each of the 120 points "
                                     "on the plan of the array, per configuration — where the model is slow and where it is fast."),
    "case-e-openfoam-agreement.png": ("Case E, OpenFOAM 12, wind from SW: measured velocity ratio against the modelled "
                                      "√(|U|²+2k)/U_ref (filled) and |U|/U_ref (hollow), before and after construction, and the "
                                      "change the construction makes."),
    "case-e-openfoam-bias-map.png": ("Case E, OpenFOAM 12, wind from SW: log₂(model / tunnel) of the scalar speed at the 80 "
                                     "points on the plan of the district, before and after construction."),
    "cases-ab-engine-comparison.png": ("Cases A and B, every engine on the same points: measured against modelled U/U_H and "
                                       "V/U_H, one row per engine (OpenFOAM 12; OpenLB at dx = 1.6 m; FluidX3D at H/64). FluidX3D "
                                       "is scored on the filled points, the heights where its empty-domain control holds the "
                                       "imposed log law; the hollow points near the ground are excluded."),
    "case-d-openfoam-agreement.png": ("Case D, OpenFOAM 12, wind directions 0°, 22.5° and 45°: measured thermistor Vs/U_H against the "
                                      "modelled √(|U|²+2k)/U_H (filled) and |U|/U_H (hollow), and the split-fibre |U| against "
                                      "the modelled |U| at 0°. At 0° the 66 thermistor points are 33 mirror pairs."),
    "cases-hi-openfoam-agreement.png": ("Cases H and I, OpenFOAM 12 (realizable k-ε): measured against modelled U, W, k and the dimensionless "
                                        "concentration c* = C/c0 (turbulent Schmidt number 0.5; log axes show the positive pairs only), with the 1:1 line and the "
                                        "factor-of-two band where the values do not change sign."),
    "case-i-openfoam-closures.png": ("Case I, OpenFOAM 12 under standard k-ε, realizable k-ε and k-ω SST on one mesh: measured against modelled U, k and c* "
                                     "(Sct 0.5)."),
    "ml-surrogate-agreement.png": ("Eddy3D ML surrogate (Yel-2.0): measured against predicted pedestrian-height speed, one "
                                   "panel per case, with the 1:1 line and the factor-of-two band."),
}

METRIC_MEANING = {
    "Count": "number of measured points scored",
    "MeanObserved": "mean of the measured, normalised quantity", "MeanPredicted": "mean of the modelled, normalised quantity",
    "Fb": "fractional bias, 2 (mean_obs - mean_pred) / (mean_obs + mean_pred); positive = model low",
    "Nmse": "normalised mean square error", "Nad": "normalised absolute difference",
    "Fac2": "fraction of points within a factor of two (harsh near zero for sign-changing V and W)",
    "HitRate": "fraction of points within D = 0.25 relative or W = 0.05 U_H absolute",
    "Mg": "geometric mean bias", "Vg": "geometric variance", "GeometricPairs": "pairs with both values positive (used for Mg/Vg)",
    "R": "Pearson correlation coefficient",
    "null": "a metric that is undefined for the data (for example Mg and Vg when no pair has both values positive; Fb, Nmse and Nad of a signed velocity "
            "component of Case H or I whose observed and predicted means are not both positive)",
}

COLUMN_MEANING = {
    "point_id": "the tunnel's own measurement point number",
    "config": "configuration key: 'default', Case C centre building '0D'/'1D'/'2D', Case E state 'bc' (before) / 'ac' (after construction)",
    "instrument": "'split_fibre' (vector components) or 'thermistor' (omnidirectional scalar speed)",
    "wind_direction": "compass name of the direction the wind comes FROM (Case E)",
    "wind_direction_deg": "AIJ wind direction in degrees; 0 is the case's reference direction (see frame)",
    "x": "m, case frame", "y": "m, case frame", "z": "m above ground, case frame",
    "U": "m/s, mean velocity along +x", "V": "m/s, mean velocity along +y (sign unified: positive toward +y)", "W": "m/s, mean velocity along +z",
    "uu": "m^2/s^2, variance of u", "vv": "m^2/s^2, variance of v", "ww": "m^2/s^2, variance of w",
    "k": "m^2/s^2, turbulent kinetic energy",
    "Vs": "m/s, mean omnidirectional scalar wind speed (thermistor); Case D also lists |U| of the split-fibre probe under Vs for its 33 vector points",
    "velocity_ratio": "dimensionless, mean speed over the case's reference speed (Case E: Vs / U(15.9 m), U(15.9 m) = 3.935 m/s; see the case's normalisation)",
    "campaign": "'wind_tunnel' (model scale) or 'field' (a full-scale observation: Cases F, G, M)",
    "run": "replicate label within a campaign where the dataset publishes individual runs (Case M); empty elsewhere",
    "uv": "m^2/s^2, Reynolds shear stress <u'v'> as published",
    "uw": "m^2/s^2, Reynolds shear stress <u'w'> as published",
    "vw": "m^2/s^2, Reynolds shear stress <v'w'> as published",
    "C": "ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air)",
    "c_rms": "ppm, rms of the concentration fluctuation",
    "concentration_ratio": "C / c0, c0 = q / (U_ref L_ref^2) as the benchmark defines it for the case (manifest cases.<id>.normalisation)",
    "T": "degC, mean air temperature as published (Cases J, L)",
    "T_rms": "K, rms of the temperature fluctuation",
    "uc": "ppm m/s, turbulent concentration flux <u'c'>",
    "vc": "ppm m/s, turbulent concentration flux <v'c'>",
    "wc": "ppm m/s, turbulent concentration flux <w'c'>",
    "uT": "K m/s, turbulent heat flux <u'theta'>",
    "vT": "K m/s, turbulent heat flux <v'theta'>",
    "wT": "K m/s, turbulent heat flux <w'theta'>",
    "velocity_ratio_sd": "standard deviation of velocity_ratio over the observations behind a field value (Case F)",
    "k_ratio": "k / U_ref^2 where the dataset publishes only normalised values (Case G; U_ref = U at the tree height)",
}

# (path, media type, schema name or None, description); the order is the order of index.json and openapi.json.
ENDPOINTS = [
    ("index.json", "application/json", "index", "every endpoint and file with its size and SHA-256, versions, compatibility policy, changelog, licence, citation"),
    ("versions.json", "application/json", "versions", "every release, newest first: version, date, status (latest or superseded), schema and data version, base URL, tag, changelog; always at the unversioned /api/ path"),
    ("cases.json", "application/json", "cases", "every case: id, title, frame, units, counts, engine status, links"),
    ("cases/{id}.json", "application/json", "case", "one case in full: configurations, frame, units, inflow fit and approach-flow profile, point-table summary, geometry files, validation status, known data issues, attribution"),
    ("cases/{id}/points.json", "application/json", "points", "the cleaned measurement table: SI units, one frame, null where not measured"),
    ("cases/{id}/points.csv", "text/csv", None, "the same table as CSV (empty cell = not measured)"),
    ("cases/{id}/approach_flow.csv", "text/csv", None, "the measured approach-flow profile: z (m), U (m/s), and k (m^2/s^2) or u_rms (m/s) where published; Case G's U and k are dimensionless (U/Ub, k/Ub^2)"),
    ("cases/{id}/geometry.json", "application/json", "geometry", "the case's STL files with statistics, renders, and the boxes where the geometry is boxes"),
    ("cases/{id}/geometry.stl", "model/stl", None, "cleaned ASCII STL of the default configuration: metres, case frame, outward normals"),
    ("cases/{id}/geometry_{configuration}.stl", "model/stl", None, "the other configurations' STLs (C: 0D, 1D; E: bc, before construction)"),
    ("cases/{id}/validation.json", "application/json", "validation", "Eddy3D's scores per engine and run, with figures and the per-point pairs"),
    ("cases/{id}/pairs/{engine}.csv", "text/csv", None, "per-point measured and modelled values of one engine's runs on the case (columns described by the result's pairs_columns)"),
    ("validation.json", "application/json", "validation-summary", "every case and engine in one table: status, runs, headline scores"),
    ("geometry.json", "application/json", "geometry-index", "every STL of every case in one list: case, configuration, units, frame, bounding box, size, SHA-256"),
    ("geometry.zip", "application/zip", None, "every STL in one archive (each keeps its own case's frame and units: they are not one scene)"),
    ("schemas/{name}.schema.json", "application/schema+json", None, "the JSON Schema (draft 2020-12) of each JSON document"),
    ("openapi.json", "application/json", None, "OpenAPI 3.1 description of every endpoint"),
    ("llms.txt", "text/plain", None, "plain-text entry point for agents"),
]
ROOT_ENDPOINTS = {"versions.json"}   # served once, at the unversioned /api/ path, not inside any tree
MEDIA_TYPES = {".json": "application/json", ".csv": "text/csv", ".stl": "model/stl", ".zip": "application/zip", ".txt": "text/plain"}

WRITTEN = set()          # every file this build wrote into the current tree (relative); anything else there is stale
DATA_VERSION = None      # set once the data files are written


# ----------------------------------------------------------------------------- trees

def is_release_dir(name):
    """docs/api/<name>/ is a frozen release tree if <name> is a MAJOR.MINOR.PATCH version."""
    return bool(R.SEMVER.match(name))


def release_dirs():
    """The versions that have a frozen tree under docs/api/, oldest first."""
    names = [n for n in os.listdir(API_ROOT) if is_release_dir(n) and os.path.isdir(os.path.join(API_ROOT, n))]
    return sorted(names, key=R.parse)


def tree_files(root):
    """Relative paths of every file in a tree. The alias's root also holds the frozen trees and versions.json, which
    belong to no tree's file list."""
    out = set()
    for dirpath, dirs, names in os.walk(root):
        if os.path.abspath(dirpath) == API_ROOT:
            dirs[:] = [d for d in dirs if not is_release_dir(d)]
            names = [n for n in names if n not in ROOT_ENDPOINTS]
        out.update(os.path.relpath(os.path.join(dirpath, n), root).replace(os.sep, "/") for n in names)
    return out


def use_tree(kind):
    """Point every writer at one tree: the frozen copy docs/api/<release>/ or the latest alias docs/api/. The two
    are built by the same code, so they differ only in the address each document gives its own files."""
    # shortcut: module globals switched between two sequential builds; make the tree an object if they ever run in parallel
    global TREE, API, API_BASE, FALLBACK_BASE, WRITTEN
    WRITTEN = set()
    TREE = kind
    if kind == "release":
        API, API_BASE, FALLBACK_BASE = os.path.join(API_ROOT, RELEASE), PINNED_BASE, RELEASE_BASE
    else:
        API, API_BASE, FALLBACK_BASE = API_ROOT, LIVE_BASE, RAW_BASE
    os.makedirs(API, exist_ok=True)


# ----------------------------------------------------------------------------- files and URLs

def url(rel):
    return f"{API_BASE}/{rel}"


def schema_url_in(base, name):
    return f"{base}/schemas/{name}.schema.json"


def schema_url(name):
    return schema_url_in(API_BASE, name)


def render_url(case, configuration=None):
    """The site URL of a configuration's render (the case's default configuration if None)."""
    return f"{SITE}/assets/geometry/{D.render_file(case, configuration)}"


def _sha256(rel, root=None):
    with io.open(os.path.join(root or API, rel), "rb") as f:
        body = f.read()
    return hashlib.sha256(body).hexdigest(), len(body)


def media_type(rel):
    if rel.startswith("schemas/"):
        return "application/schema+json"
    return MEDIA_TYPES[os.path.splitext(rel)[1]]


def download(rel):
    """A file to fetch: versioned URL, path, media type, size and SHA-256 of the bytes on disk."""
    sha, n = _sha256(rel)
    return {"url": f"{url(rel)}?v={sha[:12]}", "path": rel, "media_type": media_type(rel), "bytes": n, "sha256": sha}


def _target(rel):
    path = os.path.join(API, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    WRITTEN.add(rel)
    return path


def write_text(rel, text):
    with io.open(_target(rel), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return rel


def write_csv(rel, header, rows):
    with io.open(_target(rel), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(["" if v is None else v for v in r])
    return rel


def copy_file(src, rel):
    shutil.copyfile(src, _target(rel))
    return rel


def dump(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def write_json(rel, schema, obj):
    """A JSON document: the four header keys, then the body."""
    body = {"$schema": schema_url(schema), "schema_version": SCHEMA_VERSION, "data_version": DATA_VERSION,
            "license": D.LICENSE["spdx"]}
    body.update(obj)
    return write_text(rel, dump(body))


# ----------------------------------------------------------------------------- phase 1: data files

def points_summary(rows):
    cols = [c for c in D.POINT_COLUMNS if any(r[c] not in (None, "") for r in rows)]
    by = lambda key: sorted({str(r[key]) for r in rows})  # noqa: E731
    counts = {}
    for key in ("config", "instrument", "wind_direction_deg"):
        if key in cols:
            counts[key] = {k: sum(1 for r in rows if str(r[key]) == k) for k in by(key)}
    nulls = {c: sum(1 for r in rows if r[c] is None) for c in cols if c not in ("config", "instrument", "wind_direction")}
    xyz = [(r["x"], r["y"], r["z"]) for r in rows if None not in (r["x"], r["y"], r["z"])]
    return {
        "rows": len(rows),
        "distinct_points": len({r["point_id"] for r in rows}),
        "columns": cols,
        "counts": counts,
        "nulls": {k: v for k, v in nulls.items() if v},
        "bbox_min": [round(min(p[i] for p in xyz), 6) for i in range(3)],
        "bbox_max": [round(max(p[i] for p in xyz), 6) for i in range(3)],
    }


# Boxes the case states (the building, the belt, the array), in the case frame. F's STL is a 725 m disc drawn as a polygon, so its
# extent in y is short of the radius by up to 3 mm; M's and F's z start at -0.0 on the ground.
BBOX_TOLERANCE = {"F": 0.01}
EXPECTED_BBOX = {
    "F": ([-725.0, -725.0, 0.0], [725.0, 725.0, 225.0]),               # the 725 m disc of terrain, the 225 m roof of the tallest tower (readme, STL)
    "G": ([-2.0, -37.0, 1.2], [0.0, 37.0, 7.0]),                       # the belt: 2 m deep, 74 m long, 7 m tall, 1.2 m gap below
    "H": ([-0.1, -0.05, 0.0], [0.0, 0.05, 0.2]),                       # the 0.10 x 0.10 x 0.20 m building, leeward face at x = 0
    "I": ([-0.05, -0.05, 0.0], [0.05, 0.05, 0.1]),                     # the 0.1 m cube, centred on the origin
    "J": ([-0.08, -0.04, 0.0], [0.0, 0.04, 0.16]),                     # b = 0.08 m, H = 0.16 m
    "K": ([-0.36, -0.51, 0.0], [0.66, 0.51, 0.06]),                    # 9 x 9 cubes of 0.06 m on a 0.12 m pitch
    "L": ([-0.96, -0.51, 0.0], [0.66, 0.51, 0.06]),                    # 14 x 9 cubes of 0.06 m on a 0.12 m pitch
    "M": ([-540.0, -360.0, 0.0], [540.0, 360.0, 64.9152]),             # the 1.8 x 1.2 m model, x600
}


def expected_bbox(case, cfg):
    c = D.CASES[case]["configuration"]
    if case in EXPECTED_BBOX:
        return EXPECTED_BBOX[case]
    if case == "A":
        return [-c["b_m"] / 2, -c["b_m"] / 2, 0.0], [c["b_m"] / 2, c["b_m"] / 2, c["H_m"]]
    if case == "B":
        return [-c["depth_m"] / 2, -c["width_m"] / 2, 0.0], [c["depth_m"] / 2, c["width_m"] / 2, c["H_m"]]
    if case == "C":
        return [-0.5, -0.5, 0.0], [0.5, 0.5, 0.4 if cfg == "2D" else 0.2]
    if case == "D":
        e = c["array_extent_m"]
        return [e["x"][0], e["y"][0], e["z"][0]], [e["x"][1], e["y"][1], e["z"][1]]
    return None, None


def stl_rel(case, cfg):
    return f"cases/{case}/geometry.stl" if cfg == D.DEFAULT_CONFIGURATION[case] else f"cases/{case}/geometry_{cfg}.stl"


def write_data(case):
    """Points CSV, approach-flow CSV, STLs and pairs of one case; returns what the JSON phase needs."""
    rows, src = D.load_points(case)
    summ = points_summary(rows)
    write_csv(f"cases/{case}/points.csv", summ["columns"], ([r[c] for c in summ["columns"]] for r in rows))

    af, af_src = D.load_approach_flow(case)
    af_cols = [c for c in ("z", "U", "k", "u_rms") if any(c in r for r in af)]
    write_csv(f"cases/{case}/approach_flow.csv", af_cols, ([r.get(c) for c in af_cols] for r in af))

    geometry = []
    for cfg, tris, boxes, note in D.case_geometry(case):
        stats = D.stl_stats(tris)
        rel = stl_rel(case, cfg)
        D.write_ascii_stl(_target(rel), tris, f"AIJ_case{case}_{cfg}")
        lo, hi = expected_bbox(case, cfg)
        ok = None
        if lo is not None:
            tol = BBOX_TOLERANCE.get(case, 1e-6)
            ok = all(abs(a - b) < tol for a, b in zip(stats["bbox_min"], lo)) and all(abs(a - b) < tol for a, b in zip(stats["bbox_max"], hi))
            if not ok:
                raise SystemExit(f"geometry check failed for {case}/{cfg}: bbox {stats['bbox_min']}..{stats['bbox_max']} != {lo}..{hi}")
        if boxes is not None and not stats["watertight"]:
            raise SystemExit(f"geometry check failed for {case}/{cfg}: box geometry is not edge-manifold")
        geometry.append({"configuration": cfg, "rel": rel, "stats": stats, "boxes": boxes, "note": note, "bbox_ok": ok})
    geometry.sort(key=lambda g: g["configuration"] != D.DEFAULT_CONFIGURATION[case])

    for r in RUNS:
        if r["case"] == case:
            copy_file(os.path.join(RESULTS_DIR, r["pairs"]), f"cases/{case}/pairs/{r['engine']}.csv")
    return {"rows": rows, "src": src, "summ": summ, "af": af, "af_src": af_src, "af_cols": af_cols, "geometry": geometry}


def write_archive(data):
    """geometry.zip: every STL under a self-describing name, with fixed timestamps and order.

    Deflate output depends on the zlib version (1.2.13 and 1.3.1 encode the same bytes differently), so an
    archive whose members already equal the current STLs is kept as it is: its bytes then depend on the
    geometry alone, and a rebuild on any platform reproduces the committed file."""
    rel = "geometry.zip"
    if TREE == "latest":   # the alias holds the release tree's archive itself, so the two cannot differ by a zlib
        shutil.copyfile(os.path.join(API_ROOT, RELEASE, rel), _target(rel))
        return rel
    members = []
    for case in D.CASE_IDS:
        for g in data[case]["geometry"]:
            with io.open(os.path.join(API, g["rel"]), "rb") as f:
                members.append((archive_name(case, g["configuration"]), f.read()))
    path = _target(rel)
    if os.path.isfile(path):
        try:
            with zipfile.ZipFile(path) as z:
                infos = z.infolist()
                if ([i.filename for i in infos] == [n for n, _ in members]
                        and all(i.date_time == (1980, 1, 1, 0, 0, 0) and i.compress_type == zipfile.ZIP_DEFLATED for i in infos)
                        and all(z.read(n) == body for n, body in members)):
                    return rel
        except zipfile.BadZipFile:
            pass
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, body in members:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, body)
    return rel


def archive_name(case, cfg):
    return f"AIJ_case{case}_{cfg}.stl"


def compute_data_version():
    """SHA-256 over (path, SHA-256) of every data file served and every score snapshot behind validation.json.

    The served files are written here with LF endings, so their bytes are their content. The score snapshots
    are hashed as canonical JSON (sorted keys, no whitespace), so a checkout's line endings cannot move it."""
    entries = []
    for rel in sorted(WRITTEN):
        if rel.endswith((".csv", ".stl")):
            entries.append(f"api/{rel}\t{_sha256(rel)[0]}")
    for r in sorted({r["results"] for r in RUNS}):
        with io.open(os.path.join(RESULTS_DIR, r), encoding="utf-8") as f:
            canonical = json.dumps(json.load(f), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        entries.append(f"validation/results/{r}\t{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- phase 2: JSON documents

def check_runs_registry():
    """Every snapshot is registered and every registered snapshot exists: nothing is served by accident."""
    on_disk = {n for n in os.listdir(RESULTS_DIR) if n.endswith(".json")}
    listed = {r["results"] for r in RUNS}
    if on_disk != listed:
        raise SystemExit(f"validation/results/ and RUNS disagree: unregistered {sorted(on_disk - listed)}, "
                         f"missing {sorted(listed - on_disk)}")
    missing = sorted({r["pairs"] for r in RUNS if not os.path.isfile(os.path.join(RESULTS_DIR, r["pairs"]))})
    if missing:
        raise SystemExit(f"RUNS names pairs files that are not in validation/results/: {missing}")


def is_metric(v):
    return isinstance(v, dict) and "Fb" in v and "R" in v


def defined(metric):
    """A metric with every undefined value (NaN or an infinity, which some fixtures write as the strings
    "NaN", "Infinity") as None: JSON has no NaN, and a string where a number belongs breaks clients."""
    out = {}
    for k, v in metric.items():
        if isinstance(v, str) and v in ("NaN", "Infinity", "-Infinity"):
            v = None
        elif isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
            v = None
        out[k] = v
    return out


def flat_scores(res, prefix=""):
    """Every score in a results.json as {dotted key: metrics}. A score nested as {"score": {...}} takes its
    parent's key (velocity.U.comparable); other nesting joins the keys
    (negativeControl.noBuilding.components.U.control)."""
    out = {}
    for k, v in res.items():
        key = f"{prefix}{k}"
        if is_metric(v):
            out[key] = defined(v)
        elif isinstance(v, dict):
            if is_metric(v.get("score")):
                out[key] = defined(v["score"])
            else:
                out.update(flat_scores(v, key + "."))
    return out


def validation_entries(case):
    out = []
    for r in RUNS:
        if r["case"] != case:
            continue
        with io.open(os.path.join(RESULTS_DIR, r["results"]), encoding="utf-8") as f:
            res = json.load(f)
        scores = flat_scores(res)
        for label, key in r["headline"].items():
            if key not in scores:
                raise SystemExit(f"{r['results']}: headline '{label}' -> '{key}' is not a score in the file")
        out.append({
            "run_id": r["run_id"],
            "engine": r["engine"],
            "configuration": r["configuration"],
            "solver": res.get("engine") or res.get("turbulenceModel"), "numerics_level": res.get("numericsLevel"),
            "scale": res.get("scale"), "solved_time": res.get("solvedTime"), "iterations": res.get("iterations"),
            "points_measured": res.get("points.measured"),
            "lateral_sign_applied_in_fixture": res.get("lateralSign"),
            "recirculation_Lr_over_H": res.get("recirculation.LrOverH",
                                               (res.get("recirculation.z=0.05H") or {}).get("LrOverH")),
            "quantity": res.get("quantity"),
            "normalisation": ("velocities by U_H, k by U_H^2 (the benchmark's own convention; Case E by U at 15.9 m, "
                              "as it is published); hit rate D = 0.25, W = 0.05 in those units"),
            "metric_meaning": METRIC_MEANING,
            "headline": dict(r["headline"]),
            "scores": scores,
            "figures": [{"url": f"{SITE}/assets/figures/{fig}", "caption": FIGURE_CAPTIONS[fig]} for fig in r["figures"]],
            "pairs": download(f"cases/{case}/pairs/{r['engine']}.csv"),
            "pairs_columns": r["pairs_columns"],
            "reproduce": r["reproduce"],
            "source_file": f"validation/results/{r['results']}",
            "source_url": f"{REPO_URL}/blob/main/validation/results/{r['results']}",
            # The benchmark's citation from one place, not the fixture's free-text reference line.
            "cite": D.CITATION["benchmark"],
        })
    return out


def configurations(case, rows):
    configs = []
    if case == "C":
        for cb in ("0D", "1D", "2D"):
            for wd in (0.0, 22.5, 45.0):
                configs.append({"config": cb, "wind_direction_deg": wd, "points": sum(1 for r in rows if r["config"] == cb and r["wind_direction_deg"] == wd)})
    elif case == "D":
        for inst in ("thermistor", "split_fibre"):
            for wd in sorted({r["wind_direction_deg"] for r in rows if r["instrument"] == inst}):
                sel = [r for r in rows if r["instrument"] == inst and r["wind_direction_deg"] == wd]
                configs.append({"instrument": inst, "wind_direction_deg": wd, "points": len(sel),
                                "measured": sum(1 for r in sel if (r["Vs"] if inst == "thermistor" else r["U"]) is not None)})
    elif case == "E":
        for st in ("bc", "ac"):
            configs.append({"config": st, "wind_directions": D.COMPASS, "points_per_direction": sum(1 for r in rows if r["config"] == st and r["wind_direction"] == "N")})
    elif case in ("A", "B"):
        configs.append({"config": "default", "wind_direction_deg": 0.0, "points": len(rows)})
    else:
        # Cases F to M: one entry per campaign, instrument, run and direction the table holds, in table order.
        groups = {}
        for r in rows:
            groups.setdefault((r["config"], r["campaign"], r["instrument"], r["run"], r["wind_direction"], r["wind_direction_deg"]), []).append(r)
        for (cfg, camp, inst, run, name, wd), sel in groups.items():
            c = {"config": cfg, "campaign": camp, "instrument": inst}
            if run:
                c["run"] = run
            if name:
                c["wind_direction"] = name
            configs.append({**c, "wind_direction_deg": wd, "points": len(sel)})
    return configs


def write_case_documents(case, d):
    meta = D.CASES[case]
    summ = d["summ"]
    cols = summ["columns"]
    units_label = "metres" + (" (full scale)" if case in D.FULL_SCALE else " (model scale)")

    write_json(f"cases/{case}/points.json", "points", {
        "case": case, "title": meta["title"],
        "points_source": d["src"],
        "units": meta["units"], "frame": meta["frame"],
        "columns": cols,
        "column_meaning": {c: COLUMN_MEANING[c] for c in cols},
        "n": len(d["rows"]),
        "csv": download(f"cases/{case}/points.csv"),
        "points": [{c: r[c] for c in cols} for r in d["rows"]],
    })

    files = []
    for g in d["geometry"]:
        entry = {"configuration": g["configuration"], **download(g["rel"]), "format": "ASCII STL, LF line endings, outward normals",
                 "source": g["note"], "stats": g["stats"], "bbox_matches_stated_dimensions": g["bbox_ok"],
                 "render": render_url(case, g["configuration"]), "render_caption": D.RENDER_CAPTIONS[(case, g["configuration"])]}
        if g["boxes"] is not None:
            b = g["boxes"]
            entry.update({"boxes": b, "box_count": len(b), "analytic_volume": round(sum(
                (x["max"][0] - x["min"][0]) * (x["max"][1] - x["min"][1]) * (x["max"][2] - x["min"][2]) for x in b), 9)})
        files.append(entry)
    write_json(f"cases/{case}/geometry.json", "geometry", {
        "case": case, "title": meta["title"], "units": units_label, "frame": meta["frame"],
        "default_configuration": D.DEFAULT_CONFIGURATION[case],
        "configurations": [f["configuration"] for f in files],
        "is_boxes": files[0].get("boxes") is not None,
        "files": files,
        "render": render_url(case),
    })

    results = validation_entries(case)
    write_json(f"cases/{case}/validation.json", "validation", {
        "case": case, "title": meta["title"],
        "status": "scored" if results else "pending",
        "status_meaning": STATUS_MEANING,
        "engines": [{"engine": e["id"], "status": ENGINE_STATUS[case][e["id"]]} for e in case_engines(case)],
        "results": results,
        "note": (None if results else "No validation has been run for this case yet; results is an empty list. "
                 f"Nothing on this page is a claim about this case. {QUEUED}"),
    })

    configs = configurations(case, d["rows"])
    write_json(f"cases/{case}.json", "case", {
        "id": case, "slug": meta["slug"], "title": meta["title"], "summary": meta["short"],
        "configuration": meta["configuration"],
        "configurations": configs,
        "quantities": meta["quantities"],
        "units": meta["units"], "frame": meta["frame"],
        "inflow_fit": meta["inflow_fit"],
        "approach_flow": {"source": d["af_src"], "units": {c: {**{"z": "m", "U": "m/s", "k": "m^2/s^2", "u_rms": "m/s"}, **meta.get("approach_flow_units", {})}[c] for c in d["af_cols"]},
                          "rows": d["af"], "csv": download(f"cases/{case}/approach_flow.csv")},
        "points": {"url": url(f"cases/{case}/points.json"), "csv": download(f"cases/{case}/points.csv"), "source": d["src"], **summ},
        "geometry": {"url": url(f"cases/{case}/geometry.json"),
                     "files": [{"configuration": f["configuration"], "url": f["url"], "triangles": f["stats"]["triangles"],
                                "watertight": f["stats"]["watertight"]} for f in files]},
        "validation": {"url": url(f"cases/{case}/validation.json"), "status": "scored" if results else "pending",
                       "engines": ENGINE_STATUS[case]},
        "known_issues": meta["known_issues"],
        "people": meta["people"], "doi": meta["doi"], "doi_note": meta.get("doi_note"),
        "citation_requested": meta["citation_requested"],
        "files_in_repository": {"folder": f"{REPO_URL}/tree/main/{meta['folder']}", "reference": meta["reference_file"],
                                "approach_flow": meta["approach_flow_file"], "readme": meta["readme"]},
        "render": render_url(case),
        "page": f"{SITE}/cases/{meta['slug']}/",
    })
    return {"summ": summ, "configs": configs, "results": results, "files": files}


def write_cases_index(percase):
    items = []
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        p = percase[case]
        items.append({
            "id": case, "slug": meta["slug"], "title": meta["title"], "summary": meta["short"],
            "configuration": meta["configuration"],
            "quantities": meta["quantities"], "units": meta["units"],
            "frame": {k: meta["frame"][k] for k in ("origin", "x", "y", "z")},
            "counts": {"rows": p["summ"]["rows"], "distinct_points": p["summ"]["distinct_points"], "configurations": len(p["configs"])},
            "engines": ENGINE_STATUS[case],
            "doi": meta["doi"],
            "links": {"case": url(f"cases/{case}.json"), "points": url(f"cases/{case}/points.json"),
                      "points_csv": download(f"cases/{case}/points.csv")["url"],
                      "geometry": url(f"cases/{case}/geometry.json"), "geometry_stl": p["files"][0]["url"],
                      "validation": url(f"cases/{case}/validation.json"), "page": f"{SITE}/cases/{meta['slug']}/",
                      "render": render_url(case)},
        })
    write_json("cases.json", "cases", {"cases": items})


def write_geometry_index(data):
    """One index of every STL. The STLs are NOT merged into one scene: each case has its own origin, E, F, G and M are
    full scale (hundreds of times larger than the model-scale cases), and C's three centre-block variants and E's
    before/after states are alternatives that cannot share one CFD domain."""
    items = []
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        for g in data[case]["geometry"]:
            items.append({
                "case": case, "configuration": g["configuration"], **download(g["rel"]),
                "archive_name": archive_name(case, g["configuration"]),
                "units": "metres" + (" (full scale)" if case in D.FULL_SCALE else " (model scale)"),
                "frame": {k: meta["frame"][k] for k in ("origin", "x", "y", "z")},
                "bbox_min": g["stats"]["bbox_min"], "bbox_max": g["stats"]["bbox_max"],
                "triangles": g["stats"]["triangles"], "watertight": g["stats"]["watertight"],
                "render": render_url(case, g["configuration"]),
            })
    write_json("geometry.json", "geometry-index", {
        "description": ("Every cleaned STL, one entry per case and configuration. Each file is in its own case's frame "
                        "and units — points.json of the same case lives in that frame — so they are deliberately not one "
                        "scene: overlaid, the cases would stack at the origin, and Cases E, F, G and M are full scale while the "
                        "others are model scale. geometry.zip holds the same files under archive_name."),
        "archive": download("geometry.zip"),
        "files": items,
    })


def write_validation_summary(percase):
    cases = []
    for case in D.CASE_IDS:
        engines = []
        for e in case_engines(case):
            runs = []
            for res in percase[case]["results"]:
                if res["engine"] != e["id"]:
                    continue
                runs.append({"run_id": res["run_id"], "configuration": res["configuration"], "headline": [
                    {"label": label, "score": key, **{m: res["scores"][key].get(m) for m in ("Count", "R", "Fac2", "Fb", "HitRate")}}
                    for label, key in res["headline"].items()]})
            engines.append({"engine": e["id"], "status": ENGINE_STATUS[case][e["id"]], "runs": runs})
        cases.append({"case": case, "title": D.CASES[case]["title"], "url": url(f"cases/{case}/validation.json"), "engines": engines})
    write_json("validation.json", "validation-summary", {
        "description": ("Every case and engine in one table. 'scored' means a run exists, not that it agrees: read the "
                        "scores. Headline scores are the ones to quote; every score, the figures and the per-point pairs "
                        "are in each case's validation.json."),
        "engines": ENGINES, "status_meaning": STATUS_MEANING, "metric_meaning": METRIC_MEANING, "cases": cases,
    })


def write_schemas():
    for name, schema in S.published(API_BASE).items():
        write_text(f"schemas/{name}.schema.json", dump(schema))


def write_openapi():
    ids = D.CASE_IDS
    variants = sorted({g for case in ids for (c, g) in D.RENDER_CAPTIONS if c == case and g != D.DEFAULT_CONFIGURATION[case]})
    params = {
        "id": {"name": "id", "in": "path", "required": True, "description": "case id", "schema": {"type": "string", "enum": ids}},
        "configuration": {"name": "configuration", "in": "path", "required": True, "schema": {"type": "string", "enum": variants},
                          "description": "a non-default geometry configuration: C 0D or 1D (2D is geometry.stl); E bc (ac is geometry.stl)"},
        "engine": {"name": "engine", "in": "path", "required": True, "description": "an engine with a scored run on the case",
                   "schema": {"type": "string", "enum": [e["id"] for e in ENGINES]}},
        "name": {"name": "name", "in": "path", "required": True, "description": "a document schema",
                 "schema": {"type": "string", "enum": list(S.DOCUMENTS)}},
        "v": {"name": "v", "in": "query", "required": False, "schema": {"type": "string", "pattern": "^[0-9a-f]{12}$"},
              "description": "the file's SHA-256 prefix, as in the URLs the JSON documents give; ignored by the server, it keeps caches from serving a stale copy"},
    }
    op_ids = {
        "index.json": ("getIndex", "discovery"), "versions.json": ("getVersions", "discovery"), "cases.json": ("listCases", "cases"), "cases/{id}.json": ("getCase", "cases"),
        "cases/{id}/points.json": ("getPoints", "points"), "cases/{id}/points.csv": ("getPointsCsv", "points"),
        "cases/{id}/approach_flow.csv": ("getApproachFlowCsv", "points"),
        "cases/{id}/geometry.json": ("getGeometry", "geometry"), "cases/{id}/geometry.stl": ("getGeometryStl", "geometry"),
        "cases/{id}/geometry_{configuration}.stl": ("getGeometryVariantStl", "geometry"),
        "cases/{id}/validation.json": ("getValidation", "validation"), "cases/{id}/pairs/{engine}.csv": ("getPairsCsv", "validation"),
        "validation.json": ("getValidationSummary", "validation"), "geometry.json": ("listGeometry", "geometry"),
        "geometry.zip": ("getGeometryArchive", "geometry"), "schemas/{name}.schema.json": ("getSchema", "discovery"),
        "openapi.json": ("getOpenApi", "discovery"), "llms.txt": ("getLlmsTxt", "discovery"),
    }
    names = {n: "".join(w.capitalize() for w in n.split("-")) for n in S.DOCUMENTS}
    stl_note = (" GitHub Pages labels .stl responses `application/vnd.ms-pki.stl` (a certificate type); the body is "
                "ASCII STL whatever the header says.")
    not_found = {"description": "No such case, configuration, engine or file. GitHub Pages answers with an HTML page, not JSON."}
    paths = {}
    for path, media, schema, desc in ENDPOINTS:
        op_id, tag = op_ids[path]
        if schema:
            body = {"schema": {"$ref": f"#/components/schemas/{names[schema]}"}}
        elif media == "application/zip":
            body = {"schema": {"type": "string", "format": "binary"}}
        elif media == "application/schema+json":
            body = {"schema": {"type": "object"}}
        else:
            body = {"schema": {"type": "string"}}
        op = {"operationId": op_id, "tags": [tag], "summary": desc[0].upper() + desc[1:].split(":")[0],
              "description": desc + (stl_note if media == "model/stl" else ""),
              "responses": {"200": {"description": "OK", "content": {media: body}}, "404": not_found}}
        ps = [params[p] for p in ("id", "configuration", "engine", "name") if "{" + p + "}" in path]
        if not path.endswith(".json") and path != "llms.txt" or path.endswith(".schema.json"):
            ps.append(params["v"])
        if ps:
            op["parameters"] = ps
        paths["/" + path] = {"get": op}
        if path in ROOT_ENDPOINTS:   # one home, whichever tree this document is in: say so, or a release tree's server would 404
            paths["/" + path]["servers"] = [{"url": LIVE_BASE, "description": "the unversioned alias; versions.json is not copied into release trees"}]
    components = {names[n]: {k: v for k, v in s.items() if k not in ("$schema", "$id")} for n, s in S.DOCUMENTS.items()}
    doc = {
        "openapi": "3.1.0",
        "jsonSchemaDialect": S.DRAFT,
        "info": {"title": "AIJ UWE benchmark — cleaned data API", "version": SCHEMA_VERSION,
                 "summary": f"Wind-tunnel and field reference data of the AIJ UWE benchmark (Cases {CASE_SPAN}), cleaned, with Eddy3D's validation against it.",
                 "description": ("Static files, one GET each; nothing is computed on request. Lengths in metres, velocities in "
                                 "m/s, variances and k in m^2/s^2, in one frame per case. " + COMPATIBILITY + " " + CACHING),
                 "license": {"name": D.LICENSE["name"], "identifier": D.LICENSE["spdx"]}},
        "servers": [{"url": API_BASE, "description": ("release " + RELEASE + ", frozen" if TREE == "release" else "the latest release")},
                    {"url": FALLBACK_BASE, "description": "the same files, raw from the repository (fallback)"}],
        "tags": [{"name": "discovery", "description": "where everything is"}, {"name": "cases", "description": f"the {len(D.CASE_IDS)} cases"},
                 {"name": "points", "description": "measurement tables"}, {"name": "geometry", "description": "STL geometry"},
                 {"name": "validation", "description": "Eddy3D's scores and the per-point pairs behind them"}],
        "paths": paths,
        "components": {"schemas": components},
    }
    write_text("openapi.json", dump(doc))


def llms_text(percase):
    walk = [
        "# AIJ UWE benchmark — cleaned data API",
        "",
        "> Wind-tunnel and field reference data from the Architectural Institute of Japan Urban Wind Environment (UWE)",
        f"> benchmark, Cases {CASE_SPAN}, cleaned into one schema, plus Eddy3D's validation against it. Static files, plain GET.",
        "",
        f"Base URL: {API_BASE}",
        f"Fallback (raw files from the repository): {FALLBACK_BASE}",
        f"Repository: {REPO_URL}",
        f"Release: {RELEASE} ({RELEASE_DATE}). " + (
            "This is the frozen copy of that release: its files never change and every URL below stays inside it."
            if TREE == "release" else
            f"This is the latest alias, which always equals the newest release; the frozen copy of {RELEASE} is {PINNED_BASE}."),
        f"All releases: {endpoint_url('versions.json')}",
        f"API schema version: {SCHEMA_VERSION}. Data version (SHA-256 of the served data): {DATA_VERSION}.",
        "Licence: CC-BY-4.0 — the data belongs to its collectors; cite the benchmark and the per-case papers.",
        "",
        "## How to use this",
        "",
        "1. GET index.json — every endpoint and file (with size and SHA-256), versions, changelog, citation.",
        f"2. GET cases.json — every case with its frame, units, counts and links. Pick an id ({', '.join(D.CASE_IDS)}).",
        "3. GET cases/{id}.json — read `frame`, `units` and `known_issues` BEFORE the numbers; they differ per case.",
        "4. GET cases/{id}/points.json (or points.csv) — every value is SI (m, m/s, m^2/s^2; concentrations in ppm, temperatures in",
        "   degC) in ONE frame per case; unmeasured values are null. Cases E, F and G publish dimensionless ratios (velocity_ratio,",
        "   k_ratio), not speeds in m/s; Case M has wind-tunnel and field rows (`campaign`). Read `units` and the normalisation first.",
        "5. GET cases/{id}/geometry.stl — ASCII STL in metres, outward normals, in the case's own frame (cases/{id}.json `frame`).",
        "   Cases A-D and H-L are model-scale with +x along the wind at WD = 0; E to G and M are full-scale: E and F keep their",
        "   geographic frame (+x east, +y north), G has +x downwind, and M has +x north and +y west.",
        "   geometry.json lists the boxes where the geometry IS boxes (A, B, C, D, G, H, I, J, K, L), so you need not parse the STL at all.",
        "6. GET validation.json for every case and engine at once, or cases/{id}/validation.json for one case in full.",
        "   Quote the `headline` scores. An engine whose status is not \"scored\" has NO result for that case: do not",
        "   infer one. \"scored\" means a run exists, not that it agrees — read the numbers. Each result's `pairs` is",
        "   the per-point measured and modelled values, so any score can be recomputed. Status today: "
        + "; ".join(f"{c}: " + ", ".join(f"{e} {s}" for e, s in ENGINE_STATUS[c].items()) for c in D.CASE_IDS) + ".",
        "7. All geometry at once: GET geometry.json (every STL with its case, configuration, units, frame and SHA-256)",
        "   or geometry.zip. Each STL stays in its own case's frame and units; they are NOT one scene.",
        "8. Every JSON document names its JSON Schema in `$schema` (schemas/{name}.schema.json); openapi.json describes",
        "   every endpoint. Download URLs carry ?v=<SHA-256 prefix>: use the URLs the documents give, not hand-built ones.",
        "9. Send a descriptive User-Agent: the site's CDN answers HTTP 403 to Python urllib's default one and to some AI",
        "   crawlers. If you are refused, the fallback URL above serves byte-identical files from the repository.",
        "10. To make a result reproducible, pin the release: GET versions.json, take the base_url of the release you used,",
        "   and fetch every path below from it instead of from the unversioned base. A release's files never change, and",
        "   every URL to an API file inside its documents points back into it. Quote the release number with any number you report.",
        "",
        "## Endpoints",
        "",
    ]
    for p, _, _, d in ENDPOINTS:
        if "{" not in p:
            walk.append(f"- {endpoint_url(p)} — {d}")
            continue
        # A template is not a URL to fetch: name it as a path and list the files it stands for.
        walk.append(f"- {p} (base URL + path, one file per value) — {d}:")
        walk += [f"  - {link(rel)}" for rel in expand(p)]
    walk += ["", "## Cases", ""]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        summ = percase[case]["summ"]
        walk.append(f"- {case}: {meta['title']}. {meta['short']} {summ['rows']} rows, {summ['distinct_points']} points, "
                    f"columns {', '.join(summ['columns'])}. Engines: " + ", ".join(f"{k} {v}" for k, v in ENGINE_STATUS[case].items()) + ".")
    walk += ["", "## Known data issues", "", "Each of these changes the result of a comparison if it is not accounted for.", ""]
    for case in D.CASE_IDS:
        for g in D.CASES[case]["known_issues"]:
            walk.append(f"- [{case}] {g}")
    walk += [
        "",
        "## Validation method",
        "",
        "Each case is solved through Eddy3D's production case writer (build-case -> run -> probe), not a hand-built",
        "OpenFOAM case; the probe sits at exactly the tunnel's measurement coordinates. Scores are normalised by U_H",
        "(k by U_H^2; Case E by U at 15.9 m); hit rate uses D = 0.25, W = 0.05 in those units. FAC2 is harsh by",
        "construction on sign-changing V and W; read R and hit rate there. The lateral sign of Case B is corrected",
        "before scoring. Cases C-E measure an omnidirectional SCALAR speed (thermistor): the model is scored as",
        "sqrt(|U|^2 + 2k) and as |U|, the two ends of the bracket the measurement must fall in.",
        "The ML surrogate predicts |U|/U_ref at 1.8 m; each case is scaled so its measurement plane lands there.",
        "On the full prediction window it does not respond to the wind direction at all (reversing the wind changes",
        "the field by < 1e-4 U_ref) — its scores grade the geometry it was given, not a wind it was told.",
        "",
        "## Cite",
        "",
        f"- {D.CITATION['benchmark']}",
        f"- {D.CITATION['guidelines']}",
        "- Each case's own requested citation and Zenodo DOI are in cases/{id}.json.",
        "",
    ]
    return "\n".join(walk)


def write_dataset_jsonld(percase):
    """schema.org Dataset metadata for the home page (docs/_includes/dataset-jsonld.html), so search engines
    that index datasets (Google Dataset Search among them) find the data, its licence and its downloads."""
    editors = sorted({p for c in D.CASE_IDS for p in D.CASES[c]["people"]["editors_distributors"]})
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"AIJ Urban Wind Environment benchmark, Cases {CASE_SPAN} — cleaned wind-tunnel and field data",
        "description": ("Wind-tunnel and field reference data of the Architectural Institute of Japan Urban Wind Environment (UWE) "
                        f"benchmark, Cases {CASE_SPAN} — isolated buildings and arrays of blocks and cubes, a high-rise among city "
                        "blocks, districts of Niigata, Shinjuku and Atsugi, a tree belt, and tracer-gas dispersion around buildings and cube "
                        "arrays, some non-isothermal — cleaned into SI units and one frame per case, with cleaned STL geometry and "
                        "Eddy3D's CFD validation scores where they exist."),
        "url": SITE + "/",
        "sameAs": REPO_URL,
        "version": RELEASE,
        "dateModified": RELEASE_DATE,
        "license": D.LICENSE["url"],
        "isAccessibleForFree": True,
        "keywords": ["computational fluid dynamics", "CFD validation", "wind tunnel", "urban wind environment",
                     "pedestrian wind", "tracer gas dispersion", "Architectural Institute of Japan", "benchmark"],
        "creator": [{"@type": "Person", "name": n.split(" (")[0]} for n in editors],
        "citation": D.CITATION["benchmark"],
        "isBasedOn": [f"https://doi.org/{D.CASES[c]['doi']}" for c in D.CASE_IDS if D.CASES[c]["doi"]],
        "measurementTechnique": ["hot-wire anemometry (split-fibre probes)", "thermistor anemometry", "laser Doppler velocimetry",
                                 "sonic and cup anemometry (field)", "hydrocarbon analyser and sorbent-tube sampling (tracer gas)"],
        "variableMeasured": ["mean velocity components U, V, W", "velocity variances", "turbulent kinetic energy k",
                             "mean scalar wind speed", "velocity ratio", "tracer-gas concentration", "air temperature and turbulent fluxes"],
        "distribution": [
            {"@type": "DataDownload", "name": f"{D.CASES[c]['title']}, measurement table",
             "encodingFormat": "text/csv", "contentUrl": download(f"cases/{c}/points.csv")["url"]} for c in D.CASE_IDS
        ] + [
            {"@type": "DataDownload", "name": "Geometry of every case (STL, metres)", "encodingFormat": "application/zip",
             "contentUrl": download("geometry.zip")["url"]},
            {"@type": "DataDownload", "name": "API index", "encodingFormat": "application/json", "contentUrl": url("index.json")},
        ],
    }
    body = json.dumps(dataset, indent=1, ensure_ascii=False).replace("</", "<\\/")
    os.makedirs(os.path.join(DOCS, "_includes"), exist_ok=True)
    with io.open(os.path.join(DOCS, "_includes", "dataset-jsonld.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write("<!-- Generated by scripts/build_api.py (write_dataset_jsonld). -->\n"
                f'<script type="application/ld+json">\n{body}\n</script>\n')


def write_changelog_include():
    """docs/_includes/api-changelog.md: the changelog index.json serves, as Markdown for the API page."""
    L = ["<!-- Generated by scripts/build_api.py from CHANGELOG. -->", ""]
    for entry in CHANGELOG:
        for c in entry["changes"]:   # the text is Markdown here and plain text in index.json: a bare <word> would open an HTML tag
            if re.search(r"<[A-Za-z/!?]", re.sub(r"`[^`]*`", "", c)):
                raise SystemExit(f"CHANGELOG {entry['version']}: put the text with a '<' in `code` so Markdown does not read it as HTML: {c[:80]}")
        L += [f"### {entry['version']} ({entry['date']})", ""] + [f"- {c}" for c in entry["changes"]] + [""]
    with io.open(os.path.join(DOCS, "_includes", "api-changelog.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


def expand(template):
    """The files a templated path stands for: every file this build wrote that the template matches."""
    rx = re.compile("^" + re.sub(r"\\\{[a-z]+\\\}", "[^/]+", re.escape(template)) + "$")
    return sorted(r for r in WRITTEN | {"index.json"} if rx.match(r))


def link(rel):
    """The URL a document gives for a file: plain for JSON, versioned (?v=) for downloads."""
    return url(rel) if rel.endswith(".json") else download(rel)["url"]


def endpoint_entry(path, media, schema, description):
    """A single-file endpoint carries its `url`; a templated one (cases/{id}.json) is not a URL to follow, so
    it says `templated` and lists every concrete file under `urls` (the template stays in `path`)."""
    entry = {"path": path, "method": "GET", "media_type": media, "description": description,
             "schema": schema_url(schema) if schema else None}
    if "{" in path:
        entry.update({"templated": True, "urls": [link(rel) for rel in expand(path)]})
    else:
        entry.update({"templated": False, "url": endpoint_url(path)})
    return entry


def endpoint_url(path):
    """Where a single-file endpoint is served: inside the tree, except the registry, which has one home."""
    return f"{LIVE_BASE}/{path}" if path in ROOT_ENDPOINTS else url(path)


def write_index():
    """Last: index.json lists every other file of the tree with its size and SHA-256."""
    files = sorted(WRITTEN - {"index.json"})
    write_json("index.json", "index", {
        "name": "AIJ UWE benchmark — cleaned data API",
        "description": ("Static JSON/CSV/STL endpoints for the Architectural Institute of Japan Urban Wind Environment "
                        f"benchmark (Cases {CASE_SPAN}) and Eddy3D's validation against it. Every file is a plain HTTP GET; nothing is computed on request."),
        "base_url": API_BASE,
        "tree": TREE,
        "release_base_url": PINNED_BASE,
        "versions_url": endpoint_url("versions.json"),
        "fallback_base_url": FALLBACK_BASE,
        "fallback_note": (f"the same files, served raw from the repository at the tag v{RELEASE}, which never moves (use when "
                          "the Pages site is not reachable)" if TREE == "release" else
                          "the same files, served raw from the repository's main branch (use when the Pages site is not reachable)"),
        "repository": REPO_URL, "site": SITE,
        "versions": {"release": RELEASE, "schema": SCHEMA_VERSION, "data": DATA_VERSION,
                     "clean_manifest": (D.clean_manifest() or {}).get("version")},
        "release": {"version": RELEASE, "date": RELEASE_DATE, "tag": f"v{RELEASE}",
                    "url": f"{REPO_URL}/releases/tag/v{RELEASE}", "base_url": RELEASE_BASE,
                    "changelog": f"{REPO_URL}/blob/v{RELEASE}/CHANGELOG.md"},
        "compatibility": COMPATIBILITY,
        "caching": CACHING,
        "changelog": CHANGELOG,
        "endpoints": [endpoint_entry(p, m, s, d) for p, m, s, d in ENDPOINTS],
        "case_ids": D.CASE_IDS,
        "files": [download(rel) for rel in files],
        "license_detail": D.LICENSE,
        "cite": D.CITATION,
        "agents": {
            "start_here": url("llms.txt"),
            "pin_a_version": f"GET {endpoint_url('versions.json')} and use the base_url of the release you want; paths are the same in every release",
            "walk": ["GET index.json", "GET cases.json and pick an id", "GET cases/{id}.json for frame, units and known_issues",
                     "GET cases/{id}/points.json (SI units, one frame) and cases/{id}/geometry.stl (metres)",
                     "GET validation.json or cases/{id}/validation.json before quoting any Eddy3D score; an engine that is not 'scored' has no result"],
        },
    })


def remove_stale():
    """Delete anything in the current tree this build did not write (a renamed or retired file). Other releases'
    frozen trees and versions.json belong to no tree and are never touched."""
    for rel in sorted(tree_files(API) - WRITTEN):
        os.remove(os.path.join(API, rel))
        print("removed stale", os.path.relpath(os.path.join(API, rel), API_ROOT).replace(os.sep, "/"))
    dirs_below = []
    for root, dirs, _ in os.walk(API):
        if root == API_ROOT:
            dirs[:] = [d for d in dirs if not is_release_dir(d)]
        dirs_below += [os.path.join(root, d) for d in dirs]
    for p in sorted(dirs_below, key=len, reverse=True):
        if not os.listdir(p):
            os.rmdir(p)


# ----------------------------------------------------------------------------- the registry of releases

def release_record(v):
    """One entry of versions.json. A release with a tree under docs/api/ is described by that tree's own index.json;
    one without (a release from before the layout) by its tag and what LEGACY_RELEASES records."""
    date = R.release_date(v)
    if not date:
        raise SystemExit(f"CHANGELOG.md has no dated section for {v}, which versions.json lists")
    base = f"{LIVE_BASE}/{v}"
    raw_tag = RAW_BASE.replace("/main/", f"/v{v}/")
    rec = {"version": v, "date": date, "status": None}
    tree_index = os.path.join(API_ROOT, v, "index.json")
    if os.path.isfile(tree_index):
        with io.open(tree_index, encoding="utf-8") as f:
            idx = json.load(f)
        hosted_later = v in LEGACY_RELEASES   # put there by scripts/host_release.py, so the copy is on main, not in the tag; its fallback is the tag
        if hosted_later and (idx["versions"]["schema"], idx["versions"]["data"]) != tuple(LEGACY_RELEASES[v].values()):
            raise SystemExit(f"docs/api/{v}/index.json and LEGACY_RELEASES disagree on release {v}'s schema or data version")
        rec.update({"schema_version": idx["versions"]["schema"], "data_version": idx["versions"]["data"],
                    "base_url": base, "index_url": f"{base}/index.json",
                    "fallback_base_url": raw_tag if hosted_later else f"{raw_tag}/{v}", "self_contained": True})
        if hosted_later:
            rec["note"] = (f"Released before the versioned layout and hosted here afterwards by scripts/host_release.py: the files of "
                           f"tag v{v}, byte for byte, with only their own addresses rewritten into this copy. The raw files at the tag "
                           f"(release.base_url in this copy's index.json) are the originals.")
    else:
        rec.update({**LEGACY_RELEASES[v], "base_url": raw_tag, "index_url": f"{raw_tag}/index.json", "fallback_base_url": None,
                    "self_contained": False,
                    "note": ("Released before the versioned layout and not regenerated: base_url is the raw files at the release "
                             "tag. Its documents link to the live /api/ paths, not back into base_url, so fetch its files by the "
                             "paths in its index.json instead of following those links.")})
    rec.update({"tag": f"v{v}", "tag_url": f"{REPO_URL}/releases/tag/v{v}", "changelog_url": f"{REPO_URL}/blob/v{v}/CHANGELOG.md"})
    return rec


def versions_document(data_version):
    """versions.json: every release newest first. A pure function of docs/api/'s frozen trees, CHANGELOG.md and
    LEGACY_RELEASES, so verify() can rebuild it and compare."""
    found = sorted({*LEGACY_RELEASES, *release_dirs(), RELEASE}, key=R.parse, reverse=True)
    if found[0] != RELEASE:
        raise SystemExit(f"VERSION {RELEASE} is older than {found[0]}, which has a release tree: versions only move forward")
    records = [release_record(v) for v in found]
    for i, rec in enumerate(records):
        rec["status"] = "latest" if i == 0 else "superseded"
    return {
        "$schema": schema_url_in(LIVE_BASE, "versions"), "schema_version": SCHEMA_VERSION, "data_version": data_version,
        "license": D.LICENSE["spdx"],
        "description": ("Every release of the data and API, newest first. The unversioned /api/ paths serve `latest`. To pin an "
                        "analysis to a release, fetch its files from its `base_url` instead (the paths are those of its "
                        "index.json): a release's files never change. `data_version` is the latest release's."),
        "latest": RELEASE, "latest_base_url": LIVE_BASE, "versions": records,
    }


def write_versions(data_version):
    """docs/api/versions.json: one registry, served from the unversioned root only (it changes at every release, so no
    frozen tree can hold it)."""
    with io.open(os.path.join(API_ROOT, "versions.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(versions_document(data_version)))


# ----------------------------------------------------------------------------- assets

def _png_size(path):
    """(width, height) of a PNG, from its IHDR chunk."""
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])


def web_copy(src, dst):
    """A WEB_WIDTH px wide copy of a 1200 dpi master, for the pages; returns its (width, height).

    Deterministic: LANCZOS resampling, the encoder's own settings, no metadata chunks, so two builds write the same bytes.
    An opaque RGBA master is stored as RGB (the page is white; an alpha channel only adds bytes). Pillow is imported here,
    so --check needs none; the masters are up to 120 MP, which is why the pixel limit is lifted in this function only."""
    from PIL import Image
    limit = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None
    try:
        with Image.open(src) as master:
            im = master
            im.load()
            if im.mode == "RGBA" and im.getchannel("A").getextrema() == (255, 255):
                im = im.convert("RGB")
            if im.width > WEB_WIDTH:
                im = im.resize((WEB_WIDTH, round(im.height * WEB_WIDTH / im.width)), Image.LANCZOS)
            im.save(dst, format="PNG", optimize=True)
            return im.size
    finally:
        Image.MAX_IMAGE_PIXELS = limit


def copy_assets():
    """docs/assets/geometry/ = every render, docs/assets/figures/ = every figure a run names, docs/assets/web/ = a 1600 px
    copy of each (same file name), docs/_data/figures.json = what a page needs to embed them; nothing else."""
    wanted = {
        "geometry": {D.render_file(c, cfg) for (c, cfg) in D.RENDER_CAPTIONS},
        "figures": {fig for r in RUNS for fig in r["figures"]},
    }
    clash = wanted["geometry"] & wanted["figures"]
    if clash:
        raise SystemExit(f"a render and a figure share the file name {sorted(clash)}; the web copies are named alike in one folder")
    masters = {}
    for sub_dir, names in wanted.items():
        src = os.path.join(FIGURES, "geometry") if sub_dir == "geometry" else FIGURES
        dst = os.path.join(ASSETS, sub_dir)
        os.makedirs(dst, exist_ok=True)
        for stale in set(os.listdir(dst)) - names:
            os.remove(os.path.join(dst, stale))
        for name in sorted(names):
            shutil.copyfile(os.path.join(src, name), os.path.join(dst, name))
            masters[name] = (sub_dir, os.path.join(dst, name))
    os.makedirs(WEB, exist_ok=True)
    for stale in set(os.listdir(WEB)) - set(masters):
        os.remove(os.path.join(WEB, stale))
    FIGURE_INFO.clear()
    for name in sorted(masters):
        sub_dir, master = masters[name]
        web = os.path.join(WEB, name)
        width, height = web_copy(master, web)
        FIGURE_INFO[name] = {"master": f"/assets/{sub_dir}/{name}", "master_bytes": os.path.getsize(master),
                             "master_width": _png_size(master)[0], "master_height": _png_size(master)[1],
                             "web": f"/assets/web/{name}", "web_bytes": os.path.getsize(web), "width": width, "height": height,
                             "mb": f"{os.path.getsize(master) / 1e6:.1f}"}
    os.makedirs(DATA_FILES, exist_ok=True)
    with io.open(os.path.join(DATA_FILES, "figures.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(FIGURE_INFO, indent=1, ensure_ascii=False, sort_keys=True) + "\n")


# ----------------------------------------------------------------------------- the README's figures

# README.md is written by hand, except for the figures: each sits between <!--fig name="x.png" alt="..." width="700"-->
# and <!--/fig--> on one line, and the build writes what is between them (the 1600 px copy at the width given, linked to
# its 1200 dpi master; label="0" puts the size in a tooltip instead of under the image).
FIG_MARKER = re.compile(r'<!--fig ((?:\w+="[^"]*"\s*)+)-->(.*?)<!--/fig-->')


def _readme_figure(attrs, info):
    name, width = attrs["name"], int(attrs["width"])
    f = info[name]
    master = "validation/figures/" + ("geometry/" if f["master"].startswith("/assets/geometry/") else "") + name
    img = (f'<img src="docs/assets/web/{name}" width="{width}" height="{round(width * f["height"] / f["width"])}" '
           f'loading="lazy" alt="{attrs["alt"]}">')
    if attrs.get("label") == "0":
        return f'<a href="{master}" title="{_original(f)}">{img}</a>'
    return f'<a href="{master}">{img}</a><br><sub><a href="{master}">{_original(f)}</a></sub>'


def readme_with_figures(text, info):
    def one(m):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        return f"<!--fig {m.group(1)}-->{_readme_figure(attrs, info)}<!--/fig-->"
    return FIG_MARKER.sub(one, text)


def sync_readme():
    path = os.path.join(REPO, "README.md")
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    new = readme_with_figures(text, FIGURE_INFO)
    if new != text:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)


# ----------------------------------------------------------------------------- site pages

# Row labels for the case pages' tables: the API keeps its snake_case keys, the pages read as prose.
LABELS = {
    "D_m": "Block size D (m)", "H_m": "Height H (m)", "Re": "Reynolds number", "Re_D": "Reynolds number Re_D",
    "Re_H": "Reynolds number Re_H", "U_H_m_s": "U_H (m/s)", "U_H_note": "U_H, note", "array": "Array",
    "array_extent_m": "Array extent (m)", "b_m": "Width b (m)", "blocks": "Blocks", "building": "Building",
    "centre_building": "Centre building", "configurations": "Configurations", "configurations_note": "Configurations, note",
    "depth_m": "Depth (m)", "district": "District", "instrument": "Instrument", "measurement_height_m": "Measurement height (m)",
    "measurement_height_note": "Measurement height, note", "measurement_planes": "Measurement planes",
    "new_buildings": "New buildings", "normalisation": "Normalisation", "pitch_note": "Pitch, note", "points": "Points",
    "roads": "Roads", "scale": "Scale", "scale_note": "Scale, note", "states": "States", "tower": "Tower",
    "tunnel": "Wind tunnel", "values": "Values", "width_m": "Width (m)", "wind_directions": "Wind directions",
    "wind_directions_deg": "Wind directions (°)",
    "coordinate_scale_applied": "Coordinate scale applied", "lateral_sign_applied": "Lateral sign applied",
    "origin": "Origin", "wind_direction_rotation": "Wind direction convention",
    "U_H_measured_m_s": "U_H, measured (m/s)", "U_ref_15_9m_m_s": "U_ref at 15.9 m (m/s)", "log_law": "Log law",
    "log_law_error_at_H": "Log-law error at H", "method": "Method", "note": "Note", "power_law_exponent": "Power-law exponent",
    "power_law_exponent_fitted": "Power-law exponent, fitted", "power_law_exponent_paper": "Power-law exponent, data paper",
    "turbulence_intensity_at_D": "Turbulence intensity at D", "u_star_m_s": "Friction velocity u* (m/s)",
    "z0_mm": "Roughness length z₀ (mm)", "length": "Length", "variance": "Variance", "velocity": "Velocity",
    "velocity_ratio": "Velocity ratio", "concentration_ratio": "Concentration ratio", "campaign": "Campaign",
}


def _label(k):
    return LABELS.get(k, k.replace("_", " "))


def _config_part(k, v):
    """'2D', 'WD 22.5°', 'split fibre', 'before construction': one part of a configuration's name."""
    if k == "wind_direction_deg":
        return f"WD {v:g}°"
    if k == "config":
        return {"bc": "before construction", "ac": "after construction", "default": "default"}.get(v, v)
    return str(v).replace("_", " ")


def _esc(text):
    """Plain text from the data, safe in Markdown on GitHub and in kramdown: emphasis, HTML and link characters are
    backslash-escaped, and a Liquid delimiter (which the site build would try to run) stops the build."""
    text = str(text)
    if "{{" in text or "{%" in text:
        raise SystemExit(f"a Liquid delimiter in text that becomes a page: {text[:80]!r}")
    out = []
    for i, piece in enumerate(re.split(r"(https?://[^\s<>]+)", text)):
        if i % 2:                                  # a URL becomes an autolink, which GitHub and kramdown both follow
            url, tail = re.match(r"(.*?)([.,;:]*)$", piece).groups()
            out.append(f"<{url}>" + tail)
            continue
        for ch in "\\*_<>[]'\"":              # quotes too: kramdown's smart quotes turn '-' into two opening quotes
            piece = piece.replace(ch, "\\" + ch)
        out.append(piece)
    return "".join(out)


def _cell(text):
    """_esc, and the pipe that would end a table cell."""
    return _esc(text).replace("|", "\\|")


def _md_value(v):
    """A configuration value as the text of one table cell: escaped once (the cell's pipes too, as in |y|)."""
    if isinstance(v, dict):
        return "<br>".join(f"**{_esc(_label(k))}**: {_md_value(x)}" for k, x in v.items())
    if isinstance(v, list):
        return ", ".join(_cell(x) for x in v)
    if isinstance(v, int) and not isinstance(v, bool) and abs(v) >= 10000:
        return f"{v:,}"
    return _cell(v)


def _asset(rel):
    return f"{{{{ '{rel}' | relative_url }}}}"


def _plain(html):
    """A caption as plain text (for alt attributes): tags dropped, quotes escaped."""
    out, inside = [], False
    for ch in html:
        inside = True if ch == "<" else False if ch == ">" else inside
        if not inside and ch != ">":
            out.append(ch)
    return "".join(out).replace('"', "&quot;")


def _original(f):
    """The link text to a figure's 1200 dpi master."""
    return f"1200 dpi original, {f['master_bytes'] / 1e6:.1f} MB"


def _web_img(f, alt):
    return (f'<img src="{_asset(f["web"])}" width="{f["width"]}" height="{f["height"]}" loading="lazy" '
            f'alt="{_plain(alt)}">')


def figure(src, alt, caption, cls="figure"):
    """One image with its caption, as HTML (<figure>), so the caption stays attached to the image. The page shows the
    1600 px copy; the image and a link under the caption lead to the 1200 dpi master."""
    f = FIGURE_INFO[src.rsplit("/", 1)[-1]]
    return [f'<figure class="{cls}">', f'<a href="{_asset(f["master"])}">{_web_img(f, alt)}</a>',
            f'<figcaption>{caption}<br><a class="original" href="{_asset(f["master"])}">{_original(f)}</a></figcaption>',
            "</figure>", ""]


def figure_table(cells, columns, caption=None):
    """Images side by side in a Markdown table marked {: .figures } (see docs/_sass/custom/custom.scss):
    cells are (src, alt, caption, link or None); the header row is blank and hidden by the stylesheet. An image with
    a link leads there; one without leads to its 1200 dpi master, named under it."""
    L = ["|" + " |" * columns, "|" + "---|" * columns]
    for i in range(0, len(cells), columns):
        row = []
        for src, alt, cap, link in cells[i:i + columns]:
            f = FIGURE_INFO[src.rsplit("/", 1)[-1]]
            img = f'<a href="{_asset(link or f["master"])}">{_web_img(f, alt)}</a>'
            original = "" if link else f'<br><a class="original" href="{_asset(f["master"])}">{_original(f)}</a>'
            row.append(f"{img}<br><span class=\"caption\">{cap.replace('|', '&#124;')}{original}</span>")
        row += [" "] * (columns - len(row))
        L.append("| " + " | ".join(row) + " |")
    L += ["{: .figures }", ""]
    if caption:
        L += [f'<p class="caption">{caption}</p>', ""]
    return L


# What the gallery says under each render. A case without an entry gets its one-line summary and its counts, so a
# new case needs no change here.
GALLERY_CAPTIONS = {
    "A": "Isolated building · {points} points · U, V, W and k",
    "B": "Isolated slab · {points} points · U, V, W and k",
    "C": "Centre block at 0D, 1D or 2D (2D shown) · {rows} scalar speeds at pedestrian height, 3 wind directions",
    "D": "A tower among 82 low blocks · {rows} measurements: scalar speed at 3 wind directions, velocity at 33 points",
    "E": "Before and after a 60 m high-rise (after shown) · {rows} velocity ratios over 16 wind directions",
}
# The caption of a case page's figure when the case has several renders (configurations on one scale).
RENDER_GROUP_CAPTIONS = {
    "C": "The three configurations of the centre block, on one scale; 120 measurement points each, at three wind directions.",
    "E": "The two states, on one scale (full-scale metres, +x east, +y north); the arrow marks SW, the direction Eddy3D is scored at.",
}

ENGINE_SHORT = {"openfoam12-realizableKE": "OpenFOAM 12", "openfoam12-kEpsilon": "OpenFOAM 12 k-ε", "openfoam12-kOmegaSST": "OpenFOAM 12 k-ω SST",
                "openlb": "OpenLB", "fluidx3d": "FluidX3D", "ml-surrogate": "ML surrogate"}
STATUS_CLASS = {"scored": "label-green", "running": "label-blue", "pending": "label-yellow", "not comparable": "label-grey"}
# Where the hand-written validation pages show each figure, beside its reading. A case's own Validation page links
# there instead of repeating the figure, so a figure is on the site once. A figure that is not listed is shown on the
# case's Validation page, unless it illustrates runs of ALL_CASES_FIGURE_MIN or more cases: then it is an all-cases
# figure, and the case pages link to the Validation overview instead of each repeating it.
FIGURE_HOME = {
    "cases-ab-openfoam-agreement.png": ("/validation/cases-ab/", "Cases A and B (OpenFOAM)"),
    "cases-ab-openfoam-profiles.png": ("/validation/cases-ab/", "Cases A and B (OpenFOAM)"),
    "cases-ab-engine-comparison.png": ("/validation/engines/", "OpenLB and FluidX3D"),
    "case-c-openfoam-agreement.png": ("/validation/case-c/", "Case C (OpenFOAM)"),
    "case-c-openfoam-bias-map.png": ("/validation/case-c/", "Case C (OpenFOAM)"),
    "case-d-openfoam-agreement.png": ("/validation/case-d/", "Case D (OpenFOAM)"),
    "case-e-openfoam-agreement.png": ("/validation/case-e/", "Case E (OpenFOAM)"),
    "case-e-openfoam-bias-map.png": ("/validation/case-e/", "Case E (OpenFOAM)"),
    "cases-hi-openfoam-agreement.png": ("/validation/cases-hi/", "Cases H and I (OpenFOAM)"),
    "case-i-openfoam-closures.png": ("/validation/cases-hi/", "Cases H and I (OpenFOAM)"),
    "ml-surrogate-agreement.png": ("/validation/ml-surrogate/", "ML surrogate"),
}
ALL_CASES_FIGURE_MIN = 3
# A score table stays open up to this many rows, a table of configurations up to OPEN_LIST_ROWS; a longer one sits in
# a closed <details>.
OPEN_TABLE_ROWS = 12
OPEN_LIST_ROWS = 8
# Facts the case page's "At a glance" table shows, one row per group: the first configuration key present in it,
# under that key's label. The Data page has everything.
GLANCE = [("building", "array", "tower", "district"), ("scale",), ("Re_H", "Re_D", "Re"), ("U_H_m_s", "normalisation"),
          ("wind_directions", "wind_directions_deg"), ("measurement_height_m", "measurement_planes")]
# The hand-written page that reads a case's results (a case without one is read on the Validation overview).
READING_PAGES = {"A": "/validation/cases-ab/", "B": "/validation/cases-ab/", "C": "/validation/case-c/",
                 "D": "/validation/case-d/", "E": "/validation/case-e/", "H": "/validation/cases-hi/", "I": "/validation/cases-hi/"}


def _engine_name(engine_id):
    return ENGINE_SHORT.get(engine_id, engine_id)


def status_label(status):
    return f'<span class="label {STATUS_CLASS[status]} status">{status}</span>'


def _front(title, nav_order, parent=None, grand_parent=None, has_children=None, has_toc=None, description=None):
    """Front matter of a generated page. `generated: true` makes the footer point at this script, not at the page."""
    L = ["---", f'title: "{title}"']
    if parent:
        L.append(f'parent: "{parent}"')
    if grand_parent:
        L.append(f'grand_parent: "{grand_parent}"')
    L.append(f"nav_order: {nav_order}")
    if has_children is not None:
        L.append(f"has_children: {'true' if has_children else 'false'}")
    if has_toc is not None:
        L.append(f"has_toc: {'true' if has_toc else 'false'}")
    L.append("generated: true")
    if description:
        L.append(f'description: "{description.replace(chr(34), chr(39))}"')
    return L + ["---", ""]


def _write(rel, lines):
    path = os.path.join(DOCS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")


def _page_url(slug, sub=""):
    return f"/cases/{slug}/" + (f"{sub}/" if sub else "")


def _link(text, url, anchor=""):
    return f"[{text}]({_asset(url)}{anchor})"


def _toc():
    """just-the-docs' collapsible table of contents of a page's headings."""
    return ['<details open markdown="block">', "  <summary>", "    Contents", "  </summary>", "  {: .text-delta }",
            "1. TOC", "{:toc}", "</details>", ""]


def _is_control(label):
    """A headline whose label says 'control' is a negative control (the frame flipped, the wind reversed, the
    building removed): it shows the test can fail, it is not a result, so no summary of results includes it."""
    return "control" in label.lower()


def _headline_ranges(entries):
    """{'R': (lo, hi), 'Fac2': (lo, hi)} over the headline scores of these validation entries, controls excluded;
    None when there is none."""
    vals = {"R": [], "Fac2": []}
    for e in entries:
        for label, key in e["headline"].items():
            if _is_control(label):
                continue
            for m in vals:
                v = e["scores"][key].get(m)
                if v is not None:
                    vals[m].append(v)
    if not vals["R"]:
        return None
    return {m: (min(v), max(v)) for m, v in vals.items() if v}


def _range(lo_hi, signed):
    if lo_hi is None:
        return "—"
    lo, hi = (f"{x:+.2f}" if signed else f"{x:.2f}" for x in lo_hi)
    return lo if lo == hi else f"{lo} … {hi}"


def _shared_figures(percase):
    """Figures of runs of at least ALL_CASES_FIGURE_MIN cases: {file name: set of case ids}."""
    users = {}
    for case, p in percase.items():
        for e in p["results"]:
            for fig in e["figures"]:
                users.setdefault(fig["url"].rsplit("/", 1)[-1], set()).add(case)
    return {name: cases for name, cases in users.items() if len(cases) >= ALL_CASES_FIGURE_MIN}


def build_gallery(percase):
    """docs/_includes/case-gallery.md: every case, two to a row (three once there are more than six), each render
    linked to its page."""
    cells = []
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        summ = percase[case]["summ"]
        counts = dict(points=f"{summ['distinct_points']:,}", rows=f"{summ['rows']:,}")
        cap = (GALLERY_CAPTIONS[case].format(**counts) if case in GALLERY_CAPTIONS
               else f"{_esc(meta['short'])} · {counts['rows']} rows")
        cells.append((f"/assets/geometry/{D.render_file(case)}", meta["title"], f"<strong>{meta['title']}</strong><br>{cap}",
                      _page_url(meta["slug"])))
    _write("_includes/case-gallery.md",
           ["<!-- Generated by scripts/build_api.py; edit GALLERY_CAPTIONS there. -->", ""]
           + figure_table(cells, 2 if len(cells) <= 6 else 3))


def build_cases_table(percase):
    """docs/_includes/cases-table.md: one row per case, what it is, what was measured, who scored it."""
    L = ["<!-- Generated by scripts/build_api.py. -->", "",
         "| Case | What it is | Measured | Scored by |", "|---|---|---|---|"]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        summ = percase[case]["summ"]
        scored = [_engine_name(e["id"]) for e in case_engines(case) if ENGINE_STATUS[case][e["id"]] == "scored"]
        measured = f"{summ['rows']:,} rows over {summ['distinct_points']:,} points; {_cell(', '.join(meta['quantities']))}"
        L.append(f"| {_link(_cell(meta['title']), _page_url(meta['slug']))} | {_cell(meta['short'])} | {measured} | "
                 f"{', '.join(scored) if scored else 'none yet'} |")
    _write("_includes/cases-table.md", L)


def build_cases_frames():
    """docs/_includes/cases-frames.md: each case's length unit, the unit of what it measures, and its origin."""
    L = ["<!-- Generated by scripts/build_api.py. -->", "", "| Case | Length unit | Measured in | Origin |", "|---|---|---|---|"]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        units = meta["units"]
        measured = units.get("velocity", next((v for k, v in units.items() if k != "length"), ""))
        L.append(f"| {_link(_cell(meta['title']), _page_url(meta['slug'], 'data'), '#frame-and-units')} | {_cell(units.get('length', ''))} | "
                 f"{_cell(measured)} | {_cell(meta['frame'].get('origin', ''))} |")
    _write("_includes/cases-frames.md", L)


def build_validation_matrix(percase):
    """docs/_includes/validation-matrix.md: every case against every engine, status and the range of the headline
    R and FAC2 (negative controls excluded). Five columns of short cells: it needs no sideways scrolling."""
    L = ["<!-- Generated by scripts/build_api.py. -->", "",
         "| Case | " + " | ".join(_engine_name(e["id"]) for e in MATRIX_ENGINES) + " |", "|---" * (len(MATRIX_ENGINES) + 1) + "|"]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        cells = []
        for e in MATRIX_ENGINES:
            status = ENGINE_STATUS[case][e["id"]]
            entries = [r for r in percase[case]["results"] if r["engine"] == e["id"]]
            cell = status_label(status)
            ranges = _headline_ranges(entries) if entries else None
            if ranges:
                cell += (f'<br><span class="caption">R {_range(ranges["R"], True)}'
                         f'<br>FAC2 {_range(ranges.get("Fac2"), False)}</span>')
            cells.append(cell)
        L.append(f"| {_link(_cell(meta['title']), _page_url(meta['slug'], 'validation'))} | " + " | ".join(cells) + " |")
    _write("_includes/validation-matrix.md", L)


def build_known_issues():
    """docs/_includes/known-issues-fm.md: the known issues of the cases whose sections are not hand-written (F to M), one
    section per case, from the same lists the Data pages and llms.txt carry."""
    L = ["<!-- Generated by scripts/build_api.py from each case's known_issues. -->", ""]
    for case in D.CASE_IDS:
        if case in "ABCDE":
            continue
        meta = D.CASES[case]
        L += [f"## Case {case}", "", f"{_esc(meta['title'])}.", ""] + [f"- {_esc(g)}" for g in meta["known_issues"]] + [""]
    _write("_includes/known-issues-fm.md", L)


def build_version_label():
    """docs/_includes/version-label.html: the release, the API schema version and the data fingerprint, for the
    sidebar footer. The numbers are this build's, so the label cannot say something the files do not."""
    _write("_includes/version-label.html", [
        "<!-- Generated by scripts/build_api.py. -->",
        f'<span class="version-label"><a href="{{{{ \'/api-reference/versions/\' | relative_url }}}}">Release {RELEASE}</a>'
        f' · API schema {SCHEMA_VERSION}'
        f' · <abbr title="SHA-256 of the served data; the full value is in api/index.json">data {DATA_VERSION[:8]}</abbr></span>'])


def _frame_traps(meta):
    """One sentence per way the cleaned table differs from the published file, read from the case's frame."""
    frame, traps = meta["frame"], []
    if frame.get("lateral_sign_applied") not in (None, 1):
        traps.append(f"The lateral velocity V is multiplied by {frame['lateral_sign_applied']} in the cleaned table "
                     "(`lateral_sign_applied`): the published file's V has the other sign convention.")
    if frame.get("coordinate_scale_applied") not in (None, 1, 1.0):
        traps.append(f"The published coordinates are multiplied by {frame['coordinate_scale_applied']:g} in the cleaned table "
                     "(`coordinate_scale_applied`).")
    if "wind_direction_rotation" in frame:
        traps.append("The sense in which the wind direction rotates is a convention to check before comparing at "
                     "any direction other than 0° (see *Frame and units* on the Data page).")
    return traps


def _case_page(case, meta, p, shared):
    summ, results = p["summ"], p["results"]
    base, data_url, val_url = _page_url(meta["slug"]), _page_url(meta["slug"], "data"), _page_url(meta["slug"], "validation")
    n = D.CASE_IDS.index(case) + 1
    L = _front(meta["title"], n, parent="Cases", has_children=True, has_toc=False, description=meta["short"])
    L += [f"# {meta['title']}", "", f"{_esc(meta['short'])}", "{: .fs-5 .fw-300 .lede }", "",
          f"{_link('Reference data', data_url)}{{: .btn .btn-primary }} {_link('Validation', val_url)}{{: .btn }} "
          f"{_link('Case as JSON', f'/api/cases/{case}.json')}{{: .btn }}", ""]
    cfgs = [cfg for (c, cfg) in D.RENDER_CAPTIONS if c == case]
    if not cfgs:
        pass                                           # a case without a render has no figure
    elif len(cfgs) == 1:
        L += figure(f"/assets/geometry/{D.render_file(case)}", meta["title"], D.RENDER_CAPTIONS[(case, cfgs[0])], "figure render")
    else:
        group = RENDER_GROUP_CAPTIONS.get(case, f"The configurations of {meta['title']}, on one scale.")
        L += figure_table([(f"/assets/geometry/{D.render_file(case, cfg)}", f"{meta['title']}, {cfg}",
                            D.RENDER_CAPTIONS[(case, cfg)], None) for cfg in cfgs], min(len(cfgs), 3), group)
    L += ["## At a glance", "", "| Fact | Value |", "|---|---|"]
    conf = meta["configuration"]
    for keys in GLANCE:
        key = next((k for k in keys if k in conf), None)
        if key:
            L.append(f"| {_cell(_label(key))} | {_md_value(conf[key])} |")
    L.append(f"| Measured | {summ['rows']:,} rows over {summ['distinct_points']:,} points: {_cell(', '.join(meta['quantities']))} |")
    L += ["", "## Agreement with the tunnel", ""]
    if results:
        L += ["| Engine | Status | R | FAC2 |", "|---|---|---|---|"]
        for e in case_engines(case):
            ranges = _headline_ranges([r for r in results if r["engine"] == e["id"]])
            L.append(f"| {_engine_name(e['id'])} | {status_label(ENGINE_STATUS[case][e['id']])} | "
                     + (" | ".join((_range(ranges["R"], True), _range(ranges.get("Fac2"), False))) if ranges else "— | —") + " |")
        L += ["{: .scores }", "",
              "R and FAC2 are the range over the headline scores of an engine's runs (velocity components, k, wind directions; "
              "negative controls left out). *Scored* means a run exists and its scores are served, not that it agrees: "
              f"every score, its figures and its reading are on the {_link('Validation page', val_url)}.", ""]
    else:
        L += [f"**No validation has been run for this case yet.** Nothing on this page is a claim about it. {QUEUED} Engine status: "
              + " · ".join(f"{_engine_name(k)} {status_label(v)}" for k, v in ENGINE_STATUS[case].items()), ""]
    traps = _frame_traps(meta)
    L += ["{: .warning-title }", "> Before you compare", ">",
          "> The cleaned table is in SI units and one frame, with this case's corrections applied once; "
          "do not apply them again to the published files.", ">"]
    for t in traps:
        L.append(f"> - {t}")
    L += [f"> - {len(meta['known_issues'])} known issues in the published files are listed under "
          f"{_link('Known data issues', data_url, '#known-data-issues')}.", ""]
    return L


def _case_data_page(case, meta, p):
    summ, configs = p["summ"], p["configs"]
    n = D.CASE_IDS.index(case) + 1
    L = _front("Data", 1, parent=meta["title"], grand_parent="Cases", has_children=False,
               description=f"{meta['title']}: configuration, frame and units, reference data, inflow and known data issues.")
    L += [f"# Case {case}: reference data", "{: .no_toc }", ""] + _toc()
    L += ["## Configuration", "", "| Parameter | Value |", "|---|---|"]
    for k, v in meta["configuration"].items():
        L.append(f"| {_cell(_label(k))} | {_md_value(v)} |")
    L += ["", "## Frame and units", "", "| Property | Definition |", "|---|---|"]
    for k, v in meta["frame"].items():
        L.append(f"| {_cell(_label(k))} | {_md_value(v)} |")
    for k, v in meta["units"].items():
        L.append(f"| Unit of {'k' if k == 'k' else _cell(_label(k).lower())} | {_cell(v)} |")
    af = meta.get("approach_flow_file")
    L += ["", "## Reference data", "",
          f"Source in this repository: `{meta['reference_file']}`" + (f" (approach flow: `{af}`)" if af else "") + ".", "",
          f"The cleaned table has **{summ['rows']:,} rows** over **{summ['distinct_points']:,} distinct points**; "
          f"columns `{'`, `'.join(summ['columns'])}`.", ""]
    if summ["nulls"]:
        L += ["Unmeasured cells (null): " + ", ".join(f"{k} {v}" for k, v in summ["nulls"].items()) + ".", ""]
    rows = []
    for c in configs:
        key = ", ".join(_config_part(k, v) for k, v in c.items() if k not in ("points", "measured", "points_per_direction", "wind_directions"))
        val = c.get("points", c.get("points_per_direction"))
        if "measured" in c:
            val = f"{val} ({c['measured']} measured)"
        if "wind_directions" in c:
            key += ", 16 wind directions"
            val = f"{val} per direction"
        rows.append(f"| {_cell(key)} | {val} |")
    table = ["| Configuration | Points |", "|---|---|"] + rows
    if len(rows) > OPEN_LIST_ROWS:
        L += ['<details markdown="block">', f"  <summary>The {len(rows)} configurations and their points</summary>", ""] + table + ["", "</details>", ""]
    else:
        L += table + [""]
    cols = ["| Column | Meaning |", "|---|---|"] + [f"| `{c}` | {_cell(COLUMN_MEANING.get(c, ''))} |" for c in summ["columns"]]
    L += ["## Columns", "", "The columns of the cleaned table (`points.csv`, `points.json`), in order.", ""]
    if len(cols) - 2 > OPEN_LIST_ROWS:
        L += ['<details markdown="block">', f"  <summary>The {len(cols) - 2} columns and what each holds</summary>", ""] + cols + ["", "</details>", ""]
    else:
        L += cols + [""]
    inflow = meta.get("inflow_fit")
    if inflow:
        L += ["## Inflow", "", "| Property | Value |", "|---|---|"]
        for k, v in inflow.items():
            if k == "windows":
                for w in v:
                    L.append("| Fit window | " + "; ".join(f"{_cell(_label(a))} {_cell(b)}" for a, b in w.items()) + " |")
            else:
                L.append(f"| {_cell(_label(k))} | {_md_value(v)} |")
        L.append("")
    L += ["## Known data issues", "", "Each of these changes the result of a comparison if it is not accounted for.", ""]
    for g in meta["known_issues"]:
        L.append(f"- {_esc(g)}")
    L += ["", "## API", "", "| Resource | Endpoint |", "|---|---|"]
    for name, rel in (("Case", f"cases/{case}.json"), ("Points (JSON)", f"cases/{case}/points.json"),
                      ("Points (CSV)", f"cases/{case}/points.csv"), ("Approach flow (CSV)", f"cases/{case}/approach_flow.csv"),
                      ("Geometry", f"cases/{case}/geometry.json"), ("Geometry (STL)", f"cases/{case}/geometry.stl"),
                      ("Validation", f"cases/{case}/validation.json")):
        L.append(f"| {name} | {_link('`/api/' + rel + '`', '/api/' + rel)} |")
    L += ["", "## Attribution", "", f"- Data collectors: {_esc(', '.join(meta['people']['data_collectors']))}",
          f"- Editors and distributors: {_esc(', '.join(meta['people']['editors_distributors']))}"]
    if meta["doi"]:
        L.append(f"- DOI: [{meta['doi']}](https://doi.org/{meta['doi']})")
    elif meta.get("doi_note"):
        L.append(f"- DOI: {_esc(meta['doi_note'])}")
    L += [f"- Citation requested: {_esc(meta['citation_requested'])}", "- Licence: CC BY 4.0"]
    return L


def _score_table(e):
    """One run's headline scores: a row per score, the metrics across. A bare '|' in a label (|U|) is escaped."""
    L = ["| Score | R | FAC2 | FB | Hit rate | n |", "|---|---|---|---|---|---|"]
    for label, key in e["headline"].items():
        s = e["scores"][key]
        num = lambda m, f: "—" if s.get(m) is None else f"{s[m]:{f}}"  # noqa: E731
        L.append(f"| {_cell(label)} | {num('R', '+.3f')} | {num('Fac2', '.3f')} | {num('Fb', '+.3f')} | "
                 f"{num('HitRate', '.3f')} | {num('Count', 'd')} |")
    L.append("{: .scores }")
    return L


def _case_validation_page(case, meta, p, shared):
    results = p["results"]
    n = D.CASE_IDS.index(case) + 1
    L = _front("Validation", 2, parent=meta["title"], grand_parent="Cases", has_children=False,
               description=f"{meta['title']}: Eddy3D's scores against the tunnel data, by engine.")
    L += [f"# Case {case}: validation", "{: .no_toc }", ""]
    L += ["Engine status: " + " · ".join(f"{_engine_name(k)} {status_label(v)}" for k, v in ENGINE_STATUS[case].items()), ""]
    if not results:
        L += [f"**No validation has been run for this case yet.** Nothing on this page is a claim about it. {QUEUED}", ""]
        return L
    L += ["*Scored* means a run exists and its scores are below, not that it agrees. How to read them is on "
          f"{_link('the reading page', READING_PAGES.get(case, '/validation/'))}; the "
          f"{_link('Validation', '/validation/')} overview says what each status means and why an engine is *not comparable*.", ""]
    names = {e["id"]: e["name"] for e in ENGINES}
    figures, fig_no = [], 1
    for e in results:
        L += [f"## {_esc(names[e['engine']])}" + (f", configuration {_esc(e['configuration'])}" if e["configuration"] else ""), ""]
        if e["quantity"]:
            L += [f"Quantity: {_esc(e['quantity'])}.", ""]
        if e["recirculation_Lr_over_H"] is not None:
            L += [f"Reattachment length L<sub>r</sub>/H = {e['recirculation_Lr_over_H']:.2f}.", ""]
        table = _score_table(e)
        if len(e["headline"]) > OPEN_TABLE_ROWS:
            L += ['<details markdown="block">', f"  <summary>All {len(e['headline'])} headline scores</summary>", ""] + table + ["", "</details>", ""]
        else:
            L += table + [""]
        pairs_rel = e["pairs"]["path"]
        L += [f"{_esc(e['normalisation'])}. Per-point values: {_link('`/api/' + pairs_rel + '`', '/api/' + pairs_rel)}. "
              f"Reproduce: {_esc(e['reproduce'])}.", ""]
        figures += [f for f in e["figures"] if f not in figures]
    own, elsewhere = [], {}
    for fig in figures:
        name = fig["url"].rsplit("/", 1)[-1]
        if name in FIGURE_HOME:
            elsewhere.setdefault(FIGURE_HOME[name], []).append(fig)
        elif name in shared:
            elsewhere.setdefault(("/validation/", "Validation"), []).append(fig)
        else:
            own.append(fig)
    if own:
        L += ["## Figures", ""]
    for fig in own:
        name = fig["url"].rsplit("/", 1)[-1]
        L += figure(f"/assets/figures/{name}", fig["caption"], f"<strong>Figure {fig_no}.</strong> {fig['caption']}")
        fig_no += 1
    if elsewhere:
        L += ["## Figures", ""] if not own else []
        L += ["The figures for these runs are shown once, beside their reading: "
              + "; ".join(f"{_link(label, page)}" for (page, label) in elsewhere) + ".", ""]
    return L


def build_pages(percase):
    """The site's generated pages, one set per case in D.CASE_IDS (any id the data has gets its pages): the case page
    (summary, render, status), its Data page and its Validation page, plus the includes the hand-written pages use."""
    shared = _shared_figures(percase)
    build_gallery(percase)
    build_cases_table(percase)
    build_cases_frames()
    build_validation_matrix(percase)
    build_known_issues()
    build_version_label()
    for case in D.CASE_IDS:
        meta, p = D.CASES[case], percase[case]
        _write(f"cases/{meta['slug']}.md", _case_page(case, meta, p, shared))
        _write(f"cases/{meta['slug']}/data.md", _case_data_page(case, meta, p))
        _write(f"cases/{meta['slug']}/validation.md", _case_validation_page(case, meta, p, shared))


# ----------------------------------------------------------------------------- verify

TEMPLATED_URL = re.compile(r"https?://[^\s\"'<>]*\{[^\s\"'<>]*")
API_URL = re.compile(r"https://sustainableurbansystems\.com/[^\s\"'<>)]*?/api(?:/[^\s\"'<>)]*)?")


def _strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)
    elif isinstance(obj, str):
        yield obj


def _read(root, rel):
    with io.open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def _link_problem(sv, base, root, on_disk, index):
    """Why a URL a tree's document gives is wrong, or None. Inside a tree every URL stays in the tree; the registry
    (versions.json) is the one file outside it, and the latest alias may name its release's frozen copy."""
    if sv == base or "{" in sv or not (sv == LIVE_BASE or sv.startswith(LIVE_BASE + "/")):
        return None
    if sv == f"{LIVE_BASE}/versions.json":
        return None if os.path.isfile(os.path.join(API_ROOT, "versions.json")) else "link to versions.json, which does not exist"
    if base == LIVE_BASE and sv == f"{LIVE_BASE}/{index['versions']['release']}":
        return None if os.path.isdir(os.path.join(API_ROOT, index["versions"]["release"])) else f"names {sv}, which does not exist"
    if not sv.startswith(base + "/"):
        return f"link {sv} leaves the tree (it must start with {base}/)"
    rel_t, _, query = sv[len(base) + 1:].partition("?v=")
    if rel_t not in on_disk:
        return f"link to {rel_t}, which does not exist"
    if query and _sha256(rel_t, root)[0][:12] != query:
        return f"link to {rel_t} carries a stale ?v={query}"
    return None


def verify_tree(root, base, strict_assets):
    """One tree (the latest alias or a frozen release), checked on its own: the file list against index.json, every
    document against the schema it names, every link, openapi.json, the data files and the archive."""
    problems = []
    import jsonschema
    from openapi_spec_validator import validate as validate_openapi

    def load(rel):
        return json.loads(_read(root, rel))

    on_disk = tree_files(root)
    index = load("index.json")
    if index["base_url"] != base:
        problems.append(f"index.json base_url is {index['base_url']}, this tree is served at {base}")
    if index.get("tree") is not None and index["tree"] != ("latest" if base == LIVE_BASE else "release"):
        problems.append(f"index.json says tree={index['tree']}")
    if base != LIVE_BASE and index["versions"]["release"] != os.path.basename(root):
        problems.append(f"the tree {os.path.basename(root)}/ holds release {index['versions']['release']}")

    # index.json: lists every other file, with the right size and hash
    listed = {f["path"]: f for f in index["files"]}
    for rel in sorted(on_disk - {"index.json"} - set(listed)):
        problems.append(f"{rel} is served but not listed in index.json")
    for rel, f in listed.items():
        if rel not in on_disk:
            problems.append(f"index.json lists {rel}, which does not exist")
            continue
        sha, n = _sha256(rel, root)
        if (sha, n) != (f["sha256"], f["bytes"]):
            problems.append(f"index.json size/hash of {rel} disagree with the file")

    # schemas: valid themselves, and every document valid against the one it names
    schemas = {}
    for rel in sorted(r for r in on_disk if r.startswith("schemas/")):
        sc = load(rel)
        jsonschema.Draft202012Validator.check_schema(sc)
        schemas[sc["$id"]] = sc
    versions = set()
    for rel in sorted(r for r in on_disk if r.endswith(".json") and not r.startswith("schemas/") and r != "openapi.json"):
        try:
            doc = load(rel)
        except ValueError as e:
            problems.append(f"{rel}: not valid JSON ({str(e)[:80]})")
            continue
        sc = schemas.get(doc.get("$schema"))
        if sc is None:
            problems.append(f"{rel}: $schema {doc.get('$schema')} is not a published schema")
            continue
        for err in jsonschema.Draft202012Validator(sc).iter_errors(doc):
            problems.append(f"{rel}: {'/'.join(str(p) for p in err.absolute_path)}: {err.message[:160]}")
        versions.add((doc.get("schema_version"), doc.get("data_version")))
        # every link into the API resolves inside the tree, and a ?v= is the file's current hash prefix
        for sv in _strings(doc):
            bad = _link_problem(sv, base, root, on_disk, index)
            if bad:
                problems.append(f"{rel}: {bad}")
            # Site assets (figures, renders) are not part of a release's frozen files: only the current build's must exist.
            if strict_assets and sv.startswith(SITE + "/assets/") and not os.path.isfile(os.path.join(DOCS, sv[len(SITE) + 1:])):
                problems.append(f"{rel}: link to site asset {sv[len(SITE) + 1:]}, which does not exist")
    if len(versions) != 1:
        problems.append(f"documents disagree on schema/data version: {sorted(versions)}")

    # A URI template is not a URL; and a text file may not send a reader out of its tree.
    for rel in sorted(r for r in on_disk if r.endswith((".json", ".txt"))):
        text = _read(root, rel)
        for bad in TEMPLATED_URL.findall(text):
            problems.append(f"{rel}: {bad} is a URI template, not a URL to follow")
        if rel.endswith(".txt"):
            for u in sorted(set(API_URL.findall(text))):
                bad = _link_problem(u.rstrip(".,;"), base, root, on_disk, index)
                if bad:
                    problems.append(f"{rel}: {bad}")

    # openapi.json: a valid OpenAPI 3.1 document whose paths exist
    oa = load("openapi.json")
    try:
        validate_openapi(oa)
    except Exception as e:  # noqa: BLE001 — report whatever the validator found
        problems.append(f"openapi.json is not valid OpenAPI: {str(e)[:300]}")
    for p in oa["paths"]:
        pattern = p.lstrip("/")
        if pattern in ROOT_ENDPOINTS:
            if not os.path.isfile(os.path.join(API_ROOT, pattern)):
                problems.append(f"openapi path {p} has no file")
        elif "{" not in pattern:
            if pattern not in on_disk:
                problems.append(f"openapi path {p} has no file")
        else:
            rx = re.compile("^" + re.sub(r"\\\{[a-z]+\\\}", "[^/]+", re.escape(pattern)) + "$")
            if not any(rx.match(r) for r in on_disk):
                problems.append(f"openapi path {p} matches no file")

    # content checks
    for case in index["case_ids"]:
        pj = load(f"cases/{case}/points.json")
        with io.open(os.path.join(root, f"cases/{case}/points.csv"), encoding="utf-8", newline="") as f:
            n_csv = sum(1 for _ in csv.reader(f)) - 1
        if pj["n"] != len(pj["points"]) or pj["n"] != n_csv:
            problems.append(f"case {case}: points.json n={pj['n']} rows={len(pj['points'])} csv={n_csv}")
        gj = load(f"cases/{case}/geometry.json")
        for g in gj["files"]:
            if D.stl_stats(D.read_ascii_stl(os.path.join(root, g["path"])))["triangles"] != g["stats"]["triangles"]:
                problems.append(f"case {case}: {g['path']} triangle count disagrees with geometry.json")
    gall = load("geometry.json")
    with zipfile.ZipFile(os.path.join(root, "geometry.zip")) as z:
        names = set(z.namelist())
        for it in gall["files"]:
            if it["archive_name"] not in names or hashlib.sha256(z.read(it["archive_name"])).hexdigest() != it["sha256"]:
                problems.append(f"geometry.zip lacks {it['archive_name']} or holds different bytes")
        if len(names) != len(gall["files"]):
            problems.append(f"geometry.zip holds {len(names)} files, geometry.json lists {len(gall['files'])}")
    return problems


# Header fields and lines a release tree and the alias legitimately word differently (they name themselves).
TREE_SPECIFIC_INDEX = {"tree", "fallback_note"}
SAME_IN_BOTH_INDEXES = ("release", "release_base_url", "versions_url")


def _alias_form(text):
    """The text of a release-tree file with its frozen addresses replaced by the alias's."""
    return text.replace(PINNED_BASE, LIVE_BASE).replace(RELEASE_BASE, RAW_BASE)


def _normal(obj):
    """A parsed release-tree document with its addresses in the alias's form."""
    return json.loads(_alias_form(json.dumps(obj, ensure_ascii=False)))


def verify_alias_matches_release():
    """The alias is the newest release: file for file, the same bytes, except that a document names its own tree."""
    problems = []
    rel_root = os.path.join(API_ROOT, RELEASE)
    a_files, r_files = tree_files(API_ROOT), tree_files(rel_root)
    for rel in sorted(a_files ^ r_files):
        problems.append(f"{rel} is in only the {'alias' if rel in a_files else 'release ' + RELEASE + ' tree'}")
    for rel in sorted(a_files & r_files):
        with io.open(os.path.join(API_ROOT, rel), "rb") as f:
            a = f.read()
        with io.open(os.path.join(rel_root, rel), "rb") as f:
            r = f.read()
        if rel.endswith((".csv", ".stl", ".zip")):
            if a != r:
                problems.append(f"{rel} differs between the alias and release {RELEASE}")
        elif rel == "index.json":
            ia, ir = json.loads(a), json.loads(r)
            # the fields that name the release and the registry read the same in both trees; the rest is re-addressed
            for k in SAME_IN_BOTH_INDEXES:
                if ia.get(k) != ir.get(k):
                    problems.append(f"index.json `{k}` differs between the alias and release {RELEASE}")
                ia.pop(k, None), ir.pop(k, None)
            ir = _normal(ir)
            for d in (ia, ir):
                for k in TREE_SPECIFIC_INDEX:
                    d.pop(k, None)
                # a JSON file's hash and size follow its own addresses, so only the other files' entries must agree
                d["files"] = [f for f in d["files"] if not f["path"].endswith((".json", ".txt"))]
            if ia != ir:
                problems.append(f"index.json of the alias and of release {RELEASE} disagree beyond their own addresses: "
                                + ", ".join(k for k in sorted(set(ia) | set(ir)) if ia.get(k) != ir.get(k)))
        elif rel == "openapi.json":
            ia, ir = json.loads(a), _normal(json.loads(r))
            ia.pop("servers"), ir.pop("servers")
            if ia != ir:
                problems.append(f"openapi.json of the alias and of release {RELEASE} disagree beyond their servers")
        elif rel == "llms.txt":
            ta, tr = a.decode("utf-8"), _alias_form(r.decode("utf-8"))
            if ta[ta.index("\n## "):] != tr[tr.index("\n## "):]:
                problems.append(f"llms.txt of the alias and of release {RELEASE} disagree below their headers")
        elif _normal(json.loads(r)) != json.loads(a):
            problems.append(f"{rel} of the alias and of release {RELEASE} differ beyond their addresses")
    return problems


def verify_registry():
    """versions.json against the schema it names, and against a fresh rebuild of it from the trees on disk."""
    import jsonschema
    problems = []
    path = os.path.join(API_ROOT, "versions.json")
    if not os.path.isfile(path):
        return ["versions.json does not exist"]
    text = _read(API_ROOT, "versions.json")
    doc = json.loads(text)
    schema = json.loads(_read(API_ROOT, "schemas/versions.schema.json"))
    for err in jsonschema.Draft202012Validator(schema).iter_errors(doc):
        problems.append(f"versions.json: {'/'.join(str(p) for p in err.absolute_path)}: {err.message[:160]}")
    index = json.loads(_read(API_ROOT, "index.json"))
    if index["versions"]["release"] != RELEASE:
        problems.append(f"the alias holds release {index['versions']['release']}, VERSION is {RELEASE}")
    for v in release_dirs():
        if not R.release_date(v):
            problems.append(f"docs/api/{v}/ is a release tree, but CHANGELOG.md has no dated section for {v}")
    if problems:
        return problems
    try:
        expected = dump(versions_document(index["data_version"]))
    except SystemExit as e:   # an unreleasable state (a tree newer than VERSION): a problem to report, not a crash
        return [str(e)]
    if text != expected:
        problems.append("versions.json is not what the release trees, CHANGELOG.md and LEGACY_RELEASES give; rebuild it")
    return problems


def verify_web():
    """The web copies: each one exists at the size _data/figures.json records, next to its master; the README's figure blocks
    are what the build writes; and no page or README embeds a 1200 dpi master directly."""
    problems = []
    path = os.path.join(DATA_FILES, "figures.json")
    if not os.path.isfile(path):
        return ["docs/_data/figures.json does not exist; run scripts/build_api.py"]
    with io.open(path, encoding="utf-8") as f:
        info = json.load(f)
    for name, rec in info.items():
        web, master = (os.path.join(DOCS, rec[k].lstrip("/")) for k in ("web", "master"))
        if not os.path.isfile(web) or not os.path.isfile(master):
            problems.append(f"{name}: the web copy or the master is missing")
            continue
        if _png_size(web) != (rec["width"], rec["height"]) or os.path.getsize(web) != rec["web_bytes"]:
            problems.append(f"{name}: the web copy is not the size _data/figures.json records")
        if os.path.getsize(master) != rec["master_bytes"] or _png_size(master) != (rec["master_width"], rec["master_height"]):
            problems.append(f"{name}: the master is not the one _data/figures.json describes")
        if rec["width"] > WEB_WIDTH:
            problems.append(f"{name}: the web copy is wider than {WEB_WIDTH} px")
    if set(os.listdir(WEB)) != set(info):
        problems.append("docs/assets/web/ and _data/figures.json list different files")
    with io.open(os.path.join(REPO, "README.md"), encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        if readme_with_figures(text, info) != text:
            problems.append("README.md: a figure block is not what the build writes (sizes, links or labels); run scripts/build_api.py")
    except KeyError as e:
        problems.append(f"README.md: a figure block names {e}, which is not a figure of the site")
    if re.search(r'<img[^>]*src="validation/figures/|!\[[^\]]*\]\(validation/figures/', text):
        problems.append("README.md embeds a 1200 dpi master directly; use a <!--fig ...--> block")
    for path in sorted(glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True)):
        rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
        if rel.startswith("api/"):
            continue
        with io.open(path, encoding="utf-8") as f:
            page = f.read()
        if re.search(r"<img[^>]*src=\"\{\{ '/assets/(figures|geometry)/|\]\(\{\{ '/assets/(figures|geometry)/", page):
            problems.append(f"docs/{rel} embeds a 1200 dpi master directly; show the web copy (the include figure.html)")
    return problems


def verify():
    """Everything a client relies on, checked against the files on disk: the latest alias, every frozen release tree,
    that the alias is the newest release, and the registry that lists them."""
    try:
        import jsonschema  # noqa: F401
        from openapi_spec_validator import validate as validate_openapi  # noqa: F401
    except ImportError as e:  # the contract is not optional
        return [f"{e.name} is not installed: pip install --require-hashes -r requirements.lock"]
    problems = []
    dirs = release_dirs()
    if RELEASE not in dirs:
        return [f"docs/api/{RELEASE}/, the tree of the current release, does not exist; run scripts/build_api.py"]
    for label, root, base, strict in [("alias", API_ROOT, LIVE_BASE, True)] + [
            (f"release {v}", os.path.join(API_ROOT, v), f"{LIVE_BASE}/{v}", v == RELEASE) for v in dirs]:
        problems += [f"[{label}] {p}" for p in verify_tree(root, base, strict)]
    problems += [f"[alias vs release] {p}" for p in verify_alias_matches_release()]
    problems += [f"[registry] {p}" for p in verify_registry()]
    problems += [f"[web copies] {p}" for p in verify_web()]
    if _read(DOCS, "llms.txt") != _read(API_ROOT, "llms.txt"):
        problems.append("docs/llms.txt and docs/api/llms.txt differ")
    return problems


# ----------------------------------------------------------------------------- main

def build_tree():
    """Write the tree selected by use_tree(): the data files, then the JSON documents, then its index. Returns what
    the site's generated pages need."""
    global DATA_VERSION
    # Phase 1: the data files. Their hashes define data_version, which every JSON document carries.
    data = {case: write_data(case) for case in D.CASE_IDS}
    write_archive(data)
    dv = compute_data_version()
    if DATA_VERSION not in (None, dv):
        raise SystemExit(f"the two trees disagree on data_version ({DATA_VERSION} vs {dv})")
    DATA_VERSION = dv
    # Phase 2: the JSON documents and the index of it all.
    percase = {}
    for case in D.CASE_IDS:
        percase[case] = write_case_documents(case, data[case])
        g = data[case]["geometry"]
        print(f"[{TREE}] case {case}: {percase[case]['summ']['rows']} rows from {data[case]['src']}; geometry "
              f"{[(x['configuration'], x['stats']['triangles'], x['stats']['watertight']) for x in g]}; "
              f"{len(percase[case]['results'])} validation result(s)")
    write_cases_index(percase)
    write_geometry_index(data)
    write_validation_summary(percase)
    write_schemas()
    write_openapi()
    write_text("llms.txt", llms_text(percase))
    write_index()
    remove_stale()
    return percase


def build():
    if RELEASE in LEGACY_RELEASES:
        raise SystemExit(f"VERSION {RELEASE} predates the versioned layout and is not regenerated; set VERSION to the next release")
    os.makedirs(API_ROOT, exist_ok=True)
    check_runs_registry()
    copy_assets()
    sync_readme()
    # The frozen copy of this release first, then the latest alias, which is the same files addressed without the release.
    use_tree("release")
    percase = build_tree()
    write_dataset_jsonld(percase)       # the home page describes this release by its frozen addresses
    write_changelog_include()
    build_pages(percase)
    use_tree("latest")
    build_tree()
    with io.open(os.path.join(DOCS, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(_read(API_ROOT, "llms.txt"))
    write_versions(DATA_VERSION)
    print("data_version", DATA_VERSION)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="verify the files on disk; build nothing")
    args = ap.parse_args()
    if not args.check:
        build()
    problems = verify()
    for p in problems:
        print("PROBLEM:", p)
    print("verify:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
