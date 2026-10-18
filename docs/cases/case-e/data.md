---
title: "Data"
parent: "Case E — Niigata district"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case E — Niigata district: configuration, frame and units, reference data, inflow and known data issues."
---

# Case E: reference data
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
| District | Niigata City urban area near the Shinano River; dense low-rise stock (median top 6 m, max 30 m) |
| Scale | 1:250 |
| States | **bc**: before construction (sites of A, B, C empty)<br>**ac**: after construction of A (60 m high-rise), B and C (18 m mid-rises) |
| New buildings | **A**: 60 m high-rise, bbox x \[-79.3, -49.1\], y \[-17.1, 18.3\]<br>**B**: 18 m, bbox x \[41.5, 61.0\], y \[-18.5, 8.5\]<br>**C**: 18 m, bbox x \[64.0, 83.5\], y \[-8.0, 19.0\] |
| Wind directions | N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW |
| Wind directions (°) | 0.0, 22.5, 45.0, 67.5, 90.0, 112.5, 135.0, 157.5, 180.0, 202.5, 225.0, 247.5, 270.0, 292.5, 315.0, 337.5 |
| Measurement height (m) | 2.0 |
| Measurement height, note | 2 m full scale = 0.008 m model scale |
| Points | 80 |
| Values | 2560 |
| Reynolds number | 17,000 |
| Normalisation | velocity ratio = mean scalar speed at 2 m / inflow velocity at 15.9 m (the Niigata meteorological station height); U(15.9 m) = 0.504531 x UR = 3.935 m/s with UR = 7.8 m/s at ZR = 250 m |
| Instrument | thermistor anemometer, 100 Hz, 60 s per point, mean scalar wind speed |
| Wind tunnel | Niigata Institute of Technology, Kashiwazaki |

## Frame and units

| Property | Definition |
|---|---|
| Origin | centre of the reproduced area, ground plane |
| x | +x EAST (full-scale metres) |
| y | +y NORTH (compass rose in MP\_caseE.png) |
| z | +z up; all points at z = 2.0 |
| Wind direction convention | Meteorological: the compass name is the direction the wind comes FROM (N = 0 deg blows toward -y, E = 90 deg toward -x), clockwise from north. This case keeps its geographic frame instead of \'+x along the wind\' |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (FULL scale) |
| Unit of velocity ratio | dimensionless |

<details markdown="block">
<summary>Data notes: Wind direction convention</summary>

The district is real and its coordinates are the data\'s.

</details>

## Reference data

Source in this repository: `raw/cases/case-e/LF_caseE.xls` (approach flow: `raw/cases/case-e/LF_caseE.xls [sheet Inflow]`).

The cleaned table has **2,560 rows** over **80 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction`, `wind_direction_deg`, `x`, `y`, `z`, `velocity_ratio`, `campaign`.

| Configuration | Points |
|---|---|
| before construction, 16 wind directions | 80 per direction |
| after construction, 16 wind directions | 80 per direction |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 10 columns and what each holds</summary>

| Column | Meaning |
|---|---|
| `point_id` | the tunnel\'s own measurement point number |
| `config` | configuration key: \'default\', Case C centre building \'0D\'/\'1D\'/\'2D\', Case E state \'bc\' (before) / \'ac\' (after construction) |
| `instrument` | \'split\_fibre\' (vector components) or \'thermistor\' (omnidirectional scalar speed) |
| `wind_direction` | compass name of the direction the wind comes FROM (Case E) |
| `wind_direction_deg` | AIJ wind direction in degrees; 0 is the case\'s reference direction (see frame) |
| `x` | m, case frame |
| `y` | m, case frame |
| `z` | m above ground, case frame |
| `velocity_ratio` | dimensionless, mean speed over the case\'s reference speed (Case E: Vs / U(15.9 m), U(15.9 m) = 3.935 m/s; see the case\'s normalisation) |
| `campaign` | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | the workbook publishes z/ZR, U/UR, k/UR^2 with ZR = 250 m, UR = 7.8 m/s and epsilon = Cmu^0.5 k dU/dz (Cmu = 0.09); de-normalised to full-scale metres and m/s here |
| U\_ref at 15.9 m (m/s) | 3.935 |
| Log law | does not fit: kappa = 0.41 fits reach 5.3-9.4 % max error over the relevant height range and overshoot U(15.9 m) by 4-7 % |
| Power-law exponent | **ground to 60m**: 0.158<br>**whole profile**: 0.201 |
| Note | derived during scoping, not published by AIJ |

## Known data issues

- The velocity ratio is normalised by the inflow velocity at 15.9 m (= 3.935 m/s), NOT by U\_H and NOT by UR = 7.8 m/s.
- All 2560 published ratios are integer multiples of 0.0198204 (55 distinct levels): the data\'s own resolution is +/-0.0099, 3.1 % of the median value and about 10 % at the lowest points.
- The readme describes AF\_caseE.csv, RS\_caseE.csv and BD\_caseE.stl, but this repository holds only the .3dm, .ghx, .xls and the MP drawing; everything here is extracted from the workbook and the 3dm.
- case-e.3dm is FULL-SCALE metres (MP\_caseE.png is drawn at model scale, +/-0.8 m). Use layers \'buildings\' (5,015 meshes, before construction) and \'buildings\_new\_construction\' (3 prisms); exclude the map plate on the Japanese-named general layer, the terrain plates (the site is flat) and \'probes\'.
- Do not take the measurement coordinates from the 3dm\'s \'probes\' layer: its 80 spheres sit a median 2.31 m (max 21 m) from the workbook\'s points, which are authoritative (all 80 fall in open space, min 0.83 m from a building edge).
- The measured quantity is a scalar (thermistor) speed. The construction signal (ac - bc) is largest for SW (mean |d| 0.2155) and smallest for SSE (0.093).

<details markdown="block">
<summary>Data notes: Prior comparison</summary>

A prior Eddy3D comparison in the folder divided by the wrong reference and came out low by a factor of 2.048 (FAC2 0.338 -\> 0.863 once rescaled, R unchanged at 0.661).

</details>

<details markdown="block">
<summary>Interpretation: Scalar speed</summary>

A RANS |U| is biased low against the thermistor speed in a dense canopy.

</details>

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/E.json`]({{ '/api/cases/E.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/E/points.json`]({{ '/api/cases/E/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/E/points.csv`]({{ '/api/cases/E/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/E/approach_flow.csv`]({{ '/api/cases/E/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/E/geometry.json`]({{ '/api/cases/E/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/E/geometry.stl`]({{ '/api/cases/E/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/E/validation.json`]({{ '/api/cases/E/validation.json' | relative_url }}) |

## Attribution

- Data collectors: Yoshihide Tominaga (Niigata Institute of Technology)
- Editors and distributors: Hideki Kikumoto (The University of Tokyo), Tsubasa Okaze (Institute of Science Tokyo)
- DOI: [10.5281/zenodo.15429017](https://doi.org/10.5281/zenodo.15429017)
- Citation requested: Tominaga, Y. et al. (2008). AIJ guidelines for practical applications of CFD to pedestrian wind environment around buildings. JWEIA 96, 1749-1761. <https://doi.org/10.1016/j.jweia.2008.02.058>
- Licence: CC BY 4.0
