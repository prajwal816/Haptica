#!/usr/bin/env python3
"""
HAPTICA Setup Script
Automated setup and validation for HAPTICA system
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_system_dependencies():
    """Check system-level dependencies"""
    print("\n🔍 Checking system dependencies...")
    
    dependencies = {
        'Windows': ['pip'],
        'Linux': ['pip', 'libgl1-mesa-glx', 'python3-tk'],
        'Darwin': ['pip']  # macOS
    }
    
    system = platform.system()
    required = dependencies.get(system, ['pip'])
    
    for dep in required:
        try:
            if dep == 'pip':
                subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                             check=True, capture_output=True)
            print(f"✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ {dep} not found")
            return False
    
    return True


def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python packages...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def check_model_file():
    """Check if model file exists"""
    model_path = Path("models/hand_recognition_model.h5")
    if model_path.exists():
        print(f"✅ Model file found: {model_path}")
        return True
    else:
        print(f"❌ Model file not found: {model_path}")
        print("   Please ensure the trained model is in the models/ directory")
        return False


def check_camera():
    """Test camera access"""
    print("\n📹 Testing camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera accessible")
                cap.release()
                return True
        cap.release()
        print("❌ Camera not accessible")
        return False
    except ImportError:
        print("❌ OpenCV not installed")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['logs', 'temp', 'exports']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")


def validate_config():
    """Validate configuration files"""
    print("\n⚙️ Validating configuration...")
    
    config_files = [
        'config/labels.json',
        'config/actions.json'
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} missing")
            return False
    
    return True


def run_basic_test():
    """Run basic system test"""
    print("\n🧪 Running basic system test...")
    
    try:
        # Test imports
        sys.path.append('src')
        from inference.predictor import GesturePredictor
        from preprocessing.transforms import ImageTransforms
        
        print("✅ Core modules importable")
        
        # Test model loading
        if Path("models/hand_recognition_model.h5").exists():
            predictor = GesturePredictor(
                "models/hand_recognition_model.h5",
                "config/labels.json"
            )
            print("✅ Model loads successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 HAPTICA Setup & Validation")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("System Dependencies", check_system_dependencies),
        ("Python Packages", install_requirements),
        ("Model File", check_model_file),
        ("Camera Access", check_camera),
        ("Directories", create_directories),
        ("Configuration", validate_config),
        ("System Test", run_basic_test)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Setup Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {name}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 HAPTICA is ready to run!")
        print("   Start with: python src/main.py")
    else:
        print("\n⚠️  Please fix the failed checks before running HAPTICA")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())