---
title: "Validation"
nav_order: 3
has_children: true
description: "How Eddy3D's solvers score against the AIJ measurements, case by case and engine by engine."
---

# Validation: Eddy3D against the measurements

Each case is solved through Eddy3D's production case writer (`build-case → run → probe`). The probe sits at the tunnel's own
measurement coordinates.

## Cases

Each case's Validation page has its measurement locations, every engine's results and a leaderboard of its runs.

- [Case A]({{ '/cases/case-a/validation/' | relative_url }}): 1:1:2 building
- [Case B]({{ '/cases/case-b/validation/' | relative_url }}): 1:4:4 slab
- [Case C]({{ '/cases/case-c/validation/' | relative_url }}): 3 × 3 block array
- [Case D]({{ '/cases/case-d/validation/' | relative_url }}): high-rise among city blocks
- [Case E]({{ '/cases/case-e/validation/' | relative_url }}): Niigata district
- [Case F]({{ '/cases/case-f/validation/' | relative_url }}): Shinjuku district
- [Case G]({{ '/cases/case-g/validation/' | relative_url }}): flow behind a tree belt
- [Case H]({{ '/cases/case-h/validation/' | relative_url }}): 1:1:2 building with a floor point source
- [Case I]({{ '/cases/case-i/validation/' | relative_url }}): cube with a roof point source
- [Case J]({{ '/cases/case-j/validation/' | relative_url }}): 1:1:2 building, non-isothermal
- [Case K]({{ '/cases/case-k/validation/' | relative_url }}): 9 x 9 cube array, point source
- [Case L]({{ '/cases/case-l/validation/' | relative_url }}): 9 x 14 cube array, line source, non-isothermal
- [Case M]({{ '/cases/case-m/validation/' | relative_url }}): TPU Atsugi campus

## Cases C and D by configuration

{% include figure.html name="cases-cd-scores.png" alt="Correlation and error against the wind tunnel for every configuration of Cases C and D, OpenFOAM and ML surrogate" caption="<strong>Figure 1.</strong> Cases C and D, one row per configuration: the correlation coefficient C.C. (higher is better) and the root-mean-square difference S.E. (lower is better) between the tunnel and each model over the points of the row. The AIJ gives no formula for S.E.; the RMS difference is this repository's reading. Speeds are over $$U_H$$ in Case D and over the approach speed at the measuring height ($$z = 0.02\thinspace\mathrm{m}$$) in Case C, as in the AIJ benchmark. Filled blue: OpenFOAM scalar speed $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ against the thermistor's $$V_{\mathrm{s}}$$; in the split-fibre row, $$\lvert\mathbf{U}\rvert$$ against the measured $$\lvert\mathbf{U}\rvert$$. Hollow blue, Case C: OpenFOAM $$\lvert\mathbf{U}\rvert$$ without the $$2k$$ term, the quantity of the AIJ table. Green: ML surrogate, $$\lvert\mathbf{U}\rvert$$. Grey: range of the CFD codes the AIJ ran on the row (steady RANS; four codes in Case C, five runs at 0° and three at 22.5° and 45°; three codes in Case D), from Table 3-1-3 and Figs. 3-2-10 to 3-2-16 of the AIJ benchmark book (2016). Rows: Case C, the centre block (0D absent, 1D, 2D) and the wind direction; Case D, the wind direction." %}

## Every case and engine

{% include validation-matrix.md %}

{% include nomenclature-scores.md %}

R, FAC2: range over the engine's headline scores, negative controls excluded. The [method]({{ '/validation/method/' | relative_url }}) defines every metric.

| Status | Meaning |
|---|---|
| <span class="label label-green status">scored</span> | A validation run exists and its scores are in `cases/{id}/validation.json`. |
| <span class="label label-blue status">running</span> | The solve is in progress; no scores yet. |
| <span class="label label-yellow status">pending</span> | Not run yet. |
| <span class="label label-grey status">not comparable</span> | The engine cannot produce the measured quantity at the measured location: OpenLB at 2 m on Cases C to E, where its empty-domain control misses the bar. The measurement behind it is on the [OpenLB and FluidX3D]({{ '/validation/engines/' | relative_url }}) page. |

- A dash in the matrix: the engine does not apply to the case.
- **OpenFOAM 12** on Cases J and L is urbanMicroclimateFoam (UMF), the OpenFOAM 12 solver Eddy3D uses for non-isothermal flow; the isothermal solver was not run on them.
- API engine ids: `openfoam12-realizableKE` (also `openfoam12-kEpsilon` and `openfoam12-kOmegaSST`, Case I only), `umf-realizableKE` (also `umf-buoyantKEpsilon`, Case J only), `openlb`, `fluidx3d` and `ml-surrogate`.
