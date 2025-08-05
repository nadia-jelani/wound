"""
Utility functions for the Wound Analysis System
"""
import os
import cv2
import numpy as np
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import hashlib

def setup_logging(log_file: str, log_level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def validate_image_file(file_path: str) -> bool:
    """Validate if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of a file"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Resize image to target size"""
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to [0, 1] range"""
    if image.max() > 1.0:
        return image.astype(np.float32) / 255.0
    return image.astype(np.float32)

def create_visualization(image: np.ndarray, mask: np.ndarray, 
                        output_path: str, title: str = "Wound Analysis") -> None:
    """Create and save visualization of image and mask"""
    img_rgb = (image * 255).astype(np.uint8) if image.max() <= 1.0 else image.copy()
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = img_rgb.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.imshow(img_rgb)
    plt.title("Original Image")
    plt.axis('off')
    plt.subplot(1, 3, 2)
    plt.imshow(mask, cmap='gray')
    plt.title("Segmentation Mask")
    plt.axis('off')
    plt.subplot(1, 3, 3)
    plt.imshow(contour_img)
    plt.title("Wound Outline")
    plt.axis('off')
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def calculate_wound_metrics(mask: np.ndarray, scale_mm_per_pixel: float = 0.1) -> Dict[str, float]:
    """Calculate wound area and other metrics"""
    wound_area_px = np.sum(mask > 0)
    wound_area_mm2 = wound_area_px * (scale_mm_per_pixel ** 2)
    estimated_diameter = np.sqrt(wound_area_px / np.pi) * scale_mm_per_pixel
    
    return {
        'area_pixels': wound_area_px,
        'area_mm2': wound_area_mm2,
        'diameter_mm': estimated_diameter
    }

def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_safe_filename(filename: str) -> str:
    """Convert filename to safe version"""
    return "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.')).rstrip()