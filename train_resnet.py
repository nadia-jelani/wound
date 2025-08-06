import os
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import logging
import matplotlib.pyplot as plt

# Setup logging
# Logging is now handled by utils.setup_logging

from config import *
from utils import setup_logging, ensure_directory

# Setup logging
logger = setup_logging(LOG_FILE, LOG_LEVEL)

# Configuration
IMG_HEIGHT, IMG_WIDTH = IMG_SIZE, IMG_SIZE
TRAIN_DIR = os.path.join(DATASET_PATH, 'train')
VALIDATION_DIR = os.path.join(DATASET_PATH, 'validation')
MODEL_PATH = CLASSIFIER_MODEL_PATH

# Data augmentation and preprocessing
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
validation_datagen = ImageDataGenerator(rescale=1./255)

# Load data
try:
    logger.info("Loading training data from %s", TRAIN_DIR)
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        classes=CLASS_NAMES
    )
    logger.info("Loading validation data from %s", VALIDATION_DIR)
    val_generator = validation_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        classes=CLASS_NAMES
    )
except Exception as e:
    logger.error("Failed to load data: %s", str(e))
    raise

# Build ResNet50 model
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3))
base_model.trainable = False  # Freeze base model initially

inputs = base_model.input
x = GlobalAveragePooling2D()(base_model.output)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
outputs = Dense(1, activation='sigmoid')(x)  # Binary classification
model = Model(inputs, outputs)

# Compile model
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train model
try:
    logger.info("Starting training...")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=val_generator,
        validation_steps=val_generator.samples // BATCH_SIZE,
        callbacks=[
            tf.keras.callbacks.ModelCheckpoint(
                MODEL_PATH,
                save_best_only=True,
                monitor='val_loss',
                mode='min',
                verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=3,
                min_lr=1e-7,
                verbose=1
            )
        ]
    )
    logger.info("Training completed")
except Exception as e:
    logger.error("Training failed: %s", str(e))
    raise

# Save final model
model.save(MODEL_PATH)
logger.info("Model saved to %s", MODEL_PATH)

# Plot training history
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig('training_history.png')
plt.close()
logger.info("Training history plot saved to training_history.png")