---
title: "Known data issues"
nav_order: 4
description: "What in the published AIJ data files changes a comparison if it is not accounted for, case by case."
redirect_from:
  - /gotchas/
---

# Known issues in the published data files

The cleaned tables served by the API apply the corrections (units, signs, frames); the raw files in the repository do not. Do not apply the corrections again to the published files.

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Across cases

{: .warning-title }
> Scalar vs vector mean speed
>
> Cases C, D and E, and the tunnel part of Case F, measure with thermistor anemometers: an *omnidirectional scalar*
> speed, not |mean velocity vector|. The data paper suggests comparing $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ as a conservative correction.
> Case D, over the 33 points both instruments share: thermistor / $$\lvert\mathbf{U}\rvert$$ = 1.34, as a ratio of means.
> Compare the bracket $$\lvert\mathbf{U}\rvert$$ ≤ $$V_{\mathrm{s}}$$ ≤ $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$.

{: .warning-title }
> Each case has its own frame and unit
>
> A–D and H–L: model-scale metres, $$+x$$ along the wind at $$\mathrm{WD} = 0$$.
> E, F, G and M: full-scale metres. E and F: $$+x$$ east, $$+y$$ north, meteorological (from-) directions. G: $$+x$$ downwind.
> M: $$+x$$ north, $$+y$$ west. In F and M the heights are above the tunnel floor, not the ground.
> `frame` in `/api/cases/{id}.json` states it.

{: .warning-title }
> Concentrations are normalised per case
>
> Cases H to M carry a tracer concentration `C` in ppm and `concentration_ratio` = $$C/c_0$$. $$c_0$$ is defined by each
> case's own release rate, reference speed and length (`normalisation` in `/api/cases/{id}.json`).
> Case K: the workbook and its data paper use different reference scales (a factor of 23.6 apart).
> Case M: field values are published in ppq and converted to ppm.
> Do not compare `concentration_ratio` across cases without reading each case's normalisation.

## Case A

- $$V$$ is positive toward $$+y$$ ($$V$$ = −2.893 m/s at (−0.040, −0.050, 0.010), just outside the $$y \lt 0$$ flank).
- Coordinates are metres; turbulence columns are rms values. The API serves variances ($$\overline{u'u'}$$ = $$u_{\mathrm{rms}}^2$$) so A and B share
  one column meaning.

## Case B

- $$V$$ is positive toward $$-y$$, the opposite of Case A. The API flips it (`lateral_sign_applied: -1`).
- Coordinates are millimetres (`x[mm]`); velocities are m/s. Read as metres, every probe lands 1000× too far out. The
  API serves metres (`coordinate_scale_applied: 0.001`).
- Geometry was taken from each case's own measurement-point drawing (`MP-z_case*.png`). Both buildings are centred on
  the origin; points are published on the $$y \le 0$$ half by the tunnel's symmetry convention.

<details markdown="block">
<summary>Data notes: Cases A and B, sign of V and geometry source</summary>

Just outside the windward side face the flow must deflect away from the centreline, toward $$-y$$ on the $$y \lt 0$$ flank.

- Case A: $$V$$ = **−2.893 m/s** at (−0.040, −0.050, 0.010), edge at $$y = -0.04$$.
- Case B: $$V$$ = **+3.630 m/s** at (−0.025, −0.110, 0.013), edge at $$y = -0.100$$.

Same flow feature, opposite sign, so Case B's $$V$$ is positive toward $$-y$$. Scored without the flip, Case B's $$V$$ gives
$$R = -0.910$$ against an $$R = +0.959$$ streamwise control on the same points, an anti-correlation no turbulence closure
produces.

The geometry was not inferred from the CSV extents.

</details>

## Case C

- The `CB` column is text (`0D`, `1D`, `2D`); a reader that parses every field as a number gets NaN for it. The header
  ends with a trailing comma (an empty 8th column).
- 1080 rows = 3 wind directions × 3 centre buildings × 120 points: nine configurations. In the 0D configuration the 25
  centre grid nodes are still absent although the ground there is free.
- The CSV and Figure 3 of the data paper disagree on the sense of the WD rotation. This release keeps the CSV frame:
  WD rotates the wind from $$+x$$ toward $$-y$$. $$\mathrm{WD} = 0$$ is not affected.
- 24 of the 120 points sit exactly on a building face plane ($$\lvert x\rvert = 0.30$$ or $$\lvert y\rvert = 0.30$$), in the gap between blocks.
- The 0.40 m pitch is read from the drawing and the paper (street = D); the point grid alone bounds it to (0.35, 0.40].
- Repeatability floor from the mirror-symmetric pairs: mean $$\lvert\Delta V_{\mathrm{s}}\rvert$$ 0.088–0.137 m/s (0.024–0.038 $$U_H$$).

<details markdown="block">
<summary>Data notes: Sense of the WD rotation</summary>

In the CSV's own frame the $$\mathrm{WD} = 45^\circ$$ field is mirror-symmetric about $$y = -x$$ to within the experiment's repeatability
(0.10–0.13 m/s) and not about $$y = +x$$ (0.5–0.8 m/s), so WD rotates the wind from $$+x$$ toward $$-y$$. Figure 3 of the data
paper draws the fan the other way. The question is invisible at $$\mathrm{WD} = 0$$.

