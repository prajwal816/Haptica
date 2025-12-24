"""
Gesture Smoothing Module - Temporal filtering and debouncing
"""
from collections import deque
from typing import Dict, Optional
import time
from loguru import logger


class GestureSmoother:
    """Temporal smoothing and debouncing for stable gesture recognition"""
    
    def __init__(self, window_size: int = 5, debounce_time: float = 0.5):
        self.window_size = window_size
        self.debounce_time = debounce_time
        
        # Rolling window for predictions
        self.prediction_window = deque(maxlen=window_size)
        
        # State tracking
        self.current_gesture = None
        self.last_gesture_time = 0
        self.gesture_start_time = 0
        self.stable_count = 0
        
        logger.info(f"Gesture smoother initialized: window={window_size}, debounce={debounce_time}s")
    
    def process_prediction(self, prediction: Dict) -> Dict:
        """
        Process raw prediction through smoothing pipeline
        
        Args:
            prediction: Raw prediction from model
            
        Returns:
            Smoothed prediction result
        """
        current_time = time.time()
        
        # Add to rolling window
        self.prediction_window.append({
            'gesture': prediction['gesture'],
            'confidence': prediction['confidence'],
            'timestamp': current_time,
            'is_confident': prediction['is_confident']
        })
        
        # Apply smoothing
        smoothed_gesture = self._apply_temporal_smoothing()
        
        # Apply debouncing
        final_gesture = self._apply_debouncing(smoothed_gesture, current_time)
        
        # Create result
        result = {
            'gesture': final_gesture,
            'confidence': prediction['confidence'],
            'is_stable': self._is_gesture_stable(final_gesture),
            'raw_gesture': prediction['gesture'],
            'smoothed_gesture': smoothed_gesture,
            'window_size': len(self.prediction_window),
            'debounce_remaining': max(0, self.debounce_time - (current_time - self.last_gesture_time))
        }
        
        return result
    
    def _apply_temporal_smoothing(self) -> str:
        """Apply majority voting across time window"""
        if not self.prediction_window:
            return 'none'
        
        # Count confident predictions only
        confident_predictions = [
            p for p in self.prediction_window 
            if p['is_confident'] and p['gesture'] != 'uncertain'
        ]
        
        if not confident_predictions:
            return 'uncertain'
        
        # Majority voting
        gesture_counts = {}
        for pred in confident_predictions:
            gesture = pred['gesture']
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        # Return most frequent gesture
        if gesture_counts:
            return max(gesture_counts, key=gesture_counts.get)
        
        return 'uncertain'
    
    def _apply_debouncing(self, gesture: str, current_time: float) -> str:
        """Apply debouncing to prevent rapid gesture changes"""
        
        # If same gesture, continue
        if gesture == self.current_gesture:
            return gesture
        
        # Check debounce time
        time_since_last = current_time - self.last_gesture_time
        
        if time_since_last < self.debounce_time:
            # Still in debounce period, return current gesture
            return self.current_gesture if self.current_gesture else 'none'
        
        # New gesture detected, update state
        if gesture != 'uncertain' and gesture != 'none':
            self.current_gesture = gesture
            self.last_gesture_time = current_time
            self.gesture_start_time = current_time
            self.stable_count = 1
            
            logger.debug(f"New gesture detected: {gesture}")
        
        return gesture
    
    def _is_gesture_stable(self, gesture: str) -> bool:
        """Check if current gesture is stable"""
        if not gesture or gesture in ['none', 'uncertain']:
            return False
        
        # Count consecutive occurrences
        consecutive_count = 0
        for pred in reversed(self.prediction_window):
            if pred['gesture'] == gesture and pred['is_confident']:
                consecutive_count += 1
            else:
                break
        
        # Consider stable if seen consistently
        stability_threshold = min(3, self.window_size // 2)
        return consecutive_count >= stability_threshold
    
    def reset(self):
        """Reset smoother state"""
        self.prediction_window.clear()
        self.current_gesture = None
        self.last_gesture_time = 0
        self.gesture_start_time = 0
        self.stable_count = 0
        logger.debug("Gesture smoother reset")
    
    def get_stats(self) -> Dict:
        """Get smoothing statistics"""
        current_time = time.time()
        
        return {
            'window_size': len(self.prediction_window),
            'current_gesture': self.current_gesture,
            'gesture_duration': current_time - self.gesture_start_time if self.gesture_start_time else 0,
            'time_since_last': current_time - self.last_gesture_time,
            'debounce_active': (current_time - self.last_gesture_time) < self.debounce_time
        }