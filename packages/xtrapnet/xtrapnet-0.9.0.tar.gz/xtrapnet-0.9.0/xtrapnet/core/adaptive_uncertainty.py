"""
Adaptive Uncertainty Quantification for Neural Networks

This module implements a novel approach to uncertainty quantification that adapts
the uncertainty estimation based on the local data density and model confidence.
The key innovation is the Adaptive Uncertainty Decomposition (AUD) method that
dynamically balances epistemic and aleatoric uncertainty based on the input's
position in the feature space.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import math


@dataclass
class UncertaintyComponents:
    """Components of predictive uncertainty."""
    epistemic: torch.Tensor
    aleatoric: torch.Tensor
    total: torch.Tensor
    confidence: torch.Tensor


class AdaptiveUncertaintyLayer(nn.Module):
    """
    Novel adaptive uncertainty layer that dynamically adjusts uncertainty
    estimation based on local data density and model confidence.
    
    Key innovation: The uncertainty estimation adapts to the local neighborhood
    of the input, providing more accurate uncertainty bounds for both
    in-distribution and out-of-distribution samples.
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dim: int = 64,
        num_components: int = 3,
        temperature: float = 1.0,
        density_threshold: float = 0.1
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
        self.num_components = num_components
        self.temperature = temperature
        self.density_threshold = density_threshold
        
        # Main prediction network
        self.predictor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Uncertainty estimation networks
        self.epistemic_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Softplus()
        )
        
        self.aleatoric_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Softplus()
        )
        
        # Adaptive weighting network
        self.adaptive_weight = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2),  # [epistemic_weight, aleatoric_weight]
            nn.Softmax(dim=-1)
        )
        
        # Density estimation network
        self.density_estimator = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(
        self,
        x: torch.Tensor,
        return_components: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, UncertaintyComponents]]:
        """
        Forward pass with adaptive uncertainty estimation.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            return_components: Whether to return uncertainty components
            
        Returns:
            Either predictions or (predictions, uncertainty_components)
        """
        # Get predictions
        predictions = self.predictor(x)
        
        # Estimate local data density
        density = self.density_estimator(x)
        
        # Get base uncertainty estimates
        epistemic_base = self.epistemic_net(x)
        aleatoric_base = self.aleatoric_net(x)
        
        # Compute adaptive weights based on density and confidence
        adaptive_weights = self.adaptive_weight(x)
        epistemic_weight = adaptive_weights[:, 0:1]
        aleatoric_weight = adaptive_weights[:, 1:2]
        
        # Apply density-based scaling
        density_scale = torch.where(
            density < self.density_threshold,
            torch.exp(-self.temperature * (self.density_threshold - density)),
            torch.ones_like(density)
        )
        
        # Compute final uncertainty components
        epistemic = epistemic_base * epistemic_weight * density_scale
        aleatoric = aleatoric_base * aleatoric_weight
        
        # Total uncertainty
        total = epistemic + aleatoric
        
        # Confidence score (inverse of total uncertainty)
        confidence = 1.0 / (1.0 + total)
        
        if return_components:
            components = UncertaintyComponents(
                epistemic=epistemic,
                aleatoric=aleatoric,
                total=total,
                confidence=confidence
            )
            return predictions, components
        
        return predictions
    
    def compute_uncertainty_loss(
        self,
        x: torch.Tensor,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        components: UncertaintyComponents,
        beta: float = 0.5
    ) -> torch.Tensor:
        """
        Compute the adaptive uncertainty loss.
        
        This loss function balances prediction accuracy with uncertainty
        calibration, adapting the weighting based on the local data density.
        """
        # Prediction loss
        pred_loss = F.mse_loss(predictions, targets, reduction='none')
        
        # Uncertainty calibration loss
        # For high-density regions, focus on aleatoric uncertainty
        # For low-density regions, focus on epistemic uncertainty
        # Use input features for density estimation
        density = self.density_estimator(x)
        
        epistemic_loss = torch.mean(components.epistemic * (1 - density))
        aleatoric_loss = torch.mean(components.aleatoric * density)
        
        # Combined loss
        total_loss = torch.mean(pred_loss) + beta * (epistemic_loss + aleatoric_loss)
        
        return total_loss


