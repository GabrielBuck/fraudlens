from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from app.detection.features import MODEL_FEATURES, model_matrix


class AnomalyDetector(Protocol):
    def fit(self, features: pd.DataFrame) -> None: ...
    def score(self, features: pd.DataFrame) -> np.ndarray: ...
    def save(self, path: Path) -> None: ...


@dataclass
class IsolationForestDetector:
    seed: int = 42
    contamination: float = 0.08

    def __post_init__(self) -> None:
        self.pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", RobustScaler()),
                (
                    "model",
                    IsolationForest(
                        n_estimators=180,
                        contamination=self.contamination,
                        random_state=self.seed,
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        self.raw_low = -0.75
        self.raw_high = -0.25

    def fit(self, features: pd.DataFrame) -> None:
        matrix = model_matrix(features)
        self.pipeline.fit(matrix)
        raw = self.pipeline.score_samples(matrix)
        self.raw_low = float(np.quantile(raw, 0.01))
        self.raw_high = float(np.quantile(raw, 0.99))
        if self.raw_high <= self.raw_low:
            self.raw_high = self.raw_low + 1e-6

    def score(self, features: pd.DataFrame) -> np.ndarray:
        raw = self.pipeline.score_samples(model_matrix(features))
        scaled = (self.raw_high - raw) / (self.raw_high - self.raw_low) * 100
        return np.asarray(np.clip(scaled, 0, 100), dtype=float)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "pipeline": self.pipeline,
                "raw_low": self.raw_low,
                "raw_high": self.raw_high,
                "features": MODEL_FEATURES,
                "seed": self.seed,
                "contamination": self.contamination,
            },
            path,
        )
        path.with_suffix(".json").write_text(
            json.dumps(
                {
                    "model": "IsolationForest",
                    "features": MODEL_FEATURES,
                    "seed": self.seed,
                    "contamination": self.contamination,
                    "score_transform": "clip((p99_raw - raw) / (p99_raw - p01_raw) * 100)",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> IsolationForestDetector:
        payload = joblib.load(path)
        detector = cls(seed=int(payload["seed"]), contamination=float(payload["contamination"]))
        detector.pipeline = payload["pipeline"]
        detector.raw_low = float(payload["raw_low"])
        detector.raw_high = float(payload["raw_high"])
        return detector
