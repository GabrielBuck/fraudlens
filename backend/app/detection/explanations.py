from __future__ import annotations

from typing import Protocol

from app.detection.rules import RuleResult
from app.detection.scoring import RiskScore


class ExplanationGenerator(Protocol):
    def generate(self, score: RiskScore, rules: list[RuleResult]) -> str: ...


class DeterministicExplanationGenerator:
    def generate(self, score: RiskScore, rules: list[RuleResult]) -> str:
        triggered = [rule for rule in rules if rule.triggered]
        if not triggered:
            return (
                f"A operação recebeu prioridade {score.severity} principalmente pelo score de "
                "anomalia do modelo e deve ser comparada ao histórico antes de qualquer conclusão."
            )
        factors = ", ".join(rule.rule_name.lower() for rule in triggered[:3])
        return (
            f"A operação recebeu prioridade {score.severity} por apresentar {factors}. "
            f"O modelo contribuiu com {score.model:.0f}/100 e as regras com {score.rules:.0f}/100. "
            "O padrão é sintético, não comprova fraude e requer investigação contextual."
        )
