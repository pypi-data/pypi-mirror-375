"""
Uncertainty decomposition and quantification for Bayesian Neural Networks.

This module provides advanced uncertainty quantification methods that decompose
uncertainty into different components for better understanding and control.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from .bnn import BayesianNeuralNetwork


class UncertaintyDecomposition:
    """
    Advanced uncertainty decomposition for Bayesian Neural Networks.
    
    This class provides methods to decompose predictive uncertainty into
    different components: epistemic (model) uncertainty, aleatoric (data)
    uncertainty, and other sources.
    """
    
    def __init__(self, model: BayesianNeuralNetwork):
        self.model = model
    
    def decompose_uncertainty(
        self,
        x: torch.Tensor,
        num_samples: int = 100,
        return_samples: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Decompose predictive uncertainty into different components.
        
        Args:
            x: Input tensor
            num_samples: Number of Monte Carlo samples
            return_samples: Whether to return individual samples
            
        Returns:
            Dictionary containing different uncertainty components
        """
        self.model.eval()
        with torch.no_grad():
            # Get multiple samples
            samples = []
            for _ in range(num_samples):
                sample = self.model.forward(x, sample=True)
                samples.append(sample)
            
            samples = torch.stack(samples, dim=0)  # [num_samples, batch_size, output_dim]
            
            # Basic statistics
            mean = torch.mean(samples, dim=0)
            variance = torch.var(samples, dim=0)
            std = torch.sqrt(variance)
            
            # Epistemic uncertainty (model uncertainty)
            epistemic_var = variance
            epistemic_std = std
            
            # Aleatoric uncertainty (data uncertainty)
            # This is a simplified approach - in practice, you might want to
            # learn the noise variance as a parameter
            aleatoric_var = torch.ones_like(epistemic_var) * 0.1  # Placeholder
            aleatoric_std = torch.sqrt(aleatoric_var)
            
            # Total uncertainty
            total_var = epistemic_var + aleatoric_var
            total_std = torch.sqrt(total_var)
            
            # Confidence intervals
            confidence_95 = {
                'lower': mean - 1.96 * total_std,
                'upper': mean + 1.96 * total_std
            }
            
            confidence_99 = {
                'lower': mean - 2.58 * total_std,
                'upper': mean + 2.58 * total_std
            }
            
            # Uncertainty ratios
            epistemic_ratio = epistemic_var / total_var
            aleatoric_ratio = aleatoric_var / total_var
            
            result = {
                'mean': mean,
                'epistemic_variance': epistemic_var,
                'aleatoric_variance': aleatoric_var,
                'total_variance': total_var,
                'epistemic_std': epistemic_std,
                'aleatoric_std': aleatoric_std,
                'total_std': total_std,
                'confidence_95': confidence_95,
                'confidence_99': confidence_99,
                'epistemic_ratio': epistemic_ratio,
                'aleatoric_ratio': aleatoric_ratio,
            }
            
            if return_samples:
                result['samples'] = samples
            
            return result
    
    def get_uncertainty_metrics(
        self,
        x: torch.Tensor,
        y_true: Optional[torch.Tensor] = None,
        num_samples: int = 100
    ) -> Dict[str, float]:
        """
        Compute various uncertainty metrics.
        
        Args:
            x: Input tensor
            y_true: True labels (optional, for calibration metrics)
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary of uncertainty metrics
        """
        uncertainty = self.decompose_uncertainty(x, num_samples)
        
        metrics = {
            'mean_epistemic_std': torch.mean(uncertainty['epistemic_std']).item(),
            'mean_aleatoric_std': torch.mean(uncertainty['aleatoric_std']).item(),
            'mean_total_std': torch.mean(uncertainty['total_std']).item(),
            'epistemic_ratio': torch.mean(uncertainty['epistemic_ratio']).item(),
            'aleatoric_ratio': torch.mean(uncertainty['aleatoric_ratio']).item(),
        }
        
        if y_true is not None:
            # Calibration metrics
            mean_pred = uncertainty['mean']
            total_std = uncertainty['total_std']
            
            # Check if true values fall within confidence intervals
            within_95 = torch.logical_and(
                y_true >= uncertainty['confidence_95']['lower'],
                y_true <= uncertainty['confidence_95']['upper']
            )
            within_99 = torch.logical_and(
                y_true >= uncertainty['confidence_99']['lower'],
                y_true <= uncertainty['confidence_99']['upper']
            )
            
            metrics['calibration_95'] = torch.mean(within_95.float()).item()
            metrics['calibration_99'] = torch.mean(within_99.float()).item()
            
            # Negative log-likelihood
            nll = 0.5 * torch.mean(
                (y_true - mean_pred)**2 / total_std**2 + torch.log(2 * np.pi * total_std**2)
            )
            metrics['negative_log_likelihood'] = nll.item()
            
            # Root mean square error
            rmse = torch.sqrt(torch.mean((y_true - mean_pred)**2))
            metrics['rmse'] = rmse.item()
        
        return metrics
    
    def analyze_uncertainty_by_region(
        self,
        x: torch.Tensor,
        num_samples: int = 100,
        num_bins: int = 10
    ) -> Dict[str, torch.Tensor]:
        """
        Analyze uncertainty patterns across different regions of input space.
        
        Args:
            x: Input tensor
            num_samples: Number of Monte Carlo samples
            num_bins: Number of bins for analysis
            
        Returns:
            Dictionary with uncertainty analysis by region
        """
        uncertainty = self.decompose_uncertainty(x, num_samples)
        
        # Bin the data based on input magnitude
        input_norms = torch.norm(x, dim=1)
        bin_edges = torch.linspace(
            torch.min(input_norms), 
            torch.max(input_norms), 
            num_bins + 1
        )
        
        bin_indices = torch.bucketize(input_norms, bin_edges) - 1
        bin_indices = torch.clamp(bin_indices, 0, num_bins - 1)
        
        # Compute statistics for each bin
        bin_stats = {}
        for i in range(num_bins):
            mask = bin_indices == i
            if torch.sum(mask) > 0:
                bin_stats[f'bin_{i}'] = {
                    'count': torch.sum(mask).item(),
                    'mean_epistemic_std': torch.mean(uncertainty['epistemic_std'][mask]).item(),
                    'mean_aleatoric_std': torch.mean(uncertainty['aleatoric_std'][mask]).item(),
                    'mean_total_std': torch.mean(uncertainty['total_std'][mask]).item(),
                    'input_norm_range': (bin_edges[i].item(), bin_edges[i+1].item())
                }
        
        return bin_stats
    
    def get_uncertainty_heatmap(
        self,
        x: torch.Tensor,
        num_samples: int = 100
    ) -> torch.Tensor:
        """
        Generate uncertainty heatmap for visualization.
        
        Args:
            x: Input tensor
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Uncertainty heatmap tensor
        """
        uncertainty = self.decompose_uncertainty(x, num_samples)
        
        # Create heatmap with different uncertainty components
        heatmap = torch.stack([
            uncertainty['epistemic_std'],
            uncertainty['aleatoric_std'],
            uncertainty['total_std']
        ], dim=-1)  # [batch_size, output_dim, 3]
        
        return heatmap
    
    def compare_uncertainty_methods(
        self,
        x: torch.Tensor,
        num_samples: int = 100
    ) -> Dict[str, Dict[str, torch.Tensor]]:
        """
        Compare different uncertainty estimation methods.
        
        Args:
            x: Input tensor
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary comparing different uncertainty methods
        """
        # Standard Monte Carlo
        mc_uncertainty = self.decompose_uncertainty(x, num_samples)
        
        # Deterministic forward pass (no uncertainty)
        self.model.eval()
        with torch.no_grad():
            deterministic_pred = self.model.forward(x, sample=False)
        
        # Single sample (point estimate)
        single_sample = self.model.forward(x, sample=True)
        
        return {
            'monte_carlo': mc_uncertainty,
            'deterministic': {
                'mean': deterministic_pred,
                'variance': torch.zeros_like(deterministic_pred),
                'std': torch.zeros_like(deterministic_pred)
            },
            'single_sample': {
                'mean': single_sample,
                'variance': torch.zeros_like(single_sample),
                'std': torch.zeros_like(single_sample)
            }
        }
