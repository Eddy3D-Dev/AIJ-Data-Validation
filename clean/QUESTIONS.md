# Open questions for the data collectors (Ilker / Patrick to forward)

Things the published files, readmes and the data paper (Kikumoto et al. 2026, JAR 9(1) e70083)
cannot settle. Contacts: `manifest.json → cases.<id>.contact`. Numbers: `checks.json`.

## Q1 — Case C: which way does the turntable turn? (Nonomura)

In `RS_caseC.csv`'s own frame (+x = the WD = 0 flow, confirmed three ways on the data) the WD = 45°
field is mirror-symmetric about the line **y = −x**: mean |ΔVs| over the 57 mirror pairs is
0.108 / 0.103 / 0.130 m/s for 0D / 1D / 2D (the experiment's own repeatability floor), while the
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

## Questions on Cases F and M

Numbers: `checks.json` and `manifest.json → cases.F / M`. Contacts: Case F, Tsubasa Okaze; Case M, Ryuichiro Yoshie.

## QF1 — Case F: is the field series of point 14 shifted by one direction? (Okaze)

In `RS-FO_caseF.csv` the 16 rows of point 14 hold the value that `LF_CaseF.xls` ('Results (No.1-No.15)', block
No.14) gives for the **next** direction clockwise: (14, N) = workbook NNE, (14, NNE) = workbook NE, … (14, NNW) =
workbook N, each times the sector's factor and rounded. The other 12 points match the workbook on all 16 directions
with no shift (192 of 192 rows reproduced). The R between the 12 tunnel directions and the field at point 14 is 0.55
as published (every other point: 0.63 … 0.93) and 0.72 with the workbook's alignment. This release follows the workbook; the published values are in
`manifest.json → cases.F.known_issues`. **Question:** which alignment is the field observation's? One line closes it.

## QF2 — Case F: tunnel value of point 8, SW, 9 m (Okaze)

`RS-WT_caseF.csv` has U/R = 0.474 at (8, SW, z = 0.02375 m). The workbook's 'Results' sheet is blank for it (as for
the 'Other' column), and its flat 'Sheet1' table gives 0.63 (× 0.9629 = 0.607). The 155 other 9 m rows all reproduce
from the workbook within 0.014. Is the value 0.474, 0.607, or was the point not measured at SW?

## QF3 — Case F: what is the 'Other' column of the workbook? (Okaze)

The workbook's wind-tunnel block has 'Other' and 'Target' columns. 'Target' is the 9 m plane (155 of the CSV's 156 rows
reproduce within 0.014 with the sector factors). 'Other' has 109 values, 9 of them at **ESE**, where the readme says the tunnel
did not run (E, ESE, WSW, W), and it reproduces neither the 5 m nor the 20 m rows of the CSV (2 of 79 comparable pairs).
What are they: another model state, another height, or another run? Are the 5 m and 20 m values of the CSV from the original
reports only?

## QF4 — Case F: which ground do the heights refer to? (Okaze)

The readme says the points' z is above the tunnel floor and the ground is at z − 10 m, because the building data were raised
by 10 m; the planes are then 5, 9, 20 m above ground. In `BD_caseF.stl` the terrain under all 13 points is at
**z = 5 m**, so the planes stand 10, 14 and 25 m above it, and the two reference roofs (SMB, KDD) are 15 m above their
stated G.L. elevations (225 against 210 m, 180 against 165 m: 5 m terrain + 10 m). Where was the probe relative to the model's
street surface, and is the STL the model that was in the tunnel?

## QF5 — Case F: size and orientation of the STL (Okaze)

The STL is a disc of radius 725.0 m (0.90625 m model), open along its rim (812 boundary edges, all at z = 0); the readme says
"radius = 800 m equivalent" and the data paper "a diameter of 1,600 m". A 1.8125 m model would not fit the 1.55 m wide tunnel
the paper describes. All its ground and roof facets (and a sample of walls) face down, so the file is wound inward; this release
reverses it. Please confirm the radius that was in the tunnel, and that the file is meant to describe the 1978 configuration.

## QF6 — Case F: which reference point is SMB? (Okaze)

