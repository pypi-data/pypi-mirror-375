# GPU Estimator

A Python package for estimating GPU memory requirements and the number of GPUs needed for training machine learning models.

## Features

- **Latest Model Support**: Built-in configs for LLaMA 4, Gemma 3, Qwen 2.5/3, and more
- Estimate GPU memory requirements based on model parameters
- Calculate optimal number of GPUs for training
- Support for different precision types (FP32, FP16, BF16, INT8)
- Account for optimizer states and gradient storage
- Integration with Hugging Face Hub for latest models
- Discover and search trending models
- Support for popular architectures (GPT, LLaMA, BERT, T5, Mistral, Gemma, Qwen, etc.)
- CLI interface for quick estimates
- Detailed memory breakdown and recommendations

## Installation

```bash
pip install gpu-estimator
```


## Quick Start

### Basic Usage
```python
from gpu_estimator import GPUEstimator

estimator = GPUEstimator()

# Estimate for latest models using predefined configs
from gpu_estimator.utils import get_model_config

result = estimator.estimate_from_architecture(
    **get_model_config("qwen2.5-7b"),
    batch_size=8,
    sequence_length=2048,
    precision="fp16"
)

print(f"Memory needed per GPU: {result.memory_per_gpu_gb:.2f} GB")
print(f"Recommended GPUs: {result.num_gpus}")

# Or estimate by parameters for any model size
result = estimator.estimate(
    model_params=7e9,
    batch_size=32,
    sequence_length=2048,
    precision="fp16"
)
```

### Hugging Face Integration

```python
from gpu_estimator import GPUEstimator

estimator = GPUEstimator()

# Estimate directly from Hugging Face model ID
result = estimator.estimate_from_huggingface(
    model_id="meta-llama/Llama-3.2-3B",
    batch_size=4,
    sequence_length=2048,
    precision="fp16",
    gradient_checkpointing=True
)

print(f"Total memory required: {result.total_memory_gb:.2f} GB")
print(f"GPUs needed: {result.num_gpus}")

# Discover trending models
trending = estimator.list_trending_models(limit=10, task="text-generation")
for model in trending:
    print(f"{model.model_id} - {model.downloads:,} downloads")

# Search for specific models
models = estimator.search_models("qwen", limit=5)
for model in models:
    print(f"{model.model_id} - {model.architecture}")
```

## CLI Usage

### Basic Estimation
```bash
# Estimate for any model by parameters
gpu-estimate estimate --model-params 7e9 --batch-size 4 --precision fp16

# Estimate for predefined models (classic)
gpu-estimate estimate --model-name llama-7b --batch-size 8

# Estimate for latest predefined models
gpu-estimate estimate --model-name qwen2.5-7b --batch-size 4 --precision fp16
gpu-estimate estimate --model-name llama3.2-3b --batch-size 16 --gpu-type A100
gpu-estimate estimate --model-name gemma2-9b --batch-size 8 --precision bf16

# Estimate for Hugging Face models
gpu-estimate estimate --huggingface-model meta-llama/Llama-3.2-3B --batch-size 4
gpu-estimate estimate --huggingface-model Qwen/Qwen2.5-7B --batch-size 8
```

### Model Discovery
```bash
# List trending models
gpu-estimate trending --limit 20 --task text-generation

# Search for models
gpu-estimate search "mistral" --limit 10

# Get popular models by architecture
gpu-estimate popular llama --limit 5

# Get model information
gpu-estimate info qwen2.5-7b
```

### Advanced Options
```bash
# With gradient checkpointing and specific GPU
gpu-estimate estimate \
  --huggingface-model meta-llama/Llama-4-Scout-17B \
  --batch-size 8 \
  --seq-length 1024 \
  --precision fp16 \
  --gpu-type A100 \
  --gradient-checkpointing \
  --verbose
```

### Interactive Mode
Launch an interactive session for guided GPU estimation:

```bash
gpu-estimate interactive
```

Features:
- Guided workflows for all estimation tasks
- Model discovery with direct estimation
- Flexible model specification (parameters, names, or HF IDs)
- Step-by-step configuration of training parameters
- Quick estimates from trending model lists

## Supported Models & Architectures

### Hugging Face Models
The package automatically supports any model on Hugging Face Hub by detecting their configuration. Popular architectures include:

| Architecture | Examples | Use Cases |
|-------------|----------|-----------|
| LLaMA/LLaMA2/3/4 | `meta-llama/Llama-2-7b-hf`, `meta-llama/Llama-3.2-3B`, `meta-llama/Llama-4-Scout-17B` | General language modeling, chat |
| GPT | `gpt2`, `microsoft/DialoGPT-large` | Text generation, conversation |
| Mistral | `mistralai/Mistral-7B-v0.1` | Efficient language modeling |
| CodeLlama | `codellama/CodeLlama-7b-Python-hf` | Code generation |
| BERT | `google-bert/bert-base-uncased` | Text classification, NLU |
| T5 | `google-t5/t5-base`, `google/flan-t5-large` | Text-to-text tasks |
| Phi | `microsoft/phi-2` | Small efficient models |
| Gemma/Gemma2/3 | `google/gemma-7b`, `google/gemma-2-9b`, `google/gemma-3-270m` | Google's language models |
| Qwen/Qwen2.5/3 | `Qwen/Qwen-7B`, `Qwen/Qwen2.5-7B`, `Qwen/Qwen3-4B` | Multilingual models |

### Predefined Models
Classic and latest models with known configurations:

**GPT Family:**
- `gpt2`, `gpt2-medium`, `gpt2-large`, `gpt2-xl`, `gpt3`

**LLaMA Family:**
- Original: `llama-7b`, `llama-13b`, `llama-30b`, `llama-65b`  
- LLaMA 2: `llama2-7b`, `llama2-13b`, `llama2-70b`
- LLaMA 3.2: `llama3.2-1b`, `llama3.2-3b`
- LLaMA 3.3: `llama3.3-70b`
- LLaMA 4: `llama4-scout-17b`, `llama4-maverick-17b`
- Code LLaMA: `codellama-7b`, `codellama-13b`, `codellama-34b`

**Mistral Family:**
- `mistral-7b`

**Phi Family:**
- `phi-1.5b`, `phi-2.7b`

**Gemma Family:**
- Original: `gemma-2b`, `gemma-7b`
- Gemma 2: `gemma2-2b`, `gemma2-9b`, `gemma2-27b`
- Gemma 3: `gemma3-270m`

**Qwen Family:**
- Qwen 2.5: `qwen2.5-7b`, `qwen2.5-14b`, `qwen2.5-32b`, `qwen2.5-72b`
- Qwen 3: `qwen3-4b`, `qwen3-30b`, `qwen3-235b`

**Flexible Naming**: Model names support flexible matching. Use `custom-llama-7b`, `my-mistral-7b`, or any name containing a known model identifier.

## GPU Types Supported

| GPU | Memory | Use Case |
|-----|--------|----------|
| H100 | 80 GB | Latest high-performance training |
| A100 | 80 GB | Large model training and inference |
| A40 | 48 GB | Professional workstation training |
| A6000 | 48 GB | Creative and AI workstation |
| L40 | 48 GB | Data center inference |
| L4 | 24 GB | Efficient inference |
| RTX 4090 | 24 GB | Consumer high-end |
| RTX 3090 | 24 GB | Consumer enthusiast |
| V100 | 32 GB | Previous generation training |
| T4 | 16 GB | Cloud inference |