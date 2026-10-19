Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts $$\lvert\mathbf{U_{\mathrm{mean}}}\rvert/U_{\mathrm{ref}}$$ at one height, 1.8 m, so the case is scaled ×144 to put its measurement plane there; the prediction is read at the tunnel's own sensor coordinates. How the surrogate is run is on the [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}) page.

{% include figure.html name="case-b-ml-agreement.png" alt="Measured vs predicted, ML surrogate, Case B" caption="<strong>Figure 5.</strong> Case B, measured vs predicted pedestrian-height speed, ML surrogate, with the 1:1 line and the factor-of-two band." %}

| Quantity | n | FB | FAC2 | R | hit rate | OpenFOAM, same points and quantity |
|---|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U_H$$, $$z = H/16$$ plane | 122 | +0.82 | 0.36 | −0.24 | 0.17 | FB +0.12, FAC2 0.84, R +0.87, hit rate 0.57 |

{% include nomenclature-scores.md %}

- FB is positive when the model is low. Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$: the prediction does not depend on the wind direction.
