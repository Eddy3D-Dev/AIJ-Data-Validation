---
title: "Data"
parent: "Case K — 9 x 9 cube array, point source"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case K — 9 x 9 cube array, point source: configuration, frame and units, reference data, inflow and known data issues."
---

# Case K: reference data
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
| Array | 9 rows (along x) by 9 columns (across y) of cubes, H = 0.06 m, pitch 0.12 m (street width = H, plan area ratio 25 %); the pitch is read from the MP drawings |
| Height H (m) | 0.06 |
| pitch m | 0.12 |
| cubes | 81 |
| Reynolds number Re\_H | 9800 |
| U\_H (m/s) | 2.33 |
| U\_H, note | stated by the readme and data paper; the approach-flow file (Case H\'s) gives 2.24 m/s at z = 0.06 m |
| Wind directions (°) | 0 |
| Measurement planes | y/H = 0, +-1, +-2, +-3 (z up to 0.07 m), five heights from 4 mm to 70 mm; the three upper heights only on y = 0 and +-H |
| Points | 203 |
| source | 5 mm floor outlet at (-0.15, 0, 0), between rows 2 and 3 on the centre line; 100 % ethylene, 3.6e-6 m3/s |
| concentration normalisation | c0 = q / (U\_H H^2) = 429.18 ppm with the cube\'s H and U\_H; the legacy workbook uses H = 0.2 m and UH = 4.94 m/s instead (C0 = 18.218 ppm), see known issues |
| Instrument | split-fibre hot wire (velocity), high-speed hydrocarbon analyser (concentration), 1000 Hz with a 200 Hz low-pass filter, 60 s per point |
| Wind tunnel | Eiffel-type wind tunnel, Tokyo Polytechnic University (Atsugi); 1.2 m wide, 1.0 m high |
| Scale, note | model scale; the sources state no model:full scale ratio |

## Frame and units

| Property | Definition |
|---|---|
| Origin | bottom centre of the windward wall of the 4th row of the central column: x = 0 is that wall, y = 0 the centre line of the central column |
| x | +x streamwise (the wind blows toward +x); row k spans x in \[0.12 (k-4), 0.12 (k-4) + 0.06\], so the array spans x in \[-0.36, 0.66\] |
| y | +y lateral; column centres at y = 0, +-0.12, ... +-0.48 (the array spans y in \[-0.51, 0.51\]) |
| z | +z up; cube tops at z = 0.06 |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |
| Unit of variance | m^2/s^2 |
| Unit of k | m^2/s^2 |
| Unit of concentration | ppm of the released ethylene |

## Reference data

Source in this repository: `raw/cases/case-k/RS_caseK.csv` (approach flow: `raw/cases/case-k/AF_caseK.csv`).

The cleaned table has **203 rows** over **203 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`, `C`, `c_rms`, `concentration_ratio`.

| Configuration | Points |
|---|---|
| default, wind tunnel, split fibre, WD 0° | 203 |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 18 columns and what each holds</summary>

| Column | Meaning |
|---|---|
| `point_id` | the tunnel\'s own measurement point number |
| `config` | configuration key: \'default\', Case C centre building \'0D\'/\'1D\'/\'2D\', Case E state \'bc\' (before) / \'ac\' (after construction) |
| `instrument` | \'split\_fibre\' (vector components) or \'thermistor\' (omnidirectional scalar speed) |
| `wind_direction_deg` | AIJ wind direction in degrees; 0 is the case\'s reference direction (see frame) |
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
| `campaign` | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |
| `C` | ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air) |
| `c_rms` | ppm, rms of the concentration fluctuation |
| `concentration_ratio` | C / c0, c0 = q / (U\_ref L\_ref^2) as the benchmark defines it for the case (manifest cases.\<id\>.normalisation) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | least squares, kappa = 0.41, z = 0.02 .. 0.6 m (10 H) on AF\_caseK.csv: the profile is Case H\'s, tabulated for a 0.2 m building, so the window is a choice |
| Friction velocity u\* (m/s) | 0.40706 |
| Roughness length z₀ (mm) | 7.4385 |
| U\_H, measured (m/s) | 2.2377 |
| U H stated m s | 2.33 |
| Log-law error at H | -7.4 % |
| log law rms residual | 2.5 % |
| Note | the file is the approach flow of Case H (identical rows); the workbook normalises it with uH = U(0.2 m) = 3.23 m/s and H = 0.2 m |

## Known data issues

- The legacy workbook normalises with H = 0.2 m (Case H\'s building), UH = 4.94009 m/s and C0 = 18.218 ppm, not the cube\'s H = 0.06 m and U\_H = 2.33 m/s; its normalised columns are 23.6 times smaller in concentration. The API\'s concentration\_ratio uses the cube\'s c0 = 429.18 ppm.
- RS\_caseK.csv has no point numbers; point\_id is the row order of the file.
- The published CSV is the workbook rounded (3 decimals, concentrations 2), with k recomputed from the rounded rms values; the table is rebuilt from the workbook.
- AF\_caseK.csv is Case H\'s approach-flow file, row for row (x = -0.493 m, tabulated for a 0.2 m building); it gives 2.24 m/s at z = 0.06 m against the stated U\_H = 2.33.
- The lateral velocity V is dominated by a cross-flow offset (about 0.06 m/s, also in the empty tunnel); the +y and -y halves cannot confirm its sign.
- The mean concentration is not mirror-symmetric (the +y and -y values of one point differ by 44 % on average), so the mirror pairs are not a repeatability estimate; velocity and k are (3 % and 5 %).
- The workbook\'s \<usc\> / sigma\_usc (\'velocity magnitude\', never below |U|) is not in the table.
- Data paper section 3.11 describes the measurements as \'approximately 30 points at eight heights downwind of the line source\'; Case K has 203 points at five heights and a point source.
- Workbook units: x and y in millimetres in both data sheets; z in millimetres in \'Measurement data\' but metres in \'Inflow\'.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/K.json`]({{ '/api/cases/K.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/K/points.json`]({{ '/api/cases/K/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/K/points.csv`]({{ '/api/cases/K/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/K/approach_flow.csv`]({{ '/api/cases/K/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/K/geometry.json`]({{ '/api/cases/K/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/K/geometry.stl`]({{ '/api/cases/K/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/K/validation.json`]({{ '/api/cases/K/validation.json' | relative_url }}) |

## Attribution

- Data collected by Ryuichiro Yoshie (Tokyo Polytechnic University) and Takumi Tachibana (Wind Engineering Institute), 2016.
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15448050](https://doi.org/10.5281/zenodo.15448050)
- Citation requested: Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. <https://doi.org/10.1007/978-4-431-55912-2_9>
- Licence: CC BY 4.0
