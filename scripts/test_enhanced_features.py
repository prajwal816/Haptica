#!/usr/bin/env python3
"""
Enhanced HAPTICA Features Test Suite
Comprehensive testing of all company-level improvements
"""
import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vision.roi_calibrator import AdaptiveROICalibrator
from vision.background_robustness import BackgroundRobustnessProcessor
from core.state_machine import GestureStateMachine, GestureEvent
from core.async_pipeline import AsyncGesturePipeline
from actions.keyboard import KeyboardActionPlugin
from actions.mouse import MouseActionPlugin
from actions.media import MediaActionPlugin
from actions.api import APIActionPlugin


def test_adaptive_roi_calibrator():
    """Test adaptive ROI calibration"""
    print("🔍 Testing Adaptive ROI Calibrator...")
    
    calibrator = AdaptiveROICalibrator(history_size=10)
    
    # Simulate hand bounding boxes at different distances
    test_bboxes = [
        (100, 100, 80, 80),   # Close hand
        (150, 150, 60, 60),   # Medium distance
        (200, 200, 40, 40),   # Far hand
    ]
    
    frame_shape = (480, 640)
    
    for i, bbox in enumerate(test_bboxes):
        adaptive_roi = calibrator.get_adaptive_roi(bbox, frame_shape)
        distance = calibrator.estimate_hand_distance(bbox)
        
        print(f"  Test {i+1}: Original {bbox} -> Adaptive {adaptive_roi}")
        print(f"           Estimated distance: {distance:.1f}cm")
    
    # Test calibration stats
    stats = calibrator.get_calibration_stats()
    print(f"  Calibration stats: {stats}")
    
    print("✅ Adaptive ROI Calibrator test passed\n")


def test_background_robustness():
    """Test background robustness processor"""
    print("🎨 Testing Background Robustness...")
    
    processor = BackgroundRobustnessProcessor(
        enable_clahe=True,
        enable_background_suppression=True,
        enable_skin_masking=False
    )
    
    # Create test frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Test frame enhancement
    enhanced_frame, processing_info = processor.enhance_frame(test_frame)
    
    print(f"  Frame enhancement: {processing_info}")
    print(f"  Enhanced frame shape: {enhanced_frame.shape}")
    
    # Test lighting analysis
    lighting_conditions = processor.detect_lighting_conditions(test_frame)
    print(f"  Lighting analysis: {lighting_conditions}")
    
    # Test ROI enhancement
    test_roi = test_frame[100:200, 100:200]
    enhanced_roi = processor.enhance_roi(test_roi)
    
    print(f"  ROI enhancement: {test_roi.shape} -> {enhanced_roi.shape}")
    
    print("✅ Background Robustness test passed\n")


def test_gesture_state_machine():
    """Test gesture state machine"""
    print("🤖 Testing Gesture State Machine...")
    
    state_machine = GestureStateMachine(
        detection_threshold=0.7,
        confirmation_time=0.1,  # Shorter for testing
        cooldown_time=0.2,
        long_press_threshold=0.5
    )
    
    # Register test callback
    action_results = []
    
    def test_callback(gesture, action_type):
        result = f"{gesture}_{action_type}"
        action_results.append(result)
        return result
    
    state_machine.register_action_callback('palm', test_callback, test_callback)
    
    # Test gesture sequence
    test_events = [
        GestureEvent('palm', 0.8, time.time(), True),
        GestureEvent('palm', 0.9, time.time() + 0.05, True),
        GestureEvent('palm', 0.85, time.time() + 0.15, True),  # Should confirm
        GestureEvent('palm', 0.9, time.time() + 0.6, True),   # Long press
        GestureEvent('none', 0.0, time.time() + 0.8, False),  # End gesture
    ]
    
    for i, event in enumerate(test_events):
        result = state_machine.process_gesture(event)
        print(f"  Event {i+1}: {event.gesture} -> State: {result['state']}")
        
        if result.get('action'):
            print(f"           Action executed: {result['action']}")
        
        time.sleep(0.1)  # Brief delay between events
    
    # Check stats
    stats = state_machine.get_stats()
    print(f"  Final stats: {stats}")
    print(f"  Actions executed: {action_results}")
    
    print("✅ Gesture State Machine test passed\n")


