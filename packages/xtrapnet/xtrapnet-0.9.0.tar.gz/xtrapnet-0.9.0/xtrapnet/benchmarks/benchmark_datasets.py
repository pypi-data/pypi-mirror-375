"""
Benchmark datasets for evaluating XtrapNet components.

This module provides standardized datasets for benchmarking OOD detection,
uncertainty quantification, extrapolation control, and anomaly detection.
"""

from __future__ import annotations

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class DatasetType(Enum):
    """Types of benchmark datasets."""
    SYNTHETIC = "synthetic"
    REAL_WORLD = "real_world"
    TABULAR = "tabular"
    IMAGE = "image"
    TEXT = "text"
    TIME_SERIES = "time_series"


@dataclass
class DatasetSplit:
    """Dataset split information."""
    train_data: np.ndarray
    train_labels: np.ndarray
    test_data: np.ndarray
    test_labels: np.ndarray
    val_data: Optional[np.ndarray] = None
    val_labels: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None


class BenchmarkDataset:
    """Base class for benchmark datasets."""
    
    def __init__(
        self,
        name: str,
        dataset_type: DatasetType,
        description: str = ""
    ):
        self.name = name
        self.dataset_type = dataset_type
        self.description = description
        self.splits: Dict[str, DatasetSplit] = {}
    
    def load_data(self) -> None:
        """Load dataset data."""
        raise NotImplementedError
    
    def get_split(self, split_name: str = "train") -> DatasetSplit:
        """Get a specific dataset split."""
        if split_name not in self.splits:
            raise ValueError(f"Split '{split_name}' not found. Available splits: {list(self.splits.keys())}")
        return self.splits[split_name]
    
    def create_ood_split(
        self, 
        split_name: str = "test",
        ood_ratio: float = 0.3,
        ood_generator: Optional[Callable] = None
    ) -> DatasetSplit:
        """Create an OOD split from existing data."""
        split = self.get_split(split_name)
        
        n_samples = len(split.test_data)
        n_ood = int(n_samples * ood_ratio)
        n_id = n_samples - n_ood
        
        # Randomly select ID and OOD samples
        indices = np.random.permutation(n_samples)
        id_indices = indices[:n_id]
        ood_indices = indices[n_id:]
        
        # Create OOD data
        if ood_generator is not None:
            ood_data = ood_generator(split.test_data[ood_indices])
        else:
            # Default: add noise to create OOD samples
            ood_data = split.test_data[ood_indices] + np.random.normal(0, 0.5, split.test_data[ood_indices].shape)
        
        # Combine ID and OOD data
        combined_data = np.vstack([split.test_data[id_indices], ood_data])
        combined_labels = np.hstack([split.test_labels[id_indices], np.ones(n_ood)])  # 1 for OOD
        
        return DatasetSplit(
            train_data=split.train_data,
            train_labels=split.train_labels,
            test_data=combined_data,
            test_labels=combined_labels,
            metadata={"ood_ratio": ood_ratio, "n_ood": n_ood, "n_id": n_id}
        )


