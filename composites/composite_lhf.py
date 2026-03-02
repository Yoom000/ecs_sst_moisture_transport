"""
plot composite latent heat flux (lhf) fields during high-SST and low-SST years.
"""

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from matplotlib.ticker import FormatStrFormatter

# dir settings
ROOT = Path(__file__).resolve().parents[1]                 
FILE_PATH = ROOT / "data" / "raw" / "LHF_landmasked.nc"

HIGH_YEARS_CSV = ROOT / "data" / "final" / "ecs_high_years.csv"
LOW_YEARS_CSV  = ROOT / "data" / "final" / "ecs_low_years.csv"

VAR_NAME = "slhf"
REGION = dict(lon_min=90, lon_max=180, lat_min=0, lat_max=60)

OUT_DIR = ROOT / "plot"
OUT_DIR.mkdir(exist_ok=True)
OUT_PNG = OUT_DIR / "LHF_composite.png"

# Read years from CSV
high_df = pd.read_csv(HIGH_YEARS_CSV)
low_df  = pd.read_csv(LOW_YEARS_CSV)

HIGH_YEARS = (high_df["year"] if "year" in high_df.columns else high_df.iloc[:, 0]).dropna().astype(int).tolist()
LOW_YEARS  = (low_df["year"]  if "year" in low_df.columns  else low_df.iloc[:, 0]).dropna().astype(int).tolist()

# Load and preprocess
ds = xr.open_dataset(FILE_PATH)
da = ds[VAR_NAME].sortby("latitude")

# Group by year (yearly mean over valid_time)
# =========================================================
slhf_yearly = da.groupby("valid_time.year").mean("valid_time", skipna=True)
print("Available years:", slhf_yearly["year"].values)

# =========================================================
# Compute composites
# =========================================================
comp_high = slhf_yearly.sel(year=HIGH_YEARS).mean("year", skipna=True)
comp_low  = slhf_yearly.sel(year=LOW_YEARS).mean("year", skipna=True)
diff      = comp_high - comp_low

# =========================================================
# Convert J/m² -> W/m² + sign flip
# =========================================================
comp_high_flux = -(comp_high / 86400.0)
comp_low_flux  = -(comp_low  / 86400.0)
diff_flux      = -(diff      / 86400.0)

for da_ in [comp_high_flux, comp_low_flux, diff_flux]:
    da_.attrs["units"] = "W m$^{-2}$"

# =========================================================
# Subplot flow (like your IWV example)
# =========================================================
proj = ccrs.PlateCarree()
lon = comp_high_flux["longitude"]
lat = comp_high_flux["latitude"]

plot_extent = [REGION["lon_min"], REGION["lon_max"], REGION["lat_min"], REGION["lat_max"]]

# color ranges (robust) for High/Low
all_vals = xr.concat([comp_high_flux, comp_low_flux], dim="stack")
vmin = float(all_vals.quantile(0.02))
vmax = float(all_vals.quantile(0.98))

# diff range (0 -> diff_lim, Reds)
diff_lim = float(np.nanmax(np.abs(diff_flux.values)))

fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={"projection": proj})

titles = [
    "LHF (W m$^{-2}$) HSST",
    "LHF (W m$^{-2}$) LSST",
    "Difference (High - Low)"
]

data_list = [comp_high_flux, comp_low_flux, diff_flux]
cmaps = ["RdBu_r", "RdBu_r", "RdBu_r"]
vmins = [-150, -150, -20]
vmaxs = [150, 150, 20]

for ax, title, data, cmap, v0, v1 in zip(axes, titles, data_list, cmaps, vmins, vmaxs):
    ax.set_extent(plot_extent, crs=proj)
    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linewidth=0.5)

    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.5, linestyle="--")
    gl.right_labels = False
    gl.top_labels = False

    im = ax.pcolormesh(lon, lat, data.values,
                       transform=proj, shading="auto",
                       cmap=cmap, vmin=v0, vmax=v1)

    cb = plt.colorbar(im, ax=ax, orientation="horizontal", pad=0.05, fraction=0.06, extend ="both")
    cb.set_label(comp_high_flux.attrs.get("units", "W m$^{-2}$"))
    ax.set_title(title, fontsize=10)
    cb.ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
plt.show()

print("[Saved]")
print(OUT_PNG)
