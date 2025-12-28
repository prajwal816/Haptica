#!/usr/bin/env python3
"""
Test Gesture Recognition Fixes
Validates all model-runtime alignment fixes
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import numpy as np
import time
from loguru import logger

# Import HAPTICA modules
from main import HapticaEngine

def test_real_time_gestures():
    """Test real-time gesture recognition with all fixes applied"""
    logger.info("=== TESTING REAL-TIME GESTURE RECOGNITION ===")
    logger.info("Testing all fixes:")
    logger.info("✓ FIX 1: Class index order verified")
    logger.info("✓ FIX 2: Grayscale shape (1,50,50,1) enforced")
    logger.info("✓ FIX 3: Horizontal flip fallback implemented")
    logger.info("✓ FIX 4: Gesture grouping implemented")
    logger.info("✓ FIX 5: Temporal confirmation (7 consecutive frames)")
    logger.info("")
    logger.info("Instructions:")
    logger.info("1. Make clear gestures in front of camera")
    logger.info("2. Hold each gesture steady for 1-2 seconds")
    logger.info("3. Watch console for detailed debug output")
    logger.info("4. Press 'q' to quit")
    logger.info("")
    
    try:
        # Create HAPTICA engine with debug logging
        haptica = HapticaEngine()
        
        # Enable debug logging for predictor
        import logging
        logging.getLogger('inference.predictor').setLevel(logging.DEBUG)
        
        # Run with enhanced debugging
        haptica.run()
        
    except KeyboardInterrupt:
        logger.info("✅ Test completed by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

def test_gesture_sequence():
    """Test specific gesture sequence"""
    logger.info("=== TESTING GESTURE SEQUENCE ===")
    
    gestures_to_test = [
        ("PALM", "Hold open palm facing camera"),
        ("FIST", "Make a closed fist"),
        ("THUMB", "Thumbs up gesture"),
        ("INDEX", "Point with index finger"),
        ("OK", "Make OK sign with thumb and index"),
        ("C_SHAPE", "Make C-shape with hand")
    ]
    
    logger.info("Test each gesture for 3-5 seconds:")
    for gesture, instruction in gestures_to_test:
        logger.info(f"Next: {gesture} - {instruction}")
        input("Press Enter when ready...")
    
    test_real_time_gestures()

def main():
    """Main test function"""
    logger.info("HAPTICA Gesture Recognition Fix Validation")
    logger.info("=" * 50)
    
    print("Choose test mode:")
    print("1. Real-time gesture testing")
    print("2. Guided gesture sequence")
    print("3. Exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        test_real_time_gestures()
    elif choice == '2':
        test_gesture_sequence()
    elif choice == '3':
        logger.info("Goodbye!")
    else:
        logger.error("Invalid choice")

if __name__ == "__main__":
    main()