from pathlib import Path
import math
import pytest
import pandas as pd
from winnipeg311.analysis import load_daily_calls, prepare_daily_series, summaries

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "311_incoming_calls_by_day_20260217.csv"

@pytest.fixture(scope="module")
def study():
    raw = load_daily_calls(DATA)
    return prepare_daily_series(raw)

def test_source_has_no_duplicate_dates():
    raw = load_daily_calls(DATA)
    assert len(raw) == 6346
    assert raw["date"].is_unique
    assert raw["date"].min() == pd.Timestamp("2008-10-03")
    assert raw["date"].max() == pd.Timestamp("2026-02-17")

def test_missing_day_and_imputation(study):
    frame, missing = study
    assert missing == ["2024-03-09"]
    assert frame.loc["2024-03-09", "calls"] == 1027
    assert not frame["calls"].isna().any()

def test_full_year_window(study):
    frame, _ = study
    assert str(frame.index.min().date()) == "2009-01-01"
    assert str(frame.index.max().date()) == "2025-12-31"
    assert len(frame) == 6209

def test_reported_year_totals(study):
    stats = summaries(study[0])
    years = stats["year_totals"]
    assert years.loc[2012] == 1336437
    assert years.loc[2021] == 530030
    assert years.loc[2024] == 675205
    assert years.loc[2025] == 815788

def test_2025_increase(study):
    stats = summaries(study[0]); means = stats["year_means"]
    assert math.isclose(means.loc[2024],1844.8224043716,abs_tol=1e-7)
    assert math.isclose(means.loc[2025],2235.0356164384,abs_tol=1e-7)
    assert math.isclose(stats["percent_increase_2025_vs_2024"],21.151803617632915,abs_tol=1e-7)

def test_peak_months(study):
    stats = summaries(study[0])
    assert stats["highest_year_month"] == "2013-03"
    assert stats["lowest_year_month"] == "2021-10"

def test_reported_month_extrema(study):
    summary = summaries(study[0])
    assert summary["monthly_totals"].loc[(2013, 3)] == 130524
    assert summary["monthly_totals"].loc[(2021, 10)] == 37906
