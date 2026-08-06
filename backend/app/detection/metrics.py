from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


def evaluate_scores(
    ground_truth: pd.Series,
    final_scores: np.ndarray,
    scenarios: pd.Series,
    threshold: float = 30,
    predicted: np.ndarray | None = None,
) -> dict[str, Any]:
    truth = ground_truth.astype(bool).to_numpy()
    predictions = predicted if predicted is not None else final_scores >= threshold
    precision, recall, f1, _ = precision_recall_fscore_support(
        truth, predictions, average="binary", zero_division=0
    )
    true_count = int(np.count_nonzero(truth))
    k = max(1, true_count)
    top_indexes = np.argsort(final_scores)[::-1][:k]
    precision_at_k = float(truth[top_indexes].mean())
    recall_at_k = float(np.count_nonzero(truth[top_indexes]) / max(true_count, 1))
    scenario_recall: dict[str, float] = {}
    scenario_values = scenarios.fillna("normal").astype(str).to_numpy()
    for scenario in sorted(set(scenario_values) - {"normal"}):
        mask = scenario_values == scenario
        scenario_recall[scenario] = round(float(predictions[mask].mean()), 4)
    matrix = confusion_matrix(truth, predictions, labels=[False, True]).tolist()
    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "precision_at_k": round(precision_at_k, 4),
        "recall_at_k": round(recall_at_k, 4),
        "pr_auc": round(float(average_precision_score(truth, final_scores)), 4),
        "confusion_matrix": matrix,
        "scenario_recall": scenario_recall,
        "alert_rate": round(float(predictions.mean()), 4),
        "false_positive_rate": round(
            float(np.count_nonzero(predictions & ~truth) / max(int(np.count_nonzero(~truth)), 1)),
            4,
        ),
    }


def population_stability_index(reference: np.ndarray, recent: np.ndarray, bins: int = 10) -> float:
    if len(reference) == 0 or len(recent) == 0:
        return 0.0
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    reference_hist = np.histogram(reference, bins=edges)[0] / len(reference)
    recent_hist = np.histogram(recent, bins=edges)[0] / len(recent)
    reference_hist = np.clip(reference_hist, 1e-6, None)
    recent_hist = np.clip(recent_hist, 1e-6, None)
    return float(np.sum((recent_hist - reference_hist) * np.log(recent_hist / reference_hist)))
