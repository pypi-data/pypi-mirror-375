"""
Explainable Anomaly Detection for providing insights into anomaly causes.

This module provides explainable AI capabilities for anomaly detection,
helping users understand why data points are considered anomalous.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
# matplotlib will be imported conditionally in methods that need it


class ExplanationType(Enum):
    """Types of explanations for anomalies."""
    FEATURE_IMPORTANCE = "feature_importance"
    ATTRIBUTION = "attribution"
    COUNTERFACTUAL = "counterfactual"
    SIMILARITY = "similarity"
    CONTEXTUAL = "contextual"


@dataclass
class AnomalyExplanation:
    """Data structure for anomaly explanations."""
    explanation_type: ExplanationType
    anomaly_score: float
    confidence: float
    explanation_data: Dict[str, Any]
    visualization_data: Optional[Dict[str, Any]] = None
    text_description: Optional[str] = None


class ExplainableAnomalyDetector:
    """
    Explainable Anomaly Detector for providing insights into anomaly causes.
    
    This class provides explainable AI capabilities for understanding
    why data points are considered anomalous.
    """
    
    def __init__(
        self,
        anomaly_detector: Any,
        explanation_methods: Optional[List[ExplanationType]] = None
    ):
        """
        Initialize Explainable Anomaly Detector.
        
        Args:
            anomaly_detector: Base anomaly detector
            explanation_methods: List of explanation methods to use
        """
        self.anomaly_detector = anomaly_detector
        self.explanation_methods = explanation_methods or [
            ExplanationType.FEATURE_IMPORTANCE,
            ExplanationType.ATTRIBUTION,
            ExplanationType.SIMILARITY
        ]
        
        # Explanation cache
        self.explanation_cache = {}
        
        # Reference data for explanations
        self.normal_reference_data = None
        self.anomaly_reference_data = None
    
    def set_reference_data(
        self,
        normal_data: Union[np.ndarray, torch.Tensor, List[Any]],
        anomaly_data: Optional[Union[np.ndarray, torch.Tensor, List[Any]]] = None
    ):
        """Set reference data for explanations."""
        self.normal_reference_data = normal_data
        self.anomaly_reference_data = anomaly_data
    
    def explain_anomaly(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]],
        explanation_types: Optional[List[ExplanationType]] = None
    ) -> List[AnomalyExplanation]:
        """
        Generate explanations for an anomalous data point.
        
        Args:
            data: Data point to explain
            explanation_types: Types of explanations to generate
            
        Returns:
            List of anomaly explanations
        """
        if explanation_types is None:
            explanation_types = self.explanation_methods
        
        explanations = []
        
        for explanation_type in explanation_types:
            try:
                explanation = self._generate_explanation(data, explanation_type)
                explanations.append(explanation)
            except Exception as e:
                print(f"Error generating {explanation_type.value} explanation: {e}")
        
        return explanations
    
    def _generate_explanation(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]],
        explanation_type: ExplanationType
    ) -> AnomalyExplanation:
        """Generate a specific type of explanation."""
        if explanation_type == ExplanationType.FEATURE_IMPORTANCE:
            return self._explain_feature_importance(data)
        elif explanation_type == ExplanationType.ATTRIBUTION:
            return self._explain_attribution(data)
        elif explanation_type == ExplanationType.COUNTERFACTUAL:
            return self._explain_counterfactual(data)
        elif explanation_type == ExplanationType.SIMILARITY:
            return self._explain_similarity(data)
        elif explanation_type == ExplanationType.CONTEXTUAL:
            return self._explain_contextual(data)
        else:
            raise ValueError(f"Unknown explanation type: {explanation_type}")
    
    def _explain_feature_importance(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]]
    ) -> AnomalyExplanation:
        """Explain anomaly using feature importance."""
        # Get base anomaly score
        if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
            if isinstance(data, dict):
                base_score = self.anomaly_detector.get_combined_anomaly_score(data)
            else:
                data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                base_score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
        else:
            base_score = self.anomaly_detector.get_anomaly_score(data)
        
        # Convert to numpy if needed
        if isinstance(data, torch.Tensor):
            data_np = data.detach().numpy()
        elif isinstance(data, dict):
            # For multi-modal data, use the first modality
            first_key = list(data.keys())[0]
            first_data = data[first_key]
            data_np = first_data.detach().numpy() if isinstance(first_data, torch.Tensor) else first_data
        else:
            data_np = data
        
        # Flatten data for feature analysis
        if data_np.ndim > 1:
            data_flat = data_np.flatten()
        else:
            data_flat = data_np
        
        # Compute feature importance using perturbation
        feature_importance = []
        for i in range(len(data_flat)):
            # Create perturbed data
            perturbed_data = data_flat.copy()
            perturbed_data[i] = 0  # Set feature to zero
            
            # Reshape back to original shape
            if data_np.ndim > 1:
                perturbed_data = perturbed_data.reshape(data_np.shape)
            
            # Get anomaly score for perturbed data
            if isinstance(data, torch.Tensor):
                perturbed_tensor = torch.tensor(perturbed_data)
                if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                    perturbed_dict = {list(self.anomaly_detector.detectors.keys())[0]: perturbed_tensor}
                    perturbed_score = self.anomaly_detector.get_combined_anomaly_score(perturbed_dict)
                else:
                    perturbed_score = self.anomaly_detector.get_anomaly_score(perturbed_tensor)
            else:
                if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                    perturbed_dict = {list(self.anomaly_detector.detectors.keys())[0]: perturbed_data}
                    perturbed_score = self.anomaly_detector.get_combined_anomaly_score(perturbed_dict)
                else:
                    perturbed_score = self.anomaly_detector.get_anomaly_score(perturbed_data)
            
            # Feature importance is the change in anomaly score
            importance = abs(base_score - perturbed_score)
            feature_importance.append(importance)
        
        # Normalize importance scores
        feature_importance = np.array(feature_importance)
        if feature_importance.sum() > 0:
            feature_importance = feature_importance / feature_importance.sum()
        
        # Get top contributing features
        top_features = np.argsort(feature_importance)[-5:][::-1]
        
        explanation_data = {
            'feature_importance': feature_importance.tolist(),
            'top_features': top_features.tolist(),
            'top_importance_scores': feature_importance[top_features].tolist(),
            'base_anomaly_score': base_score
        }
        
        # Generate text description
        text_description = f"Top contributing features: {top_features[:3].tolist()}"
        
        return AnomalyExplanation(
            explanation_type=ExplanationType.FEATURE_IMPORTANCE,
            anomaly_score=base_score,
            confidence=0.8,  # Placeholder confidence
            explanation_data=explanation_data,
            text_description=text_description
        )
    
    def _explain_attribution(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]]
    ) -> AnomalyExplanation:
        """Explain anomaly using attribution methods."""
        # Simplified attribution using gradient-based methods
        if isinstance(data, torch.Tensor) and data.requires_grad:
            # Compute gradients
            data.requires_grad_(True)
            
            if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
            else:
                score = self.anomaly_detector.get_anomaly_score(data)
            
            # Compute gradients
            gradients = torch.autograd.grad(score, data, retain_graph=True)[0]
            attribution = gradients.abs()
            
            explanation_data = {
                'attribution_scores': attribution.detach().numpy().tolist(),
                'gradient_norm': gradients.norm().item(),
                'anomaly_score': score.item()
            }
            
            text_description = f"Attribution analysis shows gradient norm: {gradients.norm().item():.4f}"
            
        else:
            # Fallback to feature importance
            feature_explanation = self._explain_feature_importance(data)
            explanation_data = feature_explanation.explanation_data
            text_description = "Attribution analysis (using feature importance as fallback)"
        
        return AnomalyExplanation(
            explanation_type=ExplanationType.ATTRIBUTION,
            anomaly_score=explanation_data.get('anomaly_score', 0.0),
            confidence=0.7,
            explanation_data=explanation_data,
            text_description=text_description
        )
    
    def _explain_counterfactual(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]]
    ) -> AnomalyExplanation:
        """Explain anomaly using counterfactual examples."""
        # Get base anomaly score
        if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
            if isinstance(data, dict):
                base_score = self.anomaly_detector.get_combined_anomaly_score(data)
            else:
                data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                base_score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
        else:
            base_score = self.anomaly_detector.get_anomaly_score(data)
        
        # Convert to numpy for manipulation
        if isinstance(data, torch.Tensor):
            data_np = data.detach().numpy()
        elif isinstance(data, dict):
            first_key = list(data.keys())[0]
            first_data = data[first_key]
            data_np = first_data.detach().numpy() if isinstance(first_data, torch.Tensor) else first_data
        else:
            data_np = data
        
        # Generate counterfactual by moving towards normal reference
        if self.normal_reference_data is not None:
            if isinstance(self.normal_reference_data, torch.Tensor):
                normal_np = self.normal_reference_data.detach().numpy()
            else:
                normal_np = self.normal_reference_data
            
            # Simple counterfactual: interpolate towards normal data
            alpha = 0.5  # Interpolation factor
            counterfactual = (1 - alpha) * data_np + alpha * normal_np
            
            # Get anomaly score for counterfactual
            if isinstance(data, torch.Tensor):
                counterfactual_tensor = torch.tensor(counterfactual)
                if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                    counterfactual_dict = {list(self.anomaly_detector.detectors.keys())[0]: counterfactual_tensor}
                    counterfactual_score = self.anomaly_detector.get_combined_anomaly_score(counterfactual_dict)
                else:
                    counterfactual_score = self.anomaly_detector.get_anomaly_score(counterfactual_tensor)
            else:
                if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                    counterfactual_dict = {list(self.anomaly_detector.detectors.keys())[0]: counterfactual}
                    counterfactual_score = self.anomaly_detector.get_combined_anomaly_score(counterfactual_dict)
                else:
                    counterfactual_score = self.anomaly_detector.get_anomaly_score(counterfactual)
            
            explanation_data = {
                'original_score': base_score,
                'counterfactual_score': counterfactual_score,
                'improvement': base_score - counterfactual_score,
                'interpolation_factor': alpha,
                'counterfactual_data': counterfactual.tolist()
            }
            
            text_description = f"Counterfactual analysis shows {base_score - counterfactual_score:.4f} improvement"
            
        else:
            explanation_data = {
                'original_score': base_score,
                'message': 'No reference data available for counterfactual analysis'
            }
            text_description = "Counterfactual analysis not available (no reference data)"
        
        return AnomalyExplanation(
            explanation_type=ExplanationType.COUNTERFACTUAL,
            anomaly_score=base_score,
            confidence=0.6,
            explanation_data=explanation_data,
            text_description=text_description
        )
    
    def _explain_similarity(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]]
    ) -> AnomalyExplanation:
        """Explain anomaly using similarity to reference data."""
        # Get base anomaly score
        if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
            if isinstance(data, dict):
                base_score = self.anomaly_detector.get_combined_anomaly_score(data)
            else:
                data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                base_score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
        else:
            base_score = self.anomaly_detector.get_anomaly_score(data)
        
        # Convert to numpy for similarity computation
        if isinstance(data, torch.Tensor):
            data_np = data.detach().numpy()
        elif isinstance(data, dict):
            first_key = list(data.keys())[0]
            first_data = data[first_key]
            data_np = first_data.detach().numpy() if isinstance(first_data, torch.Tensor) else first_data
        else:
            data_np = data
        
        similarities = {}
        
        # Compute similarity to normal data
        if self.normal_reference_data is not None:
            if isinstance(self.normal_reference_data, torch.Tensor):
                normal_np = self.normal_reference_data.detach().numpy()
            else:
                normal_np = self.normal_reference_data
            
            # Flatten for similarity computation
            data_flat = data_np.flatten()
            normal_flat = normal_np.flatten()
            
            # Ensure same length
            min_len = min(len(data_flat), len(normal_flat))
            data_flat = data_flat[:min_len]
            normal_flat = normal_flat[:min_len]
            
            # Compute cosine similarity
            cosine_sim = np.dot(data_flat, normal_flat) / (np.linalg.norm(data_flat) * np.linalg.norm(normal_flat))
            similarities['normal_similarity'] = cosine_sim
        
        # Compute similarity to anomaly data
        if self.anomaly_reference_data is not None:
            if isinstance(self.anomaly_reference_data, torch.Tensor):
                anomaly_np = self.anomaly_reference_data.detach().numpy()
            else:
                anomaly_np = self.anomaly_reference_data
            
            # Flatten for similarity computation
            data_flat = data_np.flatten()
            anomaly_flat = anomaly_np.flatten()
            
            # Ensure same length
            min_len = min(len(data_flat), len(anomaly_flat))
            data_flat = data_flat[:min_len]
            anomaly_flat = anomaly_flat[:min_len]
            
            # Compute cosine similarity
            cosine_sim = np.dot(data_flat, anomaly_flat) / (np.linalg.norm(data_flat) * np.linalg.norm(anomaly_flat))
            similarities['anomaly_similarity'] = cosine_sim
        
        explanation_data = {
            'similarities': similarities,
            'anomaly_score': base_score,
            'data_shape': data_np.shape
        }
        
        # Generate text description
        if similarities:
            text_description = f"Similarity analysis: {similarities}"
        else:
            text_description = "Similarity analysis not available (no reference data)"
        
        return AnomalyExplanation(
            explanation_type=ExplanationType.SIMILARITY,
            anomaly_score=base_score,
            confidence=0.7,
            explanation_data=explanation_data,
            text_description=text_description
        )
    
    def _explain_contextual(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]]
    ) -> AnomalyExplanation:
        """Explain anomaly using contextual information."""
        # Get base anomaly score
        if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
            if isinstance(data, dict):
                base_score = self.anomaly_detector.get_combined_anomaly_score(data)
            else:
                data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                base_score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
        else:
            base_score = self.anomaly_detector.get_anomaly_score(data)
        
        # Contextual analysis based on data characteristics
        if isinstance(data, torch.Tensor):
            data_np = data.detach().numpy()
        elif isinstance(data, dict):
            first_key = list(data.keys())[0]
            first_data = data[first_key]
            data_np = first_data.detach().numpy() if isinstance(first_data, torch.Tensor) else first_data
        else:
            data_np = data
        
        # Compute contextual features
        contextual_features = {
            'data_range': (data_np.min(), data_np.max()),
            'data_mean': data_np.mean(),
            'data_std': data_np.std(),
            'data_shape': data_np.shape,
            'has_negative_values': (data_np < 0).any(),
            'has_zero_values': (data_np == 0).any()
        }
        
        # Generate contextual insights
        insights = []
        if contextual_features['data_std'] > 1.0:
            insights.append("High variance in data values")
        if contextual_features['has_negative_values']:
            insights.append("Contains negative values")
        if contextual_features['data_range'][1] - contextual_features['data_range'][0] > 10:
            insights.append("Wide range of values")
        
        explanation_data = {
            'contextual_features': contextual_features,
            'insights': insights,
            'anomaly_score': base_score
        }
        
        text_description = f"Contextual analysis: {'; '.join(insights) if insights else 'No specific insights'}"
        
        return AnomalyExplanation(
            explanation_type=ExplanationType.CONTEXTUAL,
            anomaly_score=base_score,
            confidence=0.5,
            explanation_data=explanation_data,
            text_description=text_description
        )
    
    def generate_explanation_report(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]],
        include_visualizations: bool = True
    ) -> Dict[str, Any]:
        """Generate a comprehensive explanation report."""
        explanations = self.explain_anomaly(data)
        
        report = {
            'data_info': {
                'shape': data.shape if hasattr(data, 'shape') else 'unknown',
                'type': type(data).__name__
            },
            'explanations': []
        }
        
        for explanation in explanations:
            explanation_dict = {
                'type': explanation.explanation_type.value,
                'anomaly_score': explanation.anomaly_score,
                'confidence': explanation.confidence,
                'description': explanation.text_description,
                'data': explanation.explanation_data
            }
            
            if include_visualizations and explanation.visualization_data:
                explanation_dict['visualization'] = explanation.visualization_data
            
            report['explanations'].append(explanation_dict)
        
        return report
    
    def get_explanation_summary(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]]
    ) -> str:
        """Get a text summary of all explanations."""
        explanations = self.explain_anomaly(data)
        
        summary_parts = []
        for explanation in explanations:
            summary_parts.append(f"{explanation.explanation_type.value}: {explanation.text_description}")
        
        return "\n".join(summary_parts)
