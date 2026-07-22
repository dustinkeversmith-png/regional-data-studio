"""Join monthly Oregon fire proxies to monthly AMOC values and compute correlations."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from pipeline_common import PROCESSED, number, read_csv, write_csv, years_from_env


FIELDS = [
    "date",
    "year",
    "month",
    "amoc_transport_sv",
    "amoc_anomaly_sv",
    "oregon_fire_count",
    "oregon_active_fire_points",
    "oregon_acres_burned_estimate",
    "mean_frp",
    "max_frp",
    "monthly_fire_points",
    "monthly_sum_frp",
    "monthly_acres_burned_estimate",
    "rolling_3mo_fire_points",
    "rolling_12mo_fire_points",
    "rolling_12mo_amoc",
]


INTERPRETATION = (
    "This panel measures exploratory statistical relationships between AMOC time-series changes and "
    "Oregon wildfire activity proxies. It does not prove AMOC causes Oregon fire spread. Strong apparent "
    "correlations should be checked against drought, temperature, wind, precipitation, ENSO, PDO, fuel "
    "moisture, and ignition variables."
)


def main() -> None:
    start_year, end_year = years_from_env()
    fire_rows = {row["date"]: row for row in read_csv(PROCESSED / "monthly_fire_metrics.csv")}
    amoc_rows = {row["date"]: row for row in read_csv(PROCESSED / "amoc_monthly.csv")}

    rows = build_joined_rows(fire_rows, amoc_rows, start_year, end_year)
    rows = add_rolling(rows)
    summary = correlation_summary(rows)

    write_csv(PROCESSED / "fire_amoc_joined_monthly.csv", rows, FIELDS)
    Path(PROCESSED / "fire_amoc_correlation_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(rows)} joined monthly rows")
    print("Wrote fire_amoc_correlation_summary.json")


def build_joined_rows(
    fire_rows: dict[str, dict[str, str]],
    amoc_rows: dict[str, dict[str, str]],
    start_year: int,
    end_year: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            key = f"{year:04d}-{month:02d}"
            fire = fire_rows.get(key, {})
            amoc = amoc_rows.get(key, {})
            rows.append(
                {
                    "date": key,
                    "year": year,
                    "month": month,
                    "amoc_transport_sv": number(amoc.get("amoc_transport_sv")),
                    "amoc_anomaly_sv": number(amoc.get("amoc_anomaly_sv")),
                    "oregon_fire_count": number(fire.get("oregon_fire_count")),
                    "oregon_active_fire_points": number(fire.get("oregon_active_fire_points")),
                    "oregon_acres_burned_estimate": number(fire.get("oregon_acres_burned_estimate")),
                    "mean_frp": fire.get("mean_frp") or "",
                    "max_frp": fire.get("max_frp") or "",
                    "monthly_fire_points": number(fire.get("monthly_fire_points")),
                    "monthly_sum_frp": number(fire.get("monthly_sum_frp")),
                    "monthly_acres_burned_estimate": number(fire.get("monthly_acres_burned_estimate")),
                    "rolling_3mo_fire_points": 0,
                    "rolling_12mo_fire_points": 0,
                    "rolling_12mo_amoc": 0,
                }
            )
    return rows


def add_rolling(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for index, row in enumerate(rows):
        row["rolling_3mo_fire_points"] = round(rolling_mean(rows, index, "monthly_fire_points", 3), 4)
        row["rolling_12mo_fire_points"] = round(rolling_mean(rows, index, "monthly_fire_points", 12), 4)
        row["rolling_12mo_amoc"] = round(rolling_mean(rows, index, "amoc_transport_sv", 12), 4)
    return rows


def rolling_mean(rows: list[dict[str, Any]], index: int, key: str, window: int) -> float:
    start = max(0, index - window + 1)
    values = [number(row.get(key)) for row in rows[start : index + 1]]
    return sum(values) / len(values) if values else 0


def correlation_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fire = [number(row["rolling_12mo_fire_points"]) for row in rows]
    amoc = [number(row["rolling_12mo_amoc"]) for row in rows]
    seasonal_rows = [row for row in rows if 6 <= int(row["month"]) <= 10]

    lag_scores = []
    for lag in range(-24, 25):
        lag_scores.append({"lag_months": lag, "pearson": lagged_correlation(fire, amoc, lag)})

    best = max(lag_scores, key=lambda item: abs(item["pearson"]) if item["pearson"] == item["pearson"] else -1)
    return {
        "pearson": round(pearson(fire, amoc), 4),
        "spearman": round(spearman(fire, amoc), 4),
        "fire_season_pearson": round(
            pearson(
                [number(row["rolling_12mo_fire_points"]) for row in seasonal_rows],
                [number(row["rolling_12mo_amoc"]) for row in seasonal_rows],
            ),
            4,
        ),
        "best_lag_months": best["lag_months"],
        "best_lag_pearson": round(best["pearson"], 4),
        "lag_correlations": lag_scores,
        "interpretation": INTERPRETATION,
    }


def lagged_correlation(x: list[float], y: list[float], lag: int) -> float:
    if lag > 0:
        return pearson(x[lag:], y[:-lag])
    if lag < 0:
        return pearson(x[:lag], y[-lag:])
    return pearson(x, y)


def pearson(x: list[float], y: list[float]) -> float:
    pairs = [(a, b) for a, b in zip(x, y) if a == a and b == b]
    if len(pairs) < 3:
        return 0.0
    xs, ys = zip(*pairs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in pairs)
    denom_x = math.sqrt(sum((a - mean_x) ** 2 for a in xs))
    denom_y = math.sqrt(sum((b - mean_y) ** 2 for b in ys))
    if denom_x == 0 or denom_y == 0:
        return 0.0
    return numerator / (denom_x * denom_y)


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(rank(x), rank(y))


def rank(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    for rank_index, (_, original_index) in enumerate(ordered, start=1):
        ranks[original_index] = float(rank_index)
    return ranks


if __name__ == "__main__":
    main()
