---
title: "Validation"
nav_order: 3
has_children: true
description: "How Eddy3D's solvers score against the AIJ wind-tunnel data, case by case and engine by engine."
---

# Validation: Eddy3D against the tunnel

Each case is solved through Eddy3D's production case writer (`build-case → run → probe`), not a hand-built
OpenFOAM case, so what is validated is what a user gets. The probe sits at **exactly the tunnel's own
measurement coordinates**, so no interpolation enters the comparison. This page is the overview; the pages
under it hold the method, the reading of each case and each engine, and the figures.

{: .warning-title }
> Scored does not mean agrees
>
> *Scored* means a run exists and its scores are published here. How well it agrees is in the numbers and in
> their reading on the pages below. Anything not marked scored is not a claim.

## Every case and engine

{% include validation-matrix.md %}

Under each *scored* label, R and FAC2 are the range over that engine's headline scores for the case: velocity
components, k, wind directions, configurations. Negative controls (a flipped frame, a reversed wind, the building
removed) are left out of the range; they are on the case's own Validation page. Pearson **R** is the correlation
of measured and modelled values; **FAC2** is the fraction of points within a factor of two. The
[method]({{ '/validation/method/' | relative_url }}) defines every metric.

| Status | Meaning |
|---|---|
| <span class="label label-green status">scored</span> | A run exists and its scores are served. Whether it agrees is in the numbers. |
| <span class="label label-blue status">running</span> | The solve is in progress; no scores yet. |
| <span class="label label-yellow status">pending</span> | Not run yet. |
| <span class="label label-grey status">not comparable</span> | The engine cannot produce the measured quantity at the measured location: OpenLB at the resolution this hardware runs, FluidX3D without a ground wall function. The measurements behind each are on the [OpenLB and FluidX3D]({{ '/validation/engines/' | relative_url }}) page. |

An engine that is not *scored* has no result for that case, and nothing here infers one. A dash in the table means the engine does not apply to the case:
**UMF** is urbanMicroclimateFoam, an OpenFOAM 12 solver and Eddy3D's engine for the non-isothermal Cases J and L; the isothermal OpenFOAM 12 engine
was not run there. The API's engine ids are `openfoam12-realizableKE` (also `openfoam12-kEpsilon` and `openfoam12-kOmegaSST`, Case I only),
`umf-realizableKE` (also `umf-buoyantKEpsilon`, Case J only), `openlb`, `fluidx3d` and `ml-surrogate`.

## What the scores say

- **Cases A and B, OpenFOAM 12.** The streamwise field is right: R ≈ 0.96 in both cases, FAC2 0.82 and 0.70. k is
  under-predicted in both (FB ≈ +0.47, R ≈ 0.4). [Reading]({{ '/validation/cases-ab/' | relative_url }}).
- **Case C, OpenFOAM 12.** The pattern is right in every configuration (R 0.80 to 0.91, FAC2 0.85 to 0.98). The model
  is slow, worst at WD = 0 (FB +0.25 to +0.34), and where the deficit comes from is not settled.
  [Reading]({{ '/validation/case-c/' | relative_url }}).
- **Case D, OpenFOAM 12.** R is 0.80 to 0.85 on the thermistor plane at all three headings. Against the split-fibre
  |U|, the instrument that measures what RANS computes, the model is nearly unbiased (FB +0.07).
  [Reading]({{ '/validation/case-d/' | relative_url }}).
- **Case E, OpenFOAM 12, wind from SW.** The absolute ratios are low and the cause is not established. The change the
  construction makes (after − before) has R = 0.84. [Reading]({{ '/validation/case-e/' | relative_url }}).
- **Cases H and I, OpenFOAM 12.** Velocity is reproduced (R 0.90 to 1.00 for U), the tracer concentration is well
  correlated (R 0.92 to 0.95) and its bias depends on the turbulent Schmidt number. k is poor in Case H (R 0.11). Case I
  was also solved with standard k-ε and k-ω SST: the mean velocity does not tell the closures apart, k and the
  concentration do. [Reading]({{ '/validation/cases-hi/' | relative_url }}).
- **Cases G and K, OpenFOAM 12.** Case K reproduces the velocity pattern (U R 0.96) and the tracer pattern (R 0.95 at every Schmidt number), with the velocity
  and k low and the concentration high. Case G is a field case with an unknown leaf area density, so Eddy3D solved a drag sweep, published arm by arm: drag moves
  the level of the mean speed and not its pattern (R about 0.5), and k is not modelled by the trees. [Reading]({{ '/validation/cases-gk/' | relative_url }}).
- **Cases J and L, UMF.** Eddy3D's buoyant microclimate engine (urbanMicroclimateFoam) on the two heated-floor cases. Case J under two closures: the flow is
  reproduced in pattern (U R 0.92) and low in level, the recirculation is too long, the model is 3.5 K warmer, and the tracer's bias changes sign with the
  Schmidt number. Case L: U and temperature follow the tunnel (R 0.92 and 0.94), the street air is nearly stagnant in the model, and the tracer is high.
  [Reading]({{ '/validation/cases-jl/' | relative_url }}).
- **OpenLB and FluidX3D** are scored on Cases A and B only. On C to E each cannot produce the measured quantity at the
  measured height, which was measured rather than assumed. [Reading]({{ '/validation/engines/' | relative_url }}).
- **The ML surrogate** predicts roughly half the tunnel's speed everywhere, and it does not respond to the wind
  direction. It has been run on Cases A to E only. [Reading]({{ '/validation/ml-surrogate/' | relative_url }}).
- **Cases F and M have no validation run yet.** Eddy3D's fixtures for them are written and their solves
  are queued, so every engine is *pending* there; nothing on this site is a claim about them.

Every case's scores, with the figures that show them, are on its own page: *Cases*, then the case, then
*Validation*. The same scores are served by the API as `/api/validation.json` and `/api/cases/{id}/validation.json`.
