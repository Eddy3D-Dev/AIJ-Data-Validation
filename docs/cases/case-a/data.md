---
title: "Data"
parent: "Case A — 1:1:2 building"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case A — 1:1:2 building: configuration, frame and units, reference data, inflow and known data issues."
---

# Case A: reference data
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Configuration

| Parameter | Value |
|---|---|
| Building | 1:1:2 (width : depth : height) prism |
| Width b (m) | 0.08 |
| Height H (m) | 0.16 |
| Reynolds number Re\_H | 24,000 |
| U\_H (m/s) | 4.491 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane y/b = 0, horizontal z/b = 0.125, horizontal z/b = 1.25 |
| Instrument | hot-wire anemometer, split-fibre probes (DANTEC 55R55 streamwise, 55R57 spanwise/vertical), 1000 Hz, 60 s per point, 500 Hz low-pass |
| Wind tunnel | Technical Research Institute, Shimizu Corporation, Tokyo |
| Scale, note | model scale; Eddy3D solves it at 1:100 (b = 8 m, H = 16 m) with the tunnel velocities |

## Frame and units

| Property | Definition |
|---|---|
| Origin | building centre on the ground plane |
| x | +x streamwise (the wind at WD = 0 blows toward +x); building spans x in \[-0.04, 0.04\] |
| y | +y lateral; building spans y in \[-0.04, 0.04\]; points published on the y \<= 0 half by the tunnel's symmetry convention |
| z | +z up from the ground; roof at z = 0.16 |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |
| Unit of variance | m^2/s^2 |
| Unit of k | m^2/s^2 |

## Reference data

Source in this repository: `raw/cases/case-a/RS-caseA.csv` (approach flow: `raw/cases/case-a/AF_caseA.csv`).

The cleaned table has **186 rows** over **186 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`.

| Configuration | Points |
|---|---|
| default, WD 0° | 186 |

## Inflow

| Property | Value |
|---|---|
| Method | log law, kappa = 0.41, least squares over z = 0.02 ... 2H on the case's own approach-flow file |
| Friction velocity u\* (m/s) | 0.343 |
| Roughness length z₀ (mm) | 0.668 |
| U\_H, measured (m/s) | 4.491 |
| Log-law error at H | +2.0 % |

## Known data issues

Each of these changes the result of a comparison if it is not accounted for.

- Lateral velocity V is positive toward +y (checked: V = -2.893 m/s at (-0.040, -0.050, 0.010), just outside the y \< 0 flank, deflecting away from the centreline). Case B uses the OPPOSITE sign; the API flips Case B so both agree.
- Coordinates are metres (Case B's are millimetres in the published file).
- Case A's turbulence columns are rms values (u\_rms, ...). The API serves VARIANCES (uu = u\_rms^2) so A and B share one column meaning.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/A.json`]({{ '/api/cases/A.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/A/points.json`]({{ '/api/cases/A/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/A/points.csv`]({{ '/api/cases/A/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/A/approach_flow.csv`]({{ '/api/cases/A/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/A/geometry.json`]({{ '/api/cases/A/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/A/geometry.stl`]({{ '/api/cases/A/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/A/validation.json`]({{ '/api/cases/A/validation.json' | relative_url }}) |

## Attribution

- Data collectors: Takeshi Ishihara (The University of Tokyo), Kazuki Hibi (Numerical Flow Design)
- Editors and distributors: Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo), Tsubasa Okaze (Institute of Science Tokyo)
- DOI: [10.5281/zenodo.15050147](https://doi.org/10.5281/zenodo.15050147)
- Citation requested: Meng, Y., & Hibi, K. (1998). Turbulent measurements of the flow field around a high-rise building. Journal of Wind Engineering, JAWE, 76, 55-64. <https://doi.org/10.5359/jawe.1998.76_55>
- Licence: CC BY 4.0
