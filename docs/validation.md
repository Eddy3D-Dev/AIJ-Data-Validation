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

An engine that is not *scored* has no result for that case, and nothing here infers one.

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
- **OpenLB and FluidX3D** are scored on Cases A and B only. On C to E each cannot produce the measured quantity at the
  measured height, which was measured rather than assumed. [Reading]({{ '/validation/engines/' | relative_url }}).
- **The ML surrogate** predicts roughly half the tunnel's speed everywhere, and it does not respond to the wind
  direction. [Reading]({{ '/validation/ml-surrogate/' | relative_url }}).

Every case's scores, with the figures that show them, are on its own page: *Cases*, then the case, then
*Validation*. The same scores are served by the API as `/api/validation.json` and `/api/cases/{id}/validation.json`.
