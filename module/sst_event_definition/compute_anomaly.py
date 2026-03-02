"""
1. Compute sea surface temperature (SST) anomaly
2. Define extreme SST event years (High SST, Low SST)
"""

import xarray as xr


def compute_jja_sst_anomaly_ts(
file_sst,
file_clim,
var_sst = "sst",
var_clim = "sst",
lon_range =(117,130),
lat_range =(33, 22),
):

    # 1) Load
    ds = xr.open_dataset(file_sst).rename({"valid_time": "time"})
    ds_clim = xr.open_dataset(file_clim)

    # --- 1. SST (K -> Â°C) ---
    sst = ds[var_sst] - 273.15
    clim = ds_clim[var_clim]

    # --- 2. JJA Anomaly ---
    anom = sst - clim
    anom_jja = anom.sel(time=anom.time.dt.month.isin([6, 7, 8]))

    # --- 3. ECS Domain ---
    anom_dom = anom_jja.sel(
    longitude=slice(lon_range[0], lon_range[1]),
    latitude=slice(lat_range[0], lat_range[1]),
    )

    # --- 4. Yearly JJA mean ---
    anom_year = anom_dom.groupby("time.year").mean("time")

    # 8) Spatial mean -> pandas Series
    ts = anom_year.mean(dim=["latitude", "longitude"]).to_series().sort_index()
    ts.index = ts.index.astype(int)
    ts.index.name = "year"
    ts.name = "jja_sst_anomaly"
    return ts

def split_high_low_years(ts):

   #Split years into High/Low based on mean Â x*std.
   

    ts = ts.dropna()

    mean = ts.mean()
    std = ts.std()
    coeff = 1     # <--- set the coefficient for the threshold here

    high_thr = mean + coeff * std
    low_thr  = mean - coeff * std

    high_years = ts.index[ts > high_thr].astype(int).tolist()
    low_years  = ts.index[ts < low_thr].astype(int).tolist()

    return high_years, low_years

