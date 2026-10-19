---
title: "ML surrogate"
parent: Validation
nav_order: 4
summary: "how the Wind Predictor is run on Cases A to E, and what its scores grade"
description: "Eddy3D's ML wind surrogate (Wind Predictor, Yel-2.0) against the tunnel data of Cases A to E."
---

# ML surrogate

The surrogate has been run on Cases A to E; its scores and figures are on each case's Validation page: [Case A]({{ '/cases/case-a/validation/' | relative_url }}), [Case B]({{ '/cases/case-b/validation/' | relative_url }}), [Case C]({{ '/cases/case-c/validation/' | relative_url }}), [Case D]({{ '/cases/case-d/validation/' | relative_url }}) and [Case E]({{ '/cases/case-e/validation/' | relative_url }}). It has not been run on Cases F to M.

Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts $$\lvert\mathbf{U_{\mathrm{mean}}}\rvert/U_{\mathrm{ref}}$$ at one height, 1.8 m. Each case is scaled so its measurement plane lands there (A ×180, B ×144, C ×90, D ×360, E ×0.9). Its buildings are rasterised onto the model's 504 × 504 lattice of 2 m cells with the shipped grid code, the prediction is read at the tunnel's own sensor coordinates, and $$U_{\mathrm{ref}}$$ is converted to $$U_H$$ with each case's approach-flow file. The metric code and settings are those of the OpenFOAM rows.

FB is positive when the model is low.

- FB is +0.23 to +1.07: the mean predicted speed is 0.79 to 0.30 of the mean measured speed.
- Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$ over all 254,016 cells, in every case.

<details markdown="block">
<summary>Interpretation: Wind direction and what the scores grade</summary>

- The network responds to spatial contrast in a channel and has no response to its level. On a lattice that fills the window the direction channels are constant planes; with the lattice cut at ±250 m the direction enters through the step at its edge, and the reversed wind then scores as well as the right one or better on A, B and D.
- The scores grade the geometry given to the model; the wind direction does not enter.

</details>
