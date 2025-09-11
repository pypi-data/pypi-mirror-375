"""
Continual Learning for handling sequential OOD data streams.

This module provides continual learning capabilities to handle sequential
streams of OOD data without catastrophic forgetting.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import copy
from collections import defaultdict
import random


class ContinualLearning:
    """
    Continual Learning for handling sequential OOD data streams.
    
    This class provides continual learning capabilities to handle sequential
    streams of OOD data without catastrophic forgetting.
    """
    
    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 0.001,
        memory_size: int = 1000,
        task_memory_size: int = 100,
        regularization_weight: float = 1.0,
        method: str = "ewc"
    ):
        """
        Initialize Continual Learning.
        
        Args:
            model: Model for continual learning
            learning_rate: Learning rate for updates
            memory_size: Size of experience replay buffer
            task_memory_size: Size of task-specific memory
            regularization_weight: Weight for regularization
            method: Continual learning method ("ewc", "l2", "replay")
        """
        self.model = model
        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.task_memory_size = task_memory_size
        self.regularization_weight = regularization_weight
        self.method = method
        
        # Task tracking
        self.current_task = 0
        self.task_memories = defaultdict(list)
        self.task_parameters = {}
        
        # Experience replay buffer
        self.replay_buffer = []
        
        # EWC parameters
        if method == "ewc":
            self.fisher_information = {}
            self.optimal_parameters = {}
        
        # Performance tracking
        self.task_performance = defaultdict(list)
        self.forgetting_metrics = {}
        
        # Optimizer
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    def start_new_task(self, task_id: int):
        """Start a new task in continual learning."""
        self.current_task = task_id
        
        # Store current parameters as optimal for previous task
        if self.method == "ewc" and task_id > 0:
            self.optimal_parameters[task_id - 1] = {
                name: param.clone() for name, param in self.model.named_parameters()
            }
        
        # Compute Fisher Information for EWC
        if self.method == "ewc":
            self._compute_fisher_information()
    
    def learn_task(
        self,
        task_data: List[Tuple[torch.Tensor, torch.Tensor]],
        epochs: int = 10,
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        Learn a new task while preventing catastrophic forgetting.
        
        Args:
            task_data: Data for the current task
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Learning results
        """
        # Store task data in memory
        self.task_memories[self.current_task] = random.sample(
            task_data, min(len(task_data), self.task_memory_size)
        )
        
        # Training loop
        training_losses = []
        for epoch in range(epochs):
            epoch_loss = self._train_epoch(task_data, batch_size)
            training_losses.append(epoch_loss)
        
        # Evaluate performance on current task
        current_performance = self._evaluate_task(task_data)
        self.task_performance[self.current_task].append(current_performance)
        
        # Evaluate forgetting on previous tasks
        forgetting_metrics = self._evaluate_forgetting()
        
        return {
            'task_id': self.current_task,
            'final_loss': training_losses[-1],
            'current_performance': current_performance,
            'forgetting_metrics': forgetting_metrics,
            'training_losses': training_losses
        }
    
    def _train_epoch(
        self,
        task_data: List[Tuple[torch.Tensor, torch.Tensor]],
        batch_size: int
    ) -> float:
        """Train for one epoch."""
        # Shuffle data
        shuffled_data = random.sample(task_data, len(task_data))
        
        total_loss = 0.0
        num_batches = 0
        
        for i in range(0, len(shuffled_data), batch_size):
            batch = shuffled_data[i:i + batch_size]
            
            # Prepare batch
            inputs = torch.stack([data[0] for data in batch])
            targets = torch.stack([data[1] for data in batch])
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            
            # Task loss
            task_loss = nn.MSELoss()(outputs, targets)
            
            # Regularization loss
            if self.method == "ewc":
                reg_loss = self._compute_ewc_loss()
            elif self.method == "l2":
                reg_loss = self._compute_l2_loss()
            elif self.method == "replay":
                reg_loss = self._compute_replay_loss()
            else:
                reg_loss = torch.tensor(0.0)
            
            # Total loss
            total_loss_value = task_loss + self.regularization_weight * reg_loss
            
            # Backward pass
            total_loss_value.backward()
            self.optimizer.step()
            
            total_loss += total_loss_value.item()
            num_batches += 1
        
        return total_loss / num_batches
    
    def _compute_ewc_loss(self) -> torch.Tensor:
        """Compute Elastic Weight Consolidation loss."""
        if not self.fisher_information or not self.optimal_parameters:
            return torch.tensor(0.0)
        
        ewc_loss = 0.0
        
        for task_id, optimal_params in self.optimal_parameters.items():
            if task_id in self.fisher_information:
                fisher_info = self.fisher_information[task_id]
                
                for name, param in self.model.named_parameters():
                    if name in optimal_params and name in fisher_info:
                        optimal_param = optimal_params[name]
                        fisher = fisher_info[name]
                        ewc_loss += (fisher * (param - optimal_param) ** 2).sum()
        
        return ewc_loss
    
    def _compute_l2_loss(self) -> torch.Tensor:
        """Compute L2 regularization loss."""
        l2_loss = 0.0
        
        for param in self.model.parameters():
            l2_loss += (param ** 2).sum()
        
        return l2_loss
    
    def _compute_replay_loss(self) -> torch.Tensor:
        """Compute experience replay loss."""
        if not self.replay_buffer:
            return torch.tensor(0.0)
        
        # Sample from replay buffer
        replay_batch = random.sample(self.replay_buffer, min(32, len(self.replay_buffer)))
        
        if not replay_batch:
            return torch.tensor(0.0)
        
        # Prepare replay batch
        replay_inputs = torch.stack([data[0] for data in replay_batch])
        replay_targets = torch.stack([data[1] for data in replay_batch])
        
        # Forward pass on replay data
        replay_outputs = self.model(replay_inputs)
        replay_loss = nn.MSELoss()(replay_outputs, replay_targets)
        
        return replay_loss
    
    def _compute_fisher_information(self):
        """Compute Fisher Information Matrix for EWC."""
        if self.current_task not in self.task_memories:
            return
        
        task_data = self.task_memories[self.current_task]
        if not task_data:
            return
        
        self.fisher_information[self.current_task] = {}
        
        # Sample data for Fisher computation
        sample_data = random.sample(task_data, min(10, len(task_data)))
        
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                fisher_info = torch.zeros_like(param)
                
                for input_data, target in sample_data:
                    # Forward pass
                    output = self.model(input_data.unsqueeze(0))
                    loss = nn.MSELoss()(output, target.unsqueeze(0))
                    
                    # Compute gradients
                    grad = torch.autograd.grad(loss, param, retain_graph=True)[0]
                    fisher_info += grad ** 2
                
                self.fisher_information[self.current_task][name] = fisher_info / len(sample_data)
    
    def _evaluate_task(self, task_data: List[Tuple[torch.Tensor, torch.Tensor]]) -> float:
        """Evaluate model performance on a task."""
        total_loss = 0.0
        
        with torch.no_grad():
            for input_data, target in task_data:
                output = self.model(input_data.unsqueeze(0))
                loss = nn.MSELoss()(output, target.unsqueeze(0))
                total_loss += loss.item()
        
        return total_loss / len(task_data)
    
    def _evaluate_forgetting(self) -> Dict[str, float]:
        """Evaluate catastrophic forgetting on previous tasks."""
        forgetting_metrics = {}
        
        for task_id in range(self.current_task):
            if task_id in self.task_performance:
                # Get original performance
                original_performance = self.task_performance[task_id][0]
                
                # Get current performance
                current_performance = self._evaluate_task(self.task_memories[task_id])
                
                # Compute forgetting
                forgetting = original_performance - current_performance
                forgetting_metrics[f'task_{task_id}'] = forgetting
        
        return forgetting_metrics
    
    def continual_learning_loop(
        self,
        task_stream: List[Tuple[int, List[Tuple[torch.Tensor, torch.Tensor]]]],
        epochs_per_task: int = 10
    ) -> Dict[str, Any]:
        """
        Run continual learning on a stream of tasks.
        
        Args:
            task_stream: Stream of (task_id, task_data) tuples
            epochs_per_task: Number of epochs per task
            
        Returns:
            Continual learning results
        """
        results = {
            'task_results': [],
            'forgetting_analysis': {},
            'performance_matrix': {}
        }
        
        for task_id, task_data in task_stream:
            # Start new task
            self.start_new_task(task_id)
            
            # Learn task
            task_result = self.learn_task(task_data, epochs_per_task)
            results['task_results'].append(task_result)
            
            # Update replay buffer
            if self.method == "replay":
                self._update_replay_buffer(task_data)
        
        # Analyze forgetting
        results['forgetting_analysis'] = self._analyze_forgetting()
        
        # Performance matrix
        results['performance_matrix'] = self._compute_performance_matrix()
        
        return results
    
    def _update_replay_buffer(self, task_data: List[Tuple[torch.Tensor, torch.Tensor]]):
        """Update experience replay buffer."""
        # Add new data to buffer
        self.replay_buffer.extend(task_data)
        
        # Maintain buffer size
        if len(self.replay_buffer) > self.memory_size:
            self.replay_buffer = random.sample(
                self.replay_buffer, self.memory_size
            )
    
    def _analyze_forgetting(self) -> Dict[str, Any]:
        """Analyze catastrophic forgetting across tasks."""
        if len(self.task_performance) < 2:
            return {'analysis': 'Not enough tasks for forgetting analysis'}
        
        forgetting_rates = []
        for task_id in range(len(self.task_performance) - 1):
            if task_id in self.task_performance:
                original_perf = self.task_performance[task_id][0]
                final_perf = self.task_performance[task_id][-1]
                forgetting_rate = (original_perf - final_perf) / original_perf
                forgetting_rates.append(forgetting_rate)
        
        return {
            'average_forgetting_rate': np.mean(forgetting_rates),
            'max_forgetting_rate': np.max(forgetting_rates),
            'forgetting_rates': forgetting_rates
        }
    
    def _compute_performance_matrix(self) -> Dict[str, Any]:
        """Compute performance matrix across tasks."""
        matrix = {}
        
        for task_id, performances in self.task_performance.items():
            matrix[f'task_{task_id}'] = {
                'initial_performance': performances[0],
                'final_performance': performances[-1],
                'performance_trend': np.polyfit(range(len(performances)), performances, 1)[0]
            }
        
        return matrix
    
    def get_continual_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about continual learning."""
        return {
            'total_tasks': len(self.task_performance),
            'current_task': self.current_task,
            'replay_buffer_size': len(self.replay_buffer),
            'task_memories': {task_id: len(memory) for task_id, memory in self.task_memories.items()},
            'method': self.method
        }
    
    def save_continual_learning_state(self, filepath: str):
        """Save continual learning state to file."""
        state = {
            'current_task': self.current_task,
            'task_memories': dict(self.task_memories),
            'task_parameters': self.task_parameters,
            'replay_buffer': self.replay_buffer,
            'fisher_information': self.fisher_information,
            'optimal_parameters': self.optimal_parameters,
            'task_performance': dict(self.task_performance)
        }
        torch.save(state, filepath)
    
    def load_continual_learning_state(self, filepath: str):
        """Load continual learning state from file."""
        state = torch.load(filepath)
        self.current_task = state['current_task']
        self.task_memories = defaultdict(list, state['task_memories'])
        self.task_parameters = state['task_parameters']
        self.replay_buffer = state['replay_buffer']
        self.fisher_information = state['fisher_information']
        self.optimal_parameters = state['optimal_parameters']
        self.task_performance = defaultdict(list, state['task_performance'])
