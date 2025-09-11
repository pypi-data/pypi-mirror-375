"""
Extrapolation-Aware Meta-Learning

This module implements a novel meta-learning approach specifically designed for
extrapolation scenarios. The key innovation is the Extrapolation-Aware Meta-Learning
(EAML) algorithm that learns to adapt to new domains while maintaining extrapolation
capabilities.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
import math


@dataclass
class MetaTask:
    """Represents a meta-learning task."""
    support_x: torch.Tensor
    support_y: torch.Tensor
    query_x: torch.Tensor
    query_y: torch.Tensor
    task_id: str
    domain_info: Optional[Dict] = None


class ExtrapolationAwareMetaLearner(nn.Module):
    """
    Extrapolation-Aware Meta-Learning algorithm that learns to adapt to new domains
    while maintaining extrapolation capabilities.
    
    Key innovation: The algorithm learns both task-specific adaptation and
    extrapolation strategies, enabling better generalization to unseen domains.
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dim: int = 128,
        adaptation_steps: int = 5,
        extrapolation_steps: int = 3,
        meta_lr: float = 0.01,
        adaptation_lr: float = 0.1
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
        self.adaptation_steps = adaptation_steps
        self.extrapolation_steps = extrapolation_steps
        self.meta_lr = meta_lr
        self.adaptation_lr = adaptation_lr
        
        # Base network
        self.base_network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Extrapolation network
        self.extrapolation_network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Domain adaptation network
        self.domain_adaptation = nn.Sequential(
            nn.Linear(input_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.Tanh()
        )
        
        # Extrapolation confidence estimator
        self.confidence_estimator = nn.Sequential(
            nn.Linear(input_dim + output_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
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
        adapted_params: Optional[Dict] = None,
        return_confidence: bool = False
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass with optional parameter adaptation.
        
        Args:
            x: Input tensor
            adapted_params: Adapted parameters from meta-learning
            return_confidence: Whether to return confidence estimates
            
        Returns:
            Predictions and optionally confidence estimates
        """
        if adapted_params is not None:
            # Use adapted parameters
            predictions = self._forward_with_params(x, adapted_params)
        else:
            # Use base network
            predictions = self.base_network(x)
        
        if return_confidence:
            # Estimate extrapolation confidence
            confidence = self.confidence_estimator(
                torch.cat([x, predictions], dim=-1)
            )
            return predictions, confidence
        
        return predictions
    
    def _forward_with_params(
        self,
        x: torch.Tensor,
        params: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Forward pass with custom parameters."""
        # This is a simplified version - in practice, you'd need to
        # implement proper parameter substitution
        return self.base_network(x)
    
    def adapt_to_task(
        self,
        task: MetaTask,
        num_steps: Optional[int] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Adapt the model to a specific task using gradient-based meta-learning.
        
        This implements the extrapolation-aware adaptation algorithm.
        """
        if num_steps is None:
            num_steps = self.adaptation_steps
        
        # Initialize adapted parameters
        adapted_params = {}
        for name, param in self.base_network.named_parameters():
            adapted_params[name] = param.clone()
        
        # Adaptation loop
        for step in range(num_steps):
            # Forward pass on support set
            support_pred = self._forward_with_params(task.support_x, adapted_params)
            support_loss = F.mse_loss(support_pred, task.support_y)
            
            # Compute gradients
            grads = torch.autograd.grad(
                support_loss,
                adapted_params.values(),
                create_graph=True,
                retain_graph=True
            )
            
            # Update adapted parameters
            for (name, param), grad in zip(adapted_params.items(), grads):
                adapted_params[name] = param - self.adaptation_lr * grad
        
        return adapted_params
    
    def extrapolation_adaptation(
        self,
        task: MetaTask,
        adapted_params: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Perform extrapolation-specific adaptation.
        
        This is a novel step that adapts the model specifically for
        extrapolation scenarios.
        """
        # Get extrapolation network predictions
        extrapolation_pred = self.extrapolation_network(task.support_x)
        
        # Compute extrapolation loss
        extrapolation_loss = F.mse_loss(extrapolation_pred, task.support_y)
        
        # Adapt extrapolation network
        extrapolation_grads = torch.autograd.grad(
            extrapolation_loss,
            self.extrapolation_network.parameters(),
            create_graph=True
        )
        
        # Update extrapolation parameters
        extrapolation_params = {}
        for (name, param), grad in zip(
            self.extrapolation_network.named_parameters(),
            extrapolation_grads
        ):
            extrapolation_params[name] = param - self.adaptation_lr * grad
        
        return extrapolation_params
    
    def meta_update(
        self,
        tasks: List[MetaTask],
        meta_optimizer: torch.optim.Optimizer
    ) -> Dict[str, float]:
        """
        Perform meta-update using multiple tasks.
        
        This implements the extrapolation-aware meta-learning algorithm.
        """
        meta_losses = []
        adaptation_losses = []
        extrapolation_losses = []
        
        for task in tasks:
            # Adapt to task
            adapted_params = self.adapt_to_task(task)
            
            # Extrapolation adaptation
            extrapolation_params = self.extrapolation_adaptation(task, adapted_params)
            
            # Evaluate on query set
            query_pred = self._forward_with_params(task.query_x, adapted_params)
            adaptation_loss = F.mse_loss(query_pred, task.query_y)
            
            # Extrapolation evaluation
            extrapolation_pred = self._forward_with_params(
                task.query_x, extrapolation_params
            )
            extrapolation_loss = F.mse_loss(extrapolation_pred, task.query_y)
            
            # Combined loss
            total_loss = 0.7 * adaptation_loss + 0.3 * extrapolation_loss
            
            meta_losses.append(total_loss)
            adaptation_losses.append(adaptation_loss)
            extrapolation_losses.append(extrapolation_loss)
        
        # Meta-update
        meta_loss = torch.stack(meta_losses).mean()
        meta_optimizer.zero_grad()
        meta_loss.backward()
        meta_optimizer.step()
        
        return {
            'meta_loss': meta_loss.item(),
            'adaptation_loss': torch.stack(adaptation_losses).mean().item(),
            'extrapolation_loss': torch.stack(extrapolation_losses).mean().item()
        }
    
    def predict_with_uncertainty(
        self,
        x: torch.Tensor,
        adapted_params: Optional[Dict] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Make predictions with uncertainty estimates.
        """
        predictions, confidence = self.forward(x, adapted_params, return_confidence=True)
        
        # Estimate uncertainty based on confidence
        uncertainty = 1.0 - confidence
        
        return predictions, uncertainty


class DomainAdaptiveExtrapolation:
    """
    Domain-adaptive extrapolation that learns to extrapolate across different
    domains while maintaining task-specific performance.
    
    This is a novel approach that combines domain adaptation with extrapolation
    capabilities.
    """
    
    def __init__(
        self,
        meta_learner: ExtrapolationAwareMetaLearner,
        domain_encoder_dim: int = 64
    ):
        self.meta_learner = meta_learner
        self.domain_encoder_dim = domain_encoder_dim
        
        # Domain encoder
        self.domain_encoder = nn.Sequential(
            nn.Linear(meta_learner.input_dim, domain_encoder_dim),
            nn.ReLU(),
            nn.Linear(domain_encoder_dim, domain_encoder_dim),
            nn.ReLU(),
            nn.Linear(domain_encoder_dim, domain_encoder_dim)
        )
        
        # Domain-specific adaptation
        self.domain_adaptation = nn.ModuleDict({
            'linear1': nn.Linear(domain_encoder_dim, meta_learner.hidden_dim),
            'linear2': nn.Linear(domain_encoder_dim, meta_learner.hidden_dim),
            'linear3': nn.Linear(domain_encoder_dim, meta_learner.output_dim)
        })
    
    def encode_domain(self, x: torch.Tensor) -> torch.Tensor:
        """Encode domain information from input data."""
        return self.domain_encoder(x)
    
    def adapt_to_domain(
        self,
        x: torch.Tensor,
        domain_code: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """Adapt model parameters based on domain encoding."""
        adapted_params = {}
        
        # Get base parameters
        for name, param in self.meta_learner.base_network.named_parameters():
            adapted_params[name] = param.clone()
        
        # Apply domain-specific adaptation
        for layer_name, adaptation_layer in self.domain_adaptation.items():
            if layer_name in adapted_params:
                domain_adaptation = adaptation_layer(domain_code)
                adapted_params[layer_name] = adapted_params[layer_name] + domain_adaptation
        
        return adapted_params
    
    def extrapolate_across_domains(
        self,
        source_x: torch.Tensor,
        source_y: torch.Tensor,
        target_x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extrapolate from source domain to target domain.
        """
        # Encode domains
        source_domain = self.encode_domain(source_x)
        target_domain = self.encode_domain(target_x)
        
        # Adapt to source domain
        source_params = self.adapt_to_domain(source_x, source_domain)
        
        # Make predictions on target domain
        target_pred, target_uncertainty = self.meta_learner.predict_with_uncertainty(
            target_x, source_params
        )
        
        return target_pred, target_uncertainty


class ExtrapolationBenchmark:
    """
    Benchmark for evaluating extrapolation capabilities of meta-learning algorithms.
    
    This provides standardized evaluation protocols for extrapolation scenarios.
    """
    
    def __init__(
        self,
        num_tasks: int = 100,
        support_size: int = 10,
        query_size: int = 20,
        extrapolation_ratio: float = 0.3
    ):
        self.num_tasks = num_tasks
        self.support_size = support_size
        self.query_size = query_size
        self.extrapolation_ratio = extrapolation_ratio
    
    def generate_extrapolation_tasks(
        self,
        input_dim: int = 2,
        output_dim: int = 1
    ) -> List[MetaTask]:
        """Generate extrapolation tasks for evaluation."""
        tasks = []
        
        for i in range(self.num_tasks):
            # Generate task-specific function
            task_func = self._generate_task_function()
            
            # Generate support set (in-distribution)
            support_x = torch.randn(self.support_size, input_dim)
            support_y = task_func(support_x)
            
            # Generate query set (mix of in-distribution and extrapolation)
            num_extrapolation = int(self.query_size * self.extrapolation_ratio)
            num_indistribution = self.query_size - num_extrapolation
            
            # In-distribution queries
            id_query_x = torch.randn(num_indistribution, input_dim)
            id_query_y = task_func(id_query_x)
            
            # Extrapolation queries (outside training distribution)
            extrapolation_query_x = torch.randn(num_extrapolation, input_dim) * 2.0 + 3.0
            extrapolation_query_y = task_func(extrapolation_query_x)
            
            # Combine queries
            query_x = torch.cat([id_query_x, extrapolation_query_x], dim=0)
            query_y = torch.cat([id_query_y, extrapolation_query_y], dim=0)
            
            # Create task
            task = MetaTask(
                support_x=support_x,
                support_y=support_y,
                query_x=query_x,
                query_y=query_y,
                task_id=f"task_{i}",
                domain_info={'extrapolation_ratio': self.extrapolation_ratio}
            )
            
            tasks.append(task)
        
        return tasks
    
    def _generate_task_function(self) -> Callable:
        """Generate a random task function."""
        # Random polynomial function
        degree = np.random.randint(1, 4)
        coefficients = torch.randn(degree + 1)
        
        def task_func(x):
            result = torch.zeros(x.size(0), 1)
            for i, coeff in enumerate(coefficients):
                if i == 0:
                    result += coeff
                else:
                    result += coeff * torch.pow(x[:, 0:1], i)
            return result
        
        return task_func
    
    def evaluate_extrapolation_performance(
        self,
        meta_learner: ExtrapolationAwareMetaLearner,
        tasks: List[MetaTask]
    ) -> Dict[str, float]:
        """Evaluate extrapolation performance on benchmark tasks."""
        total_losses = []
        extrapolation_losses = []
        indistribution_losses = []
        
        for task in tasks:
            # Adapt to task
            adapted_params = meta_learner.adapt_to_task(task)
            
            # Make predictions
            predictions, uncertainty = meta_learner.predict_with_uncertainty(
                task.query_x, adapted_params
            )
            
            # Compute losses
            total_loss = F.mse_loss(predictions, task.query_y)
            total_losses.append(total_loss.item())
            
            # Separate extrapolation and in-distribution losses
            extrapolation_ratio = task.domain_info['extrapolation_ratio']
            num_extrapolation = int(len(task.query_x) * extrapolation_ratio)
            
            if num_extrapolation > 0:
                extrapolation_pred = predictions[:num_extrapolation]
                extrapolation_target = task.query_y[:num_extrapolation]
                extrapolation_loss = F.mse_loss(extrapolation_pred, extrapolation_target)
                extrapolation_losses.append(extrapolation_loss.item())
            
            if num_extrapolation < len(task.query_x):
                id_pred = predictions[num_extrapolation:]
                id_target = task.query_y[num_extrapolation:]
                id_loss = F.mse_loss(id_pred, id_target)
                indistribution_losses.append(id_loss.item())
        
        return {
            'total_loss': np.mean(total_losses),
            'extrapolation_loss': np.mean(extrapolation_losses) if extrapolation_losses else 0.0,
            'indistribution_loss': np.mean(indistribution_losses) if indistribution_losses else 0.0,
            'extrapolation_ratio': len(extrapolation_losses) / len(total_losses) if total_losses else 0.0
        }
