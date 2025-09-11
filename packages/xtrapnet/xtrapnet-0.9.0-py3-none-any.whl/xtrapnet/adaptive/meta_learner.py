"""
Meta-Learning for rapid adaptation to new OOD scenarios.

This module implements meta-learning algorithms that enable XtrapNet
to quickly adapt to new out-of-distribution tasks and domains.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import copy
from abc import ABC, abstractmethod


class MetaLearningAlgorithm(ABC):
    """Abstract base class for meta-learning algorithms."""
    
    @abstractmethod
    def meta_update(
        self,
        model: nn.Module,
        support_data: List[Tuple[torch.Tensor, torch.Tensor]],
        query_data: List[Tuple[torch.Tensor, torch.Tensor]],
        meta_lr: float
    ) -> Dict[str, Any]:
        """Perform a meta-learning update step."""
        pass


class MAML(MetaLearningAlgorithm):
    """Model-Agnostic Meta-Learning (MAML) implementation."""
    
    def __init__(self, inner_lr: float = 0.01, first_order: bool = False):
        """
        Initialize MAML.
        
        Args:
            inner_lr: Learning rate for inner loop updates
            first_order: Whether to use first-order approximation
        """
        self.inner_lr = inner_lr
        self.first_order = first_order
    
    def meta_update(
        self,
        model: nn.Module,
        support_data: List[Tuple[torch.Tensor, torch.Tensor]],
        query_data: List[Tuple[torch.Tensor, torch.Tensor]],
        meta_lr: float
    ) -> Dict[str, Any]:
        """
        Perform MAML meta-update.
        
        Args:
            model: Model to meta-update
            support_data: Support set for adaptation
            query_data: Query set for evaluation
            meta_lr: Meta-learning rate
            
        Returns:
            Dictionary with meta-update results
        """
        # Store original parameters
        original_params = {name: param.clone() for name, param in model.named_parameters()}
        
        # Inner loop: adapt to support data
        adapted_params = self._inner_loop_update(model, support_data)
        
        # Query evaluation: evaluate on query data
        query_loss = self._evaluate_query(model, query_data, adapted_params)
        
        # Outer loop: meta-update using query loss
        meta_gradients = self._compute_meta_gradients(
            model, query_loss, original_params, adapted_params
        )
        
        # Apply meta-update
        self._apply_meta_update(model, meta_gradients, meta_lr)
        
        return {
            'query_loss': query_loss.item(),
            'adapted_params': adapted_params,
            'meta_gradients': meta_gradients
        }
    
    def _inner_loop_update(
        self,
        model: nn.Module,
        support_data: List[Tuple[torch.Tensor, torch.Tensor]]
    ) -> Dict[str, torch.Tensor]:
        """Perform inner loop adaptation."""
        # Create temporary model copy
        temp_model = copy.deepcopy(model)
        temp_optimizer = optim.SGD(temp_model.parameters(), lr=self.inner_lr)
        
        # Adapt to support data
        for inputs, targets in support_data:
            temp_optimizer.zero_grad()
            outputs = temp_model(inputs)
            loss = nn.MSELoss()(outputs, targets)
            loss.backward()
            temp_optimizer.step()
        
        # Return adapted parameters
        return {name: param.clone() for name, param in temp_model.named_parameters()}
    
    def _evaluate_query(
        self,
        model: nn.Module,
        query_data: List[Tuple[torch.Tensor, torch.Tensor]],
        adapted_params: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Evaluate adapted model on query data."""
        # Temporarily set adapted parameters
        original_params = {}
        for name, param in model.named_parameters():
            original_params[name] = param.data.clone()
            param.data = adapted_params[name]
        
        # Compute query loss
        total_loss = 0.0
        for inputs, targets in query_data:
            outputs = model(inputs)
            loss = nn.MSELoss()(outputs, targets)
            total_loss += loss
        
        # Restore original parameters
        for name, param in model.named_parameters():
            param.data = original_params[name]
        
        return total_loss / len(query_data)
    
    def _compute_meta_gradients(
        self,
        model: nn.Module,
        query_loss: torch.Tensor,
        original_params: Dict[str, torch.Tensor],
        adapted_params: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """Compute meta-gradients for outer loop update."""
        if self.first_order:
            # First-order approximation: use gradients from adapted model
            meta_gradients = {}
            for name, param in model.named_parameters():
                if param.grad is not None:
                    meta_gradients[name] = param.grad.clone()
            return meta_gradients
        else:
            # Second-order: compute gradients w.r.t. original parameters
            meta_gradients = torch.autograd.grad(
                query_loss, model.parameters(), create_graph=True
            )
            return {name: grad for name, grad in zip(model.named_parameters(), meta_gradients)}
    
    def _apply_meta_update(
        self,
        model: nn.Module,
        meta_gradients: Dict[str, torch.Tensor],
        meta_lr: float
    ):
        """Apply meta-update to model parameters."""
        for name, param in model.named_parameters():
            if name in meta_gradients:
                param.data = param.data - meta_lr * meta_gradients[name]


class Reptile(MetaLearningAlgorithm):
    """Reptile meta-learning algorithm."""
    
    def __init__(self, inner_lr: float = 0.01, inner_steps: int = 5):
        """
        Initialize Reptile.
        
        Args:
            inner_lr: Learning rate for inner loop
            inner_steps: Number of inner loop steps
        """
        self.inner_lr = inner_lr
        self.inner_steps = inner_steps
    
    def meta_update(
        self,
        model: nn.Module,
        support_data: List[Tuple[torch.Tensor, torch.Tensor]],
        query_data: List[Tuple[torch.Tensor, torch.Tensor]],
        meta_lr: float
    ) -> Dict[str, Any]:
        """Perform Reptile meta-update."""
        # Store original parameters
        original_params = {name: param.clone() for name, param in model.named_parameters()}
        
        # Inner loop: multiple gradient steps
        adapted_params = self._inner_loop_update(model, support_data)
        
        # Reptile update: move towards adapted parameters
        for name, param in model.named_parameters():
            param.data = param.data + meta_lr * (adapted_params[name] - param.data)
        
        # Evaluate on query data
        query_loss = self._evaluate_query(model, query_data)
        
        return {
            'query_loss': query_loss.item(),
            'adapted_params': adapted_params,
            'meta_update': {name: adapted_params[name] - original_params[name] 
                          for name in original_params}
        }
    
    def _inner_loop_update(
        self,
        model: nn.Module,
        support_data: List[Tuple[torch.Tensor, torch.Tensor]]
    ) -> Dict[str, torch.Tensor]:
        """Perform inner loop with multiple steps."""
        optimizer = optim.SGD(model.parameters(), lr=self.inner_lr)
        
        for step in range(self.inner_steps):
            total_loss = 0.0
            for inputs, targets in support_data:
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = nn.MSELoss()(outputs, targets)
                loss.backward()
                total_loss += loss
            
            optimizer.step()
        
        return {name: param.clone() for name, param in model.named_parameters()}
    
    def _evaluate_query(
        self,
        model: nn.Module,
        query_data: List[Tuple[torch.Tensor, torch.Tensor]]
    ) -> torch.Tensor:
        """Evaluate model on query data."""
        total_loss = 0.0
        for inputs, targets in query_data:
            outputs = model(inputs)
            loss = nn.MSELoss()(outputs, targets)
            total_loss += loss
        
        return total_loss / len(query_data)


class MetaLearner:
    """
    Meta-Learner for rapid adaptation to new OOD scenarios.
    
    This class provides meta-learning capabilities for quickly adapting
    to new out-of-distribution tasks and domains.
    """
    
    def __init__(
        self,
        algorithm: str = "maml",
        inner_lr: float = 0.01,
        meta_lr: float = 0.001,
        first_order: bool = False
    ):
        """
        Initialize Meta-Learner.
        
        Args:
            algorithm: Meta-learning algorithm ("maml" or "reptile")
            inner_lr: Learning rate for inner loop
            meta_lr: Learning rate for meta-updates
            first_order: Whether to use first-order approximation (MAML only)
        """
        self.meta_lr = meta_lr
        
        # Initialize algorithm
        if algorithm.lower() == "maml":
            self.algorithm = MAML(inner_lr=inner_lr, first_order=first_order)
        elif algorithm.lower() == "reptile":
            self.algorithm = Reptile(inner_lr=inner_lr)
        else:
            raise ValueError(f"Unknown meta-learning algorithm: {algorithm}")
        
        # Task memory for storing task-specific information
        self.task_memory = {}
        
        # Adaptation history
        self.adaptation_history = []
    
    def adapt_to_task(
        self,
        model: nn.Module,
        task_data: Dict[str, List[Tuple[torch.Tensor, torch.Tensor]]],
        task_id: str,
        n_adaptation_steps: int = 5
    ) -> Dict[str, Any]:
        """
        Adapt model to a new OOD task using meta-learning.
        
        Args:
            model: Model to adapt
            task_data: Dictionary with 'support' and 'query' data
            task_id: Unique identifier for the task
            n_adaptation_steps: Number of meta-adaptation steps
            
        Returns:
            Adaptation results
        """
        support_data = task_data.get('support', [])
        query_data = task_data.get('query', [])
        
        if not support_data or not query_data:
            raise ValueError("Both support and query data are required")
        
        # Store original model state
        original_state = {name: param.clone() for name, param in model.named_parameters()}
        
        # Perform meta-adaptation
        adaptation_results = []
        for step in range(n_adaptation_steps):
            result = self.algorithm.meta_update(
                model, support_data, query_data, self.meta_lr
            )
            adaptation_results.append(result)
        
        # Store task information
        self.task_memory[task_id] = {
            'original_state': original_state,
            'adaptation_results': adaptation_results,
            'support_data': support_data,
            'query_data': query_data,
            'final_loss': adaptation_results[-1]['query_loss']
        }
        
        # Record adaptation
        self.adaptation_history.append({
            'task_id': task_id,
            'steps': n_adaptation_steps,
            'final_loss': adaptation_results[-1]['query_loss'],
            'improvement': original_state.get('loss', float('inf')) - adaptation_results[-1]['query_loss']
        })
        
        return {
            'task_id': task_id,
            'final_loss': adaptation_results[-1]['query_loss'],
            'adaptation_steps': n_adaptation_steps,
            'improvement': adaptation_results[-1]['query_loss'] - adaptation_results[0]['query_loss']
        }
    
    def few_shot_adaptation(
        self,
        model: nn.Module,
        few_shot_data: List[Tuple[torch.Tensor, torch.Tensor]],
        n_shots: int = 5,
        adaptation_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Perform few-shot adaptation to new OOD data.
        
        Args:
            model: Model to adapt
            few_shot_data: Few-shot examples for adaptation
            n_shots: Number of shots (examples per class)
            adaptation_steps: Number of adaptation steps
            
        Returns:
            Few-shot adaptation results
        """
        if len(few_shot_data) < n_shots:
            raise ValueError(f"Need at least {n_shots} examples for few-shot adaptation")
        
        # Split data into support and query sets
        support_data = few_shot_data[:n_shots]
        query_data = few_shot_data[n_shots:]
        
        if not query_data:
            # If no query data, use support data for evaluation
            query_data = support_data
        
        # Create temporary task
        task_data = {'support': support_data, 'query': query_data}
        task_id = f"few_shot_{len(self.adaptation_history)}"
        
        # Adapt to task
        result = self.adapt_to_task(model, task_data, task_id, adaptation_steps)
        
        return result
    
    def get_task_performance(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get performance information for a specific task."""
        return self.task_memory.get(task_id)
    
    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get summary of all adaptations."""
        if not self.adaptation_history:
            return {'total_tasks': 0, 'average_improvement': 0.0}
        
        improvements = [h['improvement'] for h in self.adaptation_history if h['improvement'] != float('inf')]
        
        return {
            'total_tasks': len(self.adaptation_history),
            'average_improvement': np.mean(improvements) if improvements else 0.0,
            'best_improvement': np.max(improvements) if improvements else 0.0,
            'worst_improvement': np.min(improvements) if improvements else 0.0,
            'successful_adaptations': len(improvements)
        }
    
    def reset_task_memory(self):
        """Reset task memory and adaptation history."""
        self.task_memory = {}
        self.adaptation_history = []
    
    def save_meta_learner(self, filepath: str):
        """Save meta-learner state to file."""
        state = {
            'task_memory': self.task_memory,
            'adaptation_history': self.adaptation_history,
            'meta_lr': self.meta_lr,
            'algorithm_type': type(self.algorithm).__name__
        }
        torch.save(state, filepath)
    
    def load_meta_learner(self, filepath: str):
        """Load meta-learner state from file."""
        state = torch.load(filepath)
        self.task_memory = state['task_memory']
        self.adaptation_history = state['adaptation_history']
        self.meta_lr = state['meta_lr']
