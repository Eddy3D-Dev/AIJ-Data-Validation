# Open questions for the data collectors (Ilker / Patrick to forward)

Things the published files, readmes and the data paper (Kikumoto et al. 2026, JAR 9(1) e70083)
cannot settle, each with what was measured and what one line from the collector would close.
Contacts are in `manifest.json → cases.<id>.contact`. Numbers below are in `checks.json`.

## Q1 — Case C: which way does the turntable turn? (Nonomura)

In `RS_caseC.csv`'s own frame (+x = the WD = 0 flow, confirmed three ways on the data) the WD = 45°
field is mirror-symmetric about the line **y = −x**: mean |ΔVs| over the 57 mirror pairs is
0.108 / 0.103 / 0.130 m/s for 0D / 1D / 2D — the experiment's own repeatability floor — while the
mirror about y = +x gives 0.52 / 0.77 / 0.80 m/s. So in the CSV the wind rotates from +x **toward
−y** as WD grows. Figure 3 of the data paper draws the 0 / 22.5 / 45° arrows fanning toward **+y**.
The two differ by a sign of y, which is invisible at WD = 0.

This release keeps the CSV frame (`directions.csv`: flow_dir = (cos WD, −sin WD)) because the point
coordinates live in it. **Question:** is the y axis of `RS_caseC.csv` the one in Figure 3, or its
mirror? Equivalently: for WD = 45°, does the wind come from the (−x, +y) quadrant or the (−x, −y)
quadrant of the CSV coordinates?

*Update 2026-10-14 — a second, independent line of evidence.* Eddy3D solved all nine configurations
(OpenFOAM 12, realizable k-ε) and scored the 120 points both ways on the same solutions: in the CSV's
sense R = 0.83–0.91 at 22.5° and 45°; in Figure 3's sense (the y mirror) R = −0.33 … +0.03. A RANS
solution knows nothing about the CSV's convention, so the data's own symmetry and the physics now agree;
the question stays open only for the collector's word on Figure 3.

## Q2 — Case D: rotation sense for 22.5° and 45° (Tominaga)

The 83-block array is exactly symmetric under y → −y, so a wind at +θ and one at −θ give exact mirror
fields and **no measurement can distinguish them**; the 0° thermistor column is itself an exact
y-mirror (33 pairs with ΔVs = 0, i.e. half of it was measured and mirrored). The sense used here
(flow_dir = (cos WD, +sin WD), status `unverified`) is a reading of Figure 4 of the data paper, and
it is the OPPOSITE of what Case C's data show for Case C. The Zenodo readme (now in
`clean/sources/zenodo_caseD/`) does not state it either.

**Question:** at WD = 22.5° and 45°, is the wind turned from +x toward +y or toward −y, in the
coordinates of `RS-T_caseD.csv` / `MP_caseD.png`? (Also: which half of the 0° plane was actually
measured, +y or −y?)

*Update 2026-10-15 — the solved field decides 22.5°.* No measurement alone can, but a solution can: Eddy3D
solved the array at 22.5° (OpenFOAM 12, realizable k-ε, 3.6 million cells) and scored the 66 measured
points in this release's sense and in its y mirror on the same solution. In Figure 4's sense (+x toward
+y) R = 0.80, FAC2 0.92; mirrored R = 0.40, FAC2 0.74. A RANS solution knows nothing about the figure, so
22.5° is corroborated in Figure 4's sense (`directions.csv` says so); 45° stays unverified until it is
solved. The question stays open for the collector's word, and for 45°.

*Update 2026-10-16 — and 45°.* Solved the same way (3000 iterations, the same residual plateau as 0° and
22.5°): in Figure 4's sense R = 0.85, FAC2 0.89; mirrored R = 0.17, FAC2 0.70 — a wider margin than at 22.5°.
Both rotated headings are now corroborated in Figure 4's sense. The question stays open only for the
collector's own word, and for which half of the 0° plane was measured.

## Q3 — Case E: the sensor frame against the two geometries (Tominaga)

