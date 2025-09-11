import click
from .estimator import GPUEstimator
from .utils import estimate_from_model_name, get_model_config, format_number


def display_results(result, model_display_name, batch_size, seq_length, precision, 
                   optimizer, gradient_checkpointing, gpu_type, gpu_memory, 
                   estimator, verbose):
    """Display estimation results."""
    model_params = result.model_memory_gb * (1024**3) / (2 if precision in ['fp16', 'bf16'] else 4)
    
    click.echo("\n" + "="*50)
    click.echo("GPU ESTIMATION RESULTS")
    click.echo("="*50)
    
    if model_display_name:
        click.echo(f"Model: {model_display_name}")
    click.echo(f"Model Parameters: {format_number(model_params)}")
    click.echo(f"Batch Size: {batch_size}")
    click.echo(f"Sequence Length: {seq_length}")
    click.echo(f"Precision: {precision}")
    click.echo(f"Optimizer: {optimizer}")
    if gradient_checkpointing:
        click.echo("Gradient Checkpointing: Enabled")
    
    click.echo("\n" + "-"*30)
    click.echo("MEMORY BREAKDOWN")
    click.echo("-"*30)
    
    if verbose:
        click.echo(f"Model Memory:      {result.model_memory_gb:.2f} GB")
        click.echo(f"Optimizer Memory:  {result.optimizer_memory_gb:.2f} GB")
        click.echo(f"Gradient Memory:   {result.gradient_memory_gb:.2f} GB")
        click.echo(f"Activation Memory: {result.activation_memory_gb:.2f} GB")
        click.echo(f"Total Memory:      {result.total_memory_gb:.2f} GB")
    else:
        click.echo(f"Total Memory Required: {result.total_memory_gb:.2f} GB")
    
    click.echo("\n" + "-"*30)
    click.echo("GPU REQUIREMENTS")
    click.echo("-"*30)
    
    if gpu_type:
        gpu_desc = f"{gpu_type} ({int(gpu_memory) if gpu_memory else estimator.gpu_memory_sizes[gpu_type]}GB)"
    else:
        gpu_desc = f"{int(gpu_memory) if gpu_memory else 'A100 (80)'}GB"
    click.echo(f"GPU Type: {gpu_desc}")
    click.echo(f"Number of GPUs Needed: {result.num_gpus}")
    click.echo(f"Memory per GPU: {result.memory_per_gpu_gb:.2f} GB")
    click.echo(f"Efficiency Ratio: {result.efficiency_ratio:.1%}")
    
    # Recommendations
    if result.num_gpus > 8:
        click.echo(f"\n⚠️  Warning: {result.num_gpus} GPUs required. Consider:")
        click.echo("   - Using gradient checkpointing")
        click.echo("   - Reducing batch size")
        click.echo("   - Using model parallelism")
        click.echo("   - Applying quantization techniques")


