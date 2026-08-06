from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

import pandas as pd
import yaml


@dataclass(frozen=True)
class RuleResult:
    triggered: bool
    rule_id: str
    rule_name: str
    weight: float
    severity: str
    observed_value: float
    expected_value: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


RulePredicate = Callable[[pd.Series, float], bool]
OBSERVATIONS: dict[str, tuple[str, RulePredicate, str]] = {
    "NEW_DEVICE": (
        "new_device",
        lambda row, threshold: row["new_device"] >= threshold,
        "dispositivo confiável",
    ),
    "NEW_COUNTERPARTY": (
        "new_counterparty",
        lambda row, threshold: row["new_counterparty"] >= threshold,
        "contraparte recorrente",
    ),
    "UNUSUAL_HOUR": (
        "unusual_hour",
        lambda row, threshold: row["unusual_hour"] >= threshold,
        "janela habitual",
    ),
    "HIGH_AMOUNT_DEVIATION": (
        "amount_zscore",
        lambda row, threshold: row["amount_zscore"] >= threshold,
        "até 3 desvios-padrão",
    ),
    "VELOCITY_5M": (
        "tx_count_5m",
        lambda row, threshold: row["tx_count_5m"] >= threshold,
        "menos de 3 operações",
    ),
    "VELOCITY_1H": (
        "tx_count_1h",
        lambda row, threshold: row["tx_count_1h"] >= threshold,
        "menos de 8 operações",
    ),
    "FAILED_AUTH_BURST": (
        "failed_auth_30m",
        lambda row, threshold: row["failed_auth_30m"] >= threshold,
        "menos de 3 falhas",
    ),
    "IMPOSSIBLE_TRAVEL": (
        "estimated_speed_kmh",
        lambda row, threshold: row["estimated_speed_kmh"] >= threshold,
        "abaixo de 900 km/h",
    ),
    "RISKY_COUNTERPARTY": (
        "counterparty_risk",
        lambda row, threshold: row["counterparty_risk"] >= threshold,
        "risco histórico baixo",
    ),
    "UNUSUAL_PAYMENT_METHOD": (
        "unusual_payment_method",
        lambda row, threshold: row["unusual_payment_method"] >= threshold,
        "meio recorrente",
    ),
}


class RuleEngine:
    def __init__(self, config_path: Path) -> None:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("Detection configuration must be a mapping")
        self.config = cast(dict[str, Any], loaded)
        self.rules: list[dict[str, Any]] = self.config["rules"]

    def evaluate(self, row: pd.Series) -> list[RuleResult]:
        results: list[RuleResult] = []
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            rule_id = str(rule["id"])
            threshold = float(rule["threshold"])
            observed = 0.0
            triggered = False
            expected = "comportamento histórico"
            if rule_id in OBSERVATIONS:
                feature, predicate, expected = OBSERVATIONS[rule_id]
                observed = float(row.get(feature, 0))
                triggered = bool(predicate(row, threshold))
            elif rule_id == "DUPLICATE_PATTERN":
                observed = float(row.get("tx_count_5m", 0))
                triggered = observed >= 2 and float(row.get("amount_zscore", 0)) < 1
                expected = "sem repetição em cinco minutos"
            elif rule_id == "LOW_VALUE_TESTING":
                observed = float(row.get("denied_count_30m", 0))
                triggered = observed >= 3 and float(row["amount"]) >= 5000
                expected = "sem sequência de testes negados"
            elif rule_id == "SPLIT_PAYMENT_PATTERN":
                observed = float(row.get("amount_sum_1h", 0))
                triggered = (
                    float(row.get("tx_count_1h", 0)) >= 3
                    and observed >= 12_000
                    and float(row["amount"]) <= 6_000
                )
                expected = "volume horário abaixo de R$ 12 mil"
            results.append(
                RuleResult(
                    triggered=triggered,
                    rule_id=rule_id,
                    rule_name=str(rule["name"]),
                    weight=float(rule["weight"]),
                    severity=str(rule["severity"]),
                    observed_value=round(observed, 3),
                    expected_value=expected,
                    description=str(rule["description"]),
                )
            )
        return results

    @staticmethod
    def score(results: list[RuleResult]) -> float:
        active = [result for result in results if result.triggered]
        return min(100.0, sum(result.weight for result in active))
