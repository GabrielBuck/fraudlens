from __future__ import annotations

from dataclasses import dataclass

from app.detection.rules import RuleResult


@dataclass(frozen=True)
class RiskScore:
    final: float
    model: float
    rules: float
    booster: float
    severity: str


def severity_for(score: float, medium: float = 30, high: float = 60, critical: float = 80) -> str:
    if score >= critical:
        return "crítica"
    if score >= high:
        return "alta"
    if score >= medium:
        return "média"
    return "baixa"


def combine_scores(
    model_score: float,
    rules_score: float,
    rules: list[RuleResult],
    model_weight: float = 0.55,
    rules_weight: float = 0.45,
    medium_threshold: float = 30,
    high_threshold: float = 60,
    critical_threshold: float = 80,
) -> RiskScore:
    if abs(model_weight + rules_weight - 1.0) > 1e-6:
        raise ValueError("Score weights must add up to 1.0")
    triggered = {rule.rule_id for rule in rules if rule.triggered}
    boosters = [
        {"NEW_DEVICE", "NEW_COUNTERPARTY", "HIGH_AMOUNT_DEVIATION"},
        {"FAILED_AUTH_BURST", "NEW_DEVICE"},
        {"IMPOSSIBLE_TRAVEL", "NEW_DEVICE"},
        {"VELOCITY_5M", "SPLIT_PAYMENT_PATTERN"},
    ]
    boost = 8.0 if any(combo.issubset(triggered) for combo in boosters) else 0.0
    final = min(100.0, max(0.0, model_score * model_weight + rules_score * rules_weight + boost))
    return RiskScore(
        final=round(final, 2),
        model=round(model_score, 2),
        rules=round(rules_score, 2),
        booster=boost,
        severity=severity_for(final, medium_threshold, high_threshold, critical_threshold),
    )
