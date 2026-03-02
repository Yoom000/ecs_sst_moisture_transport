"""
Compute:
1. Yearly integrated water vapor flux (Q)
2. Q flux across specified boundaries
"""

import xarray as xr



G = 9.80665  # m s^-2


def compute_yearly_ivt_850_1000(file_q, file_u, file_v):
    ds_q = xr.open_dataset(file_q)
    ds_u = xr.open_dataset(file_u)
    ds_v = xr.open_dataset(file_v)

    q = ds_q["q"]
    u = ds_u["u"]
    v = ds_v["v"]

    qY = q.groupby("valid_time.year").mean("valid_time").sortby("pressure_level")
    uY = u.groupby("valid_time.year").mean("valid_time").sortby("pressure_level")
    vY = v.groupby("valid_time.year").mean("valid_time").sortby("pressure_level")

    Qx_year = (qY * uY).integrate("pressure_level") * 100.0 / G
    Qy_year = (qY * vY).integrate("pressure_level") * 100.0 / G

    Qx_year = Qx_year.assign_attrs({"units": "kg m^-1 s^-1", "long_name": "IVT_x (850-1000 hPa)"})
    Qy_year = Qy_year.assign_attrs({"units": "kg m^-1 s^-1", "long_name": "IVT_y (850-1000 hPa)"})

    return Qx_year, Qy_year


def extract_west_boundary(
    Qx_year,
    lon_west,
    lat_range
):
    lat1, lat2 = lat_range
    lat_min = min(lat1, lat2)
    lat_max = max(lat1, lat2)

    prof = (
    Qx_year
    .sel(longitude=lon_west, method="nearest")
    .sel(latitude=slice(lat_max, lat_min))
    .sortby("latitude")
    )

    prof = prof.assign_attrs({
        "long_name": "West boundary moisture flux (eastward positive)",
        "units": "kg m^-1 s^-1",
        "note": "Positive means flux directed eastward"
    })
    return prof


def extract_south_boundary(
    Qy_year,
    lat_south,
    lon_range
):
    
    lon_min, lon_max = lon_range

    prof = (
        Qy_year
        .sel(latitude=lat_south, method="nearest")
        .sel(longitude=slice(lon_min, lon_max))
        .sortby("longitude")
    )

    prof = prof.assign_attrs({
        "long_name": "South boundary moisture flux (northward positive)",
        "units": "kg m^-1 s^-1",
        "note": "Positive means flux directed northward "
    })
    return prof

import numpy as np
import pandas as pd

R_EARTH = 6_371_000.0  # m


def integrate_west_boundary(Qx_west_profile, ddeg=1.0):
    #
    prof = Qx_west_profile.sortby("latitude")

    dy_m = np.deg2rad(ddeg) * R_EARTH  # meters per ddeg latitude

    vals = prof.values  # (nyear, nlat)
    total = np.trapz(vals, dx=dy_m, axis=1)  # (nyear,) kg/s

    years = prof["year"].values.astype(int)
    return pd.Series(total, index=years, name="west_total_kg_per_s")


def integrate_south_boundary(Qy_south_profile, lat_south, ddeg=1.0):
    # 
    prof = Qy_south_profile.sortby("longitude")

    phi = np.deg2rad(lat_south)
    dx_m = np.deg2rad(ddeg) * R_EARTH * np.cos(phi)  # meters per ddeg longitude at lat_south

    vals = prof.values  # (nyear, nlon)
    total = np.trapz(vals, dx=dx_m, axis=1)  # (nyear,) kg/s

    years = prof["year"].values.astype(int)
    return pd.Series(total, index=years, name="south_total_kg_per_s")
