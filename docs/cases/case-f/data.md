---
title: "Data"
parent: "Case F — Shinjuku district"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case F — Shinjuku district: configuration, frame and units, reference data, inflow and known data issues."
---

# Case F: reference data
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
| District | Shinjuku sub-centre during construction of the high-rise group, building configuration of November 1978 |
| Scale | 1:800 |
| model | terrain and buildings in a disc of radius 725 m (BD\_caseF.stl; the readme and the data paper say 800 m / 1600 m diameter) |
| Points | 13 |
| point numbers | 1-3, 5-11, 13-15 (4 and 12 absent; points 16 and later belong to later construction stages and are not in the dataset) |
| Wind directions | N, NNE, NE, ENE, SE, SSE, S, SSW, SW, WNW, NW, NNW |
| wind directions field | N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, $$W$$, WNW, NW, NNW |
| measurement planes above ground m | 5, 9, 20 |
| measurement planes z m | 15, 19, 30 |
| ground offset m | 10 |
| Normalisation | velocity ratio = mean speed / the approaching mean speed at the boundary-layer height 500 m (full scale); the field values were converted to it with the tunnel (readme). $$U(500\text{ m})$$ is 10 m/s in the data paper and 10.65 m/s implied by the profile |
| Instrument | tunnel: thermistor anemometer, 30 s averaging; field: three-cup anemometer with wind vane, 10-minute means above 5 m/s at the reference roof, December 1977 - November 1978 |
| Wind tunnel | Shimizu Corporation wind tunnel; cross-section 1.55 m wide, 2.2 m high; power-law inflow, exponent 1/4 |
| reference roofs | **SMB**: Shinjuku-Mitsui Building, roof G.L.+210 m, anemometer G.L.+237 m, for NW-NE<br>**KDD**: KDD Building, roof G.L.+165 m, anemometer G.L.+187 m, for the other directions |

{% include nomenclature.md %}

## Frame and units

| Property | Definition |
|---|---|
| Origin | centre of the reproduced district, tunnel floor plane |
| x | +x EAST (full-scale metres) |
| y | +y NORTH (compass rose in MP\_caseF.png) |
| z | +z up from the TUNNEL FLOOR; the readme\'s rule is ground = z - 10 m (the STL\'s terrain under the points is at z = 5 m) |
| Wind direction convention | compass FROM-direction (N = 0, E = 90), so N blows toward -y; flow\_dir = (-sin WD, -cos WD). Not stated by the sources; supported by the reference-building choice and by upwind roughness, and at NNW by a solved field (status \'corroborated by a solved field\'; the other directions stay \'unverified\'). |
| Lateral sign applied | 1 |
| Coordinate scale applied | 800.0 |
| Unit of length | m (FULL scale) |
| Unit of $$U/U_{\mathrm{ref}}$$ | dimensionless |
| Unit of $$\sigma_{U/U_{\mathrm{ref}}}$$ | dimensionless |

{% include nomenclature.md %}

## Reference data

Source in this repository: [`raw/cases/case-f/RS-WT_caseF.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-f/RS-WT_caseF.csv) (approach flow: [`raw/cases/case-f/AF_caseF.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-f/AF_caseF.csv)).

