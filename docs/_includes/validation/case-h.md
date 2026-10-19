**OpenFOAM 12.** An Eddy3D production run, realizable k-ε at numerics level 3 and 3000 iterations, at 1:100, with the probe at the tunnel's own coordinates.

- Velocities are divided by $$U_H$$, $$k$$ by $$U_H^2$$. Each side uses its own $$U_H$$: the tunnel's (3.226 m/s) for the measurement, the value the solve was driven with (3.23 m/s) for the model.
- Concentration: the cleaned table's $$C/c_0$$ ($$c_0$$ = 45.18 ppm) against the model's $$c^\ast = c\thinspace U_H H^2/Q$$, scored at the turbulent Schmidt numbers 0.3, 0.5 and 0.7 (the figure shows 0.5). One detection limit, $$10^{-3}$$ of the largest measured value.

## Measurement layout

{% include figure.html name="case-h-layout.png" alt="Measurement lines and planes, Case H" caption="<strong>Figure 1.</strong> Case H, measurement lines and planes: A vertical profiles, $$y/H = 0$$; B plane $$z/H = 0.0625$$; C plane $$z/H = 0.25$$; D plane $$z/H = 0.5$$. Positions in multiples of $$H$$." %}

## OpenFOAM 12: measured against modelled

{% include figure.html name="case-h-openfoam-agreement.png" alt="Measured vs modelled, Case H" caption="<strong>Figure 2.</strong> Case H, measured vs modelled $$U$$, $$W$$, $$k$$ and $$c^\ast$$, realizable k-ε; the dots take the colour of the line or plane they were measured on, as in Figure 1. The concentration panel shows the positive pairs only." %}

FB is positive when the model is low.

- **Flow.** R is 0.90, 0.94 and 0.89 for $$U$$, $$V$$ and $$W$$. $$W$$: FB +2.76 on a near-zero mean. $$k$$: R 0.11, FB +0.51.
- **Concentration.** R is 0.95 at every Schmidt number. FB is −0.83 at 0.5, and the modelled $$c^\ast$$ at the measured points peaks at 238 against a measured peak of 66. FB is −0.60, −0.83 and −0.93 for 0.3, 0.5 and 0.7; FAC2 falls from 0.69 to 0.59. [Case I]({{ '/cases/case-i/validation/' | relative_url }}) has a positive FB (model low) at 0.3 and a negative one at 0.7.

<details markdown="block">
<summary>Interpretation: Case H scores</summary>

- The mean flow is reproduced, $$k$$ is not. FAC2 on $$V$$ and $$W$$ is low by construction, because those components change sign (as in [Case A]({{ '/cases/case-a/validation/' | relative_url }})); $$W$$'s FB of +2.76 comes from a near-zero mean, so R and the hit rate carry the comparison. The pattern of the tunnel's turbulence at the measured points is not followed ($$k$$ R 0.11).
- The concentration is well correlated and over-predicted. A higher turbulent Schmidt number raises the modelled concentration further.
- Case I's bias changes sign with the Schmidt number; Case H over-predicts at all three, so the Schmidt number that suits one case does not suit the other.

</details>
