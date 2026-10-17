# Spatial Hotspot Analysis of Conflict Fatality Rates (PySAL)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySAL](https://img.shields.io/badge/PySAL-esda%20%26%20libpysal-orange.svg)](https://pysal.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview
A reproducible Python workflow for finding statistically significant hotspots and spatial clusters in area-based fatality rates, using **PySAL** (`esda`, `libpysal`), **GeoPandas**, **pandas** and **NumPy**. It is based on my MSc project on conflict fatalities across Myanmar's townships.

The repository has two parts:
- **`conflict_hotspot_demo.py`** runs on synthetic data (a 20 × 20 grid with made-up population and fatalities). It needs no downloads and illustrates the method only.
- **`myanmar_conflict_analysis.py`** is the full pipeline for real township data (boundaries, ACLED, census). The data is not included for licensing reasons; see `DATA.md`. No real-data results are published here.

## Workflow
1. Join boundary, conflict and population tables on township P-code (left joins, so zero-fatality townships are kept).
2. Check the join: stop if a population is missing or fatalities exceed population (catches ID and unit mismatches).
3. Project to UTM 46N and calculate fatalities per 100,000 population.
4. Build K-nearest-neighbour weights (K = 8, row-standardised), so no area is isolated.
5. **Getis-Ord Gi\*** hotspots: p < 0.05 with a positive z-score.
6. **Local Moran's I (LISA)**: High-High and Low-Low clusters, High-Low and Low-High outliers, p < 0.05.
7. Print global Moran's I and cluster counts; export a GeoPackage for mapping in ArcGIS Pro or QGIS.

## Repository structure
```
conflict_hotspot_demo.py       # synthetic-data demo
myanmar_conflict_analysis.py   # real-data pipeline
DATA.md                        # data sources and required columns
requirements.txt
LICENSE
```

## Run
```
pip install -r requirements.txt
python conflict_hotspot_demo.py
```
Real-data pipeline: place the three input files next to the script, then `python myanmar_conflict_analysis.py`.
A fixed random seed (42) makes the permutation tests repeatable.

## Limitations
- Rates are unstable where populations are small.
- The census (2014) predates the conflict period.
- p-values are not corrected for multiple testing.
- Most areas record zero fatalities, so Low-Low clusters partly reflect clusters of zeros.
- ACLED records reported events only, so reporting bias applies.
- Results depend on correct ID matching between the three inputs.

## Author
Aung Kaung Myat, MSc GIS & Remote Sensing, University College Dublin.
