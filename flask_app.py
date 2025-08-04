from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# HTML template (you could also use template files)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wound Analysis Web App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-form {
            margin: 20px 0;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Flask Wound Analysis App</h1>
        <div class="status">
            <strong>Server Status:</strong> Flask app running on {{ url }}
        </div>
        
        <form class="upload-form" action="/analyze" method="POST" enctype="multipart/form-data">
            <p>Upload an image for wound analysis:</p>
            <input type="file" name="image" accept="image/*" required>
            <br><br>
            <button type="submit">Analyze Wound</button>
        </form>
        
        <div class="result">
            <h3>Available Python Scripts in Workspace:</h3>
            <ul>
                {% for script in scripts %}
                <li>{{ script }}</li>
                {% endfor %}
            </ul>
            <p><em>These scripts can be integrated with this web interface for real-time analysis.</em></p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    # Get list of Python scripts in the workspace
    scripts = [f for f in os.listdir('/workspace') if f.endswith('.py')]
    return render_template_string(HTML_TEMPLATE, 
                                url=request.url_root, 
                                scripts=scripts)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Here you would integrate with your wound analysis scripts
    # For now, return a mock response
    return jsonify({
        'status': 'success',
        'filename': file.filename,
        'message': 'Image received successfully! Integration with wound analysis scripts pending.',
        'available_analyzers': [
            'wound_analyze.py',
            'wound_checker.py', 
            'analyze_wound.py',
            'test_wound_progress.py'
        ]
    })

if __name__ == '__main__':
    print("Starting Flask web server...")
    print("Access the webpage at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)