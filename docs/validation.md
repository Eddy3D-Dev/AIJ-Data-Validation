---
title: Validation
nav_order: 3
---

# Validation: Eddy3D vs the tunnel

**Status.** *Scored* means a run exists and its scores are on this page — not that it agrees; how well it agrees is
in the numbers and their reading. Anything not marked scored is not a claim; see "What is still running" below.

## Method

Each case is solved through Eddy3D's production case writer (`build-case → run → probe`), not a hand-built
OpenFOAM case, so what is validated is what a user gets. The probe sits at **exactly the tunnel's own measurement
coordinates**, so no interpolation enters the comparison.

- Cases C–E measure an omnidirectional *scalar* speed with thermistors, so the model is scored as √(\|U\|² + 2k) and
  as \|U\| — the two ends of the bracket the measurement has to fall in.
- The tunnel's model-scale geometry is solved at 1:100 (Cases A, B) with the tunnel's own velocities; the log-law
  inlet is fitted to each case's own approach-flow file over z = 0.02 … 2H (`u*`, `z₀` below), and the profile
  shape is scale-invariant for a log law, so U/U_H values carry over unchanged.
- Everything is normalised by U_H (k by U_H²), the benchmark's own convention.
- Metrics per quantity: Pearson **R**; **FAC2**, the fraction of points within a factor of two; **FB**, the fractional
  bias 2(ō − p̄)/(ō + p̄), positive when the model is low; and the **hit rate**, the fraction within D = 0.25 relative
  or W = 0.05 U_H absolute. NMSE, NAD, MG, VG are in the API's `validation.json`.
- Case B's lateral velocity is sign-corrected before scoring (see [Data gotchas]({{ '/gotchas/' | relative_url }})).
- The reattachment length L_r behind the building is read from a wake line at ground level.

## Cases A and B — does the model agree?

![Measured vs modelled, Cases A and B]({{ '/assets/aij_agreement.png' | relative_url }})

Measured against modelled for each quantity, with the 1:1 line and, where the quantity does not change sign, the
factor-of-two band.

| | A — U | A — V | A — W | A — k | B — U | B — V | B — W | B — k |
|---|---|---|---|---|---|---|---|---|
| **R** | +0.955 | +0.961 | +0.708 | +0.480 | +0.959 | +0.910 | +0.929 | +0.399 |
| **FAC2** | 0.817 | 0.349 | 0.398 | 0.667 | 0.701 | 0.281 | 0.536 | 0.562 |
| **FB** | +0.185 | −0.207 | −1.501 | +0.478 | +0.240 | +0.370 | +0.263 | +0.463 |
| **hit rate** | 0.586 | 0.892 | 0.801 | 0.177 | 0.562 | 0.612 | 0.808 | 0.223 |

Normalised by U_H throughout. Hit rate uses D = 0.25, W = 0.05 U_H.
Reattachment length behind the building: **L_r/H = 1.49** (Case A), **3.27** (Case B).

Reading these honestly:

- **The streamwise field is right** — R ≈ 0.96 in both cases, FAC2 0.82 / 0.70.
- **k is under-predicted in both** (FB ≈ +0.47, R ≈ 0.4), the familiar realizable k-ε behaviour and consistent with
  what Eddy3D already records for AIJ Case H.
- **FAC2 on V and W is low by construction, not by failure.** Those components change sign, so factor-of-two
  agreement is a harsh measure near zero; R and hit rate are the meaningful columns there. The flat row of model
  V ≈ 0 in Case B's panel is the symmetry plane: a RANS solution is symmetric, so V ≡ 0 at y = 0, while the tunnel
  measures small non-zero values.
- **Case A's W FB of −1.50 and its NMSE are artefacts of a near-zero mean** (mean measured W is ~0.01 m/s), not a
  blow-up. Read R = +0.71 instead.

## Cases A and B — where does it agree?

![Centre-plane profiles, Cases A and B]({{ '/assets/aij_profiles.png' | relative_url }})

Vertical profiles of U/U_H on the centre plane at the first three measured stations behind the building, offset
per station. The model follows the measured profile closely above roof height and in the recovering wake; the
near-ground deficit immediately behind the building is where the closure does least well.

## Case C — the 3 × 3 block array

All nine configurations (centre block 0D / 1D / 2D × WD 0°, 22.5°, 45°), solved at 1:100 on a cylindrical domain —
the tunnel's turntable: the array turns with WD, the domain does not — ~310,000 cells per centre-block height,
3000 iterations per direction, the 120 probes at exactly the tunnel's coordinates.

![Case C, measured vs modelled]({{ '/assets/aij_caseC_agreement.png' | relative_url }})

| centre block | WD | R | FAC2 | FB | hit rate | \|U\| alone: FB / R |
|---|---|---|---|---|---|---|
| 0D | 0° | +0.824 | 0.908 | +0.266 | 0.567 | +0.466 / +0.804 |
| 0D | 22.5° | +0.857 | 0.983 | +0.106 | 0.750 | +0.295 / +0.846 |
| 0D | 45° | +0.831 | 0.942 | +0.121 | 0.783 | +0.307 / +0.801 |
| 1D | 0° | +0.801 | 0.858 | +0.341 | 0.433 | +0.551 / +0.741 |
| 1D | 22.5° | +0.896 | 0.975 | +0.192 | 0.675 | +0.394 / +0.882 |
| 1D | 45° | +0.872 | 0.942 | +0.198 | 0.733 | +0.353 / +0.873 |
| 2D | 0° | +0.857 | 0.850 | +0.251 | 0.492 | +0.443 / +0.848 |
| 2D | 22.5° | +0.906 | 0.983 | +0.091 | 0.875 | +0.240 / +0.894 |
| 2D | 45° | +0.909 | 0.958 | +0.103 | 0.883 | +0.243 / +0.912 |

