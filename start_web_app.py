#!/usr/bin/env python3
"""
Startup script for the Wound Analysis Web Application
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'opencv-python', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_models():
    """Check if trained models are available"""
    model_files = [
        'models/best_unet_wound_model.h5',
        'models/best_medsam_model.pth',
        'models/wound_classifier.h5'
    ]
    
    available_models = []
    for model_file in model_files:
        if Path(model_file).exists():
            available_models.append(model_file)
    
    return available_models

def start_demo_mode():
    """Start the application in demo mode"""
    print("🚀 Starting Demo Mode...")
    print("📝 This mode works without trained models")
    print("⚠️  Results are simulated for demonstration purposes")
    print()
    
    try:
        subprocess.run([sys.executable, "demo_analyze_wound.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Demo mode stopped by user")
    except Exception as e:
        print(f"❌ Error starting demo mode: {e}")

def start_full_mode():
    """Start the application in full mode with trained models"""
    print("🚀 Starting Full Mode...")
    print("🤖 This mode requires trained models")
    print()
    
    try:
        subprocess.run([sys.executable, "analyze_wound.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Full mode stopped by user")
    except Exception as e:
        print(f"❌ Error starting full mode: {e}")

def main():
    """Main startup function"""
    print("🩹 Wound Analysis System - Web Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return 1
    
    # Check for models
    available_models = check_models()
    
    print("\n📋 Available Options:")
    print("1. Demo Mode - Works without trained models (simulated results)")
    print("2. Full Mode - Requires trained models (real analysis)")
    print("3. Exit")
    
    if available_models:
        print(f"\n✅ Found {len(available_models)} trained model(s):")
        for model in available_models:
            print(f"   - {model}")
    else:
        print("\n⚠️  No trained models found. Demo mode recommended.")
    
    while True:
        try:
            choice = input("\n🎯 Select an option (1-3): ").strip()
            
            if choice == '1':
                start_demo_mode()
                break
            elif choice == '2':
                if not available_models:
                    print("❌ No trained models found. Please use demo mode or add models to the 'models/' directory.")
                    continue
                start_full_mode()
                break
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())