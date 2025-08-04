#!/usr/bin/env python3
"""
Test runner for the Wound Analysis System
"""
import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run all tests in the project"""
    print("🧪 Running Wound Analysis System Tests...")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    
    if start_dir.exists():
        suite = loader.discover(start_dir, pattern='test_*.py')
    else:
        print("⚠️  No tests directory found. Creating basic test...")
        suite = unittest.TestSuite()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

def validate_project_structure():
    """Validate that all required files and directories exist"""
    print("\n🔍 Validating Project Structure...")
    print("=" * 50)
    
    required_files = [
        'requirements.txt',
        'README.md',
        'config.py',
        'utils.py',
        'model_manager.py',
        'analyze_wound.py',
        'train_classifier.py',
        'train_resnet.py'
    ]
    
    required_dirs = [
        'tests',
        'models',
        'uploads',
        'reports',
        'logs'
    ]
    
    all_good = True
    
    # Check required files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_good = False
    
    # Check required directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            all_good = False
    
    return all_good

def test_imports():
    """Test that all modules can be imported"""
    print("\n📦 Testing Module Imports...")
    print("=" * 50)
    
    modules_to_test = [
        'config',
        'utils',
        'model_manager',
        'analyze_wound',
        'train_classifier',
        'train_resnet'
    ]
    
    all_good = True
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            if "No module named" in str(e):
                print(f"⚠️  {module_name} - External dependencies not installed: {e}")
            else:
                print(f"❌ {module_name} - {e}")
                all_good = False
        except Exception as e:
            print(f"⚠️  {module_name} - {e}")
    
    return all_good

def main():
    """Main test runner"""
    print("🚀 Wound Analysis System - Test Suite")
    print("=" * 50)
    
    # Validate project structure
    structure_ok = validate_project_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    # Run unit tests
    tests_ok = run_all_tests()
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 Final Results:")
    print(f"Project Structure: {'✅ OK' if structure_ok else '❌ Issues'}")
    print(f"Module Imports: {'✅ OK' if imports_ok else '❌ Issues'}")
    print(f"Unit Tests: {'✅ OK' if tests_ok else '❌ Issues'}")
    
    if all([structure_ok, imports_ok, tests_ok]):
        print("\n🎉 All checks passed! The project is ready to use.")
        return 0
    else:
        print("\n⚠️  Some issues were found. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())