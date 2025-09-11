"""
Online Adaptation for continuous learning from OOD data streams.

This module provides online learning capabilities that allow XtrapNet
to continuously adapt to new OOD data without catastrophic forgetting.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import copy
from collections import deque
import random


class OnlineAdaptation:
    """
    Online Adaptation for continuous learning from OOD data streams.
    
    This class provides online learning capabilities that allow models
    to continuously adapt to new OOD data without catastrophic forgetting.
    """
    
    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 0.001,
        memory_size: int = 1000,
        adaptation_threshold: float = 0.1,
        forgetting_prevention: str = "ewc"
    ):
        """
        Initialize Online Adaptation.
        
        Args:
            model: Model to adapt online
            learning_rate: Learning rate for online updates
            memory_size: Size of experience replay buffer
            adaptation_threshold: Threshold for triggering adaptation
            forgetting_prevention: Method to prevent catastrophic forgetting
        """
        self.model = model
        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.adaptation_threshold = adaptation_threshold
        self.forgetting_prevention = forgetting_prevention
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=memory_size)
        
        # Model state tracking
        self.original_params = {name: param.clone() for name, param in model.named_parameters()}
        self.importance_weights = {}
        
        # Adaptation statistics
        self.adaptation_count = 0
        self.adaptation_history = []
        
        # Online optimizer
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        # EWC (Elastic Weight Consolidation) parameters
        if forgetting_prevention == "ewc":
            self.fisher_information = {}
            self.ewc_lambda = 1000.0
    
    def detect_adaptation_need(
        self,
        input_data: torch.Tensor,
        prediction: torch.Tensor,
        uncertainty: Dict[str, float]
    ) -> bool:
        """
        Detect if online adaptation is needed.
        
        Args:
            input_data: Input data
            prediction: Model prediction
            uncertainty: Uncertainty components
            
        Returns:
            True if adaptation is needed
        """
        # Check uncertainty threshold
        total_uncertainty = uncertainty.get('total_std', 0.0)
        if total_uncertainty > self.adaptation_threshold:
            return True
        
        # Check for significant prediction changes
        if len(self.adaptation_history) > 0:
            recent_predictions = [h['prediction'] for h in self.adaptation_history[-10:]]
            if recent_predictions:
                avg_recent = np.mean(recent_predictions)
                if abs(prediction.item() - avg_recent) > 2 * np.std(recent_predictions):
                    return True
        
        return False
    
    def adapt_online(
        self,
        input_data: torch.Tensor,
        target: torch.Tensor,
        uncertainty: Dict[str, float],
        adaptation_steps: int = 5
    ) -> Dict[str, Any]:
        """
        Perform online adaptation to new OOD data.
        
        Args:
            input_data: Input data for adaptation
            target: Target value
            uncertainty: Uncertainty components
            adaptation_steps: Number of adaptation steps
            
        Returns:
            Adaptation results
        """
        # Store experience in replay buffer
        self.experience_buffer.append({
            'input': input_data.clone(),
            'target': target.clone(),
            'uncertainty': uncertainty.copy(),
            'timestamp': len(self.adaptation_history)
        })
        
        # Compute importance weights if using EWC
        if self.forgetting_prevention == "ewc" and self.adaptation_count == 0:
            self._compute_fisher_information()
        
        # Perform online adaptation
        adaptation_losses = []
        for step in range(adaptation_steps):
            # Sample batch from experience buffer
            batch = self._sample_experience_batch(batch_size=min(32, len(self.experience_buffer)))
            
            # Compute adaptation loss
            loss = self._compute_adaptation_loss(batch)
            
            # Add forgetting prevention loss
            if self.forgetting_prevention == "ewc":
                ewc_loss = self._compute_ewc_loss()
                loss = loss + ewc_loss
            
            # Update model
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            adaptation_losses.append(loss.item())
        
        # Update adaptation statistics
        self.adaptation_count += 1
        self.adaptation_history.append({
            'step': self.adaptation_count,
            'loss': adaptation_losses[-1],
            'prediction': self.model(input_data).item(),
            'uncertainty': uncertainty
        })
        
        return {
            'adaptation_step': self.adaptation_count,
            'final_loss': adaptation_losses[-1],
            'loss_reduction': adaptation_losses[0] - adaptation_losses[-1],
            'buffer_size': len(self.experience_buffer)
        }
    
    def _sample_experience_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """Sample a batch from the experience replay buffer."""
        if len(self.experience_buffer) < batch_size:
            return list(self.experience_buffer)
        
        # Prioritized sampling based on uncertainty
        uncertainties = [exp['uncertainty']['total_std'] for exp in self.experience_buffer]
        probabilities = np.array(uncertainties) / np.sum(uncertainties)
        
        indices = np.random.choice(
            len(self.experience_buffer),
            size=batch_size,
            replace=False,
            p=probabilities
        )
        
        return [self.experience_buffer[i] for i in indices]
    
    def _compute_adaptation_loss(self, batch: List[Dict[str, Any]]) -> torch.Tensor:
        """Compute adaptation loss for a batch of experiences."""
        total_loss = 0.0
        
        for experience in batch:
            input_data = experience['input']
            target = experience['target']
            uncertainty = experience['uncertainty']
            
            # Forward pass
            prediction = self.model(input_data)
            
            # Base prediction loss
            prediction_loss = nn.MSELoss()(prediction, target)
            
            # Uncertainty-weighted loss
            uncertainty_weight = 1.0 / (1.0 + uncertainty['total_std'])
            weighted_loss = prediction_loss * uncertainty_weight
            
            total_loss += weighted_loss
        
        return total_loss / len(batch)
    
    def _compute_fisher_information(self):
        """Compute Fisher Information Matrix for EWC."""
        self.fisher_information = {}
        
        # Sample data from experience buffer
        if len(self.experience_buffer) < 10:
            return
        
        sample_batch = random.sample(list(self.experience_buffer), min(10, len(self.experience_buffer)))
        
        # Compute gradients for each parameter
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                fisher_info = torch.zeros_like(param)
                
                for experience in sample_batch:
                    input_data = experience['input']
                    target = experience['target']
                    
                    # Forward pass
                    prediction = self.model(input_data)
                    loss = nn.MSELoss()(prediction, target)
                    
                    # Compute gradients
                    grad = torch.autograd.grad(loss, param, retain_graph=True)[0]
                    fisher_info += grad ** 2
                
                self.fisher_information[name] = fisher_info / len(sample_batch)
    
    def _compute_ewc_loss(self) -> torch.Tensor:
        """Compute Elastic Weight Consolidation loss."""
        if not self.fisher_information:
            return torch.tensor(0.0)
        
        ewc_loss = 0.0
        
        for name, param in self.model.named_parameters():
            if name in self.fisher_information:
                fisher_info = self.fisher_information[name]
                original_param = self.original_params[name]
                
                ewc_loss += (fisher_info * (param - original_param) ** 2).sum()
        
        return self.ewc_lambda * ewc_loss
    
    def incremental_learning(
        self,
        new_data_stream: List[Tuple[torch.Tensor, torch.Tensor]],
        adaptation_batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Perform incremental learning on a stream of new data.
        
        Args:
            new_data_stream: Stream of new (input, target) pairs
            adaptation_batch_size: Size of batches for adaptation
            
        Returns:
            Incremental learning results
        """
        adaptation_results = []
        
        for i in range(0, len(new_data_stream), adaptation_batch_size):
            batch = new_data_stream[i:i + adaptation_batch_size]
            
            # Process each sample in the batch
            for input_data, target in batch:
                # Simulate uncertainty (in practice, this would come from the model)
                uncertainty = {
                    'epistemic_std': random.uniform(0.1, 0.5),
                    'aleatoric_std': random.uniform(0.05, 0.2),
                    'total_std': random.uniform(0.15, 0.6)
                }
                
                # Check if adaptation is needed
                prediction = self.model(input_data)
                if self.detect_adaptation_need(input_data, prediction, uncertainty):
                    result = self.adapt_online(input_data, target, uncertainty)
                    adaptation_results.append(result)
        
        return {
            'total_adaptations': len(adaptation_results),
            'data_processed': len(new_data_stream),
            'adaptation_rate': len(adaptation_results) / len(new_data_stream),
            'results': adaptation_results
        }
    
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get statistics about online adaptations."""
        if not self.adaptation_history:
            return {'total_adaptations': 0}
        
        losses = [h['loss'] for h in self.adaptation_history]
        uncertainties = [h['uncertainty']['total_std'] for h in self.adaptation_history]
        
        return {
            'total_adaptations': len(self.adaptation_history),
            'average_loss': np.mean(losses),
            'loss_trend': np.polyfit(range(len(losses)), losses, 1)[0],  # Slope
            'average_uncertainty': np.mean(uncertainties),
            'uncertainty_trend': np.polyfit(range(len(uncertainties)), uncertainties, 1)[0],
            'buffer_utilization': len(self.experience_buffer) / self.memory_size
        }
    
    def reset_adaptation(self):
        """Reset adaptation state."""
        self.experience_buffer.clear()
        self.adaptation_count = 0
        self.adaptation_history = []
        self.original_params = {name: param.clone() for name, param in self.model.named_parameters()}
        self.fisher_information = {}
    
    def save_adaptation_state(self, filepath: str):
        """Save adaptation state to file."""
        state = {
            'experience_buffer': list(self.experience_buffer),
            'adaptation_history': self.adaptation_history,
            'adaptation_count': self.adaptation_count,
            'fisher_information': self.fisher_information,
            'original_params': self.original_params
        }
        torch.save(state, filepath)
    
    def load_adaptation_state(self, filepath: str):
        """Load adaptation state from file."""
        state = torch.load(filepath)
        self.experience_buffer = deque(state['experience_buffer'], maxlen=self.memory_size)
        self.adaptation_history = state['adaptation_history']
        self.adaptation_count = state['adaptation_count']
        self.fisher_information = state['fisher_information']
        self.original_params = state['original_params']