class HierarchicalUncertaintyNetwork(nn.Module):
    """
    Hierarchical uncertainty network that models uncertainty at multiple scales.
    
    This is a novel architecture that captures uncertainty at different levels
    of abstraction, from local feature-level uncertainty to global model uncertainty.
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        num_levels: int = 3,
        hidden_dims: List[int] = [128, 64, 32]
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_levels = num_levels
        self.hidden_dims = hidden_dims
        
        # Hierarchical feature extractors
        self.feature_extractors = nn.ModuleList()
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            self.feature_extractors.append(
                nn.Sequential(
                    nn.Linear(prev_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1)
                )
            )
            prev_dim = hidden_dim
        
        # Uncertainty layers for each level
        self.uncertainty_layers = nn.ModuleList()
        for i, hidden_dim in enumerate(hidden_dims):
            self.uncertainty_layers.append(
                AdaptiveUncertaintyLayer(
                    input_dim=hidden_dim,
                    output_dim=output_dim,
                    hidden_dim=hidden_dim // 2
                )
            )
        
        # Final fusion layer
        self.fusion_layer = nn.Linear(
            output_dim * num_levels,
            output_dim
        )
        
        # Uncertainty fusion
        self.uncertainty_fusion = nn.Linear(
            output_dim * num_levels,
            output_dim
        )
    
    def forward(
        self,
        x: torch.Tensor,
        return_uncertainty: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass through hierarchical uncertainty network.
        
        Args:
            x: Input tensor
            return_uncertainty: Whether to return uncertainty estimates
            
        Returns:
            Predictions and optionally uncertainty estimates
        """
        # Extract features at multiple levels
        features = [x]
        for extractor in self.feature_extractors:
            features.append(extractor(features[-1]))
        
        # Get predictions and uncertainties at each level
        level_predictions = []
        level_uncertainties = []
        
        for i, (feature, uncertainty_layer) in enumerate(
            zip(features[1:], self.uncertainty_layers)
        ):
            if return_uncertainty:
                pred, components = uncertainty_layer(feature, return_components=True)
                level_predictions.append(pred)
                level_uncertainties.append(components.total)
            else:
                pred = uncertainty_layer(feature)
                level_predictions.append(pred)
        
        # Fuse predictions
        fused_features = torch.cat(level_predictions, dim=-1)
        final_prediction = self.fusion_layer(fused_features)
        
        if return_uncertainty:
            # Fuse uncertainties
            fused_uncertainties = torch.cat(level_uncertainties, dim=-1)
            final_uncertainty = self.uncertainty_fusion(fused_uncertainties)
            return final_prediction, final_uncertainty
        
        return final_prediction
    
    def compute_hierarchical_loss(
        self,
        x: torch.Tensor,
        targets: torch.Tensor,
        level_weights: Optional[List[float]] = None
    ) -> torch.Tensor:
        """
        Compute hierarchical loss that considers uncertainty at all levels.
        """
        if level_weights is None:
            level_weights = [1.0 / self.num_levels] * self.num_levels
        
        # Extract features
        features = [x]
        for extractor in self.feature_extractors:
            features.append(extractor(features[-1]))
        
        total_loss = 0.0
        
        for i, (feature, uncertainty_layer, weight) in enumerate(
            zip(features[1:], self.uncertainty_layers, level_weights)
        ):
            pred, components = uncertainty_layer(feature, return_components=True)
            level_loss = uncertainty_layer.compute_uncertainty_loss(
                feature, pred, targets, components
            )
            total_loss += weight * level_loss
        
        return total_loss


class DensityAwareOODDetector:
    """
    Density-aware out-of-distribution detector that uses the learned density
    estimates from the uncertainty network to detect OOD samples.
    
    This is more principled than traditional distance-based methods because
    it uses the model's own uncertainty about the data density.
    """
    
    def __init__(
        self,
        uncertainty_network: HierarchicalUncertaintyNetwork,
        density_threshold: float = 0.1,
        uncertainty_threshold: float = 0.5
    ):
        self.uncertainty_network = uncertainty_network
        self.density_threshold = density_threshold
        self.uncertainty_threshold = uncertainty_threshold
        self.training_densities = None
    
    def fit(self, training_data: torch.Tensor):
        """Fit the OOD detector on training data."""
        self.uncertainty_network.eval()
        with torch.no_grad():
            # Get density estimates for training data
            features = [training_data]
            for extractor in self.uncertainty_network.feature_extractors:
                features.append(extractor(features[-1]))
            
            # Use the density estimator from the last uncertainty layer
            last_layer = self.uncertainty_network.uncertainty_layers[-1]
            densities = last_layer.density_estimator(features[-1])
            self.training_densities = densities.cpu().numpy()
    
    def predict_ood_scores(self, test_data: torch.Tensor) -> np.ndarray:
        """Predict OOD scores for test data."""
        self.uncertainty_network.eval()
        with torch.no_grad():
            # Get density estimates
            features = [test_data]
            for extractor in self.uncertainty_network.feature_extractors:
                features.append(extractor(features[-1]))
            
            last_layer = self.uncertainty_network.uncertainty_layers[-1]
            test_densities = last_layer.density_estimator(features[-1])
            
            # Get uncertainty estimates
            _, uncertainty = self.uncertainty_network(test_data, return_uncertainty=True)
            
            # Combine density and uncertainty for OOD score
            density_scores = 1.0 - test_densities.cpu().numpy()
            uncertainty_scores = uncertainty.cpu().numpy()
            
            # Weighted combination
            ood_scores = 0.7 * density_scores + 0.3 * uncertainty_scores
            
            return ood_scores.flatten()
    
    def is_ood(self, test_data: torch.Tensor) -> np.ndarray:
        """Binary OOD classification."""
        ood_scores = self.predict_ood_scores(test_data)
        return ood_scores > self.uncertainty_threshold
