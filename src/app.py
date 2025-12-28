"""
HAPTICA Enhanced Application
Company-grade gesture recognition with all improvements integrated
"""
import cv2
import time
import argparse
import threading
from pathlib import Path
from loguru import logger
import sys
import json

# Import enhanced components
from camera.video_stream import VideoStream
from detection.hand_detector import HandDetector
from preprocessing.transforms import ImageTransforms
from inference.predictor import GesturePredictor
from ui.overlay import HapticaOverlay

# Import new enhanced modules
from vision.roi_calibrator import AdaptiveROICalibrator
from vision.background_robustness import BackgroundRobustnessProcessor
from core.state_machine import GestureStateMachine, GestureEvent
from core.async_pipeline import AsyncGesturePipeline

# Import action plugins
from actions.keyboard import KeyboardActionPlugin
from actions.mouse import MouseActionPlugin
from actions.media import MediaActionPlugin
from actions.api import APIActionPlugin


class EnhancedHapticaEngine:
    """
    Enhanced HAPTICA Engine with company-level improvements:
    - Adaptive ROI calibration
    - Background robustness
    - Intent-aware state machine
    - Asynchronous pipeline
    - Plugin-based actions
    """
    
    def __init__(self, config_dir: str = "config", model_path: str = "models/hand_recognition_model.h5"):
        self.config_dir = Path(config_dir)
        self.model_path = Path(model_path)
        
        # Core components
        self.video_stream = None
        self.hand_detector = None
        self.transforms = None
        self.predictor = None
        self.overlay = None
        
        # Enhanced components
        self.roi_calibrator = None
        self.background_processor = None
        self.state_machine = None
        self.async_pipeline = None
        
        # Action plugins
        self.action_plugins = {}
        
        # Runtime state
        self.running = False
        self.performance_metrics = {}
        
        # Configuration
        self.config = self._load_configuration()
        
        logger.info("Enhanced HAPTICA Engine initialized")
    
    def _load_configuration(self) -> dict:
        """Load enhanced configuration"""
        try:
            # Load base configuration
            with open(self.config_dir / "labels.json", 'r') as f:
                labels_config = json.load(f)
            
            with open(self.config_dir / "actions.json", 'r') as f:
                actions_config = json.load(f)
            
            # Enhanced configuration with defaults
            config = {
                'labels': labels_config,
                'actions': actions_config,
                'roi_calibration': {
                    'enable_adaptive_roi': True,
                    'history_size': 30,
                    'padding_factor': 0.3
                },
                'background_robustness': {
                    'enable_clahe': True,
                    'enable_background_suppression': True,
                    'enable_skin_masking': False
                },
                'state_machine': {
                    'detection_threshold': 0.7,
                    'confirmation_time': 0.3,
                    'cooldown_time': 1.0,
                    'long_press_threshold': 2.0
                },
                'async_pipeline': {
                    'enable_async': False,  # Disable async for now
                    'max_queue_size': 10,
                    'max_workers': 3,
                    'target_fps': 30.0
                },
                'performance': {
                    'enable_metrics': True,
                    'metrics_interval': 1.0
                }
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            return {}
    
    def initialize(self) -> bool:
        """Initialize all enhanced components"""
        try:
            # 1. Core components
            self.video_stream = VideoStream(source=0, resolution=(640, 480))
            if not self.video_stream.start():
                logger.error("Failed to initialize video stream")
                return False
            
            self.hand_detector = HandDetector(confidence=0.7, max_hands=1)
            self.transforms = ImageTransforms(target_size=(50, 50))
            
            labels_path = self.config_dir / "labels.json"
            self.predictor = GesturePredictor(str(self.model_path), str(labels_path))
            
            self.overlay = HapticaOverlay("HAPTICA Enhanced - Real-Time Gesture Recognition")
            
            # 2. Enhanced vision components
            if self.config.get('roi_calibration', {}).get('enable_adaptive_roi', True):
                self.roi_calibrator = AdaptiveROICalibrator(
                    history_size=self.config['roi_calibration'].get('history_size', 30)
                )
            
            self.background_processor = BackgroundRobustnessProcessor(
                enable_clahe=self.config['background_robustness'].get('enable_clahe', True),
                enable_background_suppression=self.config['background_robustness'].get('enable_background_suppression', True),
                enable_skin_masking=self.config['background_robustness'].get('enable_skin_masking', False)
            )
            
            # 3. State machine
            state_config = self.config.get('state_machine', {})
            self.state_machine = GestureStateMachine(
                detection_threshold=state_config.get('detection_threshold', 0.7),
                confirmation_time=state_config.get('confirmation_time', 0.3),
                cooldown_time=state_config.get('cooldown_time', 1.0),
                long_press_threshold=state_config.get('long_press_threshold', 2.0)
            )
            
            # 4. Action plugins
            self._initialize_action_plugins()
            
            # 5. Async pipeline (optional)
            if self.config.get('async_pipeline', {}).get('enable_async', False):
                pipeline_config = self.config['async_pipeline']
                self.async_pipeline = AsyncGesturePipeline(
                    max_queue_size=pipeline_config.get('max_queue_size', 10),
                    max_workers=pipeline_config.get('max_workers', 3),
                    target_fps=pipeline_config.get('target_fps', 30.0)
                )
                
                # Inject components into pipeline
                self.async_pipeline.inject_components(
                    self.video_stream,
                    self.hand_detector,
                    self.predictor,
                    self._create_unified_action_mapper(),
                    self.state_machine
                )
            
            logger.info("All enhanced components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced initialization failed: {e}")
            return False
    
    def _initialize_action_plugins(self):
        """Initialize action plugins"""
        try:
            # Keyboard plugin
            self.action_plugins['keyboard'] = KeyboardActionPlugin()
            
            # Mouse plugin
            self.action_plugins['mouse'] = MouseActionPlugin()
            
            # Media plugin
            self.action_plugins['media'] = MediaActionPlugin()
            
            # API plugin
            self.action_plugins['api'] = APIActionPlugin()
            
            # Register callbacks with state machine
            self._register_action_callbacks()
            
            logger.info(f"Action plugins initialized: {list(self.action_plugins.keys())}")
            
        except Exception as e:
            logger.error(f"Action plugin initialization failed: {e}")
    
    def _register_action_callbacks(self):
        """Register action callbacks with state machine"""
        def execute_action(gesture: str, action_type: str):
            """Unified action executor"""
            try:
                # Get action configuration for gesture
                gesture_actions = self.config['actions']['gesture_actions']
                if gesture not in gesture_actions:
                    return {'executed': False, 'reason': 'no_mapping'}
                
                action_config = gesture_actions[gesture]
                plugin_type = action_config.get('type', 'keyboard')
                action_command = action_config.get('action', '')
                
                # Get appropriate plugin
                plugin = self.action_plugins.get(plugin_type)
                if not plugin:
                    return {'executed': False, 'reason': 'plugin_not_found'}
                
                # Prepare context
                context = {
                    'action': action_command,
                    'gesture': gesture,
                    'action_type': action_type,
                    'confidence': 0.8  # Will be updated with actual confidence
                }
                
                # Execute action
                if action_type == 'long_press' and hasattr(plugin, 'execute_long_press'):
                    return plugin.execute_long_press(context)
                else:
                    return plugin.execute(context)
                    
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                return {'executed': False, 'error': str(e)}
        
        # Register for all gestures
        gesture_actions = self.config['actions']['gesture_actions']
        for gesture in gesture_actions.keys():
            self.state_machine.register_action_callback(
                gesture, 
                lambda g, at: execute_action(g, at),
                lambda g, at: execute_action(g, 'long_press')  # Long press callback
            )
    
    def _create_unified_action_mapper(self):
        """Create unified action mapper for async pipeline"""
        class UnifiedActionMapper:
            def __init__(self, plugins, config):
                self.plugins = plugins
                self.config = config
            
            def execute_action(self, gesture: str, confidence: float):
                # This would integrate with the action plugins
                return {'executed': True, 'gesture': gesture}
        
        return UnifiedActionMapper(self.action_plugins, self.config)
    
    def run(self):
        """Run enhanced HAPTICA with async pipeline or traditional loop"""
        if not self.initialize():
            logger.error("Failed to initialize Enhanced HAPTICA")
            return
        
        self.running = True
        
        if self.async_pipeline:
            self._run_async_pipeline()
        else:
            self._run_traditional_loop()
    
    def _run_async_pipeline(self):
        """Run with asynchronous pipeline"""
        logger.info("Starting Enhanced HAPTICA with async pipeline")
        
        try:
            # Start async pipeline
            self.async_pipeline.start()
            
            # UI loop for display
            while self.running:
                # Get latest processed frame
                pipeline_frame = self.async_pipeline.get_latest_frame()
                
                if pipeline_frame:
                    # Display frame with overlay
                    display_frame = self._create_enhanced_overlay(
                        pipeline_frame.processed_frame or pipeline_frame.raw_frame,
                        pipeline_frame.prediction or {},
                        pipeline_frame.hand_info or [],
                        pipeline_frame.action_result or {}
                    )
                    
                    cv2.imshow(self.overlay.window_name, display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('m'):
                    self._show_performance_metrics()
                elif key == ord('r'):
                    self._reload_configuration()
                elif key == ord('e'):
                    self.state_machine.emergency_disable()
                elif key == ord('s'):
                    self.state_machine.force_enable()
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Async pipeline error: {e}")
        finally:
            if self.async_pipeline:
                self.async_pipeline.stop()
            self._cleanup()
    
    def _run_traditional_loop(self):
        """Run with traditional processing loop"""
        logger.info("Starting Enhanced HAPTICA with traditional loop")
        
        try:
            while self.running:
                # Get frame
                frame = self.video_stream.get_frame()
                if frame is None:
                    continue
                
                # Enhanced processing
                processed_frame = self._process_enhanced_frame(frame)
                
                # Display
                cv2.imshow(self.overlay.window_name, processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('m'):
                    self._show_performance_metrics()
                elif key == ord('r'):
                    self._reload_configuration()
                elif key == ord('e'):
                    self.state_machine.emergency_disable()
                elif key == ord('s'):
                    self.state_machine.force_enable()
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Traditional loop error: {e}")
        finally:
            self._cleanup()
    
    def _process_enhanced_frame(self, frame):
        """Process frame with all enhancements"""
        try:
            # 1. Background robustness (with fallback)
            try:
                enhanced_frame, processing_info = self.background_processor.enhance_frame(frame)
            except Exception as e:
                logger.warning(f"Background processing failed, using original frame: {e}")
                enhanced_frame = frame
                processing_info = {}
            
            # 2. Hand detection
            hands_info, annotated_frame = self.hand_detector.detect_hands(enhanced_frame)
            
            # 3. Adaptive ROI if hand detected
            if hands_info and self.roi_calibrator:
                hand_info = hands_info[0]
                original_bbox = hand_info.get('bbox')
                
                if original_bbox is not None:
                    try:
                        # Get adaptive ROI
                        adaptive_roi_bbox = self.roi_calibrator.get_adaptive_roi(
                            original_bbox, frame.shape
                        )
                        
                        # Update hand info with adaptive ROI
                        x, y, w, h = adaptive_roi_bbox
                        
                        # Ensure valid coordinates
                        if (x >= 0 and y >= 0 and w > 0 and h > 0 and 
                            x + w <= enhanced_frame.shape[1] and y + h <= enhanced_frame.shape[0]):
                            adaptive_roi = enhanced_frame[y:y+h, x:x+w]
                            hand_info['adaptive_roi'] = adaptive_roi
                            hand_info['adaptive_bbox'] = adaptive_roi_bbox
                    except Exception as e:
                        logger.warning(f"Adaptive ROI processing failed: {e}")
                        # Fallback to original ROI
                        pass
            
            # 4. Gesture prediction
            prediction = {'gesture': 'none', 'confidence': 0.0, 'is_stable': False}
            
            if hands_info:
                hand_info = hands_info[0]
                roi = hand_info.get('adaptive_roi')
                if roi is None:
                    roi = hand_info.get('roi')
                
                if roi is not None and roi.size > 0:
                    try:
                        # Enhanced ROI processing
                        enhanced_roi = self.background_processor.enhance_roi(roi)
                        processed_tensor = self.transforms.preprocess_roi(enhanced_roi)
                        
                        if processed_tensor is not None:
                            raw_prediction = self.predictor.predict(processed_tensor)
                            
                            # Process through state machine
                            gesture_event = GestureEvent(
                                gesture=raw_prediction['gesture'],
                                confidence=raw_prediction['confidence'],
                                timestamp=time.time(),
                                is_stable=raw_prediction.get('is_confident', False)
                            )
                            
                            state_result = self.state_machine.process_gesture(gesture_event)
                            prediction.update(state_result)
                    except Exception as e:
                        logger.warning(f"Gesture prediction failed: {e}")
                        # Keep default prediction
            
            # 5. Create enhanced overlay
            display_frame = self._create_enhanced_overlay(
                annotated_frame, prediction, hands_info, {}
            )
            
            return display_frame
            
        except Exception as e:
            logger.error(f"Enhanced frame processing error: {e}")
            return frame
    
    def _create_enhanced_overlay(self, frame, prediction, hands_info, action_result):
        """Create enhanced overlay with additional information"""
        try:
            # Base overlay
            display_frame = self.overlay.draw_main_overlay(
                frame, prediction, hands_info, 30.0  # FPS placeholder
            )
            
            # Enhanced information
            if self.roi_calibrator:
                stats = self.roi_calibrator.get_calibration_stats()
                if stats:
                    # Draw calibration info
                    cv2.putText(display_frame, 
                              f"ROI Stability: {stats.get('roi_stability', 0):.2f}",
                              (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # State machine info
            if self.state_machine:
                state_stats = self.state_machine.get_stats()
                cv2.putText(display_frame,
                          f"State: {state_stats.get('current_state', 'unknown')}",
                          (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            return display_frame
            
        except Exception as e:
            logger.error(f"Enhanced overlay creation failed: {e}")
            return frame
    
    def _show_performance_metrics(self):
        """Display performance metrics"""
        try:
            if self.async_pipeline:
                metrics = self.async_pipeline.get_performance_metrics()
                logger.info(f"Performance Metrics: {metrics}")
            
            if self.state_machine:
                state_stats = self.state_machine.get_stats()
                logger.info(f"State Machine Stats: {state_stats}")
            
            if self.roi_calibrator:
                roi_stats = self.roi_calibrator.get_calibration_stats()
                logger.info(f"ROI Calibration Stats: {roi_stats}")
                
        except Exception as e:
            logger.error(f"Metrics display failed: {e}")
    
    def _reload_configuration(self):
        """Reload configuration files"""
        try:
            self.config = self._load_configuration()
            logger.info("Configuration reloaded")
        except Exception as e:
            logger.error(f"Configuration reload failed: {e}")
    
    def _cleanup(self):
        """Enhanced cleanup"""
        logger.info("Shutting down Enhanced HAPTICA...")
        
        if self.video_stream:
            self.video_stream.stop()
        
        if self.hand_detector:
            self.hand_detector.cleanup()
        
        # Cleanup action plugins
        for plugin in self.action_plugins.values():
            if hasattr(plugin, 'close'):
                plugin.close()
        
        cv2.destroyAllWindows()
        logger.info("Enhanced HAPTICA shutdown complete")


def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(description="HAPTICA Enhanced - Company-Grade Gesture Recognition")
    parser.add_argument("--model", default="models/hand_recognition_model.h5", 
                       help="Path to gesture recognition model")
    parser.add_argument("--config", default="config", 
                       help="Configuration directory")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--async", action="store_true",
                       help="Enable asynchronous pipeline")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    logger.add("logs/haptica_enhanced_{time}.log", rotation="1 day", level="DEBUG")
    
    # Check model file
    if not Path(args.model).exists():
        logger.error(f"Model file not found: {args.model}")
        return
    
    # Create and run Enhanced HAPTICA
    haptica = EnhancedHapticaEngine(config_dir=args.config, model_path=args.model)
    haptica.run()


if __name__ == "__main__":
    main()