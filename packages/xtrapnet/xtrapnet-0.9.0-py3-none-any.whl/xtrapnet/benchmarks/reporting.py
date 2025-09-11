"""
Reporting and visualization tools for benchmark results.

This module provides comprehensive reporting capabilities for benchmark results,
including summary statistics, comparisons, and visualizations.
"""

from __future__ import annotations

import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import time

from .benchmark_suite import BenchmarkResult


@dataclass
class BenchmarkReport:
    """Comprehensive benchmark report."""
    report_name: str
    timestamp: str
    benchmark_results: List[BenchmarkResult]
    summary_stats: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ComparisonReport:
    """Report comparing multiple methods or benchmarks."""
    comparison_name: str
    timestamp: str
    method_comparisons: Dict[str, List[BenchmarkResult]]
    ranking: Dict[str, int]
    statistical_tests: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceReport:
    """Performance-focused benchmark report."""
    report_name: str
    timestamp: str
    performance_metrics: Dict[str, Any]
    scalability_analysis: Dict[str, Any]
    resource_usage: Dict[str, Any]
    recommendations: List[str]
    metadata: Optional[Dict[str, Any]] = None


class BenchmarkReporter:
    """Main class for generating benchmark reports."""
    
    def __init__(self, output_dir: str = "./benchmark_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_benchmark_report(
        self,
        results: List[BenchmarkResult],
        report_name: str = "benchmark_report"
    ) -> BenchmarkReport:
        """Generate a comprehensive benchmark report."""
        # Compute summary statistics
        summary_stats = self._compute_summary_statistics(results)
        
        # Create report
        report = BenchmarkReport(
            report_name=report_name,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            benchmark_results=results,
            summary_stats=summary_stats,
            metadata={
                "n_results": len(results),
                "generated_by": "XtrapNet Benchmark Reporter"
            }
        )
        
        # Save report
        self._save_benchmark_report(report)
        
        return report
    
    def generate_comparison_report(
        self,
        method_results: Dict[str, List[BenchmarkResult]],
        comparison_name: str = "method_comparison"
    ) -> ComparisonReport:
        """Generate a comparison report for multiple methods."""
        # Compute rankings
        ranking = self._compute_method_ranking(method_results)
        
        # Perform statistical tests
        statistical_tests = self._perform_statistical_tests(method_results)
        
        # Create report
        report = ComparisonReport(
            comparison_name=comparison_name,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            method_comparisons=method_results,
            ranking=ranking,
            statistical_tests=statistical_tests,
            metadata={
                "n_methods": len(method_results),
                "generated_by": "XtrapNet Benchmark Reporter"
            }
        )
        
        # Save report
        self._save_comparison_report(report)
        
        return report
    
    def generate_performance_report(
        self,
        results: List[BenchmarkResult],
        report_name: str = "performance_report"
    ) -> PerformanceReport:
        """Generate a performance-focused report."""
        # Analyze performance metrics
        performance_metrics = self._analyze_performance_metrics(results)
        
        # Analyze scalability
        scalability_analysis = self._analyze_scalability(results)
        
        # Analyze resource usage
        resource_usage = self._analyze_resource_usage(results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(performance_metrics, resource_usage)
        
        # Create report
        report = PerformanceReport(
            report_name=report_name,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            performance_metrics=performance_metrics,
            scalability_analysis=scalability_analysis,
            resource_usage=resource_usage,
            recommendations=recommendations,
            metadata={
                "n_results": len(results),
                "generated_by": "XtrapNet Benchmark Reporter"
            }
        )
        
        # Save report
        self._save_performance_report(report)
        
        return report
    
    def _compute_summary_statistics(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Compute summary statistics for benchmark results."""
        if not results:
            return {}
        
        # Aggregate all metrics
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
        
        # Compute statistics for each metric
        metric_stats = {}
        for metric_name, values in all_metrics.items():
            metric_stats[metric_name] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "median": float(np.median(values)),
                "q25": float(np.percentile(values, 25)),
                "q75": float(np.percentile(values, 75))
            }
        
        # Performance statistics
        performance_stats = {
            "execution_time": {
                "mean": float(np.mean(execution_times)),
                "std": float(np.std(execution_times)),
                "min": float(np.min(execution_times)),
                "max": float(np.max(execution_times)),
                "median": float(np.median(execution_times))
            },
            "memory_usage": {
                "mean": float(np.mean(memory_usage)),
                "std": float(np.std(memory_usage)),
                "min": float(np.min(memory_usage)),
                "max": float(np.max(memory_usage)),
                "median": float(np.median(memory_usage))
            }
        }
        
        return {
            "metrics": metric_stats,
            "performance": performance_stats,
            "n_evaluations": len(results)
        }
    
    def _compute_method_ranking(self, method_results: Dict[str, List[BenchmarkResult]]) -> Dict[str, int]:
        """Compute ranking of methods based on performance."""
        # Aggregate metrics for each method
        method_scores = {}
        
        for method_name, results in method_results.items():
            if not results:
                continue
            
            # Compute average score across all metrics
            all_scores = []
            for result in results:
                for metric_name, metric_value in result.metrics.items():
                    all_scores.append(metric_value)
            
            if all_scores:
                method_scores[method_name] = np.mean(all_scores)
            else:
                method_scores[method_name] = 0.0
        
        # Rank methods (higher scores are better)
        sorted_methods = sorted(method_scores.items(), key=lambda x: x[1], reverse=True)
        ranking = {method: rank + 1 for rank, (method, _) in enumerate(sorted_methods)}
        
        return ranking
    
    def _perform_statistical_tests(self, method_results: Dict[str, List[BenchmarkResult]]) -> Dict[str, Any]:
        """Perform statistical tests to compare methods."""
        # This is a simplified version - in practice, you'd use proper statistical tests
        # like t-tests, ANOVA, etc.
        
        statistical_tests = {}
        
        # Get all method names
        method_names = list(method_results.keys())
        
        if len(method_names) < 2:
            return {"message": "Need at least 2 methods for statistical comparison"}
        
        # Compare each pair of methods
        for i, method1 in enumerate(method_names):
            for method2 in method_names[i+1:]:
                comparison_key = f"{method1}_vs_{method2}"
                
                # Get scores for both methods
                scores1 = []
                scores2 = []
                
                for result in method_results[method1]:
                    scores1.extend(result.metrics.values())
                
                for result in method_results[method2]:
                    scores2.extend(result.metrics.values())
                
                if scores1 and scores2:
                    # Simple comparison (mean difference)
                    mean_diff = np.mean(scores1) - np.mean(scores2)
                    statistical_tests[comparison_key] = {
                        "mean_difference": float(mean_diff),
                        "method1_mean": float(np.mean(scores1)),
                        "method2_mean": float(np.mean(scores2)),
                        "method1_std": float(np.std(scores1)),
                        "method2_std": float(np.std(scores2))
                    }
        
        return statistical_tests
    
    def _analyze_performance_metrics(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze performance metrics."""
        if not results:
            return {}
        
        execution_times = [r.execution_time for r in results]
        memory_usage = [r.memory_usage for r in results]
        
        # Compute throughput (assuming batch size of 1)
        throughputs = [1.0 / t if t > 0 else 0 for t in execution_times]
        
        return {
            "latency": {
                "mean": float(np.mean(execution_times)),
                "std": float(np.std(execution_times)),
                "p95": float(np.percentile(execution_times, 95)),
                "p99": float(np.percentile(execution_times, 99))
            },
            "throughput": {
                "mean": float(np.mean(throughputs)),
                "std": float(np.std(throughputs)),
                "max": float(np.max(throughputs))
            },
            "memory": {
                "mean": float(np.mean(memory_usage)),
                "max": float(np.max(memory_usage)),
                "min": float(np.min(memory_usage))
            }
        }
    
    def _analyze_scalability(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze scalability characteristics."""
        # This is a simplified analysis - in practice, you'd need more data points
        # with different dataset sizes
        
        if len(results) < 2:
            return {"message": "Need more data points for scalability analysis"}
        
        execution_times = [r.execution_time for r in results]
        
        # Simple scalability metrics
        scalability = {
            "time_variance": float(np.var(execution_times)),
            "time_stability": float(1.0 / (1.0 + np.std(execution_times) / np.mean(execution_times))),
            "performance_consistency": "high" if np.std(execution_times) < np.mean(execution_times) * 0.1 else "medium" if np.std(execution_times) < np.mean(execution_times) * 0.3 else "low"
        }
        
        return scalability
    
    def _analyze_resource_usage(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze resource usage patterns."""
        if not results:
            return {}
        
        memory_usage = [r.memory_usage for r in results]
        execution_times = [r.execution_time for r in results]
        
        # Compute resource efficiency
        resource_efficiency = []
        for mem, time in zip(memory_usage, execution_times):
            if time > 0:
                efficiency = 1.0 / (mem * time)  # Higher is better
                resource_efficiency.append(efficiency)
        
        return {
            "memory_efficiency": {
                "mean": float(np.mean(memory_usage)),
                "max": float(np.max(memory_usage)),
                "min": float(np.min(memory_usage))
            },
            "resource_efficiency": {
                "mean": float(np.mean(resource_efficiency)) if resource_efficiency else 0.0,
                "std": float(np.std(resource_efficiency)) if resource_efficiency else 0.0
            },
            "resource_utilization": "efficient" if np.mean(memory_usage) < 100 else "moderate" if np.mean(memory_usage) < 500 else "high"
        }
    
    def _generate_recommendations(
        self, 
        performance_metrics: Dict[str, Any], 
        resource_usage: Dict[str, Any]
    ) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Latency recommendations
        if "latency" in performance_metrics:
            mean_latency = performance_metrics["latency"]["mean"]
            if mean_latency > 1.0:
                recommendations.append("Consider optimizing for lower latency - current mean latency is high")
            elif mean_latency < 0.1:
                recommendations.append("Excellent latency performance - system is well optimized")
        
        # Memory recommendations
        if "memory" in resource_usage:
            mean_memory = resource_usage["memory_efficiency"]["mean"]
            if mean_memory > 1000:
                recommendations.append("High memory usage detected - consider memory optimization")
            elif mean_memory < 100:
                recommendations.append("Good memory efficiency - system is memory optimized")
        
        # Throughput recommendations
        if "throughput" in performance_metrics:
            mean_throughput = performance_metrics["throughput"]["mean"]
            if mean_throughput < 1.0:
                recommendations.append("Low throughput detected - consider batch processing or parallelization")
            elif mean_throughput > 100:
                recommendations.append("Excellent throughput performance")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System performance is within acceptable ranges")
        
        return recommendations
    
    def _save_benchmark_report(self, report: BenchmarkReport) -> None:
        """Save benchmark report to disk."""
        report_file = self.output_dir / f"{report.report_name}.json"
        
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        print(f"Benchmark report saved to {report_file}")
    
    def _save_comparison_report(self, report: ComparisonReport) -> None:
        """Save comparison report to disk."""
        report_file = self.output_dir / f"{report.comparison_name}.json"
        
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        print(f"Comparison report saved to {report_file}")
    
    def _save_performance_report(self, report: PerformanceReport) -> None:
        """Save performance report to disk."""
        report_file = self.output_dir / f"{report.report_name}.json"
        
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        print(f"Performance report saved to {report_file}")
    
    def create_summary_table(self, results: List[BenchmarkResult]) -> str:
        """Create a summary table of benchmark results."""
        if not results:
            return "No results to display"
        
        # Create table header
        table = "Benchmark Results Summary\n"
        table += "=" * 50 + "\n"
        table += f"{'Method':<20} {'Dataset':<15} {'AUC-ROC':<10} {'Latency':<10}\n"
        table += "-" * 50 + "\n"
        
        # Add rows
        for result in results:
            auc_roc = result.metrics.get('auc_roc', 0.0)
            latency = result.execution_time
            
            table += f"{result.method_name:<20} {result.metadata.get('dataset', 'unknown'):<15} {auc_roc:<10.3f} {latency:<10.3f}\n"
        
        return table
    
    def print_summary(self, results: List[BenchmarkResult]) -> None:
        """Print a summary of benchmark results."""
        print(self.create_summary_table(results))
        
        # Print additional statistics
        if results:
            print(f"\nTotal evaluations: {len(results)}")
            
            # Find best performing method
            best_result = max(results, key=lambda r: r.metrics.get('auc_roc', 0.0))
            print(f"Best performing method: {best_result.method_name} (AUC-ROC: {best_result.metrics.get('auc_roc', 0.0):.3f})")
            
            # Performance statistics
            execution_times = [r.execution_time for r in results]
            print(f"Average execution time: {np.mean(execution_times):.3f}s")
            print(f"Execution time range: {np.min(execution_times):.3f}s - {np.max(execution_times):.3f}s")
