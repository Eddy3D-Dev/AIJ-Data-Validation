---
title: "Data"
parent: "Case J"
grand_parent: "Cases"
nav_order: 1
has_children: false
generated: true
description: "Case J — 1:1:2 building, non-isothermal: configuration, frame and units, reference data, inflow and known data issues."
---

# Case J: reference data
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
| Building | 1:1:2 (width : depth : height) prism, $$b = 0.08\thinspace\mathrm{m}$$, $$H = 2b = 0.16\thinspace\mathrm{m}$$ |
| Width b (m) | 0.08 |
| Height H (m) | 0.16 |
| Reynolds number $$\mathrm{Re_H}$$ | 16,000 |
| $$U_H$$ (m/s) | 1.4581 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane $$y/H = 0$$, horizontal $$z/H = 0.025$$ (y \<= 0 side only), horizontal $$z/H = 0.25$$ |
| Points | 444 |
| stratification | unstable: heated floor 45.8 degC, air at $$z = H$$ 12.2 degC (difference 33.6 K), bulk Richardson number -0.086; building surface 22.0 .. 28.9 degC (mean 24.5 degC, 121 points in clean/cases/J/surface\_temperature.csv) |
| source | 5 mm floor outlet at (0.04, 0, 0), $$0.25\thinspace H$$ beyond the leeward wall; 5 % ethylene in air at 30.4 degC, 9.17e-6 m³/s |
| concentration normalisation | $$c_0 = \dfrac{0.05\thinspace q}{U_H H^2}$$ = 12.283 ppm (the workbook\'s value; the 5 % gas fraction is in it) |
| Instrument | split-fibre hot wire (velocity), cold wire (temperature), high-speed hydrocarbon analyser (concentration), 1000 Hz, 120 s per point |
| Wind tunnel | thermally stratified wind tunnel, Tokyo Polytechnic University (Atsugi); 1.2 m wide, 1.0 m high |
| Scale, note | model scale; the sources state no model:full scale ratio |

{% include nomenclature.md %}

## Frame and units

| Property | Definition |
|---|---|
| Origin | the building\'s leeward (downwind) wall centre on the ground; $$x = 0$$ is the leeward wall |
| x | $$+x$$ streamwise (the wind blows toward $$+x$$); the building spans $$x \in \lbrack -0.08,\thinspace 0\rbrack$$; the floor source is at $$x = +0.04$$ |
| y | $$+y$$ lateral; the building spans $$y \in \lbrack -0.04,\thinspace 0.04\rbrack$$; the $$z/H = 0.025$$ plane is measured on the y \<= 0 side only |
| z | $$+z$$ up; roof at $$z = 0.16$$; heated floor at $$z = 0$$ |
| Lateral sign applied | 1 |
| Coordinate scale applied | 1.0 |
| Unit of length | m (model scale) |
| Unit of velocity | m/s |
| Unit of variance | m²/s² |
| Unit of $$k$$ | m²/s² |
| Unit of concentration | ppm of the released ethylene |
| Unit of temperature | degC (T); K ($$T_{\mathrm{rms}}$$); heat fluxes K m/s |

{% include nomenclature.md %}

## Reference data

Source in this repository: [`raw/cases/case-j/RS_caseJ.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-j/RS_caseJ.csv) (approach flow: [`raw/cases/case-j/AF_caseJ.csv`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/raw/cases/case-j/AF_caseJ.csv)).

The cleaned table has **444 rows** over **444 distinct points**; columns `point_id`, `config`, `instrument`, `wind_direction_deg`, `x`, `y`, `z`, `U`, `V`, `W`, `uu`, `vv`, `ww`, `k`, `campaign`, `C`, `c_rms`, `concentration_ratio`, `T`, `T_rms`, `uT`, `vT`, `wT`.

| Configuration | Points |
|---|---|
| default, wind tunnel, split fibre, WD 0° | 444 |

## Columns

The columns of the cleaned table (`points.csv`, `points.json`), in order.

<details markdown="block">
  <summary>The 23 columns and what each holds</summary>

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
| `C` | $$C$$ | ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air) |
| `c_rms` | $$c_{\mathrm{rms}}$$ | ppm, rms of the concentration fluctuation |
| `concentration_ratio` | $$c^\ast$$ | $$C/c_0$$, $$c_0 = \dfrac{q}{U_{\mathrm{ref}} L_{\mathrm{ref}}^2}$$ as the benchmark defines it for the case (manifest cases.\<id\>.normalisation) |
| `T` | $$T$$ | degC, mean air temperature as published (Cases J, L) |
| `T_rms` | $$T_{\mathrm{rms}}$$ | K, rms of the temperature fluctuation |
| `uT` | $$\overline{u'\theta'}$$ | K m/s, turbulent heat flux \<u\'theta\'\> |
| `vT` | $$\overline{v'\theta'}$$ | K m/s, turbulent heat flux \<v\'theta\'\> |
| `wT` | $$\overline{w'\theta'}$$ | K m/s, turbulent heat flux \<w\'theta\'\> |

{% include nomenclature.md %}

</details>

## Inflow

| Property | Value |
|---|---|
| Method | least squares, $$\kappa$$ = 0.41, $$z = 0.02\thinspace\ldots\thinspace 2H$$ on AF\_caseJ.csv |
| Friction velocity $$u_\ast$$ (m/s) | 0.09369 |
| Roughness length $$z_0$$ (mm) | 0.3051 |
| $$U_H$$, measured (m/s) | 1.46 |
| Log-law error at H | -2.0 % |
| log law rms residual | 2.1 % |
| Note | derived during scoping, not published by AIJ; the boundary layer is unstably stratified, so a neutral log law is only a rough description |

{% include nomenclature.md %}

## Known data issues

- Temperature is in KELVIN in all three published CSVs; the API serves degrees Celsius (T) and kelvin differences ($$T_{\mathrm{rms}}$$, heat fluxes).
- The published CSV is the legacy workbook\'s non-dimensional values rounded to 3-4 decimals and scaled back; the table is rebuilt from the workbook. The CSV\'s heat fluxes sit on a 0.0049 K m/s grid and $$k$$ on 0.00021 m²/s².
- $$c_0$$ = 12.283 ppm includes the 5 % ethylene fraction of the released gas (workbook cell Co); $$q/(U_H H^2)$$ alone is 245.7 ppm. The data paper states no $$c_0$$ for Case J.
- RS\_caseJ.csv lists the location (-0.16, 0, 0.004) twice (No. 1 and 153, identical values): a score over the table counts that point twice.
- The workbook\'s $$\overline{u'^2}$$ is not always the square of its $$\sigma_u$$ (up to 3 % in single rows); the table uses the variances, which reproduce $$k$$.
- The workbook lists an expanded uncertainty beside every quantity (no column here; clean/manifest.json cases.J.extra\_measurements.expanded\_uncertainty). The mean concentration is below its own uncertainty (about 1 ppm) at 42 % of the rows, and 193 uncertainty cells of the w\'theta\' flux are an Excel fill series, not values.
- The empty-tunnel profile changes along the tunnel: $$U$$ at $$z = 0.019\thinspace H$$ is 0.33 $$U_H$$ at $$x/H = -2.5$$ (the published AF\_caseJ.csv), 0.58 at the building\'s own position. The workbook has all three stations (clean/cases/J/approach\_flow\_full.csv).
- The $$+y$$ and -y halves are not mirror images: over the 97 mirror pairs of the $$z/H = 0.25$$ plane $$U$$ at $$+y$$ is 11 % lower (means 0.558 and 0.629 $$U_H$$, R between the halves 0.955), so a y-symmetric model has a ceiling on this file.
- The readme\'s Reynolds number (43,000) is Case H\'s; $$U_H H/\nu$$ = 1.6e4 as the data paper states.
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ are not published at the points; $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ were not measured.

## API

| Resource | Endpoint |
|---|---|
| Case | [`/api/cases/J.json`]({{ '/api/cases/J.json' | relative_url }}) |
| Points (JSON) | [`/api/cases/J/points.json`]({{ '/api/cases/J/points.json' | relative_url }}) |
| Points (CSV) | [`/api/cases/J/points.csv`]({{ '/api/cases/J/points.csv' | relative_url }}) |
| Approach flow (CSV) | [`/api/cases/J/approach_flow.csv`]({{ '/api/cases/J/approach_flow.csv' | relative_url }}) |
| Geometry | [`/api/cases/J/geometry.json`]({{ '/api/cases/J/geometry.json' | relative_url }}) |
| Geometry (STL) | [`/api/cases/J/geometry.stl`]({{ '/api/cases/J/geometry.stl' | relative_url }}) |
| Validation | [`/api/cases/J/validation.json`]({{ '/api/cases/J/validation.json' | relative_url }}) |

## Attribution

- Data collected by Ryuichiro Yoshie (Tokyo Polytechnic University), Hideyuki Tanaka (Takenaka Corporation) and Tsuyoshi Kobayashi (Tokyo Polytechnic University).
- Edited and distributed by Yoshihide Tominaga (Niigata Institute of Technology), Hideki Kikumoto (The University of Tokyo) and Tsubasa Okaze (Institute of Science Tokyo).
- DOI: [10.5281/zenodo.15447887](https://doi.org/10.5281/zenodo.15447887)
- Citation requested: Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. <https://doi.org/10.1007/978-4-431-55912-2_9>
- Licence: CC BY 4.0

### Cite

**APA**

```text
Yoshie, R., Tanaka, H., Kobayashi, T., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case J (112CT): Wind Tunnel Experiment for Flow and Dispersion Around a 1:1:2 Shape Building Model under Non-isothermal Conditions [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15447887
```

**BibTeX**

```bibtex
@misc{aijuwe_case_j,
  author    = "Yoshie, Ryuichiro and Tanaka, Hideyuki and Kobayashi, Tsuyoshi and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case J (112CT): Wind Tunnel Experiment for Flow and Dispersion Around a 1:1:2 Shape Building Model under Non-isothermal Conditions}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15447887",
  url       = "https://doi.org/10.5281/zenodo.15447887",
  note      = "Data set"
}
```

API: see [About]({{ '/about/#cite' | relative_url }}).
