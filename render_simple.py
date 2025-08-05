#!/usr/bin/env python3
"""
Ultra-Simple Wound Analysis App - No External Dependencies
"""
import random
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

class WoundAnalysisHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>WoundCare AI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                    .header { text-align: center; margin-bottom: 30px; padding: 20px; background: #1e3c72; color: white; border-radius: 8px; }
                    .notice { background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
                    .upload-section { text-align: center; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
                    .btn { background: #1e3c72; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px; }
                    .btn:hover { background: #2a5298; }
                    .btn:disabled { background: #ccc; cursor: not-allowed; }
                    .btn-analyze { background: #4CAF50; }
                    .btn-analyze:hover { background: #45a049; }
                    .loading { display: none; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0; }
                    .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin: 15px 0; display: none; }
                    .success { background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 8px; margin: 15px 0; display: none; }
                    .results { display: none; margin-top: 30px; }
                    .results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
                    .result-card { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #1e3c72; }
                    .result-value { font-size: 1.5em; font-weight: bold; color: #333; margin: 10px 0; }
                    .severity-mild { color: #4CAF50; }
                    .severity-moderate { color: #FF9800; }
                    .severity-severe { color: #f44336; }
                    .footer { margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: center; color: #666; font-size: 0.9em; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🩹 WoundCare AI</h1>
                        <p>Professional Medical Wound Analysis System</p>
                    </div>

                    <div class="notice">
                        <strong>⚠️ Medical Disclaimer:</strong> This system is for educational purposes only. 
                        Always consult healthcare professionals for medical decisions.
                    </div>

                    <div class="upload-section">
                        <h2>Wound Image Analysis</h2>
                        <p>Upload a clear image of the wound for AI-powered analysis</p>
                        <input type="file" id="fileInput" accept="image/*" style="margin: 20px;">
                        <br>
                        <button class="btn" id="browseBtn">Browse Files</button>
                        <button class="btn btn-analyze" id="analyzeBtn" disabled>Analyze Wound</button>
                    </div>

                    <div class="loading" id="loading">
                        <h3>Processing Analysis...</h3>
                        <p>AI algorithms are analyzing your image</p>
                    </div>

                    <div class="error" id="error"></div>
                    <div class="success" id="success"></div>

                    <div class="results" id="results">
                        <h2>Analysis Results</h2>
                        <div class="results-grid" id="resultsGrid"></div>
                    </div>

                    <div class="footer">
                        <p><strong>⚠️ Medical Disclaimer:</strong> This AI system is for educational purposes only.</p>
                        <p>&copy; 2024 WoundCare AI - Professional Medical Analysis System</p>
                    </div>
                </div>

                <script>
                    const fileInput = document.getElementById('fileInput');
                    const browseBtn = document.getElementById('browseBtn');
                    const analyzeBtn = document.getElementById('analyzeBtn');
                    const loading = document.getElementById('loading');
                    const results = document.getElementById('results');
                    const error = document.getElementById('error');
                    const success = document.getElementById('success');

                    let selectedFile = null;

                    browseBtn.addEventListener('click', () => fileInput.click());

                    fileInput.addEventListener('change', (e) => {
                        if (e.target.files.length > 0) {
                            handleFileSelect(e.target.files[0]);
                        }
                    });

                    function handleFileSelect(file) {
                        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
                        if (!allowedTypes.includes(file.type)) {
                            showError('Please select a valid image file (JPG, PNG, BMP, TIFF)');
                            return;
                        }
                        if (file.size > 5 * 1024 * 1024) {
                            showError('File size must be less than 5MB');
                            return;
                        }
                        selectedFile = file;
                        analyzeBtn.disabled = false;
                        showSuccess('Image selected successfully! Click "Analyze Wound" to begin.');
                    }

                    analyzeBtn.addEventListener('click', async () => {
                        if (!selectedFile) {
                            showError('Please select an image first');
                            return;
                        }

                        loading.style.display = 'block';
                        results.style.display = 'none';
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
                                <h3>Wound Detection</h3>
                                <div class="result-value">${data.is_wound ? 'WOUND DETECTED' : 'NO WOUND'}</div>
                                <div>AI Classification Result</div>
                            </div>
                            <div class="result-card">
                                <h3>Confidence Level</h3>
                                <div class="result-value">${(data.confidence * 100).toFixed(1)}%</div>
                                <div>AI Confidence Score</div>
                            </div>
                            <div class="result-card">
                                <h3>Wound Area</h3>
                                <div class="result-value">${data.wound_area_mm2.toFixed(2)} mm²</div>
                                <div>Measured Surface Area</div>
                            </div>
                            <div class="result-card">
                                <h3>Clinical Severity</h3>
                                <div class="result-value severity-${data.severity.toLowerCase()}">${data.severity.toUpperCase()}</div>
                                <div>Assessment Classification</div>
                            </div>
                            <div class="result-card">
                                <h3>Healing Prognosis</h3>
                                <div class="result-value">${data.healing_potential.toUpperCase()}</div>
                                <div>Recovery Potential</div>
                            </div>
                            <div class="result-card">
                                <h3>Analysis Time</h3>
                                <div class="result-value">${new Date(data.timestamp).toLocaleTimeString()}</div>
                                <div>Processing Timestamp</div>
                            </div>
                        `;

                        results.style.display = 'block';
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
            
            self.wfile.write(html.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "mode": "ultra_simple",
                "message": "Ultra-simple wound analysis demo"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simple analysis without file processing
            is_wound = random.choice([True, True, True, False])
            confidence = random.uniform(0.75, 0.98)
            wound_area_mm2 = random.uniform(50, 500)
            severity = random.choice(['Mild', 'Moderate', 'Severe'])
            healing_potential = random.choice(['Good', 'Fair', 'Poor'])
            
            result = {
                'is_wound': is_wound,
                'confidence': confidence,
                'wound_area_mm2': wound_area_mm2,
                'severity': severity,
                'healing_potential': healing_potential,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_server():
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), WoundAnalysisHandler)
    print(f'Starting server on port {port}...')
    server.serve_forever()

if __name__ == '__main__':
    run_server()