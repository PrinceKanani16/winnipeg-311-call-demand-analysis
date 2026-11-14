"""Reproducible data preparation and descriptive statistics for Winnipeg 311.

Analysis uses the archived CSV, not a live API response. This ensures that the
reported 2009–2025 statistics are reproducible even as city data are updated.
"""
from pathlib import Path
import pandas as pd

START = pd.Timestamp("2009-01-01")
END = pd.Timestamp("2025-12-31")


def load_daily_calls(csv_path: str | Path) -> pd.DataFrame:
    """Read the City's original five-column file and validate its dates/counts."""
    data = pd.read_csv(csv_path, dtype=str)
    required = {"Year", "Month Number", "Day", "Total Incoming Calls"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing source fields: {sorted(missing)}")
    for name in ("Year", "Month Number", "Day", "Total Incoming Calls"):
        values = data[name].str.replace(",", "", regex=False)
        data[name] = pd.to_numeric(values, errors="raise")
    for col in ("Year", "Month Number", "Day", "Total Incoming Calls"):
        if data[col].isna().any():
            raise ValueError(f"Null values in {col}")
    if (data["Total Incoming Calls"] < 0).any():
        raise ValueError("Daily calls cannot be negative")
    data["date"] = pd.to_datetime(dict(
        year=data["Year"], month=data["Month Number"], day=data["Day"]
    ), errors="raise")
    if data["date"].duplicated().any():
        raise ValueError("Repeated dates in input dataset")
    return data.sort_values("date").reset_index(drop=True)


def prepare_daily_series(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Reindex every date and linearly impute gaps with adjacent days.

    Returns a study-window DataFrame plus the exact imputed ISO dates.
    """
    dates = pd.date_range(raw["date"].min(), raw["date"].max(), freq="D")
    values = raw.set_index("date")["Total Incoming Calls"].astype(float).reindex(dates)
    missing = values[values.isna()].index
    if missing.min() == dates.min() or missing.max() == dates.max():
        raise ValueError("Cannot impute missing endpoints")
    values = values.interpolate(method="linear", limit_area="inside")
    if values.isna().any():
        raise ValueError("Interpolation did not resolve all gaps")
    out = values.loc[START:END].to_frame(name="calls")
    if out.empty or out.index.min() != START or out.index.max() != END:
        raise ValueError("The source file does not cover all full years 2009–2025")
    out.index.name = "date"
    out["year"] = out.index.year
    out["month"] = out.index.month
    out["is_weekend"] = out.index.dayofweek >= 5
    return out, [d.strftime("%Y-%m-%d") for d in missing]


def summaries(series: pd.DataFrame) -> dict:
    """Compute the main descriptive summaries used in the report."""
    yearly = series.groupby("year")["calls"].sum()
    means = series.groupby("year")["calls"].mean()
    monthly_total = series.groupby(["year", "month"])["calls"].sum()
    monthly_avg = series.groupby(["year", "month"])["calls"].mean()
    relative = (means.loc[2025] / means.loc[2024] - 1) * 100.0
    return {
        "year_totals": yearly,
        "year_means": means,
        "monthly_totals": monthly_total,
        "monthly_means": monthly_avg,
        "percent_increase_2025_vs_2024": float(relative),
        "highest_year": int(yearly.idxmax()),
        "lowest_year": int(yearly.idxmin()),
        "highest_year_month": "%04d-%02d" % monthly_total.idxmax(),
        "lowest_year_month": "%04d-%02d" % monthly_total.idxmin(),
    }
