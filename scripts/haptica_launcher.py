#!/usr/bin/env python3
"""
HAPTICA Launcher - Choose Your Version
Interactive launcher for Standard and Enhanced HAPTICA
"""
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from loguru import logger

def show_welcome():
    """Show welcome message"""
    print("=" * 60)
    print("🎯 HAPTICA - Real-Time Hand Gesture Recognition")
    print("=" * 60)
    print()
    print("Welcome to your company-grade gesture recognition system!")
    print()
    print("Available options:")
    print("  1. Standard Version  - Stable, reliable, tested")
    print("  2. Enhanced Version  - Advanced features, adaptive ROI")
    print("  3. Test Components   - Verify system functionality")
    print("  4. View User Guide   - Complete operation instructions")
    print("  5. Exit")
    print()

def run_standard_version():
    """Run standard HAPTICA"""
    print("🚀 Starting Standard HAPTICA...")
    print()
    print("Features:")
    print("  • Real-time hand detection")
    print("  • Gesture classification")
    print("  • Action execution")
    print("  • Live visual feedback")
    print()
    print("Controls:")
    print("  • 'q' - Quit")
    print("  • 'd' - Toggle debug")
    print("  • 'f' - Toggle FPS")
    print()
    print("Press 'q' in the camera window to quit")
    print("Press Ctrl+C here to force quit")
    print()
    
    try:
        from main import HapticaEngine
        haptica = HapticaEngine()
        haptica.run()
    except KeyboardInterrupt:
        print("\n✅ Standard HAPTICA stopped by user")
    except Exception as e:
        print(f"❌ Standard HAPTICA error: {e}")

def run_enhanced_version():
    """Run enhanced HAPTICA"""
    print("🚀 Starting Enhanced HAPTICA...")
    print()
    print("Enhanced features:")
    print("  • Adaptive ROI calibration")
    print("  • Background robustness")
    print("  • Intent-aware state machine")
    print("  • Plugin-based actions")
    print("  • Advanced gesture processing")
    print()
    print("Controls:")
    print("  • 'q' - Quit")
    print("  • 'm' - Show metrics")
    print("  • 'r' - Reload config")
    print("  • 'e' - Emergency disable")
    print("  • 's' - Re-enable")
    print()
    
    try:
        from app import EnhancedHapticaEngine
        haptica = EnhancedHapticaEngine()
        haptica.run()
    except KeyboardInterrupt:
        print("\n✅ Enhanced HAPTICA stopped by user")
    except Exception as e:
        print(f"❌ Enhanced HAPTICA error: {e}")

def test_components():
    """Test system components"""
    print("🔧 Testing HAPTICA Components...")
    print()
    
    # Test camera
    print("1. Testing camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("   ✅ Camera detected and working")
            cap.release()
        else:
            print("   ❌ Camera not detected")
    except Exception as e:
        print(f"   ❌ Camera test failed: {e}")
    
    # Test model
    print("2. Testing model...")
    try:
        from pathlib import Path
        model_path = Path("models/hand_recognition_model.h5")
        if model_path.exists():
            print("   ✅ Model file found")
            # Test model loading
            from inference.predictor import GesturePredictor
            predictor = GesturePredictor(str(model_path), "config/labels.json")
            print("   ✅ Model loaded successfully")
        else:
            print("   ❌ Model file missing")
    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
    
    # Test configuration
    print("3. Testing configuration...")
    try:
        import json
        with open("config/labels.json", 'r') as f:
            labels = json.load(f)
        with open("config/actions.json", 'r') as f:
            actions = json.load(f)
        print("   ✅ Configuration files loaded")
        print(f"   ✅ {len(labels['labels'])} gesture classes configured")
        print(f"   ✅ {len(actions['gesture_actions'])} actions configured")
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
    
    # Test imports
    print("4. Testing imports...")
    try:
        from camera.video_stream import VideoStream
        from detection.hand_detector import HandDetector
        from inference.predictor import GesturePredictor
        print("   ✅ Core modules imported successfully")
        
        # Test enhanced modules
        from vision.roi_calibrator import AdaptiveROICalibrator
        from core.state_machine import GestureStateMachine
        print("   ✅ Enhanced modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
    
    print()
    print("Component testing complete!")
    input("Press Enter to continue...")

def show_user_guide():
    """Show user guide information"""
    print("📚 HAPTICA User Guide")
    print("=" * 40)
    print()
    print("Complete documentation available in: docs/USER_GUIDE.md")
    print()
    print("Quick Reference:")
    print()
    print("🎮 Available Gestures:")
    print("  ✋ PALM     → Spacebar (Play/Pause)")
    print("  ✊ FIST     → Ctrl+C (Copy)")
    print("  👍 THUMB    → Volume Up")
    print("  👆 INDEX    → Left Click")
    print("  👌 OK       → Enter Key")
    print("  🤏 C_SHAPE → API Call")
    print()
    print("💡 Best Practices:")
    print("  • Sit 2-3 feet from camera")
    print("  • Ensure good lighting")
    print("  • Keep background simple")
    print("  • Hold gestures steady for 0.5 seconds")
    print()
    print("🔧 Customization:")
    print("  • Edit config/actions.json for custom actions")
    print("  • Modify config/labels.json for thresholds")
    print("  • Check logs/ directory for debugging")
    print()
    input("Press Enter to continue...")

def main():
    """Main launcher function"""
    while True:
        show_welcome()
        
        try:
            choice = input("Choose an option (1-5): ").strip()
            
            if choice == '1':
                run_standard_version()
            elif choice == '2':
                run_enhanced_version()
            elif choice == '3':
                test_components()
            elif choice == '4':
                show_user_guide()
            elif choice == '5':
                print("👋 Goodbye! Thanks for using HAPTICA!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using HAPTICA!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()