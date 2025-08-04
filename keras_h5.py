import tensorflow as tf
from tensorflow.keras.models import load_model
import logging
import os

# === Setup Logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Define Custom Loss Functions ===
def dice_loss(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.keras.backend.flatten(y_true)
    y_pred_f = tf.keras.backend.flatten(y_pred)
    intersection = tf.keras.backend.sum(y_true_f * y_pred_f)
    return 1 - (2. * intersection + smooth) / (
        tf.keras.backend.sum(y_true_f) + tf.keras.backend.sum(y_pred_f) + smooth
    )

def combined_loss(y_true, y_pred):
    bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    dice = dice_loss(y_true, y_pred)
    return bce + dice

# === File Paths ===
KERAS_MODEL_PATH = "/Users/nadiajelani/projects/wound-segmentation/models/simclr_unet_wound_segmentation.keras"
H5_MODEL_PATH = "/Users/nadiajelani/projects/wound-segmentation/models/simclr_unet_wound_segmentation.h5"

# === Conversion Function ===
def convert_keras_to_h5(keras_path, h5_path):
    try:
        # Check if .keras file exists
        if not os.path.exists(keras_path):
            raise FileNotFoundError(f".keras model file not found at {keras_path}. Please ensure the trained model exists.")

        # Load the .keras model with custom loss
        logger.info(f"Loading .keras model from {keras_path}...")
        model = load_model(keras_path, custom_objects={'combined_loss': combined_loss})
        logger.info("✅ Model loaded successfully.")

        # Log model summary for verification
        model.summary()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(h5_path), exist_ok=True)

        # Save the model in .h5 format
        logger.info(f"Saving model to {h5_path} in .h5 format...")
        model.save(h5_path)
        logger.info(f"✅ Model saved successfully to {h5_path}")

        # Verify the .h5 model by loading it
        logger.info(f"Verifying .h5 model by loading {h5_path}...")
        model_h5 = load_model(h5_path, custom_objects={'combined_loss': combined_loss})
        logger.info("✅ .h5 model loaded successfully for verification.")

    except Exception as e:
        logger.error(f"❌ Failed to convert model: {e}")
        raise

# === Execute Conversion ===
if __name__ == "__main__":
    logger.info(f"TensorFlow version: {tf.__version__}")
    logger.info(f"Current date and time: 2025-06-28 20:20:00 BST")
    convert_keras_to_h5(KERAS_MODEL_PATH, H5_MODEL_PATH)
