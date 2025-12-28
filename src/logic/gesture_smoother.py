"""
Gesture Smoothing Module - Temporal filtering and debouncing
"""
from collections import deque
from typing import Dict, Optional
import time
from loguru import logger


class GestureSmoother:
    """Temporal smoothing and debouncing for stable gesture recognition"""
    
    def __init__(self, window_size: int = 10, debounce_time: float = 0.5, consecutive_frames: int = 7):
        self.window_size = window_size
        self.debounce_time = debounce_time
        self.consecutive_frames = consecutive_frames  # FIX 5: Require N consecutive frames
        
        # Rolling window for predictions
        self.prediction_window = deque(maxlen=window_size)
        
        # State tracking
        self.current_gesture = None
        self.last_gesture_time = 0
        self.gesture_start_time = 0
        self.stable_count = 0
        
        logger.info(f"Gesture smoother initialized: window={window_size}, debounce={debounce_time}s, consecutive={consecutive_frames}")
    
    def process_prediction(self, prediction: Dict) -> Dict:
        """
        Process raw prediction through smoothing pipeline with stronger temporal confirmation
        
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
        
        # Apply temporal smoothing with consecutive frame requirement
        smoothed_gesture = self._apply_temporal_smoothing_strict()
        
        # Apply debouncing
        final_gesture = self._apply_debouncing(smoothed_gesture, current_time)
        
        # Create result
        result = {
            'gesture': final_gesture,
            'confidence': prediction['confidence'],
            'is_stable': self._is_gesture_stable_strict(final_gesture),
            'raw_gesture': prediction['gesture'],
            'smoothed_gesture': smoothed_gesture,
            'window_size': len(self.prediction_window),
            'consecutive_count': self._count_consecutive_frames(prediction['gesture']),
            'debounce_remaining': max(0, self.debounce_time - (current_time - self.last_gesture_time))
        }
        
        return result
    
    def _apply_temporal_smoothing_strict(self) -> str:
        """Apply strict temporal smoothing requiring consecutive frames"""
        if len(self.prediction_window) < self.consecutive_frames:
            return 'uncertain'
        
        # Get the last N frames
        recent_frames = list(self.prediction_window)[-self.consecutive_frames:]
        
        # Check if all recent frames have the same confident gesture
        first_gesture = None
        for frame in recent_frames:
            if not frame['is_confident'] or frame['gesture'] in ['uncertain', 'none']:
                return 'uncertain'
            
            if first_gesture is None:
                first_gesture = frame['gesture']
            elif frame['gesture'] != first_gesture:
                return 'uncertain'
        
        # All consecutive frames agree on the same gesture
        return first_gesture if first_gesture else 'uncertain'
    
    def _count_consecutive_frames(self, gesture: str) -> int:
        """Count consecutive frames with the same gesture"""
        if not self.prediction_window:
            return 0
        
        count = 0
        for frame in reversed(self.prediction_window):
            if frame['gesture'] == gesture and frame['is_confident']:
                count += 1
            else:
                break
        
        return count
    
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
        """Check if current gesture is stable with strict requirements"""
        if not gesture or gesture in ['none', 'uncertain']:
            return False
        
        # Count consecutive occurrences
        consecutive_count = self._count_consecutive_frames(gesture)
        
        # Require at least consecutive_frames for stability
        return consecutive_count >= self.consecutive_frames
    
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
    
    def _is_gesture_stable_strict(self, gesture: str) -> bool:
        """Check if current gesture is stable with strict requirements"""
        if not gesture or gesture in ['none', 'uncertain']:
            return False
        
        # Count consecutive occurrences
        consecutive_count = self._count_consecutive_frames(gesture)
        
        # Require at least consecutive_frames for stability
        return consecutive_count >= self.consecutive_frames