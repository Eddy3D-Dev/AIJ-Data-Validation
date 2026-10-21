Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts $$\lvert\mathbf{U_{\mathrm{mean}}}\rvert/U_{\mathrm{ref}}$$ at one height, 1.8 m, so the case is scaled ×90 to put its measurement plane there; the prediction is read at the tunnel's own sensor coordinates. How the surrogate is run is on the [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}) page.

{% include figure.html name="case-c-ml-agreement.png" alt="Measured vs predicted, ML surrogate, Case C" caption="<strong>Figure 4.</strong> Case C, measured vs predicted pedestrian-height speed, ML surrogate, with the 1:1 line and the factor-of-two band." %}

| Quantity | n | FB | FAC2 | R | hit rate | OpenFOAM, same points and quantity |
|---|---|---|---|---|---|---|
| $$V_{\mathrm{s}}/U_H$$, 9 configurations | 1080 | +0.67 | 0.44 | +0.21 | 0.18 | $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$: FB +0.18, FAC2 0.93, R +0.87, hit rate 0.69 |

- FB is positive when the model is low. Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$: the prediction does not depend on the wind direction.
