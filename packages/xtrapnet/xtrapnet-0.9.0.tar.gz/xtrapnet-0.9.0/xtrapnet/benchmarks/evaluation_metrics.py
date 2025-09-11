"""
Comprehensive evaluation metrics for XtrapNet components.

This module provides standardized metrics for evaluating OOD detection,
uncertainty quantification, extrapolation control, and anomaly detection.
"""

from __future__ import annotations

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import time
import json
from pathlib import Path


class MetricType(Enum):
    """Types of evaluation metrics."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    AUC_PR = "auc_pr"
    CALIBRATION_ERROR = "calibration_error"
    SHARPNESS = "sharpness"
    CONFIDENCE = "confidence"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"


@dataclass
class MetricResult:
    """Result of a single metric evaluation."""
    metric_name: str
    value: float
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Optional[Dict[str, Any]] = None


class EvaluationMetrics:
    """Base class for evaluation metrics."""
    
    def __init__(self):
        self.results: List[MetricResult] = []
    
    def compute_metric(self, predictions: np.ndarray, targets: np.ndarray, **kwargs) -> float:
        """Compute a single metric value."""
        raise NotImplementedError
    
    def evaluate(self, predictions: np.ndarray, targets: np.ndarray, **kwargs) -> MetricResult:
        """Evaluate and return metric result."""
        value = self.compute_metric(predictions, targets, **kwargs)
        return MetricResult(
            metric_name=self.__class__.__name__,
            value=value,
            metadata=kwargs
        )
    
    def bootstrap_confidence_interval(
        self, 
        predictions: np.ndarray, 
        targets: np.ndarray, 
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Compute bootstrap confidence interval."""
        n_samples = len(predictions)
        bootstrap_values = []
        
        for _ in range(n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            pred_bootstrap = predictions[indices]
            target_bootstrap = targets[indices]
            
            # Compute metric on bootstrap sample
            value = self.compute_metric(pred_bootstrap, target_bootstrap)
            bootstrap_values.append(value)
        
        # Compute confidence interval
        alpha = 1 - confidence_level
        lower = np.percentile(bootstrap_values, 100 * alpha / 2)
        upper = np.percentile(bootstrap_values, 100 * (1 - alpha / 2))
        
        return lower, upper


class OODDetectionMetrics(EvaluationMetrics):
    """Metrics for Out-of-Distribution detection."""
    
    def __init__(self):
        super().__init__()
        self.metrics = {
            'auc_roc': self._compute_auc_roc,
            'auc_pr': self._compute_auc_pr,
            'f1_score': self._compute_f1_score,
            'precision': self._compute_precision,
            'recall': self._compute_recall,
            'accuracy': self._compute_accuracy
        }
    
    def evaluate_all(
        self, 
        ood_scores: np.ndarray, 
        is_ood: np.ndarray,
        threshold: Optional[float] = None
    ) -> Dict[str, MetricResult]:
        """Evaluate all OOD detection metrics."""
        results = {}
        
        for metric_name, metric_func in self.metrics.items():
            if threshold is not None and metric_name in ['f1_score', 'precision', 'recall', 'accuracy']:
                # Binary classification metrics need threshold
                predictions = (ood_scores > threshold).astype(int)
                value = metric_func(predictions, is_ood)
            else:
                # Ranking metrics use continuous scores
                value = metric_func(ood_scores, is_ood)
            
            results[metric_name] = MetricResult(
                metric_name=metric_name,
                value=value
            )
        
        return results
    
    def _compute_auc_roc(self, scores: np.ndarray, is_ood: np.ndarray) -> float:
        """Compute AUC-ROC for OOD detection."""
        try:
            from sklearn.metrics import roc_auc_score
            return roc_auc_score(is_ood, scores)
        except ImportError:
            # Fallback implementation
            return self._fallback_auc_roc(scores, is_ood)
    
    def _compute_auc_pr(self, scores: np.ndarray, is_ood: np.ndarray) -> float:
        """Compute AUC-PR for OOD detection."""
        try:
            from sklearn.metrics import precision_recall_curve, auc
            precision, recall, _ = precision_recall_curve(is_ood, scores)
            return auc(recall, precision)
        except ImportError:
            return 0.0
    
    def _compute_f1_score(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute F1 score."""
        try:
            from sklearn.metrics import f1_score
            return f1_score(targets, predictions)
        except ImportError:
            return self._fallback_f1_score(predictions, targets)
    
    def _compute_precision(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute precision."""
        try:
            from sklearn.metrics import precision_score
            return precision_score(targets, predictions, zero_division=0)
        except ImportError:
            return self._fallback_precision(predictions, targets)
    
    def _compute_recall(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute recall."""
        try:
            from sklearn.metrics import recall_score
            return recall_score(targets, predictions, zero_division=0)
        except ImportError:
            return self._fallback_recall(predictions, targets)
    
    def _compute_accuracy(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute accuracy."""
        return np.mean(predictions == targets)
    
    def _fallback_auc_roc(self, scores: np.ndarray, is_ood: np.ndarray) -> float:
        """Fallback AUC-ROC computation."""
        # Simple implementation without sklearn
        sorted_indices = np.argsort(scores)
        sorted_scores = scores[sorted_indices]
        sorted_labels = is_ood[sorted_indices]
        
        # Count true positives and false positives at each threshold
        tp = np.cumsum(sorted_labels[::-1])
        fp = np.cumsum(1 - sorted_labels[::-1])
        
        # Compute ROC curve
        tpr = tp / tp[-1] if tp[-1] > 0 else np.zeros_like(tp)
        fpr = fp / fp[-1] if fp[-1] > 0 else np.zeros_like(fp)
        
        # Compute AUC using trapezoidal rule
        auc = np.trapz(tpr, fpr)
        return auc
    
    def _fallback_f1_score(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Fallback F1 score computation."""
        tp = np.sum((predictions == 1) & (targets == 1))
        fp = np.sum((predictions == 1) & (targets == 0))
        fn = np.sum((predictions == 0) & (targets == 1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    def _fallback_precision(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Fallback precision computation."""
        tp = np.sum((predictions == 1) & (targets == 1))
        fp = np.sum((predictions == 1) & (targets == 0))
        return tp / (tp + fp) if (tp + fp) > 0 else 0
    
    def _fallback_recall(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Fallback recall computation."""
        tp = np.sum((predictions == 1) & (targets == 1))
        fn = np.sum((predictions == 0) & (targets == 1))
        return tp / (tp + fn) if (tp + fn) > 0 else 0


class UncertaintyMetrics(EvaluationMetrics):
    """Metrics for uncertainty quantification."""
    
    def __init__(self):
        super().__init__()
    
    def evaluate_all(
        self,
        predictions: np.ndarray,
        uncertainties: np.ndarray,
        targets: np.ndarray,
        confidence_levels: List[float] = [0.5, 0.8, 0.9, 0.95, 0.99]
    ) -> Dict[str, MetricResult]:
        """Evaluate all uncertainty metrics."""
        results = {}
        
        # Calibration error
        results['calibration_error'] = MetricResult(
            metric_name='calibration_error',
            value=self._compute_calibration_error(predictions, uncertainties, targets)
        )
        
        # Sharpness
        results['sharpness'] = MetricResult(
            metric_name='sharpness',
            value=self._compute_sharpness(uncertainties)
        )
        
        # Confidence intervals
        for conf_level in confidence_levels:
            ci_accuracy = self._compute_confidence_interval_accuracy(
                predictions, uncertainties, targets, conf_level
            )
            results[f'ci_accuracy_{conf_level}'] = MetricResult(
                metric_name=f'ci_accuracy_{conf_level}',
                value=ci_accuracy
            )
        
        return results
    
    def _compute_calibration_error(
        self, 
        predictions: np.ndarray, 
        uncertainties: np.ndarray, 
        targets: np.ndarray
    ) -> float:
        """Compute calibration error (ECE)."""
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (uncertainties > bin_lower) & (uncertainties <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = (predictions[in_bin] == targets[in_bin]).mean()
                avg_confidence_in_bin = uncertainties[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    def _compute_sharpness(self, uncertainties: np.ndarray) -> float:
        """Compute sharpness (inverse of average uncertainty)."""
        return 1.0 / (uncertainties.mean() + 1e-8)
    
    def _compute_confidence_interval_accuracy(
        self,
        predictions: np.ndarray,
        uncertainties: np.ndarray,
        targets: np.ndarray,
        confidence_level: float
    ) -> float:
        """Compute accuracy within confidence interval."""
        # For simplicity, assume uncertainties represent confidence intervals
        # In practice, this would depend on the specific uncertainty type
        threshold = 1.0 - confidence_level
        in_interval = uncertainties > threshold
        
        if in_interval.sum() == 0:
            return 0.0
        
        return (predictions[in_interval] == targets[in_interval]).mean()


class ExtrapolationMetrics(EvaluationMetrics):
    """Metrics for extrapolation control."""
    
    def __init__(self):
        super().__init__()
    
    def evaluate_all(
        self,
        predictions: np.ndarray,
        targets: np.ndarray,
        extrapolation_flags: np.ndarray,
        confidence_scores: np.ndarray
    ) -> Dict[str, MetricResult]:
        """Evaluate all extrapolation metrics."""
        results = {}
        
        # Extrapolation accuracy
        results['extrapolation_accuracy'] = MetricResult(
            metric_name='extrapolation_accuracy',
            value=self._compute_extrapolation_accuracy(predictions, targets, extrapolation_flags)
        )
        
        # Confidence calibration
        results['confidence_calibration'] = MetricResult(
            metric_name='confidence_calibration',
            value=self._compute_confidence_calibration(predictions, targets, confidence_scores)
        )
        
        # Extrapolation detection accuracy
        results['extrapolation_detection'] = MetricResult(
            metric_name='extrapolation_detection',
            value=self._compute_extrapolation_detection_accuracy(extrapolation_flags, targets)
        )
        
        return results
    
    def _compute_extrapolation_accuracy(
        self, 
        predictions: np.ndarray, 
        targets: np.ndarray, 
        extrapolation_flags: np.ndarray
    ) -> float:
        """Compute accuracy on extrapolation samples."""
        extrapolation_mask = extrapolation_flags == 1
        if extrapolation_mask.sum() == 0:
            return 0.0
        
        return (predictions[extrapolation_mask] == targets[extrapolation_mask]).mean()
    
    def _compute_confidence_calibration(
        self, 
        predictions: np.ndarray, 
        targets: np.ndarray, 
        confidence_scores: np.ndarray
    ) -> float:
        """Compute confidence calibration."""
        return 1.0 - np.abs(confidence_scores.mean() - (predictions == targets).mean())
    
    def _compute_extrapolation_detection_accuracy(
        self, 
        extrapolation_flags: np.ndarray, 
        targets: np.ndarray
    ) -> float:
        """Compute accuracy of extrapolation detection."""
        # This is a simplified version - in practice, you'd need ground truth extrapolation labels
        return 0.5  # Placeholder


class AnomalyDetectionMetrics(EvaluationMetrics):
    """Metrics for anomaly detection."""
    
    def __init__(self):
        super().__init__()
    
    def evaluate_all(
        self,
        anomaly_scores: np.ndarray,
        is_anomaly: np.ndarray,
        threshold: Optional[float] = None
    ) -> Dict[str, MetricResult]:
        """Evaluate all anomaly detection metrics."""
        results = {}
        
        # Use OOD detection metrics as base
        ood_metrics = OODDetectionMetrics()
        ood_results = ood_metrics.evaluate_all(anomaly_scores, is_anomaly, threshold)
        
        # Add anomaly-specific metrics
        results.update(ood_results)
        
        # Anomaly detection specific metrics
        results['anomaly_detection_rate'] = MetricResult(
            metric_name='anomaly_detection_rate',
            value=self._compute_anomaly_detection_rate(anomaly_scores, is_anomaly, threshold)
        )
        
        return results
    
    def _compute_anomaly_detection_rate(
        self, 
        anomaly_scores: np.ndarray, 
        is_anomaly: np.ndarray, 
        threshold: float
    ) -> float:
        """Compute anomaly detection rate."""
        if threshold is None:
            return 0.0
        
        predicted_anomalies = anomaly_scores > threshold
        true_anomalies = is_anomaly == 1
        
        if true_anomalies.sum() == 0:
            return 0.0
        
        return (predicted_anomalies & true_anomalies).sum() / true_anomalies.sum()


class PerformanceMetrics:
    """Metrics for system performance evaluation."""
    
    def __init__(self):
        self.timings: List[float] = []
        self.memory_usage: List[float] = []
    
    def start_timing(self) -> float:
        """Start timing measurement."""
        return time.time()
    
    def end_timing(self, start_time: float) -> float:
        """End timing measurement and record result."""
        elapsed = time.time() - start_time
        self.timings.append(elapsed)
        return elapsed
    
    def record_memory_usage(self, memory_mb: float) -> None:
        """Record memory usage."""
        self.memory_usage.append(memory_mb)
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        if not self.timings:
            return {}
        
        return {
            'mean_latency': np.mean(self.timings),
            'std_latency': np.std(self.timings),
            'min_latency': np.min(self.timings),
            'max_latency': np.max(self.timings),
            'p95_latency': np.percentile(self.timings, 95),
            'p99_latency': np.percentile(self.timings, 99)
        }
    
    def get_throughput(self, batch_size: int = 1) -> float:
        """Get throughput in samples per second."""
        if not self.timings:
            return 0.0
        
        mean_latency = np.mean(self.timings)
        return batch_size / mean_latency if mean_latency > 0 else 0.0
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        if not self.memory_usage:
            return {}
        
        return {
            'mean_memory': np.mean(self.memory_usage),
            'max_memory': np.max(self.memory_usage),
            'min_memory': np.min(self.memory_usage)
        }
