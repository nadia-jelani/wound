"""
Model Manager for efficient model loading and caching
"""
import os
import logging
import tensorflow as tf
from typing import Optional, Dict, Any
import gc
from config import *

class ModelManager:
    """Manages model loading, caching, and memory optimization"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def load_model(self, model_name: str, model_path: str, model_type: str = 'tensorflow') -> Any:
        """Load and cache a model"""
        if model_name in self.models:
            self.logger.info(f"Model {model_name} already loaded, returning cached version")
            return self.models[model_name]
        
        try:
            self.logger.info(f"Loading model {model_name} from {model_path}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            if model_type == 'tensorflow':
                # Load TensorFlow model
                model = tf.keras.models.load_model(model_path, compile=False)
            elif model_type == 'pytorch':
                # Load PyTorch model (placeholder for future implementation)
                import torch
                model = torch.load(model_path, map_location='cpu')
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Cache the model
            self.models[model_name] = model
            self.logger.info(f"Successfully loaded and cached model {model_name}")
            
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a cached model"""
        return self.models.get(model_name)
    
    def unload_model(self, model_name: str) -> None:
        """Unload and remove a model from cache"""
        if model_name in self.models:
            del self.models[model_name]
            gc.collect()  # Force garbage collection
            self.logger.info(f"Unloaded model {model_name}")
    
    def unload_all_models(self) -> None:
        """Unload all cached models"""
        model_names = list(self.models.keys())
        for model_name in model_names:
            self.unload_model(model_name)
        self.logger.info("Unloaded all cached models")
    
    def get_loaded_models(self) -> list:
        """Get list of currently loaded models"""
        return list(self.models.keys())
    
    def preload_models(self) -> None:
        """Preload commonly used models"""
        try:
            # Preload UNet model
            if os.path.exists(UNET_MODEL_PATH):
                self.load_model('unet', UNET_MODEL_PATH, 'tensorflow')
            
            # Preload classifier model
            if os.path.exists(CLASSIFIER_MODEL_PATH):
                self.load_model('classifier', CLASSIFIER_MODEL_PATH, 'tensorflow')
                
            self.logger.info("Preloaded common models")
            
        except Exception as e:
            self.logger.warning(f"Failed to preload some models: {str(e)}")

# Global model manager instance
model_manager = ModelManager()