`MP_caseF.csv` gives SMB (0.10725, −0.433875) and KDD (−0.021875, 0.12) m (model); the workbook's 'Points' sheet gives the
Shinjuku-Mitsui Building at (−17.5, 96.0) and the KDD Building at (85.8, −347.1) m, which are the same points with the names
exchanged; `MP_caseF.png` labels (−0.02, 0.12) as D and (0.107, −0.434) as C, as the workbook does. The STL has a 225 m roof at
(−17.5, 96.0) and a 180 m roof at (85.8, −347.1): 45 m apart as SMB (210 m) and KDD (165 m) are. The release takes the workbook's
assignment; please confirm `MP_caseF.csv` is the one that is wrong.

## QF7 — Case F: field anemometer heights (Okaze)

By the readme's rule (z − 10 m) the field anemometers stand 3 m (point 15), 7 m (8), 8 m (11), 9 m (1, 2, 3, 5, 6, 7, 9, 10) and
**11 m** (13, 14) above ground. The data paper says "3 to 9 m". Are 13 and 14 at 11 m or at 9 m, and are the heights the true
heights above the local ground?

## QF8 — Case F: the reference speed and the conversion factors (Okaze)

The ratios are normalised by the approaching speed at 500 m. The data paper gives it as 10 m/s; `AF_caseF.csv` reaches 400 m
at 10.0 m/s, and combined with the workbook's U/UR profile (0.94 at 400 m) the 18 shared heights imply U(500 m) = 10.65 m/s
(10.59 … 10.73). The field values are the workbook's roof-anemometer ratios times 0.9397 (SMB sector, interval
[0.93947, 0.94000]) and 0.9629 (KDD, [0.96250, 0.96324]), which the readme describes without giving. What are U(500 m) in m/s and the two
factors, and what height does AF_caseF.csv's last row stand for?

## QF9 — Case F: direction sense (Okaze)

Are the wind directions the meteorological directions the wind blows **from**, clockwise from north, with +y north in
`MP_caseF.png`? This release assumes so (status `unverified`): the reference-building choice (SMB, the northern building, for
NW to NE) and the upwind roughness of the northern points (higher for S than for N) agree with it.

*Update 2026-10-18 — a solved field decides NNW.* Eddy3D solved the district for the wind from NNW (OpenFOAM 12, realizable k-ε, 2,143,488 cells,
2000 iterations) and scored the 13 points of the 9 m plane against the tunnel's column for that label and against its column for the opposite
wind, SSE, on the same solution. Probed at the published z, R = 0.935 with the NNW column and R = 0.077 with the SSE column (FAC2 1.00 and 0.62);
probed at the STL's ground plus 9 m, R = 0.945 and 0.102. A RANS solution knows no compass, so the labels name the direction the wind comes
from, at least at this direction (`directions.csv` says so for the NNW rows; the other directions stay `unverified` until one is solved). The
question stays open for the collector's own word.

## QF10 — Case F: the field band of the workbook (Okaze)

In 10 rows of the workbook (2/NW, 6/E, 7/ESE, 7/NW, 9/E, 13/WNW, 14/ENE, 14/SSE, 15/N, 15/SSE) Mean + S.D. and Mean − S.D. are not
symmetric about the mean (differences from −0.11 to +0.10), and the last column equals Mean − (Mean − S.D.). The CSV's σ is that
lower half-width times the factor. Which is the standard deviation: the lower half-width, the upper, or the mean of the two?

## QM1 — Case M: where was the tracer released in the tunnel? (Yoshie)

