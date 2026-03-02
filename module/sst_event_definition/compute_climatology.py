"""
Compute sea surface temperature (SST) climatology and save it as a NetCDF (.nc) file.
"""
 
from pathlib import Path
import xarray as xr

def compute_jja_climatology(
    file_in,
    file_out,
    var="sst",
    base_start=1991,
    base_end=2020,
):
    """
    To calculate JJA climatology(1991 to 2020)
    """

    file_in = Path(file_in)
    file_out = Path(file_out)
    file_out.parent.mkdir(parents=True, exist_ok=True)

    # --- Load ---
    ds = xr.open_dataset(file_in).rename({"valid_time": "time"})

    # --- Kelvin to Celsius ---
    da = ds[var] - 273.15

    # ---  JJA for climatology  ---
    da_jja = da.sel(time=da.time.dt.month.isin([6, 7, 8]))
    da_ref = da_jja.sel(
        time=slice(f"{base_start}-06-01", f"{base_end}-08-31")
    )

    # ---Climatology JJA mean ---
    clim_month = da_ref.groupby("time.month").mean("time")
    clim_jja = clim_month.mean("month")

    clim_jja.name = f"{var}"

    # --- to nc file  ---
    clim_jja.to_dataset().to_netcdf(
        file_out,
        format="NETCDF4",
        encoding={clim_jja.name: {"zlib": True, "complevel": 4, "dtype": "float32"}},
    )
    print(f"Saved: {file_out}")

