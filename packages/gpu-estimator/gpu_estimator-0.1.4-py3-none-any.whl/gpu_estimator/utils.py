import math
from typing import Dict, Any, Optional


def calculate_transformer_params(
    num_layers: int,
    hidden_size: int,
    num_attention_heads: int,
    vocab_size: int,
    intermediate_size: Optional[int] = None
) -> float:
    """
    Calculate the number of parameters in a transformer model.
    
    Args:
        num_layers: Number of transformer layers
        hidden_size: Hidden dimension size
        num_attention_heads: Number of attention heads
        vocab_size: Vocabulary size
        intermediate_size: FFN intermediate size (defaults to 4 * hidden_size)
    
    Returns:
        Total number of parameters
    """
    if intermediate_size is None:
        intermediate_size = 4 * hidden_size
    
    # Embedding parameters
    embedding_params = vocab_size * hidden_size
    
    # Per-layer parameters
    # Self-attention: Q, K, V projections + output projection
    attention_params = 4 * (hidden_size * hidden_size)
    
    # Feed-forward network
    ffn_params = hidden_size * intermediate_size + intermediate_size * hidden_size
    
    # Layer normalization (2 per layer: pre-attention and pre-ffn)
    ln_params = 2 * hidden_size
    
    layer_params = attention_params + ffn_params + ln_params
    total_layer_params = num_layers * layer_params
    
    # Final layer norm
    final_ln_params = hidden_size
    
    # Output projection (usually shares weights with embedding, but count separately)
    output_params = hidden_size * vocab_size
    
    total_params = embedding_params + total_layer_params + final_ln_params + output_params
    
    return float(total_params)


def calculate_model_params(architecture: str, **kwargs) -> float:
    """
    Calculate model parameters for common architectures.
    
    Args:
        architecture: Model architecture name
        **kwargs: Architecture-specific parameters
    
    Returns:
        Number of parameters
    """
    architecture = architecture.lower()
    
    if architecture in ["gpt", "transformer", "llama"]:
        return calculate_transformer_params(**kwargs)
    elif architecture == "bert":
        return calculate_transformer_params(**kwargs)
    else:
        raise ValueError(f"Unsupported architecture: {architecture}")


