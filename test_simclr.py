
import tensorflow as tf
from tensorflow.keras.models import load_model
import logging
import os
import segmentation_models as sm

# === Setup Logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Define Custom Loss Function ===
def weighted_focal_dice_loss(y_true, y_pred, alpha=0.7, gamma=2.0):
    y_true = tf.keras.backend.cast(y_true, tf.keras.backend.floatx())
    y_pred = tf.keras.backend.cast(y_pred, tf.keras.backend.floatx())
    ce_loss = -tf.keras.backend.mean(alpha * tf.keras.backend.pow(1. - y_pred, gamma) * y_true * tf.keras.backend.log(y_pred + tf.keras.backend.epsilon()))
    intersection = tf.keras.backend.sum(y_true * y_pred, axis=[1, 2, 3])
    union = tf.keras.backend.sum(y_true, axis=[1, 2, 3]) + tf.keras.backend.sum(y_pred, axis=[1, 2, 3])
    dice_loss = 1 - (2. * intersection + 1.) / (union + 1.)
    return ce_loss + dice_loss

# === File Paths ===
KERAS_MODEL_PATH = "/Users/nadiajelani/projects/wound-segmentation/models/wound_classifier_optimized.keras"
H5_MODEL_PATH    = "/Users/nadiajelani/projects/wound-segmentation/models/wound_classifier_optimized.h5"

# === Conversion Function ===
def convert_keras_to_h5(keras_path, h5_path):
    try:
        # Check if .keras file exists
        if not os.path.exists(keras_path):
            raise FileNotFoundError(f".keras model file not found at {keras_path}")

        # Load the .keras model with custom loss
        logger.info(f"Loading .keras model from {keras_path}...")
        model = load_model(keras_path, custom_objects={'weighted_focal_dice_loss': weighted_focal_dice_loss, 'iou_score': sm.metrics.iou_score})
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
        model_h5 = load_model(h5_path, custom_objects={'weighted_focal_dice_loss': weighted_focal_dice_loss, 'iou_score': sm.metrics.iou_score})
        logger.info("✅ .h5 model loaded successfully for verification.")

    except Exception as e:
        logger.error(f"❌ Failed to convert model: {e}")
        raise

# === Execute Conversion ===
if __name__ == "__main__":
    logger.info(f"TensorFlow version: {tf.__version__}")
    logger.info(f"Current date and time: 2025-06-28 21:17:00 BST")
    convert_keras_to_h5(KERAS_MODEL_PATH, H5_MODEL_PATH)
