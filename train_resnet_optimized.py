
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Concatenate
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import numpy as np
import logging
import os
import matplotlib.pyplot as plt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[logging.FileHandler('/Users/nadiajelani/projects/wound-segmentation/wound_progress.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Set mixed precision
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Verify GPU
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    logger.info(f"GPU detected: {physical_devices}")
    for device in physical_devices:
        tf.config.experimental.set_memory_growth(device, True)
else:
    logger.warning("No GPU detected, falling back to CPU.")

# Configuration
IMG_HEIGHT, IMG_WIDTH = 224, 224
BATCH_SIZE = 64  # Increased for speed
PRETRAIN_EPOCHS = 2  # Reduced for 30-min target
EPOCHS = 5  # Reduced for speed
TRAIN_DIR = '/Users/nadiajelani/Desktop/wounds-whisperer/wounds/u_net_images/train_images'
TRAIN_MASK_DIR = '/Users/nadiajelani/Desktop/wounds-whisperer/wounds/u_net_images/train_masks'
VALID_DIR = '/Users/nadiajelani/Desktop/wounds-whisperer/wounds/u_net_images/test_images'
VALID_MASK_DIR = '/Users/nadiajelani/Desktop/wounds-whisperer/wounds/u_net_images/test_masks'
MODEL_SAVE_PATH = '/Users/nadiajelani/projects/wound-segmentation/models/simclr_unet_wound_segmentation.keras'
CHECKPOINT_DIR = '/Users/nadiajelani/projects/wound-segmentation/models/checkpoints'
CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, 'unet_{epoch:02d}_{val_loss:.4f}.keras')
PRETRAIN_SAVE_PATH = '/Users/nadiajelani/projects/wound-segmentation/models/pretrained_base_model.keras'

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# SimCLR augmentation
def simclr_augmentation():
    return ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
        preprocessing_function=lambda x: tf.image.random_contrast(x, 0.8, 1.2)
    )

# U-Net data augmentation
train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=20, horizontal_flip=True)
valid_datagen = ImageDataGenerator(rescale=1./255)

# Paired generator
def paired_generator(images_dir, masks_dir, datagen, target_size=(224, 224), batch_size=64):
    image_generator = datagen.flow_from_directory(
        images_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode=None,
        shuffle=True
    )
    mask_generator = datagen.flow_from_directory(
        masks_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode=None,
        shuffle=True,
        color_mode='grayscale'
    )
    while True:
        images = next(image_generator)
        masks = next(mask_generator)
        yield (images, masks)

train_generator = paired_generator(TRAIN_DIR, TRAIN_MASK_DIR, train_datagen, batch_size=BATCH_SIZE)
validation_generator = paired_generator(VALID_DIR, VALID_MASK_DIR, valid_datagen, batch_size=BATCH_SIZE)

# SimCLR pretraining
def build_simclr_model(input_shape=(224, 224, 3)):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    return Model(inputs=base_model.input, outputs=x)

@tf.function
def simclr_train_step(images, model, optimizer, temperature=0.1, accumulation_steps=4):
    loss = 0.0
    for i in range(accumulation_steps):
        with tf.GradientTape() as tape:
            view1 = tf.image.random_flip_left_right(images)
            view1 = tf.image.random_brightness(view1, max_delta=0.1)
            view1 = tf.image.random_contrast(view1, lower=0.8, upper=1.2)
            view1 = tf.image.random_crop(view1, size=[tf.shape(images)[0], IMG_HEIGHT, IMG_WIDTH, 3])
            view1 = tf.clip_by_value(view1, 0.0, 1.0)
            
            view2 = tf.image.random_flip_left_right(images)
            view2 = tf.image.random_brightness(view2, max_delta=0.1)
            view2 = tf.image.random_contrast(view2, lower=0.8, upper=1.2)
            view2 = tf.image.random_crop(view2, size=[tf.shape(images)[0], IMG_HEIGHT, IMG_WIDTH, 3])
            view2 = tf.clip_by_value(view2, 0.0, 1.0)
            
            h1 = model(view1, training=True)
            h2 = model(view2, training=True)
            h1 = tf.math.l2_normalize(h1, axis=1)
            h2 = tf.math.l2_normalize(h2, axis=1)
            batch_size = tf.shape(h1)[0]
            labels = tf.range(batch_size)
            logits_ab = tf.matmul(h1, h2, transpose_b=True) / temperature
            logits_ba = tf.matmul(h2, h1, transpose_b=True) / temperature
            masks = tf.one_hot(tf.range(batch_size), batch_size, dtype=logits_ab.dtype)
            logits_aa = tf.matmul(h1, h1, transpose_b=True) / temperature - masks * 1e9
            logits_bb = tf.matmul(h2, h2, transpose_b=True) / temperature - masks * 1e9
            loss_step = tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(labels, logits_ab, from_logits=True)) + \
                        tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(labels, logits_ba, from_logits=True))
            loss += loss_step / accumulation_steps
        if i == accumulation_steps - 1:
            gradients = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return loss