def get_model_config(model_name: str) -> Dict[str, Any]:
    """
    Get configuration for well-known models.
    
    Args:
        model_name: Name of the model
    
    Returns:
        Dictionary with model configuration
    """
    configs = {
        "gpt2": {
            "num_layers": 12,
            "hidden_size": 768,
            "num_attention_heads": 12,
            "vocab_size": 50257
        },
        "gpt2-medium": {
            "num_layers": 24,
            "hidden_size": 1024,
            "num_attention_heads": 16,
            "vocab_size": 50257
        },
        "gpt2-large": {
            "num_layers": 36,
            "hidden_size": 1280,
            "num_attention_heads": 20,
            "vocab_size": 50257
        },
        "gpt2-xl": {
            "num_layers": 48,
            "hidden_size": 1600,
            "num_attention_heads": 25,
            "vocab_size": 50257
        },
        "gpt3": {
            "num_layers": 96,
            "hidden_size": 12288,
            "num_attention_heads": 96,
            "vocab_size": 50257
        },
        "llama-7b": {
            "num_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "vocab_size": 32000
        },
        "llama-13b": {
            "num_layers": 40,
            "hidden_size": 5120,
            "num_attention_heads": 40,
            "vocab_size": 32000
        },
        "llama-30b": {
            "num_layers": 60,
            "hidden_size": 6656,
            "num_attention_heads": 52,
            "vocab_size": 32000
        },
        "llama-65b": {
            "num_layers": 80,
            "hidden_size": 8192,
            "num_attention_heads": 64,
            "vocab_size": 32000
        },
        # Llama 2 variants (same as original LLaMA)
        "llama2-7b": {
            "num_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "vocab_size": 32000
        },
        "llama2-13b": {
            "num_layers": 40,
            "hidden_size": 5120,
            "num_attention_heads": 40,
            "vocab_size": 32000
        },
        "llama2-70b": {
            "num_layers": 80,
            "hidden_size": 8192,
            "num_attention_heads": 64,
            "vocab_size": 32000
        },
        # Code Llama variants
        "codellama-7b": {
            "num_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "vocab_size": 32016
        },
        "codellama-13b": {
            "num_layers": 40,
            "hidden_size": 5120,
            "num_attention_heads": 40,
            "vocab_size": 32016
        },
        "codellama-34b": {
            "num_layers": 48,
            "hidden_size": 8192,
            "num_attention_heads": 64,
            "vocab_size": 32016
        },
        # Mistral models
        "mistral-7b": {
            "num_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "vocab_size": 32000
        },
        # Phi models
        "phi-1.5b": {
            "num_layers": 24,
            "hidden_size": 2048,
            "num_attention_heads": 32,
            "vocab_size": 51200
        },
        "phi-2.7b": {
            "num_layers": 32,
            "hidden_size": 2560,
            "num_attention_heads": 32,
            "vocab_size": 51200
        },
        # Gemma models
        "gemma-2b": {
            "num_layers": 18,
            "hidden_size": 2048,
            "num_attention_heads": 8,
            "vocab_size": 256000
        },
        "gemma-7b": {
            "num_layers": 28,
            "hidden_size": 3072,
            "num_attention_heads": 16,
            "vocab_size": 256000
        },
        # Gemma 2 models
        "gemma2-2b": {
            "num_layers": 26,
            "hidden_size": 2304,
            "num_attention_heads": 8,
            "vocab_size": 256000
        },
        "gemma2-9b": {
            "num_layers": 42,
            "hidden_size": 3584,
            "num_attention_heads": 16,
            "vocab_size": 256000
        },
        "gemma2-27b": {
            "num_layers": 46,
            "hidden_size": 4608,
            "num_attention_heads": 32,
            "vocab_size": 256000
        },
        # Gemma 3 models
        "gemma3-270m": {
            "num_layers": 15,
            "hidden_size": 1152,
            "num_attention_heads": 12,
            "vocab_size": 256000
        },
        # Llama 3.2 models
        "llama3.2-1b": {
            "num_layers": 16,
            "hidden_size": 2048,
            "num_attention_heads": 32,
            "vocab_size": 128256
        },
        "llama3.2-3b": {
            "num_layers": 28,
            "hidden_size": 3072,
            "num_attention_heads": 24,
            "vocab_size": 128256
        },
        # Llama 3.3 models
        "llama3.3-70b": {
            "num_layers": 80,
            "hidden_size": 8192,
            "num_attention_heads": 64,
            "vocab_size": 128256
        },
        # Llama 4 models (based on available info)
        "llama4-scout-17b": {
            "num_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "vocab_size": 128256
        },
        "llama4-maverick-17b": {
            "num_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "vocab_size": 128256
        },
        # Qwen 2.5 models (verified configurations)
        "qwen2.5-7b": {
            "num_layers": 28,
            "hidden_size": 3584,
            "num_attention_heads": 28,
            "vocab_size": 152064,
            "intermediate_size": 18944
        },
        "qwen2.5-14b": {
            "num_layers": 48,
            "hidden_size": 5120,
            "num_attention_heads": 40,
            "vocab_size": 152064,
            "intermediate_size": 13824
        },
        "qwen2.5-32b": {
            "num_layers": 64,
            "hidden_size": 5120,
            "num_attention_heads": 40,
            "vocab_size": 152064,
            "intermediate_size": 27648
        },
        "qwen2.5-72b": {
            "num_layers": 80,
            "hidden_size": 8192,
            "num_attention_heads": 64,
            "vocab_size": 152064,
            "intermediate_size": 29568
        },
        # Qwen 3 models (estimated based on patterns)
        "qwen3-4b": {
            "num_layers": 32,
            "hidden_size": 3584,
            "num_attention_heads": 28,
            "vocab_size": 152064,
            "intermediate_size": 18944
        },
        "qwen3-30b": {
            "num_layers": 64,
            "hidden_size": 6144,
            "num_attention_heads": 48,
            "vocab_size": 152064,
            "intermediate_size": 32768
        },
        "qwen3-235b": {
            "num_layers": 88,
            "hidden_size": 12288,
            "num_attention_heads": 96,
            "vocab_size": 152064,
            "intermediate_size": 49152
        }
    }
    
    model_name_lower = model_name.lower()
    
    # First try exact match
    if model_name_lower in configs:
        return configs[model_name_lower]
    
    # Try flexible matching - look for base model names
    for config_name in configs:
        if config_name in model_name_lower:
            return configs[config_name]
    
    # If no match found, suggest similar models
    similar = [name for name in configs.keys() if any(part in model_name_lower for part in name.split('-'))]
    if similar:
        raise ValueError(f"Unknown model: {model_name}. Did you mean one of: {similar}? Available: {list(configs.keys())}")
    else:
        raise ValueError(f"Unknown model: {model_name}. Available: {list(configs.keys())}")


def estimate_from_model_name(model_name: str) -> float:
    """
    Estimate parameters for a well-known model by name.
    
    Args:
        model_name: Name of the model
    
    Returns:
        Number of parameters
    """
    config = get_model_config(model_name)
    return calculate_transformer_params(**config)


def bytes_to_gb(bytes_val: float) -> float:
    """Convert bytes to gigabytes."""
    return bytes_val / (1024**3)


def gb_to_bytes(gb_val: float) -> float:
    """Convert gigabytes to bytes."""
    return gb_val * (1024**3)


def format_number(num: float, suffix: str = "") -> str:
    """Format large numbers with appropriate suffixes."""
    if num >= 1e12:
        return f"{num/1e12:.1f}T{suffix}"
    elif num >= 1e9:
        return f"{num/1e9:.1f}B{suffix}"
    elif num >= 1e6:
        return f"{num/1e6:.1f}M{suffix}"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K{suffix}"
    else:
        return f"{num:.1f}{suffix}"