@click.command()
@click.option('--model-params', type=float, help='Number of model parameters (e.g., 7e9 for 7B)')
@click.option('--model-name', type=str, help='Pre-defined model name (e.g., llama-7b, gpt2)')
@click.option('--huggingface-model', type=str, help='Hugging Face model ID (e.g., meta-llama/Llama-2-7b-hf)')
@click.option('--batch-size', default=1, help='Training batch size')
@click.option('--seq-length', default=2048, help='Input sequence length')
@click.option('--precision', default='fp16', type=click.Choice(['fp32', 'fp16', 'bf16', 'int8']))
@click.option('--optimizer', default='adam', type=click.Choice(['adam', 'adamw', 'sgd']))
@click.option('--gpu-memory', type=float, help='Available GPU memory in GB')
@click.option('--gpu-type', type=click.Choice(['V100', 'A100', 'H100', 'RTX3090', 'RTX4090', 'T4', 'L4', 'L40', 'A40', 'A6000']))
@click.option('--gradient-checkpointing', is_flag=True, help='Enable gradient checkpointing')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed breakdown')
def main(model_params, model_name, huggingface_model, batch_size, seq_length, precision, optimizer, 
         gpu_memory, gpu_type, gradient_checkpointing, verbose):
    """Estimate GPU requirements for training machine learning models."""
    
    estimator = GPUEstimator()
    
    # Determine model parameters
    model_display_name = None
    if huggingface_model:
        try:
            if verbose:
                click.echo(f"Loading Hugging Face model: {huggingface_model}")
            
            result = estimator.estimate_from_huggingface(
                model_id=huggingface_model,
                batch_size=batch_size,
                sequence_length=seq_length,
                precision=precision,
                optimizer=optimizer,
                gpu_memory_gb=gpu_memory,
                gpu_type=gpu_type,
                gradient_checkpointing=gradient_checkpointing
            )
            model_display_name = huggingface_model
            
            # Display results for HF model and return
            display_results(result, model_display_name, batch_size, seq_length, precision, 
                          optimizer, gradient_checkpointing, gpu_type, gpu_memory, 
                          estimator, verbose)
            return
            
        except Exception as e:
            click.echo(f"Error loading Hugging Face model '{huggingface_model}': {e}", err=True)
            return
    elif model_name:
        try:
            model_params = estimate_from_model_name(model_name)
            model_display_name = model_name
            if verbose:
                config = get_model_config(model_name)
                click.echo(f"Model: {model_name}")
                click.echo(f"Configuration: {config}")
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            return
    elif model_params is None:
        click.echo("Error: Must specify --model-params, --model-name, or --huggingface-model", err=True)
        return
    
    # Run estimation
    try:
        result = estimator.estimate(
            model_params=model_params,
            batch_size=batch_size,
            sequence_length=seq_length,
            precision=precision,
            optimizer=optimizer,
            gpu_memory_gb=gpu_memory,
            gpu_type=gpu_type,
            gradient_checkpointing=gradient_checkpointing
        )
        
        # Display results
        display_results(result, model_display_name, batch_size, seq_length, precision, 
                       optimizer, gradient_checkpointing, gpu_type, gpu_memory, 
                       estimator, verbose)
        
    except Exception as e:
        click.echo(f"Error during estimation: {e}", err=True)


@click.command()
@click.argument('model_name')
def model_info(model_name):
    """Show information about a pre-defined model."""
    try:
        config = get_model_config(model_name)
        params = estimate_from_model_name(model_name)
        
        click.echo(f"\nModel: {model_name}")
        click.echo("-" * (len(model_name) + 7))
        click.echo(f"Parameters: {format_number(params)}")
        click.echo(f"Layers: {config['num_layers']}")
        click.echo(f"Hidden Size: {config['hidden_size']}")
        click.echo(f"Attention Heads: {config['num_attention_heads']}")
        click.echo(f"Vocabulary Size: {config['vocab_size']}")
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@click.command()
@click.option('--limit', default=20, help='Maximum number of models to show')
@click.option('--task', type=str, help='Filter by task (e.g., text-generation)')
def trending(limit, task):
    """List trending models from Hugging Face."""
    try:
        estimator = GPUEstimator()
        models = estimator.list_trending_models(limit=limit, task=task)
        
        if not models:
            click.echo("No models found or Hugging Face integration not available.")
            return
        
        click.echo(f"\n🔥 Top {len(models)} Trending Models" + (f" for {task}" if task else ""))
        click.echo("=" * 60)
        
        for i, model in enumerate(models, 1):
            click.echo(f"{i:2d}. {model.model_id}")
            click.echo(f"    Architecture: {model.architecture}")
            click.echo(f"    Downloads: {model.downloads:,}")
            click.echo(f"    Likes: {model.likes:,}")
            if model.parameters:
                click.echo(f"    Parameters: {format_number(model.parameters)}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error listing trending models: {e}", err=True)