# Pretrain SimCLR
if not os.path.exists(PRETRAIN_SAVE_PATH):
    logger.info("Starting SimCLR pretraining...")
    simclr_datagen = simclr_augmentation()
    all_generator = simclr_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode=None,
        shuffle=True
    )
    all_dataset = tf.data.Dataset.from_generator(
        lambda: all_generator,
        output_signature=tf.TensorSpec(shape=(None, IMG_HEIGHT, IMG_WIDTH, 3), dtype=tf.float32)
    ).map(
        lambda x: tf.clip_by_value(x, 0.0, 1.0),
        num_parallel_calls=tf.data.AUTOTUNE
    ).cache()
    .prefetch(tf.data.AUTOTUNE)
    
    pretrain_model = build_simclr_model()
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    for epoch in range(PRETRAIN_EPOCHS):
        logger.info(f"Pretraining Epoch {epoch + 1}/{PRETRAIN_EPOCHS}")
        epoch_loss = 0.0
        steps = 0
        for images in all_dataset:
            loss = simclr_train_step(images, pretrain_model, optimizer)
            epoch_loss += loss.numpy()
            steps += 1
            if steps % 10 == 0:
                logger.info(f"Step {steps}, Loss: {loss.numpy():.4f}")
        epoch_loss /= steps
        logger.info(f"Pretraining Epoch {epoch + 1} Avg Loss: {epoch_loss:.4f}")
    pretrain_model.save(PRETRAIN_SAVE_PATH)
    logger.info(f"Pretraining completed, model saved to {PRETRAIN_SAVE_PATH}")
else:
    logger.info(f"Pretrained model found at {PRETRAIN_SAVE_PATH}, skipping pretraining.")
    pretrain_model = tf.keras.models.load_model(PRETRAIN_SAVE_PATH)

# U-Net model
def build_unet(input_shape=(224, 224, 3), num_classes=1):
    inputs = Input(shape=input_shape)
    enc1 = pretrain_model.get_layer('conv1')(inputs)
    enc1 = pretrain_model.get_layer('bn_conv1')(enc1)
    enc1 = pretrain_model.get_layer('activation')(enc1)
    enc1 = pretrain_model.get_layer('max_pooling2d_1')(enc1)
    enc2 = pretrain_model.get_layer('conv2_block3_out')(enc1)
    enc3 = pretrain_model.get_layer('conv3_block4_out')(enc2)
    enc4 = pretrain_model.get_layer('conv4_block6_out')(enc3)
    enc5 = pretrain_model.get_layer('conv5_block3_out')(enc4)

    up1 = UpSampling2D(size=(2, 2))(enc5)
    up1 = Concatenate()([up1, enc4])
    up1 = Conv2D(512, 3, activation='relu', padding='same')(up1)
    up1 = Conv2D(512, 3, activation='relu', padding='same')(up1)

    up2 = UpSampling2D(size=(2, 2))(up1)
    up2 = Concatenate()([up2, enc3])
    up2 = Conv2D(256, 3, activation='relu', padding='same')(up2)
    up2 = Conv2D(256, 3, activation='relu', padding='same')(up2)

    up3 = UpSampling2D(size=(2, 2))(up2)
    up3 = Concatenate()([up3, enc2])
    up3 = Conv2D(128, 3, activation='relu', padding='same')(up3)
    up3 = Conv2D(128, 3, activation='relu', padding='same')(up3)

    up4 = UpSampling2D(size=(2, 2))(up3)
    up4 = Concatenate()([up4, enc1])
    up4 = Conv2D(64, 3, activation='relu', padding='same')(up4)
    up4 = Conv2D(64, 3, activation='relu', padding='same')(up4)

    outputs = Conv2D(num_classes, 1, activation='sigmoid')(up4)

    return Model(inputs=inputs, outputs=outputs)

# Define losses
def dice_loss(y_true, y_pred, smooth=1e-6):
    y_true_f = tf.keras.backend.flatten(y_true)
    y_pred_f = tf.keras.backend.flatten(y_pred)
    intersection = tf.keras.backend.sum(y_true_f * y_pred_f)
    return 1 - (2. * intersection + smooth) / (tf.keras.backend.sum(y_true_f) + tf.keras.backend.sum(y_pred_f) + smooth)

def combined_loss(y_true, y_pred):
    bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    dice = dice_loss(y_true, y_pred)
    return 0.5 * bce + 0.5 * dice

# Build and compile
model = build_unet()
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=combined_loss,
    metrics=['accuracy', tf.keras.metrics.MeanIoU(num_classes=2)]
)

# Callbacks
checkpoint = ModelCheckpoint(CHECKPOINT_PATH, monitor='val_loss', save_best_only=True, mode='min')
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6)

# Train
logger.info("Starting U-Net training...")
history = model.fit(
    train_generator,
    steps_per_epoch=50,  # Reduced for speed
    epochs=EPOCHS,
    validation_data=validation_generator,
    validation_steps=20,  # Subset for speed
    callbacks=[checkpoint, early_stopping, reduce_lr]
)

# Save and visualize
model.save(MODEL_SAVE_PATH)
logger.info(f"Final model saved to {MODEL_SAVE_PATH}")

def visualize_predictions(model, images_dir, masks_dir, num_samples=3):
    datagen = ImageDataGenerator(rescale=1./255)
    image_gen = datagen.flow_from_directory(
        images_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=num_samples,
        class_mode=None,
        shuffle=False
    )
    mask_gen = datagen.flow_from_directory(
        masks_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=num_samples,
        class_mode=None,
        shuffle=False,
        color_mode='grayscale'
    )
    images = next(image_gen)
    masks = next(mask_gen)
    predictions = model.predict(images)
    predictions = (predictions > 0.5).astype(np.uint8)

    for i in range(num_samples):
        plt.figure(figsize=(15, 5))
        plt.subplot(1, 3, 1)
        plt.imshow(images[i])
        plt.title("Original Image")
        plt.axis('off')
        plt.subplot(1, 3, 2)
        plt.imshow(masks[i, :, :, 0], cmap='gray')
        plt.title("Ground Truth Mask")
        plt.axis('off')
        plt.subplot(1, 3, 3)
        plt.imshow(predictions[i, :, :, 0], cmap='gray')
        plt.title("Predicted Mask")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

logger.info("Visualizing sample predictions...")
visualize_predictions(model, VALID_DIR, VALID_MASK_DIR)