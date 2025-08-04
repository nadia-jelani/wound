#!/usr/bin/env python3
"""
Demo Wound Analysis System - Works without trained models
"""
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import cv2
import numpy as np
import time
from datetime import datetime
from config import *
from utils import setup_logging, ensure_directory, get_safe_filename, create_visualization

# Setup logging
logger = setup_logging(LOG_FILE, LOG_LEVEL)

app = Flask(__name__)
CORS(app)

def demo_analyze_image(image_path, output_dir):
    """Demo analysis function that simulates wound detection"""
    try:
        # Load and preprocess image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not load image")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_normalized = img_rgb.astype(np.float32) / 255.0
        
        # Create a simulated segmentation mask
        # This is just for demo purposes - in real system, this would come from the model
        height, width = img_normalized.shape[:2]
        
        # Create a random wound-like region (simulating model prediction)
        np.random.seed(int(time.time()))  # Use time as seed for variety
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Simulate wound detection with random regions
        num_regions = np.random.randint(1, 4)
        for _ in range(num_regions):
            # Random center and size
            center_x = np.random.randint(width // 4, 3 * width // 4)
            center_y = np.random.randint(height // 4, 3 * height // 4)
            radius = np.random.randint(min(width, height) // 8, min(width, height) // 4)
            
            # Create circular region
            y, x = np.ogrid[:height, :width]
            mask_region = (x - center_x)**2 + (y - center_y)**2 <= radius**2
            mask[mask_region] = 255
        
        # Add some noise to make it more realistic
        noise = np.random.random((height, width)) > 0.9
        mask[noise] = 255
        
        # Calculate metrics
        wound_area_px = np.sum(mask > 0)
        wound_area_mm2 = wound_area_px * (0.264 ** 2)  # Assuming 0.264 mm per pixel
        
        # Determine severity based on area
        if wound_area_mm2 < 50:
            severity = "Mild"
        elif wound_area_mm2 < 200:
            severity = "Moderate"
        else:
            severity = "Severe"
        
        # Determine healing potential
        if severity == "Mild":
            healing_potential = "High"
        elif severity == "Moderate":
            healing_potential = "Medium"
        else:
            healing_potential = "Low"
        
        # Create visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vis_path = os.path.join(output_dir, f"wound_vis_{timestamp}.png")
        create_visualization(img_normalized, mask, vis_path, "Demo Wound Analysis")
        
        # Create a simple report
        report_path = os.path.join(output_dir, f"demo_report_{timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(f"Demo Wound Analysis Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Image: {os.path.basename(image_path)}\n")
            f.write(f"Wound Area: {wound_area_mm2:.2f} mm²\n")
            f.write(f"Severity: {severity}\n")
            f.write(f"Healing Potential: {healing_potential}\n")
            f.write(f"Confidence: {np.random.uniform(0.7, 0.95):.2f}\n")
        
        return report_path, vis_path, mask, wound_area_mm2, severity, healing_potential
        
    except Exception as e:
        logger.error(f"Error in demo analysis: {str(e)}")
        raise

@app.route("/upload", methods=["POST"])
def upload():
    try:
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
        
        # Save uploaded file
        filename = get_safe_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        file.save(file_path)
        
        # Create output directory for this analysis
        analysis_id = f"demo_analysis_{timestamp}"
        output_dir = os.path.join(REPORT_FOLDER, analysis_id)
        ensure_directory(output_dir)
        
        # Perform demo analysis
        report_path, vis_path, mask, wound_area_mm2, severity, healing_potential = demo_analyze_image(file_path, output_dir)
        
        # Calculate confidence (simulated)
        confidence = np.random.uniform(0.7, 0.95)
        
        # Determine if it's a wound (simulated)
        is_wound = wound_area_mm2 > 20  # Threshold for demo
        
        # Create response data
        response_data = {
            'is_wound': is_wound,
            'confidence': float(confidence),
            'wound_area_mm2': float(wound_area_mm2),
            'severity': severity,
            'healing_potential': healing_potential,
            'visualization_url': f'/reports/{analysis_id}/wound_vis_{timestamp}.png',
            'report_url': f'/reports/{analysis_id}/demo_report_{timestamp}.txt'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "demo",
        "message": "Demo mode - no trained models required"
    })

@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/reports/<path:filename>")
def serve_analysis_report(filename):
    return send_from_directory(REPORT_FOLDER, filename)

if __name__ == "__main__":
    print("🚀 Starting Demo Wound Analysis System...")
    print("📝 This is a demo version that works without trained models")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("⚠️  Results are simulated for demonstration purposes")
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)