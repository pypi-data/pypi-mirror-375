"""
XtrapNet Core Components

This module contains the core technical contributions of XtrapNet:
1. Adaptive Uncertainty Decomposition (AUD)
2. Constraint Satisfaction Networks (CSN) 
3. Extrapolation-Aware Meta-Learning (EAML)
4. SOTA Benchmarking Framework
"""

from .adaptive_uncertainty import (
    AdaptiveUncertaintyLayer,
    HierarchicalUncertaintyNetwork,
    DensityAwareOODDetector,
    UncertaintyComponents
)

from .physics_constrained import (
    ConstraintSatisfactionNetwork,
    AdaptivePhysicsNetwork,
    ExtrapolationConfidenceEstimator,
    PhysicsConstraint,
    conservation_constraint,
    monotonicity_constraint,
    symmetry_constraint,
    boundedness_constraint,
    smoothness_constraint
)

from .extrapolation_meta_learning import (
    ExtrapolationAwareMetaLearner,
    DomainAdaptiveExtrapolation,
    ExtrapolationBenchmark,
    MetaTask
)

from .sota_benchmark import (
    SOTABenchmark,
    SOTABaseline,
    DeepEnsemble,
    MCDropout,
    EvidentialDeepLearning,
    MahalanobisOOD,
    BenchmarkResult
)

__all__ = [
    # Adaptive Uncertainty
    "AdaptiveUncertaintyLayer",
    "HierarchicalUncertaintyNetwork", 
    "DensityAwareOODDetector",
    "UncertaintyComponents",
    
    # Physics Constrained
    "ConstraintSatisfactionNetwork",
    "AdaptivePhysicsNetwork",
    "ExtrapolationConfidenceEstimator",
    "PhysicsConstraint",
    "conservation_constraint",
    "monotonicity_constraint", 
    "symmetry_constraint",
    "boundedness_constraint",
    "smoothness_constraint",
    
    # Meta Learning
    "ExtrapolationAwareMetaLearner",
    "DomainAdaptiveExtrapolation",
    "ExtrapolationBenchmark",
    "MetaTask",
    
    # SOTA Benchmarking
    "SOTABenchmark",
    "SOTABaseline",
    "DeepEnsemble",
    "MCDropout", 
    "EvidentialDeepLearning",
    "MahalanobisOOD",
    "BenchmarkResult"
]
