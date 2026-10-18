---
title: "Data"
parent: "Case B — 1:4:4 slab"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case B — 1:4:4 slab: configuration, frame and units, reference data, inflow and known data issues."
---

# Case B: reference data
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
| Building | 1:4:4 (depth : width : height) slab |
| Depth (m) | 0.05 |
| Width (m) | 0.2 |
| Height H (m) | 0.2 |
| Reynolds number Re\_H | 72,000 |
| U\_H (m/s) | 5.133 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane y/H = 0, horizontal z/H = 1/16 |
| Instrument | hot-wire anemometer, split-fibre probe, 100 Hz, 60 s per point |
| Wind tunnel | Niigata Institute of Technology, Kashiwazaki |
| Scale, note | model scale; Eddy3D solves it at 1:100 (H = 20 m) with the tunnel velocities |

## Frame and units

| Property | Definition |
|---|---|
| Origin | building centre on the ground plane |
| x | +x streamwise (the wind at WD = 0 blows toward +x); slab spans x in \[-0.025, 0.025\] |
| y | +y lateral; slab spans y in \[-0.10, 0.10\]; points published on the y \<= 0 half by the tunnel's symmetry convention |
| z | +z up from the ground; roof at z = 0.20 |
| Lateral sign applied | -1 |
| Coordinate scale applied | 0.001 |
| Unit of length | m (model scale; converted from the published millimetres) |
| Unit of velocity | m/s |
| Unit of variance | m^2/s^2 |
| Unit of k | m^2/s^2 |

## Reference data

Source in this repository: `raw/cases/case-b/RS_caseB.csv` (approach flow: `raw/cases/case-b/AF_caseB.csv`).

The cleaned table has **224 rows** over **224 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`.

| Configuration | Points |
|---|---|
| default, WD 0° | 224 |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 15 columns and what each holds</summary>

| Column | Meaning |
|---|---|
| `point_id` | the tunnel's own measurement point number |
| `config` | configuration key: 'default', Case C centre building '0D'/'1D'/'2D', Case E state 'bc' (before) / 'ac' (after construction) |
| `instrument` | 'split\_fibre' (vector components) or 'thermistor' (omnidirectional scalar speed) |
| `wind_direction_deg` | AIJ wind direction in degrees; 0 is the case's reference direction (see frame) |
| `x` | m, case frame |
| `y` | m, case frame |
| `z` | m above ground, case frame |
| `U` | m/s, mean velocity along +x |
| `V` | m/s, mean velocity along +y (sign unified: positive toward +y) |
| `W` | m/s, mean velocity along +z |
| `uu` | m^2/s^2, variance of u |
| `vv` | m^2/s^2, variance of v |
| `ww` | m^2/s^2, variance of w |
| `k` | m^2/s^2, turbulent kinetic energy |
| `campaign` | 'wind\_tunnel' (model scale) or 'field' (a full-scale observation: Cases F, G, M) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | log law, kappa = 0.41, least squares over z = 0.02 ... 2H on the case's own approach-flow file |
| Friction velocity u\* (m/s) | 0.399 |
| Roughness length z₀ (mm) | 0.882 |
| U\_H, measured (m/s) | 5.133 |
| Log-law error at H | +2.9 % |

## Known data issues

Each of these changes the result of a comparison if it is not accounted for.

- The published coordinates are MILLIMETRES (x\[mm\]) while velocities are m/s. The API serves metres (coordinate\_scale\_applied = 0.001). Read as metres, every probe lands 1000x too far out.
- The published lateral velocity V is positive toward -y (V = +3.630 m/s at (-0.025, -0.110, 0.013), just outside the y \< 0 flank where the flow must deflect toward -y). The API multiplies V by -1 (lateral\_sign\_applied = -1) so that V is positive toward +y as in Case A. Scored without this, Case B's V comes out at R = -0.910 against R = +0.959 for U on the same points.
- The RANS solution is symmetric, so model V = 0 on the centre plane while the tunnel measures small non-zero values there.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/B.json`]({{ '/api/cases/B.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/B/points.json`]({{ '/api/cases/B/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/B/points.csv`]({{ '/api/cases/B/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/B/approach_flow.csv`]({{ '/api/cases/B/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/B/geometry.json`]({{ '/api/cases/B/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/B/geometry.stl`]({{ '/api/cases/B/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/B/validation.json`]({{ '/api/cases/B/validation.json' | relative_url }}) |

## Attribution

- Data collectors: Yoshihide Tominaga (Niigata Institute of Technology)
- Editors and distributors: Hideki Kikumoto (The University of Tokyo), Tsubasa Okaze (Institute of Science Tokyo)
- DOI: [10.5281/zenodo.15401455](https://doi.org/10.5281/zenodo.15401455)
- Citation requested: Miyazaki, T., Tominaga, Y. (2003). Wind tunnel experiment on flow field around a building model with a scale ratio of 4:4:1 placed within the surface boundary layer. Proc. Annual Meeting of Hokuriku Chapter, AIJ, 201-204 (in Japanese). <https://www.aij.or.jp/paper/detail.html?productId=313933>
- Licence: CC BY 4.0
