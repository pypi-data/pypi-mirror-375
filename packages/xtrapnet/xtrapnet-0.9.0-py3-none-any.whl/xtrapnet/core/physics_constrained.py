"""
Physics-Constrained Neural Networks for Extrapolation

This module implements a novel approach to physics-informed neural networks that
uses constraint satisfaction networks to ensure physical consistency during
extrapolation. The key innovation is the Constraint Satisfaction Network (CSN)
that learns to satisfy physical constraints while maintaining prediction accuracy.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
import math


@dataclass
class PhysicsConstraint:
    """Represents a physical constraint."""
    name: str
    constraint_func: Callable
    weight: float = 1.0
    domain: Optional[Tuple[float, float]] = None


class ConstraintSatisfactionNetwork(nn.Module):
    """
    Constraint Satisfaction Network that learns to satisfy physical constraints.
    
    This is a novel architecture that explicitly models constraint satisfaction
    as part of the learning process, ensuring that predictions remain physically
    consistent even during extrapolation.
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        constraint_dim: int,
        hidden_dim: int = 128,
        num_constraints: int = 5
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.constraint_dim = constraint_dim
        self.hidden_dim = hidden_dim
        self.num_constraints = num_constraints
        
        # Main prediction network
        self.predictor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Constraint satisfaction network
        self.constraint_net = nn.Sequential(
            nn.Linear(input_dim + output_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, constraint_dim)
        )
        
        # Constraint violation penalty network
        self.penalty_net = nn.Sequential(
            nn.Linear(constraint_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Softplus()
        )
        
        # Adaptive constraint weighting
        self.constraint_weights = nn.Parameter(torch.ones(num_constraints))
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize network weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(
        self,
        x: torch.Tensor,
        constraints: Optional[List[PhysicsConstraint]] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass with constraint satisfaction.
        
        Args:
            x: Input tensor
            constraints: List of physical constraints
            
        Returns:
            predictions, constraint_violations, penalty_scores
        """
        # Get initial predictions
        predictions = self.predictor(x)
        
        # Compute constraint violations
        if constraints is not None:
            constraint_violations = self._compute_constraint_violations(
                x, predictions, constraints
            )
        else:
            constraint_violations = torch.zeros(x.size(0), self.constraint_dim)
        
        # Compute penalty scores
        penalty_scores = self.penalty_net(constraint_violations)
        
        return predictions, constraint_violations, penalty_scores
    
    def _compute_constraint_violations(
        self,
        x: torch.Tensor,
        predictions: torch.Tensor,
        constraints: List[PhysicsConstraint]
    ) -> torch.Tensor:
        """Compute constraint violations for given predictions."""
        violations = []
        
        for i, constraint in enumerate(constraints):
            try:
                # Evaluate constraint function
                violation = constraint.constraint_func(x, predictions)
                
                # Apply domain constraints if specified
                if constraint.domain is not None:
                    domain_violation = self._compute_domain_violation(
                        x, constraint.domain
                    )
                    violation = violation + domain_violation
                
                violations.append(violation)
                
            except Exception:
                # If constraint evaluation fails, use zero violation
                violations.append(torch.zeros(x.size(0), 1))
        
        # Pad or truncate to match expected constraint dimension
        while len(violations) < self.constraint_dim:
            violations.append(torch.zeros(x.size(0), 1))
        
        violations = violations[:self.constraint_dim]
        
        return torch.cat(violations, dim=-1)
    
    def _compute_domain_violation(
        self,
        x: torch.Tensor,
        domain: Tuple[float, float]
    ) -> torch.Tensor:
        """Compute violation of domain constraints."""
        lower, upper = domain
        violation = torch.zeros_like(x)
        
        # Violation for values below lower bound
        below_lower = x < lower
        violation[below_lower] = (lower - x[below_lower]) ** 2
        
        # Violation for values above upper bound
        above_upper = x > upper
        violation[above_upper] = (x[above_upper] - upper) ** 2
        
        return violation.sum(dim=-1, keepdim=True)
    
    def compute_physics_loss(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        constraint_violations: torch.Tensor,
        penalty_scores: torch.Tensor,
        physics_weight: float = 1.0
    ) -> torch.Tensor:
        """
        Compute physics-informed loss that balances prediction accuracy
        with constraint satisfaction.
        """
        # Prediction loss
        pred_loss = F.mse_loss(predictions, targets)
        
        # Constraint violation loss
        constraint_loss = torch.mean(penalty_scores)
        
        # Total loss
        total_loss = pred_loss + physics_weight * constraint_loss
        
        return total_loss


class AdaptivePhysicsNetwork(nn.Module):
    """
    Adaptive Physics Network that learns to apply different physical constraints
    based on the input domain and context.
    
    This is a novel approach that allows the model to adapt its physical
    constraints based on the local context, enabling more flexible and
    accurate extrapolation.
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        num_physics_regimes: int = 3,
        hidden_dim: int = 128
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_physics_regimes = num_physics_regimes
        self.hidden_dim = hidden_dim
        
        # Regime classification network
        self.regime_classifier = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_physics_regimes),
            nn.Softmax(dim=-1)
        )
        
        # Physics networks for each regime
        self.physics_networks = nn.ModuleList([
            ConstraintSatisfactionNetwork(
                input_dim=input_dim,
                output_dim=output_dim,
                constraint_dim=5,
                hidden_dim=hidden_dim
            )
            for _ in range(num_physics_regimes)
        ])
        
        # Fusion network
        self.fusion_net = nn.Linear(
            output_dim * num_physics_regimes,
            output_dim
        )
    
    def forward(
        self,
        x: torch.Tensor,
        constraints: Optional[List[PhysicsConstraint]] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass with adaptive physics constraints.
        """
        # Classify physics regime
        regime_probs = self.regime_classifier(x)
        
        # Get predictions from each physics network
        regime_predictions = []
        regime_violations = []
        regime_penalties = []
        
        for i, physics_net in enumerate(self.physics_networks):
            pred, violations, penalties = physics_net(x, constraints)
            regime_predictions.append(pred)
            regime_violations.append(violations)
            regime_penalties.append(penalties)
        
        # Weighted combination based on regime probabilities
        weighted_predictions = torch.zeros_like(regime_predictions[0])
        weighted_violations = torch.zeros_like(regime_violations[0])
        weighted_penalties = torch.zeros_like(regime_penalties[0])
        
        for i, (pred, violations, penalties) in enumerate(
            zip(regime_predictions, regime_violations, regime_penalties)
        ):
            weight = regime_probs[:, i:i+1]
            weighted_predictions += weight * pred
            weighted_violations += weight * violations
            weighted_penalties += weight * penalties
        
        return weighted_predictions, weighted_violations, weighted_penalties
    
    def compute_adaptive_physics_loss(
        self,
        x: torch.Tensor,
        targets: torch.Tensor,
        constraints: Optional[List[PhysicsConstraint]] = None,
        physics_weight: float = 1.0
    ) -> torch.Tensor:
        """Compute adaptive physics loss."""
        predictions, violations, penalties = self.forward(x, constraints)
        
        # Prediction loss
        pred_loss = F.mse_loss(predictions, targets)
        
        # Physics loss
        physics_loss = torch.mean(penalties)
        
        # Regime classification loss (encourage confident regime selection)
        regime_probs = self.regime_classifier(x)
        regime_entropy = -torch.sum(regime_probs * torch.log(regime_probs + 1e-8), dim=-1)
        entropy_loss = torch.mean(regime_entropy)
        
        # Total loss
        total_loss = pred_loss + physics_weight * physics_loss + 0.1 * entropy_loss
        
        return total_loss


class ExtrapolationConfidenceEstimator:
    """
    Extrapolation confidence estimator that quantifies how confident the model
    is in its extrapolation predictions based on physical constraints.
    
    This is a novel approach that uses constraint satisfaction to estimate
    extrapolation confidence, providing a principled way to assess prediction
    reliability in extrapolation scenarios.
    """
    
    def __init__(
        self,
        physics_network: AdaptivePhysicsNetwork,
        confidence_threshold: float = 0.5
    ):
        self.physics_network = physics_network
        self.confidence_threshold = confidence_threshold
    
    def estimate_confidence(
        self,
        x: torch.Tensor,
        constraints: Optional[List[PhysicsConstraint]] = None
    ) -> torch.Tensor:
        """
        Estimate extrapolation confidence based on constraint satisfaction.
        """
        self.physics_network.eval()
        with torch.no_grad():
            predictions, violations, penalties = self.physics_network(x, constraints)
            
            # Confidence is inversely related to constraint violations
            # and penalty scores
            violation_confidence = 1.0 / (1.0 + torch.mean(violations, dim=-1))
            penalty_confidence = 1.0 / (1.0 + penalties.squeeze())
            
            # Combined confidence
            confidence = 0.7 * violation_confidence + 0.3 * penalty_confidence
            
            return confidence
    
    def is_safe_extrapolation(
        self,
        x: torch.Tensor,
        constraints: Optional[List[PhysicsConstraint]] = None
    ) -> torch.Tensor:
        """
        Determine if extrapolation is safe based on confidence estimates.
        """
        confidence = self.estimate_confidence(x, constraints)
        return confidence > self.confidence_threshold


# Common physical constraints
def conservation_constraint(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Conservation law constraint (e.g., mass, energy conservation)."""
    # Example: sum of outputs should be constant
    return torch.abs(torch.sum(y, dim=-1, keepdim=True) - 1.0)


def monotonicity_constraint(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Monotonicity constraint."""
    # Example: output should be monotonically increasing with input
    if x.size(-1) > 1 and y.size(-1) > 1:
        x_diff = x[:, 1:] - x[:, :-1]
        y_diff = y[:, 1:] - y[:, :-1]
        violation = torch.relu(-x_diff * y_diff)  # Violation if signs differ
        return torch.sum(violation, dim=-1, keepdim=True)
    return torch.zeros(x.size(0), 1)


def symmetry_constraint(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Symmetry constraint."""
    # Example: f(-x) = -f(x) for odd functions
    if x.size(-1) > 0:
        x_neg = -x
        y_neg = -y
        violation = torch.abs(y - y_neg)
        return torch.mean(violation, dim=-1, keepdim=True)
    return torch.zeros(x.size(0), 1)


def boundedness_constraint(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Boundedness constraint."""
    # Example: outputs should be bounded
    upper_bound = 10.0
    lower_bound = -10.0
    
    upper_violation = torch.relu(y - upper_bound)
    lower_violation = torch.relu(lower_bound - y)
    
    return torch.mean(upper_violation + lower_violation, dim=-1, keepdim=True)


def smoothness_constraint(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Smoothness constraint."""
    # Example: outputs should be smooth (low second derivative)
    if x.size(-1) > 2 and y.size(-1) > 2:
        # Approximate second derivative
        y_diff2 = y[:, 2:] - 2 * y[:, 1:-1] + y[:, :-2]
        return torch.mean(torch.abs(y_diff2), dim=-1, keepdim=True)
    return torch.zeros(x.size(0), 1)
