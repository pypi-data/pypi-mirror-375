"""
Physics-Informed Neural Network implementation.

This module provides the core PINN implementation that combines neural networks
with physical constraints for domain-aware extrapolation.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union, Callable
import numpy as np
from abc import ABC, abstractmethod


class PhysicsInformedNN(nn.Module):
    """
    Physics-Informed Neural Network for domain-aware extrapolation.
    
    This class combines neural networks with physical constraints to provide
    better extrapolation behavior that respects domain knowledge.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int = 1,
        activation: str = 'tanh',
        physics_loss_weight: float = 1.0,
        data_loss_weight: float = 1.0,
        boundary_loss_weight: float = 1.0,
        initial_loss_weight: float = 1.0
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        self.physics_loss_weight = physics_loss_weight
        self.data_loss_weight = data_loss_weight
        self.boundary_loss_weight = boundary_loss_weight
        self.initial_loss_weight = initial_loss_weight
        
        # Build neural network
        self.layers = nn.ModuleList()
        
        # Input layer
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            self.layers.append(nn.Linear(prev_dim, hidden_dim))
            prev_dim = hidden_dim
        
        # Output layer
        self.layers.append(nn.Linear(prev_dim, output_dim))
        
        # Activation function
        if activation == 'tanh':
            self.activation = torch.tanh
        elif activation == 'relu':
            self.activation = F.relu
        elif activation == 'sin':
            self.activation = torch.sin
        else:
            raise ValueError(f"Unknown activation: {activation}")
        
        # Physics constraints
        self.physics_constraints = []
        self.boundary_conditions = []
        self.initial_conditions = []
        
        # Domain boundaries
        self.domain_bounds = None
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the neural network."""
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = self.activation(x)
        
        # Output layer (no activation)
        x = self.layers[-1](x)
        return x
    
    def add_physics_constraint(
        self,
        constraint_func: Callable,
        weight: float = 1.0,
        name: str = "physics_constraint"
    ):
        """
        Add a physics constraint to the network.
        
        Args:
            constraint_func: Function that computes physics loss
            weight: Weight for this constraint
            name: Name of the constraint
        """
        self.physics_constraints.append({
            'func': constraint_func,
            'weight': weight,
            'name': name
        })
    
    def add_boundary_condition(
        self,
        boundary_func: Callable,
        weight: float = 1.0,
        name: str = "boundary_condition"
    ):
        """
        Add a boundary condition to the network.
        
        Args:
            boundary_func: Function that computes boundary loss
            weight: Weight for this constraint
            name: Name of the boundary condition
        """
        self.boundary_conditions.append({
            'func': boundary_func,
            'weight': weight,
            'name': name
        })
    
    def add_initial_condition(
        self,
        initial_func: Callable,
        weight: float = 1.0,
        name: str = "initial_condition"
    ):
        """
        Add an initial condition to the network.
        
        Args:
            initial_func: Function that computes initial condition loss
            weight: Weight for this constraint
            name: Name of the initial condition
        """
        self.initial_conditions.append({
            'func': initial_func,
            'weight': weight,
            'name': name
        })
    
    def set_domain_bounds(self, bounds: Dict[str, Tuple[float, float]]):
        """
        Set domain boundaries for the problem.
        
        Args:
            bounds: Dictionary mapping dimension names to (min, max) tuples
        """
        self.domain_bounds = bounds
    
    def compute_derivatives(
        self,
        x: torch.Tensor,
        order: int = 1
    ) -> List[torch.Tensor]:
        """
        Compute derivatives of the network output with respect to inputs.
        
        Args:
            x: Input tensor
            order: Order of derivatives to compute
            
        Returns:
            List of derivative tensors
        """
        x.requires_grad_(True)
        u = self.forward(x)
        
        derivatives = []
        for i in range(order):
            if i == 0:
                # First derivative
                grad_outputs = torch.ones_like(u)
                grad = torch.autograd.grad(
                    u, x, grad_outputs=grad_outputs, create_graph=True, retain_graph=True
                )[0]
            else:
                # Higher order derivatives
                grad_outputs = torch.ones_like(derivatives[-1])
                grad = torch.autograd.grad(
                    derivatives[-1], x, grad_outputs=grad_outputs, create_graph=True, retain_graph=True
                )[0]
            derivatives.append(grad)
        
        return derivatives
    
    def compute_physics_loss(self, x: torch.Tensor) -> torch.Tensor:
        """
        Compute physics loss from all constraints.
        
        Args:
            x: Input tensor
            
        Returns:
            Total physics loss
        """
        total_loss = 0.0
        
        for constraint in self.physics_constraints:
            loss = constraint['func'](x, self)
            total_loss += constraint['weight'] * loss
        
        return total_loss
    
    def compute_boundary_loss(self, x_boundary: torch.Tensor) -> torch.Tensor:
        """
        Compute boundary condition loss.
        
        Args:
            x_boundary: Boundary points
            
        Returns:
            Total boundary loss
        """
        total_loss = 0.0
        
        for boundary in self.boundary_conditions:
            loss = boundary['func'](x_boundary, self)
            total_loss += boundary['weight'] * loss
        
        return total_loss
    
    def compute_initial_loss(self, x_initial: torch.Tensor) -> torch.Tensor:
        """
        Compute initial condition loss.
        
        Args:
            x_initial: Initial condition points
            
        Returns:
            Total initial condition loss
        """
        total_loss = 0.0
        
        for initial in self.initial_conditions:
            loss = initial['func'](x_initial, self)
            total_loss += initial['weight'] * loss
        
        return total_loss
    
    def compute_total_loss(
        self,
        x_data: torch.Tensor,
        y_data: torch.Tensor,
        x_physics: torch.Tensor,
        x_boundary: Optional[torch.Tensor] = None,
        x_initial: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Compute total loss including data, physics, boundary, and initial conditions.
        
        Args:
            x_data: Data points
            y_data: Data targets
            x_physics: Physics points
            x_boundary: Boundary points (optional)
            x_initial: Initial condition points (optional)
            
        Returns:
            Dictionary of loss components
        """
        losses = {}
        
        # Data loss
        y_pred = self.forward(x_data)
        data_loss = F.mse_loss(y_pred, y_data)
        losses['data_loss'] = data_loss
        
        # Physics loss
        physics_loss = self.compute_physics_loss(x_physics)
        losses['physics_loss'] = physics_loss
        
        # Boundary loss
        if x_boundary is not None:
            boundary_loss = self.compute_boundary_loss(x_boundary)
            losses['boundary_loss'] = boundary_loss
        else:
            boundary_loss = torch.tensor(0.0)
            losses['boundary_loss'] = boundary_loss
        
        # Initial condition loss
        if x_initial is not None:
            initial_loss = self.compute_initial_loss(x_initial)
            losses['initial_loss'] = initial_loss
        else:
            initial_loss = torch.tensor(0.0)
            losses['initial_loss'] = initial_loss
        
        # Total loss
        total_loss = (
            self.data_loss_weight * data_loss +
            self.physics_loss_weight * physics_loss +
            self.boundary_loss_weight * boundary_loss +
            self.initial_loss_weight * initial_loss
        )
        losses['total_loss'] = total_loss
        
        return losses
    
    def predict_with_physics(
        self,
        x: torch.Tensor,
        return_physics_info: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, Dict[str, torch.Tensor]]]:
        """
        Make predictions with physics information.
        
        Args:
            x: Input tensor
            return_physics_info: Whether to return physics information
            
        Returns:
            Predictions and optionally physics information
        """
        self.eval()
        with torch.no_grad():
            predictions = self.forward(x)
            
            if return_physics_info:
                # Compute physics-related information
                physics_info = {}
                
                # Check if predictions satisfy physics constraints
                physics_loss = self.compute_physics_loss(x)
                physics_info['physics_violation'] = physics_loss
                
                # Check domain bounds
                if self.domain_bounds is not None:
                    physics_info['domain_violation'] = self._check_domain_violation(x)
                
                # Compute derivatives if needed
                if len(self.physics_constraints) > 0:
                    derivatives = self.compute_derivatives(x, order=1)
                    physics_info['derivatives'] = derivatives
                
                return predictions, physics_info
            else:
                return predictions
    
    def _check_domain_violation(self, x: torch.Tensor) -> torch.Tensor:
        """Check if inputs violate domain bounds."""
        if self.domain_bounds is None:
            return torch.tensor(0.0)
        
        violation = 0.0
        for i, (dim_name, (min_val, max_val)) in enumerate(self.domain_bounds.items()):
            if i < x.shape[1]:
                # Check lower bound
                lower_violation = torch.clamp(min_val - x[:, i], min=0.0)
                # Check upper bound
                upper_violation = torch.clamp(x[:, i] - max_val, min=0.0)
                violation += torch.sum(lower_violation + upper_violation)
        
        return violation
    
    def get_physics_info(self) -> Dict[str, any]:
        """Get information about physics constraints."""
        return {
            'num_physics_constraints': len(self.physics_constraints),
            'num_boundary_conditions': len(self.boundary_conditions),
            'num_initial_conditions': len(self.initial_conditions),
            'domain_bounds': self.domain_bounds,
            'loss_weights': {
                'physics': self.physics_loss_weight,
                'data': self.data_loss_weight,
                'boundary': self.boundary_loss_weight,
                'initial': self.initial_loss_weight
            }
        }
    
    def set_loss_weights(
        self,
        physics_weight: Optional[float] = None,
        data_weight: Optional[float] = None,
        boundary_weight: Optional[float] = None,
        initial_weight: Optional[float] = None
    ):
        """Set loss weights for different components."""
        if physics_weight is not None:
            self.physics_loss_weight = physics_weight
        if data_weight is not None:
            self.data_loss_weight = data_weight
        if boundary_weight is not None:
            self.boundary_loss_weight = boundary_weight
        if initial_weight is not None:
            self.initial_loss_weight = initial_weight
