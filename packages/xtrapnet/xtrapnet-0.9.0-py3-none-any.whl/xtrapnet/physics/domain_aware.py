"""
Domain-aware extrapolation using physics-informed methods.

This module provides domain-aware extrapolation capabilities that use
physical constraints to guide predictions in out-of-distribution regions.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Callable
from .pinn import PhysicsInformedNN
from .physics_loss import PhysicsLoss


class DomainAwareExtrapolation:
    """
    Domain-aware extrapolation using physics-informed neural networks.
    
    This class provides methods to extrapolate beyond training data while
    respecting physical constraints and domain knowledge.
    """
    
    def __init__(
        self,
        model: PhysicsInformedNN,
        domain_bounds: Dict[str, Tuple[float, float]],
        physics_constraints: List[Callable],
        confidence_threshold: float = 0.1
    ):
        """
        Initialize domain-aware extrapolation.
        
        Args:
            model: Physics-informed neural network
            domain_bounds: Domain boundaries for each dimension
            physics_constraints: List of physics constraint functions
            confidence_threshold: Threshold for confidence in extrapolation
        """
        self.model = model
        self.domain_bounds = domain_bounds
        self.physics_constraints = physics_constraints
        self.confidence_threshold = confidence_threshold
        
        # Set domain bounds in the model
        self.model.set_domain_bounds(domain_bounds)
        
        # Add physics constraints to the model
        for i, constraint in enumerate(physics_constraints):
            self.model.add_physics_constraint(
                constraint, weight=1.0, name=f"constraint_{i}"
            )
    
    def extrapolate(
        self,
        x_extrapolation: torch.Tensor,
        return_confidence: bool = True
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Extrapolate beyond the training domain using physics constraints.
        
        Args:
            x_extrapolation: Points for extrapolation
            return_confidence: Whether to return confidence scores
            
        Returns:
            Predictions and optionally confidence scores
        """
        self.model.eval()
        with torch.no_grad():
            # Make predictions
            predictions = self.model.forward(x_extrapolation)
            
            if return_confidence:
                # Compute confidence based on physics violations
                confidence = self._compute_extrapolation_confidence(x_extrapolation)
                return predictions, confidence
            else:
                return predictions
    
    def _compute_extrapolation_confidence(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute confidence scores for extrapolation based on physics violations.
        
        Args:
            x: Input points
            
        Returns:
            Confidence scores (higher = more confident)
        """
        # Compute physics loss for each point
        physics_losses = []
        for i in range(x.shape[0]):
            point = x[i:i+1]
            point.requires_grad_(True)
            loss = self.model.compute_physics_loss(point)
            physics_losses.append(loss.item())
        
        physics_losses = torch.tensor(physics_losses)
        
        # Convert physics loss to confidence (lower loss = higher confidence)
        # Use exponential decay: confidence = exp(-loss/scale)
        scale = torch.mean(physics_losses) + 1e-8
        confidence = torch.exp(-physics_losses / scale)
        
        # Normalize to [0, 1]
        confidence = (confidence - torch.min(confidence)) / (torch.max(confidence) - torch.min(confidence) + 1e-8)
        
        return confidence
    
    def extrapolate_with_uncertainty(
        self,
        x_extrapolation: torch.Tensor,
        num_samples: int = 100
    ) -> Dict[str, torch.Tensor]:
        """
        Extrapolate with uncertainty quantification.
        
        Args:
            x_extrapolation: Points for extrapolation
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary with predictions and uncertainty components
        """
        self.model.eval()
        
        # Generate multiple predictions with different physics weights
        predictions = []
        physics_violations = []
        
        # Sample different physics weights
        physics_weights = torch.linspace(0.1, 2.0, num_samples)
        
        for weight in physics_weights:
            # Temporarily set physics weight
            original_weight = self.model.physics_loss_weight
            self.model.physics_loss_weight = weight.item()
            
            with torch.no_grad():
                pred = self.model.forward(x_extrapolation)
                predictions.append(pred)
                
                # Compute physics violation
                violation = self.model.compute_physics_loss(x_extrapolation)
                physics_violations.append(violation)
            
            # Restore original weight
            self.model.physics_loss_weight = original_weight
        
        predictions = torch.stack(predictions, dim=0)  # [num_samples, batch_size, output_dim]
        physics_violations = torch.stack(physics_violations, dim=0)  # [num_samples]
        
        # Compute statistics
        mean_pred = torch.mean(predictions, dim=0)
        std_pred = torch.std(predictions, dim=0)
        
        # Physics-based uncertainty
        physics_uncertainty = torch.std(physics_violations)
        
        # Domain violation
        domain_violation = self.model._check_domain_violation(x_extrapolation)
        
        return {
            'mean': mean_pred,
            'std': std_pred,
            'predictions': predictions,
            'physics_violations': physics_violations,
            'physics_uncertainty': physics_uncertainty,
            'domain_violation': domain_violation,
            'confidence_interval': {
                'lower': mean_pred - 1.96 * std_pred,
                'upper': mean_pred + 1.96 * std_pred
            }
        }
    
    def adaptive_extrapolation(
        self,
        x_extrapolation: torch.Tensor,
        max_iterations: int = 10,
        tolerance: float = 1e-4
    ) -> Dict[str, torch.Tensor]:
        """
        Adaptive extrapolation that adjusts physics weights based on violations.
        
        Args:
            x_extrapolation: Points for extrapolation
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            Dictionary with final predictions and convergence info
        """
        self.model.eval()
        
        # Initialize physics weight
        physics_weight = 1.0
        best_predictions = None
        best_violation = float('inf')
        
        for iteration in range(max_iterations):
            # Set physics weight
            self.model.physics_loss_weight = physics_weight
            
            with torch.no_grad():
                # Make predictions
                predictions = self.model.forward(x_extrapolation)
                
                # Compute physics violation
                violation = self.model.compute_physics_loss(x_extrapolation)
                violation_value = violation.item()
                
                # Check if this is the best so far
                if violation_value < best_violation:
                    best_violations = violation_value
                    best_predictions = predictions.clone()
                
                # Check convergence
                if violation_value < tolerance:
                    break
                
                # Adjust physics weight based on violation
                if violation_value > tolerance:
                    physics_weight *= 1.1  # Increase physics weight
                else:
                    physics_weight *= 0.9  # Decrease physics weight
                
                # Clamp physics weight
                physics_weight = max(0.1, min(10.0, physics_weight))
        
        return {
            'predictions': best_predictions,
            'final_physics_weight': physics_weight,
            'final_violation': best_violation,
            'iterations': iteration + 1,
            'converged': best_violation < tolerance
        }
    
    def extrapolate_with_physics_guidance(
        self,
        x_extrapolation: torch.Tensor,
        physics_guidance_strength: float = 1.0
    ) -> Dict[str, torch.Tensor]:
        """
        Extrapolate using physics guidance for better OOD behavior.
        
        Args:
            x_extrapolation: Points for extrapolation
            physics_guidance_strength: Strength of physics guidance
            
        Returns:
            Dictionary with predictions and physics information
        """
        self.model.eval()
        
        # Make predictions with physics information
        predictions, physics_info = self.model.predict_with_physics(
            x_extrapolation, return_physics_info=True
        )
        
        # Apply physics guidance
        if physics_guidance_strength > 0:
            # Adjust predictions based on physics violations
            physics_violation = physics_info['physics_violation']
            
            # Create physics-guided predictions
            # This is a simplified approach - in practice, you might want
            # to use more sophisticated physics-based corrections
            guidance_factor = torch.exp(-physics_guidance_strength * physics_violation)
            guided_predictions = predictions * guidance_factor
            
            physics_info['guided_predictions'] = guided_predictions
            physics_info['guidance_factor'] = guidance_factor
        
        return {
            'predictions': predictions,
            'physics_info': physics_info,
            'physics_guidance_strength': physics_guidance_strength
        }
    
    def evaluate_extrapolation_quality(
        self,
        x_extrapolation: torch.Tensor,
        y_true: Optional[torch.Tensor] = None
    ) -> Dict[str, float]:
        """
        Evaluate the quality of extrapolation predictions.
        
        Args:
            x_extrapolation: Extrapolation points
            y_true: True values (optional, for evaluation)
            
        Returns:
            Dictionary with quality metrics
        """
        # Get extrapolation results
        results = self.extrapolate_with_uncertainty(x_extrapolation)
        
        metrics = {
            'mean_physics_violation': torch.mean(results['physics_violations']).item(),
            'std_physics_violation': torch.std(results['physics_violations']).item(),
            'mean_prediction_std': torch.mean(results['std']).item(),
            'physics_uncertainty': results['physics_uncertainty'].item(),
            'domain_violation': results['domain_violation'].item()
        }
        
        if y_true is not None:
            # Compute prediction accuracy
            mse = torch.mean((results['mean'] - y_true)**2).item()
            rmse = np.sqrt(mse)
            
            metrics.update({
                'mse': mse,
                'rmse': rmse,
                'mae': torch.mean(torch.abs(results['mean'] - y_true)).item()
            })
        
        return metrics
    
    def get_domain_info(self) -> Dict[str, any]:
        """Get information about the domain and constraints."""
        return {
            'domain_bounds': self.domain_bounds,
            'num_physics_constraints': len(self.physics_constraints),
            'confidence_threshold': self.confidence_threshold,
            'model_physics_info': self.model.get_physics_info()
        }
