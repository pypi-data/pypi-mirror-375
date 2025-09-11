"""
Comprehensive benchmark suite for evaluating XtrapNet components.

This module provides standardized benchmarks for evaluating all aspects
of the XtrapNet system including OOD detection, uncertainty quantification,
extrapolation control, and anomaly detection.
"""

from __future__ import annotations

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import time
import json
from pathlib import Path

from .evaluation_metrics import (
    OODDetectionMetrics, UncertaintyMetrics, ExtrapolationMetrics,
    AnomalyDetectionMetrics, PerformanceMetrics
)
from .benchmark_datasets import (
    BenchmarkDataset, SyntheticOODDataset, RealWorldOODDataset,
    AnomalyDetectionDataset
)


@dataclass
class BenchmarkResult:
    """Result of a benchmark evaluation."""
    benchmark_name: str
    method_name: str
    metrics: Dict[str, float]
    execution_time: float
    memory_usage: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution."""
    n_runs: int = 5
    confidence_level: float = 0.95
    save_results: bool = True
    output_dir: str = "./benchmark_results"
    verbose: bool = True


class BenchmarkSuite:
    """Base class for benchmark suites."""
    
    def __init__(self, name: str, config: Optional[BenchmarkConfig] = None):
        self.name = name
        self.config = config or BenchmarkConfig()
        self.results: List[BenchmarkResult] = []
        self.datasets: Dict[str, BenchmarkDataset] = {}
    
    def add_dataset(self, name: str, dataset: BenchmarkDataset) -> None:
        """Add a dataset to the benchmark suite."""
        self.datasets[name] = dataset
    
    def run_benchmark(
        self,
        method: Any,
        dataset_name: str,
        method_name: str = "unknown"
    ) -> BenchmarkResult:
        """Run a single benchmark evaluation."""
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        dataset = self.datasets[dataset_name]
        dataset.load_data()
        
        # Get dataset split
        split = dataset.get_split("train")
        
        # Run benchmark
        start_time = time.time()
        metrics = self._evaluate_method(method, split)
        execution_time = time.time() - start_time
        
        # Get memory usage
        memory_usage = self._get_memory_usage()
        
        # Create result
        result = BenchmarkResult(
            benchmark_name=self.name,
            method_name=method_name,
            metrics=metrics,
            execution_time=execution_time,
            memory_usage=memory_usage,
            metadata={"dataset": dataset_name}
        )
        
        self.results.append(result)
        return result
    
    def _evaluate_method(self, method: Any, split: Any) -> Dict[str, float]:
        """Evaluate a method on a dataset split."""
        raise NotImplementedError
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def save_results(self, output_dir: Optional[str] = None) -> None:
        """Save benchmark results to disk."""
        output_dir = output_dir or self.config.output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save results as JSON
        results_data = [asdict(result) for result in self.results]
        results_file = output_path / f"{self.name}_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        if self.config.verbose:
            print(f"Results saved to {results_file}")


class OODBenchmark(BenchmarkSuite):
    """Benchmark suite for OOD detection evaluation."""
    
    def __init__(self, config: Optional[BenchmarkConfig] = None):
        super().__init__("OOD Detection", config)
        self._setup_default_datasets()
    
    def _setup_default_datasets(self) -> None:
        """Setup default datasets for OOD detection."""
        # Synthetic dataset
        synthetic_dataset = SyntheticOODDataset(
            n_samples=5000,
            n_features=10,
            complexity="medium"
        )
        self.add_dataset("synthetic", synthetic_dataset)
        
        # Real-world datasets
        try:
            cifar10_dataset = RealWorldOODDataset(
                dataset_name="cifar10",
                target_class=0,
                ood_classes=[1, 2, 3, 4, 5]
            )
            self.add_dataset("cifar10", cifar10_dataset)
        except Exception as e:
            print(f"Could not load CIFAR-10 dataset: {e}")
        
        try:
            mnist_dataset = RealWorldOODDataset(
                dataset_name="mnist",
                target_class=0,
                ood_classes=[1, 2, 3, 4, 5]
            )
            self.add_dataset("mnist", mnist_dataset)
        except Exception as e:
            print(f"Could not load MNIST dataset: {e}")
    
    def _evaluate_method(self, method: Any, split: Any) -> Dict[str, float]:
        """Evaluate OOD detection method."""
        # Train method on training data
        if hasattr(method, 'fit'):
            method.fit(split.train_data)
        
        # Get OOD scores for test data
        if hasattr(method, 'predict_ood_scores'):
            ood_scores = method.predict_ood_scores(split.test_data)
        elif hasattr(method, 'predict'):
            ood_scores = method.predict(split.test_data)
        else:
            raise ValueError("Method must have 'predict_ood_scores' or 'predict' method")
        
        # Evaluate metrics
        ood_metrics = OODDetectionMetrics()
        results = ood_metrics.evaluate_all(ood_scores, split.test_labels)
        
        # Extract metric values
        metrics = {name: result.value for name, result in results.items()}
        return metrics


class UncertaintyBenchmark(BenchmarkSuite):
    """Benchmark suite for uncertainty quantification evaluation."""
    
    def __init__(self, config: Optional[BenchmarkConfig] = None):
        super().__init__("Uncertainty Quantification", config)
        self._setup_default_datasets()
    
    def _setup_default_datasets(self) -> None:
        """Setup default datasets for uncertainty quantification."""
        # Use synthetic dataset
        synthetic_dataset = SyntheticOODDataset(
            n_samples=5000,
            n_features=10,
            complexity="medium"
        )
        self.add_dataset("synthetic", synthetic_dataset)
    
    def _evaluate_method(self, method: Any, split: Any) -> Dict[str, float]:
        """Evaluate uncertainty quantification method."""
        # Train method on training data
        if hasattr(method, 'fit'):
            method.fit(split.train_data, split.train_labels)
        
        # Get predictions and uncertainties
        if hasattr(method, 'predict_with_uncertainty'):
            predictions, uncertainties = method.predict_with_uncertainty(split.test_data)
        elif hasattr(method, 'predict'):
            predictions = method.predict(split.test_data)
            # Try to get uncertainties
            if hasattr(method, 'get_uncertainty'):
                uncertainties = method.get_uncertainty(split.test_data)
            else:
                # Use dummy uncertainties
                uncertainties = np.random.rand(len(predictions))
        else:
            raise ValueError("Method must have 'predict_with_uncertainty' or 'predict' method")
        
        # Evaluate metrics
        uncertainty_metrics = UncertaintyMetrics()
        results = uncertainty_metrics.evaluate_all(predictions, uncertainties, split.test_labels)
        
        # Extract metric values
        metrics = {name: result.value for name, result in results.items()}
        return metrics


class ExtrapolationBenchmark(BenchmarkSuite):
    """Benchmark suite for extrapolation control evaluation."""
    
    def __init__(self, config: Optional[BenchmarkConfig] = None):
        super().__init__("Extrapolation Control", config)
        self._setup_default_datasets()
    
    def _setup_default_datasets(self) -> None:
        """Setup default datasets for extrapolation control."""
        # Use synthetic dataset with extrapolation scenarios
        synthetic_dataset = SyntheticOODDataset(
            n_samples=5000,
            n_features=10,
            complexity="medium"
        )
        self.add_dataset("synthetic", synthetic_dataset)
    
    def _evaluate_method(self, method: Any, split: Any) -> Dict[str, float]:
        """Evaluate extrapolation control method."""
        # Train method on training data
        if hasattr(method, 'fit'):
            method.fit(split.train_data, split.train_labels)
        
        # Get predictions and extrapolation flags
        if hasattr(method, 'predict_with_extrapolation'):
            predictions, extrapolation_flags, confidence_scores = method.predict_with_extrapolation(split.test_data)
        elif hasattr(method, 'predict'):
            predictions = method.predict(split.test_data)
            # Try to get extrapolation information
            if hasattr(method, 'is_extrapolation'):
                extrapolation_flags = method.is_extrapolation(split.test_data)
            else:
                # Use OOD labels as extrapolation flags
                extrapolation_flags = split.test_labels
            
            if hasattr(method, 'get_confidence'):
                confidence_scores = method.get_confidence(split.test_data)
            else:
                # Use dummy confidence scores
                confidence_scores = np.random.rand(len(predictions))
        else:
            raise ValueError("Method must have 'predict_with_extrapolation' or 'predict' method")
        
        # Evaluate metrics
        extrapolation_metrics = ExtrapolationMetrics()
        results = extrapolation_metrics.evaluate_all(
            predictions, split.test_labels, extrapolation_flags, confidence_scores
        )
        
        # Extract metric values
        metrics = {name: result.value for name, result in results.items()}
        return metrics


class AnomalyBenchmark(BenchmarkSuite):
    """Benchmark suite for anomaly detection evaluation."""
    
    def __init__(self, config: Optional[BenchmarkConfig] = None):
        super().__init__("Anomaly Detection", config)
        self._setup_default_datasets()
    
    def _setup_default_datasets(self) -> None:
        """Setup default datasets for anomaly detection."""
        # Synthetic anomaly dataset
        synthetic_dataset = AnomalyDetectionDataset(
            dataset_name="synthetic",
            n_samples=5000,
            anomaly_ratio=0.1,
            n_features=10
        )
        self.add_dataset("synthetic", synthetic_dataset)
        
        # Credit card fraud-like dataset
        credit_dataset = AnomalyDetectionDataset(
            dataset_name="credit_card",
            n_samples=5000,
            anomaly_ratio=0.05,
            n_features=15
        )
        self.add_dataset("credit_card", credit_dataset)
    
    def _evaluate_method(self, method: Any, split: Any) -> Dict[str, float]:
        """Evaluate anomaly detection method."""
        # Train method on training data (assuming normal samples)
        normal_mask = split.train_labels == 0
        if normal_mask.sum() > 0:
            normal_data = split.train_data[normal_mask]
            if hasattr(method, 'fit'):
                method.fit(normal_data)
        
        # Get anomaly scores for test data
        if hasattr(method, 'predict_anomaly_scores'):
            anomaly_scores = method.predict_anomaly_scores(split.test_data)
        elif hasattr(method, 'predict'):
            anomaly_scores = method.predict(split.test_data)
        else:
            raise ValueError("Method must have 'predict_anomaly_scores' or 'predict' method")
        
        # Evaluate metrics
        anomaly_metrics = AnomalyDetectionMetrics()
        results = anomaly_metrics.evaluate_all(anomaly_scores, split.test_labels)
        
        # Extract metric values
        metrics = {name: result.value for name, result in results.items()}
        return metrics


class FullSystemBenchmark:
    """Comprehensive benchmark for the entire XtrapNet system."""
    
    def __init__(self, config: Optional[BenchmarkConfig] = None):
        self.config = config or BenchmarkConfig()
        self.benchmarks = {
            'ood': OODBenchmark(config),
            'uncertainty': UncertaintyBenchmark(config),
            'extrapolation': ExtrapolationBenchmark(config),
            'anomaly': AnomalyBenchmark(config)
        }
        self.results: Dict[str, List[BenchmarkResult]] = {}
    
    def run_full_benchmark(self, xtrapnet_system: Any) -> Dict[str, List[BenchmarkResult]]:
        """Run comprehensive benchmark on XtrapNet system."""
        if self.config.verbose:
            print("Running comprehensive XtrapNet benchmark...")
        
        for benchmark_name, benchmark in self.benchmarks.items():
            if self.config.verbose:
                print(f"\nRunning {benchmark_name} benchmark...")
            
            benchmark_results = []
            
            # Run on each dataset
            for dataset_name in benchmark.datasets.keys():
                if self.config.verbose:
                    print(f"  Evaluating on {dataset_name} dataset...")
                
                # Get appropriate component from XtrapNet system
                if benchmark_name == 'ood':
                    method = getattr(xtrapnet_system, 'ood_detector', None)
                elif benchmark_name == 'uncertainty':
                    method = getattr(xtrapnet_system, 'uncertainty_estimator', None)
                elif benchmark_name == 'extrapolation':
                    method = getattr(xtrapnet_system, 'extrapolation_controller', None)
                elif benchmark_name == 'anomaly':
                    method = getattr(xtrapnet_system, 'anomaly_detector', None)
                else:
                    method = xtrapnet_system
                
                if method is not None:
                    try:
                        result = benchmark.run_benchmark(
                            method=method,
                            dataset_name=dataset_name,
                            method_name=f"xtrapnet_{benchmark_name}"
                        )
                        benchmark_results.append(result)
                    except Exception as e:
                        if self.config.verbose:
                            print(f"    Error: {e}")
                        continue
            
            self.results[benchmark_name] = benchmark_results
        
        # Save results
        if self.config.save_results:
            self._save_comprehensive_results()
        
        return self.results
    
    def _save_comprehensive_results(self) -> None:
        """Save comprehensive benchmark results."""
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual benchmark results
        for benchmark_name, benchmark in self.benchmarks.items():
            benchmark.save_results()
        
        # Save comprehensive summary
        summary = self._create_summary()
        summary_file = output_path / "comprehensive_benchmark_summary.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        if self.config.verbose:
            print(f"\nComprehensive benchmark summary saved to {summary_file}")
    
    def _create_summary(self) -> Dict[str, Any]:
        """Create comprehensive benchmark summary."""
        summary = {
            "benchmark_info": {
                "name": "XtrapNet Comprehensive Benchmark",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "config": asdict(self.config)
            },
            "results": {}
        }
        
        for benchmark_name, results in self.results.items():
            if not results:
                continue
            
            # Aggregate metrics across all results
            all_metrics = {}
            execution_times = []
            memory_usage = []
            
            for result in results:
                execution_times.append(result.execution_time)
                memory_usage.append(result.memory_usage)
                
                for metric_name, metric_value in result.metrics.items():
                    if metric_name not in all_metrics:
                        all_metrics[metric_name] = []
                    all_metrics[metric_name].append(metric_value)
            
            # Compute summary statistics
            summary["results"][benchmark_name] = {
                "n_evaluations": len(results),
                "metrics": {
                    metric_name: {
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "min": np.min(values),
                        "max": np.max(values)
                    }
                    for metric_name, values in all_metrics.items()
                },
                "performance": {
                    "mean_execution_time": np.mean(execution_times),
                    "mean_memory_usage": np.mean(memory_usage)
                }
            }
        
        return summary
