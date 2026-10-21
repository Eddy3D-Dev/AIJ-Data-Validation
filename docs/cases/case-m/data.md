---
title: "Data"
parent: "Case M"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case M — TPU Atsugi campus: configuration, frame and units, reference data, inflow and known data issues."
---

# Case M: reference data
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
| site | Tokyo Polytechnic University, Atsugi campus; terrain falls from about 32 m (campus plateau) to 3.6 m at the east edge; tallest building about 32 m |
| Scale | 1:600 |
| Points | 15 |
| Measurement height (m) | 3 |
| Measurement height, note | 3 m above the local ground, full scale (0.005 m model) |
| Wind directions (°) | 175, 180, 185 |
| wind direction velocity deg | 180 |
| field runs | 18 |
| field wind directions deg | 78 ... 200.7 (mean direction at the reference point per run); 11 of 18 within 5° of 180° |
| reference | **$$U$$ R m s**: 4.08<br>**H R m model**: 0.068<br>**H R m full**: 41<br>**R**: rooftop of the main building: the point is 41 m above the ground, 8 m above the roof in the STL |
| tracer | **Wind tunnel**: C2H4, 100 %, 6 mm outlet, 150 cc/min = 2.5e-6 m³/s (0.09 m/s)<br>**field**: PMCH (C7F14), 200 ppm, 5 L/min, 1.5 m above ground, 25-26 Feb 2014, 18 runs of 10 min sampling |
| Normalisation | concentration ratio = $$C/c_0$$, $$c_0 = \dfrac{q}{U_R H_R^2}$$: 132.5 ppm in the tunnel (the paper rounds to 1.33e2); per run in the field (1,444 ... 7,379 ppq) |
| Instrument | tunnel: DANTEC split-fibre probe (1000 Hz, 240 s) and high-speed hydrocarbon analyser; field: sorbent tubes with GC-ECD, sonic anemometer SAT-600 at the reference point |
| Wind tunnel | Eiffel-type boundary-layer wind tunnel, Tokyo Polytechnic University; cross-section 1.0 m high, 1.2 m wide; power law exponent 0.27 (AIJ Loads category IV) with an upwind taper for the topography |

{% include nomenclature.md %}

## Frame and units

