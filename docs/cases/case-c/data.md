---
title: "Data"
parent: "Case C — 3 × 3 block array"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case C — 3 × 3 block array: configuration, frame and units, reference data, inflow and known data issues."
---

# Case C: reference data
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
| Array | 3 x 3 cubes, D = 0.20 m, block centres at x, y in {-0.4, 0, +0.4} m (pitch 0.40 m = 2D, street width D) |
| Block size D (m) | 0.2 |
| Centre building | **0D**: no centre building<br>**1D**: 0.2 x 0.2 x 0.2 m (same as the surroundings)<br>**2D**: 0.2 x 0.2 x 0.4 m |
| Wind directions (°) | 0, 22.5, 45 |
| Configurations | 9 |
| Configurations, note | 3 centre-building heights x 3 wind directions; all nine share the identical 120-point set |
| Measurement height (m) | 0.02 |
| Measurement height, note | z = 0.1 D for every point (2.0 m at the 1:100 scale Eddy3D solves it at) |
| Reynolds number Re\_D | 52,000 |
| U\_H (m/s) | 3.654 |
| U\_H, note | U at z = D = 0.20 m from AF\_caseC.csv; the data paper states U\_H = 3.65 m/s |
| Instrument | thermistor anemometer (omnidirectional scalar speed), 1 Hz, 30 s per point; approach flow by I-type hot wire, 500 Hz, 30 s |
| Wind tunnel | Technology Development Division, Fujita Corporation, Tokyo |
| Pitch, note | The 0.40 m pitch is read from MP-z-caseC.png and Figure 3 of the data paper (street = D); the 120-point grid alone bounds the pitch to (0.35, 0.40\] m (the 49 absent nodes of the 13 x 13 grid are exactly the nine footprints for 0.375 m as well as 0.40 m). |

## Frame and units

| Property | Definition |
|---|---|
| Origin | array centre on the ground plane (centre of the middle block) |
| x | +x streamwise at WD = 0 |
| y | +y lateral |
| z | +z up; all points at z = 0.02 |
| Wind direction convention | In the CSV\'s own frame WD rotates the wind from +x TOWARD -y. Figure 3 of the data paper draws the fan rotating toward +y. The two disagree by a y-sign flip; this release keeps the CSV frame. The disagreement is invisible at WD = 0. |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |

<details markdown="block">
<summary>Data notes: Frame and wind direction</summary>

Checked three ways on the data: y -\> -y is a symmetry, the x \<= -0.25 band is faster than x \>= +0.25 in every configuration, and the regression slope of Vs is most negative within 0.8-4.3 deg of +x. The WD = 45 field is mirror-symmetric about y = -x to within the experiment\'s repeatability, 0.10-0.13 m/s, and not about y = +x, 0.5-0.8 m/s. The CSV frame is the frame the point coordinates live in.

</details>

## Reference data

Source in this repository: `raw/cases/case-c/RS_caseC.csv` (approach flow: `raw/cases/case-c/AF_caseC.csv`).

The cleaned table has **1,080 rows** over **120 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `Vs`, `campaign`.

<details markdown="block">
  <summary>The 9 configurations and their points</summary>

| Configuration | Points |
|---|---|
| 0D, WD 0° | 120 |
| 0D, WD 22.5° | 120 |
| 0D, WD 45° | 120 |
| 1D, WD 0° | 120 |
| 1D, WD 22.5° | 120 |
| 1D, WD 45° | 120 |
| 2D, WD 0° | 120 |
| 2D, WD 22.5° | 120 |
| 2D, WD 45° | 120 |

</details>

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 9 columns and what each holds</summary>

| Column | Meaning |
|---|---|
| `point_id` | the tunnel\'s own measurement point number |
| `config` | configuration key: \'default\', Case C centre building \'0D\'/\'1D\'/\'2D\', Case E state \'bc\' (before) / \'ac\' (after construction) |
| `instrument` | \'split\_fibre\' (vector components) or \'thermistor\' (omnidirectional scalar speed) |
| `wind_direction_deg` | AIJ wind direction in degrees; 0 is the case\'s reference direction (see frame) |
| `x` | m, case frame |
| `y` | m, case frame |
| `z` | m above ground, case frame |
| `Vs` | m/s, mean omnidirectional scalar wind speed (thermistor); Case D also lists \|U\| of the split-fibre probe under Vs for its 33 vector points |
| `campaign` | \'wind\_tunnel\' (model scale) or \'field\' (a full-scale observation: Cases F, G, M) |