1. Point 50 at (−45.5, −45.0) m lies **0.17 m inside a building wall of the official `BD_caseE.stl`**
   (roof at 6.75 m) and 2.06 m clear of the nearest wall in `case-e.3dm`. The other 79 points
   are in open space in both files (median 4.9 m from the nearest vertex). The two files are
   different triangulations of the district (official: 227 shells, 60,101 triangles, 5,253 open
   edges, bbox ±198 m after ×250; the 3dm: 5,015 meshes, bbox −201.5…203 m). Which is the
   measured model, and is point 50 really in the street?
2. The official STL is **model scale** (z max 0.24 m = 60 m / 250) while the readme calls the
   coordinates "actual scale"; the ×250 is this release's inference from the 60 m high-rise. Please
   confirm, and whether a watertight STL exists.
3. The dataset publishes **only the after-construction geometry**. The before-construction state
   used here (`geometry_bc_3dm.stl`) is the 3dm's `buildings` layer with the three sites empty. Is
   that what stood in the tunnel for the "bc" runs, or were there earlier buildings on the sites?
4. `RS_caseE.csv` on Zenodo is the workbook rounded to 2 dp (max |Δ| 0.00497); the workbook's values
   are exact multiples of 0.0198204 (= U/UR at 0.01 resolution re-normalised by UR / U(15.9 m), which
   gives U(15.9 m) = 3.935 m/s; the paper says 4.0). Which U_ref was used, and is the workbook the
   authoritative precision?

## Q4 — Case B: lateral sign and the seven repeated points (Tominaga)

1. The published V appears positive toward −y: V = +3.630 m/s at (−25, −110, 12.5) mm, just outside
   the y = −100 mm flank where the flow must deflect away from the centreline. Case A (V = −2.893 at
   the equivalent point) and Case D (V = +2.055 on the +y flank) both read positive toward +y. This
   release flips B's V. Please confirm the sign convention of V in `RS_caseB.csv` (or whether the
   published points are on the +y half rather than the −y half of the drawing).
2. Seven locations appear twice with different values: the foot of each vertical-section profile
   (z = 12.5 mm, y = 0; points 12, 43, 56, 69, 82, 95, 108) and the horizontal-plane centreline
   (points 110, 147, 160, 173, 186, 199, 212). |ΔU| = 0.05–0.14 m/s (mean 0.105). Two runs? Which
   is canonical, or should both be kept (as here) as a repeatability estimate?

## Q5 — Case C: what reference speed did the legacy workbook use? (Nonomura)

`LF-caseC.xls` publishes velocity ratios "normalized by the inflow velocity at the same height".
Multiplying by U(0.02 m) = 2.434 m/s from `AF_caseC.csv` reproduces the CSV's Vs only to 0.3 %:
Vs / ratio spans 2.4145–2.4525 m/s across the 1,080 values, so the ratios seem to use a per-run
reference. Is that so, and are the CSV's 2-dp Vs values the raw measurements?

## Q6 — Case D: the split-fibre "Scalar Vel." column (Tominaga)

`RS-S_caseD.csv`'s `Vs` and the workbook's `Scalar Vel.` equal √(U²+V²+W²) to 1e-15 at all 33
points, so they are the vector magnitude, not a thermistor reading, and are dropped here. Is that
right? (The thermistor readings at the same 33 points are in `RS-T_caseD.csv`; their ratio to the
magnitude averages 1.34.)

## Q7 — Cases A, B, C: model scale (Ishihara / Tominaga / Nonomura)

No model:full-scale ratio is stated for A, B or C (D says 1:400, E 1:250). Eddy3D solves them at
1:100 with the tunnel velocities, which only matters for how results are labelled. Is a nominal
scale on record?

## Q8 — Case C: data paper Table 2 vs the CSV point numbering (Nonomura)

The readme lists 1, 2, 3, 34, 35, 36, 37, 46, 55, 100, 101, 102 as missing point numbers and the CSV
agrees (4…132 with those gaps). Were points 1–3 and the nine interior gaps never measured, or
measured and withheld (e.g. inside buildings for one configuration)?

## Cases G, H and I