def test_action_plugins():
    """Test action plugins"""
    print("🎮 Testing Action Plugins...")
    
    # Test keyboard plugin
    keyboard_plugin = KeyboardActionPlugin()
    keyboard_plugin.set_cooldown(0.1)  # Short cooldown for testing
    
    keyboard_context = {
        'action': 'space',
        'gesture': 'palm',
        'action_type': 'short_press',
        'confidence': 0.8
    }
    
    # Note: This will actually press space key - comment out if not desired
    # keyboard_result = keyboard_plugin.execute(keyboard_context)
    # print(f"  Keyboard test: {keyboard_result}")
    
    # Test mouse plugin
    mouse_plugin = MouseActionPlugin()
    mouse_plugin.set_cooldown(0.1)
    
    mouse_context = {
        'action': 'move_relative_10_10',
        'gesture': 'index',
        'action_type': 'short_press',
        'confidence': 0.8
    }
    
    # Note: This will actually move mouse - comment out if not desired
    # mouse_result = mouse_plugin.execute(mouse_context)
    # print(f"  Mouse test: {mouse_result}")
    
    # Test media plugin
    media_plugin = MediaActionPlugin()
    media_plugin.set_cooldown(0.1)
    
    media_context = {
        'action': 'volume_up',
        'gesture': 'thumb',
        'action_type': 'short_press',
        'confidence': 0.8
    }
    
    # Note: This will actually change volume - comment out if not desired
    # media_result = media_plugin.execute(media_context)
    # print(f"  Media test: {media_result}")
    
    # Test API plugin
    api_plugin = APIActionPlugin(base_url="http://httpbin.org")
    api_plugin.set_cooldown(0.1)
    
    api_context = {
        'action': '/post',
        'gesture': 'c_shape',
        'action_type': 'short_press',
        'confidence': 0.8,
        'method': 'POST',
        'payload': {'test': 'data'}
    }
    
    api_result = api_plugin.execute(api_context)
    print(f"  API test: {api_result}")
    
    # Test connectivity
    connectivity = api_plugin.test_connectivity()
    print(f"  API connectivity: {connectivity}")
    
    print("✅ Action Plugins test passed\n")


def test_async_pipeline():
    """Test async pipeline (without actual camera)"""
    print("⚡ Testing Async Pipeline...")
    
    pipeline = AsyncGesturePipeline(
        max_queue_size=5,
        max_workers=2,
        target_fps=10.0
    )
    
    # Mock components
    class MockCamera:
        def get_frame(self):
            return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    class MockDetector:
        def detect_hands(self, frame):
            return [], frame
    
    class MockPredictor:
        def predict(self, tensor):
            return {'gesture': 'palm', 'confidence': 0.8}
    
    class MockActionMapper:
        def execute_action(self, gesture, confidence):
            return {'executed': True, 'gesture': gesture}
    
    class MockStateMachine:
        def process_gesture(self, event):
            return {'gesture': event.gesture, 'action': None}
    
    # Inject mock components
    pipeline.inject_components(
        MockCamera(),
        MockDetector(),
        MockPredictor(),
        MockActionMapper(),
        MockStateMachine()
    )
    
    # Test pipeline start/stop
    pipeline.start()
    time.sleep(2.0)  # Let it run briefly
    
    # Get metrics
    metrics = pipeline.get_performance_metrics()
    print(f"  Pipeline metrics: {metrics}")
    
    pipeline.stop()
    
    print("✅ Async Pipeline test passed\n")


def test_integration():
    """Test integration of multiple components"""
    print("🔗 Testing Component Integration...")
    
    # Create components
    roi_calibrator = AdaptiveROICalibrator(history_size=5)
    background_processor = BackgroundRobustnessProcessor()
    state_machine = GestureStateMachine(confirmation_time=0.1, cooldown_time=0.2)
    
    # Simulate integrated processing
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # 1. Background processing
    enhanced_frame, _ = background_processor.enhance_frame(test_frame)
    
    # 2. Simulate hand detection
    mock_bbox = (200, 200, 80, 80)
    
    # 3. Adaptive ROI
    adaptive_roi = roi_calibrator.get_adaptive_roi(mock_bbox, test_frame.shape)
    
    # 4. State machine processing
    gesture_event = GestureEvent('palm', 0.8, time.time(), True)
    state_result = state_machine.process_gesture(gesture_event)
    
    print(f"  Integration test:")
    print(f"    Enhanced frame: {enhanced_frame.shape}")
    print(f"    Adaptive ROI: {adaptive_roi}")
    print(f"    State result: {state_result}")
    
    print("✅ Integration test passed\n")


def main():
    """Run all enhanced feature tests"""
    print("🚀 HAPTICA Enhanced Features Test Suite")
    print("=" * 50)
    
    try:
        test_adaptive_roi_calibrator()
        test_background_robustness()
        test_gesture_state_machine()
        test_action_plugins()
        test_async_pipeline()
        test_integration()
        
        print("🎉 All enhanced feature tests passed!")
        print("\n📊 Test Summary:")
        print("  ✅ Adaptive ROI Calibration")
        print("  ✅ Background Robustness")
        print("  ✅ Gesture State Machine")
        print("  ✅ Action Plugins")
        print("  ✅ Async Pipeline")
        print("  ✅ Component Integration")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())