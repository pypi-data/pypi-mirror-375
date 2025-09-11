"""
Multi-Modal Anomaly Detection for comprehensive OOD and anomaly identification.

This module provides multi-modal anomaly detection capabilities that can
handle different data types (tabular, image, text) in a unified framework.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import json
from abc import ABC, abstractmethod
from enum import Enum


class DataType(Enum):
    """Supported data types for anomaly detection."""
    TABULAR = "tabular"
    IMAGE = "image"
    TEXT = "text"
    TIME_SERIES = "time_series"
    MULTIMODAL = "multimodal"


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    POINT_ANOMALY = "point_anomaly"
    CONTEXTUAL_ANOMALY = "contextual_anomaly"
    COLLECTIVE_ANOMALY = "collective_anomaly"
    DRIFT_ANOMALY = "drift_anomaly"
    NOVELTY_ANOMALY = "novelty_anomaly"


class AnomalyDetector(ABC):
    """Abstract base class for anomaly detectors."""
    
    def __init__(self, data_type: DataType, detector_name: str):
        self.data_type = data_type
        self.detector_name = detector_name
        self.is_fitted = False
    
    @abstractmethod
    def fit(self, data: Union[np.ndarray, torch.Tensor, List[Any]]) -> None:
        """Fit the detector to normal data."""
        pass
    
    @abstractmethod
    def predict(self, data: Union[np.ndarray, torch.Tensor, List[Any]]) -> np.ndarray:
        """Predict anomaly scores for given data."""
        pass
    
    @abstractmethod
    def get_anomaly_score(self, data: Union[np.ndarray, torch.Tensor, List[Any]]) -> float:
        """Get anomaly score for a single sample."""
        pass


class TabularAnomalyDetector(AnomalyDetector):
    """Anomaly detector for tabular data."""
    
    def __init__(self, method: str = "isolation_forest"):
        super().__init__(DataType.TABULAR, f"tabular_{method}")
        self.method = method
        self.detector = None
        self.normal_data = None
    
    def fit(self, data: np.ndarray) -> None:
        """Fit detector to normal tabular data."""
        try:
            if self.method == "isolation_forest":
                from sklearn.ensemble import IsolationForest
                self.detector = IsolationForest(contamination=0.1, random_state=42)
            elif self.method == "one_class_svm":
                from sklearn.svm import OneClassSVM
                self.detector = OneClassSVM(nu=0.1)
            elif self.method == "local_outlier_factor":
                from sklearn.neighbors import LocalOutlierFactor
                self.detector = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
            else:
                raise ValueError(f"Unknown method: {self.method}")
            
            self.detector.fit(data)
            self.normal_data = data.copy()
            self.is_fitted = True
        except (ImportError, ValueError):
            # Fallback to simple distance-based detector
            self.detector = None
            self.normal_data = data.copy()
            self.is_fitted = True
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Predict anomaly scores for tabular data."""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before prediction")
        
        if self.detector is not None:
            if self.method == "local_outlier_factor":
                scores = -self.detector.decision_function(data)
            else:
                scores = -self.detector.decision_function(data)
        else:
            # Fallback: simple distance-based scoring
            scores = np.array([self.get_anomaly_score(sample) for sample in data])
        
        return scores
    
    def get_anomaly_score(self, data: np.ndarray) -> float:
        """Get anomaly score for a single sample."""
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        if self.detector is not None:
            return self.predict(data)[0]
        else:
            # Fallback: simple distance-based scoring
            if self.normal_data is not None:
                # Calculate distance to nearest neighbor in normal data
                # data is a single sample, so we need to broadcast it properly
                distances = np.linalg.norm(self.normal_data - data, axis=1)
                return np.min(distances)
            else:
                return 0.0


