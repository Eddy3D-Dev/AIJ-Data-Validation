---
title: "Validation"
nav_order: 3
has_children: true
description: "How Eddy3D's solvers score against the AIJ measurements, case by case and engine by engine."
---

# Validation: Eddy3D against the measurements

Each case is solved through Eddy3D's production case writer (`build-case → run → probe`). The probe sits at the tunnel's own
measurement coordinates.

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
- **UMF** is urbanMicroclimateFoam, an OpenFOAM 12 solver and Eddy3D's engine for the non-isothermal Cases J and L. The isothermal OpenFOAM 12 engine was not run on them.
- API engine ids: `openfoam12-realizableKE` (also `openfoam12-kEpsilon` and `openfoam12-kOmegaSST`, Case I only), `umf-realizableKE` (also `umf-buoyantKEpsilon`, Case J only), `openlb`, `fluidx3d` and `ml-surrogate`.

## Headline scores

FB is positive when the model is low.

- **[Case A]({{ '/cases/case-a/validation/' | relative_url }}), OpenFOAM 12.** $$U$$: $$R = 0.96$$, FAC2 0.82. $$k$$: FB +0.48, $$R = 0.48$$.
- **[Case B]({{ '/cases/case-b/validation/' | relative_url }}), OpenFOAM 12.** $$U$$: $$R = 0.96$$, FAC2 0.70. $$k$$: FB +0.46, $$R = 0.40$$.
- **[Case C]({{ '/cases/case-c/validation/' | relative_url }}), OpenFOAM 12.** R 0.80 to 0.91 and FAC2 0.85 to 0.98 in every configuration. FB +0.25 to +0.34 at $$\mathrm{WD} = 0$$.
- **[Case D]({{ '/cases/case-d/validation/' | relative_url }}), OpenFOAM 12.** Thermistor plane: R 0.80 to 0.85 at all three headings. Split-fibre $$\lvert\mathbf{U}\rvert$$: FB +0.07.
- **[Case E]({{ '/cases/case-e/validation/' | relative_url }}), OpenFOAM 12, wind from SW.** $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$: FB +0.12 before and +0.23 after the construction. Change after − before: $$R = 0.84$$.
- **[Case F]({{ '/cases/case-f/validation/' | relative_url }}), OpenFOAM 12.** One steady solve, wind from NNW only, two vertical frames: $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ R 0.90 to 0.95 at the 9 m plane and over all 33 tunnel points, 0.87 to 0.89 for the field; FB +0.04 (literal frame) or +0.13 (agl frame) at the 9 m plane; R with the tunnel's NNW column 0.935 and with its SSE column 0.077 (agl frame 0.945 and 0.102).
- **[Case G]({{ '/cases/case-g/validation/' | relative_url }}), OpenFOAM 12.** Field data; the leaf area density and drag coefficient are not in the dataset, so the drag values are crowns of the Eddy3D vegetation library, one run per arm. Mean $$U/U_H$$ is 0.948 with no belt, 0.735, 0.613 and 0.554 with the three crowns, 0.478 measured; $$U$$ R +0.46 to +0.50 in the arms with trees. Eddy3D's trees have no canopy $$k$$ or ε source terms.
- **[Case H]({{ '/cases/case-h/validation/' | relative_url }}), OpenFOAM 12.** $$U$$: R 0.90. Tracer concentration: R 0.95, FB −0.60 to −0.93 (model high). $$k$$: R 0.11.
- **[Case I]({{ '/cases/case-i/validation/' | relative_url }}), OpenFOAM 12.** $$U$$: R 1.00. Tracer concentration: R 0.92 to 0.95; FB changes sign with the turbulent Schmidt number. Also solved with standard k-ε and k-ω SST: $$U$$ R 0.99 to 1.00 under all three; $$k$$ FAC2 0.912, 0.923 and 0.396 and $$c^\ast$$ R +0.955, +0.940 and +0.466 (standard k-ε, realizable k-ε, k-ω SST).
- **[Case J]({{ '/cases/case-j/validation/' | relative_url }}), UMF.** Two closures: $$U$$ R 0.92, FB +0.19 and +0.17; reattachment at $$z/H = 0.25$$ is $$1.35\thinspace H$$ against $$0.68\thinspace H$$ measured; temperature bias +3.46 K and +3.63 K (model warmer); tracer FB changes sign with the Schmidt number (+0.065, −0.162, −0.256 under realizable k-ε).
- **[Case K]({{ '/cases/case-k/validation/' | relative_url }}), OpenFOAM 12.** $$U$$ R 0.96; $$c^\ast$$ R 0.95 at every Schmidt number; $$U$$ and $$k$$ low (FB +0.59 and +1.20), $$c^\ast$$ high (FB −0.69 to −0.98).
- **[Case L]({{ '/cases/case-l/validation/' | relative_url }}), UMF.** $$U$$ R 0.92, $$\theta$$ R 0.94; mean $$U/U_H$$ in the streets below 30 mm 0.045 modelled and 0.297 measured; tracer FB −0.50 to −0.73.
- **[Case M]({{ '/cases/case-m/validation/' | relative_url }}), OpenFOAM 12.** One steady solve, tracer release over a campus, WD 180 only, three Schmidt numbers: $$c^\ast$$ R 0.20 to 0.41, FB +1.40 to +1.58.
- **OpenLB and FluidX3D** are scored on Cases A and B. On Cases C to E each cannot produce the measured quantity at the measured height ([measurements]({{ '/validation/engines/' | relative_url }})). Not run on Cases F to M.
- **ML surrogate.** Run on Cases A to E only. FB is +0.23 to +1.07: the mean predicted speed is 0.79 to 0.30 of the mean measured speed. Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$. [Scores]({{ '/validation/ml-surrogate/' | relative_url }}).

<details markdown="block">
<summary>Interpretation: Headline scores by case</summary>

- **Cases A and B.** The streamwise field is right. $$k$$ is under-predicted.
- **Case C.** The pattern is right in every configuration. The model is slow, worst at $$\mathrm{WD} = 0$$. Where the deficit comes from is not settled.
- **Case D.** Against the split-fibre $$\lvert\mathbf{U}\rvert$$, the instrument that measures what RANS computes, the model is nearly unbiased.
- **Case E.** The absolute ratios are low and the cause is not established.
- **Case F.** The pattern follows the tunnel and the field, and the level depends on the frame. The solved field correlates with the tunnel's NNW column and not with its SSE one, which corroborates the compass reading of the wind directions.
- **Case G.** Drag moves the level of the mean speed and not its pattern, and $$k$$ is not modelled by the trees.
- **Case H.** Velocity is reproduced, $$k$$ is not. The tracer is well correlated and high at every Schmidt number.
- **Case I.** Velocity is reproduced. The tracer's bias depends on the Schmidt number. The mean velocity does not tell the closures apart; $$k$$ and the concentration do.
- **Case J.** The flow is reproduced in pattern and low in level, the recirculation is too long, the model is warmer than the tunnel, and the tracer's bias changes sign with the Schmidt number.
- **Case K.** The velocity pattern and the tracer pattern are reproduced, with the velocity and $$k$$ low and the concentration high.
- **Case L.** $$U$$ and temperature follow the tunnel, the street air is nearly stagnant in the model, and the tracer is high.
- **Case M.** The tracer is under-predicted at every Schmidt number and the modelled plume is displaced sideways against the tunnel's.
- **ML surrogate.** The predicted field does not respond to the wind direction.

</details>
