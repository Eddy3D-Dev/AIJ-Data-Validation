---
title: "Data"
parent: "Case L — 9 x 14 cube array, line source, non-isothermal"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case L — 9 x 14 cube array, line source, non-isothermal: configuration, frame and units, reference data, inflow and known data issues."
---

# Case L: reference data
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
| Array | 14 rows (along x) by 9 columns (across y) of cubes, $$H = 0.06\thinspace\mathrm{m}$$, pitch 0.12 m (street width = H, plan area ratio 25 %), published as BD\_caseL.stl; the data paper calls it \'9 rows by 14 columns\' |
| Height H (m) | 0.06 |
| pitch m | 0.12 |
| cubes | 126 |
| Reynolds number $$\mathrm{Re_H}$$ | 5600 |
| $$U_H$$ (m/s) | 1.339415 |
| Wind directions (°) | 0 |
| Measurement planes | 8 heights (4 .. 150 mm) at 27 locations in the streets near the source, 4 heights (70 .. 150 mm) at 14 locations above the blocks, 3 heights (4 .. 30 mm) at 24 locations around |
| Points | 344 |
| stratification | unstable: floor 45.0 degC, air at $$z = H$$ 14.75 degC (difference 30.3 K), bulk Richardson number -0.035 (workbook; the readme says -0.04); the workbook gives the building surface as 42.2 degC |
| source | floor line source across the tunnel at $$x = -0.15\thinspace\mathrm{m}$$ between rows 7 and 8: readme 0.037 m x 1.2 m, BD\_caseL.stl patch 0.04 m x 1.02 m; 100 % ethylene, 8.33e-6 m³/s (500 cc/min) at 35 degC |
| concentration normalisation | $$c_0 = \dfrac{q}{U_H H^2}$$ = 1728.23 ppm (the workbook\'s value) |
| Instrument | split-fibre hot wire (velocity), cold wire (temperature), high-speed hydrocarbon analyser (concentration), 1000 Hz with a 200 Hz low-pass filter, 60 s per point |
| Wind tunnel | thermally stratified wind tunnel, Tokyo Polytechnic University (Atsugi); 1.2 m wide, 1.0 m high; 26 aluminium angles 9 mm high every 200 mm as roughness; model floor 10 mm above the tunnel floor |
| Scale, note | model scale; the sources state no model:full scale ratio |

{% include nomenclature.md %}

## Frame and units

| Property | Definition |
|---|---|
| Origin | bottom centre of the windward wall of the 9th row (of 14) of the central column: $$x = 0$$ is that wall, $$y = 0$$ the centre line of the central column |
| x | $$+x$$ streamwise (the wind blows toward $$+x$$); row $$k$$ spans x in \[0.12 ($$k$$-9), 0.12 ($$k$$-9) + 0.06\], so the array spans $$x \in \lbrack -0.96,\thinspace 0.66\rbrack$$ |
| y | $$+y$$ lateral; column centres at $$y = 0$$, +-0.12, ... +-0.48 (the array spans $$y \in \lbrack -0.51,\thinspace 0.51\rbrack$$) |
| z | $$+z$$ up from the model floor; cube tops at $$z = 0.06$$; heated floor at $$z = 0$$ |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |
| Unit of variance | m²/s² |
| Unit of $$k$$ | m²/s² |
| Unit of concentration | ppm of the released ethylene |
| Unit of temperature | degC (T); K ($$T_{\mathrm{rms}}$$); heat fluxes K m/s; concentration fluxes ppm m/s |

{% include nomenclature.md %}

## Reference data

Source in this repository: [`raw/cases/case-l/RS_caseL.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-l/RS_caseL.csv) (approach flow: [`raw/cases/case-l/AF_caseL.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-l/AF_caseL.csv)).

