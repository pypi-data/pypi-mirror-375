__all__ = [
    "GenerationConfig",
    "generate",
    "ResidualInjectionHook",
    "LogitBiasHook",
    "SoftPromptHook",
    "forward_with_hidden",
    "detect_components",
    # Training
    "TrainingConfig",
    "loss_forward",
    "xent_loss",
    "apply_lora",
    "merge_lora",
    "unmerge_lora",
    "train_step",
]

from .api import (
    GenerationConfig,
    generate,
    forward_with_hidden,
    detect_components,
)
from .injection import ResidualInjectionHook, LogitBiasHook, SoftPromptHook

from .training import (
    TrainingConfig,
    loss_forward,
    xent_loss,
    apply_lora,
    merge_lora,
    unmerge_lora,
    train_step,
)

__version__ = "0.1.0"