@click.command()
@click.argument('query')
@click.option('--limit', default=10, help='Maximum number of models to show')
@click.option('--task', type=str, help='Filter by task')
def search(query, limit, task):
    """Search for models on Hugging Face."""
    try:
        estimator = GPUEstimator()
        models = estimator.search_models(query=query, limit=limit, task=task)
        
        if not models:
            click.echo(f"No models found for query: '{query}'")
            return
        
        click.echo(f"\n🔍 Search Results for '{query}'" + (f" (task: {task})" if task else ""))
        click.echo("=" * 60)
        
        for i, model in enumerate(models, 1):
            click.echo(f"{i:2d}. {model.model_id}")
            click.echo(f"    Architecture: {model.architecture}")
            click.echo(f"    Downloads: {model.downloads:,}")
            if model.parameters:
                click.echo(f"    Parameters: {format_number(model.parameters)}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error searching models: {e}", err=True)


@click.command()
@click.argument('architecture')
@click.option('--limit', default=10, help='Maximum number of models to show')
def popular(architecture, limit):
    """Get popular models for a specific architecture (e.g., llama, gpt, bert)."""
    try:
        estimator = GPUEstimator()
        models = estimator.get_popular_models_by_architecture(architecture=architecture, limit=limit)
        
        if not models:
            click.echo(f"No models found for architecture: '{architecture}'")
            return
        
        click.echo(f"\n⭐ Popular {architecture.upper()} Models")
        click.echo("=" * 60)
        
        for i, model in enumerate(models, 1):
            click.echo(f"{i:2d}. {model.model_id}")
            click.echo(f"    Downloads: {model.downloads:,}")
            click.echo(f"    Likes: {model.likes:,}")
            if model.parameters:
                click.echo(f"    Parameters: {format_number(model.parameters)}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error getting popular models: {e}", err=True)


@click.group()
def cli():
    """GPU Estimator - Estimate GPU requirements for ML training."""
    pass


# Interactive mode functions
@click.command()
def interactive():
    """Interactive mode for GPU estimation."""
    click.echo("🚀 GPU Estimator - Interactive Mode")
    click.echo("=" * 50)
    
    estimator = GPUEstimator()
    
    while True:
        click.echo("\nChoose an option:")
        click.echo("1. Estimate GPU requirements")
        click.echo("2. Discover trending models")
        click.echo("3. Search for models")
        click.echo("4. Get popular models by architecture")
        click.echo("5. Get model info")
        click.echo("6. Exit")
        
        try:
            choice = click.prompt("Enter your choice (1-6)", type=int)
        except (ValueError, click.Abort):
            click.echo("Invalid choice. Please enter a number 1-6.")
            continue
        
        if choice == 1:
            interactive_estimate(estimator)
        elif choice == 2:
            interactive_trending(estimator)
        elif choice == 3:
            interactive_search(estimator)
        elif choice == 4:
            interactive_popular(estimator)
        elif choice == 5:
            interactive_model_info()
        elif choice == 6:
            click.echo("👋 Goodbye!")
            break
        else:
            click.echo("Invalid choice. Please enter a number 1-6.")


