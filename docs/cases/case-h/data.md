---
title: "Data"
parent: "Case H — 1:1:2 building with a floor point source"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case H — 1:1:2 building with a floor point source: configuration, frame and units, reference data, inflow and known data issues."
---

# Case H: reference data
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
| Building | 1:1:2 (width : depth : height) prism, 0.10 × 0.10 × 0.20 m |
| Width b (m) | 0.1 |
| Height H (m) | 0.2 |
| Reynolds number Re\_H | 43,000 |
| U\_H (m/s) | 3.226 |
| U\_H, note | the workbook\'s uH; the readme and the data paper state 3.23 m/s; the workbook\'s free-stream reference U0 is 5.279 m/s |
| Wind directions (°) | 0 |
| source | 4 mm hole in the floor 0.25 H = 0.05 m behind the leeward face at (0.05, 0, 0); ethylene (C2H4), 100 %, 350 cc/min = 5.83e-6 m3/s |
| reference concentration | c0 = cgas q / (UH H^2) = 45.18 ppm (45.2 in the paper); concentration\_ratio = C / c0 |
| Measurement planes | vertical centre plane y/H = 0, horizontal z/H = 1/16 (y in \[-0.2, 0.2\]), horizontal z/H = 1/4 and 1/2 (y in \[0, 0.2\]) |
| Points | 876 |
| Instrument | velocity: constant-temperature anemometer (DANTEC 90C10) with a split-fibre probe (55R55, 55R56, 55R57), 1000 Hz, 120 s; concentration: high-speed total hydrocarbon analyser, 1000 Hz, 120 s |
| Wind tunnel | Eiffel-type boundary-layer wind tunnel, Tokyo Polytechnic University, Atsugi (1.0 m high, 1.2 m wide) |
| Scale, note | model scale; the source states no model:full-scale ratio; Eddy3D solves it at 1:100 |

## Frame and units

| Property | Definition |
|---|---|
| Origin | the centre of the building\'s leeward face on the ground plane |
| x | +x streamwise (the wind blows toward +x); the building spans x in \[-0.1, 0\]; points at x = -0.2 ... 0.4 m |
| y | +y lateral; the building spans y in \[-0.05, 0.05\]; the z = 1/16 H plane covers y in \[-0.2, 0.2\] |
| z | +z up; roof at z = 0.2 m; points at z = 0.01 ... 0.3 m |
| Lateral sign applied | -1 for point numbers 1-220 (the vertical-plane sheet of the workbook), +1 elsewhere |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |
| Unit of variance | m^2/s^2 |
| Unit of k | m^2/s^2 |
| Unit of c | ppm |
| Unit of concentration ratio | dimensionless, C/c0 |

## Reference data

Source in this repository: [`raw/cases/case-h/RS_caseH.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-h/RS_caseH.csv) (approach flow: [`raw/cases/case-h/AF_caseH.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-h/AF_caseH.csv)).

The cleaned table has **1,652 rows** over **876 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`, `C`, `c_rms`, `concentration_ratio`.

Unmeasured cells (null): U 826, V 826, W 826, uu 826, vv 826, ww 826, k 826, C 826, c_rms 826, concentration_ratio 826.

| Configuration | Points |
|---|---|
| default, wind tunnel, hydrocarbon analyser, WD 0° | 826 |
| default, wind tunnel, split fibre, WD 0° | 826 |

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
| Method | log law, kappa = 0.41, least squares over z = 0.02 ... 2H on the workbook\'s 17-point approach profile (x = -0.493 m) |
| Friction velocity u\* (m/s) | 0.4065 |
| Roughness length z₀ (mm) | 7.449 |
| U\_H, measured (m/s) | 3.226 |
| Log-law error at H | +1.1 % |
| turbulence intensity at H | 0.2165 |
| Note | derived during cleaning, not published by AIJ |

## Known data issues

- The table carries the legacy workbook\'s values (ratios at full precision x uH = 3.226 m/s), not RS\_caseH.csv\'s: on the z/H = 1/2 and 1/4 planes (and in the approach profile) the CSV\'s U, V, W are the workbook ratios ROUNDED TO 0.01 before the scaling, a 0.032 m/s grid (+/-0.016 m/s).
- One row per instrument and point: velocity rows (split fibre) and concentration rows (hydrocarbon analyser) with the same point\_id (the CSV\'s No.). The velocity line is x = 0.40 m and the concentration line x = 0.38 m, so 50 points have no velocity and 50 no concentration (-999.9 in the CSV); none of them is inside the building.
- V of the vertical-plane sheet (point numbers 1-220) is the exact negative of V at the same points in the horizontal-plane sheets (positive toward -y); it is multiplied by -1 so that V is positive toward +y everywhere, as in Cases A and D.
- The y = 0, z = 0.1 line (13 locations) is in two sheets and appears twice in the table, as exact copies once V is flipped; they are not independent repeat measurements.
- Concentration is the analyser\'s reading: upwind of the building (where the true value is zero) it is +/-0.1 ppm, and 97 of 826 values are negative (minimum -0.83 ppm). Log-based statistics (geometric mean, geometric variance) need a floor.
- The published header misspells w\_rms as \'w\_rsm\'; the workbook\'s inflow sheet labels z as \'mm\' but holds metres.
- The profile\'s uw and uv are published but the approach-flow table has no column for them.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/H.json`]({{ '/api/cases/H.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/H/points.json`]({{ '/api/cases/H/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/H/points.csv`]({{ '/api/cases/H/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/H/approach_flow.csv`]({{ '/api/cases/H/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/H/geometry.json`]({{ '/api/cases/H/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/H/geometry.stl`]({{ '/api/cases/H/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/H/validation.json`]({{ '/api/cases/H/validation.json' | relative_url }}) |

## Attribution

- Data collected by Ryuichiro Yoshie (Tokyo Polytechnic University) and Takumi Tachibana (Wind Engineering Institute).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15429871](https://doi.org/10.5281/zenodo.15429871)
- Citation requested: Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. <https://doi.org/10.1007/978-4-431-55912-2_9>
- Licence: CC BY 4.0

### Cite

**APA**

```text
Yoshie, R., Tachibana, T., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case H (112C): Wind Tunnel Experiment for Flow and Dispersion around a 1:1:2 Shape Building Model [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15429871
```

**BibTeX**

```bibtex
@misc{aijuwe_case_h,
  author    = "Yoshie, Ryuichiro and Tachibana, Takumi and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case H (112C): Wind Tunnel Experiment for Flow and Dispersion around a 1:1:2 Shape Building Model}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15429871",
  url       = "https://doi.org/10.5281/zenodo.15429871",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
