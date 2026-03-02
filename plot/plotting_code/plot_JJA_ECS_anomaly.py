"""
Plot SST anomalies.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress


def plot_ecs_jja_sst_anomaly_stem(root: Path):

    csv_path = root / "data" / "interim" / "ecs_jja_sst_anomaly_sst.csv"
    out_png  = root / "plot" / "ecs_jja_sst_anomaly.png"

    # --- Load ---
    df = pd.read_csv(csv_path, index_col=0)
    ts = df.iloc[:, 0]
    ts.index = ts.index.astype(int)
    ts = ts.sort_index()

    # --- Trend ---
    years = ts.index.values.astype(float)
    res = linregress(years, ts.values)
    trend_line = res.intercept + res.slope * years

    mean_val = ts.mean()
    std_val = ts.std()
    upper = mean_val + std_val
    lower = mean_val - std_val

    # --- Plot ---
    plt.figure(figsize=(9, 4.8))
    markerline, stemlines, baseline = plt.stem(ts.index, ts.values)
    plt.setp(stemlines,color ='k', linewidth=1.3)
    plt.setp(markerline,color='k', markersize=5)

    plt.plot(ts.index, trend_line,color='k', lw=2.3)
    plt.axhline(lower,color ='r', linestyle="--", lw=1)
    plt.axhline(upper,color ='r', linestyle="--", lw=1, label=r"$\pm$1 std")

    plt.title("East China Sea JJA SST Anomaly (°C)")
    plt.xlabel("Year")
    plt.ylabel("Anomaly (°C)")
    plt.grid(True, axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200)
    plt.show()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    plot_ecs_jja_sst_anomaly_stem(root)
