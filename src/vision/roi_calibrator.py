"""
Adaptive ROI & Auto-Calibration Module
Dynamically adjusts hand detection regions based on distance and user characteristics
"""
import cv2
import numpy as np
from typing import Tuple, Optional, Dict
from collections import deque
from loguru import logger


class AdaptiveROICalibrator:
    """Auto-calibrates hand ROI size based on distance and hand characteristics"""
    
    def __init__(self, history_size: int = 30):
        self.history_size = history_size
        
        # ROI history for adaptive sizing
        self.roi_history = deque(maxlen=history_size)
        self.distance_history = deque(maxlen=history_size)
        
        # Calibration parameters
        self.base_roi_size = (100, 100)
        self.min_roi_size = (60, 60)
        self.max_roi_size = (200, 200)
        self.padding_factor = 0.3  # 30% padding around detected hand
        
        # Distance estimation parameters
        self.reference_hand_width = 80  # pixels at reference distance
        self.reference_distance = 60   # cm
        
        # Adaptive parameters
        self.roi_smoothing_factor = 0.7
        self.distance_smoothing_factor = 0.8
        
        logger.info("Adaptive ROI Calibrator initialized")
    
    def estimate_hand_distance(self, hand_bbox: Tuple[int, int, int, int]) -> float:
        """
        Estimate hand distance from camera based on bounding box size
        
        Args:
            hand_bbox: (x, y, width, height) of hand bounding box
            
        Returns:
            Estimated distance in cm
        """
        _, _, width, height = hand_bbox
        hand_size = max(width, height)
        
        if hand_size <= 0:
            return self.reference_distance
        
        # Inverse relationship: larger hand = closer distance
        estimated_distance = (self.reference_hand_width * self.reference_distance) / hand_size
        
        # Clamp to reasonable range
        estimated_distance = np.clip(estimated_distance, 20, 150)
        
        return estimated_distance
    
    def calculate_adaptive_padding(self, hand_bbox: Tuple[int, int, int, int], 
                                 estimated_distance: float) -> Tuple[int, int]:
        """
        Calculate adaptive padding based on hand size and distance
        
        Args:
            hand_bbox: Hand bounding box
            estimated_distance: Estimated distance in cm
            
        Returns:
            (horizontal_padding, vertical_padding)
        """
        _, _, width, height = hand_bbox
        
        # Base padding proportional to hand size
        base_h_padding = int(width * self.padding_factor)
        base_v_padding = int(height * self.padding_factor)
        
        # Distance-based adjustment (closer = more padding for gesture variations)
        distance_factor = max(0.5, min(2.0, 80 / estimated_distance))
        
        h_padding = int(base_h_padding * distance_factor)
        v_padding = int(base_v_padding * distance_factor)
        
        return h_padding, v_padding
    
    def get_adaptive_roi(self, hand_bbox: Tuple[int, int, int, int], 
                        frame_shape: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Calculate adaptive ROI with dynamic padding and smoothing
        
        Args:
            hand_bbox: Original hand bounding box
            frame_shape: (height, width) of frame
            
        Returns:
            Adaptive ROI (x, y, width, height)
        """
        x, y, width, height = hand_bbox
        frame_height, frame_width = frame_shape[:2]
        
        # Estimate distance
        estimated_distance = self.estimate_hand_distance(hand_bbox)
        self.distance_history.append(estimated_distance)
        
        # Smooth distance estimate
        if len(self.distance_history) > 1:
            smoothed_distance = (
                self.distance_smoothing_factor * estimated_distance +
                (1 - self.distance_smoothing_factor) * self.distance_history[-2]
            )
        else:
            smoothed_distance = estimated_distance
        
        # Calculate adaptive padding
        h_padding, v_padding = self.calculate_adaptive_padding(hand_bbox, smoothed_distance)
        
        # Apply padding
        adaptive_x = max(0, x - h_padding)
        adaptive_y = max(0, y - v_padding)
        adaptive_width = min(frame_width - adaptive_x, width + 2 * h_padding)
        adaptive_height = min(frame_height - adaptive_y, height + 2 * v_padding)
        
        # Ensure minimum size
        if adaptive_width < self.min_roi_size[0]:
            center_x = adaptive_x + adaptive_width // 2
            adaptive_x = max(0, center_x - self.min_roi_size[0] // 2)
            adaptive_width = min(frame_width - adaptive_x, self.min_roi_size[0])
        
        if adaptive_height < self.min_roi_size[1]:
            center_y = adaptive_y + adaptive_height // 2
            adaptive_y = max(0, center_y - self.min_roi_size[1] // 2)
            adaptive_height = min(frame_height - adaptive_y, self.min_roi_size[1])
        
        # Ensure maximum size
        adaptive_width = min(adaptive_width, self.max_roi_size[0])
        adaptive_height = min(adaptive_height, self.max_roi_size[1])
        
        adaptive_roi = (adaptive_x, adaptive_y, adaptive_width, adaptive_height)
        
        # Smooth ROI changes
        if self.roi_history:
            last_roi = self.roi_history[-1]
            smoothed_roi = tuple(
                int(self.roi_smoothing_factor * new + (1 - self.roi_smoothing_factor) * old)
                for new, old in zip(adaptive_roi, last_roi)
            )
        else:
            smoothed_roi = adaptive_roi
        
        self.roi_history.append(smoothed_roi)
        
        return smoothed_roi
    
    def get_calibration_stats(self) -> Dict:
        """Get calibration statistics for monitoring"""
        if not self.distance_history or not self.roi_history:
            return {}
        
        avg_distance = np.mean(list(self.distance_history))
        distance_std = np.std(list(self.distance_history))
        
        roi_sizes = [(w * h) for _, _, w, h in self.roi_history]
        avg_roi_size = np.mean(roi_sizes)
        roi_stability = 1.0 - (np.std(roi_sizes) / avg_roi_size) if avg_roi_size > 0 else 0
        
        return {
            'avg_distance_cm': avg_distance,
            'distance_stability': 1.0 - min(1.0, distance_std / 20),  # Normalize by 20cm
            'avg_roi_size': avg_roi_size,
            'roi_stability': roi_stability,
            'calibration_samples': len(self.roi_history)
        }
    
    def reset_calibration(self):
        """Reset calibration history"""
        self.roi_history.clear()
        self.distance_history.clear()
        logger.info("ROI calibration reset")