Numbered per case (QG, QH, QI) so that the notes of this release's cleaning of Cases G, H and I stay together. What each check measured
is in `checks.json` (the check names are given). Contacts: G and I Tominaga, H Yoshie (`manifest.json → cases.<id>.contact`).

### QG1 — Case G: which heights were measured behind the belt? (Kurotani, Kiyota)

`readme_caseG.md` lists the heights of the measurement behind the tree belt as 1.5, 3.0, 6.0 and 9.0 m, the same as the approach flow's.
`RS_caseG.csv`, `LF_caseG.xls`, `MP-y_caseG.png` and section 3.7 of the data paper all have 1.5, 3, 4.5 and 6 m (check
`heights_are_1.5_3_4.5_6_as_the_paper_and_the_drawing_say`). This release follows the four sources that agree. **Question:** is 4.5 m
the fourth anemometer's height on the movable tower, and was nothing measured at 9 m behind the belt?

### QG2 — Case G: the turbulence of the approach flow against the lee (Kurotani, Kiyota)

`AF_caseG.csv` gives k/Ub² = 0.20-0.28 (120 min, 28 Dec 2000, four heights up to 9 m). Converted to the table's normalisation
(k/UH², UH/Ub = 0.946) that is 0.26-0.31 at 1.5-6 m. Behind the belt, five tree heights downwind (x = 35 m), `RS_caseG.csv` has k/UH²
= 0.040, 0.043, 0.054 and 0.072: 3 to 8 times lower at every height, although a windbreak's wake should not be quieter than the wind
it breaks (check `far_lee_turbulence_recovers_to_at_least_half_the_approach_flow`, a documented warning). The two records are two
days apart (28 and 26 Dec 2000) and 120 against 10 minutes. **Question:** are the two k comparable (same definition: all three
components? same detrending and averaging time?), or should the approach profile not be used to set a CFD inlet's turbulence?
Also, `Uxyz` is called 'mean scalar velocity': is it |mean vector| or the mean of the instantaneous speed?

### QG3 — Case G: the wind direction and UH (Kurotani, Kiyota)

The readme says each line is normalised by the mean speed at 7 m "during the measurement period"; no value in m/s, no wind direction
and no angle to the belt's normal is published, and the measurement lines are one-dimensional (y = 0). **Question:** what were UH
(seven lines) and the wind direction relative to the belt's normal? This release states the direction as `unverified` in
`directions.csv`.

### QG4 — Case G: an absolute Ub, and the canopy (Kurotani, Kiyota)

The workbook's `Geometry` sheet carries the Guidebook's inflow note: `U(z) = Ub (z/Hb)^0.22`, `K = 3.02 [m2/s2]`. If K is the k at 9 m,
Ub = sqrt(3.02 / 0.20) = 3.89 m/s (check `workbook_inflow_K_is_3.02_and_implies_Ub_3.9_ms`); this is derived here, not published.
**Question:** is that the intended reading? And: the data paper gives a shading rate of 81 % after pruning; is a leaf-area-density or a
drag-coefficient profile of the trimmed belt on record for canopy models?

### QH1 — Case H: the sign of V on the vertical plane (Yoshie)

At the 40 points the `y=0H` sheet shares with the horizontal-plane sheets, U, W, k and C agree to the last digit and **V has the
opposite sign** (0.00206 against -0.00206; check `vertical_plane_V_is_the_exact_negative_of_the_horizontal_planes_V_at_the_shared_points`,
`max |V1 + V2| = 0`). The horizontal planes' V has the sign of y upwind of the building (flow diverging around it: check
`lateral_sign_V_positive_toward_plus_y`) and is continuous with its neighbours at y = +/-25 mm (r = +0.66; the vertical plane's is
-0.66, 14 points). This release multiplies the 207 velocity rows of point numbers 1-220 by -1, so V is positive toward +y everywhere.
**Question:** is V on the vertical plane (`y=0H`, `RS_caseH.csv` point numbers 1-220) positive toward -y?

### QH2 — Case H: which file is the data? (Yoshie)

