#!/usr/bin/env python3
"""
Test script for Enhanced HAPTICA Application
Quick validation of enhanced features
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import time
from loguru import logger

# Test imports
try:
    from app import EnhancedHapticaEngine
    logger.info("✓ Enhanced HAPTICA imports successful")
except Exception as e:
    logger.error(f"✗ Import failed: {e}")
    sys.exit(1)

def test_enhanced_initialization():
    """Test enhanced engine initialization"""
    logger.info("Testing Enhanced HAPTICA initialization...")
    
    try:
        # Create engine
        haptica = EnhancedHapticaEngine()
        
        # Test configuration loading
        if haptica.config:
            logger.info("✓ Configuration loaded successfully")
        else:
            logger.warning("⚠ Configuration empty")
        
        # Test component initialization
        if haptica.initialize():
            logger.info("✓ Enhanced components initialized successfully")
            
            # Quick cleanup
            haptica._cleanup()
            return True
        else:
            logger.error("✗ Enhanced initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Enhanced initialization error: {e}")
        return False

def test_enhanced_features():
    """Test individual enhanced features"""
    logger.info("Testing enhanced features...")
    
    try:
        from vision.roi_calibrator import AdaptiveROICalibrator
        from vision.background_robustness import BackgroundRobustnessProcessor
        from core.state_machine import GestureStateMachine
        
        # Test ROI calibrator
        roi_calibrator = AdaptiveROICalibrator()
        test_bbox = (100, 100, 80, 80)
        test_frame_shape = (480, 640)
        adaptive_roi = roi_calibrator.get_adaptive_roi(test_bbox, test_frame_shape)
        logger.info(f"✓ ROI Calibrator: {adaptive_roi}")
        
        # Test background processor
        bg_processor = BackgroundRobustnessProcessor()
        logger.info("✓ Background Robustness Processor initialized")
        
        # Test state machine
        state_machine = GestureStateMachine()
        logger.info("✓ Gesture State Machine initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Enhanced features test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=== Enhanced HAPTICA Test Suite ===")
    
    # Test 1: Enhanced features
    if not test_enhanced_features():
        logger.error("Enhanced features test failed")
        return False
    
    # Test 2: Full initialization
    if not test_enhanced_initialization():
        logger.error("Enhanced initialization test failed")
        return False
    
    logger.info("=== All Enhanced Tests Passed! ===")
    logger.info("Enhanced HAPTICA is ready to run")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)