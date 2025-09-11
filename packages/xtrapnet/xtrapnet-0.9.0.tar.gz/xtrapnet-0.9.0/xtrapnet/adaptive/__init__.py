"""
Adaptive Learning & Meta-Learning for XtrapNet.

This module provides continuous learning capabilities for improving
OOD generalization over time without catastrophic forgetting.
"""

from .meta_learner import MetaLearner
from .online_adaptation import OnlineAdaptation
from .active_learning import ActiveLearning
from .continual_learning import ContinualLearning
from .memory_bank import MemoryBank

__all__ = [
    "MetaLearner",
    "OnlineAdaptation", 
    "ActiveLearning",
    "ContinualLearning",
    "MemoryBank",
]