| Property | Definition |
|---|---|
| Origin | centre of the tunnel turntable on the floor plane (ground surface there at $$z = 33.07\thinspace\mathrm{m}$$) |
| x | $$+x$$ NORTH (full-scale metres) |
| y | $$+y$$ WEST (compass rose of MP\_caseM.png: N at $$+x$$, W at $$+y$$); the frame is right-handed |
| z | $$+z$$ up from the TUNNEL FLOOR; the campus ground lies at z ~ 32 m |
| Wind direction convention | meteorological FROM-direction, so 180° blows toward $$+x$$; flow\_dir = (-cos WD, +sin WD), and a larger WD turns the plume toward -y. Measured on the tunnel\'s 175 / 180 / 185° and on the 18 field runs. |
| Lateral sign applied | 1 |
| Coordinate scale applied | 600.0 |
| Unit of length | m (FULL scale) |
| Unit of velocity | m/s (the tunnel\'s) |
| Unit of variance | m²/s² |
| Unit of concentration | ppm (the field\'s ppq converted) |
| Unit of $$c^\ast$$ | dimensionless |

## Reference data

Source in this repository: [`raw/cases/case-m/RS-WT_caseM.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-m/RS-WT_caseM.csv) (approach flow: [`raw/cases/case-m/AF_caseM.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-m/AF_caseM.csv)).

The cleaned table has **330 rows** over **15 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`, `run`, `C`, `c_rms`, `concentration_ratio`.

Unmeasured cells (null): `U` 315, `V` 315, `W` 315, `uu` 315, `vv` 315, `ww` 315, `k` 315, `C` 15, `c_rms` 285, `concentration_ratio` 15.

<details markdown="block">
  <summary>The 22 configurations and their points</summary>

| Configuration | Points |
|---|---|
| default, wind tunnel, hydrocarbon analyser, WD 175° | 15 |
| default, wind tunnel, hydrocarbon analyser, WD 180° | 15 |
| default, wind tunnel, hydrocarbon analyser, WD 185° | 15 |
| default, field, sorbent gc ecd, 9, WD 78° | 15 |
| default, field, sorbent gc ecd, 10, WD 115.667° | 15 |
| default, field, sorbent gc ecd, 1, WD 132.6° | 15 |
| default, field, sorbent gc ecd, 2, WD 144° | 15 |
| default, field, sorbent gc ecd, 11, WD 173.667° | 15 |
| default, field, sorbent gc ecd, 3, WD 175° | 15 |
| default, field, sorbent gc ecd, 13, WD 175.9° | 15 |
| default, field, sorbent gc ecd, 12, WD 176.7° | 15 |
| default, field, sorbent gc ecd, 15, WD 178.6° | 15 |
| default, field, sorbent gc ecd, 5, WD 179.6° | 15 |
| default, field, sorbent gc ecd, 14, WD 179.7° | 15 |
| default, field, sorbent gc ecd, 8, WD 180.3° | 15 |
| default, field, sorbent gc ecd, 4, WD 181.3° | 15 |
| default, field, sorbent gc ecd, 16, WD 181.9° | 15 |
| default, field, sorbent gc ecd, 7, WD 183.3° | 15 |
| default, field, sorbent gc ecd, 6, WD 184.3° | 15 |
| default, field, sorbent gc ecd, 17, WD 194.2° | 15 |
| default, field, sorbent gc ecd, 18, WD 200.7° | 15 |
| default, wind tunnel, split fibre, WD 180° | 15 |

</details>

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 19 columns and what each holds</summary>

| Column | Symbol | Meaning |
|---|---|---|
| `point_id` |  | the tunnel\'s own measurement point number |
| `config` |  | configuration key: \'default\', Case C centre building \'0D\'/\'1D\'/\'2D\', Case E state \'bc\' (before) / \'ac\' (after construction) |
| `instrument` |  | \'split\_fibre\' (vector components) or \'thermistor\' (omnidirectional scalar speed) |
| `wind_direction_deg` |  | AIJ wind direction in degrees; 0 is the case\'s reference direction (see frame) |
| `x` |  | m, case frame |
| `y` |  | m, case frame |
| `z` |  | m above ground, case frame |
| `U` | $$U$$ | m/s, mean velocity along $$+x$$ |
| `V` | $$V$$ | m/s, mean velocity along $$+y$$ (sign unified: positive toward $$+y$$) |
| `W` | $$W$$ | m/s, mean velocity along $$+z$$ |
| `uu` | $$\overline{u'u'}$$ | m²/s², variance of u |
| `vv` | $$\overline{v'v'}$$ | m²/s², variance of v |
| `ww` | $$\overline{w'w'}$$ | m²/s², variance of w |
| `k` | $$k$$ | m²/s², turbulent kinetic energy |
| `campaign` |  | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |
| `run` |  | replicate label within a campaign where the dataset publishes individual runs (Case M); empty elsewhere |
| `C` | $$C$$ | ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air) |
| `c_rms` | $$c_{\mathrm{rms}}$$ | ppm, rms of the concentration fluctuation |
| `concentration_ratio` | $$c^\ast$$ | $$C/c_0$$, $$c_0 = \dfrac{q}{U_{\mathrm{ref}} L_{\mathrm{ref}}^2}$$ as the benchmark defines it for the case (manifest cases.\<id\>.normalisation) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | power law on the workbook\'s 40 heights (z 0.005 ... 0.6 m model) at $$x = -0.498\thinspace\mathrm{m}$$; the data paper states exponent 0.27 |
| Power-law exponent, fitted | 0.272 |
| Power-law exponent, data paper | 0.27 |
| $$U$$ at R height m s | 3.94 |
| $$U$$ R m s | 4.08 |
| Note | z is height above the empty tunnel floor; at the profile station the model\'s taper is already 0.052 m high, so the 10 lowest heights lie below it |

## Known data issues

- Field concentrations are in ppq (1e-15 volume fraction) and the tunnel\'s in ppm: 1 ppq = 1e-9 ppm. The cleaned table converts the field\'s to ppm and carries $$C/c_0$$ for both, with the run\'s own $$c_0$$ in the field.
- Every field run has its own reference speed $$U_R$$, mean direction $$\mathrm{WD_R}$$ and tracer flow q (clean/manifest.json -\> cases.M.extra\_measurements.field\_runs); the row\'s wind\_direction\_deg is $$\mathrm{WD_R}$$.
- The tunnel measured velocity only at 180°; at 175° and 185° the CSV has -999.9 in all seven velocity columns.
- RS-WT\_caseM.csv is the legacy workbook rounded (2 dp velocity, 1 dp concentration), and its $$k$$ is half the sum of the 2-dp RMS values, up to 0.005 m2/s2 from the workbook\'s; the cleaned table carries the workbook\'s values.
- The tunnel source is on the ground in the workbook, LC\_caseM.csv and the STL (readme: \'on a rooftop\'); the field source was 1.5 m above ground.
- $$H_R$$ = 41 m is the anemometer height above the ground; the main roof under the reference point is about 33 m above it. $$c_0$$ uses $$H_R$$ = 0.068 m (41 m / 600 = 0.06833 m would give 131.2 ppm, -1 %).
- The field has an ambient floor of 8 - 11 ppq at points 11 - 15 in every run (not subtracted); the tunnel\'s concentration has a zero offset (two negative means at point 12) and an rms floor of 7 ppm.
- Only 11 of the 18 field runs are within 5° of 180°, the tunnel\'s direction; runs 1, 2 and 9 have $$U_R$$ of 1.4 - 1.8 m/s.
- BD\_caseM.stl is MODEL scale, wound inward on its ground and roof facets, and has 21 boundary and 7 non-manifold edges (7 on the rim of the panel, 14 on 7 slivers hanging on building roofs); the served geometry.stl is multiplied by 600, re-wound outward, without the slivers and closed with a base slab down to $$z = -1\thinspace\mathrm{m}$$.
- The approach-flow heights are above the empty tunnel floor: at the profile station the model\'s taper is 0.052 m high, above the 10 lowest profile heights.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/M.json`]({{ '/api/cases/M.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/M/points.json`]({{ '/api/cases/M/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/M/points.csv`]({{ '/api/cases/M/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/M/approach_flow.csv`]({{ '/api/cases/M/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/M/geometry.json`]({{ '/api/cases/M/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/M/geometry.stl`]({{ '/api/cases/M/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/M/validation.json`]({{ '/api/cases/M/validation.json' | relative_url }}) |

## Attribution

- Data collected by Ryuichiro Yoshie (Tokyo Polytechnic University) and Takumi Tachibana (Wind Engineering Institute).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15487857](https://doi.org/10.5281/zenodo.15487857)
- Citation requested: Tachibana, T., Yoshie, R., Nakayama, S., Kishida, T., Miyashita, K., Sasaki, R. (2022). Comparison between field measurement and wind tunnel experiments of gas dispersion in an urban area and verification of similarity law. Journal of Wind Engineering 47(3), 39-52 (in Japanese). <http://dx.doi.org/10.5359/jwe.47.39>
- Licence: CC BY 4.0

### Cite

**APA**

```text
Yoshie, R., Tachibana, T., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case M (TPU): Wind Tunnel Experiment and Field Observation for Flow and Dispersion within TPU Campus [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15487857
```

**BibTeX**

```bibtex
@misc{aijuwe_case_m,
  author    = "Yoshie, Ryuichiro and Tachibana, Takumi and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case M (TPU): Wind Tunnel Experiment and Field Observation for Flow and Dispersion within TPU Campus}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15487857",
  url       = "https://doi.org/10.5281/zenodo.15487857",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
