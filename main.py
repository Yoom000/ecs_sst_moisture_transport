"""
Main analysis script that computes and saves all core results.

Plotting and composite figures should be generated using scripts in
the plot/ and composites/ directories after running this script.
"""

import xarray as xr
import pandas as pd
from pathlib import Path

# 1. climatology calculation
from module.sst_event_definition.compute_climatology import compute_jja_climatology

# 2. anomaly calculation -> define high/low SST years 
from module.sst_event_definition.compute_anomaly import (
    compute_jja_sst_anomaly_ts,
    split_high_low_years,
)
# 3. moisture flux calculation
from module.moisture_flux.compute_qflux import (
    compute_yearly_ivt_850_1000,
    extract_west_boundary,
    extract_south_boundary,
    integrate_west_boundary,
    integrate_south_boundary,
)
# 4. t-test for vapor fulx
from module.t_test.t_test_vaporflux  import ttest_flux



def main():
    root = Path(__file__).resolve().parent
    (root / "data" / "interim").mkdir(parents=True, exist_ok=True)
    (root / "data" / "final").mkdir(parents=True, exist_ok=True)

    # --- 1. climatology calculation ---
    file_in = root / "data" /"raw"/ "SST_025_1979_2025_land_masked.nc"
    file_clim = root / "data" / "interim" / "SST_JJA_clim_1991-2020.nc"

    compute_jja_climatology(file_in, file_clim)

    print("[OK] Climatology done")

    # --- 2.  anomaly calculation ---
    ts = compute_jja_sst_anomaly_ts(
        file_sst=file_in,
        file_clim=file_clim,
        var_sst="sst",
        var_clim="sst",
        lon_range=(117, 130),  # <-- Insert your interested domain(lon, lat) for the SST anomaly calcuation
        lat_range=(33, 22),
    )

    out_csv = root / "data" / "interim" / "ecs_jja_sst_anomaly_sst.csv"
    ts.to_csv(out_csv, header=True)

    # --- 3. High/Low year split ---
    high_years, low_years = split_high_low_years(ts)

    print("[OK] High years:", high_years)
    print("[OK] Low years :", low_years)
    print("[OK] Saved anomaly time series:", out_csv)
    print(ts.head())

    pd.Series(high_years, name="year").to_csv(root / "data" / "final" / "ecs_high_years.csv",index=False)
    pd.Series(low_years, name="year").to_csv(root / "data" / "final" / "ecs_low_years.csv", index=False)  

    # --- 4. Qflux calculation (IVT -> boundary profiles -> line integral) ---

    # 4.1 ERA5 q/u/v (JJA, 850-1000 hPa)data
    file_q = root / "data" / "raw" / "q850_1000_1979_2025_JJA.nc"
    file_u = root / "data" / "raw" / "U_wind_850_1000_1979_2025_JJA.nc"
    file_v = root / "data" / "raw" / "V_wind_850_1000_1979_2025_JJA.nc"

    Qx_year, Qy_year = compute_yearly_ivt_850_1000(file_q, file_u, file_v)

    # 4.2 Korea West boundary: lon=124E, lat=33-43
    Qx_west_profile = extract_west_boundary(Qx_year, lon_west=124.0, lat_range=(33.0, 43.0))

    # 4.3 South boundary: lat=33N, lon=124-130
    Qy_south_profile = extract_south_boundary(Qy_year, lat_south=33.0, lon_range=(124.0, 130.0))

    # 4.4 Line integral
    west_total = integrate_west_boundary(Qx_west_profile, ddeg=1.0)
    south_total = integrate_south_boundary(Qy_south_profile, lat_south=33.0, ddeg=1.0)

    # 4.5 Save
    in_west = root / "data" / "final" / "KWB_vapor_total.csv"
    in_south = root / "data" / "final" / "KSB_vapor_total.csv"
    west_total.to_csv(in_west, header=True)
    south_total.to_csv(in_south, header=True)

    # --- 5. t-test between high/low sst vapor flux ---
    result = ttest_flux(
        west_csv=root / "data/final/KWB_vapor_total.csv",
        south_csv=root / "data/final/KSB_vapor_total.csv",
        high_csv=root / "data/final/ecs_high_years.csv",
        low_csv=root / "data/final/ecs_low_years.csv",
    )
    #save
    ttest = root / "data/final/WV_ttest.csv"

    df = pd.DataFrame({
    "mean_high": [result["west"]["mean_high"], result["south"]["mean_high"]],
    "mean_low": [result["west"]["mean_low"], result["south"]["mean_low"]],
    "t_value": [result["west"]["t"], result["south"]["t"]],
    "p_value": [result["west"]["p"], result["south"]["p"]],
    }, index=["west", "south"])

    df.index.name = "boundary"

    df.to_csv(ttest)

    print(df)

if __name__ == "__main__":

    main()


