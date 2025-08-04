"""
Configuration file for the Wound Analysis System
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATASET_PATH = os.getenv('DATASET_PATH', str(BASE_DIR / 'dataset'))
MODEL_SAVE_PATH = os.getenv('MODEL_SAVE_PATH', str(BASE_DIR / 'models'))
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
REPORT_FOLDER = os.getenv('REPORT_FOLDER', str(BASE_DIR / 'reports'))

# Model paths
UNET_MODEL_PATH = os.getenv('UNET_MODEL_PATH', str(BASE_DIR / 'models' / 'best_unet_wound_model.h5'))
MEDSAM_MODEL_PATH = os.getenv('MEDSAM_MODEL_PATH', str(BASE_DIR / 'models' / 'best_medsam_model.pth'))
CLASSIFIER_MODEL_PATH = os.getenv('CLASSIFIER_MODEL_PATH', str(BASE_DIR / 'models' / 'wound_classifier.h5'))
RESNET_MODEL_PATH = os.getenv('RESNET_MODEL_PATH', str(BASE_DIR / 'models' / 'wound_classifier.h5'))

# Dataset configuration
TRAIN_DIR = os.path.join(DATASET_PATH, 'train')
VAL_DIR = os.path.join(DATASET_PATH, 'validation')
CLASS_NAMES = ['non-wound', 'wound']

# Model configuration
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 30
SEGMENTATION_IMG_SIZE = (128, 128)

# Expected dataset counts
EXPECTED_TRAIN_COUNTS = {'non-wound': 8012, 'wound': 13218}
EXPECTED_VAL_COUNTS = {'non-wound': 2003, 'wound': 3305}

# Flask configuration
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'wound_analysis.log'))

# Create necessary directories
for path in [DATASET_PATH, MODEL_SAVE_PATH, UPLOAD_FOLDER, REPORT_FOLDER, 
             Path(LOG_FILE).parent]:
    Path(path).mkdir(parents=True, exist_ok=True)