# AIJ UWE Benchmark Dataset – Case K (ArraysC): Wind and Concentration Measurements in Cube Arrays with Point-source Dispersion

## Investigators

### Data Collectors

- Ryuichiro Yoshie (Tokyo Polytechnic University, Japan)
- Takumi Tachibana (Wind Engineering Institute, Japan)  

### Dataset Editors and Distributors

- Yoshihide Tominaga (Niigata Institute of Technology, Japan)  
- Hideki Kikumoto (The University of Tokyo, Japan)  
- Tsubasa Okaze (Institute of Science Tokyo, Japan)

### Contact for Questions

Ryuichiro Yoshie  
Email: [yoshie@arch.t-kougei.ac.jp](mailto:yoshie@arch.t-kougei.ac.jp)

---

## Overview

The wind velocity and gas concentration were measured in an urban block model formed by a group of cubes placed in the boundary layer with emission gas released from a point source placed on the floor. The cube blocks were placed at equal intervals of 9 rows by 9 columns (81 cubes in total). The gas source is located between the second and third rows on the center line. 

---

## Dataset Contents

### File List

- **AF_caseK.csv**  
  Vertical profile of the approaching flow.  
  **Columns:**
  
  - `x`, `y`, `z` (m): Coordinates (Streamwise, Spanwise, Vertical)
  - `U`, `V`, `W` (m/s): Mean wind velocity components
  - `u_rms`, `v_rms`, `w_rms` (m/s): Root mean square (RMS) of each component of wind velocity fluctuation
  - `k` (m2/s2): Turbulent kinetic energy
  - `uw`, `uv` (m2/s2): Reynolds stresses  

- **RS_caseK.csv**  
  Wind and concentration measurements around the building.  
  **Columns:** 
  
  - `x`, `y`, `z` (m): Coordinates (Streamwise, Spanwise, Vertical)
  - `U`, `V`, `W` (m/s): Mean wind velocities 
  - `u_rms`, `v_rms`, `w_rms` (m/s): RMS of each component of wind velocity fluctuation  
  - `k` (m2/s2): Turbulent kinetic energy
  - `C` (ppm): Mean gas concentration  
  - `c_rms` (ppm): RMS of concentration fluctuations

- **MP-y_caseK.png**  
  Measurement points on vertical planes (`y/H = 0, ±1, ±2, ±3`).

- **MP-z_caseK.png**  
  Measurement points on two horizontal sctions (`z/H =< 1/2` and `z/H > 1/2`).

- **LF_caseK.xlsx**  
  Legacy Excel version of the measurement dataset, provided as per the AIJ guidelines. Also available via: [Guidebook for CFD Predictions of Urban Wind Environment](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm)

---

## Experimental Methodology

### Experimental Setup

- One side of the cube: H = 0.06 m
- Mean wind velocity of the approaching flow at H: U_H = 2.33 m/s
- Reymold number: approx. 9800 (defined by H and U_H)
- Origin: Bottom center of the windward wall of the fourth row of the central building
- Source: Point source on the ground surface located at 0.15 m windward from the origin.
- Tracer gas: 100% ethylene (C2H4), released with emmision rate 3.6 × 1E-6 m3/s from a 5 mm diameter gas outlet. 

### Instrumentation

- Wind velocity:
  
  - Constant temperature anemometer (DANTEC 90C10)  
  - Split-fiber probe (DANTEC 55R55, 55R56, 55R57)  
  - The sampling frequency was 1000 Hz with 200 Hz cutoff frequency of low-pass filter. The measurements are taken for 60 sec to obtain statistics.

- Gas concentration:  
  
  - High-speed total hydrocarbon analyzer  
  - The sampling frequency was 1000 Hz with 200 Hz cutoff frequency of low-pass filter. The measurements are taken for 60 sec to obtain statistics.

### Location

Tokyo Polytechnic University, Atsugi, Japan

---

## Metadata

- **Units:**  
  - Length: meters (m)  
  - Wind speed: meters per second (m/s)  
  - Concentration: parts per million (ppm)  
- **File creation date:** 21 April, 2025  
- **Format:** CSV, PNG, XLSX  
- **Missing values:** None  
- **License:** CC BY 4.0  
- **Version:** 1.0  
- **Citation requested:** Yoshie, R. (2016). *Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer*. Adv Environ Wind Eng, 167–196. https://doi.org/10.1007/978-4-431-55912-2_9

---

## Data Accessibility

- **Repository name:** Zenodo  
- **DOI:** 10.5281/zenodo.15448050
- **URL:** https://zenodo.org/records/15448050

---

## Related Articles

- Yoshie, R. (2016). *Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer*. Adv Environ Wind Eng, 167–196. https://doi.org/10.1007/978-4-431-55912-2_9

---

*Note: This dataset is part of the AIJ urban wind environment benchmark project, which aims to support the verification and validation of CFD simulation for urban flow simulations.*
