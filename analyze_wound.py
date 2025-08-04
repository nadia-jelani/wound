from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask import render_template

import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from fpdf import FPDF
import time
import json
import base64
import uuid
from datetime import datetime
from wound_medsam import build_unet, predict_healing_potential, load_medsam_model, medsam_segment

from config import *

app = Flask(__name__)
CORS(app)

# Validate model files exist
if not os.path.exists(UNET_MODEL_PATH):
    raise FileNotFoundError(f"UNet model not found at {UNET_MODEL_PATH}")
if not os.path.exists(MEDSAM_MODEL_PATH):
    raise FileNotFoundError(f"MedSAM model not found at {MEDSAM_MODEL_PATH}")

model = build_unet(input_shape=(128, 128, 3))
model.load_weights(UNET_MODEL_PATH)

from utils import create_visualization, calculate_wound_metrics, ensure_directory

def create_visualization_wrapper(image, pred_mask, output_path):
    """Wrapper for the original create_visualization function"""
    img_rgb = (image * 255).astype(np.uint8) if image.max() <= 1.0 else image.copy()
    contours, _ = cv2.findContours(pred_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = img_rgb.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.imshow(img_rgb)
    plt.title("Your Wound")
    plt.axis('off')
    plt.subplot(1, 3, 2)
    plt.imshow(pred_mask, cmap='gray')
    plt.title("Detected Wound Area")
    plt.axis('off')
    plt.subplot(1, 3, 3)
    plt.imshow(contour_img)
    plt.title("Wound Outline")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def generate_patient_report(image, pred_mask, patient_info, severity, healing_potential, wound_area_mm2, output_dir):
    ensure_directory(output_dir)
    # Check write permissions
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"No write permissions for output directory: {output_dir}")

    # Calculate wound metrics using utility function
    metrics = calculate_wound_metrics(pred_mask, scale_mm_per_pixel=0.264)
    estimated_diameter = metrics['diameter_mm']
    wound_description = f"""
    Wound Description:
    - Size: The wound is about {estimated_diameter:.2f} millimeters wide, roughly {'smaller than a US dime' if estimated_diameter < 18 else 'about the size of a US dime' if estimated_diameter < 22 else 'larger than a US dime'}.
    - Severity: {severity}
    - Healing Potential: {healing_potential}
    """
    patient_instructions = """
    What to Do:
    - Keep the wound clean and dry.
    - Change the dressing daily or as told by your doctor.
    - Watch for signs like redness, swelling, or pain.
    - Contact your doctor if the wound doesn't improve in 3–5 days.
    """
    report_text = f"""
    About You:
    - Name: {patient_info.get('name', 'Unknown')}
    - Age: {patient_info.get('age', 'Unknown')}

    {wound_description}
    {patient_instructions}
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Wound Assessment Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for line in report_text.strip().split("\n"):
        pdf.multi_cell(0, 10, line.strip().encode('latin-1', 'replace').decode('latin-1'))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    vis_path = os.path.join(output_dir, f"wound_vis_{timestamp}.png")
    create_visualization_wrapper(image, pred_mask, vis_path)
    pdf.ln(10)
    pdf.image(vis_path, x=10, w=190)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Explanation: The left image shows your wound. The middle image shows the detected wound area. The right image highlights the wound with a green outline.")
    report_path = os.path.join(output_dir, f"patient_wound_report_{timestamp}.pdf")
    pdf.output(report_path)
    return report_path, vis_path

def analyze_image(image_path, unet_model_path, medsam_model_path, patient_info, output_dir='analysis_output'):
    ensure_directory(output_dir)

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    # Ensure 3-channel input (handle grayscale images)
    if len(img.shape) == 2:  # Grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Convert to RGB and normalize
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) / 255.0

    # Explicitly resize for model input
    img_resized = tf.image.resize(img_rgb, (128, 128), method='bilinear')
    img_resized = tf.expand_dims(img_resized, 0)  # Add batch dimension
    if img_resized.shape != (1, 128, 128, 3):
        raise ValueError(f"Resized image shape {img_resized.shape} does not match expected shape (1, 128, 128, 3)")

    # Load models
    unet_model = build_unet(input_shape=(128, 128, 3))
    unet_model.load_weights(unet_model_path)
    medsam_model = load_medsam_model(medsam_model_path)

    # Predict masks
    unet_pred = unet_model.predict([img_resized], verbose=0)[0, ..., 0]  # Pass as list to avoid Keras warning
    unet_mask = (unet_pred > 0.5).astype(np.uint8)

    medsam_mask = medsam_segment(img_rgb, medsam_model)
    medsam_mask = tf.image.resize(medsam_mask[..., None], (128, 128), method='nearest').numpy().squeeze().astype(np.uint8)

    combined_mask = np.logical_or(unet_mask, medsam_mask).astype(np.uint8)

    # Resize mask back to original size
    pred_mask_resized = tf.image.resize(combined_mask[..., None], img_rgb.shape[:2], method='nearest').numpy().squeeze().astype(np.uint8)

    # Clinical analysis
    severity, healing_potential, wound_area_mm2 = predict_healing_potential(pred_mask_resized, img_rgb)

    # Generate PDF report
    report_path, vis_path = generate_patient_report(img_rgb, pred_mask_resized, patient_info, severity, healing_potential, wound_area_mm2, output_dir)

    print(f"\n✅ Wound analysis complete.")
    print(f"- Report saved at: {report_path}")
    print(f"- Visualization saved at: {vis_path}")
    print(f"- Severity: {severity}")
    print(f"- Healing Potential: {healing_potential}")
    print(f"- Wound Area: {wound_area_mm2:.2f} mm²")

    return report_path, vis_path

@app.route("/report/<filename>")
def serve_report(filename):
    return send_from_directory(REPORT_FOLDER, filename)

@app.route("/upload", methods=["POST"])
def upload():
    # Validate file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
    if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
        return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
    
    # Validate file size (max 10MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    if file_size > 10 * 1024 * 1024:  # 10MB
        return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 400
    try:
        if "image" not in request.files:
            raise ValueError("No image file provided in the request")
        file = request.files["image"]
        name = request.form.get("name", "Unknown")
        age = request.form.get("age", "Unknown")
        use_medsam = request.form.get("use_medsam", "false").lower() == "true"

        filename = str(uuid.uuid4()) + ".png"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)

        # Validate the saved image
        img_check = cv2.imread(image_path)
        if img_check is None:
            raise ValueError(f"Failed to load the uploaded image: {image_path}. Ensure the file is a valid image (e.g., PNG, JPEG).")

        patient_info = {"name": name, "age": age}

        report_path, vis_path = analyze_image(
            image_path=image_path,
            unet_model_path=UNET_MODEL_PATH,
            medsam_model_path=MEDSAM_MODEL_PATH,
            patient_info=patient_info,
            output_dir=REPORT_FOLDER
        )

        return jsonify({
            "report_url": f"/report/{os.path.basename(report_path)}",
        })
    
    except Exception as e:
        import traceback
        print("❌ Error during image processing:", str(e))
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        import traceback
        print("❌ Error during image processing:", str(e))
        print("Traceback:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return render_template("wound-wisperer.html")

@app.route("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "unet": os.path.exists(UNET_MODEL_PATH),
            "medsam": os.path.exists(MEDSAM_MODEL_PATH)
        }
    })

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
