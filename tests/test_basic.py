"""
Basic tests that don't require external dependencies
"""
import unittest
import os
import tempfile
from pathlib import Path

# Add parent directory to path to import modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

class TestBasicFunctionality(unittest.TestCase):
    
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
    
    def test_utils_import(self):
        """Test that utils module can be imported (without external deps)"""
        try:
            # Test basic functions that don't require external dependencies
            from utils import ensure_directory, get_safe_filename
            self.assertTrue(True)
        except ImportError as e:
            # This is expected if external dependencies are not installed
            self.skipTest(f"External dependencies not available: {e}")
    
    def test_project_structure(self):
        """Test that basic project structure exists"""
        required_files = [
            'requirements.txt',
            'README.md',
            'config.py',
            'utils.py',
            'model_manager.py',
            'analyze_wound.py',
            'train_classifier.py',
            'train_resnet.py'
        ]
        
        for file_path in required_files:
            self.assertTrue(Path(file_path).exists(), f"Required file {file_path} is missing")
    
    def test_directory_structure(self):
        """Test that required directories exist"""
        required_dirs = [
            'models',
            'uploads',
            'reports',
            'logs',
            'tests'
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(Path(dir_path).exists(), f"Required directory {dir_path} is missing")
            self.assertTrue(Path(dir_path).is_dir(), f"{dir_path} should be a directory")
    
    def test_config_variables(self):
        """Test that config has required variables"""
        import config
        
        required_vars = [
            'BASE_DIR',
            'DATASET_PATH',
            'MODEL_SAVE_PATH',
            'UPLOAD_FOLDER',
            'REPORT_FOLDER',
            'IMG_SIZE',
            'BATCH_SIZE',
            'EPOCHS',
            'CLASS_NAMES'
        ]
        
        for var_name in required_vars:
            self.assertTrue(hasattr(config, var_name), f"Missing config variable: {var_name}")
    
    def test_utils_functions(self):
        """Test utility functions that don't require external dependencies"""
        try:
            from utils import ensure_directory, get_safe_filename
            
            # Test ensure_directory
            test_dir = os.path.join(self.temp_dir, "test_dir", "sub_dir")
            ensure_directory(test_dir)
            self.assertTrue(os.path.exists(test_dir))
            self.assertTrue(os.path.isdir(test_dir))
            
            # Test get_safe_filename
            unsafe_filename = "file with spaces & special chars!.txt"
            safe_filename = get_safe_filename(unsafe_filename)
            self.assertEqual(safe_filename, "file_with_spaces__special_chars.txt")
            
            # Test already safe filename
            safe_input = "safe_filename.txt"
            self.assertEqual(get_safe_filename(safe_input), safe_input)
            
        except ImportError as e:
            self.skipTest(f"External dependencies not available: {e}")

if __name__ == '__main__':
    unittest.main()