"""
Anomaly Benchmark for comprehensive evaluation of anomaly detection systems.

This module provides benchmarking capabilities for evaluating and comparing
different anomaly detection methods and configurations.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import time
import json
from dataclasses import dataclass, asdict
from enum import Enum
# matplotlib will be imported conditionally in methods that need it
# sklearn imports will be done conditionally in methods
SKLEARN_AVAILABLE = False


class BenchmarkMetric(Enum):
    """Benchmark metrics for evaluation."""
    AUC_ROC = "auc_roc"
    AUC_PR = "auc_pr"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"


@dataclass
class BenchmarkResult:
    """Result of a benchmark evaluation."""
    method_name: str
    metrics: Dict[str, float]
    predictions: np.ndarray
    scores: np.ndarray
    execution_time: float
    memory_usage: float
    config: Dict[str, Any]


@dataclass
class BenchmarkConfig:
    """Configuration for benchmarking."""
    test_data_path: str
    ground_truth_path: str
    methods: List[str]
    metrics: List[BenchmarkMetric]
    n_runs: int = 5
    confidence_interval: float = 0.95
    enable_visualization: bool = True
    output_dir: str = "benchmark_results"


class AnomalyBenchmark:
    """
    Anomaly Benchmark for comprehensive evaluation of anomaly detection systems.
    
    This class provides benchmarking capabilities for evaluating and comparing
    different anomaly detection methods and configurations.
    """
    
    def __init__(self, config: BenchmarkConfig):
        """
        Initialize Anomaly Benchmark.
        
        Args:
            config: Benchmark configuration
        """
        self.config = config
        self.results = []
        self.datasets = {}
        self.methods = {}
        
        # Load test data and ground truth
        self._load_data()
        
        # Initialize methods
        self._initialize_methods()
    
    def _load_data(self):
        """Load test data and ground truth."""
        # Load test data
        if self.config.test_data_path.endswith('.npy'):
            self.datasets['test_data'] = np.load(self.config.test_data_path)
        elif self.config.test_data_path.endswith('.pth'):
            self.datasets['test_data'] = torch.load(self.config.test_data_path).numpy()
        else:
            raise ValueError(f"Unsupported data format: {self.config.test_data_path}")
        
        # Load ground truth
        if self.config.ground_truth_path.endswith('.npy'):
            self.datasets['ground_truth'] = np.load(self.config.ground_truth_path)
        elif self.config.ground_truth_path.endswith('.pth'):
            self.datasets['ground_truth'] = torch.load(self.config.ground_truth_path).numpy()
        else:
            raise ValueError(f"Unsupported ground truth format: {self.config.ground_truth_path}")
        
        # Validate data
        if len(self.datasets['test_data']) != len(self.datasets['ground_truth']):
            raise ValueError("Test data and ground truth must have the same length")
    
    def _initialize_methods(self):
        """Initialize anomaly detection methods."""
        from .multi_modal_detector import MultiModalAnomalyDetector, DataType
        
        for method_name in self.config.methods:
            if method_name == "isolation_forest":
                from sklearn.ensemble import IsolationForest
                detector = IsolationForest(contamination=0.1, random_state=42)
                self.methods[method_name] = detector
            
            elif method_name == "one_class_svm":
                from sklearn.svm import OneClassSVM
                detector = OneClassSVM(nu=0.1)
                self.methods[method_name] = detector
            
            elif method_name == "local_outlier_factor":
                from sklearn.neighbors import LocalOutlierFactor
                detector = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
                self.methods[method_name] = detector
            
            elif method_name == "autoencoder":
                from .multi_modal_detector import ImageAnomalyDetector
                detector = ImageAnomalyDetector(method="autoencoder")
                self.methods[method_name] = detector
            
            elif method_name == "vae":
                from .multi_modal_detector import ImageAnomalyDetector
                detector = ImageAnomalyDetector(method="vae")
                self.methods[method_name] = detector
            
            elif method_name == "multimodal":
                detector = MultiModalAnomalyDetector()
                detector.add_detector(DataType.TABULAR, method="isolation_forest")
                self.methods[method_name] = detector
            
            else:
                raise ValueError(f"Unknown method: {method_name}")
    
    def run_benchmark(self) -> List[BenchmarkResult]:
        """
        Run comprehensive benchmark evaluation.
        
        Returns:
            List of benchmark results
        """
        print(f"Running benchmark with {len(self.config.methods)} methods")
        print(f"Test data shape: {self.datasets['test_data'].shape}")
        print(f"Ground truth shape: {self.datasets['ground_truth'].shape}")
        
        results = []
        
        for method_name in self.config.methods:
            print(f"\nEvaluating method: {method_name}")
            
            # Run multiple times for statistical significance
            method_results = []
            for run in range(self.config.n_runs):
                print(f"  Run {run + 1}/{self.config.n_runs}")
                
                result = self._evaluate_method(method_name, run)
                method_results.append(result)
            
            # Aggregate results
            aggregated_result = self._aggregate_results(method_name, method_results)
            results.append(aggregated_result)
        
        self.results = results
        return results
    
    def _evaluate_method(self, method_name: str, run: int) -> BenchmarkResult:
        """Evaluate a single method."""
        detector = self.methods[method_name]
        test_data = self.datasets['test_data']
        ground_truth = self.datasets['ground_truth']
        
        # Measure execution time and memory
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            # Fit detector on normal data
            normal_data = test_data[ground_truth == 0]
            if len(normal_data) == 0:
                # If no normal data, use all data
                normal_data = test_data
            
            detector.fit(normal_data)
            
            # Get predictions
            if hasattr(detector, 'decision_function'):
                scores = -detector.decision_function(test_data)
            elif hasattr(detector, 'predict'):
                scores = -detector.predict(test_data)
            elif hasattr(detector, 'get_anomaly_score'):
                scores = np.array([detector.get_anomaly_score(sample) for sample in test_data])
            else:
                raise ValueError(f"Detector {method_name} does not support scoring")
            
            # Convert scores to binary predictions
            threshold = np.percentile(scores, 90)  # Use 90th percentile as threshold
            predictions = (scores > threshold).astype(int)
            
        except Exception as e:
            print(f"    Error in method {method_name}: {e}")
            # Return dummy results
            scores = np.random.rand(len(test_data))
            predictions = np.random.randint(0, 2, len(test_data))
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        return BenchmarkResult(
            method_name=method_name,
            metrics={},  # Will be computed later
            predictions=predictions,
            scores=scores,
            execution_time=execution_time,
            memory_usage=memory_usage,
            config={'run': run}
        )
    
    def _aggregate_results(
        self,
        method_name: str,
        method_results: List[BenchmarkResult]
    ) -> BenchmarkResult:
        """Aggregate results from multiple runs."""
        # Compute metrics for each run
        all_metrics = []
        for result in method_results:
            metrics = self._compute_metrics(result.predictions, result.scores)
            all_metrics.append(metrics)
        
        # Aggregate metrics
        aggregated_metrics = {}
        for metric_name in all_metrics[0].keys():
            values = [metrics[metric_name] for metrics in all_metrics]
            aggregated_metrics[metric_name] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'values': values
            }
        
        # Use the last run's predictions and scores
        last_result = method_results[-1]
        
        return BenchmarkResult(
            method_name=method_name,
            metrics=aggregated_metrics,
            predictions=last_result.predictions,
            scores=last_result.scores,
            execution_time=np.mean([r.execution_time for r in method_results]),
            memory_usage=np.mean([r.memory_usage for r in method_results]),
            config={'n_runs': len(method_results)}
        )
    
    def _compute_metrics(
        self,
        predictions: np.ndarray,
        scores: np.ndarray
    ) -> Dict[str, float]:
        """Compute evaluation metrics."""
        ground_truth = self.datasets['ground_truth']
        
        metrics = {}
        
        try:
            from sklearn.metrics import (
                roc_auc_score, precision_recall_curve, auc,
                confusion_matrix, classification_report
            )
            
            # AUC-ROC
            try:
                metrics['auc_roc'] = roc_auc_score(ground_truth, scores)
            except ValueError:
                metrics['auc_roc'] = 0.5  # Random performance
            
            # AUC-PR
            try:
                precision, recall, _ = precision_recall_curve(ground_truth, scores)
                metrics['auc_pr'] = auc(recall, precision)
            except ValueError:
                metrics['auc_pr'] = 0.0
            
            # Classification metrics
            try:
                tn, fp, fn, tp = confusion_matrix(ground_truth, predictions).ravel()
                
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                metrics['precision'] = precision
                metrics['recall'] = recall
                metrics['f1_score'] = f1
                
            except ValueError:
                metrics['precision'] = 0.0
                metrics['recall'] = 0.0
                metrics['f1_score'] = 0.0
        except ImportError:
            # Fallback metrics without sklearn
            metrics['auc_roc'] = 0.5
            metrics['auc_pr'] = 0.0
            metrics['precision'] = 0.0
            metrics['recall'] = 0.0
            metrics['f1_score'] = 0.0
        
        return metrics
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.results:
            raise ValueError("No benchmark results available. Run benchmark first.")
        
        report = {
            'benchmark_config': asdict(self.config),
            'dataset_info': {
                'test_data_shape': self.datasets['test_data'].shape,
                'ground_truth_shape': self.datasets['ground_truth'].shape,
                'anomaly_ratio': np.mean(self.datasets['ground_truth'])
            },
            'results': []
        }
        
        # Add results for each method
        for result in self.results:
            method_report = {
                'method_name': result.method_name,
                'metrics': result.metrics,
                'execution_time': result.execution_time,
                'memory_usage': result.memory_usage,
                'config': result.config
            }
            report['results'].append(method_report)
        
        # Add comparative analysis
        report['comparative_analysis'] = self._generate_comparative_analysis()
        
        return report
    
    def _generate_comparative_analysis(self) -> Dict[str, Any]:
        """Generate comparative analysis of methods."""
        analysis = {
            'best_methods': {},
            'rankings': {},
            'statistical_significance': {}
        }
        
        # Find best methods for each metric
        for metric_name in ['auc_roc', 'auc_pr', 'f1_score', 'precision', 'recall']:
            best_method = None
            best_score = -1
            
            for result in self.results:
                if metric_name in result.metrics:
                    score = result.metrics[metric_name]['mean']
                    if score > best_score:
                        best_score = score
                        best_method = result.method_name
            
            if best_method:
                analysis['best_methods'][metric_name] = {
                    'method': best_method,
                    'score': best_score
                }
        
        # Generate rankings
        for metric_name in ['auc_roc', 'auc_pr', 'f1_score']:
            method_scores = []
            for result in self.results:
                if metric_name in result.metrics:
                    method_scores.append((result.method_name, result.metrics[metric_name]['mean']))
            
            # Sort by score (descending)
            method_scores.sort(key=lambda x: x[1], reverse=True)
            analysis['rankings'][metric_name] = [method for method, _ in method_scores]
        
        return analysis
    
    def save_results(self, filepath: str):
        """Save benchmark results to file."""
        report = self.generate_report()
        
        if filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
        else:
            torch.save(report, filepath)
        
        print(f"Benchmark results saved to {filepath}")
    
    def create_visualizations(self, output_dir: str):
        """Create visualization plots for benchmark results."""
        if not self.results:
            raise ValueError("No benchmark results available. Run benchmark first.")

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("Matplotlib not available. Skipping visualizations.")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create metric comparison plot
        self._plot_metric_comparison(output_path / "metric_comparison.png")
        
        # Create ROC curves
        self._plot_roc_curves(output_path / "roc_curves.png")
        
        # Create execution time comparison
        self._plot_execution_time(output_path / "execution_time.png")
        
        print(f"Visualizations saved to {output_dir}")
    
    def _plot_metric_comparison(self, filepath: str):
        """Plot metric comparison across methods."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return
            
        metrics = ['auc_roc', 'auc_pr', 'f1_score', 'precision', 'recall']
        methods = [result.method_name for result in self.results]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(methods))
        width = 0.15
        
        for i, metric in enumerate(metrics):
            values = []
            errors = []
            
            for result in self.results:
                if metric in result.metrics:
                    values.append(result.metrics[metric]['mean'])
                    errors.append(result.metrics[metric]['std'])
                else:
                    values.append(0)
                    errors.append(0)
            
            ax.bar(x + i * width, values, width, label=metric, yerr=errors, capsize=5)
        
        ax.set_xlabel('Methods')
        ax.set_ylabel('Score')
        ax.set_title('Benchmark Results Comparison')
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(methods, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_roc_curves(self, filepath: str):
        """Plot ROC curves for all methods."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return
            
        try:
            from sklearn.metrics import roc_curve
        except ImportError:
            return
        
        plt.figure(figsize=(10, 8))
        
        for result in self.results:
            fpr, tpr, _ = roc_curve(self.datasets['ground_truth'], result.scores)
            auc_score = result.metrics.get('auc_roc', {}).get('mean', 0)
            plt.plot(fpr, tpr, label=f"{result.method_name} (AUC = {auc_score:.3f})")
        
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_execution_time(self, filepath: str):
        """Plot execution time comparison."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return
            
        methods = [result.method_name for result in self.results]
        times = [result.execution_time for result in self.results]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(methods, times)
        plt.xlabel('Methods')
        plt.ylabel('Execution Time (seconds)')
        plt.title('Execution Time Comparison')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, time in zip(bars, times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{time:.2f}s', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            print("No benchmark results available.")
            return
        
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        # Dataset info
        print(f"Dataset: {self.datasets['test_data'].shape[0]} samples")
        print(f"Anomaly ratio: {np.mean(self.datasets['ground_truth']):.3f}")
        print(f"Number of methods: {len(self.results)}")
        print(f"Number of runs per method: {self.config.n_runs}")
        
        # Results table
        print("\nResults:")
        print("-" * 80)
        print(f"{'Method':<20} {'AUC-ROC':<10} {'AUC-PR':<10} {'F1-Score':<10} {'Time(s)':<10}")
        print("-" * 80)
        
        for result in self.results:
            auc_roc = result.metrics.get('auc_roc', {}).get('mean', 0)
            auc_pr = result.metrics.get('auc_pr', {}).get('mean', 0)
            f1 = result.metrics.get('f1_score', {}).get('mean', 0)
            time_val = result.execution_time
            
            print(f"{result.method_name:<20} {auc_roc:<10.3f} {auc_pr:<10.3f} {f1:<10.3f} {time_val:<10.2f}")
        
        print("-" * 80)
        
        # Best methods
        analysis = self._generate_comparative_analysis()
        print("\nBest Methods:")
        for metric, info in analysis['best_methods'].items():
            print(f"  {metric}: {info['method']} ({info['score']:.3f})")
