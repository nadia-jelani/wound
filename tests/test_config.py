"""
Unit tests for configuration system
"""
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path to import modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_import(self):
        """Test that config module can be imported"""
        try:
            import config
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import config: {e}")
    
    def test_config_variables_exist(self):
        """Test that all required config variables exist"""
        import config
        
        required_vars = [
            'BASE_DIR',
            'DATASET_PATH',
            'MODEL_SAVE_PATH',
            'UPLOAD_FOLDER',
            'REPORT_FOLDER',
            'UNET_MODEL_PATH',
            'MEDSAM_MODEL_PATH',
            'CLASSIFIER_MODEL_PATH',
            'RESNET_MODEL_PATH',
            'TRAIN_DIR',
            'VAL_DIR',
            'CLASS_NAMES',
            'IMG_SIZE',
            'BATCH_SIZE',
            'EPOCHS',
            'SEGMENTATION_IMG_SIZE',
            'EXPECTED_TRAIN_COUNTS',
            'EXPECTED_VAL_COUNTS',
            'FLASK_DEBUG',
            'FLASK_HOST',
            'FLASK_PORT',
            'LOG_LEVEL',
            'LOG_FILE'
        ]
        
        for var_name in required_vars:
            self.assertTrue(hasattr(config, var_name), f"Missing config variable: {var_name}")
    
    def test_config_paths_are_paths(self):
        """Test that config paths are valid Path objects or strings"""
        import config
        
        path_vars = [
            'BASE_DIR',
            'DATASET_PATH',
            'MODEL_SAVE_PATH',
            'UPLOAD_FOLDER',
            'REPORT_FOLDER',
            'UNET_MODEL_PATH',
            'MEDSAM_MODEL_PATH',
            'CLASSIFIER_MODEL_PATH',
            'RESNET_MODEL_PATH',
            'TRAIN_DIR',
            'VAL_DIR',
            'LOG_FILE'
        ]
        
        for var_name in path_vars:
            value = getattr(config, var_name)
            self.assertIsInstance(value, (str, Path), f"Config variable {var_name} should be a string or Path")
    
    def test_config_numeric_values(self):
        """Test that numeric config values are valid"""
        import config
        
        # Test IMG_SIZE
        self.assertIsInstance(config.IMG_SIZE, int)
        self.assertGreater(config.IMG_SIZE, 0)
        
        # Test BATCH_SIZE
        self.assertIsInstance(config.BATCH_SIZE, int)
        self.assertGreater(config.BATCH_SIZE, 0)
        
        # Test EPOCHS
        self.assertIsInstance(config.EPOCHS, int)
        self.assertGreater(config.EPOCHS, 0)
        
        # Test FLASK_PORT
        self.assertIsInstance(config.FLASK_PORT, int)
        self.assertGreater(config.FLASK_PORT, 0)
        self.assertLess(config.FLASK_PORT, 65536)
    
    def test_config_boolean_values(self):
        """Test that boolean config values are valid"""
        import config
        
        self.assertIsInstance(config.FLASK_DEBUG, bool)
    
    def test_config_lists_and_dicts(self):
        """Test that list and dict config values are valid"""
        import config
        
        # Test CLASS_NAMES
        self.assertIsInstance(config.CLASS_NAMES, list)
        self.assertGreater(len(config.CLASS_NAMES), 0)
        for class_name in config.CLASS_NAMES:
            self.assertIsInstance(class_name, str)
        
        # Test SEGMENTATION_IMG_SIZE
        self.assertIsInstance(config.SEGMENTATION_IMG_SIZE, tuple)
        self.assertEqual(len(config.SEGMENTATION_IMG_SIZE), 2)
        for size in config.SEGMENTATION_IMG_SIZE:
            self.assertIsInstance(size, int)
            self.assertGreater(size, 0)
        
        # Test EXPECTED_TRAIN_COUNTS
        self.assertIsInstance(config.EXPECTED_TRAIN_COUNTS, dict)
        for key, value in config.EXPECTED_TRAIN_COUNTS.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 0)
        
        # Test EXPECTED_VAL_COUNTS
        self.assertIsInstance(config.EXPECTED_VAL_COUNTS, dict)
        for key, value in config.EXPECTED_VAL_COUNTS.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 0)
    
    @patch.dict(os.environ, {
        'DATASET_PATH': './custom_dataset',
        'MODEL_SAVE_PATH': './custom_models',
        'FLASK_DEBUG': 'true',
        'FLASK_PORT': '8080'
    })
    def test_environment_variables(self):
        """Test that environment variables override defaults"""
        # Reload config to pick up environment variables
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.DATASET_PATH, './custom_dataset')
        self.assertEqual(config.MODEL_SAVE_PATH, './custom_models')
        self.assertTrue(config.FLASK_DEBUG)
        self.assertEqual(config.FLASK_PORT, 8080)
    
    def test_directory_creation(self):
        """Test that directories are created when config is imported"""
        import config
        
        # Check that directories exist
        directories = [
            config.DATASET_PATH,
            config.MODEL_SAVE_PATH,
            config.UPLOAD_FOLDER,
            config.REPORT_FOLDER,
            Path(config.LOG_FILE).parent
        ]
        
        for directory in directories:
            self.assertTrue(Path(directory).exists(), f"Directory {directory} should exist")
            self.assertTrue(Path(directory).is_dir(), f"{directory} should be a directory")

if __name__ == '__main__':
    unittest.main()