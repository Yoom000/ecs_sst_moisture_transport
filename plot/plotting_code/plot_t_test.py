"""
Plot t-test results.
"""


from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind


def plot_flux_high_low(
    flux_csv,
    high_years_csv,
    low_years_csv,
    out_png,
    title="",
    xlabel="Flux (kg/s)",
):
    # --- load data ---
    s = pd.read_csv(flux_csv, index_col=0).squeeze()
    s.index = s.index.astype(int)

    high_years = pd.read_csv(high_years_csv)["year"].astype(int).tolist()
    low_years = pd.read_csv(low_years_csv)["year"].astype(int).tolist()

    high = s.loc[high_years].dropna()
    low = s.loc[low_years].dropna()

    # --- Welch t-test ---
    t_stat, p_val = ttest_ind(high.values, low.values, equal_var=False)

    # --- mean ± SEM ---
    def mean_sem(x):
        x = np.asarray(x, dtype=float)
        mean = np.mean(x)
        sem = np.std(x, ddof=1) / np.sqrt(len(x))
        return mean, sem

    m_high, sem_high = mean_sem(high.values)
    m_low, sem_low = mean_sem(low.values)

    # --- plotting ---
    fig, ax = plt.subplots(figsize=(8, 3))

    y_high = 0
    y_low = 1

    rng = np.random.default_rng(0)

    # individual points
    ax.scatter(high.values, [y_high]*len(high), s=40, label="Individual years")
    ax.scatter(low.values, [y_low]*len(low), s=40)
    # mean ± SEM
    ax.errorbar(m_high, y_high, xerr=sem_high, fmt="o", capsize=6)
    ax.errorbar(m_low, y_low, xerr=sem_low, fmt="o", capsize=6)
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_yticks([y_high, y_low])
    ax.set_yticklabels(["High SST", "Low SST"])

    ax.set_xlabel(xlabel)
    ax.set_title(title)

    # text box
    text = (
        f"Welch t-test\n"
        f"t = {t_stat:.2f}\n"
        f"p = {p_val:.4f}\n"
        f"n_high = {len(high)}, n_low = {len(low)}"
    )

    ax.text(
        0.98, 0.95,
        text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        bbox=dict(boxstyle="round", alpha=0.9),
    )

    fig.tight_layout()
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    print("[OK] Saved:", out_png)

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]

    plot_flux_high_low(
        flux_csv=root / "data/final/KWB_vapor_total.csv",
        high_years_csv=root / "data/final/ecs_high_years.csv",
        low_years_csv=root / "data/final/ecs_low_years.csv",
        out_png=root / "plot/west_flux_ttest.png",
        title="West boundary moisture inflow",
        xlabel="Q flux west",
    )

    plot_flux_high_low(
        flux_csv=root / "data/final/KSB_vapor_total.csv",
        high_years_csv=root / "data/final/ecs_high_years.csv",
        low_years_csv=root / "data/final/ecs_low_years.csv",
        out_png=root / "plot/south_flux_ttest.png",
        title="South boundary moisture inflow",
        xlabel="Q flux south",
    )
