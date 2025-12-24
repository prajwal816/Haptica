"""
Hand Detection Module - Extracts hand regions from frames
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List
from loguru import logger


class HandDetector:
    """MediaPipe-based hand detection with ROI extraction"""
    
    def __init__(self, confidence: float = 0.7, max_hands: int = 1):
        self.confidence = confidence
        self.max_hands = max_hands
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=confidence,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        logger.info(f"Hand detector initialized: confidence={confidence}")
    
    def detect_hands(self, frame: np.ndarray) -> Tuple[List[dict], np.ndarray]:
        """
        Detect hands and extract ROI
        
        Returns:
            List of hand info dicts and annotated frame
        """
        if frame is None:
            return [], frame
            
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hands_info = []
        annotated_frame = frame.copy()
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    annotated_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Extract bounding box
                bbox = self._get_bounding_box(hand_landmarks, frame.shape)
                if bbox:
                    x, y, w, h = bbox
                    
                    # Extract ROI with padding
                    roi = self._extract_roi(frame, bbox)
                    
                    hand_info = {
                        'bbox': bbox,
                        'roi': roi,
                        'landmarks': hand_landmarks,
                        'hand_id': idx
                    }
                    hands_info.append(hand_info)
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        return hands_info, annotated_frame
    
    def _get_bounding_box(self, landmarks, frame_shape) -> Optional[Tuple[int, int, int, int]]:
        """Calculate bounding box from landmarks"""
        try:
            h, w = frame_shape[:2]
            
            # Get all landmark coordinates
            x_coords = [lm.x * w for lm in landmarks.landmark]
            y_coords = [lm.y * h for lm in landmarks.landmark]
            
            # Calculate bounding box with padding
            padding = 30
            x_min = max(0, int(min(x_coords)) - padding)
            y_min = max(0, int(min(y_coords)) - padding)
            x_max = min(w, int(max(x_coords)) + padding)
            y_max = min(h, int(max(y_coords)) + padding)
            
            return (x_min, y_min, x_max - x_min, y_max - y_min)
            
        except Exception as e:
            logger.error(f"Error calculating bounding box: {e}")
            return None
    
    def _extract_roi(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Extract region of interest from frame"""
        try:
            x, y, w, h = bbox
            roi = frame[y:y+h, x:x+w]
            
            # Ensure minimum size
            if roi.shape[0] < 50 or roi.shape[1] < 50:
                return None
                
            return roi
            
        except Exception as e:
            logger.error(f"Error extracting ROI: {e}")
            return None
    
    def cleanup(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, 'hands'):
            self.hands.close()