def interactive_estimate(estimator):
    """Interactive estimation workflow."""
    click.echo("\n📊 GPU Estimation")
    click.echo("-" * 30)
    
    # Choose model specification method
    click.echo("\nHow would you like to specify the model?")
    click.echo("1. By parameter count")
    click.echo("2. By model name")
    click.echo("3. By Hugging Face model ID")
    
    method = click.prompt("Enter choice (1-3)", type=int, default=1)
    
    model_params = None
    model_name = None
    hf_model = None
    
    if method == 1:
        model_params = click.prompt("Model parameters (e.g., 7e9 for 7B)", type=float)
    elif method == 2:
        click.echo(f"\nAvailable models: gpt2, llama-7b, llama-13b, llama-30b, llama2-7b, mistral-7b, phi-1.5b, gemma-7b")
        model_name = click.prompt("Model name")
    elif method == 3:
        if not estimator.hf_registry:
            click.echo("❌ Hugging Face integration not available. Please install: pip install transformers huggingface_hub torch")
            return
        hf_model = click.prompt("Hugging Face model ID (e.g., microsoft/DialoGPT-medium)")
    else:
        click.echo("Invalid choice.")
        return
    
    # Get training parameters
    batch_size = click.prompt("Batch size", type=int, default=1)
    seq_length = click.prompt("Sequence length", type=int, default=2048)
    precision = click.prompt("Precision", type=click.Choice(['fp32', 'fp16', 'bf16', 'int8']), default='fp16')
    optimizer = click.prompt("Optimizer", type=click.Choice(['adam', 'adamw', 'sgd']), default='adam')
    
    # GPU configuration
    click.echo(f"\nAvailable GPU types: V100, A100, H100, RTX3090, RTX4090, T4, L4, L40, A40, A6000")
    gpu_type = click.prompt("GPU type (or press Enter for A100)", default="A100")
    if gpu_type not in estimator.gpu_memory_sizes:
        gpu_memory = click.prompt("GPU memory in GB", type=float, default=80.0)
        gpu_type = None
    else:
        gpu_memory = None
    
    grad_checkpoint = click.confirm("Enable gradient checkpointing?", default=False)
    verbose = click.confirm("Show detailed breakdown?", default=True)
    
    # Run estimation
    try:
        if model_params:
            result = estimator.estimate(
                model_params=model_params,
                batch_size=batch_size,
                sequence_length=seq_length,
                precision=precision,
                optimizer=optimizer,
                gpu_memory_gb=gpu_memory,
                gpu_type=gpu_type,
                gradient_checkpointing=grad_checkpoint
            )
            display_name = f"{model_params:.1e} parameters"
        elif model_name:
            result = estimator.estimate_from_architecture(
                **get_model_config(model_name),
                batch_size=batch_size,
                sequence_length=seq_length,
                precision=precision,
                optimizer=optimizer,
                gpu_memory_gb=gpu_memory,
                gpu_type=gpu_type,
                gradient_checkpointing=grad_checkpoint
            )
            display_name = model_name
        elif hf_model:
            result = estimator.estimate_from_huggingface(
                model_id=hf_model,
                batch_size=batch_size,
                sequence_length=seq_length,
                precision=precision,
                optimizer=optimizer,
                gpu_memory_gb=gpu_memory,
                gpu_type=gpu_type,
                gradient_checkpointing=grad_checkpoint
            )
            display_name = hf_model
        
        display_results(result, display_name, batch_size, seq_length, precision, 
                       optimizer, grad_checkpoint, gpu_type, gpu_memory, 
                       estimator, verbose)
                       
    except Exception as e:
        click.echo(f"❌ Error: {e}")


def interactive_trending(estimator):
    """Interactive trending models workflow."""
    click.echo("\n🔥 Trending Models")
    click.echo("-" * 30)
    
    if not estimator.hf_registry:
        click.echo("❌ Hugging Face integration not available. Please install: pip install transformers huggingface_hub torch")
        return
    
    limit = click.prompt("Number of models to show", type=int, default=10)
    task = click.prompt("Filter by task (or press Enter for all)", default="", show_default=False)
    task = task if task else None
    
    try:
        models = estimator.list_trending_models(limit=limit, task=task)
        
        if not models:
            click.echo("No models found.")
            return
        
        click.echo(f"\n🔥 Top {len(models)} Trending Models" + (f" for {task}" if task else ""))
        click.echo("=" * 60)
        
        for i, model in enumerate(models, 1):
            click.echo(f"{i:2d}. {model.model_id}")
            click.echo(f"    Architecture: {model.architecture}")
            click.echo(f"    Downloads: {model.downloads:,}")
            click.echo(f"    Likes: {model.likes:,}")
            if model.parameters:
                click.echo(f"    Parameters: {format_number(model.parameters)}")
            click.echo()
            
        # Offer to estimate one of the models
        if click.confirm("Would you like to estimate GPU requirements for one of these models?"):
            try:
                choice = click.prompt("Enter model number", type=int)
                if 1 <= choice <= len(models):
                    selected_model = models[choice - 1]
                    click.echo(f"\nSelected: {selected_model.model_id}")
                    
                    # Quick estimation with defaults
                    batch_size = click.prompt("Batch size", type=int, default=4)
                    precision = click.prompt("Precision", type=click.Choice(['fp32', 'fp16', 'bf16']), default='fp16')
                    
                    result = estimator.estimate_from_huggingface(
                        model_id=selected_model.model_id,
                        batch_size=batch_size,
                        precision=precision
                    )
                    
                    click.echo(f"\n📊 Quick Estimation for {selected_model.model_id}")
                    click.echo(f"Total Memory: {result.total_memory_gb:.2f} GB")
                    click.echo(f"GPUs needed (A100): {result.num_gpus}")
                    
            except Exception as e:
                click.echo(f"❌ Error: {e}")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}")


