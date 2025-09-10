"""
Bayesian Neural Networks for XtrapNet.

This module provides Bayesian neural network implementations with proper
uncertainty quantification for extrapolation-aware machine learning.
"""

from .bnn import BayesianNeuralNetwork
from .variational import VariationalBNN
from .mcmc import MCMCBNN
from .uncertainty import UncertaintyDecomposition
from .conformal import BayesianConformalPredictor

__all__ = [
    "BayesianNeuralNetwork",
    "VariationalBNN", 
    "MCMCBNN",
    "UncertaintyDecomposition",
    "BayesianConformalPredictor",
]
