from __future__ import annotations

import math
from datetime import timedelta
from typing import Final, cast

import numpy as np
import pandas as pd

LABEL_COLUMNS: Final = {"synthetic_ground_truth", "synthetic_scenario"}
MODEL_FEATURES: Final = [
    "amount",
    "amount_log",
    "historical_mean",
    "historical_median",
    "historical_std",
    "amount_zscore",
    "amount_to_mean_ratio",
    "hour_sin",
    "hour_cos",
    "weekday_sin",
    "weekday_cos",
    "is_weekend",
    "unusual_hour",
    "minutes_since_previous",
    "tx_count_5m",
    "tx_count_30m",
    "tx_count_1h",
    "tx_count_24h",
    "amount_sum_1h",
    "amount_sum_24h",
    "denied_count_30m",
    "failed_auth_30m",
    "new_counterparty",
    "distinct_counterparties_24h",
    "counterparty_frequency",
    "counterparty_risk",
    "new_device",
    "trusted_device",
    "devices_24h",
    "distance_from_previous_km",
    "estimated_speed_kmh",
    "new_city",
    "new_country",
    "distance_from_home_km",
    "payment_method_frequency",
    "unusual_payment_method",
    "historical_denial_rate",
    "account_age_days",
    "average_monthly_volume",
    "outgoing_ratio",
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(max(1 - value, 0)))