The readme says ethylene was released "from a 6 mm outlet on a rooftop"; the workbook and `LC_caseM.csv` give the source at the
ground surface (z = 32.39 m full scale = the STL's terrain there, 32.39 m, no roof), and the field release was 1.5 m above ground.
Was the tunnel source at ground level, on a roof, or 1.5 m high (0.0025 m model)?

## QM2 — Case M: what is H_R = 41 m? (Yoshie)

`LC_caseM.csv` puts the reference point R at ground + 41 m (z = 72.90 m). The STL's main-building roof under R is at 64.92 m, 33.0 m
above the same ground, so R is 8.0 m above the roof; Table 1 of the data paper says Hmax = 41 m and the readme "reference building
height", while the tallest surface of the STL is 31.8 m above the origin's ground. Is 41 m the anemometer height (a mast on a 33 m roof)? The
workbook's c0 uses H_R = 0.068 m (41 m / 600 = 0.06833 m would give c0 = 131.2 ppm instead of 132.5, the paper's 1.33 × 10² ppm):
which H_R was meant for the tunnel?

## QM3 — Case M: backgrounds and baselines (Yoshie)

Every field run reads 9 to 11 ppq at point 12 (all 18 runs, whatever the wind) and 8 to 9 ppq at the minimum of points 11, 13, 14, 15; the
values are not zero and not subtracted. Is that the ambient PMCH background, the detection limit, or a blank? The tunnel's hydrocarbon
analyser has two negative means (point 12: −0.021 and −0.230 ppm) and rms of 7.3 to 17.4 ppm where the mean is below 1 ppm. Was a
baseline subtracted, and is the rms at those points noise or intermittency?

## QM4 — Case M: the rounding of the field's run conditions (Yoshie)

