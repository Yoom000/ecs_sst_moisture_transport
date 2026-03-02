"""
Plot composite integrated water vapor (IWV) fields during high-SST and low-SST years.
"""
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

# -------------------- Path  --------------------
ROOT = Path(__file__).resolve().parents[1]  
RAW = ROOT / "data" / "raw"
FINAL  = ROOT / "data" / "final"
PLOT = ROOT / "plot"

# -------------------- Config --------------------
DATA_PATH = RAW / "q850_1000_1979_2025_JJA.nc"
VAR_NAME = "q"
G = 9.80665  #gravitational acceleration

HIGH_YEARS_CSV = FINAL / "ecs_high_years.csv"
LOW_YEARS_CSV = FINAL / "ecs_low_years.csv"

plot_extent = [110, 150, 20, 60]  # [lon_min, lon_max, lat_min, lat_max]
out_path = PLOT / "IWV_composite.png"

# -------------------- Read years --------------------
high_df = pd.read_csv(HIGH_YEARS_CSV)
low_df = pd.read_csv(LOW_YEARS_CSV)

years_high = (high_df["year"] if "year" in high_df.columns else high_df.iloc[:, 0]).dropna().astype(int).tolist()
years_low  = (low_df["year"]  if "year" in low_df.columns  else low_df.iloc[:, 0]).dropna().astype(int).tolist()

# -------------------- Load --------------------
ds = xr.open_dataset(DATA_PATH)
q = ds[VAR_NAME]

q = q.sortby("pressure_level", ascending=True)

# -------------------- Integrate --------------------
q_int_hPa = q.integrate("pressure_level")
iwv = (q_int_hPa * 100.0) / G  #hpa to pa

# -------------------- Yearly mean (JJA only) --------------------
iwv_year = iwv.groupby("valid_time.year").mean("valid_time")

iwv_high = iwv_year.sel(year=years_high)
iwv_low  = iwv_year.sel(year=years_low)

iwv_high_mean = iwv_high.mean("year")
iwv_low_mean  = iwv_low.mean("year")
iwv_diff = iwv_high_mean - iwv_low_mean
# -------------------- Plot --------------------
proj = ccrs.PlateCarree()
lon = ds["longitude"]
lat = ds["latitude"]

# color ranges
all_vals = xr.concat([iwv_high_mean, iwv_low_mean], dim="stack")
vmin = float(all_vals.quantile(0.02))
vmax = float(all_vals.quantile(0.98))
diff_lim = float(np.nanmax(np.abs(iwv_diff.values)))

fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={"projection": proj})


titles = [
    "IWV (1000-850 hPa HSST)",
    "IWV (1000-850 hP LSST)",
    "HSST - LSST"
]


data_list = [iwv_high_mean, iwv_low_mean, iwv_diff]
cmaps = ["viridis", "viridis", "Reds"]
vmins = [vmin, vmin, 0]
vmaxs = [vmax, vmax, diff_lim]

for ax, title, data, cmap, v0, v1 in zip(axes, titles, data_list, cmaps, vmins, vmaxs):
    ax.set_extent(plot_extent, crs=proj)
    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.5, linestyle="--")
    gl.right_labels = False
    gl.top_labels = False

    im = ax.pcolormesh(lon, lat, data, transform=proj, shading="auto", cmap=cmap, vmin=v0, vmax=v1)
    cb = plt.colorbar(im, ax=ax, orientation="horizontal", pad=0.05, fraction=0.06)
    cb.set_label("kg m$^{-2}$")
    ax.set_title(title, fontsize=10)

PLOT.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"[Saved] {out_path}")
