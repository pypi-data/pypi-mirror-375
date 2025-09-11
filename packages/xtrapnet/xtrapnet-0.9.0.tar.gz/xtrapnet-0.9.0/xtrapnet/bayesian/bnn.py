"""
Base Bayesian Neural Network implementation.

This module provides the core Bayesian neural network class that serves as the
foundation for all Bayesian methods in XtrapNet.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from abc import ABC, abstractmethod


class BayesianLayer(nn.Module):
    """A Bayesian layer that maintains weight and bias distributions."""
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        prior_std: float = 1.0,
        bias: bool = True
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.prior_std = prior_std
        
        # Weight parameters (mean and log variance)
        self.weight_mu = nn.Parameter(torch.randn(out_features, in_features) * 0.1)
        self.weight_logvar = nn.Parameter(torch.randn(out_features, in_features) * 0.1 - 1.0)
        
        if bias:
            self.bias_mu = nn.Parameter(torch.randn(out_features) * 0.1)
            self.bias_logvar = nn.Parameter(torch.randn(out_features) * 0.1 - 1.0)
        else:
            self.register_parameter('bias_mu', None)
            self.register_parameter('bias_logvar', None)
    
    def forward(self, x: torch.Tensor, sample: bool = True) -> torch.Tensor:
        """Forward pass with optional sampling."""
        if sample:
            # Sample weights from posterior
            weight_std = torch.exp(0.5 * self.weight_logvar)
            weight_eps = torch.randn_like(weight_std)
            weight = self.weight_mu + weight_std * weight_eps
            
            if self.bias_mu is not None:
                bias_std = torch.exp(0.5 * self.bias_logvar)
                bias_eps = torch.randn_like(bias_std)
                bias = self.bias_mu + bias_std * bias_eps
            else:
                bias = None
        else:
            # Use mean weights (deterministic forward pass)
            weight = self.weight_mu
            bias = self.bias_mu
        
        return F.linear(x, weight, bias)
    
    def kl_divergence(self) -> torch.Tensor:
        """Compute KL divergence between posterior and prior."""
        # KL(q(w) || p(w)) where p(w) = N(0, prior_std^2)
        weight_kl = 0.5 * torch.sum(
            (self.weight_mu**2 + torch.exp(self.weight_logvar)) / (self.prior_std**2) 
            - self.weight_logvar + np.log(self.prior_std**2) - 1
        )
        
        bias_kl = 0.0
        if self.bias_mu is not None:
            bias_kl = 0.5 * torch.sum(
                (self.bias_mu**2 + torch.exp(self.bias_logvar)) / (self.prior_std**2)
                - self.bias_logvar + np.log(self.prior_std**2) - 1
            )
        
        return weight_kl + bias_kl


class BayesianNeuralNetwork(nn.Module):
    """
    Base Bayesian Neural Network class.
    
    This class provides the foundation for Bayesian neural networks with
    proper uncertainty quantification for extrapolation-aware learning.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int = 1,
        activation: str = 'relu',
        prior_std: float = 1.0,
        dropout_rate: float = 0.0
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        self.prior_std = prior_std
        self.dropout_rate = dropout_rate
        
        # Build network layers
        self.layers = nn.ModuleList()
        
        # Input layer
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            self.layers.append(BayesianLayer(prev_dim, hidden_dim, prior_std))
            prev_dim = hidden_dim
        
        # Output layer
        self.layers.append(BayesianLayer(prev_dim, output_dim, prior_std))
        
        # Activation function
        if activation == 'relu':
            self.activation = F.relu
        elif activation == 'tanh':
            self.activation = torch.tanh
        elif activation == 'sigmoid':
            self.activation = torch.sigmoid
        else:
            raise ValueError(f"Unknown activation: {activation}")
        
        # Dropout
        if dropout_rate > 0:
            self.dropout = nn.Dropout(dropout_rate)
        else:
            self.dropout = None
    
    def forward(
        self, 
        x: torch.Tensor, 
        sample: bool = True,
        num_samples: int = 1
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass through the Bayesian network.
        
        Args:
            x: Input tensor
            sample: Whether to sample from posterior (True) or use mean (False)
            num_samples: Number of samples for uncertainty estimation
            
        Returns:
            If num_samples=1: output tensor
            If num_samples>1: (mean, variance) tuple
        """
        if num_samples == 1:
            return self._forward_single(x, sample)
        else:
            return self._forward_multiple(x, num_samples)
    
    def _forward_single(self, x: torch.Tensor, sample: bool) -> torch.Tensor:
        """Single forward pass."""
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x, sample)
            x = self.activation(x)
            if self.dropout is not None:
                x = self.dropout(x)
        
        # Output layer (no activation)
        x = self.layers[-1](x, sample)
        return x
    
    def _forward_multiple(
        self, 
        x: torch.Tensor, 
        num_samples: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Multiple forward passes for uncertainty estimation."""
        samples = []
        for _ in range(num_samples):
            sample = self._forward_single(x, sample=True)
            samples.append(sample)
        
        samples = torch.stack(samples, dim=0)  # [num_samples, batch_size, output_dim]
        mean = torch.mean(samples, dim=0)
        variance = torch.var(samples, dim=0)
        
        return mean, variance
    
    def kl_divergence(self) -> torch.Tensor:
        """Total KL divergence across all layers."""
        total_kl = 0.0
        for layer in self.layers:
            total_kl += layer.kl_divergence()
        return total_kl
    
    def elbo_loss(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        num_samples: int = 1,
        kl_weight: float = 1.0
    ) -> torch.Tensor:
        """
        Evidence Lower Bound (ELBO) loss for variational inference.
        
        ELBO = E_q[log p(y|x,w)] - KL(q(w)||p(w))
        """
        # Likelihood term (negative log-likelihood)
        if num_samples == 1:
            y_pred = self.forward(x, sample=True)
        else:
            y_pred, _ = self.forward(x, sample=True, num_samples=num_samples)
        
        # Assuming Gaussian likelihood
        likelihood = -0.5 * F.mse_loss(y_pred, y, reduction='sum')
        
        # KL divergence term
        kl_div = self.kl_divergence()
        
        # ELBO = likelihood - KL
        elbo = likelihood - kl_weight * kl_div
        
        return -elbo  # Return negative ELBO for minimization
    
    def predict_with_uncertainty(
        self,
        x: torch.Tensor,
        num_samples: int = 100
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Make predictions with uncertainty quantification.
        
        Returns:
            mean: Predictive mean
            aleatoric_var: Data uncertainty (irreducible)
            epistemic_var: Model uncertainty (reducible)
        """
        self.eval()
        with torch.no_grad():
            # Get multiple samples
            samples = []
            for _ in range(num_samples):
                sample = self.forward(x, sample=True)
                samples.append(sample)
            
            samples = torch.stack(samples, dim=0)  # [num_samples, batch_size, output_dim]
            
            # Predictive mean
            mean = torch.mean(samples, dim=0)
            
            # Epistemic uncertainty (model uncertainty)
            epistemic_var = torch.var(samples, dim=0)
            
            # For aleatoric uncertainty, we need to estimate the noise level
            # This is a simplified approach - in practice, you might want to
            # learn the noise variance as a parameter
            aleatoric_var = torch.ones_like(epistemic_var) * 0.1  # Placeholder
            
            return mean, aleatoric_var, epistemic_var
    
    def get_uncertainty_decomposition(
        self,
        x: torch.Tensor,
        num_samples: int = 100
    ) -> Dict[str, torch.Tensor]:
        """
        Get detailed uncertainty decomposition.
        
        Returns:
            Dictionary with different uncertainty components
        """
        mean, aleatoric_var, epistemic_var = self.predict_with_uncertainty(x, num_samples)
        
        # Total uncertainty
        total_var = aleatoric_var + epistemic_var
        total_std = torch.sqrt(total_var)
        
        return {
            'mean': mean,
            'aleatoric_variance': aleatoric_var,
            'epistemic_variance': epistemic_var,
            'total_variance': total_var,
            'aleatoric_std': torch.sqrt(aleatoric_var),
            'epistemic_std': torch.sqrt(epistemic_var),
            'total_std': total_std,
            'confidence_interval': {
                'lower': mean - 1.96 * total_std,
                'upper': mean + 1.96 * total_std
            }
        }
