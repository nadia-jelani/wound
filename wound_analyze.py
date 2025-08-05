import os
import cv2
import numpy as np
import tensorflow as tf
from datetime import datetime
import logging
import gc
from tensorflow.keras import backend as K

# === Setup Logging ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/nadiajelani/projects/wound-segmentation/wound_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Model Paths ===
SEG_MODEL_PATH = "/Users/nadiajelani/projects/wound-segmentation/models/simclr_unet_wound_segmentation.keras"
CLS_MODEL_PATH = "/Users/nadiajelani/projects/wound-segmentation/models/wound_classifier.h5"
OUTPUT_DIR = "/Users/nadiajelani/projects/wound-segmentation/wound_progress_report"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Load Models ===
def load_models():
    try:
        seg_model = tf.keras.models.load_model(SEG_MODEL_PATH, compile=False)
        logger.info("Segmentation model loaded")
    except Exception as e:
        logger.error(f"Failed to load segmentation model: {e}")
        raise

    try:
        base = tf.keras.applications.ResNet50(weights=None, include_top=False, input_shape=(224, 224, 3))
        x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
        x = tf.keras.layers.Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.0001))(x)
        x = tf.keras.layers.Dropout(0.5)(x)
        x = tf.keras.layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.0001))(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(1, activation='sigmoid', dtype='float32')(x)
        cls_model = tf.keras.Model(inputs=base.input, outputs=x)
        cls_model.load_weights(CLS_MODEL_PATH, by_name=True)
        logger.info("Classifier model loaded")
    except Exception as e:
        logger.error(f"Failed to load classifier model: {e}")
        raise

    return seg_model, cls_model

# === Skin Tone Calibration ===
def calibrate_skin_tone(image, skin_ref_path="/Users/nadiajelani/Desktop/skin_image.jpg"):
    try:
        skin_ref = cv2.imread(skin_ref_path)
        if skin_ref is None:
            logger.warning("Skin reference image not found, skipping calibration")
            return image
        skin_ref_rgb = cv2.cvtColor(skin_ref, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        skin_mean = np.mean(skin_ref_rgb, axis=(0, 1))
        image_mean = np.mean(image_rgb, axis=(0, 1))
        calibrated = image_rgb * (skin_mean / (image_mean + 1e-6))
        calibrated = np.clip(calibrated, 0, 255).astype(np.uint8)
        logger.info("Skin tone calibration applied")
        return cv2.cvtColor(calibrated, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Skin tone calibration failed: {e}")
        return image

# === Image Preprocessing ===
def preprocess_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Invalid image path: {image_path}")
        image = calibrate_skin_tone(image)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(image_rgb, (224, 224)) / 255.0
        logger.info(f"Preprocessed image: {image_path}, shape: {image_rgb.shape}")
        return image_rgb, np.expand_dims(resized.astype(np.float32), axis=0)
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise

# === Prediction ===
def predict(image_tensor, seg_model, cls_model):
    try:
        cls_pred = cls_model.predict(image_tensor, batch_size=1, verbose=0)[0][0]
        is_wound = cls_pred > 0.5
        logger.info(f"Classifier Result: {'Wound' if is_wound else 'Non-Wound'} (Confidence: {cls_pred:.2f})")
        if not is_wound:
            logger.warning("Image classified as non-wound, continuing anyway")
        
        seg_output = seg_model.predict(image_tensor, batch_size=1, verbose=0)[0]
        logger.debug(f"U-Net output shape: {seg_output.shape}, min: {seg_output.min()}, max: {seg_output.max()}")
        thresh = max(np.max(seg_output) * 0.5, 0.5)  # Ensure minimum threshold
        mask = (seg_output > thresh).astype(np.uint8) * 255
        if mask.sum() == 0:
            logger.warning("Empty segmentation mask produced")
        logger.info("Segmentation completed")
        return mask, cls_pred
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise
    finally:
        K.clear_session()
        gc.collect()

# === Save Outputs ===
def save_outputs(image_rgb, mask, confidence):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mask_path = os.path.join(OUTPUT_DIR, f"simclr_mask_{timestamp}.png")
    result_path = os.path.join(OUTPUT_DIR, f"result_{timestamp}.png")
    report_path = os.path.join(OUTPUT_DIR, f"wound_report_{timestamp}.txt")

    try:
        # Ensure mask is 2D for saving
        if len(mask.shape) == 3:
            mask = mask[:, :, 0]
        cv2.imwrite(mask_path, mask)
        
        # Resize image_rgb to match mask if needed
        if image_rgb.shape[:2] != mask.shape[:2]:
            image_rgb = cv2.resize(image_rgb, (mask.shape[1], mask.shape[0]))
        
        # Convert mask to 3-channel for addWeighted
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        logger.debug(f"image_rgb shape: {image_rgb.shape}, mask_3ch shape: {mask_3ch.shape}")
        result_img = cv2.addWeighted(image_rgb, 0.7, mask_3ch, 0.3, 0)
        cv2.imwrite(result_path, cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR))
        
        with open(report_path, 'w') as f:
            f.write("Wound Analysis Report\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Confidence: {confidence:.2f}\n")
            f.write(f"Segmentation mask saved at: {mask_path}\n")
            f.write(f"Result image saved at: {result_path}\n")
        
        logger.info(f"Saved outputs: {mask_path}, {result_path}, {report_path}")
    except Exception as e:
        logger.error(f"Failed to save outputs: {e}")
        raise

# === Main Runner ===
def run_wound_analysis(image_path):
    K.clear_session()
    seg_model, cls_model = load_models()
    image_rgb, tensor = preprocess_image(image_path)
    mask, confidence = predict(tensor, seg_model, cls_model)
    if mask.sum() > 0:
        save_outputs(image_rgb, mask, confidence)
    else:
        logger.info("No wound detected or empty mask, no outputs saved")
    K.clear_session()
    gc.collect()

# === Example usage ===
if __name__ == "__main__":
    test_image_path = "/Users/nadiajelani/Desktop/ww2.jpeg"
    run_wound_analysis(test_image_path)