class SyntheticOODDataset(BenchmarkDataset):
    """Synthetic dataset for OOD detection benchmarking."""
    
    def __init__(
        self,
        n_samples: int = 10000,
        n_features: int = 10,
        n_classes: int = 2,
        noise_level: float = 0.1,
        complexity: str = "medium"
    ):
        super().__init__(
            name="synthetic_ood",
            dataset_type=DatasetType.SYNTHETIC,
            description="Synthetic dataset for OOD detection evaluation"
        )
        self.n_samples = n_samples
        self.n_features = n_features
        self.n_classes = n_classes
        self.noise_level = noise_level
        self.complexity = complexity
    
    def load_data(self) -> None:
        """Generate synthetic data."""
        # Generate training data
        train_data, train_labels = self._generate_data(
            n_samples=self.n_samples // 2,
            data_type="in_distribution"
        )
        
        # Generate test data (mix of ID and OOD)
        test_id_data, test_id_labels = self._generate_data(
            n_samples=self.n_samples // 4,
            data_type="in_distribution"
        )
        
        test_ood_data, test_ood_labels = self._generate_data(
            n_samples=self.n_samples // 4,
            data_type="out_of_distribution"
        )
        
        # Combine test data
        test_data = np.vstack([test_id_data, test_ood_data])
        test_labels = np.hstack([test_id_labels, test_ood_labels])
        
        # Create OOD labels (1 for OOD, 0 for ID)
        ood_labels = np.hstack([np.zeros(len(test_id_labels)), np.ones(len(test_ood_labels))])
        
        # Create splits
        self.splits["train"] = DatasetSplit(
            train_data=train_data,
            train_labels=train_labels,
            test_data=test_data,
            test_labels=ood_labels,
            metadata={
                "n_features": self.n_features,
                "n_classes": self.n_classes,
                "noise_level": self.noise_level,
                "complexity": self.complexity
            }
        )
    
    def _generate_data(self, n_samples: int, data_type: str = "in_distribution") -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic data samples."""
        if self.complexity == "simple":
            # Simple linear separation
            X = np.random.randn(n_samples, self.n_features)
            if data_type == "out_of_distribution":
                X = X + np.random.normal(0, 2.0, X.shape)  # Shift distribution
            
            # Create labels based on linear combination
            weights = np.random.randn(self.n_features)
            y = (X @ weights > 0).astype(int)
            
        elif self.complexity == "medium":
            # Non-linear separation
            X = np.random.randn(n_samples, self.n_features)
            if data_type == "out_of_distribution":
                X = X + np.random.normal(0, 1.5, X.shape)
            
            # Create non-linear decision boundary
            y = (np.sum(X**2, axis=1) > np.median(np.sum(X**2, axis=1))).astype(int)
            
        else:  # complex
            # Highly non-linear separation
            X = np.random.randn(n_samples, self.n_features)
            if data_type == "out_of_distribution":
                X = X + np.random.normal(0, 1.0, X.shape)
            
            # Create complex decision boundary
            y = (np.sin(X[:, 0]) * np.cos(X[:, 1]) + np.sum(X[:, 2:]**2, axis=1) > 0).astype(int)
        
        # Add noise
        if self.noise_level > 0:
            noise_indices = np.random.choice(n_samples, size=int(n_samples * self.noise_level), replace=False)
            y[noise_indices] = 1 - y[noise_indices]
        
        return X, y


class RealWorldOODDataset(BenchmarkDataset):
    """Real-world dataset for OOD detection benchmarking."""
    
    def __init__(
        self,
        dataset_name: str = "cifar10",
        target_class: int = 0,
        ood_classes: List[int] = None
    ):
        super().__init__(
            name=f"real_world_ood_{dataset_name}",
            dataset_type=DatasetType.REAL_WORLD,
            description=f"Real-world OOD detection on {dataset_name}"
        )
        self.dataset_name = dataset_name
        self.target_class = target_class
        self.ood_classes = ood_classes or [1, 2, 3, 4, 5]
    
    def load_data(self) -> None:
        """Load real-world dataset."""
        if self.dataset_name == "cifar10":
            self._load_cifar10()
        elif self.dataset_name == "mnist":
            self._load_mnist()
        else:
            raise ValueError(f"Unsupported dataset: {self.dataset_name}")
    
    def _load_cifar10(self) -> None:
        """Load CIFAR-10 dataset."""
        try:
            import torchvision
            import torchvision.transforms as transforms
            
            # Define transforms
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ])
            
            # Load dataset
            trainset = torchvision.datasets.CIFAR10(
                root='./data', train=True, download=True, transform=transform
            )
            testset = torchvision.datasets.CIFAR10(
                root='./data', train=False, download=True, transform=transform
            )
            
            # Extract data and labels
            train_data = []
            train_labels = []
            for data, label in trainset:
                if label == self.target_class:
                    train_data.append(data.numpy().flatten())
                    train_labels.append(0)  # In-distribution
            
            test_data = []
            test_labels = []
            for data, label in testset:
                if label == self.target_class:
                    test_data.append(data.numpy().flatten())
                    test_labels.append(0)  # In-distribution
                elif label in self.ood_classes:
                    test_data.append(data.numpy().flatten())
                    test_labels.append(1)  # Out-of-distribution
            
            # Convert to numpy arrays
            train_data = np.array(train_data)
            train_labels = np.array(train_labels)
            test_data = np.array(test_data)
            test_labels = np.array(test_labels)
            
            # Create split
            self.splits["train"] = DatasetSplit(
                train_data=train_data,
                train_labels=train_labels,
                test_data=test_data,
                test_labels=test_labels,
                metadata={
                    "dataset": "cifar10",
                    "target_class": self.target_class,
                    "ood_classes": self.ood_classes
                }
            )
            
        except ImportError:
            # Fallback: create synthetic data with similar characteristics
            print("torchvision not available, using synthetic CIFAR-10-like data")
            self._create_synthetic_cifar10()
    
    def _load_mnist(self) -> None:
        """Load MNIST dataset."""
        try:
            import torchvision
            import torchvision.transforms as transforms
            
            # Define transforms
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,))
            ])
            
            # Load dataset
            trainset = torchvision.datasets.MNIST(
                root='./data', train=True, download=True, transform=transform
            )
            testset = torchvision.datasets.MNIST(
                root='./data', train=False, download=True, transform=transform
            )
            
            # Extract data and labels
            train_data = []
            train_labels = []
            for data, label in trainset:
                if label == self.target_class:
                    train_data.append(data.numpy().flatten())
                    train_labels.append(0)  # In-distribution
            
            test_data = []
            test_labels = []
            for data, label in testset:
                if label == self.target_class:
                    test_data.append(data.numpy().flatten())
                    test_labels.append(0)  # In-distribution
                elif label in self.ood_classes:
                    test_data.append(data.numpy().flatten())
                    test_labels.append(1)  # Out-of-distribution
            
            # Convert to numpy arrays
            train_data = np.array(train_data)
            train_labels = np.array(train_labels)
            test_data = np.array(test_data)
            test_labels = np.array(test_labels)
            
            # Create split
            self.splits["train"] = DatasetSplit(
                train_data=train_data,
                train_labels=train_labels,
                test_data=test_data,
                test_labels=test_labels,
                metadata={
                    "dataset": "mnist",
                    "target_class": self.target_class,
                    "ood_classes": self.ood_classes
                }
            )
            
        except ImportError:
            # Fallback: create synthetic data with similar characteristics
            print("torchvision not available, using synthetic MNIST-like data")
            self._create_synthetic_mnist()
    
    def _create_synthetic_cifar10(self) -> None:
        """Create synthetic CIFAR-10-like data."""
        # Generate synthetic image-like data (32x32x3 = 3072 features)
        n_features = 3072
        
        # Training data (in-distribution)
        train_data = np.random.randn(1000, n_features)
        train_labels = np.zeros(1000)
        
        # Test data (mix of ID and OOD)
        test_id_data = np.random.randn(500, n_features)
        test_id_labels = np.zeros(500)
        
        test_ood_data = np.random.randn(500, n_features) + 2.0  # Shifted distribution
        test_ood_labels = np.ones(500)
        
        # Combine test data
        test_data = np.vstack([test_id_data, test_ood_data])
        test_labels = np.hstack([test_id_labels, test_ood_labels])
        
        # Create split
        self.splits["train"] = DatasetSplit(
            train_data=train_data,
            train_labels=train_labels,
            test_data=test_data,
            test_labels=test_labels,
            metadata={
                "dataset": "synthetic_cifar10",
                "target_class": self.target_class,
                "ood_classes": self.ood_classes
            }
        )
    
    def _create_synthetic_mnist(self) -> None:
        """Create synthetic MNIST-like data."""
        # Generate synthetic image-like data (28x28 = 784 features)
        n_features = 784
        
        # Training data (in-distribution)
        train_data = np.random.randn(1000, n_features)
        train_labels = np.zeros(1000)
        
        # Test data (mix of ID and OOD)
        test_id_data = np.random.randn(500, n_features)
        test_id_labels = np.zeros(500)
        
        test_ood_data = np.random.randn(500, n_features) + 1.5  # Shifted distribution
        test_ood_labels = np.ones(500)
        
        # Combine test data
        test_data = np.vstack([test_id_data, test_ood_data])
        test_labels = np.hstack([test_id_labels, test_ood_labels])
        
        # Create split
        self.splits["train"] = DatasetSplit(
            train_data=train_data,
            train_labels=train_labels,
            test_data=test_data,
            test_labels=test_labels,
            metadata={
                "dataset": "synthetic_mnist",
                "target_class": self.target_class,
                "ood_classes": self.ood_classes
            }
        )


class AnomalyDetectionDataset(BenchmarkDataset):
    """Dataset for anomaly detection benchmarking."""
    
    def __init__(
        self,
        dataset_name: str = "synthetic",
        n_samples: int = 10000,
        anomaly_ratio: float = 0.1,
        n_features: int = 10
    ):
        super().__init__(
            name=f"anomaly_detection_{dataset_name}",
            dataset_type=DatasetType.TABULAR,
            description=f"Anomaly detection dataset: {dataset_name}"
        )
        self.dataset_name = dataset_name
        self.n_samples = n_samples
        self.anomaly_ratio = anomaly_ratio
        self.n_features = n_features
    
    def load_data(self) -> None:
        """Load anomaly detection dataset."""
        if self.dataset_name == "synthetic":
            self._create_synthetic_anomaly_data()
        elif self.dataset_name == "credit_card":
            self._create_credit_card_like_data()
        else:
            raise ValueError(f"Unsupported dataset: {self.dataset_name}")
    
    def _create_synthetic_anomaly_data(self) -> None:
        """Create synthetic anomaly detection data."""
        n_normal = int(self.n_samples * (1 - self.anomaly_ratio))
        n_anomaly = self.n_samples - n_normal
        
        # Generate normal data (multivariate Gaussian)
        normal_data = np.random.multivariate_normal(
            mean=np.zeros(self.n_features),
            cov=np.eye(self.n_features),
            size=n_normal
        )
        normal_labels = np.zeros(n_normal)
        
        # Generate anomaly data (different distribution)
        anomaly_data = np.random.multivariate_normal(
            mean=np.ones(self.n_features) * 3,  # Shifted mean
            cov=np.eye(self.n_features) * 2,    # Different covariance
            size=n_anomaly
        )
        anomaly_labels = np.ones(n_anomaly)
        
        # Combine data
        all_data = np.vstack([normal_data, anomaly_data])
        all_labels = np.hstack([normal_labels, anomaly_labels])
        
        # Shuffle
        indices = np.random.permutation(len(all_data))
        all_data = all_data[indices]
        all_labels = all_labels[indices]
        
        # Split into train/test
        train_size = int(0.7 * len(all_data))
        train_data = all_data[:train_size]
        train_labels = all_labels[:train_size]
        test_data = all_data[train_size:]
        test_labels = all_labels[train_size:]
        
        # Create split
        self.splits["train"] = DatasetSplit(
            train_data=train_data,
            train_labels=train_labels,
            test_data=test_data,
            test_labels=test_labels,
            metadata={
                "dataset": "synthetic_anomaly",
                "n_features": self.n_features,
                "anomaly_ratio": self.anomaly_ratio,
                "n_normal": n_normal,
                "n_anomaly": n_anomaly
            }
        )
    
    def _create_credit_card_like_data(self) -> None:
        """Create credit card fraud-like data."""
        # Simulate credit card transaction features
        n_normal = int(self.n_samples * (1 - self.anomaly_ratio))
        n_anomaly = self.n_samples - n_normal
        
        # Normal transactions (lower amounts, regular patterns)
        normal_amounts = np.random.exponential(50, n_normal)
        normal_features = np.column_stack([
            normal_amounts,
            np.random.normal(0, 1, n_normal),  # Time of day
            np.random.normal(0, 1, n_normal),  # Merchant category
            np.random.normal(0, 1, n_normal),  # Location
            np.random.normal(0, 1, n_normal),  # Previous transactions
        ])
        
        # Add more features to reach n_features
        if self.n_features > 5:
            additional_features = np.random.normal(0, 1, (n_normal, self.n_features - 5))
            normal_features = np.column_stack([normal_features, additional_features])
        
        normal_labels = np.zeros(n_normal)
        
        # Anomaly transactions (higher amounts, unusual patterns)
        anomaly_amounts = np.random.exponential(500, n_anomaly)  # Higher amounts
        anomaly_features = np.column_stack([
            anomaly_amounts,
            np.random.normal(0, 3, n_anomaly),  # Unusual time
            np.random.normal(0, 3, n_anomaly),  # Unusual merchant
            np.random.normal(0, 3, n_anomaly),  # Unusual location
            np.random.normal(0, 3, n_anomaly),  # Unusual pattern
        ])
        
        # Add more features to reach n_features
        if self.n_features > 5:
            additional_features = np.random.normal(0, 3, (n_anomaly, self.n_features - 5))
            anomaly_features = np.column_stack([anomaly_features, additional_features])
        
        anomaly_labels = np.ones(n_anomaly)
        
        # Combine data
        all_data = np.vstack([normal_features, anomaly_features])
        all_labels = np.hstack([normal_labels, anomaly_labels])
        
        # Shuffle
        indices = np.random.permutation(len(all_data))
        all_data = all_data[indices]
        all_labels = all_labels[indices]
        
        # Split into train/test
        train_size = int(0.7 * len(all_data))
        train_data = all_data[:train_size]
        train_labels = all_labels[:train_size]
        test_data = all_data[train_size:]
        test_labels = all_labels[train_size:]
        
        # Create split
        self.splits["train"] = DatasetSplit(
            train_data=train_data,
            train_labels=train_labels,
            test_data=test_data,
            test_labels=test_labels,
            metadata={
                "dataset": "credit_card_like",
                "n_features": self.n_features,
                "anomaly_ratio": self.anomaly_ratio,
                "n_normal": n_normal,
                "n_anomaly": n_anomaly
            }
        )
