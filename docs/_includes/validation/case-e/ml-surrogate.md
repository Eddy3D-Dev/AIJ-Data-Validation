Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts $$\lvert\mathbf{U_{\mathrm{mean}}}\rvert/U_{\mathrm{ref}}$$ at one height, 1.8 m, so the case is scaled ×0.9 to put its measurement plane there; the prediction is read at the tunnel's own sensor coordinates. How the surrogate is run is on the [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}) page.

{% include figure.html name="case-e-ml-agreement.png" alt="Measured vs predicted, ML surrogate, Case E" caption="<strong>Figure 4.</strong> Case E, measured vs predicted pedestrian-height speed, ML surrogate, with the 1:1 line and the factor-of-two band." %}

| Quantity | n | FB | FAC2 | R | hit rate | OpenFOAM, same points and quantity |
|---|---|---|---|---|---|---|
| $$V_{\mathrm{s}}/U(15.9\text{ m})$$, 16 WD, before + after | 2560 | +1.00 | 0.22 | +0.43 | 0.08 | — |
| the same, SW only (both states) | 160 | +1.07 | 0.20 | +0.53 | 0.04 | $$\lvert\mathbf{U}\rvert$$: FB +0.31, FAC2 0.76, R +0.81, hit rate 0.36 |

- FB is positive when the model is low. Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$: the prediction does not depend on the wind direction.
