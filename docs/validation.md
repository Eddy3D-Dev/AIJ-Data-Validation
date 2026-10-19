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

## Every case and engine

{% include validation-matrix.md %}

{% include nomenclature-scores.md %}

R, FAC2: range over the engine's headline scores, negative controls excluded. The [method]({{ '/validation/method/' | relative_url }}) defines every metric.

| Status | Meaning |
|---|---|
| <span class="label label-green status">scored</span> | A validation run exists and its scores are in `cases/{id}/validation.json`. |
| <span class="label label-blue status">running</span> | The solve is in progress; no scores yet. |
| <span class="label label-yellow status">pending</span> | Not run yet. |
| <span class="label label-grey status">not comparable</span> | The engine cannot produce the measured quantity at the measured location: OpenLB at the resolution this hardware runs, FluidX3D without a ground wall function. The measurements behind each are on the [OpenLB and FluidX3D]({{ '/validation/engines/' | relative_url }}) page. |

- A dash in the matrix: the engine does not apply to the case.
- **OpenFOAM 12** on Cases J and L is urbanMicroclimateFoam (UMF), the OpenFOAM 12 solver Eddy3D uses for non-isothermal flow; the isothermal solver was not run on them.
- API engine ids: `openfoam12-realizableKE` (also `openfoam12-kEpsilon` and `openfoam12-kOmegaSST`, Case I only), `umf-realizableKE` (also `umf-buoyantKEpsilon`, Case J only), `openlb`, `fluidx3d` and `ml-surrogate`.
