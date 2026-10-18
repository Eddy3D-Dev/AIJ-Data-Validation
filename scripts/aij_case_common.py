"""Helpers for scripts/aij_case_g.py, aij_case_h.py and aij_case_i.py (Cases G, H, I). Standard library only."""
from __future__ import annotations

import csv
import io
import math
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

EDITORS = ["Yoshihide Tominaga (Niigata Institute of Technology)", "Hideki Kikumoto (The University of Tokyo)", "Tsubasa Okaze (Institute of Science Tokyo)"]


def clean_approach_flow(case: str):
    """(rows, source): the approach flow of a case from the cleaned release, as load_approach_flow returns it.

    Rows carry z and U in the units of the cleaned table, k, and u_rms (the root of uu) where uu exists."""
    rel = f"clean/cases/{case}/approach_flow.csv"
    out = []
    with io.open(os.path.join(REPO, rel), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            d = {"z": float(r["z"]), "U": float(r["U"])}
            if r["k"] != "":
                d["k"] = float(r["k"])
            if r["uu"] != "":
                d["u_rms"] = math.sqrt(float(r["uu"]))
            out.append(d)
    return out, rel
