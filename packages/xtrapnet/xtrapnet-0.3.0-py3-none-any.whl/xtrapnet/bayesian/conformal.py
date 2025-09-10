"""
Bayesian Conformal Prediction for uncertainty quantification.

This module combines Bayesian Neural Networks with conformal prediction
to provide uncertainty quantification with statistical guarantees.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from .bnn import BayesianNeuralNetwork
from .uncertainty import UncertaintyDecomposition


class BayesianConformalPredictor:
    """
    Bayesian Conformal Prediction for uncertainty quantification.
    
    This class combines Bayesian Neural Networks with conformal prediction
    to provide prediction intervals with statistical guarantees.
    """
    
    def __init__(
        self,
        model: BayesianNeuralNetwork,
        alpha: float = 0.1,
        method: str = 'bayesian'
    ):
        """
        Initialize Bayesian Conformal Predictor.
        
        Args:
            model: Bayesian Neural Network model
            alpha: Significance level (1 - confidence level)
            method: Conformal prediction method ('bayesian', 'standard', 'weighted')
        """
        self.model = model
        self.alpha = alpha
        self.method = method
        self.uncertainty_decomp = UncertaintyDecomposition(model)
        
        # Calibration data
        self.calibration_scores = None
        self.calibration_quantile = None
        self.is_calibrated = False
    
    def calibrate(
        self,
        x_cal: torch.Tensor,
        y_cal: torch.Tensor,
        num_samples: int = 100
    ):
        """
        Calibrate the conformal predictor using calibration data.
        
        Args:
            x_cal: Calibration features
            y_cal: Calibration targets
            num_samples: Number of Monte Carlo samples for uncertainty estimation
        """
        self.model.eval()
        with torch.no_grad():
            # Get predictions and uncertainty for calibration data
            if self.method == 'bayesian':
                uncertainty = self.uncertainty_decomp.decompose_uncertainty(
                    x_cal, num_samples
                )
                y_pred = uncertainty['mean']
                y_std = uncertainty['total_std']
            else:
                # Standard conformal prediction
                y_pred = self.model.forward(x_cal, sample=False)
                y_std = torch.ones_like(y_pred)  # Equal weights
            
            # Compute conformity scores
            if self.method == 'weighted':
                # Weighted conformal prediction
                scores = torch.abs(y_cal - y_pred) / (y_std + 1e-8)
            else:
                # Standard or Bayesian conformal prediction
                scores = torch.abs(y_cal - y_pred)
            
            # Store calibration scores
            self.calibration_scores = scores.flatten()
            
            # Compute quantile
            n = len(self.calibration_scores)
            quantile_level = (1 - self.alpha) * (n + 1) / n
            self.calibration_quantile = torch.quantile(
                self.calibration_scores, 
                min(quantile_level, 1.0)
            )
            
            self.is_calibrated = True
    
    def predict(
        self,
        x: torch.Tensor,
        num_samples: int = 100,
        return_uncertainty: bool = True
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """
        Make predictions with conformal prediction intervals.
        
        Args:
            x: Input features
            num_samples: Number of Monte Carlo samples
            return_uncertainty: Whether to return uncertainty components
            
        Returns:
            If return_uncertainty=False: predictions
            If return_uncertainty=True: (predictions, lower_bounds, upper_bounds)
        """
        if not self.is_calibrated:
            raise ValueError("Predictor must be calibrated before making predictions")
        
        self.model.eval()
        with torch.no_grad():
            if self.method == 'bayesian':
                uncertainty = self.uncertainty_decomp.decompose_uncertainty(x, num_samples)
                y_pred = uncertainty['mean']
                y_std = uncertainty['total_std']
            else:
                y_pred = self.model.forward(x, sample=False)
                y_std = torch.ones_like(y_pred)
            
            # Compute prediction intervals
            if self.method == 'weighted':
                # Weighted conformal prediction
                interval_width = self.calibration_quantile * y_std
            else:
                # Standard or Bayesian conformal prediction
                interval_width = self.calibration_quantile * torch.ones_like(y_pred)
            
            lower_bounds = y_pred - interval_width
            upper_bounds = y_pred + interval_width
            
            if return_uncertainty:
                return y_pred, lower_bounds, upper_bounds
            else:
                return y_pred
    
    def predict_with_uncertainty_decomposition(
        self,
        x: torch.Tensor,
        num_samples: int = 100
    ) -> Dict[str, torch.Tensor]:
        """
        Make predictions with detailed uncertainty decomposition.
        
        Args:
            x: Input features
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary with predictions and uncertainty components
        """
        if not self.is_calibrated:
            raise ValueError("Predictor must be calibrated before making predictions")
        
        # Get Bayesian uncertainty decomposition
        uncertainty = self.uncertainty_decomp.decompose_uncertainty(x, num_samples)
        
        # Get conformal prediction intervals
        y_pred, lower_bounds, upper_bounds = self.predict(x, num_samples, return_uncertainty=True)
        
        # Combine results
        result = {
            'prediction': y_pred,
            'conformal_lower': lower_bounds,
            'conformal_upper': upper_bounds,
            'conformal_width': upper_bounds - lower_bounds,
            'bayesian_mean': uncertainty['mean'],
            'bayesian_epistemic_std': uncertainty['epistemic_std'],
            'bayesian_aleatoric_std': uncertainty['aleatoric_std'],
            'bayesian_total_std': uncertainty['total_std'],
            'bayesian_confidence_95': uncertainty['confidence_95'],
            'bayesian_confidence_99': uncertainty['confidence_99'],
        }
        
        return result
    
    def evaluate_coverage(
        self,
        x_test: torch.Tensor,
        y_test: torch.Tensor,
        num_samples: int = 100
    ) -> Dict[str, float]:
        """
        Evaluate the coverage of conformal prediction intervals.
        
        Args:
            x_test: Test features
            y_test: Test targets
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary with coverage statistics
        """
        if not self.is_calibrated:
            raise ValueError("Predictor must be calibrated before evaluation")
        
        # Get predictions
        y_pred, lower_bounds, upper_bounds = self.predict(x_test, num_samples, return_uncertainty=True)
        
        # Check coverage
        covered = torch.logical_and(
            y_test >= lower_bounds,
            y_test <= upper_bounds
        )
        
        coverage = torch.mean(covered.float()).item()
        expected_coverage = 1 - self.alpha
        
        # Compute interval width statistics
        interval_widths = upper_bounds - lower_bounds
        mean_width = torch.mean(interval_widths).item()
        std_width = torch.std(interval_widths).item()
        
        # Compute prediction error
        mse = torch.mean((y_test - y_pred)**2).item()
        rmse = torch.sqrt(torch.tensor(mse)).item()
        
        return {
            'coverage': coverage,
            'expected_coverage': expected_coverage,
            'coverage_error': abs(coverage - expected_coverage),
            'mean_interval_width': mean_width,
            'std_interval_width': std_width,
            'mse': mse,
            'rmse': rmse,
            'num_test_points': len(y_test)
        }
    
    def get_calibration_info(self) -> Dict[str, Union[float, int, bool]]:
        """Get information about the calibration."""
        if not self.is_calibrated:
            return {'is_calibrated': False}
        
        return {
            'is_calibrated': True,
            'alpha': self.alpha,
            'confidence_level': 1 - self.alpha,
            'method': self.method,
            'calibration_quantile': self.calibration_quantile.item(),
            'num_calibration_points': len(self.calibration_scores),
            'calibration_scores_mean': torch.mean(self.calibration_scores).item(),
            'calibration_scores_std': torch.std(self.calibration_scores).item()
        }
    
    def update_alpha(self, new_alpha: float):
        """Update the significance level and recalibrate if needed."""
        self.alpha = new_alpha
        if self.is_calibrated:
            # Recompute quantile with new alpha
            n = len(self.calibration_scores)
            quantile_level = (1 - self.alpha) * (n + 1) / n
            self.calibration_quantile = torch.quantile(
                self.calibration_scores,
                min(quantile_level, 1.0)
            )
    
    def compare_methods(
        self,
        x_test: torch.Tensor,
        y_test: torch.Tensor,
        num_samples: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare different conformal prediction methods.
        
        Args:
            x_test: Test features
            y_test: Test targets
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary comparing different methods
        """
        results = {}
        
        # Store original method
        original_method = self.method
        
        # Test different methods
        for method in ['standard', 'weighted', 'bayesian']:
            self.method = method
            
            # Recalibrate with new method
            # Note: In practice, you'd want to use the same calibration data
            # This is a simplified version for demonstration
            
            try:
                coverage_results = self.evaluate_coverage(x_test, y_test, num_samples)
                results[method] = coverage_results
            except Exception as e:
                results[method] = {'error': str(e)}
        
        # Restore original method
        self.method = original_method
        
        return results
