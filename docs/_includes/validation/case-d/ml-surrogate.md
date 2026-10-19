Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts $$\lvert\mathbf{U_{\mathrm{mean}}}\rvert/U_{\mathrm{ref}}$$ at one height, 1.8 m, so the case is scaled ×360 to put its measurement plane there; the prediction is read at the tunnel's own sensor coordinates. How the surrogate is run is on the [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}) page.

{% include figure.html name="case-d-ml-agreement.png" alt="Measured vs predicted, ML surrogate, Case D" caption="<strong>Figure 3.</strong> Case D, measured vs predicted pedestrian-height speed, ML surrogate, with the 1:1 line and the factor-of-two band." %}

| Quantity | n | FB | FAC2 | R | hit rate | OpenFOAM, same points and quantity |
|---|---|---|---|---|---|---|
| $$V_{\mathrm{s}}/U_H$$, thermistor, 3 WD | 198 | +0.67 | 0.34 | +0.33 | 0.17 | WD 0°, 22.5° and 45° (66 points each): $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ FB +0.21 / +0.05 / +0.09, FAC2 0.73 / 0.92 / 0.89, R +0.80 / +0.80 / +0.85 |
| $$\lvert\mathbf{U}\rvert/U_H$$, split fibre, WD 0 | 33 | +0.23 | 0.52 | +0.59 | 0.24 | FB +0.07, FAC2 0.76, R +0.85, hit rate 0.52 |

{% include nomenclature-scores.md %}

- FB is positive when the model is low. Reversing the wind changes the predicted field by at most $$1 \times 10^{-4}$$ $$U_{\mathrm{ref}}$$: the prediction does not depend on the wind direction.
