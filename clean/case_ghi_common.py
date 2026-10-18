"""Helpers shared by clean/case_g.py, case_h.py and case_i.py. Standard library plus pandas only.

Cases H and I publish their legacy workbooks as .xlsx (Office Open XML). The pinned environment reads the
older .xls workbooks with xlrd 2.x, which cannot open .xlsx, and adds no second spreadsheet package for two
files, so `read_xlsx` parses the zip directly: the values of the cells (formula cells: their cached value), by
sheet name, which is all these cleaners need.
"""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def _col(ref: str) -> int:
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path: str) -> dict[str, dict[tuple[int, int], object]]:
    """{sheet name: {(row, col): value}}, 0-based; numbers as float, text as str; empty cells are absent."""
    z = zipfile.ZipFile(path)
    sst = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
            sst.append("".join(t.text or "" for t in si.iter("{%s}t" % _NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in wb.find("m:sheets", _NS):
        target = rels[s.get("{%s}id" % _NS["r"])].lstrip("/")
        part = target if target.startswith("xl/") else "xl/" + target
        cells = {}
        for c in ET.fromstring(z.read(part)).iter("{%s}c" % _NS["m"]):
            v, t = c.find("m:v", _NS), c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % _NS["m"]))
            elif v is None or v.text is None:
                continue
            elif t == "s":
                val = sst[int(v.text)]
            elif t in ("str", "e"):
                val = v.text
            elif t == "b":
                val = bool(int(v.text))
            else:
                val = float(v.text)
            ref = c.get("r")
            cells[(int(re.search(r"\d+", ref).group(0)) - 1, _col(ref))] = val
        out[s.get("name")] = cells
    return out


def sheet_rows(cells, first: int = 0, ncols: int | None = None):
    """[(row index, [values])] for the non-empty rows from `first` on; missing cells are ''."""
    if not cells:
        return []
    nc = max(c for _, c in cells) + 1 if ncols is None else ncols
    nr = max(r for r, _ in cells)
    out = []
    for r in range(first, nr + 1):
        vals = [cells.get((r, c), "") for c in range(nc)]
        if any(v != "" for v in vals):
            out.append((r, vals))
    return out


def number(v) -> float:
    """float for a numeric workbook cell, NaN for '', ' ', '-' and text."""
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else math.nan


def directions_table(case: str, pts: pd.DataFrame, quantity: dict[str, list[str]], flow) -> pd.DataFrame:
    """directions.csv rows for a case built outside build.directions_for.

    `quantity[instrument]` lists the columns whose presence makes a row 'measured'; `flow(config, instrument, wd)`
    returns (flow_dir_x, flow_dir_y, sense_basis, status)."""
    rows = []
    for (cfg, inst, wd, wname), g in pts.groupby(["config", "instrument", "wind_direction_deg", "wind_direction"], sort=True):
        fx, fy, basis, status = flow(cfg, inst, wd)
        rows.append({"case_id": case, "config": cfg, "instrument": inst, "wind_direction_deg": wd, "wind_direction": wname,
                     "flow_dir_x": round(fx, 9) + 0.0, "flow_dir_y": round(fy, 9) + 0.0, "rows": int(len(g)),
                     "measured": int(g[quantity[inst]].notna().any(axis=1).sum()), "sense_basis": basis, "status": status})
    return pd.DataFrame(rows)
