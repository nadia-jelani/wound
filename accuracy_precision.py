import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import f1_score, jaccard_score, precision_score, recall_score, confusion_matrix
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ----------- Config -----------
model_path = "/Users/nadiajelani/projects/wound-segmentation/models/simclr_unet_patch_wound.keras"
image_path = "/Users/nadiajelani/Desktop/wound2.jpg"
mask_path = "/Users/nadiajelani/Desktop/wound2_mask.png"
output_folder = "precision"
os.makedirs(output_folder, exist_ok=True)

# ----------- Load model -----------
model = tf.keras.models.load_model(model_path, compile=False)

# ----------- Load and preprocess image -----------
img = cv2.imread(image_path)
img_resized = cv2.resize(img, (128, 128)) / 255.0
input_tensor = np.expand_dims(img_resized, axis=0)

# ----------- Predict mask -----------
pred = model.predict(input_tensor)[0, :, :, 0]
pred_bin = (pred > 0.5).astype(np.uint8)
pred_bin_resized = cv2.resize(pred_bin, img.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)

# ----------- Load ground truth mask -----------
gt = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
gt_bin = (gt > 127).astype(np.uint8)

# ----------- Flatten for metric calculation -----------
y_true = gt_bin.flatten()
y_pred = pred_bin_resized.flatten()

# ----------- Calculate metrics -----------
dice = f1_score(y_true, y_pred, zero_division=0)
iou = jaccard_score(y_true, y_pred, zero_division=0)
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

# ----------- Plot and save metrics bar chart -----------
metrics = {"Dice": dice, "IoU": iou, "Precision": precision, "Recall": recall}
plt.figure(figsize=(6, 4))
plt.bar(metrics.keys(), metrics.values(), color="mediumseagreen")
plt.ylim(0, 1)
plt.title("Segmentation Metrics for wound.jpg")
plt.ylabel("Score")
plt.tight_layout()
metrics_path = os.path.join(output_folder, "single_image_metrics.png")
plt.savefig(metrics_path)
plt.close()

# ----------- Plot and save confusion matrix -----------
cm = np.array([[tn, fp], [fn, tp]])
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Pred: Non-Wound", "Pred: Wound"],
            yticklabels=["True: Non-Wound", "True: Wound"])
plt.title("Confusion Matrix: wound.jpg")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
conf_matrix_path = os.path.join(output_folder, "single_image_confusion_matrix.png")
plt.savefig(conf_matrix_path)
plt.close()

# ----------- Generate PDF Report -----------
pdf_path = os.path.join(output_folder, "single_image_evaluation.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Single Image Evaluation Report", styles["Title"]))
elements.append(Spacer(1, 12))

# Add Metric Chart
if os.path.exists(metrics_path):
    elements.append(Paragraph("Segmentation Metrics", styles["Heading2"]))
    elements.append(RLImage(metrics_path, width=5*inch, height=3*inch))
    elements.append(Spacer(1, 12))

# Add Confusion Matrix
if os.path.exists(conf_matrix_path):
    elements.append(Paragraph("Confusion Matrix", styles["Heading2"]))
    elements.append(RLImage(conf_matrix_path, width=5*inch, height=3*inch))
    elements.append(Spacer(1, 12))

# Build PDF
doc.build(elements)

# ----------- Final Output Info -----------
print("✅ Evaluation complete!")
print(f"- Saved metrics chart to: {metrics_path}")
print(f"- Saved confusion matrix to: {conf_matrix_path}")
print(f"- Saved PDF report to: {pdf_path}")