`RS-FO_caseM.csv` gives U_R to 0.01 m/s (the workbook's values are multiples of 1/30 m/s, i.e. means of three values), WD_R to 0.1° and q to
three significant digits. The cleaned table carries the workbook's. Are the workbook's the sonic anemometer's 10-minute values averaged
over three periods?

## QM5 — Case M: where was the approach flow measured? (Yoshie)

`AF_caseM.csv` is at x = −0.498 m, y = 0, with z "above the wind-tunnel floor". In `BD_caseM.stl` the model's upwind taper is 0.0521 m high at that
station, so the 10 lowest of the 40 heights (0.005 to 0.05 m) are below the model's ground there. Was the profile measured on the empty floor
(without the model), and is its U(z) the inlet for the ground at z = 0 or for the model's terrain? The profile at the height of R (0.1215 m)
gives 3.94 m/s against U_R = 4.08 m/s measured at R above the model.

## QM6 — Case M: direction convention (Yoshie)

The frame used here is +x north, +y west with WD the direction the wind comes from (the compass rose of `MP_caseM.png` and the plume's
lateral shift with WD in the tunnel and the field agree). Please confirm that WD_R of the field runs and WD of the tunnel are the same
meteorological direction, and that the sign of V in `RS-WT_caseM.csv` is positive toward +y (west).

## Cases G, H and I

What each check measured
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

## QJ1 — Case J: the w′θ′ uncertainty at z/H = 0.25 (Yoshie)

In `LF_caseJ.xlsx`, sheet `xy-plane2(Unstable state)`, the "Expanded Uncertainty" column of ⟨w′θ′⟩/(U_H Δθ) (column AH) reads
0.00374 in row 31 and then 1.0037, 2.0037, 3.0037 … 193.0037 down to row 234: the cell was dragged with the fill handle
(+1 per row), 193 cells. Only the 11 rows on y = 0 (the locations the `xz-plane` sheet shares) hold a real value (5·10⁻⁵ – 5.5·10⁻⁴); row 31, the seed, is 0.00374. What are the original
uncertainties of w′θ′ on the z/H = 0.25 plane? (The mean-concentration uncertainty has no such problem; it is about 1 ppm.)

## QJ2 — Case J: the reference concentration (Yoshie)

The workbook's c0 = 12.283 ppm equals 0.05 · q / (U_H H²) with U_H = 1.4581 m/s (to 1e-15): the 5 % ethylene fraction of the
released gas is in it. The data paper gives c0 for Cases H (45.2 ppm, pure ethylene) and I (39.2 ppm, 10 % ethane, fraction
included) but not for J, and the readme gives q = 9.17·10⁻⁶ m³/s of "5 % concentration". Confirm: are the published C
values ppm of ethylene itself (not of the 5 % mixture), and is 12.283 ppm the intended c0? (Without the fraction c0 would be
245.7 ppm and every concentration ratio 20 times smaller.)

## QJ3 — Case J: the readme's Reynolds number (Yoshie)

The readme says the Reynolds number is "approx. 43,000 (based on U_H and H)". With U_H = 1.46 m/s and H = 0.16 m it is
1.6·10⁴, which is what the data paper states; 43,000 is Case H's (3.23 m/s × 0.2 m). A copy from Case H's readme?

## QJ4 — Case J: σ against ⟨u′²⟩ (Yoshie)

The workbook's ⟨u′²⟩/U_H² columns are not the squares of its σ_u/U_H columns: up to 3.2 % in u, 2.2 % in v, 1.7 % in w
(47 of 443 locations differ by more than 1 % in a component; the largest absolute difference is at (−0.06, −0.05, 0.04): σ_u² =
0.1294, ⟨u′²⟩ = 0.1316 in units of U_H²). k is the half-sum of the ⟨u′²⟩ columns to 9·10⁻⁵. This release carries the variance columns.
Is that the right one, and why do the two differ (different sensor of the split-fibre probe, detrending)? The published CSV has
only the rms.

## QJ5 — Case J: which empty-tunnel profile is the inflow? (Yoshie)

`AF_caseJ.csv` is the workbook's profile at x/H = −2.5 (x = −0.4 m). The workbook also has the empty-tunnel profiles at
x/H = 0 and +2.5, which differ near the ground: U/U_H at z/H = 0.019 is 0.33, 0.58 and 0.50 (and 1.00, 1.03, 1.04 at z = H).
Was the boundary layer still developing over the heated floor, and which profile should a model reproduce at the
building's position? Also: `RS_caseJ.csv` lists (−0.16, 0, 0.004) twice (No. 1 and 153, identical); a duplicate or two
runs?

## QK1 — Case K: the reference height, velocity and concentration (Yoshie, Tachibana)

The readme and the data paper give the cube H = 0.06 m and U_H = 2.33 m/s, from which c0 = q / (U_H H²) = 429.18 ppm for
q = 3.6·10⁻⁶ m³/s of pure ethylene. `LF_caseK.xlsx` ('Measurement data', cells R7:R11) normalises with H = 0.2 m (Case H's
building), a "reference velocity" UH = 4.94009 m/s and C0 = 18.218 ppm; every normalised column (X/H, ⟨u⟩/UH, k/UH²,
⟨c⟩/C0) reproduces its dimensional column exactly with those, so the workbook's concentration ratios are 23.56 times smaller
than the cube's. The approach-flow file (Case H's) gives U = 2.24 m/s at z = 0.06 m (log-interpolated), 4 % below 2.33, and
4.94 m/s is not on it (U = 4.32 at z = 0.6 m). Which H, U_H and c0 are meant for Case K, and what is UH = 4.94 m/s? This
release uses the cube's (c0 = 429.18 ppm) and gives the factor to the workbook's in the manifest.

## QK2 — Cases K and L: the workbook's mean scalar speed (Yoshie)

K's workbook has `<usc>` and σ_usc ("Velocity magnitute") beside ⟨u⟩, ⟨v⟩, ⟨w⟩: it is never below |U| (1.03 – 3.9 × |U|,
median 1.19) and is not √(|U|² + 2k) (0.67 – 0.98 of it). L's workbook has `Usc`, which equals √(⟨u⟩² + ⟨v⟩² + ⟨w⟩²) to
1e-16. Is K's `<usc>` the mean of the instantaneous speed (a scalar, like a thermistor's)? If so it is the quantity a RANS |U|
should be compared with, and the table has no column for it; if not, what is it?

## QK3 — Case K: point numbers (Yoshie)

`RS_caseK.csv` and the workbook's `Measurement data` sheet have no point numbers (Cases A–E and J, L do). Are the 203 rows in
the order of measurement, and is there a numbering to use? This release numbers them 1 … 203 in file order.

## QK4 — Case K: the data paper's description (Kikumoto, Okaze)

Section 3.11 ends: "The measurements were taken at approximately 30 points at eight different heights downwind of the line
source." Case K has a point source and 203 points at five heights (0.004, 0.01, 0.03, 0.05, 0.07 m); the sentence matches
Case L (27 locations at 8 heights). A text slip?

