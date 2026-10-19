The Shinjuku sub-centre of Tokyo: a 1978 high-rise district, thermistor speed in a 1:800 tunnel and a year of field cup anemometers. An Eddy3D production run solved on 2026-10-18, realizable k-ε at numerics level 3, **one steady solve** on one mesh for the wind from NNW only (2,143,488 cells, 2000 iterations). It stopped at the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was $$1.0 \times 10^{-3}$$ ($$U_z$$ $$2.6 \times 10^{-3}$$).

- Scored in the benchmark's own ratio, $$U/U(500\text{ m})$$. The tunnel's thermistor and the field's cup anemometer read a *scalar* speed, so the model is scored as $$\lvert\mathbf{U}\rvert$$ and as $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$; both are in the tables. The model is divided by **its own** approach speed at 500 m, 9.862 m/s (probed 1100 m upwind of the centre, 0.986 of the imposed 10 m/s); over the imposed 10 m/s the scores are in the files. The tunnel measured at 5, 9 and 20 m above ground at 13 points (7, 13 and 13 of them have a value for NNW) and the field at 13 points, 3 to 11 m up.
- **Two vertical frames.** The readme says z is measured from the tunnel floor and the ground is z − 10 m, but the STL's own ground under all 13 points is 5 m. *Literal* probes the model at the published z in the STL's frame, which is 10, 14 and 25 m above the STL's ground for the three planes; *agl* probes the STL's ground plus 5, 9 and 20 m. The files do not say which one the tunnel meant, so both are scored, as two runs of one engine (`configuration` literal and agl).

<details markdown="block">
<summary>Data notes: Scores here and Eddy3D's own</summary>

The tunnel's values are identical to the CSV's. The field scores differ in the third decimal because point 14's 16 published field values are shifted by one direction in the CSV and realigned with the workbook in the cleaned table (clean/QUESTIONS.md QF1).

</details>

### Measured against modelled

{% include figure.html name="case-f-openfoam-agreement.png" alt="Case F, measured vs modelled speed over U(500 m)" caption="<strong>Figure 2.</strong> Case F, wind from NNW: the tunnel's and the field's $$U/U(500\text{ m})$$ against the modelled $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ (filled) and $$\lvert\mathbf{U}\rvert$$ (hollow), in the published-z frame (top) and the STL-ground frame (bottom). The bars are the standard deviation of the field's 10-minute means. The dots take the colour of their group in Figure 1." %}

$$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ over $$U(500\text{ m})$$:

| Points | Frame | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| Tunnel, 9 m plane | literal | +0.935 | 1.000 | +0.036 | 0.846 | 13 |
| Tunnel, 9 m plane | agl | +0.945 | 1.000 | +0.126 | 0.769 | 13 |
| Tunnel, 5 m plane | literal | +0.995 | 1.000 | +0.127 | 1.000 | 7 |
| Tunnel, 5 m plane | agl | +0.918 | 1.000 | +0.128 | 0.571 | 7 |
| Tunnel, 20 m plane | literal | +0.796 | 0.923 | +0.071 | 0.769 | 13 |
| Tunnel, 20 m plane | agl | +0.807 | 1.000 | +0.208 | 0.462 | 13 |
| Tunnel, all points | literal | +0.912 | 0.970 | +0.067 | 0.848 | 33 |
| Tunnel, all points | agl | +0.898 | 1.000 | +0.165 | 0.606 | 33 |
| Field | literal | +0.873 | 1.000 | +0.027 | 0.769 | 13 |
| Field | agl | +0.889 | 1.000 | +0.147 | 0.692 | 13 |
{: .scores }

{% include nomenclature-scores.md %}

$$\lvert\mathbf{U}\rvert$$ alone:

| Points | Frame | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| Tunnel, 9 m plane | literal | +0.928 | 1.000 | +0.134 | 0.615 | 13 |
| Tunnel, 9 m plane | agl | +0.935 | 0.923 | +0.242 | 0.538 | 13 |
| Tunnel, 5 m plane | literal | +0.988 | 0.857 | +0.307 | 0.571 | 7 |
| Tunnel, 5 m plane | agl | +0.923 | 0.857 | +0.259 | 0.571 | 7 |
| Tunnel, 20 m plane | literal | +0.788 | 0.923 | +0.112 | 0.692 | 13 |
| Tunnel, 20 m plane | agl | +0.801 | 0.846 | +0.269 | 0.308 | 13 |
| Tunnel, all points | literal | +0.906 | 0.939 | +0.149 | 0.636 | 33 |
| Tunnel, all points | agl | +0.894 | 0.879 | +0.258 | 0.455 | 33 |
| Field | literal | +0.860 | 1.000 | +0.126 | 0.308 | 13 |
| Field | agl | +0.866 | 0.846 | +0.266 | 0.308 | 13 |
{: .scores }

