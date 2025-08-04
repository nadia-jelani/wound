import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Model

# For file dialog
try:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select wound image or video",
        filetypes=[("Image/Video files", "*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov")]
    )
except Exception:
    file_path = input("Enter path to wound image or video: ").strip()
if not file_path:
    print("No file selected!")
    exit()
print("Selected:", file_path)

# === Handle video: extract first frame ===
if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
    cap = cv2.VideoCapture(file_path)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Could not read video!")
        exit()
    temp_img_path = os.path.join("/Users/nadiajelani/projects/wound-segmentation/wound_progress_report", "temp_frame.jpg")
    cv2.imwrite(temp_img_path, frame)
    img_path = temp_img_path
else:
    img_path = file_path

# Settings
IMG_SIZE = (224, 224)
segmenter_model_path = "/Users/nadiajelani/projects/wound-segmentation/models/simclr_unet_wound_segmentation.keras"
classifier_model_path = "/Users/nadiajelani/projects/wound-segmentation/models/wound_classifier_optimized.keras"
output_dir = "/Users/nadiajelani/projects/wound-segmentation/wound_progress_report/"
os.makedirs(output_dir, exist_ok=True)

# === Load models ===
segmenter = tf.keras.models.load_model(segmenter_model_path, compile=False)
classifier = tf.keras.models.load_model(classifier_model_path, compile=False)

# === Preprocess image ===
img = load_img(img_path, target_size=IMG_SIZE)
img_array = img_to_array(img) / 255.0
img_input = np.expand_dims(img_array, axis=0)

# === Predict mask ===
pred_mask = segmenter.predict(img_input, verbose=0)[0, :, :, 0]
mask_bin = (pred_mask > 0.5).astype(np.uint8) * 255

# === Resize mask to original size ===
img_cv = cv2.imread(img_path)
mask_resized = cv2.resize(mask_bin, (img_cv.shape[1], img_cv.shape[0]), interpolation=cv2.INTER_NEAREST)

# === Overlay: draw green contour on original ===
contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
overlay = img_cv.copy()
cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)  # Green

overlay_path = os.path.join(output_dir, "overlay.png")
cv2.imwrite(overlay_path, overlay)

# === Save mask ===
mask_path = os.path.join(output_dir, "segmentation_mask.png")
cv2.imwrite(mask_path, mask_resized)

# === Wound area estimation ===
wound_pixels = np.sum(mask_resized > 127)
pixel_area_mm2 = None  # If known, e.g. mm² per pixel
if pixel_area_mm2:
    wound_area = f"{wound_pixels * pixel_area_mm2 / 100:.2f} cm²"
else:
    wound_area = f"{wound_pixels} pixels"

# === Grad-CAM for classifier ===
def generate_gradcam(model, img_array, original):
    # Find the last conv layer
    for layer in reversed(model.layers):
        if 'conv' in layer.name.lower():
            layer_name = layer.name
            break
    grad_model = Model(inputs=model.inputs, outputs=[model.get_layer(layer_name).output, model.output])
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        if predictions.shape[-1] > 1:
            loss = predictions[:, np.argmax(predictions[0])]
        else:
            loss = predictions[:, 0]
    grads = tape.gradient(loss, conv_outputs)[0]  # (H, W, C)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1)).numpy()  # (C,)
    conv_outputs = conv_outputs[0].numpy()  # (H, W, C)
    conv_outputs = conv_outputs * pooled_grads[None, None, :]  # Broadcasting
    heatmap = np.sum(conv_outputs, axis=-1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= (np.max(heatmap) + 1e-10)
    heatmap = cv2.resize(heatmap, (original.shape[1], original.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    superimposed_img = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0.0)
    gradcam_path = os.path.join(output_dir, "gradcam_heatmap.png")
    cv2.imwrite(gradcam_path, superimposed_img)
    return gradcam_path


gradcam_path = generate_gradcam(classifier, img_input, img_cv)

# === Classify wound (if model is trained for multi-class, adjust as needed) ===
wound_pred = classifier.predict(img_input)
if wound_pred.shape[-1] == 1:
    wound_type = "Wound" if wound_pred[0,0] > 0.5 else "Non-wound"
else:
    wound_type = f"Class {np.argmax(wound_pred[0])} (prob={np.max(wound_pred[0]):.2f})"

# === Save simple report ===
report_txt = os.path.join(output_dir, "wound_report.txt")
with open(report_txt, 'w') as f:
    f.write(f"""Wound Segmentation & Report
==========================
Input: {os.path.basename(img_path)}
Wound type: {wound_type}
Wound area: {wound_area}
Mask file: {mask_path}
Overlay file: {overlay_path}
Grad-CAM: {gradcam_path}
""")
print(f"Report saved: {report_txt}")

# === Matplotlib visualization ===
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.title("Original")
plt.imshow(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.subplot(1, 3, 2)
plt.title("Segmentation Mask")
plt.imshow(mask_resized, cmap='gray')
plt.axis('off')
plt.subplot(1, 3, 3)
plt.title("Overlay with Grad-CAM")
gradcam_img = cv2.imread(gradcam_path)
plt.imshow(cv2.cvtColor(gradcam_img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.tight_layout()
plt.show()

# === Clean up temp file if video ===
if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
