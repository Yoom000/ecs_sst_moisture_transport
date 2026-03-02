"""
Plot composite wind fields during high-SST and low-SST years.
"""
from pathlib import Path
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# -------------------- Path --------------------
ROOT = Path(__file__).resolve().parents[1]
RAW  = ROOT / "data" / "raw"
FINAL = ROOT / "data" / "final"
PLOT = ROOT / "plot"

# -------------------- Config --------------------
U_PATH = RAW / "U_wind_850_1000_1979_2025_JJA.nc"  
V_PATH = RAW / "V_wind_850_1000_1979_2025_JJA.nc"  
U_NAME, V_NAME = "u", "v"         
LEVEL = 1000                    
STRIDE = 4                         

HIGH_YEARS_CSV = FINAL / "ecs_high_years.csv"
LOW_YEARS_CSV  = FINAL / "ecs_low_years.csv"

plot_extent = [90, 180, 0, 60]

# -------------------- Read years --------------------
high_df = pd.read_csv(HIGH_YEARS_CSV)
low_df  = pd.read_csv(LOW_YEARS_CSV)

years_high = (high_df["year"] if "year" in high_df.columns else high_df.iloc[:, 0]).dropna().astype(int).tolist()
years_low  = (low_df["year"]  if "year" in low_df.columns  else low_df.iloc[:, 0]).dropna().astype(int).tolist()

# -------------------- Load --------------------
dsu = xr.open_dataset(U_PATH)
dsv = xr.open_dataset(V_PATH)
u = dsu[U_NAME]
v = dsv[V_NAME]

# Select 1000 hPa (nearest in case float precision)
u1000 = u.sel(pressure_level=LEVEL, method="nearest")
v1000 = v.sel(pressure_level=LEVEL, method="nearest")

# -------------------- Yearly JJA mean --------------------
u_year = u1000.groupby("valid_time.year").mean("valid_time")
v_year = v1000.groupby("valid_time.year").mean("valid_time")

years_high_in = [y for y in years_high if y in u_year.year.values]
years_low_in  = [y for y in years_low  if y in u_year.year.values]

if len(years_high_in) == 0 or len(years_low_in) == 0:
    raise ValueError(
        f"No overlapping years found. "
        f"high_in={years_high_in}, low_in={years_low_in}, "
        f"available={u_year.year.values.min()}–{u_year.year.values.max()}"
    )

# -------------------- Composites --------------------
u_high = u_year.sel(year=years_high_in).mean("year")
v_high = v_year.sel(year=years_high_in).mean("year")
u_lowc = u_year.sel(year=years_low_in ).mean("year")
v_lowc = v_year.sel(year=years_low_in ).mean("year")

u_diff = u_high - u_lowc
v_diff = v_high - v_lowc

# -------------------- Prepare for quiver --------------------
proj = ccrs.PlateCarree()

lon = dsu["longitude"]
lat = dsu["latitude"]
lon2d, lat2d = np.meshgrid(lon.values, lat.values)

lon_s = lon2d[::STRIDE, ::STRIDE]
lat_s = lat2d[::STRIDE, ::STRIDE]

uH_s = u_high.values[::STRIDE, ::STRIDE]
vH_s = v_high.values[::STRIDE, ::STRIDE]
uL_s = u_lowc.values[::STRIDE, ::STRIDE]
vL_s = v_lowc.values[::STRIDE, ::STRIDE]
uD_s = u_diff.values[::STRIDE, ::STRIDE]
vD_s = v_diff.values[::STRIDE, ::STRIDE]

#-----------------Plotting----------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={"projection": proj})
titles = [
    f"1000 hPa Wind HIGH-SST composite",
    f"1000 hPa Wind LOW-SST composite",
    f"(High - Low)"
]

for ax, title in zip(axes, titles):
    ax.set_extent(plot_extent, crs=proj)
    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.5, linestyle="--")
    gl.right_labels = False
    gl.top_labels = False
    ax.set_title(title, fontsize=11)

# High composite
Q1 = axes[0].quiver(lon_s, lat_s, uH_s, vH_s, transform=proj, regrid_shape=25, scale=None)
axes[0].quiverkey(Q1, 0.92, -0.05, 10, "10 m s$^{-1}$", labelpos="E")

# Low composite
Q2 = axes[1].quiver(lon_s, lat_s, uL_s, vL_s, transform=proj, regrid_shape=25, scale=None)
axes[1].quiverkey(Q2, 0.92, -0.05, 10, "10 m s$^{-1}$", labelpos="E")

# Diff composite
Q3 = axes[2].quiver(lon_s, lat_s, uD_s, vD_s, transform=proj, regrid_shape=25,
                    color="tab:red", scale=None)
axes[2].quiverkey(Q3, 0.92, -0.05, 5, "5 m s$^{-1}$", labelpos="E")


out_path = PLOT / "Composite_Wind1000hPa.png"

plt.tight_layout()
plt.savefig(out_path, dpi=300)
plt.close()