</details>

## Inflow

| Property | Value |
|---|---|
| Method | log law, kappa = 0.41, least squares on AF\_caseC.csv (16 points, z = 0.01 ... 1.2 m); two windows |
| Fit window | z range m \[0.02, 0.4\]; Friction velocity u\* (m/s) 0.25598; Roughness length z₀ (mm) 0.4797; error at U D +3.08 %; error at z 0.02 -4.31 %; scored ratio bias -7.17 % |
| Fit window | z range m \[0.01, 0.4\]; Friction velocity u\* (m/s) 0.22853; Roughness length z₀ (mm) 0.2362; error at U D +2.83 %; error at z 0.02 +1.65 %; scored ratio bias -1.15 % |
| Power-law exponent, fitted | 0.19 |
| Power-law exponent, data paper | 0.28 |
| Turbulence intensity at D | 0.219 |
| Note | derived during scoping, not published by AIJ |

<details markdown="block">
<summary>Interpretation: Inflow fit</summary>

The fit has two windows because Case C scores at ONE height (z = 0.02 m) and the near-ground half of the fit matters. The tunnel profile is closer to a power law than a log law, so a log-law inlet carries a ~2.3 % rms residual over the fitted range.

</details>

## Known data issues

- The measured quantity Vs is the MEAN OMNIDIRECTIONAL SCALAR speed from a thermistor, not \|mean velocity vector\|. A RANS \|U\| is biased low against it; the data paper suggests comparing sqrt(\|U\|^2 + 2k) as a conservative correction (over all 1080 rows no Vs is below 0.13 U\_H).
- The \'CB\' column is TEXT (\'0D\', \'1D\', \'2D\'); a reader that parses every field as a number gets NaN for it. The header ends with a trailing comma (an empty 8th column).
- 1080 rows = 3 wind directions x 3 centre buildings x 120 points, not 3 configurations. In the 0D configuration the 25 centre grid nodes are still absent although the ground there is free: the grid is held constant across configurations.
- 24 of the 120 points sit exactly on a building face plane (\|x\| = 0.30 or \|y\| = 0.30) in the open gap between two blocks: legitimate fluid points, but a probe\'s cell lookup is delicate there.
- Point numbers 1, 2, 3, 34, 35, 36, 37, 46, 55, 100, 101, 102 do not occur (No. runs 4 ... 132 with nine interior gaps).
- Experimental repeatability, from the mirror-symmetric point pairs: mean \|dVs\| 0.088-0.137 m/s (0.024-0.038 U\_H).

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/C.json`]({{ '/api/cases/C.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/C/points.json`]({{ '/api/cases/C/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/C/points.csv`]({{ '/api/cases/C/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/C/approach_flow.csv`]({{ '/api/cases/C/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/C/geometry.json`]({{ '/api/cases/C/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/C/geometry.stl`]({{ '/api/cases/C/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/C/validation.json`]({{ '/api/cases/C/validation.json' | relative_url }}) |

## Attribution

- Data collected by Yoshitami Nonomura (Yamato University).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15401791](https://doi.org/10.5281/zenodo.15401791)
- Citation requested: Nonomura, Y., Kobayashi, N., Tominaga, Y., Mochida, A. (2003). The cross comparison of CFD results for flow field around building models (part 3). Japan Association for Wind Engineering, 95, 83-84 (in Japanese). <https://doi.org/10.14887/jaweam.2003.0.41.0>
- Licence: CC BY 4.0

### Cite

**APA**

```text
Nonomura, Y., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case C (Blocks): Wind Tunnel Experiment for Flow within Simple Building Blocks [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15401791
```

**BibTeX**

```bibtex
@misc{aijuwe_case_c,
  author    = "Nonomura, Yoshitami and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case C (Blocks): Wind Tunnel Experiment for Flow within Simple Building Blocks}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15401791",
  url       = "https://doi.org/10.5281/zenodo.15401791",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
