"""
Comprehensive benchmarking and evaluation framework for XtrapNet.

This module provides standardized benchmarks and evaluation metrics
for all XtrapNet components, enabling fair comparison and validation
of the system's capabilities.
"""

from .evaluation_metrics import (
    EvaluationMetrics,
    OODDetectionMetrics,
    UncertaintyMetrics,
    ExtrapolationMetrics,
    AnomalyDetectionMetrics
)

from .benchmark_datasets import (
    BenchmarkDataset,
    SyntheticOODDataset,
    RealWorldOODDataset,
    AnomalyDetectionDataset
)

from .benchmark_suite import (
    BenchmarkSuite,
    BenchmarkConfig,
    OODBenchmark,
    UncertaintyBenchmark,
    ExtrapolationBenchmark,
    AnomalyBenchmark,
    FullSystemBenchmark
)

from .reporting import (
    BenchmarkReport,
    ComparisonReport,
    PerformanceReport,
    BenchmarkReporter
)

__all__ = [
    # Evaluation metrics
    "EvaluationMetrics",
    "OODDetectionMetrics", 
    "UncertaintyMetrics",
    "ExtrapolationMetrics",
    "AnomalyDetectionMetrics",
    
    # Benchmark datasets
    "BenchmarkDataset",
    "SyntheticOODDataset",
    "RealWorldOODDataset", 
    "AnomalyDetectionDataset",
    
    # Benchmark suites
    "BenchmarkSuite",
    "BenchmarkConfig",
    "OODBenchmark",
    "UncertaintyBenchmark",
    "ExtrapolationBenchmark",
    "AnomalyBenchmark",
    "FullSystemBenchmark",
    
    # Reporting
    "BenchmarkReport",
    "ComparisonReport",
    "PerformanceReport",
    "BenchmarkReporter",
]
