"""Helpers shared by clean/case_j.py, case_k.py and case_l.py (the TPU non-isothermal / cube-array cases).

Nothing here knows a case; the cases pass their numbers in. Standard library + numpy only.
"""
from __future__ import annotations

import math
import re
import zipfile
import xml.etree.ElementTree as ET

import numpy as np

_M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _col(ref: str) -> int:
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path: str) -> dict[str, list[list]]:
    """{sheet name: grid of cells} of an .xlsx workbook (None = empty cell, float, str, bool).

    The workbooks of Cases F-M are OOXML, which xlrd 2 cannot open and openpyxl is not in the pinned environment;
    the format is a zip of XML, read here with the standard library. Sheet order is the workbook's own.
    """
    z = zipfile.ZipFile(path)
    sst = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            sst.append("".join(t.text or "" for t in si.iter(_M + "t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in wb.find(_M + "sheets"):
        target = rels[s.get(_R + "id")]
        data = z.read("xl/" + target.lstrip("/").replace("xl/", ""))
        rows: dict[int, dict[int, object]] = {}
        for row in ET.fromstring(data).iter(_M + "row"):
            r = int(row.get("r")) - 1
            for c in row.iter(_M + "c"):
                v, ty = c.find(_M + "v"), c.get("t")
                if ty == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(_M + "t"))
                elif v is None:
                    continue
                elif ty == "s":
                    val = sst[int(v.text)]
                elif ty in ("str", "e"):
                    val = v.text
                elif ty == "b":
                    val = bool(int(v.text))
                else:
                    val = float(v.text)
                rows.setdefault(r, {})[_col(c.get("r"))] = val
        nr = max(rows) + 1 if rows else 0
        nc = max(max(d) for d in rows.values()) + 1 if rows else 0
        out[s.get("name")] = [[rows.get(i, {}).get(j) for j in range(nc)] for i in range(nr)]
    return out


def labelled_constants(grid, label_col: int, value_col: int) -> dict[str, float]:
    """{stripped label: float} for every row whose label cell is text and whose value cell is a number."""
    out = {}
    for r in grid:
        if len(r) > max(label_col, value_col) and isinstance(r[label_col], str) and isinstance(r[value_col], float):
            out[r[label_col].replace("　", " ").strip()] = r[value_col]
    return out


def cube_boxes(n_rows: int, n_cols: int, x_first: float, y_first: float, size: float, pitch: float):
    """Axis-aligned cube footprints on a regular grid: rows run along +x, columns along +y; z from 0 to `size`."""
    boxes = []
    for i in range(n_rows):
        for j in range(n_cols):
            x0, y0 = x_first + pitch * i, y_first + pitch * j
            boxes.append({"min": [round(x0, 9), round(y0, 9), 0.0], "max": [round(x0 + size, 9), round(y0 + size, 9), round(size, 9)]})
    return boxes


def inside_count(df, boxes, shift=(0.0, 0.0, 0.0)) -> int:
    """Points strictly inside any box, after an optional shift (the negative control of every geometry check)."""
    xyz = np.column_stack([df.x.to_numpy() + shift[0], df.y.to_numpy() + shift[1], df.z.to_numpy() + shift[2]])
    inside = np.zeros(len(xyz), bool)
    for b in boxes:
        lo, hi = np.array(b["min"]), np.array(b["max"])
        inside |= np.all((xyz > lo + 1e-9) & (xyz < hi - 1e-9), axis=1)
    return int(inside.sum())


def rounded_match(published, workbook, decimals: int, scale: float = 1.0, offset: float = 0.0, pre_round: int | None = None):
    """Largest |published - round(round(workbook, pre_round) * scale + offset, decimals)| and the number of cells that differ.

    pre_round=None means the published value is the workbook value rounded once to `decimals`.
    """
    w = np.asarray(workbook, float)
    if pre_round is not None:
        w = np.round(w, pre_round)
    v = np.round(w * scale + offset, decimals)
    d = np.abs(v - np.asarray(published, float))
    return float(d.max()), int((d > 1e-9).sum())


def within_half_unit(published, workbook, decimals: int):
    """(largest |published - workbook|, number of cells further than half a unit of the last printed digit).

    The published value is the workbook value rounded to `decimals`; a half-way cell may round either way
    (Excel rounds half up, the binary double may sit just below), so half a unit is the honest bar.
    """
    d = np.abs(np.asarray(published, float) - np.asarray(workbook, float))
    return float(d.max()), int((d > 0.5 * 10.0 ** -decimals * (1 + 1e-6)).sum())


def trapezoid(y, x) -> float:
    y, x = np.asarray(y, float), np.asarray(x, float)
    return float(np.sum((y[1:] + y[:-1]) * np.diff(x)) / 2.0)


def stats(values) -> dict:
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    return {"n": int(len(v)), "min": float(v.min()), "median": float(np.median(v)), "p95": float(np.percentile(v, 95)), "max": float(v.max())}


def sig(v, digits: int = 9):
    """Round every float inside a structure to `digits` significant digits.

    The release is rebuilt on arm64 and amd64 and must come out byte for byte the same: sums, means and
    transcendental functions differ in their last bits between them, nine significant digits do not.
    """
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (float, np.floating)):
        x = float(v)
        return x if (x == 0.0 or not math.isfinite(x)) else float(f"{x:.{digits}g}")
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, dict):
        return {k: sig(x, digits) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [sig(x, digits) for x in v]
    if isinstance(v, np.ndarray):
        return [sig(x, digits) for x in v.tolist()]
    return v


def check(B, case, name, ok, **measured):
    """B.check with every measured number rounded to 9 significant digits (see sig)."""
    return B.check(case, name, ok, **sig(measured))


def tidy(df, digits: int = 10, skip=("point_id",)):
    """Round every float column of a points table to `digits` significant digits.

    clean/build.py writes the CSV with %.10g and the Parquet with the double itself; rounding here makes the two (and the
    --check comparison between them) identical, and removes the last-bit noise of the products and sums behind each value.
    """
    df = df.copy()
    for col in df.columns:
        if col in skip or df[col].dtype.kind != "f":
            continue
        df[col] = [v if not math.isfinite(v) else float(f"{v:.{digits}g}") for v in df[col]]
    return df