## QK5 — Case K: the approach flow (Yoshie)

`AF_caseK.csv` equals `AF_caseH.csv` row for row (17 heights at x = −0.493 m, U = 3.23 m/s at z = 0.2 m). The data paper says
the approach flows were the same. Was Case K's own profile measured, or is Case H's the record? (The workbook's `Inflow`
sheet divides by 3.23 m/s and H = 0.2 m, and its ratios imply 3.21 – 3.27 m/s for U, not exactly 3.23.)

## QK6 — Cases K and L: the lateral velocity (Yoshie)

In the y-symmetric arrays V should be odd in y. K's even part is 0.057 m/s against an odd part of 0.017 m/s (74 mirror pairs;
the empty-tunnel profile has V ≈ +0.04 m/s), L's comparable: a cross-flow offset of about 2° (probe yaw or tunnel swirl) that
hides the lateral structure and the sign of V. Is V corrected for it, and does +V point toward +y of the published
coordinates?

## QL1 — Case L: the unit of the temperature column (Yoshie, Katada)

`RS_caseL.csv`'s column is headed `T(K)` but holds 12.85 … 29.86, equal to the workbook's ⟨θ⟩ (deg.) to 0.005, i.e. degrees
Celsius; `AF_caseL.csv`'s `T(K)` (283.11 … 295.31) is kelvin. Confirm. This release carries °C for both.

## QL2 — Case L: the building surface temperature (Yoshie, Katada)

The readme lists "Building surface temperature: T_b = 14.8 °C", the same number as its T_0 = 14.8 °C and as the workbook's
⟨θ_H⟩ = 14.75 °C (the air at z = H); the bulk Richardson number uses T_b − T_f = θ_H − θ_f. The workbook gives
⟨θ_build⟩ = 42.2 °C (floor 45.0 °C). Which is the building surface in the experiment? (Case J's readme calls θ_H "T_b" as
well, and its measured surface is 24.5 °C.) A model needs the surface temperature, and no per-point values are published for L.

## QL3 — Case L: the source geometry (Yoshie, Katada)

The readme and data paper give the source area as 0.037 m (x) × 1.2 m (y), the tunnel width; `BD_caseL.stl`'s `line_source`
solid is a flat patch 0.04 m × 1.02 m (x from −0.17 to −0.13, y ±0.51: the width of the cube array), centred at x = −0.15 m.
Which is the physical outlet? The tracer flux through four cross-sections is 0.86 – 1.0 of q / 1.2 m and 0.73 – 0.85 of q / 1.02 m,
so the data favour the 1.2 m width only weakly.

## QL4 — Case L: the lateral asymmetry (Yoshie, Katada)

The array and the source are y-symmetric, yet the same point at +y and −y differs in U by 26 %, in k by 23 %, in C by 36 % on
average (110 mirror pairs), and at z = 0.15 m (0.09 m above the roofs) U is 0.11 m/s lower and T 1.3 K higher at +y. Is the
heated floor or the stratification non-uniform across the tunnel, were the two halves measured in different runs, and which
half is representative of a symmetric simulation?

## QL5 — Case L: the readme (Yoshie, Katada)

The readme's file list names `AF_caseK.csv` and `RS_caseK.csv` (the files are `AF_caseL.csv`, `RS_caseL.csv`), lists `tc`
(⟨θ′c′⟩, K·ppm) which has no counterpart in the other cases, and says "9 rows by 14 columns" where `BD_caseL.stl` has 14 rows
along the flow by 9 across. Please confirm the rows and columns are 14 along x and 9 across y, and that `tc` is the
covariance of the temperature and concentration fluctuations.

## QL6 — Case L: what is the model floor's height? (Yoshie, Katada)

The data paper raises the block model's floor 10 mm above the tunnel floor and joins it with a 1/7 taper; the lowest points
are at z = 4 mm. Are the heights measured from the model floor (as assumed here, so cube tops are at 0.06 m) or from the
tunnel floor?
