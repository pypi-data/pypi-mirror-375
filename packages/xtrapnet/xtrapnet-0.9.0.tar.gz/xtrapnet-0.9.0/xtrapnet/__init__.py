"""
XtrapNet - Extrapolation-Aware Neural Networks

A comprehensive framework for handling out-of-distribution extrapolation
in neural networks with novel technical contributions:

1. Adaptive Uncertainty Decomposition (AUD) - Uncertainty quantification that adapts
   based on local data density and model confidence
2. Constraint Satisfaction Networks (CSN) - Physics-informed extrapolation with
   explicit constraint satisfaction
3. Extrapolation-Aware Meta-Learning (EAML) - Meta-learning for domain adaptation
   with extrapolation capabilities
4. Comprehensive SOTA benchmarking against established methods
"""

# Core technical contributions
from .core import (
    # Adaptive Uncertainty Decomposition
    AdaptiveUncertaintyLayer,
    HierarchicalUncertaintyNetwork,
    DensityAwareOODDetector,
    UncertaintyComponents,
    
    # Constraint Satisfaction Networks
    ConstraintSatisfactionNetwork,
    AdaptivePhysicsNetwork,
    ExtrapolationConfidenceEstimator,
    PhysicsConstraint,
    conservation_constraint,
    monotonicity_constraint,
    symmetry_constraint,
    boundedness_constraint,
    smoothness_constraint,
    
    # Extrapolation-Aware Meta-Learning
    ExtrapolationAwareMetaLearner,
    DomainAdaptiveExtrapolation,
    ExtrapolationBenchmark,
    MetaTask,
    
    # SOTA Benchmarking
    SOTABenchmark,
    DeepEnsemble,
    MCDropout,
    EvidentialDeepLearning,
    MahalanobisOOD,
    BenchmarkResult
)

# Legacy components (for backward compatibility)
from .model import XtrapNet
from .trainer import XtrapTrainer
from .controller import XtrapController
from .pipeline import XtrapPipeline
from .config import PipelineConfig, default_config

# OOD Detection
from .ood.detectors import (
    MahalanobisDetector,
    KNNDetector,
    BaseDetector,
    NullDetector
)

# Uncertainty Quantification
from .uncertainty.conformal import ConformalCalibrator

# Ensemble methods
from .wrappers.ensemble import EnsembleWrapper

__version__ = "0.9.0"

__all__ = [
    # Core technical contributions
    "AdaptiveUncertaintyLayer",
    "HierarchicalUncertaintyNetwork",
    "DensityAwareOODDetector", 
    "UncertaintyComponents",
    "ConstraintSatisfactionNetwork",
    "AdaptivePhysicsNetwork",
    "ExtrapolationConfidenceEstimator",
    "PhysicsConstraint",
    "conservation_constraint",
    "monotonicity_constraint",
    "symmetry_constraint", 
    "boundedness_constraint",
    "smoothness_constraint",
    "ExtrapolationAwareMetaLearner",
    "DomainAdaptiveExtrapolation",
    "ExtrapolationBenchmark",
    "MetaTask",
    "SOTABenchmark",
    "DeepEnsemble",
    "MCDropout",
    "EvidentialDeepLearning", 
    "MahalanobisOOD",
    "BenchmarkResult",
    
    # Legacy components
    "XtrapNet",
    "XtrapTrainer",
    "XtrapController", 
    "XtrapPipeline",
    "PipelineConfig",
    "default_config",
    "MahalanobisDetector",
    "KNNDetector",
    "BaseDetector",
    "NullDetector",
    "ConformalCalibrator",
    "EnsembleWrapper",
]