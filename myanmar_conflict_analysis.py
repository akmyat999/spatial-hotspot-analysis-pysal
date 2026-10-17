"""Conflict fatality rates, Getis-Ord Gi* hotspots and Local Moran's I clusters per township.
Author: Aung Kaung Myat (MSc GIS & Remote Sensing, University College Dublin)
Inputs (see DATA.md): township shapefile, conflict CSV (TS_PCODE, fatal_post), population CSV (TS_PCODE, Total_Population)
"""
import geopandas as gpd
import numpy as np
import pandas as pd
from esda.getisord import G_Local
from esda.moran import Moran, Moran_Local
from libpysal.weights import KNN

# 1. Load and join on township P-code (left join keeps townships with no conflict records)
townships = gpd.read_file("mmr_polbnda_adm3_250k_mimu_1.shp")
conflict = pd.read_csv("conflict_data.csv")
population = pd.read_csv("population_data.csv")
gdf = (townships.merge(conflict, on="TS_PCODE", how="left")
       .merge(population, on="TS_PCODE", how="left")
       .to_crs(epsg=32646))  # UTM 46N (metres)
gdf["fatal_post"] = gdf["fatal_post"].fillna(0)

# 2. Check the join before analysing
assert gdf["Total_Population"].notna().all(), "Some townships have no population: check P-codes"
assert (gdf["fatal_post"] <= gdf["Total_Population"]).all(), "Deaths exceed population: likely P-code mismatch"

# 3. Fatalities per 100,000 people
gdf["fatal_per_100k"] = gdf["fatal_post"] / gdf["Total_Population"] * 100_000
y = gdf["fatal_per_100k"].values

# 4. Spatial weights: 8 nearest neighbours, row-standardised
w = KNN.from_dataframe(gdf, k=8)
w.transform = "r"

# 5. Getis-Ord Gi*: hotspot = significant (p < 0.05) with positive z-score
gi = G_Local(y, w, star=True, seed=42)
gdf["gi_hotspot"] = ((gi.p_sim < 0.05) & (gi.Zs > 0)).astype(int)

# 6. Local Moran's I: HH / LH / LL / HL clusters where significant
lisa = Moran_Local(y, w, seed=42)
labels = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}
gdf["lisa"] = np.where(lisa.p_sim < 0.05, pd.Series(lisa.q).map(labels), "Not Significant")

# 7. Summary and export
np.random.seed(42)
print(f"Townships: {len(gdf)} | Global Moran's I: {Moran(y, w).I:.3f} | Gi* hotspots: {gdf['gi_hotspot'].sum()}")
print(gdf["lisa"].value_counts())
gdf.to_file("conflict_analysis.gpkg", layer="townships", driver="GPKG")
