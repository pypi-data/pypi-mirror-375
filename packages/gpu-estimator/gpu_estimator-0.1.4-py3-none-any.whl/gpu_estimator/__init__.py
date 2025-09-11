from .estimator import GPUEstimator, EstimationResult
from .utils import calculate_model_params, calculate_transformer_params, get_model_config

try:
    from .huggingface_models import HuggingFaceModelRegistry, HFModelInfo
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

__version__ = "0.1.4"

__all__ = [
    "GPUEstimator",
    "EstimationResult",
    "calculate_transformer_params",
    "calculate_model_params", 
    "get_model_config"
]

if HF_AVAILABLE:
    __all__.extend(["HuggingFaceModelRegistry", "HFModelInfo"])