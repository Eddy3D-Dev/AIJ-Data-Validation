# clean/ — schema of the cleaned AIJ UWE release (Cases A–M)

Schema `2.0.0` (release `3.0.0`; schema 1.0.0 had 18 columns, 2.0.0 adds the 18 below the line, appended, so every old column keeps its position). Built by `clean/build.py` from the published Zenodo files; every
transform is listed in `build.log`, every validity check in `checks.json`, every source file with its
SHA-256 in `manifest.json`. **The headers carry no units.** Units live in `units.json` (and in each
Parquet file's schema metadata under the keys `units` and `column_meaning`).

## 1. One table, long format

`points.csv` / `points.parquet` hold every measured value of every case as one row per
*(case, configuration, instrument, point, wind direction)*. Per-case copies are `cases/<id>/points.*`
(identical rows, identical column order). The per-case CSV is what `scripts/aijdata.py` reads for the
site API (`clean/manifest.json` → `cases.<id>.files.points_csv`).

| column | type | unit | meaning |
|---|---|---|---|
| `case_id` | text | — | `A` … `M` |
| `config` | text | — | `default` (every case but C, E and F) · C: centre building `0D` / `1D` / `2D` · E: `bc` before / `ac` after construction · F: `default` (the 9 m tunnel plane and the field) and `h5` / `h20` (the tunnel's 5 m and 20 m planes) |
| `instrument` | text | — | `split_fibre` (hot-wire split-fibre probe: vector components) · `thermistor` (omnidirectional scalar speed) · and, for Cases F to M, `cup_anemometer`, `sonic_anemometer`, `ldv`, `hydrocarbon_analyser`, `sorbent_gc_ecd` (the section for each case says which) |
| `point_id` | int | — | the tunnel's own point number (`No.`); shared by every configuration and direction of a case |
| `wind_direction_deg` | float | deg | A–D and G–L: the AIJ turntable angle WD (0 = flow along $$+x$$; G–L have only 0). E and F: meteorological FROM-direction, clockwise from north (N = 0, E = 90). M: the direction the wind comes FROM in the case's frame ($$+x$$ north; 180° blows toward $$+x$$), a field run's own $$\mathrm{WD_R}$$. **Do not turn this into a vector yourself — read `flow_dir_x/y` from `directions.csv`.** |
| `wind_direction` | text | — | compass name (E and F; empty elsewhere) |
| `x` `y` `z` | float | m | case frame, section 2. Model-scale metres for A–D and H–L, FULL-scale metres for E, F, G and M |
| `U` `V` `W` | float | m/s | mean velocity along $$+x$$, $$+y$$, $$+z$$. **$$V$$ is positive toward $$+y$$ in every case** (B's published sign is flipped) |
| `uu` `vv` `ww` | float | m²/s² | velocity variances $$\overline{u'u'}$$ … (A publishes rms; squared here) |
| `k` | float | m²/s² | turbulent kinetic energy as published (= $$\tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ wherever all three exist — checked) |
| `Vs` | float | m/s | mean omnidirectional scalar speed from a thermistor. Never a vector magnitude |
| `velocity_ratio` | float | — | mean speed over the case's reference speed: E: $$V_{\mathrm{s}}/U_{\mathrm{ref}}$$, $$U_{\mathrm{ref}}$$ = approach-flow speed at $$z = 15.9\thinspace\mathrm{m}$$ full scale (3.935 m/s, section 5); F, G: see the case's `normalisation` in `manifest.json` |
| `campaign` | text | — | `wind_tunnel` (model scale) or `field` (a full-scale observation: F, G, M) |
| `run` | text | — | replicate label where the dataset publishes individual runs (M); empty elsewhere |
| `uv` `uw` `vw` | float | m²/s² | Reynolds shear stresses as published |
| `C` `c_rms` | float | ppm | mean and rms tracer-gas concentration as published |
| `concentration_ratio` | float | — | $$C/c_0$$, $$c_0 = \dfrac{q}{U_{\mathrm{ref}} L_{\mathrm{ref}}^2}$$ as the benchmark defines it for the case (`manifest.json`, `cases.<id>.normalisation`) |
| `T` `T_rms` | float | °C, K | mean air temperature and its rms (J, L) |
| `uc` `vc` `wc` | float | ppm·m/s | turbulent concentration fluxes |
| `uT` `vT` `wT` | float | K·m/s | turbulent heat fluxes |
| `velocity_ratio_sd` | float | — | standard deviation of `velocity_ratio` over the observations behind a field value (F) |
| `k_ratio` | float | — | $$k/U_{\mathrm{ref}}^2$$ where only normalised values are published (G) |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

Rules:

- **Not measured = NaN** (empty cell in CSV, null in Parquet). The sources' `-999.9`, `-` and blank
  cells all become NaN. A column a case never measures is NaN for that whole case.
- The key `(case_id, config, instrument, point_id, wind_direction_deg)` is unique. Case B's seven
  repeat measurements keep their own point numbers (README, B).
- Rows are sorted by `(config, instrument, wind_direction_deg, point_id)` within a case; cases in
  order A–M. Floats are written with `%.10g`; coordinates and variances are rounded to 1e-9.
- A *derived* quantity the source publishes beside measured ones is dropped, not carried: Case D's
  split-fibre "Vs" / "Scalar Vel." (= $$\sqrt{U^2+V^2+W^2}$$, checked to 1e-15) and "Vs/UH"; Case B's
  "1/4 power" fit column. Everything else published is here.

## 2. Frames — one per case

All five: right-handed, $$+z$$ up from the ground plane, origin on the ground. Lengths in metres.

| case | origin | $$+x$$ | $$+y$$ | scale of the coordinates | transform from the published files |
|---|---|---|---|---|---|
| A | building centre | streamwise at $$\mathrm{WD} = 0$$ | lateral; points on the $$y \le 0$$ half | model ($$b = 0.08\thinspace\mathrm{m}$$; no model:full ratio is stated) | none (metres as published); rms → variance |
| B | slab centre | streamwise | lateral; points on $$y \le 0$$ | model ($$H = 0.20\thinspace\mathrm{m}$$; ratio not stated) | $$x$$, $$y$$, $$z$$ **mm → m** (×0.001); **$$V \to -V$$** |
| C | array centre (= centre block centre) | streamwise at $$\mathrm{WD} = 0$$ | lateral | model ($$D = 0.20\thinspace\mathrm{m}$$; ratio not stated) | none; `CB` text → `config` |
| D | tower centre | streamwise at $$\mathrm{WD} = 0$$ | lateral | model, **1:400** ($$H = 0.25\thinspace\mathrm{m} = 100\thinspace\mathrm{m}$$) | none (Zenodo CSVs are in metres; the workbook's mm are cross-checked) |
| E | centre of the reproduced area | **east** | **north** | **full scale**, model 1:250 | none for points; official STL ×250 (it is model scale) |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

Why the sign flip on B: just outside the $$y \lt 0$$ flank the flow must deflect away from the centreline,
i.e. toward $$-y$$. Case A reads $$V$$ = −2.893 m/s there ((−0.040, −0.050, 0.010)); Case B reads
**+3.630** at the same place ((−0.025, −0.110, 0.0125)); Case D's split fibre reads +2.055 on its $$+y$$
flank. So B's published $$V$$ is positive toward $$-y$$ and is flipped so that $$V$$ is positive toward $$+y$$
everywhere (`checks.json`: `lateral_sign_*`). For a y-symmetric building "flip V" and "flip y" are
the same transform; $$V$$ is flipped so the coordinates stay the drawing's.

Why E keeps a geographic frame: the district is real, its points and its STL are published in
east/north coordinates, and its 16 directions are compass names. Having $$+x$$ along the wind is a property
of A–D and G–L only (E and F are geographic, M is $$+x$$ north).

### Wind direction → flow vector (`directions.csv`)

`directions.csv` has one row per `(case_id, config, instrument, wind_direction_deg)` with
`flow_dir_x`, `flow_dir_y` = the unit vector the mean wind **blows toward** in the case frame, the
row and measured counts, and `sense_basis` / `status` saying what fixes the rotation sense:

| case | flow_dir(WD) | how the sense is known |
|---|---|---|
| A, B | (1, 0) | definition |
| C | (cos WD, **−sin WD**) | measured from the data: the $$\mathrm{WD} = 45^\circ$$ field is mirror-symmetric about $$y = -x$$ (mean $$\lvert\Delta V_{\mathrm{s}}\rvert$$ 0.10–0.13 m/s, the experiment's repeatability) and not about $$y = +x$$ (0.52–0.80). Figure 3 of the data paper draws the opposite sense — QUESTIONS Q1 |
| D | (cos WD, **+sin WD**) for 22.5°, 45° | **corroborated by solved fields**: the array is exactly y-mirror symmetric, so the sense cannot be settled from the data; it is taken from Figure 4 of the data paper, and Eddy3D's solved fields score R 0.80 / 0.85 in this sense against 0.40 / 0.17 mirrored (22.5° / 45°) — QUESTIONS Q2 |
| E | (−sin WD, −cos WD) | definition: FROM-direction, $$+y$$ north (compass rose in `MP_caseE.png`); frame verified by all 80 points lying in open space and a 10° rotation control putting 26 inside the official STL's buildings |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

Note C and D disagree in sense (QUESTIONS Q1, Q2).

## 3. Approach flow (`approach_flow.csv` / `.parquet`)

One row per published height: `case_id, z, U, uu, vv, ww, k` in the same units as section 1.
A: 24 heights (rms squared); B: 12; C: 16 ($$U$$ and $$\overline{u'u'}$$ only); D: 13 ($$U$$ and $$k$$); E: 12 heights
de-normalised from `z/ZR, U/UR, k/UR²` with $$Z_R$$ = 250 m (1 m model), $$U_R$$ = 7.8 m/s, in full-scale
metres. `manifest.json → cases.<id>.inflow` carries the measured $$U_H$$, the log-law fit(s)
($$\kappa$$ = 0.41, least squares on the published points, window stated, residual and errors at the heights
that matter) and a power-law fit — reproduced in `build.py`, never typed in.

## 4. Geometry (`cases/<id>/geometry*.stl`, `geometry.json`)

ASCII STL, LF line endings, outward normals, **metres in the same frame as the points** (so the E
files are full-scale and ~400 m across). `geometry.json` lists each file, its provenance, triangle
count, bounding box, watertightness, and, for A–D and G–L, the axis-aligned boxes it is made of, so a
consumer need not parse an STL at all.

A **body** is a set of triangles joined through edges that exactly two triangles use. `stats.watertight` is true when every body
is closed (no boundary edge), consistently wound (every edge is traversed once in each direction) and has a positive volume.
`stats` also holds `bodies`, `edges_boundary`, `body_contacts` (edges that four triangles share where two separate bodies touch; they
do not open a body), `inconsistent_triangles` (the fewest triangles to reverse; 0 in every served file) and `min_body_volume`.
`scripts/check_geometry.py` re-derives all of it from the files.

| case | files | made from |
|---|---|---|
| A, B | `geometry.stl` | the readme's stated dimensions, centred (the MP drawings) |
| C | `geometry_0D/1D/2D.stl` | nine 0.20 m cubes on a 0.40 m pitch; the pitch is verified against the 120-point grid (the 49 absent nodes of the 13 × 13 lattice are exactly the nine footprints) and read from `MP-z-caseC.png` |
| D | `geometry.stl` | the 83 closed shells of the published `BD_caseD.stl`, each reduced to its box (the published file has 576 duplicate facets and every roof wound inward; the rebuild is watertight with the analytic volume 0.0214766 m³) |
| E | `geometry_ac.stl` | the official `BD_caseE.stl` scaled ×250 (after construction; 60,101 triangles; NOT watertight as published, 5,253 open edges) |
| E | `geometry_ac_3dm.stl`, `geometry_bc_3dm.stl` | Eddy3D-side reconstructions from `case-e.3dm` (layers `buildings` + `buildings_new_construction`); **the before-construction state has no published source** — provisional. 1,563 of 8,436 triangles (18.5 %) of the building meshes are wound against their neighbours and are re-wound; one wall that two buildings share (4 triangles) is removed; 545 closed bodies after construction, 542 before, 11 edges where two bodies touch |

## 5. Case E normalisation

All 2,560 published ratios are integer multiples of one quantum $$q$$ = 0.0198204 (55 distinct levels):
the sheet holds $$U/U_R$$ quantised at 0.01 and re-normalised by $$U_R/U_{\mathrm{ref}}$$, so
$$U_{\mathrm{ref}}$$ = 0.01 · $$U_R$$ / q = **3.935 m/s** at $$z = 15.9\thinspace\mathrm{m}$$. Log-interpolating the published profile at
15.9 m gives 3.973 m/s (+1 %); the data paper says "4.0 m/s". The data's own resolution is ±q/2 =
±0.0099 — 3 % of the median ratio and 10 % of the smallest (5 quanta). Zenodo's `RS_caseE.csv` is
the workbook rounded to 2 dp; this release carries the workbook's full values.

## 6. Provenance and determinism

`manifest.json → cases.<id>.provenance` lists every source file read, with SHA-256 and byte size.
Each entry has an `eol` field: `lf-normalised` means the hash and the size are those of the file with CRLF folded to LF
(text files under `raw/`: `.csv`, `.md`, `.txt`, `.json` and ASCII `.stl`; git stores them with LF, so a checkout on
Windows hashes the same), `as-is` means the file was hashed as stored (binary files, and the byte-exact mirrors under
`clean/sources/`, whose hashes equal their `SHA256SUMS.txt`).
For D and E the official Zenodo files the repository clone lacks were downloaded into
`clean/sources/zenodo_case{D,E}/` (checksums in `SHA256SUMS.txt` beside them); the clone's
workbooks are byte-identical in content to Zenodo's `LF_*.xls` and are used as cross-checks. Two
consecutive builds produce byte-identical files (49 outputs hashed), so a changed hash means a
changed input or a changed `build.py`.

## 7. Site API

`scripts/aijdata.py` reads `clean/manifest.json`, finds each case's `points_csv`, maps the columns
by name and serves them unchanged through `docs/api/cases/<id>/points.{json,csv}`
(`points_source` in each file says so). Column `case_id` is not named `case`, which
that adapter would read as the configuration.

## Cases F and M

The two cases that bring the schema-2.0.0 columns `campaign`, `run`, `C`, `c_rms`, `concentration_ratio`,
`velocity_ratio_sd` into use. Both are real sites measured in a wind tunnel and in the field, both are in
**full-scale metres**, both come from a legacy workbook as well as from the Zenodo CSVs. Modules:
`clean/case_f.py`, `clean/case_m.py`.

### Rows: what one row is

`instrument` takes three values beyond `split_fibre` and `thermistor`: `cup_anemometer` (F, field),
`hydrocarbon_analyser` (M, tunnel concentration) and `sorbent_gc_ecd` (M, field concentration: sorbent tubes read
by gas chromatography with an electron-capture detector). A row carries only what its instrument measured; the
rest is NaN.

| case | `campaign` | `instrument` | `config` | one row is | filled columns |
|---|---|---|---|---|---|
| F | `wind_tunnel` | `thermistor` | `default` (9 m plane), `h5`, `h20` | a point at one wind direction on one plane | `velocity_ratio` |
| F | `field` | `cup_anemometer` | `default` | a point at one wind direction, the year's mean | `velocity_ratio`, `velocity_ratio_sd` |
| M | `wind_tunnel` | `split_fibre` | `default` | a point at 180° | `U V W`, `uu vv ww`, `k` |
| M | `wind_tunnel` | `hydrocarbon_analyser` | `default` | a point at 175°, 180° or 185° | `C`, `c_rms`, `concentration_ratio` |
| M | `field` | `sorbent_gc_ecd` | `default` | a point in one of the 18 runs (`run` = "1" … "18") | `C`, `concentration_ratio` |

F's `config` is the tunnel plane's height above ground by the readme's rule (z − 10 m): 9 m is `default` because
it is the benchmark plane, complete at 13 points × 12 directions, and the plane the field values are compared with;
the 5 m and 20 m planes exist at some points only. M's wind direction in a field row is the run's mean direction
at the reference point (`WD_R`), which differs from run to run, so the row key stays unique. M's per-run
reference speed `U_R`, tracer flow `q` and `c0` have no column; they are in `manifest.json → cases.M.extra_measurements.field_runs`.

### Frames

| case | origin | $$+x$$ | $$+y$$ | scale of the coordinates | transform from the published files |
|---|---|---|---|---|---|
| F | centre of the reproduced district, on the tunnel floor | **east** | **north** | **full scale**, model 1:800 | tunnel $$x$$, $$y$$, $$z$$ × 800 (the field's are published in full scale); STL × 800 and re-wound outward |
| M | centre of the tunnel turntable, on the floor | **north** | **west** | **full scale**, model 1:600 | tunnel $$x$$, $$y$$, $$z$$ × 600 (the field uses the tunnel's 15 points); STL × 600 and re-wound outward |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

`z` is the height above the **tunnel floor**, not above the ground. F: the readme's rule is ground = z − 10 m
(planes at $$z = 15,\thinspace 19\text{ and }30\thinspace\mathrm{m}$$ are 5, 9 and 20 m above ground); the STL's terrain under the 13 points is at
$$z = 5\thinspace\mathrm{m}$$, so the rule and the STL disagree by 5 m (`QUESTIONS.md` QF4). M: the campus ground lies at $$z \approx 32\thinspace\mathrm{m}$$ and
every point is 3 m above the local ground (verified against the STL to ±0.06 m). Velocities and concentrations are
**not** scaled: $$U$$, $$V$$, $$W$$ are the tunnel's m/s, `C` the tunnel's ppm.

### Normalisations

- **F, `velocity_ratio`**: $$U/U_{\mathrm{ref}}$$, $$U_{\mathrm{ref}}$$ the approaching mean speed at 500 m (the boundary-layer height), full
  scale. The legacy workbook normalises by the roof anemometers instead (SMB, G.L.+237 m, for NW–NE; KDD,
  G.L.+187 m, for the other directions); the CSVs re-normalise it, and the factor is recovered from the data:
  CSV = workbook × 0.9397 (SMB sector) or × 0.9629 (KDD sector), to within [0.93947, 0.94000] and [0.96250, 0.96324].
  $$U_{\mathrm{ref}}$$ itself in m/s is 10 (data paper) or 10.65 (implied by the approach-flow profile): `QUESTIONS.md` QF8.
  `velocity_ratio_sd` is the standard deviation of the 10-minute means behind a field value; it moves in steps of
  f/100 = 0.0094 or 0.0096 because the workbook's S.D. is rounded to 0.01.
- **M, `concentration_ratio`**: $$C/c_0$$, $$c_0 = \dfrac{q}{U_R H_R^2}$$ (data paper 3.13.1). Tunnel: $$q$$ = $$2.5 \times 10^{-6}$$ m³/s,
  $$U_R$$ = 4.08 m/s, $$H_R$$ = 0.068 m, $$c_0$$ = **132.514 ppm** (the paper rounds to $$1.33 \times 10^{2}$$ ppm). Field: each run's own
  q and $$U_R$$ with $$H_R$$ = 41 m, $$c_0$$ = 1,444 … 7,379 ppq. Field concentrations are **parts per quadrillion** ($$10^{-15}$$) in
  the sources; `C` holds ppm, so `C_ppm = C_ppq × 10⁻⁹`.

### Wind direction → flow vector

| case | flow_dir(WD) | how the sense is known |
|---|---|---|
| F | (−sin WD, −cos WD) | compass FROM-direction, $$+y$$ north (`MP_caseF.png`); the readme does not define it. Supported by the reference-building choice and by upwind roughness: status `unverified` (`QUESTIONS.md` QF9), except at NNW, the one direction a solved Eddy3D field has decided (R 0.935 with the tunnel's NNW column against 0.077 with its SSE column): status `corroborated by a solved field` |
| M | (−cos WD, +sin WD) | measured: the plume's lateral centroid moves toward $$-y$$ as WD grows, in the tunnel (175° → 185°) and across the 18 field runs; the compass rose of `MP_caseM.png` (N at $$+x$$, W at $$+y$$) agrees |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

### Geometry

| case | file | made from |
|---|---|---|
| F | `geometry.stl` | the published `BD_caseF.stl` × 800 (it is model scale: 0.90625 m = 725 m), every triangle reversed (all 21,537 horizontal ground and roof facets faced down); one shell, open along the rim of the disc (812 boundary edges at $$z = 0$$) and closed here with a 1 m base slab (vertical walls down to $$z = -1\thinspace\mathrm{m}$$ and a bottom cap, 2,436 added triangles); 3 zero-area facets are removed and their neighbours split |
| M | `geometry.stl` | the published `BD_caseM.stl` × 600 (model scale: 1.8 m × 1.2 m = 1080 m × 720 m), every triangle reversed (3,118 of 3,152 horizontal facets faced down); one shell with 21 boundary and 7 non-manifold edges: the 7 slivers (0.45 m² together) hung on building roofs are removed and the rim of the panel is closed with a 1 m base slab (21 added triangles) |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

### Approach flow

F: the 18 published heights (10 … 400 m full scale), `uu` = $$u_{\mathrm{rms}}^2$$; no `vv`, `ww`, `k`. M: the workbook's 40
heights at $$x = -0.498\thinspace\mathrm{m}$$ model (−299 m full scale), $$z = 3\thinspace\ldots\thinspace 360\thinspace\mathrm{m}$$ full scale, `uu vv ww` = σ², `k` = half their sum. M's heights are above the
**empty tunnel floor**: at the profile station the model's taper is already 0.052 m high, above the 10 lowest heights.

## Cases G, H and I (a tree belt in the field, a floor source, a roof source)

Added with schema 2.0.0; the columns are the 36 of section 1, nothing new.

### Frames and transforms

| case | origin | $$+x$$ | $$+y$$ | scale of the coordinates | transform from the published files |
|---|---|---|---|---|---|
| G | leeward face of the tree belt on the ground, on the centre section | downwind (the belt is $$x \in \lbrack -2,\thinspace 0\rbrack\thinspace\mathrm{m}$$) | along the belt, every point on $$y = 0$$ | **full scale**: a field observation | none; $$U/U_H$$ and $$k/U_H^2$$ from the workbook |
| H | centre of the building's leeward face on the ground | streamwise (building $$x \in \lbrack -0.1,\thinspace 0\rbrack\thinspace\mathrm{m}$$) | lateral (building $$y \in \lbrack -0.05,\thinspace 0.05\rbrack\thinspace\mathrm{m}$$) | model (building 0.10 × 0.10 × 0.20 m; the source states no ratio) | ratios × $$u_H$$ = 3.226 m/s from the workbook; **$$V$$ × -1 for point numbers 1-220** |
| I | centre of the cube on the ground | streamwise (cube $$x,\thinspace y \in \lbrack -0.05,\thinspace 0.05\rbrack\thinspace\mathrm{m}$$) | lateral | model (cube 0.10 m; no ratio stated) | values from the workbook; **$$V$$ on the $$y = 0$$ plane → NaN** |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

All three have one wind direction, `wind_direction_deg` = 0, and one `directions.csv` row per instrument with `flow_dir` = (1, 0): measured
(recirculation behind the leeward face, downwash on the windward face, the source behind or on the building) for H and I, a definition
for G (`unverified`: the field wind's angle to the belt is not published).

### New `instrument` values

| value | case | what it is |
|---|---|---|
| `sonic_anemometer` | G | three-dimensional ultrasonic anemometer; the published quantity is the mean scalar speed |
| `split_fibre` | H | hot-wire split-fibre probe: $$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$ (as in A, B, D) |
| `ldv` | I | laser Doppler anemometer: $$U$$, $$V$$, $$W$$, $$k$$ |
| `hydrocarbon_analyser` | H, I | high-speed total hydrocarbon analyser: $$C$$, $$c_{\mathrm{rms}}$$ (H only), `concentration_ratio` |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

### Rows and point numbers

- **G**: 28 rows, `point_id` = the row order of `RS_caseG.csv` (the file has no numbers). `campaign` = `field`. Only `velocity_ratio` and `k_ratio` are filled.
- **H**: one row per (instrument, point) with `point_id` = the CSV's `No.` (1-876): 826 `split_fibre` rows and 826 `hydrocarbon_analyser` rows. The CSV's -999.9 marks the line a probe was not run on: concentration only at $$x = 0.38\thinspace\mathrm{m}$$ (50 points), velocity only at $$x = 0.40\thinspace\mathrm{m}$$ (50 points); none is inside the building. `uu`, `vv`, `ww` are (rms × $$u_H$$)².
- **I**: two point sets with no numbers, **stacked**: `ldv` rows numbered 1-91 and `hydrocarbon_analyser` rows 92-630, each in its CSV's row order, so a `point_id` names one location (17 locations have both; they stay two rows). Only $$k$$ is published, no variances.
- Locations measured twice keep one row each under their own number: H's $$y = 0$$, $$z = 0.1\thinspace\mathrm{m}$$ line (13 locations; exact copies once $$V$$'s sign is aligned), I's 13 ground-centreline concentration points (values up to 8.5 % apart).
- The tables carry the **legacy workbooks' values** at full precision, not the CSVs' (H: the CSV quantises two planes, see `QUESTIONS.md` QH2; I: 3 dp and 1 dp). The CSVs are cross-checked to their own rounding.

### Normalisations (`manifest.json → cases.<id>.normalisation`)

| case | `velocity_ratio` / U | `k_ratio` / k | `concentration_ratio` |
|---|---|---|---|
| G | $$U/U_H$$, $$U_H$$ = the mean speed at the tree height (7 m) during each period, from the approach flow's power law (0.22); no m/s anywhere | $$k/U_H^2$$ | - |
| H | $$U$$ in m/s = ratio × $$u_H$$, $$u_H$$ = 3.226 m/s (the approach flow at $$z = H$$; the readme says 3.23) | $$k$$ in m²/s² | $$C/c_0$$, $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ = 45.18 ppm (45.2 in the paper), $$q$$ = 5.83e-6 m³/s of pure ethylene |
| I | $$U$$ in m/s, $$U_H$$ = 1.7 m/s (the approach flow at $$z = H$$ is 1.697) | $$k$$ in m²/s² | $$C/c_0$$, $$c_0 = \dfrac{q}{U_H H^2}$$ = 39.22 ppm with q the **ethane** flow, 10 % of the 400 cc/min (the paper quotes the mixture's 6.67e-6 m³/s) |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

Case G's approach-flow table (`approach_flow.csv`) holds $$U/U_b$$ and $$k/U_b^2$$ ($$U_b$$ = $$U$$ at 9 m, a different day) in its `U` and `k` columns: **dimensionless
there**. Divide by $$U_H/U_b$$ = 0.946 for the table's normalisation. H's has 17 heights ($$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ = (rms × $$u_H$$)²; the profile's $$\overline{u'w'}$$ and $$\overline{u'v'}$$ are not
carried: the table has no column for them), I's 12 ($$k$$ only).

### Geometry

Box geometry, `geometry.stl` and its boxes in `geometry.json`: G the belt's 2 × 74 × 7 m envelope with the 1.2 m gap (a **porous canopy**, shading rate 81 %), H the 0.10 × 0.10 × 0.20 m building, I the 0.1 m cube. The sources are not part of the geometry; their position is in
`manifest.json → cases.<id>.extra_measurements.source`: H the 4 mm floor hole at (0.05, 0, 0), I the 6 mm roof outlet at (0, 0, 0.1).

## Cases J, K, L — frames, reference values, extra files

The three Tokyo Polytechnic University cases (J: 1:1:2 building, K: 9 x 9 cube array, L: 9 x 14 cube array (14 rows along x, 9 across y); K and L
with a tracer source on the floor, J and L in an unstably stratified boundary layer). One wind direction each
(`wind_direction_deg` = 0, flow toward $$+x$$, `directions.csv` status `settled`), one instrument (`split_fibre`: the
velocity probe; temperature was read with a cold wire and concentration with a hydrocarbon analyser beside it),
`campaign` = `wind_tunnel`, `config` = `default`.

| case | origin | $$+x$$ | $$+y$$ | scale | transform from the published files |
|---|---|---|---|---|---|
| J | centre of the building's leeward (downwind) wall, on the floor | streamwise; building $$x \in \lbrack -0.08,\thinspace 0\rbrack$$, source at $$x = +0.04$$ | lateral; building $$y \in \lbrack -0.04,\thinspace 0.04\rbrack$$; the $$z/H = 0.025$$ plane only on $$y \le 0$$ | model ($$b = 0.08\thinspace\mathrm{m}$$, $$H = 0.16\thinspace\mathrm{m}$$; ratio not stated) | none for $$x$$, $$y$$, $$z$$; T kelvin → °C |
| K | windward wall of the 4th row of the central column | streamwise; 9 rows from $$x = -0.36$$ | lateral; 9 columns centred on $$y = 0$$ (span ±0.51) | model ($$H = 0.06\thinspace\mathrm{m}$$; ratio not stated) | none (the workbook's millimetres → m); `point_id` = row order |
| L | windward wall of the 9th row (of 14) of the central column | streamwise; 14 rows from $$x = -0.96$$ | lateral; 9 columns centred on $$y = 0$$ (span ±0.51) | model ($$H = 0.06\thinspace\mathrm{m}$$; ratio not stated) | none (workbook mm → m); the CSV's `T(K)` is already °C |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

All three: right-handed, $$+z$$ up from the (model) floor, lengths in metres. $$V$$ is carried as published ($$+y$$ by the frame); in
J it is verified ($$V$$ < 0 beside the upstream half of the y < 0 flank, V > 0 in the wake), in K and L it is not
verifiable: a cross-flow offset of about 0.06 m/s is larger than the antisymmetric part (`checks.json`,
`lateral_velocity_is_an_offset_not_an_antisymmetric_field`).

**Precision.** The published `RS_case<X>.csv` of each is the legacy workbook (`LF_case<X>.xlsx`) rounded, checked cell
for cell (`csv_equals_workbook_*`). The table is built from the workbook, as Case E's is: J's CSV is the workbook's
non-dimensional values rounded to $$10^{-3}$$ ($$U$$, $$V$$, $$W$$) or $$10^{-4}$$ and then multiplied back by the reference scales, which puts the
heat fluxes on a grid of 0.0049 K·m/s and $$k$$ on 0.00021 m²/s²; K's CSV recomputes $$k$$ from the rounded rms values.
Variances `uu vv ww` are the square of the published rms (K, L) or the workbook's `<u′u′>` columns (J, where they
differ from the square of the rms by up to 3 % in single rows and reproduce $$k$$).

**Reference values** for `concentration_ratio = C / c0` (`manifest.json → cases.<id>.normalisation`):

| case | $$c_0$$ (ppm) | definition |
|---|---|---|
| J | 12.2832 | $$0.05\thinspace q/(U_H H^2)$$, $$q$$ = $$9.17 \cdot 10^{-6}$$ m³/s, $$U_H$$ = 1.4581 m/s, $$H = 0.16\thinspace\mathrm{m}$$: the 5 % ethylene fraction of the released gas is in it (the workbook's own cell). Without it $$c_0$$ would be 245.66 |
| K | 429.185 | $$q/(U_H H^2)$$, $$q$$ = $$3.6 \cdot 10^{-6}$$ m³/s, $$U_H$$ = 2.33 m/s, $$H = 0.06\thinspace\mathrm{m}$$, as the data paper defines it. The workbook normalises with $$H = 0.2\thinspace\mathrm{m}$$ and $$U_H$$ = 4.94009 m/s instead ($$C_0$$ = 18.218 ppm): multiply `concentration_ratio` by 23.558 to reproduce it (`QUESTIONS.md` QK1) |
| L | 1728.228 | $$c_{\mathrm{gas}}\thinspace q/(U_H H^2)$$, $$q$$ = $$8.33333 \cdot 10^{-6}$$ m³/s, $$U_H$$ = 1.339415 m/s, $$H = 0.06\thinspace\mathrm{m}$$ (the workbook's own cell) |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

**Temperature.** `T` is °C (the published files give kelvin in J, and a °C column headed K in L's RS file); `T_rms` and the
heat fluxes are differences (K, K·m/s). The workbook's reference scales: floor temperature, Δθ = $$\theta_f - \theta_H$$ (J: 45.8 °C and
33.6 K; L: 45.009 °C and 30.257 K).

**Not carried** (no column in schema 2.0.0): the mean scalar speed `<usc>` and its standard deviation of K's workbook
(never below $$\lvert\mathbf{U}\rvert$$), L's `Usc` ($$\lvert\mathbf{U}\rvert$$, derived) and `tc`, the temperature-concentration covariance $$\overline{\theta'c'}$$ (K·ppm), L's `tc`
column. The expanded uncertainty of J's workbook has no column either; it is summarised in
`manifest.json → cases.J.extra_measurements.expanded_uncertainty`.

**Extra files** (not part of the point table; listed in the manifest under `extra_measurements.extra_files`):

| file | columns (units) | what |
|---|---|---|
| `cases/J/surface_temperature.csv` | `x y z` (m), `T` (°C) | the building's surface temperature at 121 points (`BD-ST_caseJ.csv`, kelvin there): boundary data for a thermal CFD model |
| `cases/J/approach_flow_full.csv` | `x z` (m), `U V W` (m/s), `uu vv ww uv uw k` (m²/s²), `T` (°C), `T_rms` (K), `uT vT wT` (K·m/s) | the workbook's empty-tunnel profiles at $$x = -0.4,\thinspace 0\text{ and }+0.4\thinspace\mathrm{m}$$ (the published `AF_caseJ.csv` is the first) |
| `cases/K/approach_flow_full.csv` | `x z U V W uu vv ww uv uw k` | `AF_caseK.csv` with $$V$$, $$W$$, $$\overline{u'v'}$$, $$\overline{u'w'}$$ (it is Case H's file, row for row) |
| `cases/L/approach_flow_full.csv` | as J's | the workbook's `Inflow` sheet at $$x = -0.4\thinspace\mathrm{m}$$, ascending in z |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

`approach_flow.csv` of each case keeps the common columns (`z U uu vv ww k`); J, K and L publish the profile at one
streamwise station (J: $$x = -0.4\thinspace\mathrm{m}$$, K: −0.493 m, L: −0.4 m).

## Geometry of J, K, L

| case | files | made from |
|---|---|---|
| J | `geometry.stl` | the readme's stated dimensions: one box 0.08 × 0.08 × 0.16 m, leeward wall at the origin; 12 triangles, watertight |
| K | `geometry.stl` | 81 cubes of 0.06 m on a 0.12 m pitch (9 rows from $$x = -0.36$$, 9 columns centred on $$y = 0$$): generated, because no STL is published. The pitch is read from `MP-y_caseK.png` / `MP-z_caseK.png`; the 203 points bound it to 0.11 – 0.14 m (no point lies inside a cube only between them) and the source position ($$x = -0.15\thinspace\mathrm{m}$$, between rows 2 and 3) to 0.105 – 0.15 m. 972 triangles, watertight |
| L | `geometry.stl` | the 126 closed shells of the published `BD_caseL.stl` ('buildings' solid: 1,512 triangles, no open edge, no duplicates; the two bottom triangles of each cube are wound inward) reduced to their boxes, which equal the grid of 14 rows along x by 9 columns across y of 0.06 m cubes on a 0.12 m pitch to 1e-9. The 'line_source' solid (a flat patch 0.04 m × 1.02 m at $$x = -0.15\thinspace\mathrm{m}$$, $$z = 0$$) is not a building and is described in `geometry.json` / the frame, not served as a wall |

<!--nomenclature full-->

<details markdown="block">
  <summary>Nomenclature: symbols, columns and scores</summary>

**Geometry, reference scales and release**

- $$H$$, $$b$$, $$D$$ (m) — height of the building, cube, tower or tree belt; width of the building; edge of the cubes of Case C: the lengths the cases are drawn and normalised by
- $$U_H$$ (m/s) — reference speed: the mean approach-flow speed at the height $$H$$ (each Data page gives the value used)
- $$U_R$$, $$H_R$$, $$Z_R$$ (m/s, m) — reference speed and height of a workbook: Case E, $$U_R$$ at $$Z_R$$ = 250 m full scale (1 m in the model); Case M, $$U_R$$ and $$H_R$$ at the reference point of the tunnel and of each field run
- $$U_{\mathrm{ref}}$$, $$L_{\mathrm{ref}}$$ (m/s, m) — reference speed and length of a case's normalisation: $$U_H$$ and $$H$$ ($$U_R$$ and $$H_R$$ in Case M); for the velocity ratios the approach speed at 15.9 m (Case E) or at 500 m (Case F)
- $$U_b$$ (m/s) — Case G: mean approach-flow speed at 9 m, the normalisation of its approach-flow table
- $$q$$, $$c_{\mathrm{gas}}$$ (m³/s, ppm) — tracer release of the experiment: volume flow of the released gas, and its tracer content ($$10^6$$ ppm when pure); $$Q$$ is the source strength given to a solve
- $$R_b$$ (dimensionless) — bulk Richardson number of the heated-floor cases J and L (negative: unstable stratification)
- $$\mathrm{Re_H}$$, $$\mathrm{Re_D}$$ (dimensionless) — Reynolds numbers $$U_H H/\nu$$ and $$U_H D/\nu$$ ($$\nu$$: kinematic viscosity of air)
- $$u_\ast$$, $$z_0$$, $$\kappa$$ (m/s, mm, dimensionless) — friction velocity and roughness length of the log law fitted to the approach flow, and the von Kármán constant (0.41)
- $$\mathrm{WD}$$ (column `wind_direction_deg`; °) — wind direction (each frame says how it is counted); $$\mathrm{WD_R}$$ is the mean direction of a field run at its reference point (Case M)
- $$x$$, $$y$$, $$z$$ (columns `x`, `y`, `z`; m) — coordinates in the case's frame ($$+x$$, $$+y$$ and $$+z$$ are the positive directions; each Data page says which way $$+x$$ points), $$z$$ up from the floor of the tunnel or from the ground
- $$\mathrm{d}x$$ (m) — lattice spacing of the OpenLB and FluidX3D runs, in metres or as a fraction of $$H$$ ($$H/64$$)
- $$L_r$$ (m) — reattachment length behind the building, read from a wake line at ground level; reported as $$L_r/H$$

**Velocity and turbulence**

- $$U$$, $$V$$, $$W$$ (columns `U`, `V`, `W`; m/s) — mean velocity along $$+x$$, $$+y$$, $$+z$$; $$V$$ is positive toward $$+y$$ in every case
- $$\lvert\mathbf{U}\rvert$$ (m/s) — magnitude of the mean velocity vector, $$\sqrt{U^2+V^2+W^2}$$
- $$V_{\mathrm{s}}$$ (column `Vs`; m/s) — mean omnidirectional scalar speed of a thermistor (never a vector magnitude)
- $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$ (columns `uu`, `vv`, `ww`; m²/s²) — velocity variances (overbar: time average, prime: fluctuation about it)
- $$\overline{u'v'}$$, $$\overline{u'w'}$$, $$\overline{v'w'}$$ (columns `uv`, `uw`, `vw`; m²/s²) — Reynolds shear stresses
- $$k = \tfrac{1}{2}\left(\overline{u'u'}+\overline{v'v'}+\overline{w'w'}\right)$$ (column `k`; m²/s²) — turbulent kinetic energy
- $$U/U_{\mathrm{ref}}$$ (column `velocity_ratio`; dimensionless) — mean speed over the case's reference speed ($$V_{\mathrm{s}}/U_{\mathrm{ref}}$$ for a thermistor)
- $$\sigma_{U/U_{\mathrm{ref}}}$$ (column `velocity_ratio_sd`; dimensionless) — standard deviation of `velocity_ratio` over the observations behind a field value (Case F)
- $$k/U_{\mathrm{ref}}^2$$ (column `k_ratio`; dimensionless) — turbulent kinetic energy over the square of the reference speed, where only normalised values are published (Case G)

**Concentration and temperature**

- $$C$$ (column `C`; ppm) — mean tracer-gas concentration as published (volume fraction $$\times 10^6$$ of the released gas diluted in air)
- $$c_{\mathrm{rms}}$$ (column `c_rms`; ppm) — root mean square of the concentration fluctuation
- $$c_0$$ (ppm) — reference concentration, defined for each case on its Data page: $$c_0 = \dfrac{c_{\mathrm{gas}}\thinspace q}{U_H H^2}$$ ($$U_R H_R^2$$ in the denominator in Case M)
- $$c^\ast$$ (column `concentration_ratio`; dimensionless) — dimensionless concentration $$c^\ast = C/c_0$$; the value of a solve is $$c\thinspace U_H H^2/Q$$ for its mean concentration $$c$$ and its source strength $$Q$$
- $$\mathrm{Sc_t}$$ (dimensionless) — turbulent Schmidt number of a solve (0.3, 0.5 and 0.7)
- $$T$$, $$T_{\mathrm{rms}}$$ (columns `T`, `T_rms`; °C, K) — mean air temperature as published (Cases J and L) and the root mean square of its fluctuation
- $$\overline{u'c'}$$, $$\overline{v'c'}$$, $$\overline{w'c'}$$ (columns `uc`, `vc`, `wc`; ppm·m/s) — turbulent concentration fluxes
- $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ (columns `uT`, `vT`, `wT`; K·m/s) — turbulent heat fluxes ($$\theta'$$: the temperature fluctuation)
- $$\theta = \dfrac{T_f - T}{T_f - T_H}$$ (dimensionless) — floor-referenced temperature the solves of Cases J and L are scored on: 0 at the floor, 1 in the approach air at $$H$$; $$T_f$$ is the floor temperature and $$T_H$$ the temperature of the approach flow at $$H$$

**Scores**

- $$n$$ — number of pairs of a measured value $$o_i$$ and a modelled value $$p_i$$ at one point
- $$R$$ — Pearson correlation coefficient of the pairs
- $$\mathrm{FAC2}$$ — fraction of pairs with $$0.5 \le p_i/o_i \le 2$$
- $$\mathrm{FB}$$ — fractional bias $$2(\overline{o}-\overline{p})/(\overline{o}+\overline{p})$$, positive when the model is low
- $$\mathrm{HR}$$ (hit rate) — fraction of pairs with $$\lvert p_i-o_i\rvert/\lvert o_i\rvert \le \delta_{\mathrm{rel}}$$ or $$\lvert p_i-o_i\rvert \le \delta_{\mathrm{abs}}$$, where $$\delta_{\mathrm{rel}} = 0.25$$ and $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$ for a velocity component
- $$\mathrm{NMSE} = \dfrac{\overline{(o-p)^2}}{\overline{o}\thinspace \overline{p}}$$ — normalised mean square error
- $$\mathrm{NAD} = \dfrac{\overline{\lvert o-p\rvert}}{\overline{o}+\overline{p}}$$ — normalised absolute difference
- $$\mathrm{MG} = \exp\overline{(\ln o-\ln p)}$$ — geometric mean bias
- $$\mathrm{VG} = \exp\overline{(\ln o-\ln p)^2}$$ — geometric variance
- The ratio of $$\mathrm{FAC2}$$ keeps its sign, so a model of the other sign than the measurement is a miss; $$\mathrm{FB}$$, $$\mathrm{NMSE}$$ and $$\mathrm{NAD}$$ divide by the means, so they are undefined (shown as —) for a signed component unless the measured and the modelled mean are both positive
- VDI 3783-9 calls the hit rate $$q$$ and the tolerances $$D$$ and $$W$$; on this site those letters keep their other meanings ($$q$$ the tracer release rate, $$D$$ the block size of Case C, $$W$$ the vertical velocity)
- The detection limit of a concentration is one value per case, $$10^{-3}$$ of the largest measured value. It sets $$\delta_{\mathrm{abs}}$$ of the hit rate and the both-below rule of $$\mathrm{FAC2}$$, and floors the values in $$\mathrm{MG}$$ and $$\mathrm{VG}$$.
- The scores $$\mathrm{FB}$$, $$\mathrm{FAC2}$$, $$\mathrm{NMSE}$$, $$\mathrm{NAD}$$, $$\mathrm{MG}$$ and $$\mathrm{VG}$$ follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

**Quantities scored**

- $$U$$, $$V$$ and $$W$$ (mean velocity components) over $$U_H$$
- $$k$$ (turbulent kinetic energy) over $$U_H^2$$
- the speed $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2+2k}$$, against a thermistor's $$V_{\mathrm{s}}$$
- $$c^\ast = C/c_0$$ (dimensionless concentration) at turbulent Schmidt numbers $$\mathrm{Sc_t}$$ of 0.3, 0.5 and 0.7
- $$\theta$$ (floor-referenced temperature)

</details>

<!--/nomenclature-->

All model scale; no source states a model:full-scale ratio, so the case frame is the model one.
