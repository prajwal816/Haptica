"""
UI Overlay Module - Real-time visual feedback
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import time


class HapticaOverlay:
    """Real-time UI overlay for gesture recognition feedback"""
    
    def __init__(self, window_name: str = "HAPTICA - Gesture Recognition"):
        self.window_name = window_name
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.thickness = 2
        
        # Colors (BGR format)
        self.colors = {
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'orange': (0, 165, 255),
            'purple': (255, 0, 255)
        }
        
        # UI state
        self.show_fps = True
        self.show_confidence = True
        self.show_debug = False
        self.fps_history = []
        
    def draw_main_overlay(self, frame: np.ndarray, prediction: Dict, 
                         hands_info: List[Dict], fps: float = 0) -> np.ndarray:
        """Draw complete overlay on frame"""
        overlay_frame = frame.copy()
        
        # Draw hand detection boxes
        for hand_info in hands_info:
            overlay_frame = self._draw_hand_box(overlay_frame, hand_info)
        
        # Draw gesture information
        overlay_frame = self._draw_gesture_info(overlay_frame, prediction)
        
        # Draw FPS
        if self.show_fps:
            overlay_frame = self._draw_fps(overlay_frame, fps)
        
        # Draw status bar
        overlay_frame = self._draw_status_bar(overlay_frame, prediction)
        
        return overlay_frame
    
    def _draw_hand_box(self, frame: np.ndarray, hand_info: Dict) -> np.ndarray:
        """Draw bounding box around detected hand"""
        if 'bbox' not in hand_info:
            return frame
        
        x, y, w, h = hand_info['bbox']
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), self.colors['green'], 2)
        
        # Draw hand ID
        hand_id = hand_info.get('hand_id', 0)
        cv2.putText(frame, f"Hand {hand_id}", (x, y - 10), 
                   self.font, 0.5, self.colors['green'], 1)
        
        return frame
    
    def _draw_gesture_info(self, frame: np.ndarray, prediction: Dict) -> np.ndarray:
        """Draw gesture recognition information"""
        h, w = frame.shape[:2]
        
        # Main gesture display
        gesture = prediction.get('gesture', 'none')
        confidence = prediction.get('confidence', 0.0)
        is_stable = prediction.get('is_stable', False)
        
        # Choose color based on confidence and stability
        if gesture in ['none', 'uncertain']:
            color = self.colors['white']
        elif is_stable:
            color = self.colors['green']
        elif confidence > 0.7:
            color = self.colors['yellow']
        else:
            color = self.colors['red']
        
        # Draw gesture name
        gesture_text = gesture.upper().replace('_', ' ')
        text_size = cv2.getTextSize(gesture_text, self.font, 1.2, 3)[0]
        text_x = (w - text_size[0]) // 2
        text_y = 60
        
        # Background rectangle
        cv2.rectangle(frame, (text_x - 10, text_y - 35), 
                     (text_x + text_size[0] + 10, text_y + 10), 
                     self.colors['black'], -1)
        
        # Gesture text
        cv2.putText(frame, gesture_text, (text_x, text_y), 
                   self.font, 1.2, color, 3)
        
        # Confidence bar
        if self.show_confidence and confidence > 0:
            self._draw_confidence_bar(frame, confidence, text_x, text_y + 30)
        
        return frame
    
    def _draw_confidence_bar(self, frame: np.ndarray, confidence: float, 
                           x: int, y: int) -> np.ndarray:
        """Draw confidence level bar"""
        bar_width = 200
        bar_height = 10
        
        # Background bar
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), 
                     self.colors['white'], 1)
        
        # Confidence fill
        fill_width = int(bar_width * confidence)
        fill_color = self.colors['green'] if confidence > 0.7 else self.colors['yellow']
        
        cv2.rectangle(frame, (x + 1, y + 1), 
                     (x + fill_width, y + bar_height - 1), 
                     fill_color, -1)
        
        # Confidence text
        conf_text = f"{confidence:.2f}"
        cv2.putText(frame, conf_text, (x + bar_width + 10, y + bar_height), 
                   self.font, 0.5, self.colors['white'], 1)
        
        return frame
    
    def _draw_fps(self, frame: np.ndarray, fps: float) -> np.ndarray:
        """Draw FPS counter"""
        # Update FPS history
        self.fps_history.append(fps)
        if len(self.fps_history) > 30:  # Keep last 30 frames
            self.fps_history.pop(0)
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        
        # Choose color based on FPS
        if avg_fps > 25:
            color = self.colors['green']
        elif avg_fps > 15:
            color = self.colors['yellow']
        else:
            color = self.colors['red']
        
        fps_text = f"FPS: {avg_fps:.1f}"
        cv2.putText(frame, fps_text, (10, 30), 
                   self.font, self.font_scale, color, self.thickness)
        
        return frame
    
    def _draw_status_bar(self, frame: np.ndarray, prediction: Dict) -> np.ndarray:
        """Draw status information bar"""
        h, w = frame.shape[:2]
        
        # Status background
        status_height = 80
        cv2.rectangle(frame, (0, h - status_height), (w, h), 
                     (0, 0, 0, 128), -1)  # Semi-transparent
        
        # Status information
        status_items = []
        
        # Gesture status
        gesture = prediction.get('gesture', 'none')
        is_stable = prediction.get('is_stable', False)
        status_items.append(f"Gesture: {gesture}")
        
        if is_stable:
            status_items.append("STABLE")
        
        # Debounce status
        debounce_remaining = prediction.get('debounce_remaining', 0)
        if debounce_remaining > 0:
            status_items.append(f"Cooldown: {debounce_remaining:.1f}s")
        
        # Draw status items
        y_pos = h - 50
        for i, item in enumerate(status_items):
            x_pos = 20 + i * 200
            cv2.putText(frame, item, (x_pos, y_pos), 
                       self.font, 0.6, self.colors['white'], 1)
        
        return frame
    
    def draw_action_feedback(self, frame: np.ndarray, action_result: Dict) -> np.ndarray:
        """Draw action execution feedback"""
        if not action_result.get('executed', False):
            return frame
        
        h, w = frame.shape[:2]
        
        # Action feedback
        gesture = action_result.get('gesture', '')
        action_type = action_result.get('action_type', '')
        
        feedback_text = f"Action: {gesture} -> {action_type}"
        
        # Background
        text_size = cv2.getTextSize(feedback_text, self.font, 0.8, 2)[0]
        cv2.rectangle(frame, (w - text_size[0] - 20, 10), 
                     (w - 10, 50), self.colors['green'], -1)
        
        # Text
        cv2.putText(frame, feedback_text, (w - text_size[0] - 15, 35), 
                   self.font, 0.8, self.colors['white'], 2)
        
        return frame
    
    def toggle_debug_mode(self):
        """Toggle debug information display"""
        self.show_debug = not self.show_debug
    
    def toggle_fps_display(self):
        """Toggle FPS display"""
        self.show_fps = not self.show_fps
    
    def toggle_confidence_display(self):
        """Toggle confidence display"""
        self.show_confidence = not self.show_confidence