{% include nomenclature-scores.md %}

Controls:

| Control | Frame | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| 9 m plane over the imposed $$U(500\text{ m})$$ | literal | +0.935 | 1.000 | +0.050 | 0.846 | 13 |
| 9 m plane over the imposed $$U(500\text{ m})$$ | agl | +0.945 | 1.000 | +0.139 | 0.692 | 13 |
| Tunnel's SSE column (opposite wind) | literal | +0.077 | 0.615 | +0.327 | 0.077 | 13 |
| Tunnel's SSE column (opposite wind) | agl | +0.102 | 0.385 | +0.413 | 0.000 | 13 |
| Tunnel's 9 m column as a model of the field | literal | +0.933 | 1.000 | −0.015 | 0.692 | 13 |
| Tunnel's 9 m column as a model of the field | agl | +0.933 | 1.000 | −0.015 | 0.692 | 13 |
{: .scores }

{% include nomenclature-scores.md %}

FB is positive when the model is low.

- **9 m plane and all points, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$.** At the 9 m plane R is 0.935 (literal) and 0.945 (agl) with FAC2 1.00; over all 33 tunnel points R is 0.912 and 0.898, FAC2 0.970 and 1.00. The 20 m plane has the lowest R (0.796 and 0.807); the 5 m plane (7 points) the highest in the literal frame (0.995) and 0.918 in the agl frame. The mean of the modelled scalar speed at the 9 m plane is 0.252 (literal) and 0.230 (agl) against 0.261 measured, FB +0.04 and +0.13; for $$\lvert\mathbf{U}\rvert$$ alone FB is +0.13 and +0.24, the model's mean 0.228 and 0.205.
- **Frames.** The published z sits 5 m higher above the STL's ground than the instrument heights. FB, literal against agl: +0.04 and +0.13 at the 9 m plane, +0.07 and +0.21 at the 20 m plane; R differs by at most 0.02 at those planes. Nothing in the files says which datum the tunnel meant. At the 4 m surface cells the lowest probes of the agl frame (the 7 points of the 5 m plane, 1.25 cells up, and the field's point at 3 m) sit in the first cell.
- **Point by point.** At the 9 m plane, literal frame, the model-to-tunnel ratio of $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ runs from 0.70 (point 8) to 1.51 (point 3): the model is faster than the tunnel at points 3, 5, 10 and 14 and slower at points 1, 2, 8, 9 and 13, within 5 % at points 6, 7, 11 and 15. In the agl frame the ratio runs from 0.65 (point 1) to 1.31 (point 3), slower at points 1, 2, 6, 8, 9 and 13 (0.65 to 0.80) and faster at points 3, 5, 10 and 14 (1.08 to 1.31). Over all 33 tunnel points one is outside a factor of two in the literal frame (FAC2 0.970), none in the agl frame. The plan is in Figure 3.
- **Field.** R is 0.873 and 0.889 and FAC2 1.00 for $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ ($$\lvert\mathbf{U}\rvert$$: R 0.860 and 0.866, FB +0.13 and +0.27). The standard deviation of the 10-minute means behind a field value is 0.075 to 0.15 of $$U(500\text{ m})$$, 0.20 to 0.78 of the value itself. The tunnel's own 9 m column scored as a model of the field gives R 0.933, FAC2 1.00, FB −0.015; the model's R against the field is 0.04 to 0.06 under it.
- **Opposite wind.** The solved field correlates R 0.935 with the tunnel's 9 m column for the wind from NNW and R 0.077 with its column for the opposite wind, SSE (agl frame 0.945 and 0.102). The cleaned release's direction table marks its NNW rows *corroborated by a solved field*; the other directions stay *unverified* until one is solved (clean/QUESTIONS.md QF9).

<details markdown="block">
<summary>Interpretation: Case F frames, field and wind direction</summary>

- The pattern follows the tunnel in both frames and the frame changes the level; the literal frame has the smaller bias at the 9 m and 20 m planes. The offset is the datum, which the files do not fix.
- At the lowest probes of the agl frame the point interpolation is pulled toward the wall's zero.
- A steady solve is one state for one direction; a field value averages a sector 22.5° wide over a year of strong winds.
- The tunnel's own 9 m column reaches R 0.933 as a model of the field, the level a model of the tunnel can be expected to reach.
- The compass sense is corroborated at this direction. A RANS solution knows no compass, so the correlation with the NNW column and the lack of it with the SSE one support reading the direction labels as the direction the wind comes from, which the cleaned release had marked unverified.

</details>

{% include figure.html name="case-f-openfoam-bias-map.png" alt="Case F, where the model is slow or fast" caption="<strong>Figure 3.</strong> Case F, wind from NNW: $$\log_2(\text{model}/\text{tunnel})$$ of $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ at the 13 points of the 9 m plane on the plan of the district, in the two vertical frames; the arrow is the wind." %}
