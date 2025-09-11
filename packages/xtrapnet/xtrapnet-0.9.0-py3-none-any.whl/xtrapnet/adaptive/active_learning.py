"""
Active Learning for intelligent OOD data acquisition.

This module provides active learning strategies to intelligently query
for labels on informative OOD samples.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import random
from abc import ABC, abstractmethod


class AcquisitionFunction(ABC):
    """Abstract base class for acquisition functions."""
    
    @abstractmethod
    def __call__(
        self,
        model: nn.Module,
        unlabeled_data: torch.Tensor,
        uncertainty: torch.Tensor
    ) -> torch.Tensor:
        """Compute acquisition scores for unlabeled data."""
        pass


class UncertaintySampling(AcquisitionFunction):
    """Uncertainty-based acquisition function."""
    
    def __init__(self, uncertainty_type: str = "entropy"):
        """
        Initialize uncertainty sampling.
        
        Args:
            uncertainty_type: Type of uncertainty ("entropy", "variance", "std")
        """
        self.uncertainty_type = uncertainty_type
    
    def __call__(
        self,
        model: nn.Module,
        unlabeled_data: torch.Tensor,
        uncertainty: torch.Tensor
    ) -> torch.Tensor:
        """Compute uncertainty-based acquisition scores."""
        if self.uncertainty_type == "entropy":
            # Higher entropy = more uncertain
            return uncertainty
        elif self.uncertainty_type == "variance":
            # Higher variance = more uncertain
            return uncertainty ** 2
        elif self.uncertainty_type == "std":
            # Higher standard deviation = more uncertain
            return uncertainty
        else:
            raise ValueError(f"Unknown uncertainty type: {self.uncertainty_type}")


class ExpectedImprovement(AcquisitionFunction):
    """Expected Improvement acquisition function."""
    
    def __init__(self, exploration_weight: float = 0.1):
        """
        Initialize Expected Improvement.
        
        Args:
            exploration_weight: Weight for exploration vs exploitation
        """
        self.exploration_weight = exploration_weight
    
    def __call__(
        self,
        model: nn.Module,
        unlabeled_data: torch.Tensor,
        uncertainty: torch.Tensor
    ) -> torch.Tensor:
        """Compute Expected Improvement scores."""
        # For regression, we use uncertainty as a proxy for improvement potential
        # Higher uncertainty suggests higher potential for improvement
        return uncertainty * self.exploration_weight


class DiversitySampling(AcquisitionFunction):
    """Diversity-based acquisition function."""
    
    def __init__(self, diversity_weight: float = 0.5):
        """
        Initialize diversity sampling.
        
        Args:
            diversity_weight: Weight for diversity vs uncertainty
        """
        self.diversity_weight = diversity_weight
    
    def __call__(
        self,
        model: nn.Module,
        unlabeled_data: torch.Tensor,
        uncertainty: torch.Tensor
    ) -> torch.Tensor:
        """Compute diversity-based acquisition scores."""
        # Simple diversity: distance from labeled data
        # In practice, this would compute distances to existing labeled samples
        diversity_scores = torch.rand_like(uncertainty)  # Placeholder
        
        return uncertainty + self.diversity_weight * diversity_scores


class ActiveLearning:
    """
    Active Learning for intelligent OOD data acquisition.
    
    This class provides active learning strategies to intelligently query
    for labels on informative OOD samples.
    """
    
    def __init__(
        self,
        acquisition_function: str = "uncertainty",
        query_batch_size: int = 5,
        uncertainty_threshold: float = 0.1,
        diversity_weight: float = 0.3
    ):
        """
        Initialize Active Learning.
        
        Args:
            acquisition_function: Acquisition function to use
            query_batch_size: Number of samples to query per batch
            uncertainty_threshold: Minimum uncertainty for querying
            diversity_weight: Weight for diversity in acquisition
        """
        self.query_batch_size = query_batch_size
        self.uncertainty_threshold = uncertainty_threshold
        self.diversity_weight = diversity_weight
        
        # Initialize acquisition function
        if acquisition_function == "uncertainty":
            self.acquisition_function = UncertaintySampling()
        elif acquisition_function == "expected_improvement":
            self.acquisition_function = ExpectedImprovement()
        elif acquisition_function == "diversity":
            self.acquisition_function = DiversitySampling(diversity_weight)
        else:
            raise ValueError(f"Unknown acquisition function: {acquisition_function}")
        
        # Query history
        self.query_history = []
        self.labeled_data = []
        self.unlabeled_data = []
        
        # Performance tracking
        self.performance_history = []
    
    def select_queries(
        self,
        model: nn.Module,
        unlabeled_data: torch.Tensor,
        uncertainty_scores: torch.Tensor,
        n_queries: Optional[int] = None
    ) -> List[int]:
        """
        Select samples to query for labels.
        
        Args:
            model: Current model
            unlabeled_data: Pool of unlabeled data
            uncertainty_scores: Uncertainty scores for unlabeled data
            n_queries: Number of queries to make (default: query_batch_size)
            
        Returns:
            Indices of selected samples
        """
        if n_queries is None:
            n_queries = self.query_batch_size
        
        # Filter by uncertainty threshold
        high_uncertainty_mask = uncertainty_scores > self.uncertainty_threshold
        if not high_uncertainty_mask.any():
            return []
        
        # Get high uncertainty samples
        high_uncertainty_indices = torch.where(high_uncertainty_mask)[0]
        high_uncertainty_data = unlabeled_data[high_uncertainty_indices]
        high_uncertainty_scores = uncertainty_scores[high_uncertainty_indices]
        
        # Compute acquisition scores
        acquisition_scores = self.acquisition_function(
            model, high_uncertainty_data, high_uncertainty_scores
        )
        
        # Select top-k samples
        top_k = min(n_queries, len(acquisition_scores))
        selected_indices = torch.topk(acquisition_scores, top_k).indices
        
        # Map back to original indices
        original_indices = high_uncertainty_indices[selected_indices].tolist()
        
        return original_indices
    
    def query_labels(
        self,
        model: nn.Module,
        unlabeled_data: torch.Tensor,
        uncertainty_scores: torch.Tensor,
        oracle_function: Callable[[torch.Tensor], torch.Tensor],
        n_queries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query labels for selected samples.
        
        Args:
            model: Current model
            unlabeled_data: Pool of unlabeled data
            uncertainty_scores: Uncertainty scores for unlabeled data
            oracle_function: Function to get true labels
            n_queries: Number of queries to make
            
        Returns:
            Query results
        """
        # Select samples to query
        query_indices = self.select_queries(model, unlabeled_data, uncertainty_scores, n_queries)
        
        if not query_indices:
            return {
                'queries_made': 0,
                'new_labeled_data': [],
                'remaining_unlabeled': len(unlabeled_data)
            }
        
        # Query labels from oracle
        queried_data = unlabeled_data[query_indices]
        queried_labels = oracle_function(queried_data)
        
        # Add to labeled data
        new_labeled_data = list(zip(queried_data, queried_labels))
        self.labeled_data.extend(new_labeled_data)
        
        # Remove from unlabeled data
        remaining_indices = [i for i in range(len(unlabeled_data)) if i not in query_indices]
        self.unlabeled_data = unlabeled_data[remaining_indices] if remaining_indices else torch.empty(0)
        
        # Record query
        self.query_history.append({
            'step': len(self.query_history),
            'queries_made': len(query_indices),
            'average_uncertainty': uncertainty_scores[query_indices].mean().item(),
            'indices': query_indices
        })
        
        return {
            'queries_made': len(query_indices),
            'new_labeled_data': new_labeled_data,
            'remaining_unlabeled': len(self.unlabeled_data),
            'query_indices': query_indices
        }
    
    def active_learning_loop(
        self,
        model: nn.Module,
        initial_unlabeled_data: torch.Tensor,
        oracle_function: Callable[[torch.Tensor], torch.Tensor],
        uncertainty_function: Callable[[nn.Module, torch.Tensor], torch.Tensor],
        max_iterations: int = 10,
        performance_eval_function: Optional[Callable[[nn.Module], float]] = None
    ) -> Dict[str, Any]:
        """
        Run active learning loop.
        
        Args:
            model: Model to improve
            initial_unlabeled_data: Initial pool of unlabeled data
            oracle_function: Function to get true labels
            uncertainty_function: Function to compute uncertainty
            max_iterations: Maximum number of iterations
            performance_eval_function: Function to evaluate model performance
            
        Returns:
            Active learning results
        """
        self.unlabeled_data = initial_unlabeled_data.clone()
        results = {
            'iterations': [],
            'total_queries': 0,
            'performance_history': []
        }
        
        for iteration in range(max_iterations):
            if len(self.unlabeled_data) == 0:
                break
            
            # Compute uncertainty for unlabeled data
            uncertainty_scores = uncertainty_function(model, self.unlabeled_data)
            
            # Query labels
            query_result = self.query_labels(
                model, self.unlabeled_data, uncertainty_scores, oracle_function
            )
            
            if query_result['queries_made'] == 0:
                break  # No more informative samples
            
            # Update model with new labeled data
            if query_result['new_labeled_data']:
                self._update_model(model, query_result['new_labeled_data'])
            
            # Evaluate performance
            if performance_eval_function:
                performance = performance_eval_function(model)
                results['performance_history'].append(performance)
            
            # Record iteration
            iteration_result = {
                'iteration': iteration,
                'queries_made': query_result['queries_made'],
                'total_labeled': len(self.labeled_data),
                'remaining_unlabeled': query_result['remaining_unlabeled'],
                'average_uncertainty': uncertainty_scores.mean().item()
            }
            
            if performance_eval_function:
                iteration_result['performance'] = performance
            
            results['iterations'].append(iteration_result)
            results['total_queries'] += query_result['queries_made']
        
        return results
    
    def _update_model(
        self,
        model: nn.Module,
        new_labeled_data: List[Tuple[torch.Tensor, torch.Tensor]]
    ):
        """Update model with new labeled data."""
        # Simple update: retrain on all labeled data
        # In practice, this would use more sophisticated update strategies
        
        if not new_labeled_data:
            return
        
        # Convert to tensors
        inputs = torch.stack([data[0] for data in new_labeled_data])
        targets = torch.stack([data[1] for data in new_labeled_data])
        
        # Simple gradient update
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        for _ in range(5):  # Few update steps
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = nn.MSELoss()(outputs, targets)
            loss.backward()
            optimizer.step()
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get statistics about queries made."""
        if not self.query_history:
            return {'total_queries': 0}
        
        total_queries = sum(h['queries_made'] for h in self.query_history)
        avg_uncertainty = np.mean([h['average_uncertainty'] for h in self.query_history])
        
        return {
            'total_queries': total_queries,
            'total_iterations': len(self.query_history),
            'average_queries_per_iteration': total_queries / len(self.query_history),
            'average_uncertainty': avg_uncertainty,
            'labeled_data_size': len(self.labeled_data)
        }
    
    def reset_active_learning(self):
        """Reset active learning state."""
        self.query_history = []
        self.labeled_data = []
        self.unlabeled_data = []
        self.performance_history = []
    
    def save_active_learning_state(self, filepath: str):
        """Save active learning state to file."""
        state = {
            'query_history': self.query_history,
            'labeled_data': self.labeled_data,
            'unlabeled_data': self.unlabeled_data,
            'performance_history': self.performance_history
        }
        torch.save(state, filepath)
    
    def load_active_learning_state(self, filepath: str):
        """Load active learning state from file."""
        state = torch.load(filepath)
        self.query_history = state['query_history']
        self.labeled_data = state['labeled_data']
        self.unlabeled_data = state['unlabeled_data']
        self.performance_history = state['performance_history']
