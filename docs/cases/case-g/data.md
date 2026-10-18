---
title: "Data"
parent: "Case G — flow behind a tree belt"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case G — flow behind a tree belt: configuration, frame and units, reference data, inflow and known data issues."
---

# Case G: reference data
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
| belt | Tsuiji-matsu (Japanese black pine), trimmed to a rectangle; 74 m long (y), 2 m deep (x), 7 m tall, 1.2 m bottom gap; shading rate 81 % after pruning (data paper section 3.7) |
| Height H (m) | 7.0 |
| Depth (m) | 2.0 |
| Width (m) | 74.0 |
| gap m | 1.2 |
| Campaign | field (full scale) |
| location | Taisha-machi, Hikawa-gun, Shimane, Japan; west end of an elementary-school playground |
| Wind directions (°) | 0 |
| measurement lines | 0.25 H, 0.5 H, 1 H, 2 H, 3 H, 4 H, 5 H behind the belt = x 1.75, 3.5, 7, 14, 21, 28, 35 m (H = 7 m) |
| measurement heights m | 1.5, 3.0, 4.5, 6.0 |
| Points | 28 |
| Instrument | 3-D ultrasonic anemometers (KAIJO DA-600 with TR-90Tx) at four heights on a movable tower, 5 Hz, 10 min or more per line (26 Dec 2000); approach flow 120 min (28 Dec 2000) at 1.5, 3, 6, 9 m |
| Normalisation | velocity\_ratio = U/UH and k\_ratio = k/UH^2, UH = the mean wind speed at 7 m during each measurement period (interpolated with the approach flow\'s power law, index 0.22); nothing is published in m/s |
| approach flow normalisation | AF\_caseG.csv is U/Ub and k/Ub^2 with Ub = U at 9 m; divide by UH/Ub = 0.946 (power law 0.22) for the table\'s normalisation |
| Scale, note | full scale: a field observation, there is no model |

## Frame and units

| Property | Definition |
|---|---|
| Origin | the leeward face of the tree belt at ground level, on the vertical section through the belt\'s centre |
| x | +x downwind: the belt occupies x in \[-2, 0\] m, the measurement lines lie behind it at x = 1.75 ... 35 m |
| y | +y along the belt (y in \[-37, 37\] m); every point is on y = 0 |
| z | +z up; the belt spans z in \[1.2, 7\] m; points at z = 1.5, 3, 4.5, 6 m |
| Wind direction convention | one direction, toward +x (perpendicular to the belt); the field wind\'s angle to the belt normal is not published |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (full scale) |
| Unit of velocity ratio | dimensionless, U/UH |
| Unit of k ratio | dimensionless, k/UH^2 |

## Reference data

Source in this repository: `raw/cases/case-g/RS_caseG.csv` (approach flow: `raw/cases/case-g/AF_caseG.csv`).

The cleaned table has **28 rows** over **28 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `velocity_ratio`, `campaign`, `k_ratio`.

| Configuration | Points |
|---|---|
| default, field, sonic anemometer, WD 0° | 28 |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 10 columns and what each holds</summary>

| Column | Meaning |
|---|---|
| `point_id` | the tunnel\'s own measurement point number |
| `config` | configuration key: \'default\', Case C centre building \'0D\'/\'1D\'/\'2D\', Case E state \'bc\' (before) / \'ac\' (after construction) |
| `instrument` | \'split\_fibre\' (vector components) or \'thermistor\' (omnidirectional scalar speed) |
| `wind_direction_deg` | AIJ wind direction in degrees; 0 is the case\'s reference direction (see frame) |
| `x` | m, case frame |
| `y` | m, case frame |
| `z` | m above ground, case frame |
| `velocity_ratio` | dimensionless, mean speed over the case\'s reference speed (Case E: Vs / U(15.9 m), U(15.9 m) = 3.935 m/s; see the case\'s normalisation) |
| `campaign` | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |
| `k_ratio` | k / U\_ref^2 where the dataset publishes only normalised values (Case G; U\_ref = U at the tree height) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | power law on the four published heights (1.5, 3, 6, 9 m) of U/Ub; the readme states the index 0.22 |
| power law index fitted | 0.2073 |
| power law index stated | 0.22 |
| UH over Ub power law 0.22 | 0.9462 |
| UH over Ub log interpolation | 0.938 |
| Note | derived during cleaning, not published as a fit; the profile carries 2 decimals, so the fitted index is good to about +/-0.01 |

## Known data issues

Each of these changes the result of a comparison if it is not accounted for.

- FIELD data: full-scale metres, no model, and nothing in m/s. The table carries U/UH (velocity\_ratio) and k/UH^2 (k\_ratio), UH = the mean speed at 7 m during each period; the approach-flow table carries U/Ub and k/Ub^2 (Ub = U at 9 m) in its U and k columns, which are dimensionless here.
- The readme lists the heights of the lee measurement as 1.5, 3.0, 6.0, 9.0 m; the table, the workbook, the drawing and the data paper have 1.5, 3, 4.5, 6 m.
- The tree belt is a POROUS canopy (shading rate 81 % after pruning), not a solid body: the served geometry is its 2 m × 74 m × 7 m envelope with the 1.2 m gap, and a solver needs a canopy (drag) model, not a wall.
- The approach profile (28 Dec 2000, 120 min) and the lee measurements (26 Dec 2000, 10 min or more) are from different days. Behind the belt k/UH^2 is 0.040-0.072 at 5 H, 3-8 times below the approach flow\'s 0.26-0.31 at the same heights; the files do not say why.
- Only 28 numbers per quantity exist, on one centre section, one time-average each, with no repeats and no uncertainty.
- The wind direction relative to the belt normal during the measurement is not published; the case is two-dimensional by assumption.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/G.json`]({{ '/api/cases/G.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/G/points.json`]({{ '/api/cases/G/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/G/points.csv`]({{ '/api/cases/G/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/G/approach_flow.csv`]({{ '/api/cases/G/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/G/geometry.json`]({{ '/api/cases/G/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/G/geometry.stl`]({{ '/api/cases/G/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/G/validation.json`]({{ '/api/cases/G/validation.json' | relative_url }}) |

## Attribution

- Data collectors: Yasuo Kurotani (Shimane University), Nobuyoshi Kiyota (Hiroshima Institute of Technology)
- Editors and distributors: Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo), Tsubasa Okaze (Institute of Science Tokyo)
- DOI: [10.5281/zenodo.15589666](https://doi.org/10.5281/zenodo.15589666)
- Citation requested: Kurotani, Y., Kiyota, N., Kobayashi, S. (2001). Windbreak effect of Tsuijimatsu in Izumo Part. 2. Summaries of technical papers of Annual Meeting, Architectural Institute of Japan, D-2 Environmental engineering II, 745-746 (in Japanese).
- Licence: CC BY 4.0
