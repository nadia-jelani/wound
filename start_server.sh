#!/bin/bash

echo "🌐 Starting Web Server..."
echo "📁 Serving files from: $(pwd)"
echo "🔗 Access your webpage at: http://localhost:8000/simple_web_interface.html"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the HTTP server
python3 -m http.server 8000