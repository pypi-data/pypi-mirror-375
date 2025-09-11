"""
Variational Bayesian Neural Network implementation.

This module provides variational inference methods for Bayesian neural networks,
including mean-field variational inference and more advanced techniques.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from .bnn import BayesianNeuralNetwork


class VariationalBNN(BayesianNeuralNetwork):
    """
    Variational Bayesian Neural Network with advanced VI techniques.
    
    This class extends the base BNN with sophisticated variational inference
    methods for better uncertainty quantification.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int = 1,
        activation: str = 'relu',
        prior_std: float = 1.0,
        dropout_rate: float = 0.0,
        vi_method: str = 'mean_field',
        temperature: float = 1.0
    ):
        super().__init__(
            input_dim, hidden_dims, output_dim, activation, prior_std, dropout_rate
        )
        self.vi_method = vi_method
        self.temperature = temperature
        
        # Initialize variational parameters
        self._init_variational_params()
    
    def _init_variational_params(self):
        """Initialize variational parameters based on the VI method."""
        if self.vi_method == 'mean_field':
            # Already initialized in BayesianLayer
            pass
        elif self.vi_method == 'structured':
            # Add structured variational parameters
            self._init_structured_params()
        elif self.vi_method == 'local_reparametrization':
            # Initialize for local reparameterization trick
            self._init_local_reparam()
        else:
            raise ValueError(f"Unknown VI method: {self.vi_method}")
    
    def _init_structured_params(self):
        """Initialize structured variational parameters."""
        # Add correlation parameters between layers
        self.layer_correlations = nn.ParameterList()
        for i in range(len(self.layers) - 1):
            corr = torch.randn(self.layers[i].out_features, self.layers[i+1].in_features) * 0.1
            self.layer_correlations.append(nn.Parameter(corr))
    
    def _init_local_reparam(self):
        """Initialize parameters for local reparameterization trick."""
        # This is handled in the forward pass
        pass
    
    def forward(
        self,
        x: torch.Tensor,
        sample: bool = True,
        num_samples: int = 1,
        use_local_reparam: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass with variational inference.
        
        Args:
            x: Input tensor
            sample: Whether to sample from posterior
            num_samples: Number of samples for uncertainty estimation
            use_local_reparam: Whether to use local reparameterization trick
        """
        if use_local_reparam and self.vi_method == 'local_reparametrization':
            return self._forward_local_reparam(x, num_samples)
        else:
            return super().forward(x, sample, num_samples)
    
    def _forward_local_reparam(
        self,
        x: torch.Tensor,
        num_samples: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass using local reparameterization trick.
        
        This is more efficient than standard reparameterization for large networks.
        """
        samples = []
        
        for _ in range(num_samples):
            current_x = x
            
            for i, layer in enumerate(self.layers[:-1]):
                # Local reparameterization: sample activations instead of weights
                mean = F.linear(current_x, layer.weight_mu, layer.bias_mu)
                var = F.linear(
                    current_x**2, 
                    torch.exp(layer.weight_logvar), 
                    torch.exp(layer.bias_logvar) if layer.bias_mu is not None else None
                )
                
                # Sample from N(mean, var)
                eps = torch.randn_like(mean)
                current_x = mean + torch.sqrt(var) * eps
                current_x = self.activation(current_x)
                
                if self.dropout is not None:
                    current_x = self.dropout(current_x)
            
            # Output layer
            mean = F.linear(current_x, self.layers[-1].weight_mu, self.layers[-1].bias_mu)
            var = F.linear(
                current_x**2,
                torch.exp(self.layers[-1].weight_logvar),
                torch.exp(self.layers[-1].bias_logvar) if self.layers[-1].bias_mu is not None else None
            )
            
            eps = torch.randn_like(mean)
            output = mean + torch.sqrt(var) * eps
            samples.append(output)
        
        samples = torch.stack(samples, dim=0)
        mean = torch.mean(samples, dim=0)
        variance = torch.var(samples, dim=0)
        
        return mean, variance
    
    def structured_kl_divergence(self) -> torch.Tensor:
        """Compute structured KL divergence including correlations."""
        base_kl = super().kl_divergence()
        
        # Add correlation terms
        correlation_kl = 0.0
        for corr in self.layer_correlations:
            # KL for correlation parameters (assuming Gaussian prior)
            correlation_kl += 0.5 * torch.sum(corr**2)
        
        return base_kl + correlation_kl
    
    def kl_divergence(self) -> torch.Tensor:
        """Compute KL divergence based on the VI method."""
        if self.vi_method == 'structured':
            return self.structured_kl_divergence()
        else:
            return super().kl_divergence()
    
    def elbo_loss(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        num_samples: int = 1,
        kl_weight: float = 1.0,
        use_local_reparam: bool = False
    ) -> torch.Tensor:
        """
        Enhanced ELBO loss with temperature scaling.
        
        Args:
            x: Input features
            y: Target values
            num_samples: Number of samples for Monte Carlo estimation
            kl_weight: Weight for KL divergence term
            use_local_reparam: Whether to use local reparameterization
        """
        # Likelihood term
        if use_local_reparam and self.vi_method == 'local_reparametrization':
            y_pred, y_var = self.forward(x, num_samples=num_samples, use_local_reparam=True)
            # Gaussian likelihood with learned variance
            likelihood = -0.5 * torch.sum(
                (y - y_pred)**2 / y_var + torch.log(2 * np.pi * y_var)
            )
        else:
            if num_samples == 1:
                y_pred = self.forward(x, sample=True)
            else:
                y_pred, _ = self.forward(x, sample=True, num_samples=num_samples)
            
            # Standard Gaussian likelihood
            likelihood = -0.5 * F.mse_loss(y_pred, y, reduction='sum')
        
        # KL divergence term with temperature scaling
        kl_div = self.kl_divergence() / self.temperature
        
        # ELBO = likelihood - KL
        elbo = likelihood - kl_weight * kl_div
        
        return -elbo  # Return negative ELBO for minimization
    
    def predict_with_uncertainty(
        self,
        x: torch.Tensor,
        num_samples: int = 100,
        use_local_reparam: bool = False
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Enhanced uncertainty prediction with variational methods.
        """
        self.eval()
        with torch.no_grad():
            if use_local_reparam and self.vi_method == 'local_reparametrization':
                mean, epistemic_var = self.forward(x, num_samples=num_samples, use_local_reparam=True)
                # For local reparameterization, we get the variance directly
                aleatoric_var = torch.ones_like(epistemic_var) * 0.1  # Placeholder
            else:
                # Standard sampling approach
                samples = []
                for _ in range(num_samples):
                    sample = self.forward(x, sample=True)
                    samples.append(sample)
                
                samples = torch.stack(samples, dim=0)
                mean = torch.mean(samples, dim=0)
                epistemic_var = torch.var(samples, dim=0)
                aleatoric_var = torch.ones_like(epistemic_var) * 0.1  # Placeholder
            
            return mean, aleatoric_var, epistemic_var
    
    def get_variational_parameters(self) -> Dict[str, torch.Tensor]:
        """Get all variational parameters for analysis."""
        params = {}
        
        for i, layer in enumerate(self.layers):
            params[f'layer_{i}_weight_mu'] = layer.weight_mu.data
            params[f'layer_{i}_weight_logvar'] = layer.weight_logvar.data
            
            if layer.bias_mu is not None:
                params[f'layer_{i}_bias_mu'] = layer.bias_mu.data
                params[f'layer_{i}_bias_logvar'] = layer.bias_logvar.data
        
        if self.vi_method == 'structured':
            for i, corr in enumerate(self.layer_correlations):
                params[f'correlation_{i}'] = corr.data
        
        return params
    
    def set_temperature(self, temperature: float):
        """Set temperature for annealing."""
        self.temperature = temperature
    
    def anneal_temperature(self, epoch: int, total_epochs: int, min_temp: float = 0.1):
        """Anneal temperature during training."""
        # Linear annealing from 1.0 to min_temp
        self.temperature = max(min_temp, 1.0 - (epoch / total_epochs) * (1.0 - min_temp))
