"""
Memory Bank for storing and retrieving OOD experiences.

This module provides a memory bank system for storing and retrieving
OOD experiences to support adaptive learning.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import random
from collections import deque
import heapq


class MemoryBank:
    """
    Memory Bank for storing and retrieving OOD experiences.
    
    This class provides a memory bank system for storing and retrieving
    OOD experiences to support adaptive learning.
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        embedding_dim: int = 128,
        similarity_threshold: float = 0.8,
        importance_weighting: bool = True
    ):
        """
        Initialize Memory Bank.
        
        Args:
            max_size: Maximum number of experiences to store
            embedding_dim: Dimension of experience embeddings
            similarity_threshold: Threshold for similarity-based retrieval
            importance_weighting: Whether to use importance weighting
        """
        self.max_size = max_size
        self.embedding_dim = embedding_dim
        self.similarity_threshold = similarity_threshold
        self.importance_weighting = importance_weighting
        
        # Memory storage
        self.experiences = deque(maxlen=max_size)
        self.embeddings = deque(maxlen=max_size)
        self.importance_scores = deque(maxlen=max_size)
        
        # Index for fast retrieval
        self.experience_index = {}
        self.similarity_index = {}
        
        # Statistics
        self.total_experiences = 0
        self.retrieval_count = 0
        
        # Experience metadata
        self.metadata = deque(maxlen=max_size)
    
    def add_experience(
        self,
        input_data: torch.Tensor,
        prediction: torch.Tensor,
        uncertainty: Dict[str, float],
        target: Optional[torch.Tensor] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add a new experience to the memory bank.
        
        Args:
            input_data: Input data
            prediction: Model prediction
            uncertainty: Uncertainty components
            target: Target value (if available)
            metadata: Additional metadata
            
        Returns:
            Experience ID
        """
        # Generate experience ID
        experience_id = self.total_experiences
        
        # Compute embedding
        embedding = self._compute_embedding(input_data, prediction, uncertainty)
        
        # Compute importance score
        importance = self._compute_importance(uncertainty, metadata)
        
        # Create experience
        experience = {
            'id': experience_id,
            'input_data': input_data.clone(),
            'prediction': prediction.clone(),
            'uncertainty': uncertainty.copy(),
            'target': target.clone() if target is not None else None,
            'timestamp': self.total_experiences
        }
        
        # Add to memory
        self.experiences.append(experience)
        self.embeddings.append(embedding)
        self.importance_scores.append(importance)
        self.metadata.append(metadata or {})
        
        # Update index
        self.experience_index[experience_id] = len(self.experiences) - 1
        
        # Update similarity index
        self._update_similarity_index(experience_id, embedding)
        
        self.total_experiences += 1
        
        return experience_id
    
    def retrieve_similar_experiences(
        self,
        query_input: torch.Tensor,
        query_prediction: torch.Tensor,
        query_uncertainty: Dict[str, float],
        n_experiences: int = 10,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar experiences from memory bank.
        
        Args:
            query_input: Query input data
            query_prediction: Query prediction
            query_uncertainty: Query uncertainty
            n_experiences: Number of experiences to retrieve
            similarity_threshold: Similarity threshold (overrides default)
            
        Returns:
            List of similar experiences
        """
        if not self.experiences:
            return []
        
        # Compute query embedding
        query_embedding = self._compute_embedding(query_input, query_prediction, query_uncertainty)
        
        # Compute similarities
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            similarity = self._compute_similarity(query_embedding, embedding)
            similarities.append((similarity, i))
        
        # Sort by similarity
        similarities.sort(reverse=True)
        
        # Filter by threshold
        threshold = similarity_threshold or self.similarity_threshold
        filtered_similarities = [(sim, idx) for sim, idx in similarities if sim >= threshold]
        
        # Select top experiences
        top_experiences = filtered_similarities[:n_experiences]
        
        # Retrieve experiences
        retrieved_experiences = []
        for similarity, idx in top_experiences:
            experience = self.experiences[idx].copy()
            experience['similarity'] = similarity
            experience['importance'] = self.importance_scores[idx]
            retrieved_experiences.append(experience)
        
        self.retrieval_count += 1
        
        return retrieved_experiences
    
    def retrieve_by_uncertainty(
        self,
        uncertainty_range: Tuple[float, float],
        n_experiences: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve experiences within a specific uncertainty range.
        
        Args:
            uncertainty_range: (min_uncertainty, max_uncertainty)
            n_experiences: Number of experiences to retrieve
            
        Returns:
            List of experiences in uncertainty range
        """
        min_uncertainty, max_uncertainty = uncertainty_range
        
        # Filter experiences by uncertainty
        filtered_experiences = []
        for i, experience in enumerate(self.experiences):
            total_uncertainty = experience['uncertainty'].get('total_std', 0.0)
            if min_uncertainty <= total_uncertainty <= max_uncertainty:
                filtered_experiences.append((total_uncertainty, i))
        
        # Sort by uncertainty
        filtered_experiences.sort()
        
        # Select top experiences
        top_experiences = filtered_experiences[:n_experiences]
        
        # Retrieve experiences
        retrieved_experiences = []
        for uncertainty, idx in top_experiences:
            experience = self.experiences[idx].copy()
            experience['uncertainty_score'] = uncertainty
            retrieved_experiences.append(experience)
        
        return retrieved_experiences
    
    def retrieve_by_importance(
        self,
        n_experiences: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most important experiences.
        
        Args:
            n_experiences: Number of experiences to retrieve
            
        Returns:
            List of most important experiences
        """
        if not self.experiences:
            return []
        
        # Create importance-sorted list
        importance_list = [(score, i) for i, score in enumerate(self.importance_scores)]
        importance_list.sort(reverse=True)
        
        # Select top experiences
        top_experiences = importance_list[:n_experiences]
        
        # Retrieve experiences
        retrieved_experiences = []
        for importance, idx in top_experiences:
            experience = self.experiences[idx].copy()
            experience['importance'] = importance
            retrieved_experiences.append(experience)
        
        return retrieved_experiences
    
    def update_importance(
        self,
        experience_id: int,
        new_importance: float
    ) -> bool:
        """
        Update importance score for an experience.
        
        Args:
            experience_id: ID of experience to update
            new_importance: New importance score
            
        Returns:
            True if update successful
        """
        if experience_id not in self.experience_index:
            return False
        
        idx = self.experience_index[experience_id]
        self.importance_scores[idx] = new_importance
        
        return True
    
    def _compute_embedding(
        self,
        input_data: torch.Tensor,
        prediction: torch.Tensor,
        uncertainty: Dict[str, float]
    ) -> np.ndarray:
        """Compute embedding for an experience."""
        # Simple embedding: concatenate input, prediction, and uncertainty
        input_flat = input_data.flatten().numpy()
        prediction_flat = prediction.flatten().numpy()
        
        # Uncertainty features
        uncertainty_features = np.array([
            uncertainty.get('epistemic_std', 0.0),
            uncertainty.get('aleatoric_std', 0.0),
            uncertainty.get('total_std', 0.0)
        ])
        
        # Concatenate all features
        embedding = np.concatenate([input_flat, prediction_flat, uncertainty_features])
        
        # Pad or truncate to embedding_dim
        if len(embedding) > self.embedding_dim:
            embedding = embedding[:self.embedding_dim]
        elif len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding))
            embedding = np.concatenate([embedding, padding])
        
        return embedding
    
    def _compute_importance(
        self,
        uncertainty: Dict[str, float],
        metadata: Optional[Dict[str, Any]]
    ) -> float:
        """Compute importance score for an experience."""
        if not self.importance_weighting:
            return 1.0
        
        # Base importance from uncertainty
        total_uncertainty = uncertainty.get('total_std', 0.0)
        epistemic_uncertainty = uncertainty.get('epistemic_std', 0.0)
        
        # Higher uncertainty = higher importance
        importance = total_uncertainty + 0.5 * epistemic_uncertainty
        
        # Adjust based on metadata
        if metadata:
            if metadata.get('ood_score', 0) > 0.5:
                importance *= 1.5  # Boost importance for OOD samples
            
            if metadata.get('prediction_error', 0) > 0.1:
                importance *= 1.2  # Boost importance for high-error samples
        
        return importance
    
    def _compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """Compute similarity between two embeddings."""
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return similarity
    
    def _update_similarity_index(
        self,
        experience_id: int,
        embedding: np.ndarray
    ):
        """Update similarity index for fast retrieval."""
        # Simple implementation: store embedding for later similarity computation
        # In practice, this would use more sophisticated indexing (e.g., FAISS)
        pass
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory bank."""
        if not self.experiences:
            return {
                'total_experiences': 0,
                'memory_utilization': 0.0,
                'average_importance': 0.0
            }
        
        return {
            'total_experiences': len(self.experiences),
            'memory_utilization': len(self.experiences) / self.max_size,
            'average_importance': np.mean(self.importance_scores),
            'max_importance': np.max(self.importance_scores),
            'min_importance': np.min(self.importance_scores),
            'retrieval_count': self.retrieval_count
        }
    
    def clear_memory(self):
        """Clear all experiences from memory bank."""
        self.experiences.clear()
        self.embeddings.clear()
        self.importance_scores.clear()
        self.metadata.clear()
        self.experience_index.clear()
        self.similarity_index.clear()
        self.total_experiences = 0
        self.retrieval_count = 0
    
    def save_memory_bank(self, filepath: str):
        """Save memory bank to file."""
        state = {
            'experiences': list(self.experiences),
            'embeddings': list(self.embeddings),
            'importance_scores': list(self.importance_scores),
            'metadata': list(self.metadata),
            'experience_index': self.experience_index,
            'total_experiences': self.total_experiences,
            'retrieval_count': self.retrieval_count
        }
        torch.save(state, filepath)
    
    def load_memory_bank(self, filepath: str):
        """Load memory bank from file."""
        state = torch.load(filepath)
        self.experiences = deque(state['experiences'], maxlen=self.max_size)
        self.embeddings = deque(state['embeddings'], maxlen=self.max_size)
        self.importance_scores = deque(state['importance_scores'], maxlen=self.max_size)
        self.metadata = deque(state['metadata'], maxlen=self.max_size)
        self.experience_index = state['experience_index']
        self.total_experiences = state['total_experiences']
        self.retrieval_count = state['retrieval_count']
