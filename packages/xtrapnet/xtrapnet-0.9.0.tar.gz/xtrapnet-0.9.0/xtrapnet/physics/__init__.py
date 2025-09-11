"""
Physics-Informed Neural Networks for XtrapNet.

This module provides Physics-Informed Neural Network implementations that
incorporate domain knowledge and physical constraints for better extrapolation.
"""

from .pinn import PhysicsInformedNN
from .physics_loss import PhysicsLoss
from .domain_aware import DomainAwareExtrapolation

__all__ = [
    "PhysicsInformedNN",
    "PhysicsLoss",
    "DomainAwareExtrapolation",
]
