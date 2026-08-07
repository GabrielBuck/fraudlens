import pandas as pd

from app.detection.features import (
    LABEL_COLUMNS,
    MODEL_FEATURES,
    build_features,
    haversine_km,
    model_matrix,
)
from app.detection.generator import generate_synthetic_data


def _frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = generate_synthetic_data(8, 120, seed=8)
    return tuple(
        pd.DataFrame(items)
        for items in (
            data.transactions,
            data.accounts,
            data.counterparties,
            data.devices,
            data.authentication_events,
        )
    )  # type: ignore[return-value]


def test_model_features_never_include_evaluation_labels() -> None:
    tx, accounts, counterparties, devices, auth = _frames()
    features = build_features(tx, accounts, counterparties, devices, auth)
    matrix = model_matrix(features)
    assert set(matrix.columns) == set(MODEL_FEATURES)
    assert not LABEL_COLUMNS.intersection(matrix.columns)
    assert matrix.notna().all().all()


def test_historical_mean_does_not_use_future_rows() -> None:
    tx, accounts, counterparties, devices, auth = _frames()
    features = build_features(tx, accounts, counterparties, devices, auth).sort_values(
        ["account_id", "timestamp"]
    )
    group = features.groupby("account_id").get_group("ACC-000001").reset_index(drop=True)
    assert group.loc[1, "historical_mean"] == group.loc[0, "amount"]
    original = group.loc[1, "historical_mean"]
    tx.loc[tx["id"] == group.iloc[-1]["id"], "amount"] = 999_999_999
    mutated = build_features(tx, accounts, counterparties, devices, auth).set_index("id")
    assert mutated.loc[group.loc[1, "id"], "historical_mean"] == original


def test_haversine_distance_is_reasonable() -> None:
    distance = haversine_km(-23.5505, -46.6333, -22.9068, -43.1729)
    assert 350 < distance < 380
