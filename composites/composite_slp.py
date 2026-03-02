"""
Plot composite sea level pressure (SLP) anomaly fields during high-SST years.
"""

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import FormatStrFormatter
from pathlib import Path

# =========================================================
# User settings
# =========================================================
ROOT = Path(__file__).resolve().parents[1]

FILE_PATH = ROOT / "data" / "raw" / "slp_025_1979_2025.nc"
HIGH_YEARS_CSV = ROOT / "data" / "final" / "ecs_high_years.csv"

VAR_NAME = "msl"
TIME_NAME = "valid_time"

CLIM_START, CLIM_END = 1991, 2020

REGION = dict(lon_min=90, lon_max=180, lat_min=0, lat_max=60)
PLOT_EXTENT = [REGION["lon_min"], REGION["lon_max"],
               REGION["lat_min"], REGION["lat_max"]]

OUT_DIR = ROOT / "plot"
OUT_DIR.mkdir(exist_ok=True)
OUT_PNG = OUT_DIR / "SLP_high-climatology.png"

# =========================================================
# Read composite years
# =========================================================
high_df = pd.read_csv(HIGH_YEARS_CSV)
HIGH_YEARS = (high_df["year"] if "year" in high_df.columns
              else high_df.iloc[:, 0]).dropna().astype(int).tolist()

print("HIGH years:", HIGH_YEARS)

# =========================================================
# Load data
# =========================================================
ds = xr.open_dataset(FILE_PATH)
da = ds[VAR_NAME].sortby("latitude")

da[TIME_NAME] = pd.to_datetime(da[TIME_NAME].values)

# yearly mean
slp_yearly = da.groupby(f"{TIME_NAME}.year").mean(TIME_NAME, skipna=True)

# Pa → hPa
slp_yearly = slp_yearly / 100.0
slp_yearly.attrs["units"] = "hPa"

# =========================================================
# Composite & climatology
# =========================================================
comp_high = slp_yearly.sel(year=HIGH_YEARS).mean("year", skipna=True)
clim = slp_yearly.sel(year=slice(CLIM_START, CLIM_END)).mean("year", skipna=True)

anom = comp_high - clim
anom.attrs["units"] = "hPa"

# =========================================================
# Plot
# =========================================================
proj = ccrs.PlateCarree()
lon = slp_yearly["longitude"]
lat = slp_yearly["latitude"]

fig = plt.figure(figsize=(8, 6))
ax = plt.axes(projection=proj)

ax.set_extent(PLOT_EXTENT, crs=proj)
ax.coastlines("50m", linewidth=0.8)
ax.add_feature(cfeature.BORDERS.with_scale("50m"), linewidth=0.5)

gl = ax.gridlines(draw_labels=True, linewidth=0.3,
                  color="gray", alpha=0.5, linestyle="--")
gl.right_labels = False
gl.top_labels = False

# ----- Shading: anomaly -----
vlim = float(np.nanmax(np.abs(anom.quantile([0.02, 0.98]).values)))

im = ax.contourf(
    lon, lat, anom.values,
    levels=np.linspace(-vlim, vlim, 21),
    cmap="RdBu_r",
    extend="both",
    transform=proj
)

# ----- Contour: climatology -----
step = 4.0
clim_data = clim.values
lo = float(np.nanmin(clim_data))
hi = float(np.nanmax(clim_data))
start = np.floor(lo / step) * step
stop  = np.ceil(hi / step) * step
clevs_clim = np.arange(start, stop + step, step)

cs = ax.contour(
    lon, lat, clim.values,
    levels=clevs_clim,
    colors="black",
    linewidths=0.7,
    transform=proj
)
ax.clabel(cs, inline=True, fontsize=7, fmt="%.0f")

# ----- Colorbar -----
cb = plt.colorbar(im, orientation="horizontal",
                  pad=0.08, fraction=0.08)
cb.set_label("hPa")
cb.ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))

ax.set_title(
    f"SLP (High SST - Climatology)"
    "(shading = anomaly, contour = climatology)",
    fontsize=12
)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
plt.show()

print("[Saved]")
print(OUT_PNG)
