#!/usr/bin/env python3
"""
Simple Wound Analysis Web Application - Minimal Dependencies
"""
import os
import json
import base64
import time
import random
from datetime import datetime
from pathlib import Path

# Simple HTTP server (no external dependencies)
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    import cgi
except ImportError:
    print("❌ Basic HTTP server modules not available")
    exit(1)

class WoundAnalysisHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = self.get_html_content()
            self.wfile.write(html_content.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "mode": "simple_demo",
                "message": "Simple demo mode - no external dependencies"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """Handle POST requests for file upload"""
        if self.path == '/upload':
            try:
                # Parse multipart form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                # Get uploaded file
                if 'file' not in form:
                    self.send_error_response('No file provided')
                    return
                
                fileitem = form['file']
                if not fileitem.filename:
                    self.send_error_response('No file selected')
                    return
                
                # Validate file type
                filename = fileitem.filename.lower()
                if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']):
                    self.send_error_response('Invalid file type. Please upload an image.')
                    return
                
                # Simulate analysis (demo mode)
                analysis_result = self.simulate_analysis(fileitem.filename)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                self.wfile.write(json.dumps(analysis_result).encode())
                
            except Exception as e:
                self.send_error_response(f'Analysis failed: {str(e)}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def simulate_analysis(self, filename):
        """Simulate wound analysis (demo mode)"""
        # Simulate processing time
        time.sleep(1)
        
        # Generate random analysis results
        wound_area = random.uniform(10, 500)
        
        if wound_area < 50:
            severity = "Mild"
            healing_potential = "High"
        elif wound_area < 200:
            severity = "Moderate"
            healing_potential = "Medium"
        else:
            severity = "Severe"
            healing_potential = "Low"
        
        confidence = random.uniform(0.7, 0.95)
        is_wound = wound_area > 20
        
        return {
            'is_wound': is_wound,
            'confidence': round(confidence, 3),
            'wound_area_mm2': round(wound_area, 2),
            'severity': severity,
            'healing_potential': healing_potential,
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }
    
    def send_error_response(self, message):
        """Send error response"""
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
    
    def get_html_content(self):
        """Get the HTML content for the web interface"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wound Analysis System - Demo</title>
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
            max-width: 800px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩹 Wound Analysis System</h1>
            <p>AI-Powered Wound Detection and Analysis (Demo Mode)</p>
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
                <p>This may take a few moments</p>
            </div>

            <div class="error" id="error"></div>
            <div class="success" id="success"></div>

            <div class="results-section" id="resultsSection">
                <h2>Analysis Results</h2>
                
                <div class="results-grid" id="resultsGrid">
                    <!-- Results will be displayed here -->
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

            resultsSection.style.display = 'block';
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
    
    def log_message(self, format, *args):
        """Override to suppress logging"""
        pass

def main():
    """Main function to start the server"""
    port = 5000
    
    print("🚀 Starting Simple Wound Analysis Web Application...")
    print("📝 Demo Mode - No external dependencies required")
    print(f"🌐 Web interface will be available at: http://localhost:{port}")
    print("⚠️  Results are simulated for demonstration purposes")
    print("\n💡 Press Ctrl+C to stop the server")
    
    try:
        server = HTTPServer(('localhost', port), WoundAnalysisHandler)
        print(f"\n✅ Server started successfully on port {port}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()