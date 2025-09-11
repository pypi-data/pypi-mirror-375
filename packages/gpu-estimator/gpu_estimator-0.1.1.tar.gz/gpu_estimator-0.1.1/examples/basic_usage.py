#!/usr/bin/env python3
"""
Basic usage examples for the GPU Estimator package.
"""

from gpu_estimator import GPUEstimator
from gpu_estimator.utils import estimate_from_model_name, format_number


def example_basic_estimation():
    """Basic estimation example with custom parameters."""
    print("="*60)
    print("EXAMPLE 1: Basic Estimation")
    print("="*60)
    
    estimator = GPUEstimator()
    
    # Estimate for a 7B parameter model
    result = estimator.estimate(
        model_params=7e9,  # 7 billion parameters
        batch_size=32,
        sequence_length=2048,
        precision="fp16",
        optimizer="adam"
    )
    
    print(f"Model: 7B parameters")
    print(f"Batch size: 32, Sequence length: 2048")
    print(f"Precision: fp16, Optimizer: Adam")
    print(f"\nResults:")
    print(f"  Total memory needed: {result.total_memory_gb:.2f} GB")
    print(f"  Recommended GPUs: {result.num_gpus}")
    print(f"  Memory per GPU: {result.memory_per_gpu_gb:.2f} GB")
    print(f"\nMemory breakdown:")
    print(f"  Model: {result.model_memory_gb:.2f} GB")
    print(f"  Optimizer: {result.optimizer_memory_gb:.2f} GB")
    print(f"  Gradients: {result.gradient_memory_gb:.2f} GB")
    print(f"  Activations: {result.activation_memory_gb:.2f} GB")


def example_predefined_models():
    """Example using predefined model configurations."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Predefined Models")
    print("="*60)
    
    estimator = GPUEstimator()
    models = ["gpt2", "llama-7b", "llama-13b"]
    
    for model_name in models:
        params = estimate_from_model_name(model_name)
        result = estimator.estimate(
            model_params=params,
            batch_size=16,
            sequence_length=2048,
            precision="fp16"
        )
        
        print(f"\n{model_name.upper()}:")
        print(f"  Parameters: {format_number(params)}")
        print(f"  Memory needed: {result.total_memory_gb:.2f} GB")
        print(f"  GPUs needed: {result.num_gpus}")


def example_architecture_estimation():
    """Example using architecture parameters."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Architecture-based Estimation")
    print("="*60)
    
    estimator = GPUEstimator()
    
    # Custom transformer architecture
    result = estimator.estimate_from_architecture(
        num_layers=24,
        hidden_size=2048,
        num_attention_heads=16,
        vocab_size=50000,
        batch_size=8,
        sequence_length=4096,
        precision="fp16"
    )
    
    print("Custom transformer (24 layers, 2048 hidden, 16 heads):")
    print(f"  Memory needed: {result.total_memory_gb:.2f} GB")
    print(f"  GPUs needed: {result.num_gpus}")


def example_optimization_strategies():
    """Example showing different optimization strategies."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Optimization Strategies")
    print("="*60)
    
    estimator = GPUEstimator()
    model_params = 13e9  # 13B model
    
    configs = [
        {"name": "Baseline", "gradient_checkpointing": False, "batch_size": 16},
        {"name": "Gradient Checkpointing", "gradient_checkpointing": True, "batch_size": 16},
        {"name": "Smaller Batch", "gradient_checkpointing": False, "batch_size": 8},
        {"name": "Both Optimizations", "gradient_checkpointing": True, "batch_size": 8},
    ]
    
    print(f"Model: {format_number(model_params)} parameters\n")
    
    for config in configs:
        result = estimator.estimate(
            model_params=model_params,
            batch_size=config["batch_size"],
            sequence_length=2048,
            precision="fp16",
            gradient_checkpointing=config["gradient_checkpointing"]
        )
        
        print(f"{config['name']}:")
        print(f"  Memory: {result.total_memory_gb:.2f} GB")
        print(f"  GPUs: {result.num_gpus}")
        print()


def example_gpu_comparison():
    """Example comparing different GPU types."""
    print("\n" + "="*60)
    print("EXAMPLE 5: GPU Type Comparison")
    print("="*60)
    
    estimator = GPUEstimator()
    model_params = 7e9
    gpu_types = ["V100", "A100", "H100", "RTX4090"]
    
    print(f"Model: {format_number(model_params)} parameters")
    print("Batch size: 16, Sequence length: 2048, Precision: fp16\n")
    
    for gpu_type in gpu_types:
        result = estimator.estimate(
            model_params=model_params,
            batch_size=16,
            sequence_length=2048,
            precision="fp16",
            gpu_type=gpu_type
        )
        
        memory = estimator.gpu_memory_sizes[gpu_type]
        print(f"{gpu_type} ({memory}GB): {result.num_gpus} GPUs needed")


if __name__ == "__main__":
    print("GPU Estimator - Usage Examples")
    print("This script demonstrates various ways to use the GPU estimator.\n")
    
    example_basic_estimation()
    example_predefined_models()
    example_architecture_estimation()
    example_optimization_strategies()
    example_gpu_comparison()
    
    print("\n" + "="*60)
    print("Try the CLI tool:")
    print("  gpu-estimate --model-name llama-7b --batch-size 32")
    print("  gpu-estimate --model-params 175e9 --gpu-type A100")
    print("="*60)