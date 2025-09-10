from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ModelConfig:
    input_dim: int
    hidden_dim: int = 64
    dropout_rate: float = 0.1


@dataclass
class TrainingConfig:
    learning_rate: float = 1e-3
    num_epochs: int = 200
    batch_size: int = 128


@dataclass
class EnsembleConfig:
    enabled: bool = False
    num_members: int = 5
    diversity: str = "seed"


@dataclass
class UncertaintyConfig:
    mc_dropout: bool = True
    mc_samples: int = 30
    conformal: bool = True
    conformal_alpha: float = 0.1


@dataclass
class OODConfig:
    method: str = "mahalanobis"
    threshold_quantile: float = 0.95


@dataclass
class PolicyConfig:
    strategy: str = "conservative"
    abstain_uncertainty_quantile: float = 0.90
    abstain_ood_quantile: float = 0.95


@dataclass
class PipelineConfig:
    model: ModelConfig
    training: TrainingConfig = field(default_factory=TrainingConfig)
    ensemble: EnsembleConfig = field(default_factory=EnsembleConfig)
    uncertainty: UncertaintyConfig = field(default_factory=UncertaintyConfig)
    ood: OODConfig = field(default_factory=OODConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    extras: Dict[str, Any] = field(default_factory=dict)


def default_config(input_dim: int) -> PipelineConfig:
    return PipelineConfig(model=ModelConfig(input_dim=input_dim))


