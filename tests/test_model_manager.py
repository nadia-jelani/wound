"""
Unit tests for model manager functionality
"""
import unittest
import tempfile
import os
import numpy as np
from pathlib import Path
import tensorflow as tf

# Add parent directory to path to import modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from model_manager import ModelManager

class TestModelManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.model_manager = ModelManager()
        
    def tearDown(self):
        # Clean up
        self.model_manager.unload_all_models()
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_model_manager_initialization(self):
        """Test model manager initialization"""
        self.assertIsInstance(self.model_manager.models, dict)
        self.assertEqual(len(self.model_manager.models), 0)
    
    def test_load_nonexistent_model(self):
        """Test loading a model that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            self.model_manager.load_model('nonexistent', '/path/to/nonexistent/model.h5')
    
    def test_load_tensorflow_model(self):
        """Test loading a TensorFlow model"""
        # Create a simple test model
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        # Save the model
        model_path = os.path.join(self.temp_dir, 'test_model.h5')
        model.save(model_path)
        
        # Load using model manager
        loaded_model = self.model_manager.load_model('test_model', model_path, 'tensorflow')
        
        self.assertIsNotNone(loaded_model)
        self.assertIn('test_model', self.model_manager.models)
        self.assertEqual(loaded_model, self.model_manager.models['test_model'])
    
    def test_model_caching(self):
        """Test that models are cached and not reloaded"""
        # Create a simple test model
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        # Save the model
        model_path = os.path.join(self.temp_dir, 'test_model.h5')
        model.save(model_path)
        
        # Load model twice
        model1 = self.model_manager.load_model('test_model', model_path, 'tensorflow')
        model2 = self.model_manager.load_model('test_model', model_path, 'tensorflow')
        
        # Should be the same object (cached)
        self.assertIs(model1, model2)
        self.assertEqual(len(self.model_manager.models), 1)
    
    def test_get_model(self):
        """Test getting a cached model"""
        # Create and load a model
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model_path = os.path.join(self.temp_dir, 'test_model.h5')
        model.save(model_path)
        
        self.model_manager.load_model('test_model', model_path, 'tensorflow')
        
        # Get the model
        retrieved_model = self.model_manager.get_model('test_model')
        self.assertIsNotNone(retrieved_model)
        
        # Get non-existent model
        nonexistent_model = self.model_manager.get_model('nonexistent')
        self.assertIsNone(nonexistent_model)
    
    def test_unload_model(self):
        """Test unloading a specific model"""
        # Create and load a model
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model_path = os.path.join(self.temp_dir, 'test_model.h5')
        model.save(model_path)
        
        self.model_manager.load_model('test_model', model_path, 'tensorflow')
        self.assertIn('test_model', self.model_manager.models)
        
        # Unload the model
        self.model_manager.unload_model('test_model')
        self.assertNotIn('test_model', self.model_manager.models)
    
    def test_unload_all_models(self):
        """Test unloading all models"""
        # Create and load multiple models
        for i in range(3):
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            
            model_path = os.path.join(self.temp_dir, f'test_model_{i}.h5')
            model.save(model_path)
            
            self.model_manager.load_model(f'test_model_{i}', model_path, 'tensorflow')
        
        self.assertEqual(len(self.model_manager.models), 3)
        
        # Unload all models
        self.model_manager.unload_all_models()
        self.assertEqual(len(self.model_manager.models), 0)
    
    def test_get_loaded_models(self):
        """Test getting list of loaded models"""
        # Create and load multiple models
        for i in range(2):
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            
            model_path = os.path.join(self.temp_dir, f'test_model_{i}.h5')
            model.save(model_path)
            
            self.model_manager.load_model(f'test_model_{i}', model_path, 'tensorflow')
        
        loaded_models = self.model_manager.get_loaded_models()
        self.assertEqual(len(loaded_models), 2)
        self.assertIn('test_model_0', loaded_models)
        self.assertIn('test_model_1', loaded_models)
    
    def test_unsupported_model_type(self):
        """Test loading with unsupported model type"""
        with self.assertRaises(ValueError):
            self.model_manager.load_model('test', 'path/to/model', 'unsupported_type')

if __name__ == '__main__':
    unittest.main()