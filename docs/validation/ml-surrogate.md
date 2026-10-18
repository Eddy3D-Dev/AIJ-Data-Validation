---
title: "ML surrogate"
parent: Validation
nav_order: 10
summary: "the Wind Predictor against Cases A to E"
description: "Eddy3D's ML wind surrogate (Wind Predictor, Yel-2.0) against the tunnel data of Cases A to E."
---

# ML surrogate

The surrogate has been run on Cases A to E. It has not been run on Cases F to M.

{% include figure.html name="ml-surrogate-agreement.png" alt="Measured vs predicted, ML surrogate, Cases A–E" caption="<strong>Figure 1.</strong> Measured vs predicted, ML surrogate, Cases A–E." %}

Eddy3D's Wind Predictor (the public `Yel-2.0` network) predicts \|U_mean\|/U_ref at one height, 1.8 m. Each case is
scaled so its measurement plane lands there — A ×180, B ×144, C ×90, D ×360, E ×0.9 — its buildings are rasterised
onto the model's 504 × 504 lattice of 2 m cells with the shipped grid code, the prediction is read at the tunnel's
own sensor coordinates, and U_ref is converted to U_H with each case's approach-flow file. Same metric code and
settings as the OpenFOAM rows.

| case · quantity | n | FB | FAC2 | R | hit rate | OpenFOAM, same points and quantity |
|---|---|---|---|---|---|---|
| A · \|U\|/U_H, z = 0.01 m plane | 65 | +0.77 | 0.26 | −0.13 | 0.09 | FB +0.27, FAC2 0.85, R +0.90, hit rate 0.45 |
| B · \|U\|/U_H, z = H/16 plane | 122 | +0.82 | 0.36 | −0.24 | 0.17 | FB +0.12, FAC2 0.84, R +0.87, hit rate 0.57 |
| C · Vs/U_H, 9 configurations | 1080 | +0.67 | 0.44 | +0.21 | 0.18 | √(\|U\|²+2k): FB +0.18, FAC2 0.93, R +0.87, hit rate 0.69 |
| D · Vs/U_H, thermistor, 3 WD | 198 | +0.67 | 0.34 | +0.33 | 0.17 | WD 0°, 22.5° and 45° (66 points each): √(\|U\|²+2k) FB +0.21 / +0.05 / +0.09, FAC2 0.73 / 0.92 / 0.89, R +0.80 / +0.80 / +0.85 |
| D · \|U\|/U_H, split fibre, WD 0 | 33 | +0.23 | 0.52 | +0.59 | 0.24 | FB +0.07, FAC2 0.76, R +0.85, hit rate 0.52 |
| E · Vs/U(15.9 m), 16 WD, before + after | 2560 | +1.00 | 0.22 | +0.43 | 0.08 | — |
| E · the same, SW only (both states) | 160 | +1.07 | 0.20 | +0.53 | 0.04 | \|U\|: FB +0.31, FAC2 0.76, R +0.81, hit rate 0.36 |

**It predicts roughly half the tunnel's speed everywhere, and it does not respond to the wind direction.** Reversing
the wind changes the predicted field by at most 1 × 10⁻⁴ U_ref over all 254,016 cells, in every case: the network
responds to spatial contrast in a channel, never to its level, and on a lattice that fills the window the direction
channels are constant planes. Cut the lattice at ±250 m and the direction enters through the step at its edge — but
on A, B and D the reversed wind then scores as well as the right one or better. These numbers grade the geometry
the model was given, not a wind it was told.
