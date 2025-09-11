"""
State-of-the-Art Benchmarking Framework

This module implements a comprehensive benchmarking framework that compares
XtrapNet against actual state-of-the-art methods in uncertainty quantification,
OOD detection, and extrapolation control.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
import time
import json
from pathlib import Path

from .adaptive_uncertainty import HierarchicalUncertaintyNetwork, DensityAwareOODDetector
from .physics_constrained import AdaptivePhysicsNetwork, ExtrapolationConfidenceEstimator
from .extrapolation_meta_learning import ExtrapolationAwareMetaLearner, ExtrapolationBenchmark


@dataclass
class BenchmarkResult:
    """Result of a benchmark evaluation."""
    method_name: str
    dataset_name: str
    metrics: Dict[str, float]
    execution_time: float
    memory_usage: float
    metadata: Dict[str, Any]


class SOTABaseline:
    """Base class for SOTA baseline methods."""
    
    def __init__(self, name: str):
        self.name = name
    
    def fit(self, x: torch.Tensor, y: torch.Tensor):
        """Fit the method to training data."""
        raise NotImplementedError
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Make predictions."""
        raise NotImplementedError
    
    def predict_with_uncertainty(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Make predictions with uncertainty estimates."""
        predictions = self.predict(x)
        uncertainty = torch.zeros_like(predictions)
        return predictions, uncertainty


class DeepEnsemble(SOTABaseline):
    """Deep Ensemble baseline (Lakshminarayanan et al., 2017)."""
    
    def __init__(self, input_dim: int, output_dim: int, num_models: int = 5):
        super().__init__("DeepEnsemble")
        self.num_models = num_models
        self.models = nn.ModuleList([
            nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.ReLU(),
                nn.Linear(128, output_dim)
            )
            for _ in range(num_models)
        ])
        self.optimizers = [
            torch.optim.Adam(model.parameters(), lr=0.001)
            for model in self.models
        ]
    
    def fit(self, x: torch.Tensor, y: torch.Tensor, epochs: int = 100):
        """Train ensemble of models."""
        for model, optimizer in zip(self.models, self.optimizers):
            for epoch in range(epochs):
                optimizer.zero_grad()
                pred = model(x)
                loss = F.mse_loss(pred, y)
                loss.backward()
                optimizer.step()
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Make predictions using ensemble."""
        predictions = []
        for model in self.models:
            model.eval()
            with torch.no_grad():
                pred = model(x)
                predictions.append(pred)
        
        return torch.stack(predictions).mean(dim=0)
    
    def predict_with_uncertainty(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Make predictions with uncertainty estimates."""
        predictions = []
        for model in self.models:
            model.eval()
            with torch.no_grad():
                pred = model(x)
                predictions.append(pred)
        
        predictions = torch.stack(predictions)
        mean_pred = predictions.mean(dim=0)
        uncertainty = predictions.var(dim=0)
        
        return mean_pred, uncertainty


class MCDropout(SOTABaseline):
    """Monte Carlo Dropout baseline (Gal & Ghahramani, 2016)."""
    
    def __init__(self, input_dim: int, output_dim: int, dropout_rate: float = 0.1):
        super().__init__("MCDropout")
        self.dropout_rate = dropout_rate
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, output_dim)
        )
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
    
    def fit(self, x: torch.Tensor, y: torch.Tensor, epochs: int = 100):
        """Train the model."""
        self.model.train()
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            pred = self.model(x)
            loss = F.mse_loss(pred, y)
            loss.backward()
            self.optimizer.step()
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Make predictions."""
        self.model.eval()
        with torch.no_grad():
            return self.model(x)
    
    def predict_with_uncertainty(self, x: torch.Tensor, num_samples: int = 100) -> Tuple[torch.Tensor, torch.Tensor]:
        """Make predictions with uncertainty estimates using MC Dropout."""
        self.model.train()  # Enable dropout
        predictions = []
        
        with torch.no_grad():
            for _ in range(num_samples):
                pred = self.model(x)
                predictions.append(pred)
        
        predictions = torch.stack(predictions)
        mean_pred = predictions.mean(dim=0)
        uncertainty = predictions.var(dim=0)
        
        return mean_pred, uncertainty


class EvidentialDeepLearning(SOTABaseline):
    """Evidential Deep Learning baseline (Amini et al., 2020)."""
    
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__("EvidentialDeepLearning")
        self.output_dim = output_dim
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim * 2)  # [mu, nu]
        )
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
    
    def fit(self, x: torch.Tensor, y: torch.Tensor, epochs: int = 100):
        """Train the evidential model."""
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            output = self.model(x)
            mu, nu = output[:, :self.output_dim], output[:, self.output_dim:]
            nu = F.softplus(nu) + 1e-6  # Ensure positive
            
            # Evidential loss
            loss = self._evidential_loss(mu, nu, y)
            loss.backward()
            self.optimizer.step()
    
    def _evidential_loss(self, mu: torch.Tensor, nu: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Compute evidential loss."""
        # Simplified evidential loss
        alpha = nu + 1
        beta = nu * (y - mu) ** 2 + 1
        
        loss = torch.log(beta) - torch.log(alpha) + torch.log(nu)
        return loss.mean()
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Make predictions."""
        self.model.eval()
        with torch.no_grad():
            output = self.model(x)
            mu = output[:, :self.output_dim]
            return mu
    
    def predict_with_uncertainty(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Make predictions with uncertainty estimates."""
        self.model.eval()
        with torch.no_grad():
            output = self.model(x)
            mu, nu = output[:, :self.output_dim], output[:, self.output_dim:]
            nu = F.softplus(nu) + 1e-6
            
            # Uncertainty from evidential parameters
            uncertainty = 1.0 / nu
            
            return mu, uncertainty


class MahalanobisOOD(SOTABaseline):
    """Mahalanobis distance OOD detection baseline (Lee et al., 2018)."""
    
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__("MahalanobisOOD")
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.feature_mean = None
        self.feature_cov = None
    
    def fit(self, x: torch.Tensor, y: torch.Tensor, epochs: int = 100):
        """Train the model and compute feature statistics."""
        # Train model
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            pred = self.model(x)
            loss = F.mse_loss(pred, y)
            loss.backward()
            self.optimizer.step()
        
        # Compute feature statistics for Mahalanobis distance
        self.model.eval()
        with torch.no_grad():
            features = self._extract_features(x)
            self.feature_mean = features.mean(dim=0)
            self.feature_cov = torch.cov(features.T)
    
    def _extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features from the model."""
        # Use the last hidden layer as features
        features = x
        for layer in self.model[:-1]:
            features = layer(features)
        return features
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Make predictions."""
        self.model.eval()
        with torch.no_grad():
            return self.model(x)
    
    def predict_ood_scores(self, x: torch.Tensor) -> torch.Tensor:
        """Predict OOD scores using Mahalanobis distance."""
        if self.feature_mean is None or self.feature_cov is None:
            raise ValueError("Model must be fitted first")
        
        self.model.eval()
        with torch.no_grad():
            features = self._extract_features(x)
            
            # Compute Mahalanobis distance
            diff = features - self.feature_mean
            cov_inv = torch.inverse(self.feature_cov + 1e-6 * torch.eye(self.feature_cov.size(0)))
            mahalanobis_dist = torch.sum(diff @ cov_inv * diff, dim=1)
            
            return mahalanobis_dist


class SOTABenchmark:
    """Comprehensive SOTA benchmarking framework."""
    
    def __init__(self, output_dir: str = "./benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    def generate_synthetic_datasets(
        self,
        num_samples: int = 1000,
        input_dim: int = 2,
        output_dim: int = 1,
        noise_level: float = 0.1
    ) -> Dict[str, Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Generate synthetic datasets for benchmarking."""
        datasets = {}
        
        # Dataset 1: Polynomial regression
        x_train = torch.randn(num_samples, input_dim)
        y_train = torch.sum(x_train ** 2, dim=1, keepdim=True) + noise_level * torch.randn(num_samples, output_dim)
        x_test = torch.randn(num_samples // 4, input_dim)
        y_test = torch.sum(x_test ** 2, dim=1, keepdim=True) + noise_level * torch.randn(num_samples // 4, output_dim)
        datasets['polynomial'] = (x_train, y_train, x_test, y_test)
        
        # Dataset 2: Trigonometric function
        x_train = torch.randn(num_samples, input_dim)
        y_train = torch.sin(x_train[:, 0:1]) * torch.cos(x_train[:, 1:2]) + noise_level * torch.randn(num_samples, output_dim)
        x_test = torch.randn(num_samples // 4, input_dim)
        y_test = torch.sin(x_test[:, 0:1]) * torch.cos(x_test[:, 1:2]) + noise_level * torch.randn(num_samples // 4, output_dim)
        datasets['trigonometric'] = (x_train, y_train, x_test, y_test)
        
        # Dataset 3: Exponential function
        x_train = torch.randn(num_samples, input_dim)
        y_train = torch.exp(-torch.sum(x_train ** 2, dim=1, keepdim=True)) + noise_level * torch.randn(num_samples, output_dim)
        x_test = torch.randn(num_samples // 4, input_dim)
        y_test = torch.exp(-torch.sum(x_test ** 2, dim=1, keepdim=True)) + noise_level * torch.randn(num_samples // 4, output_dim)
        datasets['exponential'] = (x_train, y_train, x_test, y_test)
        
        return datasets
    
    def evaluate_method(
        self,
        method: SOTABaseline,
        dataset_name: str,
        x_train: torch.Tensor,
        y_train: torch.Tensor,
        x_test: torch.Tensor,
        y_test: torch.Tensor
    ) -> BenchmarkResult:
        """Evaluate a method on a dataset."""
        start_time = time.time()
        
        # Fit method
        method.fit(x_train, y_train)
        
        # Make predictions
        predictions, uncertainty = method.predict_with_uncertainty(x_test)
        
        # Compute metrics
        mse = F.mse_loss(predictions, y_test).item()
        mae = F.l1_loss(predictions, y_test).item()
        
        # Uncertainty calibration (simplified)
        if hasattr(method, 'predict_ood_scores'):
            ood_scores = method.predict_ood_scores(x_test)
            uncertainty_calibration = torch.corrcoef(torch.stack([
                uncertainty.flatten(),
                ood_scores
            ]))[0, 1].item()
        else:
            uncertainty_calibration = 0.0
        
        execution_time = time.time() - start_time
        
        # Memory usage (simplified)
        memory_usage = sum(p.numel() * p.element_size() for p in method.parameters()) / 1024 / 1024
        
        return BenchmarkResult(
            method_name=method.name,
            dataset_name=dataset_name,
            metrics={
                'mse': mse,
                'mae': mae,
                'uncertainty_calibration': uncertainty_calibration
            },
            execution_time=execution_time,
            memory_usage=memory_usage,
            metadata={
                'num_parameters': sum(p.numel() for p in method.parameters()),
                'input_dim': x_train.size(1),
                'output_dim': y_train.size(1)
            }
        )
    
    def run_comprehensive_benchmark(self) -> Dict[str, List[BenchmarkResult]]:
        """Run comprehensive benchmark against SOTA methods."""
        print("Running comprehensive SOTA benchmark...")
        
        # Generate datasets
        datasets = self.generate_synthetic_datasets()
        
        # Initialize methods
        methods = {
            'DeepEnsemble': DeepEnsemble(input_dim=2, output_dim=1),
            'MCDropout': MCDropout(input_dim=2, output_dim=1),
            'EvidentialDeepLearning': EvidentialDeepLearning(input_dim=2, output_dim=1),
            'MahalanobisOOD': MahalanobisOOD(input_dim=2, output_dim=1)
        }
        
        # Initialize XtrapNet methods
        xtrapnet_methods = {
            'XtrapNet_Uncertainty': HierarchicalUncertaintyNetwork(input_dim=2, output_dim=1),
            'XtrapNet_Physics': AdaptivePhysicsNetwork(input_dim=2, output_dim=1),
            'XtrapNet_MetaLearning': ExtrapolationAwareMetaLearner(input_dim=2, output_dim=1)
        }
        
        all_methods = {**methods, **xtrapnet_methods}
        
        # Run evaluations
        results = {}
        for dataset_name, (x_train, y_train, x_test, y_test) in datasets.items():
            print(f"Evaluating on {dataset_name} dataset...")
            dataset_results = []
            
            for method_name, method in all_methods.items():
                try:
                    result = self.evaluate_method(
                        method, dataset_name, x_train, y_train, x_test, y_test
                    )
                    dataset_results.append(result)
                    print(f"  {method_name}: MSE={result.metrics['mse']:.4f}, Time={result.execution_time:.2f}s")
                except Exception as e:
                    print(f"  {method_name}: Failed - {str(e)}")
            
            results[dataset_name] = dataset_results
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _save_results(self, results: Dict[str, List[BenchmarkResult]]):
        """Save benchmark results to disk."""
        # Convert to JSON-serializable format
        json_results = {}
        for dataset_name, dataset_results in results.items():
            json_results[dataset_name] = []
            for result in dataset_results:
                json_results[dataset_name].append({
                    'method_name': result.method_name,
                    'dataset_name': result.dataset_name,
                    'metrics': result.metrics,
                    'execution_time': result.execution_time,
                    'memory_usage': result.memory_usage,
                    'metadata': result.metadata
                })
        
        # Save to file
        results_file = self.output_dir / "sota_benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"Results saved to {results_file}")
    
    def generate_report(self, results: Dict[str, List[BenchmarkResult]]) -> str:
        """Generate a comprehensive benchmark report."""
        report = []
        report.append("# SOTA Benchmark Results")
        report.append("=" * 50)
        report.append("")
        
        for dataset_name, dataset_results in results.items():
            report.append(f"## {dataset_name.title()} Dataset")
            report.append("")
            
            # Sort by MSE
            sorted_results = sorted(dataset_results, key=lambda x: x.metrics['mse'])
            
            report.append("| Method | MSE | MAE | Uncertainty Calibration | Time (s) | Memory (MB) |")
            report.append("|--------|-----|-----|------------------------|----------|-------------|")
            
            for result in sorted_results:
                report.append(
                    f"| {result.method_name} | "
                    f"{result.metrics['mse']:.4f} | "
                    f"{result.metrics['mae']:.4f} | "
                    f"{result.metrics['uncertainty_calibration']:.4f} | "
                    f"{result.execution_time:.2f} | "
                    f"{result.memory_usage:.2f} |"
                )
            
            report.append("")
        
        return "\n".join(report)