The cleaned table has **472 rows** over **13 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction`, `wind_direction_deg`, `x`, `y`, `z`, `velocity_ratio`, `campaign`, `velocity_ratio_sd`.

Unmeasured cells (null): `velocity_ratio_sd` 264.

<details markdown="block">
  <summary>The 40 configurations and their points</summary>

| Configuration | Points |
|---|---|
| default, field, cup anemometer, N, WD 0° | 13 |
| default, field, cup anemometer, NNE, WD 22.5° | 13 |
| default, field, cup anemometer, NE, WD 45° | 13 |
| default, field, cup anemometer, ENE, WD 67.5° | 13 |
| default, field, cup anemometer, E, WD 90° | 13 |
| default, field, cup anemometer, ESE, WD 112.5° | 13 |
| default, field, cup anemometer, SE, WD 135° | 13 |
| default, field, cup anemometer, SSE, WD 157.5° | 13 |
| default, field, cup anemometer, S, WD 180° | 13 |
| default, field, cup anemometer, SSW, WD 202.5° | 13 |
| default, field, cup anemometer, SW, WD 225° | 13 |
| default, field, cup anemometer, WSW, WD 247.5° | 13 |
| default, field, cup anemometer, W, WD 270° | 13 |
| default, field, cup anemometer, WNW, WD 292.5° | 13 |
| default, field, cup anemometer, NW, WD 315° | 13 |
| default, field, cup anemometer, NNW, WD 337.5° | 13 |
| default, wind tunnel, thermistor, N, WD 0° | 13 |
| default, wind tunnel, thermistor, NNE, WD 22.5° | 13 |
| default, wind tunnel, thermistor, NE, WD 45° | 13 |
| default, wind tunnel, thermistor, ENE, WD 67.5° | 13 |
| default, wind tunnel, thermistor, SE, WD 135° | 13 |
| default, wind tunnel, thermistor, SSE, WD 157.5° | 13 |
| default, wind tunnel, thermistor, S, WD 180° | 13 |
| default, wind tunnel, thermistor, SSW, WD 202.5° | 13 |
| default, wind tunnel, thermistor, SW, WD 225° | 13 |
| default, wind tunnel, thermistor, WNW, WD 292.5° | 13 |
| default, wind tunnel, thermistor, NW, WD 315° | 13 |
| default, wind tunnel, thermistor, NNW, WD 337.5° | 13 |
| h20, wind tunnel, thermistor, N, WD 0° | 9 |
| h20, wind tunnel, thermistor, NNE, WD 22.5° | 13 |
| h20, wind tunnel, thermistor, ENE, WD 67.5° | 12 |
| h20, wind tunnel, thermistor, S, WD 180° | 11 |
| h20, wind tunnel, thermistor, SSW, WD 202.5° | 12 |
| h20, wind tunnel, thermistor, SW, WD 225° | 9 |
| h20, wind tunnel, thermistor, NNW, WD 337.5° | 13 |
| h5, wind tunnel, thermistor, NNE, WD 22.5° | 4 |
| h5, wind tunnel, thermistor, ENE, WD 67.5° | 8 |
| h5, wind tunnel, thermistor, S, WD 180° | 5 |
| h5, wind tunnel, thermistor, SSW, WD 202.5° | 5 |
| h5, wind tunnel, thermistor, NNW, WD 337.5° | 7 |

</details>

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 11 columns and what each holds</summary>

| Column | Symbol | Meaning |
|---|---|---|
| `point_id` |  | the tunnel\'s own measurement point number |
| `config` |  | configuration key: \'default\', Case C centre building \'0D\'/\'1D\'/\'2D\', Case E state \'bc\' (before) / \'ac\' (after construction) |
| `instrument` |  | \'split\_fibre\' (vector components) or \'thermistor\' (omnidirectional scalar speed) |
| `wind_direction` |  | compass name of the direction the wind comes FROM (Case E) |
| `wind_direction_deg` |  | AIJ wind direction in degrees; 0 is the case\'s reference direction (see frame) |
| `x` |  | m, case frame |
| `y` |  | m, case frame |
| `z` |  | m above ground, case frame |
| `velocity_ratio` | $$U/U_{\mathrm{ref}}$$ | dimensionless, mean speed over the case\'s reference speed (Case E: $$V_{\mathrm{s}}/U(15.9\text{ m})$$, $$U(15.9\text{ m})$$ = 3.935 m/s; see the case\'s normalisation) |
| `campaign` |  | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |
| `velocity_ratio_sd` | $$\sigma_{U/U_{\mathrm{ref}}}$$ | standard deviation of `velocity_ratio` over the observations behind a field value (Case F) |

{% include nomenclature.md %}

</details>

## Inflow

| Property | Value |
|---|---|
| Method | power law on the 18 published heights (z 10 ... 400 m full scale); the data paper states exponent 1/4 |
| Power-law exponent, fitted | 0.277 |
| Power-law exponent, data paper | 0.25 |
| $$U$$ 500m m s | **data paper**: 10.0<br>**implied by profile**: 10.65 |
| Note | AF\_caseF.csv stops at 400 m ($$U$$ = 10.0 m/s); the workbook\'s $$U/U_R$$ profile (0.94 at 400 m) puts the 500 m speed at 10.65 m/s |

{% include nomenclature.md %}

## Known data issues

- The 16 field rows of point 14 in RS-FO\_caseF.csv hold the workbook\'s value of the NEXT wind direction clockwise (the series is shifted by one); the cleaned table follows the workbook (clean/QUESTIONS.md QF1).
- Tunnel and STL coordinates are MODEL scale (1:800); the field\'s are full scale. The case frame is full scale; the tunnel\'s x, y, z and the STL are multiplied by 800.
- z is height above the tunnel floor. The readme\'s rule \'ground = z - 10 m\' gives the 5 / 9 / 20 m planes, but the STL\'s terrain under all 13 points is at z = 5 m, so the planes stand 10 / 14 / 25 m above it.
- BD\_caseF.stl is wound inward on every ground, roof and sampled wall facet and is open along the rim of its 725 m disc (812 boundary edges); the served geometry.stl is re-wound outward and closed with a base slab down to z = -1 m.
- MP\_caseF.csv names the two reference points the other way round from the workbook, the STL and MP\_caseF.png (the workbook\'s Shinjuku-Mitsui Building is the 225 m tower at (-17.5, 96.0), the KDD Building the 180 m one at (85.8, -347.1)).
- Field values are the legacy workbook\'s roof-anemometer ratios times 0.940 (NW-NE) or 0.963 (other directions); sigma is the workbook\'s S.D. rounded to 0.01 times that factor, so it moves in steps of 0.0094 / 0.0096.
- The tunnel did not run E, ESE, WSW or W; the field data cover all 16. The 5 m and 20 m planes exist at some points only (29 and 79 rows).
- One tunnel value (point 8, SW, 9 m: 0.474) has no counterpart in the workbook\'s results sheet, and the flat \'Sheet1\' table has 0.63 there.
- Field anemometer heights above the tunnel floor are 13 - 21 m (3 - 11 m above ground by the readme\'s rule); the data paper says 3 - 9 m, so points 13 and 14 (11 m) disagree.
- The thermistor reads a SCALAR speed and the cup anemometer a 10-minute mean: a RANS $$\lvert\mathbf{U}\rvert$$ is biased low against both.
- The files do not say whether a wind direction names where the wind comes from. The cleaned tables read it as the direction the wind comes from (N = 0, E = 90). At NNW a solved field supports that reading: Eddy3D\'s OpenFOAM 12 run for the wind from NNW correlates R 0.935 with the tunnel\'s 9 m column labelled NNW and R 0.077 with its column labelled SSE, the opposite wind (clean/QUESTIONS.md QF9); the other directions are not solved and stay unverified.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/F.json`]({{ '/api/cases/F.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/F/points.json`]({{ '/api/cases/F/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/F/points.csv`]({{ '/api/cases/F/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/F/approach_flow.csv`]({{ '/api/cases/F/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/F/geometry.json`]({{ '/api/cases/F/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/F/geometry.stl`]({{ '/api/cases/F/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/F/validation.json`]({{ '/api/cases/F/validation.json' | relative_url }}) |

## Attribution

- Data collected by K. Fujii, Y. Asami, Y. Iwasa et al. (the original 1978 investigation; the readme names no data collectors).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15589621](https://doi.org/10.5281/zenodo.15589621)
- Citation requested: Fujii, K., Asami, Y., Iwasa, Y. et al. (1978). Wind in Shinjuku Sub-Central Area — Comparison Between Field Measurement and Wind Tunnel Experiment. Proc. 5th Symposium on Wind Resistance of Structures, 91-98 (in Japanese).
- Licence: CC BY 4.0

### Cite

**APA**

```text
Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case F (Shinjuku): Wind Tunnel Experiment and Field Observation for Flow within an Actual Urban Area in Shinjuku [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15589621
```

**BibTeX**

```bibtex
@misc{aijuwe_case_f,
  author    = "Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case F (Shinjuku): Wind Tunnel Experiment and Field Observation for Flow within an Actual Urban Area in Shinjuku}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15589621",
  url       = "https://doi.org/10.5281/zenodo.15589621",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
