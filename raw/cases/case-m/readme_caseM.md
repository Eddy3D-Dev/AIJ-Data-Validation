# AIJ UWE Benchmark Dataset – Case M (TPU): Wind Tunnel Experiment and Field Observation for Flow and Dispersion within TPU Campus

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
Email: yoshie@arch.t-kougei.ac.jp

---

## Overview

The concentration of released pollutants was measured in a real building complex. This wind tunnel experiment was conducted to reproduce the field measurement campaign of tracer gas release at the Atsugi Campus of Tokyo Polytechnic University (Tachibana et al., 2022). A model of the area with a radius of about 300 m centered on the tracer gas release point was reproduced at 1/600 scale. The database also includes the results of the field measurements (Tachibana et al., 2014).

---

## Dataset Contents

### File List

- **AF_caseM.csv**  
  Vertical profile of the approaching flow (wind tunnel).  
  **Columns:**  
  
  - `x`, `y`, `z` (m): Coordinates  
  - `U`, `V`, `W` (m/s): Mean wind velocity components  
  - `u_rms`, `v_rms`, `w_rms` (m/s): Root-mean-square (RMS) of each component of wind velocity fluctuation
  - `k` (m^2/s^2): Turbulent kinetic energy  
  - `uw` (m^2/s^2): Reynolds shear stresses  

- **RS-WT_caseM.csv**  
  Wind and concentration measurements (wind tunnel experiment).  
  **Columns:**  
  
  - `No.`: Measurement point ID  
  - `WD` (deg): Wind direction of approach flow
  - `x`, `y`, `z` (m): Coordinates  
  - `U`, `V`, `W` (m/s): Mean wind velocities  
  - `u_rms`, `v_rms`, `w_rms` (m/s): RMS of each component of wind velocity fluctuation
  - `k` (m^2/s^2): Turbulent kinetic energy  
  - `C` (ppm): Mean gas concentration  
  - `c_rms` (ppm): RMS of concentration fluctuations  
  - `-999.9`: Indicates unmeasured values

- **RS-FO_caseM.csv**  
  Wind and concentration measurements (field observation).  
  **Columns:**  
  
  - `No.`: Measurement point ID  
  - `Run`: Observation run  
  - `C` (ppq): Mean concentration  
  - `U_R` (m/s): Mean wind velocity at reference point
  - `WD_R` (deg): Mean wind direction at  reference point
  - `q` (m3/s): Gas emission rate

- **MP_caseM.png**  
  Measurement points in the wind tunnel model

- **BD_caseM.stl**  
  Building and terrain geometry in STL format. The lowest elevation is set to 0 m corresponding to the wind tunnel floor.

- **LC_caseM.csv**  
  Location of measurement points in wind tunnel.

- **LF_caseM.xlsx**  
  Legacy Excel version of the measurement dataset.  
  Also available via: https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm

---

## Experimental Methodology

### Wind Tunnel Experiment

A 1/600 scale model of the TPU Atsugi Campus was constructed to simulate a 300 m radius area centered on the gas release point.  Ethylene (C2H4) was released at 100% concentration from a 6 mm outlet on a rooftop, at a flow rate of 150 cc/min (0.09 m/s). Reference building height was H_R = 41 m (0.068 m model scale), and wind tunnel reference velocity was U_R = 4.08 m/s.

- **Wind velocity:**  
  
  - Constant temperature anemometer (DANTEC 90C10)  with split-fiber probe (DANTEC 55R55, 55R56, 55R57), 1000 Hz sampling, 240 s average

- **Gas concentration:**  
  
  - Hydrocarbon analyzer, 1000 Hz sampling, 240 s average

---

### Field Observation

Field measurements were conducted at full scale on the TPU campus.

- Date: 25?26 Feb 2014  

- Tracer: PMCH (C7F14), 200 ppm  

- Released from 1.5 m height at 5 L/min (~0.003 m/s)  

- 18 runs: 10 min pre-release, 10 min sampling

- **Sampling:**  
  
  - Concentration: Sorbent tubes, gas chromatography (ECD)  
  - Wind: Sonic anemometer (SAT-600), 10 Hz at reference point

---

## Location

Tokyo Polytechnic University, Atsugi, Japan

---

## Metadata

- **Units:**  
  - Length: meters (m)  
  - Wind speed: meters per second (m/s)  
  - Concentration: parts per million (ppm)  or parts per quadrillion (ppq)
- **File creation date:** 21 April, 2025  
- **Format:** CSV, PNG, XLSX  
- **Unmeasured values:** -999.9  
- **License:** CC BY 4.0  
- **Version:** 1.0  
- **Citation requested:** Tachibana, T., Yoshie, R., Nakayama, S., Kishida, T., Miyashita, K., Sasaki, R., 2022. Comparison between field measurement and wind tunnel experiments of gas dispersion in an urban area and verification of similarity law. Journal of Wind Engineering, 47(3), 39-52. (in Japanese) http://dx.doi.org/10.5359/jwe.47.39

---

## Data Accessibility

- **Repository name:** Zenodo  
- **DOI:** 10.5281/zenodo.15487857
- **URL:** https://zenodo.org/records/15487857

---

## Related Articles

- Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167?196. https://doi.org/10.1007/978-4-431-55912-2_9
- Tachibana, T., Tanabe, G., Yoshie, R., Nakayama, S., Namiki, S., & Miyashita, K. (2014). Prediction of pollutant dispersion in urban area based on field measurement and wind tunnel experiment. Proceedings of the 23rd National Symposium on Wind Engineering, 31-36. (in Japanese) https://doi.org/10.14887/kazekosymp.23.0_31
- Tachibana, T., Yoshie, R., Nakayama, S., Kishida, T., Miyashita, K., Sasaki, R., 2022. Comparison between field measurement and wind tunnel experiments of gas dispersion in an urban area and verification of similarity law. Journal of Wind Engineering, 47(3), 39-52. (in Japanese) http://dx.doi.org/10.5359/jwe.47.39

---

*Note: This dataset is part of the AIJ urban wind environment benchmark project, which supports validation of both wind tunnel and full-scale dispersion simulations.*
