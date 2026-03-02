"""
Perform a t-test for Q flux during High and Low SST years.
"""

import pandas as pd
from scipy.stats import ttest_ind


def ttest_flux(west_csv, south_csv, high_csv, low_csv):

    west = pd.read_csv(west_csv, index_col=0).squeeze()
    south = pd.read_csv(south_csv, index_col=0).squeeze()

    high_years = pd.read_csv(high_csv)["year"].tolist()
    low_years  = pd.read_csv(low_csv)["year"].tolist()

    west_high = west.loc[high_years]
    west_low  = west.loc[low_years]

    south_high = south.loc[high_years]
    south_low  = south.loc[low_years]

    t_west, p_west = ttest_ind(west_high, west_low, equal_var=False)
    t_south, p_south = ttest_ind(south_high, south_low, equal_var=False)

    return {
        "west": {"t": t_west, "p": p_west, "mean_high": west_high.mean(), "mean_low": west_low.mean()},
        "south": {"t": t_south, "p": p_south, "mean_high" :south_high.mean(), "mean_low": south_low.mean()},
    }
