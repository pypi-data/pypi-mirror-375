from dataclasses import dataclass
from typing import Optional, Dict, Any
import math
import warnings

try:
    from .huggingface_models import HuggingFaceModelRegistry
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


@dataclass
class EstimationResult:
    """Result of GPU estimation calculation."""
    memory_per_gpu_gb: float
    num_gpus: int
    total_memory_gb: float
    model_memory_gb: float
    optimizer_memory_gb: float
    activation_memory_gb: float
    gradient_memory_gb: float
    efficiency_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_per_gpu_gb": self.memory_per_gpu_gb,
            "num_gpus": self.num_gpus,
            "total_memory_gb": self.total_memory_gb,
            "model_memory_gb": self.model_memory_gb,
            "optimizer_memory_gb": self.optimizer_memory_gb,
            "activation_memory_gb": self.activation_memory_gb,
            "gradient_memory_gb": self.gradient_memory_gb,
            "efficiency_ratio": self.efficiency_ratio
        }


class GPUEstimator:
    """Estimates GPU memory requirements and optimal GPU count for training."""
    
    def __init__(self):
        self.precision_bytes = {
            "fp32": 4,
            "fp16": 2,
            "bf16": 2,
            "int8": 1
        }
        
        # Common GPU memory sizes in GB
        self.gpu_memory_sizes = {
            "V100": 32,
            "A100": 80,
            "H100": 80,
            "RTX3090": 24,
            "RTX4090": 24,
            "T4": 16,
            "L4": 24,
            "L40": 48,
            "A40": 48,
            "A6000": 48
        }
        
        # Initialize Hugging Face registry if available
        self.hf_registry = None
        if HF_AVAILABLE:
            try:
                self.hf_registry = HuggingFaceModelRegistry()
            except ImportError:
                warnings.warn("Hugging Face integration not available", UserWarning)
    
    def estimate(
        self,
        model_params: float,
        batch_size: int = 1,
        sequence_length: int = 2048,
        precision: str = "fp16",
        optimizer: str = "adam",
        gpu_memory_gb: Optional[float] = None,
        gpu_type: Optional[str] = None,
        gradient_checkpointing: bool = False,
        parallelism_efficiency: float = 0.85
    ) -> EstimationResult:
        """
        Estimate GPU requirements for training.
        
        Args:
            model_params: Number of model parameters
            batch_size: Training batch size
            sequence_length: Input sequence length
            precision: Model precision (fp32, fp16, bf16)
            optimizer: Optimizer type (adam, sgd, adamw)
            gpu_memory_gb: Available GPU memory in GB
            gpu_type: GPU type (V100, A100, H100, etc.)
            gradient_checkpointing: Whether gradient checkpointing is enabled
            parallelism_efficiency: Efficiency of parallelism (0.0-1.0)
        
        Returns:
            EstimationResult with memory breakdown and GPU count
        """
        if gpu_type and gpu_type in self.gpu_memory_sizes:
            gpu_memory_gb = self.gpu_memory_sizes[gpu_type]
        elif gpu_memory_gb is None:
            gpu_memory_gb = 80  # Default to A100
        
        bytes_per_param = self.precision_bytes.get(precision, 2)
        
        # Model memory (parameters)
        model_memory_gb = (model_params * bytes_per_param) / (1024**3)
        
        # Optimizer state memory
        optimizer_multiplier = self._get_optimizer_multiplier(optimizer, precision)
        optimizer_memory_gb = model_memory_gb * optimizer_multiplier
        
        # Gradient memory
        gradient_memory_gb = model_memory_gb
        
        # Activation memory (rough estimate)
        activation_memory_gb = self._estimate_activation_memory(
            batch_size, sequence_length, model_params, bytes_per_param, 
            gradient_checkpointing
        )
        
        # Total memory required
        total_memory_gb = (
            model_memory_gb + 
            optimizer_memory_gb + 
            gradient_memory_gb + 
            activation_memory_gb
        )
        
        # Add 20% overhead for framework and other memory usage
        total_memory_gb *= 1.2
        
        # Calculate number of GPUs needed
        memory_per_gpu = gpu_memory_gb * 0.9  # Leave 10% buffer
        min_gpus = max(1, math.ceil(total_memory_gb / memory_per_gpu))
        
        # Adjust for parallelism efficiency
        actual_memory_per_gpu = total_memory_gb / min_gpus if min_gpus > 0 else 0
        efficiency_ratio = min(1.0, parallelism_efficiency)
        
        return EstimationResult(
            memory_per_gpu_gb=actual_memory_per_gpu,
            num_gpus=min_gpus,
            total_memory_gb=total_memory_gb,
            model_memory_gb=model_memory_gb,
            optimizer_memory_gb=optimizer_memory_gb,
            activation_memory_gb=activation_memory_gb,
            gradient_memory_gb=gradient_memory_gb,
            efficiency_ratio=efficiency_ratio
        )
    
    def _get_optimizer_multiplier(self, optimizer: str, precision: str) -> float:
        """Get memory multiplier for optimizer states."""
        if optimizer.lower() in ["adam", "adamw"]:
            # Adam stores momentum and variance (2x parameters)
            if precision == "fp32":
                return 2.0
            else:
                # Mixed precision: optimizer states in fp32
                return 4.0
        elif optimizer.lower() == "sgd":
            # SGD with momentum (1x parameters)
            if precision == "fp32":
                return 1.0
            else:
                return 2.0
        else:
            # Default to Adam-like
            return 2.0 if precision == "fp32" else 4.0
    
    def _estimate_activation_memory(
        self, 
        batch_size: int, 
        sequence_length: int, 
        model_params: float,
        bytes_per_param: int,
        gradient_checkpointing: bool
    ) -> float:
        """Rough estimate of activation memory."""
        # Very rough heuristic: activations scale with batch_size * seq_len * sqrt(params)
        activation_scale = batch_size * sequence_length * math.sqrt(model_params)
        activation_memory_gb = (activation_scale * bytes_per_param) / (1024**3)
        
        # Apply gradient checkpointing reduction
        if gradient_checkpointing:
            activation_memory_gb *= 0.3  # Roughly 70% reduction
        
        return activation_memory_gb
    
    def estimate_from_architecture(
        self,
        num_layers: int,
        hidden_size: int,
        num_attention_heads: int,
        vocab_size: int,
        **kwargs
    ) -> EstimationResult:
        """Estimate based on transformer architecture parameters."""
        from .utils import calculate_transformer_params
        
        model_params = calculate_transformer_params(
            num_layers, hidden_size, num_attention_heads, vocab_size
        )
        
        return self.estimate(model_params=model_params, **kwargs)
    
    def estimate_from_huggingface(
        self,
        model_id: str,
        **kwargs
    ) -> EstimationResult:
        """
        Estimate GPU requirements for a Hugging Face model.
        
        Args:
            model_id: Hugging Face model ID (e.g., "meta-llama/Llama-2-7b-hf")
            **kwargs: Additional arguments passed to estimate()
        
        Returns:
            EstimationResult with memory breakdown and GPU count
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        # Get model parameters from Hugging Face
        model_params = self.hf_registry.estimate_model_parameters(model_id)
        if model_params is None:
            raise ValueError(f"Could not determine parameters for model: {model_id}")
        
        return self.estimate(model_params=model_params, **kwargs)
    
    def list_trending_models(self, limit: int = 20, task: Optional[str] = None):
        """
        List trending models from Hugging Face.
        
        Args:
            limit: Maximum number of models to return
            task: Filter by task (e.g., "text-generation")
        
        Returns:
            List of model information
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        return self.hf_registry.list_trending_models(limit=limit, task=task)
    
    def search_models(self, query: str, limit: int = 20, task: Optional[str] = None):
        """
        Search for models on Hugging Face.
        
        Args:
            query: Search query
            limit: Maximum number of models to return
            task: Filter by task
        
        Returns:
            List of model information
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        return self.hf_registry.search_models(query=query, limit=limit, task=task)
    
    def get_popular_models_by_architecture(self, architecture: str, limit: int = 10):
        """
        Get popular models for a specific architecture.
        
        Args:
            architecture: Architecture name (e.g., "llama", "gpt", "bert")
            limit: Maximum number of models to return
        
        Returns:
            List of popular models for the architecture
        """
        if not self.hf_registry:
            raise ValueError("Hugging Face integration not available. Install with: pip install transformers huggingface_hub torch")
        
        return self.hf_registry.get_popular_models_by_architecture(architecture=architecture, limit=limit)