def build_features(
    transactions: pd.DataFrame,
    accounts: pd.DataFrame,
    counterparties: pd.DataFrame,
    devices: pd.DataFrame,
    authentication_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if transactions.empty:
        return transactions.copy()
    frame = transactions.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values(["account_id", "timestamp", "id"]).reset_index(drop=True)
    account_columns = [
        "id",
        "home_city",
        "home_latitude",
        "home_longitude",
        "account_age_days",
        "average_monthly_volume",
        "usual_transaction_hour_start",
        "usual_transaction_hour_end",
    ]
    frame = frame.merge(
        accounts[account_columns].rename(columns={"id": "account_ref"}),
        left_on="account_id",
        right_on="account_ref",
        how="left",
    )
    frame["failed_auth_30m"] = 0.0
    if authentication_events is not None and not authentication_events.empty:
        auth = authentication_events.copy()
        auth["timestamp"] = pd.to_datetime(auth["timestamp"], utc=True)
        failures = auth[~auth["success"].astype(bool)]
        for account_id, indexes in frame.groupby("account_id").groups.items():
            account_failures = failures[failures["account_id"] == account_id]["timestamp"]
            if account_failures.empty:
                continue
            for index in indexes:
                timestamp = cast(pd.Timestamp, frame.at[index, "timestamp"])
                frame.at[index, "failed_auth_30m"] = float(
                    (
                        (account_failures < timestamp)
                        & (account_failures >= timestamp - timedelta(minutes=30))
                    ).sum()
                )
    frame = frame.merge(
        counterparties[["id", "historical_risk_level"]].rename(columns={"id": "cp_ref"}),
        left_on="counterparty_id",
        right_on="cp_ref",
        how="left",
    )
    frame = frame.merge(
        devices[["id", "trusted"]].rename(columns={"id": "device_ref"}),
        left_on="device_id",
        right_on="device_ref",
        how="left",
    )

    frame["amount_log"] = np.log1p(frame["amount"].astype(float))
    frame["hour"] = frame["timestamp"].dt.hour
    frame["weekday"] = frame["timestamp"].dt.dayofweek
    frame["is_weekend"] = (frame["weekday"] >= 5).astype(int)
    frame["hour_sin"] = np.sin(2 * np.pi * frame["hour"] / 24)
    frame["hour_cos"] = np.cos(2 * np.pi * frame["hour"] / 24)
    frame["weekday_sin"] = np.sin(2 * np.pi * frame["weekday"] / 7)
    frame["weekday_cos"] = np.cos(2 * np.pi * frame["weekday"] / 7)
    frame["unusual_hour"] = (
        (frame["hour"] < frame["usual_transaction_hour_start"])
        | (frame["hour"] > frame["usual_transaction_hour_end"])
    ).astype(int)

    output_groups: list[pd.DataFrame] = []
    for _, group in frame.groupby("account_id", sort=False):
        group = group.sort_values(["timestamp", "id"]).copy()
        previous_amount = group["amount"].shift(1)
        expanding = previous_amount.expanding(min_periods=1)
        group["historical_mean"] = expanding.mean().fillna(group["amount"])
        group["historical_median"] = expanding.median().fillna(group["amount"])
        group["historical_std"] = expanding.std().fillna(0.0)
        group["amount_zscore"] = (
            (
                (group["amount"] - group["historical_mean"])
                / group["historical_std"].replace(0, np.nan)
            )
            .fillna(0.0)
            .clip(-20, 20)
        )
        group["amount_to_mean_ratio"] = (
            group["amount"] / group["historical_mean"].clip(lower=1.0)
        ).clip(0, 100)
        previous_time = group["timestamp"].shift(1)
        group["minutes_since_previous"] = (
            (group["timestamp"] - previous_time).dt.total_seconds().div(60).fillna(1440)
        ).clip(0, 100_000)

        indexed = group.set_index("timestamp", drop=False)
        for label, window in (("5m", "5min"), ("30m", "30min"), ("1h", "1h"), ("24h", "24h")):
            count = indexed["amount"].rolling(window, closed="left").count()
            group[f"tx_count_{label}"] = count.to_numpy()
        group["amount_sum_1h"] = (
            indexed["amount"].rolling("1h", closed="left").sum().fillna(0).to_numpy()
        )
        group["amount_sum_24h"] = (
            indexed["amount"].rolling("24h", closed="left").sum().fillna(0).to_numpy()
        )
        denied = (indexed["status"] == "negada").astype(int)
        group["denied_count_30m"] = (
            denied.rolling("30min", closed="left").sum().fillna(0).to_numpy()
        )

        cp_seen: dict[str, int] = {}
        device_seen: set[str] = set()
        city_seen: set[str] = set()
        country_seen: set[str] = set()
        method_seen: dict[str, int] = {}
        denied_total = 0
        outgoing_total = 0
        previous: pd.Series | None = None
        derived: list[dict[str, float]] = []
        records = list(group.iterrows())
        for position, (_, row) in enumerate(records):
            cp = str(row["counterparty_id"])
            device = str(row["device_id"])
            city = str(row["ip_city"])
            country = str(row["ip_country"])
            method = str(row["payment_method"])
            history_size = max(position, 1)
            cutoff = cast(pd.Timestamp, row["timestamp"]) - timedelta(hours=24)
            recent = group.iloc[:position]
            recent = recent[recent["timestamp"] >= cutoff]
            distance_previous = 0.0
            speed = 0.0
            if previous is not None:
                distance_previous = haversine_km(
                    float(previous["latitude"]),
                    float(previous["longitude"]),
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
                elapsed_hours = max(
                    (row["timestamp"] - previous["timestamp"]).total_seconds() / 3600, 0.01
                )
                speed = min(distance_previous / elapsed_hours, 20_000)
            derived.append(
                {
                    "new_counterparty": float(position >= 5 and cp not in cp_seen),
                    "distinct_counterparties_24h": float(recent["counterparty_id"].nunique()),
                    "counterparty_frequency": cp_seen.get(cp, 0) / history_size,
                    "new_device": float(
                        not bool(row["trusted"]) or (position >= 5 and device not in device_seen)
                    ),
                    "trusted_device": float(bool(row["trusted"])),
                    "devices_24h": float(recent["device_id"].nunique()),
                    "distance_from_previous_km": distance_previous,
                    "estimated_speed_kmh": speed,
                    "new_city": float(position >= 5 and city not in city_seen),
                    "new_country": float(position >= 5 and country not in country_seen),
                    "distance_from_home_km": haversine_km(
                        float(row["home_latitude"]),
                        float(row["home_longitude"]),
                        float(row["latitude"]),
                        float(row["longitude"]),
                    ),
                    "payment_method_frequency": method_seen.get(method, 0) / history_size,
                    "unusual_payment_method": float(position >= 5 and method not in method_seen),
                    "historical_denial_rate": denied_total / history_size,
                    "outgoing_ratio": outgoing_total / history_size,
                }
            )
            cp_seen[cp] = cp_seen.get(cp, 0) + 1
            device_seen.add(device)
            city_seen.add(city)
            country_seen.add(country)
            method_seen[method] = method_seen.get(method, 0) + 1
            denied_total += int(row["status"] == "negada")
            outgoing_total += int(row["direction"] == "saída")
            previous = row
        group = pd.concat([group.reset_index(drop=True), pd.DataFrame(derived)], axis=1)
        group["counterparty_risk"] = (group["historical_risk_level"] == "alto").astype(int)
        output_groups.append(group)

    result = pd.concat(output_groups, ignore_index=True).sort_values("id").reset_index(drop=True)
    result[MODEL_FEATURES] = result[MODEL_FEATURES].replace([np.inf, -np.inf], 0).fillna(0)
    return result


def model_matrix(features: pd.DataFrame) -> pd.DataFrame:
    leaked = LABEL_COLUMNS.intersection(MODEL_FEATURES)
    if leaked:
        raise ValueError(f"Evaluation labels found in model feature list: {sorted(leaked)}")
    return features.loc[:, MODEL_FEATURES].astype(float)