def interactive_search(estimator):
    """Interactive search workflow."""
    click.echo("\n🔍 Search Models")
    click.echo("-" * 30)
    
    if not estimator.hf_registry:
        click.echo("❌ Hugging Face integration not available. Please install: pip install transformers huggingface_hub torch")
        return
    
    query = click.prompt("Search query")
    limit = click.prompt("Number of results", type=int, default=10)
    
    try:
        models = estimator.search_models(query=query, limit=limit)
        
        if not models:
            click.echo(f"No models found for '{query}'.")
            return
        
        click.echo(f"\n🔍 Search Results for '{query}'")
        click.echo("=" * 60)
        
        for i, model in enumerate(models, 1):
            click.echo(f"{i:2d}. {model.model_id}")
            click.echo(f"    Architecture: {model.architecture}")
            click.echo(f"    Downloads: {model.downloads:,}")
            if model.parameters:
                click.echo(f"    Parameters: {format_number(model.parameters)}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


def interactive_popular(estimator):
    """Interactive popular models workflow."""
    click.echo("\n⭐ Popular Models by Architecture")
    click.echo("-" * 30)
    
    if not estimator.hf_registry:
        click.echo("❌ Hugging Face integration not available. Please install: pip install transformers huggingface_hub torch")
        return
    
    architectures = list(estimator.hf_registry.model_architectures.keys())
    click.echo(f"Available architectures: {', '.join(architectures)}")
    
    architecture = click.prompt("Architecture")
    limit = click.prompt("Number of models", type=int, default=10)
    
    try:
        models = estimator.get_popular_models_by_architecture(architecture=architecture, limit=limit)
        
        if not models:
            click.echo(f"No models found for architecture '{architecture}'.")
            return
        
        click.echo(f"\n⭐ Popular {architecture.upper()} Models")
        click.echo("=" * 60)
        
        for i, model in enumerate(models, 1):
            click.echo(f"{i:2d}. {model.model_id}")
            click.echo(f"    Downloads: {model.downloads:,}")
            click.echo(f"    Likes: {model.likes:,}")
            if model.parameters:
                click.echo(f"    Parameters: {format_number(model.parameters)}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")


def interactive_model_info():
    """Interactive model info workflow."""
    click.echo("\n📋 Model Information")
    click.echo("-" * 30)
    
    available_models = ['gpt2', 'gpt2-medium', 'gpt2-large', 'gpt2-xl', 'gpt3',
                       'llama-7b', 'llama-13b', 'llama-30b', 'llama-65b',
                       'llama2-7b', 'llama2-13b', 'llama2-70b',
                       'codellama-7b', 'codellama-13b', 'codellama-34b',
                       'mistral-7b', 'phi-1.5b', 'phi-2.7b', 'gemma-2b', 'gemma-7b']
    
    click.echo(f"Available models: {', '.join(available_models)}")
    model_name = click.prompt("Model name")
    
    try:
        config = get_model_config(model_name)
        params = estimate_from_model_name(model_name)
        
        click.echo(f"\n📋 {model_name}")
        click.echo("-" * (len(model_name) + 3))
        click.echo(f"Parameters: {format_number(params)}")
        click.echo(f"Layers: {config['num_layers']}")
        click.echo(f"Hidden Size: {config['hidden_size']}")
        click.echo(f"Attention Heads: {config['num_attention_heads']}")
        click.echo(f"Vocabulary Size: {config['vocab_size']:,}")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}")


# Add commands to the group
cli.add_command(main, name="estimate")
cli.add_command(model_info, name="info")
cli.add_command(trending)
cli.add_command(search)
cli.add_command(popular)
cli.add_command(interactive)


if __name__ == '__main__':
    cli()