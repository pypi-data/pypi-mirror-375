"""
MCMC-based Bayesian Neural Network implementation.

This module provides Hamiltonian Monte Carlo (HMC) and other MCMC methods
for Bayesian neural networks.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from .bnn import BayesianNeuralNetwork


class MCMCBNN(BayesianNeuralNetwork):
    """
    MCMC-based Bayesian Neural Network.
    
    This class provides Hamiltonian Monte Carlo sampling for Bayesian
    neural networks, offering high-quality uncertainty estimates.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int = 1,
        activation: str = 'relu',
        prior_std: float = 1.0,
        dropout_rate: float = 0.0,
        mcmc_method: str = 'hmc'
    ):
        super().__init__(
            input_dim, hidden_dims, output_dim, activation, prior_std, dropout_rate
        )
        self.mcmc_method = mcmc_method
        
        # MCMC parameters
        self.samples = []
        self.current_sample = None
        self.acceptance_rate = 0.0
        self.step_size = 0.01
        self.num_steps = 10
        
    def sample_prior(self) -> Dict[str, torch.Tensor]:
        """Sample parameters from the prior distribution."""
        sample = {}
        for i, layer in enumerate(self.layers):
            sample[f'layer_{i}_weight'] = torch.randn_like(layer.weight_mu) * self.prior_std
            if layer.bias_mu is not None:
                sample[f'layer_{i}_bias'] = torch.randn_like(layer.bias_mu) * self.prior_std
        return sample
    
    def set_parameters(self, sample: Dict[str, torch.Tensor]):
        """Set network parameters from a sample."""
        for i, layer in enumerate(self.layers):
            layer.weight_mu.data = sample[f'layer_{i}_weight']
            if layer.bias_mu is not None and f'layer_{i}_bias' in sample:
                layer.bias_mu.data = sample[f'layer_{i}_bias']
    
    def log_prior(self, sample: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Compute log prior probability."""
        log_prob = 0.0
        for key, value in sample.items():
            log_prob += -0.5 * torch.sum(value**2) / (self.prior_std**2)
        return log_prob
    
    def log_likelihood(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Compute log likelihood."""
        y_pred = self.forward(x, sample=False)  # Use current parameters
        return -0.5 * F.mse_loss(y_pred, y, reduction='sum')
    
    def log_posterior(self, x: torch.Tensor, y: torch.Tensor, sample: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Compute log posterior probability."""
        self.set_parameters(sample)
        log_prior = self.log_prior(sample)
        log_likelihood = self.log_likelihood(x, y)
        return log_prior + log_likelihood
    
    def hmc_step(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        current_sample: Dict[str, torch.Tensor]
    ) -> Tuple[Dict[str, torch.Tensor], bool]:
        """
        Single HMC step.
        
        Args:
            x: Input features
            y: Target values
            current_sample: Current parameter sample
            
        Returns:
            (new_sample, accepted)
        """
        # Initialize momentum
        momentum = {}
        for key, value in current_sample.items():
            momentum[key] = torch.randn_like(value)
        
        # Compute initial energy
        self.set_parameters(current_sample)
        initial_energy = -self.log_posterior(x, y, current_sample) + 0.5 * sum(
            torch.sum(p**2) for p in momentum.values()
        )
        
        # Leapfrog integration
        new_sample = {key: value.clone() for key, value in current_sample.items()}
        new_momentum = {key: value.clone() for key, value in momentum.items()}
        
        # Half step for momentum
        for key in new_sample.keys():
            new_sample[key].requires_grad_(True)
        
        self.set_parameters(new_sample)
        log_post = self.log_posterior(x, y, new_sample)
        log_post.backward()
        
        for key in new_sample.keys():
            new_momentum[key] -= 0.5 * self.step_size * new_sample[key].grad
            new_sample[key] = new_sample[key] + self.step_size * new_momentum[key]
        
        # Full steps
        for _ in range(self.num_steps - 1):
            for key in new_sample.keys():
                new_sample[key].requires_grad_(True)
            
            self.set_parameters(new_sample)
            log_post = self.log_posterior(x, y, new_sample)
            log_post.backward()
            
            for key in new_sample.keys():
                new_momentum[key] -= self.step_size * new_sample[key].grad
                new_sample[key] = new_sample[key] + self.step_size * new_momentum[key]
        
        # Final half step for momentum
        for key in new_sample.keys():
            new_sample[key].requires_grad_(True)
        
        self.set_parameters(new_sample)
        log_post = self.log_posterior(x, y, new_sample)
        log_post.backward()
        
        for key in new_sample.keys():
            new_momentum[key] -= 0.5 * self.step_size * new_sample[key].grad
        
        # Compute final energy
        final_energy = -self.log_posterior(x, y, new_sample) + 0.5 * sum(
            torch.sum(p**2) for p in new_momentum.values()
        )
        
        # Accept/reject
        log_acceptance = -final_energy + initial_energy
        accepted = torch.log(torch.rand(1)) < log_acceptance
        
        if accepted:
            return new_sample, True
        else:
            return current_sample, False
    
    def sample_posterior(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        num_samples: int = 100,
        burn_in: int = 50
    ) -> List[Dict[str, torch.Tensor]]:
        """
        Sample from the posterior distribution using MCMC.
        
        Args:
            x: Training features
            y: Training targets
            num_samples: Number of samples to collect
            burn_in: Number of burn-in samples
            
        Returns:
            List of parameter samples
        """
        print(f"Sampling from posterior using {self.mcmc_method}...")
        
        # Initialize with prior sample
        current_sample = self.sample_prior()
        self.samples = []
        
        total_steps = burn_in + num_samples
        accepted = 0
        
        for step in range(total_steps):
            if self.mcmc_method == 'hmc':
                current_sample, accepted_step = self.hmc_step(x, y, current_sample)
            else:
                raise ValueError(f"Unknown MCMC method: {self.mcmc_method}")
            
            if accepted_step:
                accepted += 1
            
            # Store sample after burn-in
            if step >= burn_in:
                self.samples.append({key: value.clone() for key, value in current_sample.items()})
            
            if step % 10 == 0:
                acceptance_rate = accepted / (step + 1)
                print(f"Step {step}: Acceptance rate = {acceptance_rate:.3f}")
        
        self.acceptance_rate = accepted / total_steps
        print(f"Final acceptance rate: {self.acceptance_rate:.3f}")
        print(f"Collected {len(self.samples)} samples")
        
        return self.samples
    
    def predict_with_mcmc_samples(
        self,
        x: torch.Tensor,
        num_samples: Optional[int] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Make predictions using MCMC samples.
        
        Args:
            x: Input features
            num_samples: Number of samples to use (None for all)
            
        Returns:
            (mean, variance)
        """
        if not self.samples:
            raise ValueError("No MCMC samples available. Run sample_posterior first.")
        
        if num_samples is None:
            num_samples = len(self.samples)
        
        # Use the last num_samples samples
        samples_to_use = self.samples[-num_samples:]
        
        predictions = []
        for sample in samples_to_use:
            self.set_parameters(sample)
            pred = self.forward(x, sample=False)
            predictions.append(pred)
        
        predictions = torch.stack(predictions, dim=0)  # [num_samples, batch_size, output_dim]
        mean = torch.mean(predictions, dim=0)
        variance = torch.var(predictions, dim=0)
        
        return mean, variance
    
    def get_mcmc_statistics(self) -> Dict[str, float]:
        """Get MCMC sampling statistics."""
        if not self.samples:
            return {'error': 'No samples available'}
        
        return {
            'num_samples': len(self.samples),
            'acceptance_rate': self.acceptance_rate,
            'step_size': self.step_size,
            'num_steps': self.num_steps,
            'method': self.mcmc_method
        }
    
    def set_mcmc_parameters(self, step_size: float = 0.01, num_steps: int = 10):
        """Set MCMC parameters."""
        self.step_size = step_size
        self.num_steps = num_steps
