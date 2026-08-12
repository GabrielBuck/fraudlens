from dataclasses import replace

import pytest

from app.detection.data_quality import validate_generated_data
from app.detection.generator import generate_synthetic_data


def test_generated_dataset_passes_integrity_checks() -> None:
    data = generate_synthetic_data(8, 120, seed=42)
    report = validate_generated_data(data)
    assert report["status"] == "passed"
    assert report["failed"] == 0
    assert all(report["checks"].values())


def test_dataset_validation_rejects_broken_references() -> None:
    data = generate_synthetic_data(8, 120, seed=42)
    transactions = [dict(row) for row in data.transactions]
    transactions[0]["account_id"] = "ACC-MISSING"
    with pytest.raises(ValueError, match="valid_account_references"):
        validate_generated_data(replace(data, transactions=transactions))
