from pathlib import Path

import numpy as np
import pandas as pd

from app.detection.explanations import DeterministicExplanationGenerator
from app.detection.metrics import evaluate_scores, population_stability_index
from app.detection.rules import RuleEngine, RuleResult
from app.detection.scoring import combine_scores, severity_for


def _rule(rule_id: str, weight: float = 20) -> RuleResult:
    return RuleResult(True, rule_id, rule_id, weight, "alta", 1, "0", "test")


def test_rule_engine_triggers_critical_context() -> None:
    engine = RuleEngine(Path(__file__).parents[2] / "config" / "detection.yaml")
    row = pd.Series(
        {
            "new_device": 1,
            "new_counterparty": 1,
            "unusual_hour": 1,
            "amount_zscore": 5,
            "tx_count_5m": 4,
            "tx_count_1h": 4,
            "failed_auth_30m": 4,
            "estimated_speed_kmh": 1200,
            "counterparty_risk": 0,
            "unusual_payment_method": 1,
            "amount": 20_000,
            "denied_count_30m": 0,
            "amount_sum_1h": 20_000,
        }
    )
    triggered = {result.rule_id for result in engine.evaluate(row) if result.triggered}
    assert {
        "NEW_DEVICE",
        "NEW_COUNTERPARTY",
        "HIGH_AMOUNT_DEVIATION",
        "IMPOSSIBLE_TRAVEL",
    }.issubset(triggered)


def test_score_is_bounded_and_severity_is_configured() -> None:
    result = combine_scores(
        100, 100, [_rule("NEW_DEVICE"), _rule("NEW_COUNTERPARTY"), _rule("HIGH_AMOUNT_DEVIATION")]
    )
    assert result.final == 100
    assert result.booster == 8
    assert result.severity == "crítica"
    assert severity_for(29.99) == "baixa"
    assert severity_for(30) == "média"
    assert severity_for(60) == "alta"
    assert severity_for(79.99) == "alta"
    assert severity_for(80) == "crítica"


def test_score_weights_and_context_booster_are_explicit() -> None:
    plain = combine_scores(80, 60, [_rule("NEW_DEVICE")])
    boosted = combine_scores(
        80,
        60,
        [_rule("NEW_DEVICE"), _rule("FAILED_AUTH_BURST")],
    )
    assert plain.final == 71
    assert plain.booster == 0
    assert boosted.final == 79
    assert boosted.booster == 8
    try:
        combine_scores(50, 50, [], model_weight=0.8, rules_weight=0.3)
    except ValueError as exc:
        assert "add up" in str(exc)
    else:
        raise AssertionError("Expected invalid score weights to fail")


def test_explanation_is_neutral_and_includes_components() -> None:
    score = combine_scores(80, 60, [_rule("NEW_DEVICE")])
    text = DeterministicExplanationGenerator().generate(score, [_rule("NEW_DEVICE")])
    assert "requer investigação" in text
    assert "comprova fraude" in text
    assert "fraudador" not in text


def test_metrics_and_psi() -> None:
    truth = pd.Series([False, False, True, True])
    scores = np.array([10, 20, 70, 90], dtype=float)
    metrics = evaluate_scores(truth, scores, pd.Series([None, None, "a", "b"]), threshold=30)
    assert metrics["precision"] == 1
    assert metrics["recall"] == 1
    assert metrics["confusion_matrix"] == [[2, 0], [0, 2]]
    assert population_stability_index(np.arange(100), np.arange(100)) == 0
