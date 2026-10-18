---
title: "Examples"
parent: API
nav_order: 1
description: "curl and Python examples for the AIJ UWE benchmark API, and the geometry conventions."
permalink: /api-reference/examples/
---

# Examples

The endpoints are described on the [API]({{ '/api-reference/' | relative_url }}) page.

## curl

```bash
BASE=https://eddy3d-dev.github.io/AIJ-Data-Validation/api   # newest release; append /3.1.0 to pin

curl -s $BASE/index.json | jq '.versions, (.endpoints[].path)'
curl -s $BASE/cases.json | jq '.cases[] | {id, title, counts, engines}'
curl -s $BASE/cases/B.json | jq '{frame, units, known_issues}'
curl -s $BASE/validation.json | jq '.cases[] | {case, engines: [.engines[] | {engine, status}]}'

# Downloads: take the URL from the document, then check the SHA-256.
url=$(curl -s $BASE/cases/B.json | jq -r '.points.csv.url')
sha=$(curl -s $BASE/cases/B.json | jq -r '.points.csv.sha256')
curl -s -o caseB.csv "$url" && echo "$sha  caseB.csv" | sha256sum -c -

curl -s $BASE/cases/D/geometry.json | jq '.files[0].boxes | length'      # 83
curl -s $BASE/cases/C/validation.json | jq '.results[] | {run_id, headline}'
curl -s -o aij_geometry.zip "$(curl -s $BASE/geometry.json | jq -r '.archive.url')"
```

## Python

Standard library only. This script runs as written against the live API.

```python
import csv, hashlib, io, json, statistics, urllib.request

# The newest release. To pin the analysis to one release, append its number (any in /api/versions.json): ".../api/3.1.0".
BASE = "https://eddy3d-dev.github.io/AIJ-Data-Validation/api"


def fetch(url):
    # A descriptive User-Agent: the site's CDN rejects urllib's default one (see Clients on the API page).
    req = urllib.request.Request(url, headers={"User-Agent": "aij-uwe-example/1.0"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def get_json(path):
    return json.loads(fetch(f"{BASE}/{path}"))


def download(d):
    """Fetch a download object and check it arrived intact."""
    body = fetch(d["url"])
    assert hashlib.sha256(body).hexdigest() == d["sha256"], f"{d['path']} is corrupt or stale"
    return body


index = get_json("index.json")
print(index["versions"])                              # API version, data version (a SHA-256 of the data)

case = get_json("cases/B.json")
print(case["frame"]["x"])                             # read the frame and the known issues BEFORE the numbers
print(case["known_issues"][0][:80])

pts = get_json("cases/B/points.json")
U_H = case["configuration"]["U_H_m_s"]
centre = [p for p in pts["points"] if abs(p["y"]) < 1e-9 and p["U"] is not None]
print(len(centre), "centre-plane points; U/U_H at the first:", round(centre[0]["U"] / U_H, 3))

rows = list(csv.DictReader(io.StringIO(download(case["points"]["csv"]).decode())))
print(len(rows), "rows in points.csv; columns", list(rows[0]))

geom = get_json("cases/D/geometry.json")
print(len(geom["files"][0]["boxes"]), "boxes in Case D")       # boxes where the geometry is boxes: no STL parsing
stl = download(geom["files"][0])                                # ...or the STL itself, checked against its SHA-256

summary = get_json("validation.json")                           # every case and engine in one table
for c in summary["cases"]:
    print(c["case"], {e["engine"]: e["status"] for e in c["engines"]})

# Recompute a published score from the per-point pairs behind it.
val = get_json("cases/A/validation.json")
run = next(r for r in val["results"] if r["run_id"] == "A.openfoam12-realizableKE")
pairs = list(csv.DictReader(io.StringIO(download(run["pairs"]).decode())))
R = statistics.correlation([float(p["U_meas"]) for p in pairs], [float(p["U_model"]) for p in pairs])
print("R of U/U_H recomputed:", round(R, 4), "published:", round(run["scores"]["velocity.U"]["R"], 4))
```

The last line prints `R of U/U_H recomputed: 0.9548 published: 0.9548`.

## Geometry conventions

- Metres. A–D and H–L are model scale, the scale the tunnel measured at. E, F, G and M are full scale: E at the scale
  of its 3dm and workbook, F and M (measured at 1:800 and 1:600) scaled up, G a field observation. `units` in
  `geometry.json` states which.
- The origin is a point of each case's own: the building centre (A, B), the array centre (C, D), the centre of the
  reproduced area (E, F), the leeward face of the belt (G) or of the building (H, J), the cube's centre (I), a cube of
  the array (K, L) or the turntable's centre (M). `frame.origin` in the case document names it. In F and M the
  heights are above the tunnel floor, not the ground.
- +x runs along the wind at WD = 0 for A–D and H–L, and downwind for G. E and F keep their geographic frame (+x east,
  +y north), and their directions are meteorological: the direction the wind comes **from**, N = 0°, clockwise.
  M's frame is +x north, +y west.
- Outward normals, LF line endings, one `solid` per file. Every file is watertight: each body is closed, consistently
  wound and positive in volume. Where two bodies touch along an edge (11 edges in E) the edge counts as a `body_contacts`
  entry in `geometry.json`. F and M are one body each, closed with a 1 m base slab below z = 0.
- The build checks every STL: triangle count, bodies, boundary edges, winding, signed volume, and the bounding box against the stated
  dimensions; `scripts/check_geometry.py` parses the written files again and fails on any open or inconsistently wound body. `validation/render_geometry.py` draws each one from the same code that writes it, and those are the
  renders on the case pages.