The cleaned table has **344 rows** over **344 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`, `uv`, `uw`, `C`, `c_rms`, `concentration_ratio`, `T`, `T_rms`, `uc`, `vc`, `wc`, `uT`, `vT`, `wT`.

| Configuration | Points |
|---|---|
| default, wind tunnel, split fibre, WD 0° | 344 |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 28 columns and what each holds</summary>

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
| `uv` | $$\overline{u'v'}$$ | m²/s², Reynolds shear stress \<u\'v\'\> as published |
| `uw` | $$\overline{u'w'}$$ | m²/s², Reynolds shear stress \<u\'w\'\> as published |
| `C` | $$C$$ | ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air) |
| `c_rms` | $$c_{\mathrm{rms}}$$ | ppm, rms of the concentration fluctuation |
| `concentration_ratio` | $$c^\ast$$ | $$C/c_0$$, $$c_0 = \dfrac{q}{U_{\mathrm{ref}} L_{\mathrm{ref}}^2}$$ as the benchmark defines it for the case (manifest cases.\<id\>.normalisation) |
| `T` | $$T$$ | degC, mean air temperature as published (Cases J, L) |
| `T_rms` | $$T_{\mathrm{rms}}$$ | K, rms of the temperature fluctuation |
| `uc` | $$\overline{u'c'}$$ | ppm m/s, turbulent concentration flux \<u\'c\'\> |
| `vc` | $$\overline{v'c'}$$ | ppm m/s, turbulent concentration flux \<v\'c\'\> |
| `wc` | $$\overline{w'c'}$$ | ppm m/s, turbulent concentration flux \<w\'c\'\> |
| `uT` | $$\overline{u'\theta'}$$ | K m/s, turbulent heat flux \<u\'theta\'\> |
| `vT` | $$\overline{v'\theta'}$$ | K m/s, turbulent heat flux \<v\'theta\'\> |
| `wT` | $$\overline{w'\theta'}$$ | K m/s, turbulent heat flux \<w\'theta\'\> |

{% include nomenclature.md %}

</details>

## Inflow

| Property | Value |
|---|---|
| Method | least squares, $$\kappa$$ = 0.41, $$z = 0.02\thinspace\ldots\thinspace 0.32\thinspace\mathrm{m}$$ (about $$5\thinspace H$$) on the workbook\'s Inflow sheet (CSV = its rounding) |
| Friction velocity $$u_\ast$$ (m/s) | 0.06999 |
| Roughness length $$z_0$$ (mm) | 0.0265 |
| $$U_H$$, measured (m/s) | 1.3394 |
| Log-law error at H | -1.6 % |
| log law rms residual | 2.2 % |
| Note | derived during scoping, not published by AIJ; the boundary layer is unstably stratified, so a neutral log law is only a rough description |

{% include nomenclature.md %}

## Known data issues

- RS\_caseL.csv\'s temperature column is headed \'T(K)\' but holds DEGREES CELSIUS (12.85 .. 29.86); AF\_caseL.csv\'s \'T(K)\' is kelvin (283 .. 295). The API serves degrees Celsius for both.
- The published CSV is the workbook rounded to 2-4 decimals; the table is rebuilt from the workbook. Its \'tc\' column (temperature-concentration covariance, K ppm) and the workbook\'s \'Usc\' (the vector magnitude of the mean velocity) are not in the table.
- BD\_caseL.stl: the two bottom triangles ($$z = 0$$) of each of the 126 cubes (252 triangles) are wound inward; the served geometry.stl is the 126 boxes, outward.
- The readme\'s file list names AF\_caseK.csv and RS\_caseK.csv; the files are AF\_caseL.csv and RS\_caseL.csv.
- The readme\'s \'building surface temperature $$T_b$$ = 14.8 degC\' is the approach-flow air temperature at $$z = H$$; the workbook gives the building surface as 42.2 degC.
- The line source is 0.037 m x 1.2 m in the readme and data paper but a 0.04 m x 1.02 m patch in BD\_caseL.stl.
- The $$+y$$ and -y halves are not mirror images: the same point differs in $$U$$ by 26 %, in $$k$$ by 23 %, in C by 36 % on average, and $$U$$ is 0.11 m/s lower and T 1.3 K higher at $$+y$$ at $$z = 0.15\thinspace\mathrm{m}$$ (0.09 m above the roofs), so the tunnel flow has a lateral gradient; do not assume symmetry.
- The workbook carries no expanded uncertainty (the data paper mentions one for Case J only).
- AF\_caseL.csv lists the profile from the top ($$z = 0.32\thinspace\mathrm{m}$$) down and has no $$k$$.
- The measured tracer flux through the cross-sections equals q / 1.2 m to 0.86 .. 1.0 (street and cube-column lines averaged), which fixes q and the unit ppm; the cube-column line alone carries only 0.2 .. 0.4 of it.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/L.json`]({{ '/api/cases/L.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/L/points.json`]({{ '/api/cases/L/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/L/points.csv`]({{ '/api/cases/L/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/L/approach_flow.csv`]({{ '/api/cases/L/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/L/geometry.json`]({{ '/api/cases/L/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/L/geometry.stl`]({{ '/api/cases/L/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/L/validation.json`]({{ '/api/cases/L/validation.json' | relative_url }}) |

## Attribution

- Data collected by Ryuichiro Yoshie (Tokyo Polytechnic University) and Koudai Katada (Tokyo Polytechnic University).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15487637](https://doi.org/10.5281/zenodo.15487637)
- Citation requested: Yoshie, R., Nomura, K., Katada, K., Jiang, G. (2012). Non-isothermal large eddy simulation of pollutant and thermal dispersion in urban street canyons. 22nd National Symposium on Wind Engineering, 61-66 (in Japanese). <https://doi.org/10.14887/kazekosymp.22.0.61.0>; Jiang, G., Yoshie, R. (2018). Large-eddy simulation of flow and pollutant dispersion in a 3D urban street model located in an unstable boundary layer. Build. Environ. 142, 47-57. <https://doi.org/10.1016/j.buildenv.2018.06.015>
- Licence: CC BY 4.0

### Cite

**APA**

```text
Yoshie, R., Katada, K., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case L (ArraysCT): Wind Tunnel Experiment for Flow and Dispersion around Cube Arrays with a Line-source under Non-isothermal Conditions [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15487637
```

**BibTeX**

```bibtex
@misc{aijuwe_case_l,
  author    = "Yoshie, Ryuichiro and Katada, Koudai and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case L (ArraysCT): Wind Tunnel Experiment for Flow and Dispersion around Cube Arrays with a Line-source under Non-isothermal Conditions}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15487637",
  url       = "https://doi.org/10.5281/zenodo.15487637",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
