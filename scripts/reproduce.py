"""Reproduce the six figures and summary tables from the archived source CSV.

Usage from repository root: python scripts/reproduce.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from winnipeg311.analysis import load_daily_calls, prepare_daily_series, summaries

DATA = ROOT / "data" / "311_incoming_calls_by_day_20260217.csv"
OUT = ROOT / "outputs"
COLORS = {2023: "#92400E", 2024: "#D97706", 2025: "#C2410C"}


def finish(name):
    plt.tight_layout()
    plt.savefig(OUT / f"{name}.png", dpi=185, bbox_inches="tight")
    plt.close()


def main():
    OUT.mkdir(exist_ok=True)
    data, imputed = prepare_daily_series(load_daily_calls(DATA))
    stats = summaries(data)
    stats["year_totals"].rename("total_calls").to_csv(OUT / "yearly_totals.csv")
    stats["monthly_totals"].rename("total_calls").to_csv(OUT / "monthly_totals.csv")
    stats["monthly_means"].rename("average_daily_calls").to_csv(OUT / "monthly_daily_averages.csv")

    plt.figure(figsize=(9, 4.8))
    stats["year_totals"].plot.bar(color="#D97706", edgecolor="#7C2D12")
    plt.title("Total 311 Incoming Calls by Year (2009–2025)")
    plt.xlabel("Year");plt.ylabel("Total calls")
    finish("figure_1_yearly_totals")

    subset=data[data.year.isin([2023,2024,2025])]
    recent=subset.groupby(["year","month"])["calls"].sum()
    plt.figure(figsize=(9,4.8))
    for year in [2023,2024,2025]:
        s=recent.loc[year]
        plt.plot(s.index,s.values,marker="o",label=str(year),color=COLORS[year])
    plt.title("Monthly Total 311 Calls (2023–2025)")
    plt.xlabel("Month");plt.ylabel("Calls per month");plt.xticks(range(1,13));plt.legend()
    finish("figure_2_recent_monthly_totals")

    plt.figure(figsize=(9,4.8))
    for year in [2024,2025]:
        s=stats["monthly_means"].loc[year]
        plt.plot(s.index,s.values,marker="o",label=str(year),color=COLORS[year])
    plt.title("Monthly Average Daily Calls (2024 vs 2025)")
    plt.xlabel("Month");plt.ylabel("Average daily calls");plt.xticks(range(1,13));plt.legend()
    finish("figure_3_monthly_daily_average")

    recent=data.loc["2023-01-01":"2025-12-31"].copy()
    split=recent.groupby([pd.Grouper(freq="MS"),"is_weekend"])["calls"].mean().unstack()
    plt.figure(figsize=(9,4.8))
    plt.plot(split.index,split[False],marker="o",label="Weekday",color="#C2410C")
    plt.plot(split.index,split[True],marker="o",label="Weekend",color="#D97706")
    plt.title("Average Daily Calls: Weekdays vs Weekends (2023–2025)")
    plt.xlabel("Month");plt.ylabel("Average daily calls");plt.legend()
    ax=plt.gca();ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45,ha="right")
    finish("figure_4_weekday_weekend_monthly")

    rolling=data["calls"]
    plt.figure(figsize=(9,4.8))
    plt.plot(rolling.index,rolling.rolling(30,min_periods=15).mean(),label="30-day average",color="#D97706")
    plt.plot(rolling.index,rolling.rolling(90,min_periods=45).mean(),label="90-day average",color="#C2410C")
    plt.axvspan(pd.Timestamp("2025-01-01"),pd.Timestamp("2025-12-31"),alpha=.14,color="#D97706")
    plt.xlim(pd.Timestamp("2008-07-01"),pd.Timestamp("2026-07-01"))
    plt.title("Winnipeg 311 Calls: Rolling-Average Trends (2009–2025)")
    plt.xlabel("Date");plt.ylabel("Average daily calls");plt.legend()
    finish("figure_5_rolling_averages")

    plt.figure(figsize=(7.8,5))
    bp=plt.boxplot([data.loc[~data.is_weekend,"calls"],data.loc[data.is_weekend,"calls"]],
                   tick_labels=["Weekday","Weekend"],patch_artist=True)
    for obj,color in zip(bp["boxes"],["#D97706","#C2410C"]):
        obj.set(facecolor=color,edgecolor="#7C2D12")
    plt.title("Weekday vs Weekend Daily Calls (2009–2025)")
    plt.ylabel("Daily calls")
    finish("figure_6_weekday_weekend_boxplot")

    assert imputed == ["2024-03-09"], f"Unexpected missing dates: {imputed}"
    print("Imputed dates:",imputed)
    print(f"2024 mean {stats['year_means'].loc[2024]:,.2f}; 2025 mean {stats['year_means'].loc[2025]:,.2f}")
    print(f"Change {stats['percent_increase_2025_vs_2024']:.2f}%")
    print("Highest year:",stats["highest_year"],"Lowest year:",stats["lowest_year"])
    print("Figures and summary tables saved to",OUT)


if __name__ == "__main__":
    main()
