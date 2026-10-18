# AIJ UWE Benchmark Dataset – Case F (Shinjuku): Wind Tunnel Experiment and Field Observation for Flow within an Actual Urban Area in Shinjuku

## Investigators

### Dataset Editors and Distributors

- Yoshihide Tominaga (Niigata Institute of Technology, Japan)  
- Hideki Kikumoto (The University of Tokyo, Japan)  
- Tsubasa Okaze (Institute of Science Tokyo, Japan)

### Contact for Questions

Tsubasa Okaze
Email: okaze.t.f356@m.isct.ac.jp

---

## Overview

During the construction of the high-rise building group in the Shinjuku subcenter area of Tokyo, Japan, wind velocity observations near the ground surface were conducted from December 1975 to November 1983. In addition, several wind tunnel experiments reproducing the building configurations at various construction stages were performed.  
This dataset provides:  

- The field observation data collected between December 1977 and November 1978
- The wind tunnel experimental results corresponding to the 1978 building configuration

--- 

## Dataset Contents

### File List

- **AF_caseF.csv**  
  Vertical profile of the approaching flow (wind tunnel).  
  **Columns:**  
  
  - `z` (m): Coordinates  
  - `U` (m/s): Mean velocity  
  - `u_rms` (m/s): Root-mean square of streamwise velocity

- **RS-WT_caseF.csv**  
  Dataset in wind tunnel experiment.  
  **Columns:**  
  
  - `No.`: Measurement point ID
    - `x`, `y`, `z` (m): Coordinates in wind tunnel scale
    - `WD`: Wind direction
    - `U/R` (-): Mean wind speed normalized with mean approaching wind speed at 500 m in actual scale (corresponding to the boundary layer height)

- **RS-FO_caseF.csv**
  Dataset in Field observation.  
  **Columns:**
  
  - `No.`: Measurement point ID  
  - `x`, `y`, `z` (m): Coordinates in full scale
  - `WD`: Wind direction
  - `U/R` (-): Mean of 10-min mean wind speed normalized with approaching mean wind speed at 500 m in actual scale (corresponding to the boundary layer height) . The approaching mean wind speed at 500 m was converted based on the wind velcotiy ratio obtained with the wind tunnel experiment.
  - `sigma_U/R` (-): Standard deviation of normalized 10-min mean wind speeds.

- **MP_caseF.png**  
  Measurement point locations within the wind tunnel experiment. 

- **MP_caseF.csv**
  Measurement point coordinates within the wind tunnel experiment

- **BD_caseF.stl**  
  Building and terrain geometry in STL format with the wind tunnel scale. The data represents the situation as of November 1978. The lowest elevation is set to 0 m corresponding to the wind tunnel floor.

- **LF_CaseF.xls**  
  Legacy Excel version of the measurement dataset.  
  Also available via: https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm

---

## Experimental Methodology

### Field Observation

A near-round wind velocity observation was conducted in the Shinjuku subcenter area of Tokyo.

- **Observation period:** December 1977 - November 1978
- **Equipment:**: Cup anemometer with wind vene.
- **Sampling rate:** 2 Hz.
- **Averaging period**: 10 minutes
- **Reference points:** SMB at G.L.+237 m for wind directions NW, NNW, N, NNE, NE, and KDD at G.L.+187 m for other directions.
- **Analysis condition:** Only 10-min mean velocities > 5 m/s at either reference point were included.

### Wind Tunnel Experiment

A 1/800 scale model representing the Shinjuku subcenter area (radius = 800 m equivalent) was employed.  Wind speed was measured for multiple wind directions and heights (5 m, 9 m, 20 m equivalent). The experiments with wind directions E, ESE, WSW, W were not conducted since occurrence frequencies of wind direction were small in the field observation.

- **Equipment:** Thermistor anemometer
- **Averaging period**: 30 s.

---

## Notes

- The target area includes underground structures. To maintain consistency with the wind tunnel model, the building data were raised by 10 m (in actual scale) and tapered at the base. The *z*-coordinates in the measurement point files represent heights from the wind tunnel floor; the corresponding ground-level height should be obtained by subtracting the equivalent of 10 m.

- In the legacy files, both the field observation and wind tunnel experiment data were normalized using reference wind velocities as follows:
  
  - For wind directions NW, NNW, N, NNE, NE, the reference velocity was measured on the rooftop of the SMB building (rooftop elevation G.L.+210 m, anemometer height G.L.+237 m).
  - For other wind directions, the reference velocity was that of the KDD building (rooftop elevation G.L.+165 m, anemometer height G.L.+187 m).
  
  In this dataset, the reference velocities were converted such that:
  
  - For NW-NE sectors, the ratio between the wind speed at the SMB rooftop anemometer height and that at the boundary layer height (500 m) from the *N-direction* wind tunnel test was applied.
  - For other directions, the ratio between the KDD rooftop anemometer height and the boundary layer height from the *S-direction* test was used.  
    As a result, all wind speeds are normalized by the mean velocity at the inflow boundary layer height (500 m equivalent).

- In the field observations, only 10-minute averaged wind speed data exceeding 5 m/s at the SMB or KDD rooftop anemometer were used for statistical analysis.

- The wind tunnel results were recompiled from the original reports. In addition to the data corresponding to approximately 9 m above ground, additional data at 5 m and 20 m heights were included at several points.

- The legacy dataset also contains data for measurement points No. 16 and later, which were established after November 1978. These data are measured under additional buildings had been constructed beyond the configuration provided in the current building dataset.

## Location

Shinjuku subcenter area, Tokyo, Japan  

---

## Metadata

- **Units:**  
  - Length: meters (m)
  - Wind speed: meters per second (m/s)
- **File creation date:** 12 November 2025  
- **Format:** CSV, PNG, XLS, STL  
- **Absent measurement points**: points 4 and 12
- **License:** CC BY 4.0  
- **Version:** 1.0  

---

## Data Accessibility

- **Repository:** Zenodo  
- **DOI:** 10.5281/zenodo.15589621  
- **URL:** https://zenodo.org/records/15589621

---

## Related Articles

- Tominaga, Y., Mochida, A., Yoshie, R., Kataoka, H., Nozu, T., Yoshikawa, M., & Shirasawa, T. (2008). *AIJ guidelines for practical applications of CFD to pedestrian wind environment around buildings*. *Journal of Wind Engineering and Industrial Aerodynamics*, 96, 1749–1761.[https://doi.org/10.1016/j.jweia.2008.02.058](https://doi.org/10.1016/j.jweia.2008.02.058)

---

*Note: This dataset is part of the AIJ urban wind environment benchmark project, which supports validation of both wind tunnel and full-scale simulations.*
