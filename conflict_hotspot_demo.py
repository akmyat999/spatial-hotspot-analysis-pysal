"""Spatial hotspot analysis demo: Getis-Ord Gi* and Local Moran's I (LISA) with PySAL.

Author: Aung Kaung Myat (MSc GIS & Remote Sensing, University College Dublin)

This demo runs on SYNTHETIC data (a 20 x 20 grid of areas with made-up population and
fatality counts), so it needs no downloads. It shows the same workflow I used on real
township data: rate -> data checks -> spatial weights -> Gi* -> LISA -> summary.
"""
import numpy as np
import pandas as pd
from esda.getisord import G_Local
from esda.moran import Moran, Moran_Local
from libpysal.weights import KNN

SEED, K, ALPHA, SIDE = 42, 8, 0.05, 20
QUADRANTS = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}  # PySAL quadrant codes


def make_synthetic_data():
    """Grid of areas: random population, deaths concentrated around one 'hotspot' centre."""
    rng = np.random.default_rng(SEED)
    xs, ys = np.meshgrid(np.arange(SIDE), np.arange(SIDE))
    df = pd.DataFrame({"id": range(SIDE * SIDE), "x": xs.ravel(), "y": ys.ravel()})
    df["population"] = rng.integers(20_000, 400_000, len(df))
    dist = np.hypot(df["x"] - 5, df["y"] - 14)               # distance to hotspot centre
    expected = 3_000 * np.exp(-dist / 3) * df["population"] / 200_000
    df["fatalities"] = rng.poisson(expected)
    return df


def main():
    df = make_synthetic_data()

    # 1. Data check: fatalities cannot exceed population (catches ID/unit mismatches)
    if (df["fatalities"] > df["population"]).any():
        raise ValueError("Fatalities exceed population: check the join keys.")

    # 2. Rate per 100,000
    df["rate_per_100k"] = df["fatalities"] / df["population"] * 100_000
    y = df["rate_per_100k"].values

    # 3. Spatial weights: K nearest neighbours, row-standardised
    w = KNN.from_array(df[["x", "y"]].values, k=K)
    w.transform = "r"

    # 4. Getis-Ord Gi*: hotspot = significant and positive z-score
    gi = G_Local(y, w, star=True, seed=SEED)
    df["gi_hotspot"] = ((gi.p_sim < ALPHA) & (gi.Zs > 0)).astype(int)

    # 5. Local Moran's I: HH / LL clusters, HL / LH outliers where significant
    lisa = Moran_Local(y, w, seed=SEED)
    df["lisa"] = np.where(lisa.p_sim < ALPHA, pd.Series(lisa.q).map(QUADRANTS), "Not Significant")

    # 6. Global Moran's I and summary
    np.random.seed(SEED)
    mi = Moran(y, w)
    print(f"Areas: {len(df)} | Global Moran's I = {mi.I:.3f} (p = {mi.p_sim:.3f})")
    print(f"Gi* hotspots: {df['gi_hotspot'].sum()}")
    print(df["lisa"].value_counts().to_string())
    df.to_csv("demo_results.csv", index=False)


if __name__ == "__main__":
    main()
