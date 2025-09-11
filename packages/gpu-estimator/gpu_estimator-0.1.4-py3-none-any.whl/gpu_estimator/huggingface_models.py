"""Hugging Face model integration for GPU estimation."""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import warnings

try:
    from transformers import AutoConfig
    from huggingface_hub import HfApi
    from huggingface_hub.hf_api import ModelInfo
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    ModelInfo = None
    warnings.warn(
        "Hugging Face libraries not available. Install with: pip install transformers huggingface_hub torch",
        UserWarning
    )

from .utils import calculate_transformer_params


@dataclass
class HFModelInfo:
    """Information about a Hugging Face model."""
    model_id: str
    model_name: str
    downloads: int
    likes: int
    created_at: str
    updated_at: str
    architecture: str
    parameters: Optional[float] = None
    config: Optional[Dict[str, Any]] = None


class HuggingFaceModelRegistry:
    """Registry for discovering and managing Hugging Face models."""
    
    def __init__(self):
        if not HF_AVAILABLE:
            raise ImportError("Hugging Face libraries are required. Install with: pip install transformers huggingface_hub torch")
        
        self.api = HfApi()
        self.logger = logging.getLogger(__name__)
        
        # Cache for model configs
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        
        # Popular model families and their architectures
        self.model_architectures = {
            "gpt": ["gpt2", "gpt-j", "gpt-neo", "gpt-neox", "codegen"],
            "llama": ["llama", "llama2", "llama3", "llama3.2", "llama3.3", "llama4", "code-llama", "alpaca", "vicuna"],
            "bert": ["bert", "roberta", "distilbert", "electra"],
            "t5": ["t5", "flan-t5", "ul2"],
            "mistral": ["mistral", "mixtral"],
            "gemma": ["gemma", "gemma2", "gemma3"],
            "qwen": ["qwen", "qwen2", "qwen2.5", "qwen3"],
            "phi": ["phi", "phi-2", "phi-3"],
            "falcon": ["falcon"],
            "mpt": ["mpt"],
            "bloom": ["bloom"],
            "opt": ["opt"],
            "stablelm": ["stablelm"],
            "starcoder": ["starcoder", "starcoderbase"],
        }

    def list_trending_models(
        self, 
        limit: int = 50,
        task: Optional[str] = None,
        library: str = "transformers"
    ) -> List[HFModelInfo]:
        """
        List trending models from Hugging Face Hub.
        
        Args:
            limit: Maximum number of models to return
            task: Filter by task (e.g., "text-generation", "text-classification")
            library: Filter by library (default: "transformers")
        
        Returns:
            List of HFModelInfo objects
        """
        try:
            models = self.api.list_models(
                limit=limit,
                library=library,
                task=task,
                sort="downloads",
                direction=-1  # Descending order
            )
            
            model_infos = []
            for model in models:
                if hasattr(model, 'modelId'):
                    model_info = self._create_model_info(model)
                    if model_info:
                        model_infos.append(model_info)
            
            return model_infos
            
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []

    def search_models(
        self, 
        query: str, 
        limit: int = 20,
        task: Optional[str] = None
    ) -> List[HFModelInfo]:
        """
        Search for models by query.
        
        Args:
            query: Search query
            limit: Maximum number of models to return
            task: Filter by task
        
        Returns:
            List of matching HFModelInfo objects
        """
        try:
            models = self.api.list_models(
                search=query,
                limit=limit,
                library="transformers",
                task=task,
                sort="downloads",
                direction=-1
            )
            
            model_infos = []
            for model in models:
                if hasattr(model, 'modelId'):
                    model_info = self._create_model_info(model)
                    if model_info:
                        model_infos.append(model_info)
            
            return model_infos
            
        except Exception as e:
            self.logger.error(f"Error searching models: {e}")
            return []

    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific model.
        
        Args:
            model_id: Hugging Face model ID
        
        Returns:
            Model configuration dictionary or None if failed
        """
        if model_id in self._config_cache:
            return self._config_cache[model_id]
        
        try:
            config = AutoConfig.from_pretrained(model_id, trust_remote_code=False)
            config_dict = config.to_dict()
            
            # Cache the configuration
            self._config_cache[model_id] = config_dict
            
            return config_dict
            
        except Exception as e:
            self.logger.error(f"Error loading config for {model_id}: {e}")
            return None

    def estimate_model_parameters(self, model_id: str) -> Optional[float]:
        """
        Estimate the number of parameters for a model.
        
        Args:
            model_id: Hugging Face model ID
        
        Returns:
            Estimated number of parameters or None if failed
        """
        config = self.get_model_config(model_id)
        if not config:
            return None
        
        try:
            # Try to get parameter count from config
            if "num_parameters" in config:
                return float(config["num_parameters"])
            
            # Estimate based on architecture
            architecture = config.get("architectures", [])
            if not architecture:
                architecture = [config.get("model_type", "").lower()]
            
            arch_name = architecture[0].lower() if architecture else ""
            
            # Common transformer architectures
            if any(arch in arch_name for arch in ["gpt", "llama", "mistral", "phi", "gemma", "qwen"]):
                return self._estimate_transformer_params(config)
            elif "bert" in arch_name or "roberta" in arch_name:
                return self._estimate_transformer_params(config, is_encoder_only=True)
            elif "t5" in arch_name:
                return self._estimate_t5_params(config)
            else:
                # Fallback to transformer estimation
                return self._estimate_transformer_params(config)
                
        except Exception as e:
            self.logger.error(f"Error estimating parameters for {model_id}: {e}")
            return None

    def _create_model_info(self, model) -> Optional[HFModelInfo]:
        """Create HFModelInfo from ModelInfo object."""
        try:
            # Extract architecture from tags or model name
            architecture = "unknown"
            if hasattr(model, 'tags') and model.tags:
                for tag in model.tags:
                    for arch_family, arch_types in self.model_architectures.items():
                        if any(arch_type in tag.lower() for arch_type in arch_types):
                            architecture = arch_family
                            break
                    if architecture != "unknown":
                        break
            
            # If still unknown, try to infer from model name
            if architecture == "unknown":
                model_name_lower = model.modelId.lower()
                for arch_family, arch_types in self.model_architectures.items():
                    if any(arch_type in model_name_lower for arch_type in arch_types):
                        architecture = arch_family
                        break
            
            return HFModelInfo(
                model_id=model.modelId,
                model_name=model.modelId.split('/')[-1],
                downloads=getattr(model, 'downloads', 0) or 0,
                likes=getattr(model, 'likes', 0) or 0,
                created_at=str(getattr(model, 'createdAt', '')),
                updated_at=str(getattr(model, 'lastModified', '')),
                architecture=architecture
            )
            
        except Exception as e:
            self.logger.error(f"Error creating model info: {e}")
            return None

    def _estimate_transformer_params(self, config: Dict[str, Any], is_encoder_only: bool = False) -> float:
        """Estimate parameters for transformer models."""
        try:
            # Extract common configuration parameters
            hidden_size = config.get("hidden_size", config.get("d_model", 768))
            num_layers = config.get("num_hidden_layers", config.get("n_layer", config.get("num_layers", 12)))
            num_attention_heads = config.get("num_attention_heads", config.get("n_head", 12))
            vocab_size = config.get("vocab_size", 50257)
            intermediate_size = config.get("intermediate_size", config.get("d_ff", 4 * hidden_size))
            
            params = calculate_transformer_params(
                num_layers=num_layers,
                hidden_size=hidden_size,
                num_attention_heads=num_attention_heads,
                vocab_size=vocab_size,
                intermediate_size=intermediate_size
            )
            
            # For encoder-only models (like BERT), don't count output projection
            if is_encoder_only:
                params -= vocab_size * hidden_size
            
            return params
            
        except Exception as e:
            self.logger.error(f"Error estimating transformer parameters: {e}")
            return 0.0

    def _estimate_t5_params(self, config: Dict[str, Any]) -> float:
        """Estimate parameters for T5-style encoder-decoder models."""
        try:
            # T5 has shared embeddings and separate encoder/decoder
            hidden_size = config.get("d_model", 768)
            encoder_layers = config.get("num_layers", 12)
            decoder_layers = config.get("num_decoder_layers", encoder_layers)
            num_attention_heads = config.get("num_heads", 12)
            vocab_size = config.get("vocab_size", 32128)
            d_ff = config.get("d_ff", 4 * hidden_size)
            
            # Shared embeddings
            embedding_params = vocab_size * hidden_size
            
            # Encoder
            encoder_params = calculate_transformer_params(
                num_layers=encoder_layers,
                hidden_size=hidden_size,
                num_attention_heads=num_attention_heads,
                vocab_size=0,  # No embedding/output layers
                intermediate_size=d_ff
            )
            
            # Decoder (has cross-attention, so more parameters)
            decoder_params = calculate_transformer_params(
                num_layers=decoder_layers,
                hidden_size=hidden_size,
                num_attention_heads=num_attention_heads,
                vocab_size=0,  # No embedding/output layers
                intermediate_size=d_ff
            )
            
            # Add cross-attention parameters for decoder
            cross_attention_params = decoder_layers * hidden_size * hidden_size * 2  # K, V projections
            
            # Output projection
            output_params = hidden_size * vocab_size
            
            total_params = embedding_params + encoder_params + decoder_params + cross_attention_params + output_params
            
            return float(total_params)
            
        except Exception as e:
            self.logger.error(f"Error estimating T5 parameters: {e}")
            return 0.0

    def get_popular_models_by_architecture(self, architecture: str, limit: int = 10) -> List[HFModelInfo]:
        """
        Get popular models for a specific architecture.
        
        Args:
            architecture: Architecture name (e.g., "llama", "gpt", "bert")
            limit: Maximum number of models to return
        
        Returns:
            List of popular models for the architecture
        """
        if architecture.lower() not in self.model_architectures:
            return []
        
        arch_types = self.model_architectures[architecture.lower()]
        all_models = []
        
        for arch_type in arch_types:
            models = self.search_models(arch_type, limit=limit//len(arch_types) + 1)
            all_models.extend(models)
        
        # Sort by downloads and return top models
        all_models.sort(key=lambda x: x.downloads, reverse=True)
        return all_models[:limit]

    def get_latest_models(self, limit: int = 20, days: int = 30) -> List[HFModelInfo]:
        """
        Get recently updated models.
        
        Args:
            limit: Maximum number of models to return
            days: Look for models updated within this many days
        
        Returns:
            List of recently updated models
        """
        try:
            models = self.api.list_models(
                limit=limit * 2,  # Get more to filter by date
                library="transformers",
                sort="lastModified",
                direction=-1
            )
            
            model_infos = []
            for model in models:
                if hasattr(model, 'modelId'):
                    model_info = self._create_model_info(model)
                    if model_info:
                        model_infos.append(model_info)
                        if len(model_infos) >= limit:
                            break
            
            return model_infos
            
        except Exception as e:
            self.logger.error(f"Error getting latest models: {e}")
            return []