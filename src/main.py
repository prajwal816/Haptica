"""
HAPTICA Main Application
Real-Time Hand Gesture Recognition & Interaction Engine
"""
import cv2
import time
import argparse
from pathlib import Path
from loguru import logger
import sys

# Import HAPTICA modules
from camera.video_stream import VideoStream
from detection.hand_detector import HandDetector
from preprocessing.transforms import ImageTransforms
from inference.predictor import GesturePredictor
from logic.gesture_smoother import GestureSmoother
from logic.action_mapper import ActionMapper
from ui.overlay import HapticaOverlay


class HapticaEngine:
    """Main HAPTICA application engine"""
    
    def __init__(self, config_dir: str = "config", model_path: str = "models/hand_recognition_model.h5"):
        self.config_dir = Path(config_dir)
        self.model_path = Path(model_path)
        
        # Initialize components
        self.video_stream = None
        self.hand_detector = None
        self.transforms = None
        self.predictor = None
        self.smoother = None
        self.action_mapper = None
        self.overlay = None
        
        # Runtime state
        self.running = False
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        logger.info("HAPTICA Engine initialized")
    
    def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            # Video stream
            self.video_stream = VideoStream(source=0, resolution=(640, 480))
            if not self.video_stream.start():
                logger.error("Failed to initialize video stream")
                return False
            
            # Hand detector
            self.hand_detector = HandDetector(confidence=0.7, max_hands=1)
            
            # Image transforms
            self.transforms = ImageTransforms(target_size=(224, 224))
            
            # Gesture predictor
            labels_path = self.config_dir / "labels.json"
            self.predictor = GesturePredictor(str(self.model_path), str(labels_path))
            
            # Gesture smoother
            self.smoother = GestureSmoother(window_size=5, debounce_time=0.5)
            
            # Action mapper
            actions_path = self.config_dir / "actions.json"
            self.action_mapper = ActionMapper(str(actions_path))
            
            # UI overlay
            self.overlay = HapticaOverlay("HAPTICA - Real-Time Gesture Recognition")
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            logger.error("Failed to initialize HAPTICA")
            return
        
        self.running = True
        logger.info("HAPTICA started - Press 'q' to quit, 'd' for debug, 'r' to reload config")
        
        try:
            while self.running:
                # Get frame
                frame = self.video_stream.get_frame()
                if frame is None:
                    continue
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Display result
                cv2.imshow(self.overlay.window_name, processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('d'):
                    self.overlay.toggle_debug_mode()
                elif key == ord('f'):
                    self.overlay.toggle_fps_display()
                elif key == ord('c'):
                    self.overlay.toggle_confidence_display()
                elif key == ord('r'):
                    self._reload_config()
                
                # Update FPS
                self._update_fps()
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            self._cleanup()
    
    def _process_frame(self, frame):
        """Process single frame through complete pipeline"""
        try:
            # Detect hands
            hands_info, annotated_frame = self.hand_detector.detect_hands(frame)
            
            # Initialize prediction
            prediction = {
                'gesture': 'none',
                'confidence': 0.0,
                'is_stable': False,
                'is_confident': False
            }
            
            action_result = {'executed': False}
            
            # Process if hand detected
            if hands_info:
                hand_info = hands_info[0]  # Use first hand
                roi = hand_info.get('roi')
                
                if roi is not None:
                    # Preprocess ROI
                    processed_tensor = self.transforms.preprocess_roi(roi)
                    
                    if processed_tensor is not None:
                        # Make prediction
                        raw_prediction = self.predictor.predict(processed_tensor)
                        
                        # Apply smoothing
                        prediction = self.smoother.process_prediction(raw_prediction)
                        
                        # Execute action if gesture is stable
                        if prediction['is_stable'] and prediction['gesture'] != 'none':
                            action_result = self.action_mapper.execute_action(
                                prediction['gesture'], 
                                prediction['confidence']
                            )
            
            # Draw overlay
            display_frame = self.overlay.draw_main_overlay(
                annotated_frame, prediction, hands_info, self.current_fps
            )
            
            # Draw action feedback
            if action_result.get('executed'):
                display_frame = self.overlay.draw_action_feedback(display_frame, action_result)
            
            return display_frame
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return frame
    
    def _update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.last_fps_time)
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def _reload_config(self):
        """Reload configuration files"""
        try:
            self.action_mapper.reload_config()
            logger.info("Configuration reloaded")
        except Exception as e:
            logger.error(f"Failed to reload config: {e}")
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("Shutting down HAPTICA...")
        
        if self.video_stream:
            self.video_stream.stop()
        
        if self.hand_detector:
            self.hand_detector.cleanup()
        
        cv2.destroyAllWindows()
        logger.info("HAPTICA shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="HAPTICA - Real-Time Hand Gesture Recognition")
    parser.add_argument("--model", default="models/hand_recognition_model.h5", 
                       help="Path to gesture recognition model")
    parser.add_argument("--config", default="config", 
                       help="Configuration directory")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    logger.add("logs/haptica_{time}.log", rotation="1 day", level="DEBUG")
    
    # Check model file
    if not Path(args.model).exists():
        logger.error(f"Model file not found: {args.model}")
        logger.info("Please ensure hand_recognition_model.h5 is in the models/ directory")
        return
    
    # Create and run HAPTICA
    haptica = HapticaEngine(config_dir=args.config, model_path=args.model)
    haptica.run()


if __name__ == "__main__":
    main()