The solved field settles it: scored in the CSV's sense, R against the tunnel is 0.83–0.91 at 22.5° and 45°; in the
figure's sense it falls to −0.33 … +0.03.

</details>

## Case D

- All the data lives in `LF_caseD.xls`, a BIFF8 workbook (xlrd 2.x reads it; openpyxl cannot). Coordinates are
  millimetres.
- The shipped `BD_caseD.stl` has 1572 facets, 576 of them duplicates, and all 83 roofs wound inward (signed volume
  0.011159 m³ against the true 0.021477 m³). The API's `geometry.stl` is rebuilt from the 83 shells' boxes: 996
  facets, watertight, volume 0.021477 m³.
- Unmeasured thermistor cells are `-` (null in the API). At $$\mathrm{WD} = 0$$ the 66 measured values are 33 exact mirror pairs.
- The data do not fix the rotation sense for 22.5° and 45° (the array is exactly y-mirror symmetric, so $$+\theta$$ and $$-\theta$$ give
  exact mirror fields). This release rotates $$+x$$ toward $$+y$$, following Figure 4 of the data paper. Solved Eddy3D fields
  score R 0.80 (22.5°) and 0.85 (45°) in that sense, 0.40 and 0.17 mirrored.
- All 78 points lie outside every block and inside the array; shifting the cloud by 12.5 mm (5 m full scale) in x or y
  puts two points inside a block.
- The Zenodo record ([10.5281/zenodo.15402668](https://doi.org/10.5281/zenodo.15402668)) also ships CSVs: unmeasured
  is −999.9 there, and `RS-S_caseD.csv`'s z header is the full-width character `ｚ`. They match the workbook to
  $$4 \times 10^{-16}$$; the repository mirrors them under `clean/sources/zenodo_caseD/`.
- `case-d-eddy3d-prior-comparison.xlsx` (kept in the folder) scores $$R = +0.096$$ against the thermistor; the cause is a
  frame or geometry error. Do not use it as a validation.

## Case E

- The velocity ratio is normalised by the inflow velocity at 15.9 m (the Niigata meteorological station height):
  $$U(15.9\text{ m})$$ = 0.504531 × $$U_R$$ = 3.935 m/s with $$U_R$$ = 7.8 m/s at $$Z_R$$ = 250 m. The reference is neither $$U_H$$ nor $$U_R$$.
- `case-e-eddy3d-prior-comparison.xlsx` (kept in the folder) divided by the wrong reference and is low by a factor of
  2.048.
- All 2560 published ratios are integer multiples of 0.0198204 (55 distinct levels): the data's own resolution is
  ±0.0099, 3.1 % of the median and about 10 % at the lowest points. A tolerance below one quantum (0.0198204) is below
  the data's resolution.
- The readme describes `AF_caseE.csv`, `RS_caseE.csv` and `BD_caseE.stl`; the case folder holds only the `.3dm`,
  `.ghx`, `.xls` and the MP drawing. The Zenodo files are mirrored under `clean/sources/zenodo_caseE/`:
  `RS_caseE.csv` is the workbook rounded to two decimals, and `BD_caseE.stl` is model scale (×250), not
  watertight (5,253 open edges), with point 50 at (−45.5, −45.0) 0.17 m inside one of its walls (2.06 m clear in
  the 3dm). Everything served here is extracted from the workbook and the 3dm.
- `case-e.3dm` is full-scale metres; `MP_caseE.png` is drawn at model scale (±0.8 m). Use layers `buildings` and
  `buildings_new_construction`; the map plate on the Japanese-named layer, the terrain plates and `probes` are not
  buildings. 1,563 of the 8,436 triangles (18.5 %) of its building meshes are wound against their neighbours; all are re-wound in the API's STLs.
- Do not take measurement coordinates from the `probes` layer: its spheres sit a median 2.31 m (max 21 m) from the
  workbook's points, which are authoritative.

<details markdown="block">
  <summary>Data notes: Case E geometry</summary>

- 546 of the 548 bodies of the after-construction mesh (543 of 545 before construction) have triangles wound against their neighbours; a body is a set of triangles joined through edges that exactly two triangles use.
- 475 of the 503 building shells (478 of 506 after construction) are wound inward in the 3dm. A viewer that culls back faces draws the reversed triangles of a shell wound partly inward as missing walls.
- Every building is now wound consistently (each edge is traversed once in each direction) with a positive volume: 545 closed bodies after construction, 542 before, the smallest 4.125 m³.
- One wall that two buildings share (4.27 m × 3 m, x 3.5 to 7.5 m, y −76.5 to −75 m) is modelled twice, once per building, with different diagonals, so the copies never joined their buildings. The 4 triangles of both copies are removed and the two buildings are one body.
- 11 edges where two separate buildings touch (15 before the wall is removed) are counted as `body_contacts`; each building still sees them as ordinary two-triangle edges, so a contact does not open a body.
- `geometry.json` reports `bodies`, `edges_boundary`, `body_contacts`, `inconsistent_triangles` and `min_body_volume`; `watertight` is true when every body is closed, consistently wound and positive in volume.

</details>

{% include known-issues-fm.md %}
