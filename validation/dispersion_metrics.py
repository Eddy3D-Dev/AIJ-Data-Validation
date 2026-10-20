"""The validation metrics the Eddy3D fixtures write to results.json, in Python, so a score can be recomputed from a pairs file.

A transcription of Eddy3D's MetaFOAM.DispersionMetrics (Chang & Hanna 2004 FB, NMSE, MG, VG, FAC2 and NAD, the VDI 3783-9 hit rate
and Pearson's R), with the field names of its DispersionScore: Count, MeanObserved, MeanPredicted, Fb, Nmse, Nad, Fac2, HitRate, Mg,
Vg, GeometricPairs, R. The three conventions the fixtures score with:

    velocity(o, p)       a signed component: hit rate with D = 0.25 and W = 0.05 (in U_H); FAC2's ratio carries the sign;
                         FB, NMSE and NAD are undefined (None) unless both means are positive (see below)
    turbulence(o, p)     k or an rms: the plain definitions, hit rate by D = 0.25 only
    concentration(o, p)  one detection limit, 1e-3 x the largest observation, for FAC2's both-below rule, the geometric pair's
                         floor and the hit rate's W

FB, NMSE and NAD divide by the means (Chang & Hanna 2004 define them for quantities that are positive, concentrations). For a signed
quantity whose observed and predicted means have opposite signs, or either of which is not positive, they are undefined, and evaluate(signed=True)
returns None for them (the API's `null`) instead of a number that means nothing (Case H W: NMSE -91; Case I V: NMSE -4.5e6). R, FAC2, the hit
rate, the geometric metrics and the counts stay. The Eddy3D fixtures have no such rule and write a number there, so a comparison with their scores
skips what this module leaves undefined (`same(..., fixture=True)`).

`python validation/dispersion_metrics.py` checks `velocity` against the scores in validation/results/case{A,B}_openfoam12_realizableKE.json,
which the fixtures computed from the same pairs (caseA/B_..._pairs.csv); a different formula fails there. (`turbulence` and
`concentration` have no pairs of Cases A and B to be checked on; validation/plot_cases_hi_openfoam.py checks them against the Case H and I
fixtures when the Eddy3D results are available.)
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
from math import fsum

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D_HIT, W_VELOCITY, DETECTION_FRACTION = 0.25, 0.05, 1e-3


def evaluate(obs, pred, d=D_HIT, w=0.0, threshold=0.0, signed=False):
    """DispersionMetrics.Evaluate on the pairs where both values are finite (observed = the measurement).

    signed=True: FB, NMSE and NAD are None unless the observed and the predicted mean are both positive."""
    o, p = np.asarray(obs, float), np.asarray(pred, float)
    ok = np.isfinite(o) & np.isfinite(p)
    o, p = o[ok], p[ok]
    n = len(o)
    # Every reduction is an exact math.fsum: NumPy's pairwise SIMD sum rounds differently per CPU width, and the last
    # digit of a geometric mean once flapped between two CI runners on the same inputs (2026-10-20), which the
    # byte-exact verify can never settle.
    mo, mp = fsum(o) / n, fsum(p) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = p / o
    both_below = (np.abs(o) <= threshold) & (np.abs(p) <= threshold)
    fac2 = both_below | ((o != 0) & (ratio >= 0.5) & (ratio <= 2.0))
    diff = np.abs(p - o)
    with np.errstate(divide="ignore", invalid="ignore"):
        hit = (diff <= w) | ((o != 0) & (diff / np.abs(o) <= d))
    lo = np.maximum(o, threshold) if threshold > 0 else o
    lp = np.maximum(p, threshold) if threshold > 0 else p
    both = (lo > 0) & (lp > 0)
    lg = np.log(lo[both]) - np.log(lp[both])
    sxx, syy = fsum((o - mo) ** 2), fsum((p - mp) ** 2)
    undefined = signed and not (mo > 0 and mp > 0)
    return {
        "Count": int(n), "MeanObserved": mo, "MeanPredicted": mp,
        "Fb": None if undefined else 0.0 if mo + mp == 0 else (mo - mp) / (0.5 * (mo + mp)),
        "Nmse": None if undefined or mo * mp == 0 else fsum((o - p) ** 2) / n / (mo * mp),
        "Nad": None if undefined else 0.0 if mo + mp == 0 else fsum(diff) / n / (mo + mp),
        "Fac2": float(fac2.sum() / n), "HitRate": float(hit.sum() / n),
        "Mg": math.exp(fsum(lg) / len(lg)) if both.any() else None,
        "Vg": math.exp(fsum(lg ** 2) / len(lg)) if both.any() else None,
        "GeometricPairs": int(both.sum()),
        "R": None if sxx == 0 or syy == 0 else fsum((o - mo) * (p - mp)) / math.sqrt(sxx * syy),
    }


def velocity(obs, pred):
    return evaluate(obs, pred, D_HIT, W_VELOCITY, signed=True)


def turbulence(obs, pred):
    return evaluate(obs, pred)


def concentration(obs, pred):
    o = np.asarray(obs, float)
    p = np.asarray(pred, float)
    ok = np.isfinite(o) & np.isfinite(p)
    limit = max(0.0, DETECTION_FRACTION * float(o[ok].max()))
    return evaluate(o, p, D_HIT, limit, limit)


def read_pairs(path):
    """[{column: float, ...}] with NaN for empty cells; text columns stay text."""
    with io.open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        d = {}
        for k, v in r.items():
            try:
                d[k] = float(v) if v != "" else math.nan
            except ValueError:
                d[k] = v
        out.append(d)
    return out


def same(a, b, tol=1e-9, fixture=False):
    """True when two scores agree (None, 'NaN' and NaN are the same 'undefined').

    fixture=True: `b` is a fixture's score, which has a number where `a` leaves FB, NMSE or NAD undefined; those are not compared."""
    def num(v):
        return None if v is None or v == "NaN" or (isinstance(v, float) and math.isnan(v)) else float(v)
    for k, v in b.items():
        if fixture and k in ("Fb", "Nmse", "Nad") and a[k] is None:
            continue
        x, y = num(a[k]), num(v)
        if (x is None) != (y is None) or (x is not None and abs(x - y) > tol * max(1.0, abs(y))):
            return False
    return True


def _selfcheck():
    for case in ("A", "B"):
        with io.open(os.path.join(HERE, "results", f"case{case}_openfoam12_realizableKE.json"), encoding="utf-8") as f:
            ref = json.load(f)
        pairs = read_pairs(os.path.join(HERE, "results", f"case{case}_openfoam12_realizableKE_pairs.csv"))
        for q, key in (("U", "velocity.U"), ("V", "velocity.V"), ("W", "velocity.W")):
            m = velocity([r[f"{q}_meas"] for r in pairs], [r[f"{q}_model"] for r in pairs])
            assert same(m, ref[key], fixture=True), (case, key, m, ref[key])
    print("dispersion_metrics: velocity() matches the fixtures' scores for Cases A and B (U, V, W), FB/NMSE/NAD where it defines them")


if __name__ == "__main__":
    _selfcheck()