class ImageAnomalyDetector(AnomalyDetector):
    """Anomaly detector for image data."""
    
    def __init__(self, method: str = "autoencoder"):
        super().__init__(DataType.IMAGE, f"image_{method}")
        self.method = method
        self.model = None
        self.normal_data = None
        self.threshold = None
    
    def fit(self, data: torch.Tensor) -> None:
        """Fit detector to normal image data."""
        if self.method == "autoencoder":
            self._fit_autoencoder(data)
        elif self.method == "vae":
            self._fit_vae(data)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        self.normal_data = data.clone()
        self.is_fitted = True
    
    def _fit_autoencoder(self, data: torch.Tensor):
        """Fit autoencoder for image anomaly detection."""
        input_dim = data.shape[1] * data.shape[2] * data.shape[3] if len(data.shape) == 4 else data.shape[1]
        
        class AutoEncoder(nn.Module):
            def __init__(self, input_dim, hidden_dim=128):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.ReLU()
                )
                self.decoder = nn.Sequential(
                    nn.Linear(hidden_dim // 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, input_dim),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded
        
        self.model = AutoEncoder(input_dim)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        # Flatten data for training
        if len(data.shape) == 4:
            data_flat = data.view(data.shape[0], -1)
        else:
            data_flat = data
        
        # Train autoencoder
        for epoch in range(50):
            optimizer.zero_grad()
            reconstructed = self.model(data_flat)
            loss = criterion(reconstructed, data_flat)
            loss.backward()
            optimizer.step()
        
        # Set threshold based on reconstruction error
        with torch.no_grad():
            reconstructed = self.model(data_flat)
            reconstruction_errors = torch.mean((data_flat - reconstructed) ** 2, dim=1)
            self.threshold = torch.quantile(reconstruction_errors, 0.95).item()
    
    def _fit_vae(self, data: torch.Tensor):
        """Fit Variational Autoencoder for image anomaly detection."""
        # Simplified VAE implementation
        input_dim = data.shape[1] * data.shape[2] * data.shape[3] if len(data.shape) == 4 else data.shape[1]
        
        class VAE(nn.Module):
            def __init__(self, input_dim, hidden_dim=128, latent_dim=32):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.ReLU()
                )
                self.mu = nn.Linear(hidden_dim // 2, latent_dim)
                self.logvar = nn.Linear(hidden_dim // 2, latent_dim)
                self.decoder = nn.Sequential(
                    nn.Linear(latent_dim, hidden_dim // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_dim // 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, input_dim),
                    nn.Sigmoid()
                )
            
            def encode(self, x):
                h = self.encoder(x)
                return self.mu(h), self.logvar(h)
            
            def reparameterize(self, mu, logvar):
                std = torch.exp(0.5 * logvar)
                eps = torch.randn_like(std)
                return mu + eps * std
            
            def decode(self, z):
                return self.decoder(z)
            
            def forward(self, x):
                mu, logvar = self.encode(x)
                z = self.reparameterize(mu, logvar)
                return self.decode(z), mu, logvar
        
        self.model = VAE(input_dim)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        # Flatten data for training
        if len(data.shape) == 4:
            data_flat = data.view(data.shape[0], -1)
        else:
            data_flat = data
        
        # Train VAE
        for epoch in range(50):
            optimizer.zero_grad()
            reconstructed, mu, logvar = self.model(data_flat)
            
            # VAE loss
            recon_loss = nn.MSELoss()(reconstructed, data_flat)
            kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
            loss = recon_loss + 0.1 * kl_loss
            
            loss.backward()
            optimizer.step()
        
        # Set threshold based on reconstruction error
        with torch.no_grad():
            reconstructed, _, _ = self.model(data_flat)
            reconstruction_errors = torch.mean((data_flat - reconstructed) ** 2, dim=1)
            self.threshold = torch.quantile(reconstruction_errors, 0.95).item()
    
    def predict(self, data: torch.Tensor) -> np.ndarray:
        """Predict anomaly scores for image data."""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before prediction")
        
        # Flatten data
        if len(data.shape) == 4:
            data_flat = data.view(data.shape[0], -1)
        else:
            data_flat = data
        
        with torch.no_grad():
            if self.method == "autoencoder":
                reconstructed = self.model(data_flat)
                reconstruction_errors = torch.mean((data_flat - reconstructed) ** 2, dim=1)
            elif self.method == "vae":
                reconstructed, _, _ = self.model(data_flat)
                reconstruction_errors = torch.mean((data_flat - reconstructed) ** 2, dim=1)
            
            # Convert to anomaly scores (higher = more anomalous)
            scores = reconstruction_errors.numpy()
        
        return scores
    
    def get_anomaly_score(self, data: torch.Tensor) -> float:
        """Get anomaly score for a single image."""
        if len(data.shape) == 3:
            data = data.unsqueeze(0)
        return self.predict(data)[0]


class TextAnomalyDetector(AnomalyDetector):
    """Anomaly detector for text data."""
    
    def __init__(self, method: str = "embedding_distance"):
        super().__init__(DataType.TEXT, f"text_{method}")
        self.method = method
        self.detector = None
        self.normal_embeddings = None
        self.threshold = None
    
    def fit(self, data: List[str]) -> None:
        """Fit detector to normal text data."""
        if self.method == "embedding_distance":
            self._fit_embedding_distance(data)
        elif self.method == "language_model":
            self._fit_language_model(data)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        self.is_fitted = True
    
    def _fit_embedding_distance(self, data: List[str]):
        """Fit embedding-based anomaly detector."""
        # Simple embedding using word frequency (in practice, use pre-trained embeddings)
        from collections import Counter
        
        # Create vocabulary
        all_words = []
        for text in data:
            words = text.lower().split()
            all_words.extend(words)
        
        vocab = Counter(all_words)
        vocab_size = len(vocab)
        
        # Create embeddings
        embeddings = []
        for text in data:
            words = text.lower().split()
            word_counts = Counter(words)
            embedding = np.zeros(vocab_size)
            for word, count in word_counts.items():
                if word in vocab:
                    embedding[list(vocab.keys()).index(word)] = count
            embeddings.append(embedding)
        
        self.normal_embeddings = np.array(embeddings)
        
        # Compute distance threshold
        distances = []
        for i, emb1 in enumerate(self.normal_embeddings):
            for j, emb2 in enumerate(self.normal_embeddings):
                if i != j:
                    dist = np.linalg.norm(emb1 - emb2)
                    distances.append(dist)
        
        self.threshold = np.percentile(distances, 95)
    
    def _fit_language_model(self, data: List[str]):
        """Fit language model-based anomaly detector."""
        # Simplified language model using n-grams
        from collections import defaultdict
        
        ngram_counts = defaultdict(int)
        total_ngrams = 0
        
        for text in data:
            words = text.lower().split()
            for i in range(len(words) - 1):
                ngram = f"{words[i]} {words[i+1]}"
                ngram_counts[ngram] += 1
                total_ngrams += 1
        
        # Normalize counts to probabilities
        self.ngram_probs = {ngram: count / total_ngrams for ngram, count in ngram_counts.items()}
        
        # Compute perplexity threshold
        perplexities = []
        for text in data:
            perplexity = self._compute_perplexity(text)
            perplexities.append(perplexity)
        
        self.threshold = np.percentile(perplexities, 95)
    
    def _compute_perplexity(self, text: str) -> float:
        """Compute perplexity of text using n-gram model."""
        words = text.lower().split()
        log_prob = 0.0
        n_ngrams = 0
        
        for i in range(len(words) - 1):
            ngram = f"{words[i]} {words[i+1]}"
            prob = self.ngram_probs.get(ngram, 1e-6)  # Smoothing
            log_prob += np.log(prob)
            n_ngrams += 1
        
        if n_ngrams == 0:
            return float('inf')
        
        perplexity = np.exp(-log_prob / n_ngrams)
        return perplexity
    
    def predict(self, data: List[str]) -> np.ndarray:
        """Predict anomaly scores for text data."""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before prediction")
        
        scores = []
        for text in data:
            score = self.get_anomaly_score(text)
            scores.append(score)
        
        return np.array(scores)
    
    def get_anomaly_score(self, data: str) -> float:
        """Get anomaly score for a single text."""
        if self.method == "embedding_distance":
            # Create embedding for input text
            words = data.lower().split()
            word_counts = Counter(words)
            embedding = np.zeros(len(self.normal_embeddings[0]))
            
            # This is simplified - in practice, use the same vocabulary
            for word, count in word_counts.items():
                # Simple word-based scoring
                embedding[hash(word) % len(embedding)] = count
            
            # Compute minimum distance to normal embeddings
            distances = [np.linalg.norm(embedding - normal_emb) for normal_emb in self.normal_embeddings]
            min_distance = min(distances)
            
            return min_distance / self.threshold if self.threshold > 0 else min_distance
        
        elif self.method == "language_model":
            perplexity = self._compute_perplexity(data)
            return perplexity / self.threshold if self.threshold > 0 else perplexity
        
        return 0.0


class MultiModalAnomalyDetector:
    """
    Multi-Modal Anomaly Detector for comprehensive anomaly identification.
    
    This class provides unified anomaly detection across different data types
    and modalities, enabling comprehensive anomaly identification in complex systems.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Multi-Modal Anomaly Detector.
        
        Args:
            config: Configuration dictionary for detectors
        """
        self.config = config or {}
        self.detectors = {}
        self.is_fitted = False
        
        # Default detector configurations
        self.default_configs = {
            DataType.TABULAR: {"method": "isolation_forest"},
            DataType.IMAGE: {"method": "autoencoder"},
            DataType.TEXT: {"method": "embedding_distance"}
        }
    
    def add_detector(
        self,
        data_type: DataType,
        detector: Optional[AnomalyDetector] = None,
        method: Optional[str] = None
    ) -> None:
        """
        Add a detector for a specific data type.
        
        Args:
            data_type: Type of data the detector handles
            detector: Pre-configured detector (optional)
            method: Method for creating detector (optional)
        """
        if detector is not None:
            self.detectors[data_type] = detector
        else:
            method = method or self.default_configs.get(data_type, {}).get("method", "default")
            
            if data_type == DataType.TABULAR:
                self.detectors[data_type] = TabularAnomalyDetector(method)
            elif data_type == DataType.IMAGE:
                self.detectors[data_type] = ImageAnomalyDetector(method)
            elif data_type == DataType.TEXT:
                self.detectors[data_type] = TextAnomalyDetector(method)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
    
    def fit(
        self,
        data: Dict[DataType, Union[np.ndarray, torch.Tensor, List[str]]]
    ) -> None:
        """
        Fit all detectors to their respective normal data.
        
        Args:
            data: Dictionary mapping data types to their normal training data
        """
        for data_type, training_data in data.items():
            if data_type not in self.detectors:
                self.add_detector(data_type)
            
            detector = self.detectors[data_type]
            detector.fit(training_data)
        
        self.is_fitted = True
    
    def predict(
        self,
        data: Dict[DataType, Union[np.ndarray, torch.Tensor, List[str]]]
    ) -> Dict[DataType, np.ndarray]:
        """
        Predict anomaly scores for multi-modal data.
        
        Args:
            data: Dictionary mapping data types to their test data
            
        Returns:
            Dictionary mapping data types to anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before prediction")
        
        results = {}
        for data_type, test_data in data.items():
            if data_type in self.detectors:
                detector = self.detectors[data_type]
                scores = detector.predict(test_data)
                results[data_type] = scores
            else:
                raise ValueError(f"No detector available for data type: {data_type}")
        
        return results
    
    def get_combined_anomaly_score(
        self,
        data: Dict[DataType, Union[np.ndarray, torch.Tensor, List[str]]],
        weights: Optional[Dict[DataType, float]] = None
    ) -> float:
        """
        Get combined anomaly score across all modalities.
        
        Args:
            data: Dictionary mapping data types to their test data
            weights: Optional weights for different modalities
            
        Returns:
            Combined anomaly score
        """
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before prediction")
        
        if weights is None:
            weights = {data_type: 1.0 for data_type in data.keys()}
        
        total_score = 0.0
        total_weight = 0.0
        
        for data_type, test_data in data.items():
            if data_type in self.detectors:
                detector = self.detectors[data_type]
                # For batch data, we need to get the average score
                if isinstance(test_data, np.ndarray) and test_data.ndim > 1:
                    scores = detector.predict(test_data)
                    score = np.mean(scores)
                else:
                    score = detector.get_anomaly_score(test_data)
                weight = weights.get(data_type, 1.0)
                
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def detect_anomalies(
        self,
        data: Dict[DataType, Union[np.ndarray, torch.Tensor, List[str]]],
        threshold: float = 0.5,
        weights: Optional[Dict[DataType, float]] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies in multi-modal data.
        
        Args:
            data: Dictionary mapping data types to their test data
            threshold: Anomaly detection threshold
            weights: Optional weights for different modalities
            
        Returns:
            Dictionary with anomaly detection results
        """
        # Get individual scores
        individual_scores = self.predict(data)
        
        # Get combined score
        combined_score = self.get_combined_anomaly_score(data, weights)
        
        # Determine if anomalous
        is_anomalous = combined_score > threshold
        
        # Get anomaly type
        anomaly_type = self._classify_anomaly_type(individual_scores, combined_score)
        
        return {
            'is_anomalous': is_anomalous,
            'combined_score': combined_score,
            'individual_scores': individual_scores,
            'anomaly_type': anomaly_type,
            'threshold': threshold,
            'confidence': min(combined_score / threshold, 1.0) if threshold > 0 else 0.0
        }
    
    def _classify_anomaly_type(
        self,
        individual_scores: Dict[DataType, np.ndarray],
        combined_score: float
    ) -> AnomalyType:
        """Classify the type of anomaly based on scores."""
        # Simple classification logic
        if combined_score > 2.0:
            return AnomalyType.POINT_ANOMALY
        elif len(individual_scores) > 1 and max(individual_scores.values()) > 1.5:
            return AnomalyType.CONTEXTUAL_ANOMALY
        else:
            return AnomalyType.DRIFT_ANOMALY
    
    def get_detector_statistics(self) -> Dict[str, Any]:
        """Get statistics about all detectors."""
        stats = {
            'total_detectors': len(self.detectors),
            'fitted_detectors': sum(1 for d in self.detectors.values() if d.is_fitted),
            'data_types': [dt.value for dt in self.detectors.keys()],
            'detector_details': {}
        }
        
        for data_type, detector in self.detectors.items():
            stats['detector_details'][data_type.value] = {
                'name': detector.detector_name,
                'is_fitted': detector.is_fitted,
                'method': getattr(detector, 'method', 'unknown')
            }
        
        return stats
    
    def save_detector(self, filepath: str):
        """Save detector state to file."""
        state = {
            'config': self.config,
            'default_configs': self.default_configs,
            'is_fitted': self.is_fitted,
            'detectors': {}
        }
        
        # Save detector states (simplified - in practice, save model weights)
        for data_type, detector in self.detectors.items():
            state['detectors'][data_type.value] = {
                'detector_name': detector.detector_name,
                'is_fitted': detector.is_fitted,
                'method': getattr(detector, 'method', 'unknown')
            }
        
        torch.save(state, filepath)
    
    def load_detector(self, filepath: str):
        """Load detector state from file."""
        state = torch.load(filepath)
        self.config = state['config']
        self.default_configs = state['default_configs']
        self.is_fitted = state['is_fitted']
        
        # Recreate detectors (simplified - in practice, load model weights)
        for data_type_str, detector_info in state['detectors'].items():
            data_type = DataType(data_type_str)
            method = detector_info['method']
            self.add_detector(data_type, method=method)
