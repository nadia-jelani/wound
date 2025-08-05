#!/usr/bin/env python3
"""
Setup script for the Wound Analysis System
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating project directories...")
    directories = [
        'models',
        'uploads', 
        'reports',
        'logs',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")
    
    return True

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# Wound Analysis System Environment Variables\n")
            f.write("FLASK_DEBUG=False\n")
            f.write("FLASK_HOST=0.0.0.0\n")
            f.write("FLASK_PORT=5000\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("DATASET_PATH=./dataset\n")
            f.write("MODEL_SAVE_PATH=./models\n")
            f.write("UPLOAD_FOLDER=./uploads\n")
            f.write("REPORT_FOLDER=./reports\n")
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    return True

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    if not run_command("python run_tests.py", "Running test suite"):
        print("⚠️  Tests failed, but continuing with setup...")
        return True  # Continue even if tests fail
    return True

def main():
    """Main setup function"""
    print("🚀 Wound Analysis System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Place your trained models in the 'models/' directory")
    print("2. Place your dataset in the 'dataset/' directory")
    print("3. Run the web application: python analyze_wound.py")
    print("4. Or run the GUI application: python wound_checker.py")
    print("\n📚 For more information, see README.md")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())