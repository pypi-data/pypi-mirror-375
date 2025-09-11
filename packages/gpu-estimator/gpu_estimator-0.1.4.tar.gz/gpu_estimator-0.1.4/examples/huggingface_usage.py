#!/usr/bin/env python3
"""
Example usage of GPU Estimator with Hugging Face models.

This script demonstrates how to:
1. Estimate GPU requirements for specific Hugging Face models
2. Search and discover trending models
3. Compare different models and configurations
"""

from gpu_estimator import GPUEstimator


def main():
    print("🚀 GPU Estimator - Hugging Face Integration Example")
    print("=" * 60)
    
    estimator = GPUEstimator()
    
    # Check if Hugging Face integration is available
    if not estimator.hf_registry:
        print("❌ Hugging Face integration not available.")
        print("Install with: pip install transformers huggingface_hub torch")
        return
    
    print("✅ Hugging Face integration available!")
    print()
    
    # Example 1: Estimate GPU requirements for a specific model
    print("📊 Example 1: Estimate GPU requirements for Llama 2 7B")
    print("-" * 50)
    
    try:
        model_id = "meta-llama/Llama-2-7b-hf"
        result = estimator.estimate_from_huggingface(
            model_id=model_id,
            batch_size=4,
            sequence_length=2048,
            precision="fp16",
            gradient_checkpointing=True
        )
        
        print(f"Model: {model_id}")
        print(f"Total Memory Required: {result.total_memory_gb:.2f} GB")
        print(f"Number of GPUs (A100): {result.num_gpus}")
        print(f"Memory per GPU: {result.memory_per_gpu_gb:.2f} GB")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 2: Search for trending models
    print("🔥 Example 2: Find trending text generation models")
    print("-" * 50)
    
    try:
        trending_models = estimator.list_trending_models(
            limit=5, 
            task="text-generation"
        )
        
        for i, model in enumerate(trending_models, 1):
            print(f"{i}. {model.model_id}")
            print(f"   Architecture: {model.architecture}")
            print(f"   Downloads: {model.downloads:,}")
            if model.parameters:
                params_str = f"{model.parameters/1e9:.1f}B" if model.parameters >= 1e9 else f"{model.parameters/1e6:.1f}M"
                print(f"   Parameters: {params_str}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 3: Search for specific models
    print("🔍 Example 3: Search for Mistral models")
    print("-" * 50)
    
    try:
        mistral_models = estimator.search_models(
            query="mistral",
            limit=3
        )
        
        for model in mistral_models:
            print(f"• {model.model_id}")
            print(f"  Downloads: {model.downloads:,}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 4: Compare different model configurations
    print("⚖️  Example 4: Compare different configurations")
    print("-" * 50)
    
    model_configs = [
        ("fp32", 1, False),
        ("fp16", 1, False),
        ("fp16", 4, True),
    ]
    
    try:
        model_id = "microsoft/DialoGPT-medium"  # Smaller model for demo
        
        print(f"Model: {model_id}")
        print()
        
        for precision, batch_size, grad_checkpoint in model_configs:
            result = estimator.estimate_from_huggingface(
                model_id=model_id,
                batch_size=batch_size,
                precision=precision,
                gradient_checkpointing=grad_checkpoint
            )
            
            config_desc = f"{precision}, batch={batch_size}, grad_checkpoint={grad_checkpoint}"
            print(f"Config: {config_desc}")
            print(f"  Memory: {result.total_memory_gb:.2f} GB")
            print(f"  GPUs needed: {result.num_gpus}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 5: Get popular models by architecture
    print("⭐ Example 5: Popular BERT models")
    print("-" * 50)
    
    try:
        bert_models = estimator.get_popular_models_by_architecture(
            architecture="bert",
            limit=3
        )
        
        for model in bert_models:
            print(f"• {model.model_id}")
            print(f"  Downloads: {model.downloads:,}")
            print(f"  Likes: {model.likes:,}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()