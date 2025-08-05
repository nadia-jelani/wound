#!/usr/bin/env python3
"""
Simplified Wound Analysis Web Application for Easy Deployment
"""
import os
import json
import time
import random
import base64
import io
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Settings
IMG_SIZE = (128, 128)
SCALE_MM_PER_PIXEL = 0.1

def analyze_wound_image_simple(image_path):
    """Simplified wound analysis without heavy dependencies"""
    try:
        # Load image with PIL
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize for processing
            img_resized = img.resize(IMG_SIZE)
            
            # Convert to array for analysis
            img_array = list(img_resized.getdata())
            
            # Simple analysis based on image brightness
            avg_brightness = sum(sum(pixel) / 3 for pixel in img_array) / len(img_array)
            
            # Simulate wound detection based on image characteristics
            if avg_brightness < 100:  # Darker areas might indicate wounds
                is_wound = True
                confidence = random.uniform(0.7, 0.95)
                area_mm = random.uniform(50, 300)
            else:
                is_wound = random.choice([True, False])
                confidence = random.uniform(0.6, 0.9)
                area_mm = random.uniform(10, 200)
            
            # Determine severity and healing potential
            if area_mm < 50:
                severity = "Mild"
                healing_potential = "High"
            elif area_mm < 200:
                severity = "Moderate"
                healing_potential = "Medium"
            else:
                severity = "Severe"
                healing_potential = "Low"
            
            # Generate simple visualizations
            visualizations = generate_simple_visualizations(img)
            
            return {
                'is_wound': is_wound,
                'confidence': round(confidence, 3),
                'wound_area_mm2': round(area_mm, 2),
                'perimeter_mm': round(area_mm * 0.5, 2),  # Rough estimate
                'irregularity': round(random.uniform(1.2, 2.5), 3),
                'severity': severity,
                'healing_potential': healing_potential,
                'timestamp': datetime.now().isoformat(),
                'visualizations': visualizations
            }
            
    except Exception as e:
        return {
            'error': f'Analysis failed: {str(e)}',
            'is_wound': False,
            'confidence': 0,
            'wound_area_mm2': 0,
            'severity': 'Error',
            'healing_potential': 'N/A',
            'timestamp': datetime.now().isoformat()
        }

