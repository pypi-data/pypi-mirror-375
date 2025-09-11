from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from .config import PipelineConfig
from .model import XtrapNet
from .trainer import XtrapTrainer
from .wrappers.ensemble import EnsembleWrapper
from .uncertainty.conformal import ConformalCalibrator
from .ood.detectors import MahalanobisDetector, KNNDetector, NullDetector
from .policy.policy import GuardrailPolicy


class XtrapPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.model = XtrapNet(
            input_dim=config.model.input_dim,
            dropout_rate=config.model.dropout_rate,
        )

        if config.ensemble.enabled:
            self.predictor = EnsembleWrapper(
                base_model_constructor=lambda: XtrapNet(
                    input_dim=config.model.input_dim,
                    dropout_rate=config.model.dropout_rate,
                ),
                num_members=config.ensemble.num_members,
                diversity=config.ensemble.diversity,
            )
        else:
            self.predictor = self.model

        self.calibrator: Optional[ConformalCalibrator] = None
        self.ood_detector = self._init_ood_detector()
        self.policy = GuardrailPolicy(self.config.policy)

    def _init_ood_detector(self):
        if self.config.ood.method == "mahalanobis":
            return MahalanobisDetector()
        if self.config.ood.method == "knn":
            return KNNDetector()
        return NullDetector()

    def fit(self, train_labels: np.ndarray, train_features: np.ndarray):
        trainer = XtrapTrainer(
            self.model if not self.config.ensemble.enabled else self.predictor,
            learning_rate=self.config.training.learning_rate,
            num_epochs=self.config.training.num_epochs,
            batch_size=self.config.training.batch_size,
        )
        trainer.train(train_labels, train_features)

        self.ood_detector.fit(train_features)

        if self.config.uncertainty.conformal:
            self.calibrator = ConformalCalibrator(alpha=self.config.uncertainty.conformal_alpha)
            self.calibrator.fit(self.predictor, train_features, train_labels)

        self._fit_cache = {
            "train_features": train_features,
            "train_labels": train_labels,
        }
        return self

    def predict(self, features: np.ndarray, return_uncertainty: bool = True):
        pred = self.predictor.predict(
            features,
            mc_dropout=self.config.uncertainty.mc_dropout,
            n_samples=self.config.uncertainty.mc_samples,
        )
        if isinstance(pred, tuple):
            mean, var = pred
        else:
            mean, var = pred, None

        intervals = None
        if self.calibrator is not None:
            intervals = self.calibrator.predict_intervals(features)

        ood_scores = self.ood_detector.score(features)

        if return_uncertainty:
            return mean, var, intervals, ood_scores
        return mean

    def evaluate(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        from .metrics.calibration import expected_calibration_error
        from .metrics.selective import risk_coverage_curve

        mean, var, intervals, _ = self.predict(features, return_uncertainty=True)

        metrics: Dict[str, Any] = {}
        if var is not None:
            metrics["ece"] = expected_calibration_error(mean.flatten(), labels.flatten(), var.flatten())

        if intervals is not None:
            lower, upper = intervals
            coverage = np.mean((labels.flatten() >= lower.flatten()) & (labels.flatten() <= upper.flatten()))
            metrics["pi_coverage"] = float(coverage)

        rc = risk_coverage_curve(mean.flatten(), labels.flatten(), var.flatten() if var is not None else None)
        metrics.update(rc)
        return metrics


