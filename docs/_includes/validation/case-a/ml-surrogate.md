Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts $$\lvert\mathbf{U_{\mathrm{mean}}}\rvert/U_{\mathrm{ref}}$$ at one height, 1.8 m, so the case is scaled ×180 to put its measurement plane there; the prediction is read at the tunnel's own sensor coordinates. How the surrogate is run is on the [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}) page.

{% include figure.html name="case-a-ml-agreement.png" alt="Measured vs predicted, ML surrogate, Case A" caption="<strong>Figure 8.</strong> Case A, measured vs predicted pedestrian-height speed, ML surrogate, with the 1:1 line and the factor-of-two band." %}

| Quantity | n | FB | FAC2 | R | hit rate | OpenFOAM, same points and quantity |
|---|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U_H$$, $$z = 0.01\thinspace\mathrm{m}$$ plane | 65 | +0.77 | 0.26 | −0.13 | 0.09 | FB +0.27, FAC2 0.85, R +0.90, hit rate 0.45 |

- FB is positive when the model is low. Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$: the prediction does not depend on the wind direction.