def generate_simple_visualizations(original_img):
    """Generate simple visualizations using PIL only"""
    visualizations = {}
    
    try:
        # 1. Original Image
        original_b64 = image_to_base64(original_img)
        visualizations['original'] = original_b64
        
        # 2. Create a simple "mask" (just a colored overlay)
        mask_img = original_img.copy()
        mask_draw = ImageDraw.Draw(mask_img)
        
        # Draw a simple rectangle as "wound area"
        width, height = mask_img.size
        rect_width = width // 3
        rect_height = height // 3
        x1 = (width - rect_width) // 2
        y1 = (height - rect_height) // 2
        x2 = x1 + rect_width
        y2 = y1 + rect_height
        
        mask_draw.rectangle([x1, y1, x2, y2], fill=(0, 255, 0, 128), outline=(0, 255, 0))
        mask_b64 = image_to_base64(mask_img)
        visualizations['mask'] = mask_b64
        
        # 3. Create overlay
        overlay_img = original_img.copy()
        overlay_draw = ImageDraw.Draw(overlay_img)
        overlay_draw.rectangle([x1, y1, x2, y2], fill=(255, 0, 0, 100), outline=(255, 0, 0))
        
        # Add text
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        overlay_draw.text((10, 10), "Wound Analysis", fill=(255, 255, 255), font=font)
        overlay_draw.text((10, 30), f"Area: {random.randint(50, 200)} mm²", fill=(255, 255, 255), font=font)
        
        overlay_b64 = image_to_base64(overlay_img)
        visualizations['overlay'] = overlay_b64
        
        # 4. Create simple heatmap (just a colored version)
        heatmap_img = original_img.copy()
        heatmap_img = heatmap_img.convert('RGB')
        # Apply a simple color transformation
        heatmap_data = heatmap_img.getdata()
        heatmap_data = [(r, g//2, b//2) for r, g, b in heatmap_data]
        heatmap_img.putdata(heatmap_data)
        heatmap_b64 = image_to_base64(heatmap_img)
        visualizations['heatmap'] = heatmap_b64
        
        # 5. Create simple analysis chart
        chart_b64 = generate_simple_chart()
        visualizations['chart'] = chart_b64
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
    
    return visualizations

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return ""

def generate_simple_chart():
    """Generate a simple text-based chart"""
    try:
        # Create a simple chart image
        chart_img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(chart_img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add chart title and data
        draw.text((10, 10), "Wound Analysis Results", fill='black', font=font)
        draw.text((10, 40), f"Area: {random.randint(50, 200)} mm²", fill='blue', font=font)
        draw.text((10, 70), f"Severity: {random.choice(['Mild', 'Moderate', 'Severe'])}", fill='red', font=font)
        draw.text((10, 100), f"Confidence: {random.randint(70, 95)}%", fill='green', font=font)
        draw.text((10, 130), "Analysis Complete", fill='black', font=font)
        
        return image_to_base64(chart_img)
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        return ""

# HTML template (same as before)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wound Analysis System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .upload-section {
            text-align: center;
            margin-bottom: 40px;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 60px 20px;
            margin: 20px 0;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f8f9ff;
        }

        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
            transform: translateY(-2px);
        }

        .upload-icon {
            font-size: 4em;
            color: #667eea;
            margin-bottom: 20px;
        }

        .upload-text {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 15px;
        }

        .upload-hint {
            font-size: 0.9em;
            color: #999;
        }

        .file-input {
            display: none;
        }

        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 20px 10px;
        }

        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .upload-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .results-section {
            display: none;
            margin-top: 40px;
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .result-card {
            background: #f8f9ff;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .result-card:hover {
            transform: translateY(-5px);
        }

        .result-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .result-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }

        .result-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .visualization-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .visualization-card {
            background: #f8f9ff;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            text-align: center;
        }

        .visualization-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .visualization-image {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #ffe6e6;
            color: #d63031;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            display: none;
        }

        .success {
            background: #e6ffe6;
            color: #00b894;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            display: none;
        }

        .demo-notice {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #ffeaa7;
        }

        .footer {
            background: #f8f9ff;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }

        .tab-buttons {
            display: flex;
            justify-content: center;
            margin: 20px 0;
            gap: 10px;
        }

        .tab-btn {
            background: #f0f2ff;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .tab-btn.active {
            background: #667eea;
            color: white;
        }

        .tab-btn:hover {
            transform: translateY(-2px);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩹 Wound Analysis System</h1>
            <p>AI-Powered Wound Detection and Analysis</p>
        </div>

        <div class="main-content">
            <div class="demo-notice">
                <strong>⚠️ Demo Mode:</strong> This is a demonstration version with simulated results.
                No actual AI analysis is performed. Results are randomly generated for testing purposes.
            </div>

            <div class="upload-section">
                <h2>Upload Wound Image</h2>
                <p>Upload a clear image of the wound for analysis</p>

                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📷</div>
                    <div class="upload-text">Click to select an image file</div>
                    <div class="upload-hint">Supports: JPG, PNG, BMP, TIFF</div>
                </div>

                <input type="file" id="fileInput" class="file-input" accept="image/*">

                <div>
                    <button class="upload-btn" id="browseBtn">Browse Files</button>
                    <button class="upload-btn" id="analyzeBtn" disabled>Analyze Wound</button>
                </div>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <h3>Analyzing your image...</h3>
                <p>Processing image and generating analysis</p>
            </div>

            <div class="error" id="error"></div>
            <div class="success" id="success"></div>

            <div class="results-section" id="resultsSection">
                <h2>Analysis Results</h2>

                <div class="tab-buttons">
                    <button class="tab-btn active" onclick="showTab('summary')">Summary</button>
                    <button class="tab-btn" onclick="showTab('visualizations')">Visualizations</button>
                    <button class="tab-btn" onclick="showTab('details')">Details</button>
                </div>

                <div class="tab-content active" id="summary">
                    <div class="results-grid" id="resultsGrid">
                        <!-- Results will be displayed here -->
                    </div>
                </div>

                <div class="tab-content" id="visualizations">
                    <div class="visualization-grid" id="visualizationGrid">
                        <!-- Visualizations will be displayed here -->
                    </div>
                </div>

                <div class="tab-content" id="details">
                    <div class="results-grid" id="detailsGrid">
                        <!-- Detailed results will be displayed here -->
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>⚠️ This system is for research and educational purposes only. Always consult healthcare professionals for medical decisions.</p>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const resultsSection = document.getElementById('resultsSection');
        const error = document.getElementById('error');
        const success = document.getElementById('success');

        let selectedFile = null;

        // Click to browse
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        function handleFileSelect(file) {
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
            if (!allowedTypes.includes(file.type)) {
                showError('Please select a valid image file (JPG, PNG, BMP, TIFF)');
                return;
            }

            selectedFile = file;
            analyzeBtn.disabled = false;
            showSuccess('Image selected successfully! Click "Analyze Wound" to proceed.');
        }

        // Analyze button
        analyzeBtn.addEventListener('click', async () => {
            if (!selectedFile) {
                showError('Please select an image first');
                return;
            }

            // Show loading
            loading.style.display = 'block';
            resultsSection.style.display = 'none';
            error.style.display = 'none';
            success.style.display = 'none';
            analyzeBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('file', selectedFile);

                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    showResults(result);
                    showSuccess('Analysis completed successfully!');
                } else {
                    const errorData = await response.json();
                    showError(errorData.error || 'Analysis failed. Please try again.');
                }
            } catch (err) {
                showError('Network error. Please check your connection and try again.');
            } finally {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        });

        function showResults(data) {
            const resultsGrid = document.getElementById('resultsGrid');
            const visualizationGrid = document.getElementById('visualizationGrid');
            const detailsGrid = document.getElementById('detailsGrid');

            // Summary results
            resultsGrid.innerHTML = `
                <div class="result-card">
                    <h3>Classification</h3>
                    <div class="result-value">${data.is_wound ? 'Wound' : 'Non-Wound'}</div>
                    <div class="result-label">Detection Result</div>
                </div>
                <div class="result-card">
                    <h3>Confidence</h3>
                    <div class="result-value">${(data.confidence * 100).toFixed(1)}%</div>
                    <div class="result-label">AI Confidence Level</div>
                </div>
                <div class="result-card">
                    <h3>Wound Area</h3>
                    <div class="result-value">${data.wound_area_mm2.toFixed(2)} mm²</div>
                    <div class="result-label">Estimated Area</div>
                </div>
                <div class="result-card">
                    <h3>Severity</h3>
                    <div class="result-value">${data.severity}</div>
                    <div class="result-label">Assessment Level</div>
                </div>
                <div class="result-card">
                    <h3>Healing Potential</h3>
                    <div class="result-value">${data.healing_potential}</div>
                    <div class="result-label">Recovery Outlook</div>
                </div>
                <div class="result-card">
                    <h3>Analysis Time</h3>
                    <div class="result-value">${new Date(data.timestamp).toLocaleTimeString()}</div>
                    <div class="result-label">Timestamp</div>
                </div>
            `;

            // Visualizations
            if (data.visualizations && Object.keys(data.visualizations).length > 0) {
                visualizationGrid.innerHTML = `
                    <div class="visualization-card">
                        <h3>Original Image</h3>
                        <img src="${data.visualizations.original}" alt="Original Image" class="visualization-image">
                    </div>
                    <div class="visualization-card">
                        <h3>Segmentation Mask</h3>
                        <img src="${data.visualizations.mask}" alt="Segmentation Mask" class="visualization-image">
                    </div>
                    <div class="visualization-card">
                        <h3>Overlay Analysis</h3>
                        <img src="${data.visualizations.overlay}" alt="Overlay Analysis" class="visualization-image">
                    </div>
                    <div class="visualization-card">
                        <h3>Heatmap</h3>
                        <img src="${data.visualizations.heatmap}" alt="Heatmap" class="visualization-image">
                    </div>
                    <div class="visualization-card">
                        <h3>Analysis Chart</h3>
                        <img src="${data.visualizations.chart}" alt="Analysis Chart" class="visualization-image">
                    </div>
                `;
            }

            // Detailed results
            detailsGrid.innerHTML = `
                <div class="result-card">
                    <h3>Perimeter</h3>
                    <div class="result-value">${data.perimeter_mm ? data.perimeter_mm.toFixed(2) : 'N/A'} mm</div>
                    <div class="result-label">Wound Perimeter</div>
                </div>
                <div class="result-card">
                    <h3>Irregularity</h3>
                    <div class="result-value">${data.irregularity ? data.irregularity.toFixed(3) : 'N/A'}</div>
                    <div class="result-label">Shape Irregularity Index</div>
                </div>
                <div class="result-card">
                    <h3>Scale Factor</h3>
                    <div class="result-value">0.1 mm/pixel</div>
                    <div class="result-label">Measurement Scale</div>
                </div>
                <div class="result-card">
                    <h3>Processing Details</h3>
                    <div class="result-value">Simplified</div>
                    <div class="result-label">Analysis Type</div>
                </div>
            `;

            resultsSection.style.display = 'block';
        }

        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));

            // Remove active class from all tab buttons
            const tabButtons = document.querySelectorAll('.tab-btn');
            tabButtons.forEach(btn => btn.classList.remove('active'));

            // Show selected tab content
            document.getElementById(tabName).classList.add('active');

            // Add active class to clicked button
            event.target.classList.add('active');
        }

        function showError(message) {
            error.textContent = message;
            error.style.display = 'block';
            success.style.display = 'none';
        }

        function showSuccess(message) {
            success.textContent = message;
            success.style.display = 'block';
            error.style.display = 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "simple_demo",
        "message": "Simplified wound analysis demo"
    })

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save file temporarily
        filename = f"wound_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Analyze the image
        result = analyze_wound_image_simple(filepath)
        
        # Clean up temporary file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)