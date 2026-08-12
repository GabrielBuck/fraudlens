from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from app.detection.generator import GeneratedData


def validate_generated_data(data: GeneratedData) -> dict[str, Any]:
    """Validate the small set of invariants required by the synthetic pipeline."""

    checks: dict[str, bool] = {}
    entity_rows = {
        "accounts": data.accounts,
        "counterparties": data.counterparties,
        "devices": data.devices,
        "authentication_events": data.authentication_events,
        "transactions": data.transactions,
    }
    checks["unique_ids"] = all(
        len({str(row["id"]) for row in rows}) == len(rows) for rows in entity_rows.values()
    )
    account_ids = {str(row["id"]) for row in data.accounts}
    counterparty_ids = {str(row["id"]) for row in data.counterparties}
    device_ids = {str(row["id"]) for row in data.devices}
    checks["valid_account_references"] = all(
        str(row["account_id"]) in account_ids
        for row in data.transactions + data.devices + data.authentication_events
    )
    checks["valid_device_references"] = all(
        str(row["device_id"]) in device_ids
        for row in data.transactions + data.authentication_events
    )
    checks["valid_counterparty_references"] = all(
        str(row["counterparty_id"]) in counterparty_ids for row in data.transactions
    )
    checks["valid_timestamps"] = all(
        isinstance(row["timestamp"], datetime) and row["timestamp"].tzinfo is not None
        for row in data.transactions + data.authentication_events
    )
    checks["valid_amounts"] = all(
        math.isfinite(float(row["amount"])) and float(row["amount"]) > 0
        for row in data.transactions
    )
    checks["valid_currency"] = all(row["currency"] == "BRL" for row in data.transactions)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Synthetic dataset failed quality checks: {', '.join(failed)}")
    return {"status": "passed", "checks": checks, "passed": len(checks), "failed": 0}
