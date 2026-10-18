---
title: "Data"
parent: "Case I — cube with a roof point source"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case I — cube with a roof point source: configuration, frame and units, reference data, inflow and known data issues."
---

# Case I: reference data
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
| Building | cube, 0.10 m on a side (= H) |
| Height H (m) | 0.1 |
| Reynolds number Re\_H | 11,000 |
| U\_H (m/s) | 1.7 |
| U\_H, note | the readme and the velocity sheet; the approach flow at z = H is 1.6969 m/s and the workbook\'s inflow sheet divides by 1.697 |
| Wind directions (°) | 0 |
| source | 6 mm circular outlet at the centre of the roof (0, 0, 0.1); 10 % ethane in the mixture, 400 cc/min (= 6.67e-6 m3/s of mixture, 6.67e-7 m3/s of ethane); release velocity 0.236 m/s, M = Ve/UH = 0.14 |
| reference concentration | c0 = q / (UH H^2) = 39.22 ppm (39.2 in the paper), q the ETHANE flow; concentration\_ratio = C / c0 |
| Measurement planes | velocity: y/H = 0 and z/H = 0.5, concentration: y/H = 0 and z/H = 0 (the ground) |
| Points | **Velocity**: 91<br>**concentration**: 539 |
| Instrument | velocity: laser Doppler anemometer (Dantec BSA F60), 200 Hz, 240 s; concentration: hydrocarbon analyser (Kimoto HADA-01), 1 Hz, 120 s |
| Wind tunnel | AIST wind tunnel, 20 m long, 3.0 × 2.0 m cross-section; approach flow described as a 1/7 power law (data paper section 3.9) |
| Scale, note | model scale; the source states no model:full-scale ratio; Eddy3D solves it at 1:60 (a 6 m cube) |

## Frame and units

| Property | Definition |
|---|---|
| Origin | the centre of the cube on the ground plane |
| x | +x streamwise (the wind blows toward +x); the cube spans x in \[-0.05, 0.05\]; wind points x = -0.15 ... 0.25 m, concentration points x = 0.065 ... 2.7 m |
| y | +y lateral; the cube spans y in \[-0.05, 0.05\]; concentration points reach \|y\| = 0.44 m on the ground |
| z | +z up; roof at z = 0.1 m; the outlet at (0, 0, 0.1) |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |
| Unit of k | m^2/s^2 |
| Unit of c | ppm |
| Unit of concentration ratio | dimensionless, C/c0 |

## Reference data

Source in this repository: `raw/cases/case-i/RS-w_caseI.csv` (approach flow: `raw/cases/case-i/AF_caseI.csv`).

The cleaned table has **630 rows** over **630 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `k`, `campaign`, `C`, `concentration_ratio`.

Unmeasured cells (null): U 539, V 592, W 539, k 539, C 91, concentration_ratio 91.

| Configuration | Points |
|---|---|
| default, wind tunnel, hydrocarbon analyser, WD 0° | 539 |
| default, wind tunnel, ldv, WD 0° | 91 |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 14 columns and what each holds</summary>

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
| `k` | m^2/s^2, turbulent kinetic energy |
| `campaign` | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |
| `C` | ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air) |
| `concentration_ratio` | C / c0, c0 = q / (U\_ref L\_ref^2) as the benchmark defines it for the case (manifest cases.\<id\>.normalisation) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | log law, kappa = 0.41, least squares over z = 0.02 ... 0.4 m on the workbook\'s 12-point approach profile |
| Friction velocity u\* (m/s) | 0.0928 |
| Roughness length z₀ (mm) | 0.0455 |
| U\_H, measured (m/s) | 1.6969 |
| Log-law error at H | +2.6 % |
| power law index fitted | 0.115 |
| power law index paper | 1/7 |
| Note | derived during cleaning, not published by AIJ; the workbook\'s own (z/H)^(1/7) column is within 4.6 % of the measured profile over z = 0.02 ... 0.7 m |

## Known data issues

- Two point sets, no point numbers: the velocity file (91 points: y = 0 plane and z/H = 0.5 plane) and the concentration file (539 points: y = 0 plane and the ground). The table stacks them, one row per instrument and point: velocity rows (instrument ldv) are numbered 1-91 and concentration rows (hydrocarbon\_analyser) 92-630, in the files\' order. 17 locations have both a velocity and a concentration value.
- V on the y = 0 plane (53 of 91 points) is 0 in the CSV and 1e-9 ... 4e-6 m/s in the workbook, a symmetry value. It is NaN in the table; V is measured only at the 38 off-plane points.
- The table carries the legacy workbook\'s values; the CSVs round to 3 decimals (velocity, k) and 1 decimal (concentration, ppm). Every concentration is a multiple of 0.1 ppm: a 0.4 ppm value carries +/-12 % of quantisation.
- The paper\'s c0 = 39.2 ppm needs the ETHANE flow (10 % of the 400 cc/min, 6.67e-7 m3/s); its sentence \'ethane released at 6.67e-6 m3/s\' is the mixture. With the mixture flow c0 would be 392 ppm.
- The workbook normalises the approach flow with 1.697 m/s and the points with 1.7 m/s (0.18 % apart).
- AF\_caseI.csv ends in 53 rows of \',,\' and two stray cells, \'0.5\*\' and \'1.5\*\' (chart axis labels): a reader that does not test z for a number takes them for data.
- Thirteen ground-centreline locations (x, 0, 0) are measured twice (they are on both the y = 0 and the z = 0 plane) with values up to 8.5 % apart; both are kept. The four y = 0, z = 0.05 wind points that appear twice in the workbook are identical copies and appear once.
- Only the TKE is published, no variances and no concentration fluctuation: k cannot be checked against the components.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/I.json`]({{ '/api/cases/I.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/I/points.json`]({{ '/api/cases/I/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/I/points.csv`]({{ '/api/cases/I/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/I/approach_flow.csv`]({{ '/api/cases/I/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/I/geometry.json`]({{ '/api/cases/I/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/I/geometry.stl`]({{ '/api/cases/I/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/I/validation.json`]({{ '/api/cases/I/validation.json' | relative_url }}) |

## Attribution

- Data collected by Hiroaki Kondo (National Institute of Advanced Industrial Science and Technology), Katsuhiko Mutou (National Institute of Advanced Industrial Science and Technology) and Akihiro Hori (National Institute for Environmental Studies).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15430018](https://doi.org/10.5281/zenodo.15430018)
- Citation requested: Japan Society for Atmospheric Environment (2013). Guidelines for Atmospheric Environment Assessment Methods Using CFD Models (DiMCFD). Japan Society for Atmospheric Environment (in Japanese).
- Licence: CC BY 4.0

### Cite

**APA**

```text
Kondo, H., Mutou, K., Hori, A., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case I (CubeC): Wind Tunnel Experiment for Flow and Dispersion around a Cubic Building Model [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15430018
```

**BibTeX**

```bibtex
@misc{aijuwe_case_i,
  author    = "Kondo, Hiroaki and Mutou, Katsuhiko and Hori, Akihiro and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case I (CubeC): Wind Tunnel Experiment for Flow and Dispersion around a Cubic Building Model}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15430018",
  url       = "https://doi.org/10.5281/zenodo.15430018",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