1. On the z/H = 1/2 and 1/4 planes (and in the approach profile) `RS_caseH.csv`'s U, V, W are the workbook's ratios rounded to 0.01 and then
   multiplied by uH = 3.226 m/s, a 0.032 m/s grid (check `csv_velocity_on_the_z_0.5H_and_z_0.25H_planes_is_the_ratio_rounded_to_0.01_then_scaled`:
   632 values differ from the exact ones by more than the 2 dp rounding, by up to 0.021 m/s); on the other two planes the CSV is the
   exact ratio x uH to 2 dp. This release takes the workbook. Is the workbook the authoritative precision?
2. The y = 0, z = 0.1 m line (13 locations with velocity, 13 with concentration) is in two sheets and appears twice in the CSV (point
   numbers 18 & 221, 31 & 231, ...), identical once V's sign is aligned: one record or two runs? The CSV drops the same duplicate
   on the 1/4 and 1/16 planes (29 workbook rows) but keeps it on the 1/2 plane.
3. The workbook's z/H = 1/16 sheet labels 19 concentration-only rows x = 400 mm; the CSV, and every other plane, put the
   concentration line at x = 380 mm and the velocity line at x = 400 mm. A labelling slip in the workbook (read as 380 here)? Why are the
   two lines 20 mm apart?

### QH3 — Case H: the concentration baseline, uH and c0 (Yoshie)

Upwind of the building, where the true concentration is zero, the analyser reads +/-0.1 ppm (median |c| 0.12, mean +0.067) and 97 of 826
values are negative, down to -0.83 ppm (check `upwind_concentration_is_the_analyser_offset_not_tracer`). **Question:** is the baseline
subtracted, and what detection limit or floor do you recommend for geometric statistics (MG, VG)? Also: the workbook's `<c>/Co`
column divides by 45.1773 ppm, its parameter sheet says c0 = 45.1798 ppm (uH = 3.226) and the paper 45.2: which c0 is intended (the
difference is 0.006 %)? And the workbook's `inflow` sheet labels its z column `z(mm)` but holds metres.

### QI1 — Case I: the release rate (Kondo, Mutou, Hori)

The paper says "10 % ethane was released at 6.67e-6 m3/s" and c0 = q/(UH H²) = 39.2 ppm. With q = 6.67e-6 m³/s, c0 would be 392 ppm;
39.2 ppm needs the ethane flow, 10 % of 400 cc/min = 6.67e-7 m³/s (check `c0_is_the_ethane_flow_over_UH_H2`; the workbook's 39.2235
is 666.8/17). **Question:** is 6.67e-6 m³/s the total (mixture) flow and 6.67e-7 m³/s the ethane flow, as this release reads it?

### QI2 — Case I: what was measured on the y = 0 plane? (Kondo, Mutou)

V at the 53 y = 0 wind points is 1e-9 ... 4e-6 m/s in the workbook (and 0 in the CSV) against 0.02 ... 0.39 m/s at the 38 off-plane
points (check `V_on_the_y0_plane_is_numerically_zero_not_measured`). An LDA's noise is 1e-2 m/s, so these look like symmetry values.
This release sets them to NaN. **Question:** was V measured on the y = 0 plane (a 3-component LDA), or is it a symmetry fill? How is
the TKE built (2 or 3 components)? Only k is published, not the variances.

### QI3 — Case I: UH, the inflow and the repeats (Kondo, Mutou)

1. The workbook normalises the points by UH = 1.7 m/s and its inflow sheet by 1.697 m/s (U(0.1 m), 0.18 % apart).
2. The paper says the approach flow follows a 1/7 power law; the workbook's (z/H)^(1/7) column is within 4.6 % of the profile but the
   least-squares index over z = 0.02 ... 0.2 m is 0.115 (check `approach_profile_follows_the_1_over_7_power_law_within_5_percent`). Which
   is the intended inflow?
3. 13 ground-centreline locations (x, 0, 0) are in both the y = 0 and the z = 0 concentration plane; the two values differ by up to 8.5 %
   (mean 2.5 %). Two runs? The wind CSV drops the four duplicated wind points (identical copies); the concentration CSV keeps its 13.
4. Every concentration is a multiple of 0.1 ppm: the analyser's resolution, or a rounding of the published file? A 0.4 ppm value carries
   +/-12 % of it.
