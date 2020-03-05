import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.units as munits

INPUT = "parsed_hp.csv"


def mad(x):
    return np.median(np.abs(x - np.median(x)))


def clean_data(df, filter_window=7, filter_offset=3):
    df.columns = df.columns.str.strip()
    df = df.dropna()
    df = df.sort_values("Japan Standard Time")
    rolling_median = (
        df["Kills"]
        .rolling(filter_window, center=True)
        .median()
        .fillna(method="ffill")
        .fillna(method="bfill")
        .fillna(0)
    )
    rolling_mad = (
        df["Kills"]
        .rolling(filter_window, center=True)
        .apply(mad, raw=True)
        .fillna(method="ffill")
        .fillna(method="bfill")
        .fillna(0)
    )
    lower_bound = rolling_median - filter_offset * rolling_mad
    upper_bound = rolling_median + filter_offset * rolling_mad
    index = (lower_bound <= df["Kills"]) & (df["Kills"] <= upper_bound)
    df = df[index]
    df = df[df.iloc[:, 1] != 3]
    return df


def make_dps_chart(df, output="kps.png"):
    for _ in range(10):
        df = df[df["Kills"] < df["Kills"].shift(-1).fillna(0)]
    # for _ in range(5):
    #     df = df[df["Kills"] > df["Kills"].shift(-1).fillna(0)]
    x = df.iloc[4:, 0]
    y = df["Kills"].diff(4)[4:] / df["Japan Standard Time"].diff(4).dt.total_seconds()[4:]
    x = x[y >= 0]
    y = y[y >= 0]
    # y = y.rolling(4, center=True).mean()
    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(14, 7.5))
    ax.plot(x, y, marker='o', markersize=3, linestyle="None")
    ax.set_title("JP Case Files raid KPS")
    ax.set_xlabel("Japan Standard Time")
    ax.set_ylabel("Kills per second")
    ax.set_ylim(top=680, bottom=-30)
    fig.savefig(output, dpi=200, bbox_inches='tight')


def make_hp_chart(df, output="kills.png"):
    x = df["Japan Standard Time"]
    y = df["Kills"] / 1000000
    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(14, 7.5))
    ax.plot(x, y)
    ax.set_title("JP Case Files raid kills count")
    ax.set_xlabel("Japan Standard Time")
    ax.set_ylabel("Kills (millions)")
    fig.savefig(output, dpi=200, bbox_inches='tight')


if __name__ == "__main__":
    register_matplotlib_converters()
    converter = mdates.ConciseDateConverter()
    munits.registry[np.datetime64] = converter
    all_df = pd.read_csv(INPUT, parse_dates=[0, 2], dtype={"Kills": "Int64"})
    all_df = clean_data(all_df)
    all_df.to_csv("cleaned_data.csv", index=False)
    make_hp_chart(all_df)
    make_dps_chart(all_df)