![Case C, where the model is slow or fast]({{ '/assets/aij_caseC_map.png' | relative_url }})

- **The pattern is right in every configuration** — R 0.80–0.91, FAC2 0.85–0.98.
- **The model is slow, worst at WD = 0** (FB +0.25 … +0.34, hit rate 0.43–0.57; at 22.5° and 45° FB +0.09 … +0.20,
  hit rate 0.68–0.88). The map puts the deficit in the streets running along the wind.
- **It is not the scalar-vs-vector question.** The tunnel reads above even √(\|U\|² + 2k) at 902 of the 1080 points
  (84 %); \|U\| alone is lower still.
- **Most of it arrives with the inflow.** The approach flow reaching the array is 0.83 of the tunnel's at the probe
  height (0.99 at z = D) and carries 0.46 of its k there. A 17 % slow approach is worth FB ≈ +0.19 by itself.
- **The frame is checked by the scores.** Scored with the paper figure's rotation sense (the y mirror) R falls to
  −0.33 … +0.03 at 22.5° and 45°; with upwind and downwind swapped to −0.41 … +0.14 in eight of nine configurations.
- An independent re-scoring from the probe files and the original `RS_caseC.csv` reproduces every number (largest
  difference 9 × 10⁻¹⁶).

## ML surrogate

![Measured vs predicted, ML surrogate, Cases A–E]({{ '/assets/aij_ml_agreement.png' | relative_url }})

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
| D · Vs/U_H, thermistor, 3 WD | 198 | +0.67 | 0.34 | +0.33 | 0.17 | solving |
| D · \|U\|/U_H, split fibre, WD 0 | 33 | +0.23 | 0.52 | +0.59 | 0.24 | solving |
| E · Vs/U(15.9 m), 16 WD, before + after | 2560 | +1.00 | 0.22 | +0.43 | 0.08 | solving |

**It predicts roughly half the tunnel's speed everywhere, and it does not respond to the wind direction.** Reversing
the wind changes the predicted field by at most 1 × 10⁻⁴ U_ref over all 254,016 cells, in every case: the network
responds to spatial contrast in a channel, never to its level, and on a lattice that fills the window the direction
channels are constant planes. Cut the lattice at ±250 m and the direction enters through the step at its edge — but
on A, B and D the reversed wind then scores as well as the right one or better. These numbers grade the geometry
the model was given, not a wind it was told.

## Inflow

Fitted to each case's own approach-flow file over z = 0.02 … 2H, rather than assumed:

| Case | u\* (m/s) | z₀ (mm) | U_H measured (m/s) | log-law error |
|---|---|---|---|---|
| A | 0.343 | 0.668 | 4.491 | +2.0 % |
| B | 0.399 | 0.882 | 5.133 | +2.9 % |

Cases C, D and E carry their own fitted profiles on their pages — and a caveat each: their tunnels' profiles are
closer to a power law than a log law, and C, D and E all score at a single near-ground height, which is where a
log-law inlet is least right. The fits are in `/api/cases/{id}.json` under `inflow_fit`.

## Reproducing the figures

`validation/plot_aij.py` (Cases A and B), `validation/plot_aij_caseC.py` and `validation/plot_aij_ml.py` (UltraPlot)
build the figures. The Eddy3D fixtures are `TestAijCaseAContainerE2E`, `TestAijCaseBContainerE2E`,
`TestAijCaseC{0D,1D,2D}ContainerE2E` and `Outdoor.ML.Tests/TestAijSurrogateE2E`. The scores they wrote are
snapshotted in `validation/results/` with the per-point pairs beside them, and served unchanged by
`/api/cases/{id}/validation.json`.

## What is still running

| | A | B | C | D | E |
|---|---|---|---|---|---|
| OpenFOAM 12, realizable k-ε | scored | scored | scored | solving | solving |
| OpenLB | running | running | pending | pending | pending |
| FluidX3D | running | running | pending | pending | pending |
| ML surrogate | scored | scored | scored | scored | scored |

Both lattice-Boltzmann engines meet the ground with a plain no-slip (bounce-back) wall and carry the roughness only
in the inlet profile. On an empty domain at the finest lattice FluidX3D fits on the GPU, the flow at Case A's lowest
plane arrives 42 % below the fitted log law. Cases C–E measure *only* in that layer, so whether either engine can be
scored on them is being measured on the A and B runs before anything is claimed.

Two things that shape the C/D/E validations, both measured on the data rather than assumed:

- **Scalar vs vector speed.** C, D and E measure with thermistor anemometers, which report a mean *omnidirectional
  scalar* speed; steady RANS gives the magnitude of the mean velocity, which is lower by construction. Case D is the
  only case where both instruments overlap: over its 33 shared points the thermistor reads 1.34× |U| (ratio of means),
  and √(|U|² + 2k) from the split-fibre data matches the thermistor to FB +0.058 where |U| alone gives +0.292. A
  Case C/D/E score is therefore reported at both ends of the bracket \|U\| ≤ Vs ≤ √(\|U\|² + 2k).
- **The inlet is a log law, the tunnels' profiles are not.** Fitted power-law exponents are 0.19 (C, D) and 0.16–0.20
  (E) against the papers' 0.28 / 0.25; a log-law fit misses the single measurement height by −4 … −11 % depending on
  the fitting window, and sets the inlet k 26–48 % below the tunnel's (Case D). These are declared systematics, and
  the first thing to quote if the scores come back worse than A and B.
