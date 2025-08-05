"""
Unit tests for utility functions
"""
import unittest
import numpy as np
import tempfile
import os
from pathlib import Path
from PIL import Image

# Add parent directory to path to import utils
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    setup_logging, validate_image_file, calculate_file_hash,
    resize_image, normalize_image, calculate_wound_metrics,
    ensure_directory, get_safe_filename
)

class TestUtils(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_setup_logging(self):
        """Test logging setup"""
        log_file = os.path.join(self.temp_dir, "test.log")
        logger = setup_logging(log_file)
        self.assertIsNotNone(logger)
        self.assertTrue(os.path.exists(log_file))
    
    def test_validate_image_file(self):
        """Test image file validation"""
        # Create a valid test image
        test_image_path = os.path.join(self.temp_dir, "test.png")
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path)
        
        self.assertTrue(validate_image_file(test_image_path))
        
        # Test invalid file
        invalid_path = os.path.join(self.temp_dir, "invalid.txt")
        with open(invalid_path, 'w') as f:
            f.write("not an image")
        
        self.assertFalse(validate_image_file(invalid_path))
    
    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        test_file_path = os.path.join(self.temp_dir, "test.txt")
        test_content = "Hello, World!"
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        hash_value = calculate_file_hash(test_file_path)
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 32)  # MD5 hash length
    
    def test_resize_image(self):
        """Test image resizing"""
        original = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        resized = resize_image(original, (50, 50))
        
        self.assertEqual(resized.shape, (50, 50, 3))
        self.assertEqual(resized.dtype, original.dtype)
    
    def test_normalize_image(self):
        """Test image normalization"""
        # Test with uint8 image
        uint8_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        normalized = normalize_image(uint8_img)
        
        self.assertEqual(normalized.dtype, np.float32)
        self.assertTrue(np.all(normalized >= 0) and np.all(normalized <= 1))
        
        # Test with already normalized image
        float_img = np.random.random((100, 100, 3)).astype(np.float32)
        normalized_float = normalize_image(float_img)
        
        np.testing.assert_array_almost_equal(float_img, normalized_float)
    
    def test_calculate_wound_metrics(self):
        """Test wound metrics calculation"""
        # Create a test mask
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[25:75, 25:75] = 255  # 50x50 wound area
        
        metrics = calculate_wound_metrics(mask, scale_mm_per_pixel=0.1)
        
        self.assertEqual(metrics['area_pixels'], 2500)  # 50*50
        self.assertEqual(metrics['area_mm2'], 25.0)  # 2500 * 0.1^2
        self.assertGreater(metrics['diameter_mm'], 0)
    
    def test_ensure_directory(self):
        """Test directory creation"""
        test_dir = os.path.join(self.temp_dir, "new_dir", "sub_dir")
        ensure_directory(test_dir)
        
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))
    
    def test_get_safe_filename(self):
        """Test filename sanitization"""
        unsafe_filename = "file with spaces & special chars!.txt"
        safe_filename = get_safe_filename(unsafe_filename)
        
        self.assertEqual(safe_filename, "file_with_spaces__special_chars.txt")
        
        # Test already safe filename
        safe_input = "safe_filename.txt"
        self.assertEqual(get_safe_filename(safe_input), safe_input)

if __name__ == '__main__':
    unittest.main()