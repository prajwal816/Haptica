"""
Background Robustness Layer
Adaptive image enhancement for real-world conditions
"""
import cv2
import numpy as np
from typing import Tuple, Optional, Dict
from loguru import logger


class BackgroundRobustnessProcessor:
    """
    Enhances image quality and robustness for real-world conditions
    Implements CLAHE, background suppression, and optional skin-tone masking
    """
    
    def __init__(self, 
                 enable_clahe: bool = True,
                 enable_background_suppression: bool = True,
                 enable_skin_masking: bool = False):
        
        self.enable_clahe = enable_clahe
        self.enable_background_suppression = enable_background_suppression
        self.enable_skin_masking = enable_skin_masking
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        
        # Background suppression
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True, varThreshold=50
        )
        
        # Skin color ranges (HSV)
        self.skin_lower = np.array([0, 20, 70], dtype=np.uint8)
        self.skin_upper = np.array([20, 255, 255], dtype=np.uint8)
        
        # Motion detection
        self.prev_frame = None
        self.motion_threshold = 30
        
        logger.info(f"Background robustness initialized: "
                   f"CLAHE={enable_clahe}, BG_suppress={enable_background_suppression}, "
                   f"skin_mask={enable_skin_masking}")
    
    def enhance_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Apply comprehensive frame enhancement
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Enhanced frame and processing info
        """
        if frame is None:
            return frame, {}
        
        enhanced_frame = frame.copy()
        processing_info = {
            'clahe_applied': False,
            'background_suppressed': False,
            'skin_masked': False,
            'motion_detected': False
        }
        
        # 1. Adaptive Histogram Equalization (CLAHE)
        if self.enable_clahe:
            enhanced_frame = self._apply_clahe(enhanced_frame)
            processing_info['clahe_applied'] = True
        
        # 2. Background Motion Suppression
        if self.enable_background_suppression:
            enhanced_frame, motion_detected = self._suppress_background_motion(enhanced_frame)
            processing_info['background_suppressed'] = True
            processing_info['motion_detected'] = motion_detected
        
        # 3. Optional Skin-tone Masking
        if self.enable_skin_masking:
            enhanced_frame = self._apply_skin_masking(enhanced_frame)
            processing_info['skin_masked'] = True
        
        return enhanced_frame, processing_info
    
    def _apply_clahe(self, frame: np.ndarray) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization"""
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Apply CLAHE to L channel
            lab[:, :, 0] = self.clahe.apply(lab[:, :, 0])
            
            # Convert back to BGR
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"CLAHE enhancement failed: {e}")
            return frame
    
    def _suppress_background_motion(self, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Suppress background motion while preserving hand movements"""
        try:
            # Apply background subtraction
            fg_mask = self.background_subtractor.apply(frame)
            
            # Detect significant motion
            motion_detected = np.sum(fg_mask > 0) > (frame.shape[0] * frame.shape[1] * 0.05)
            
            if motion_detected:
                # Create enhanced frame focusing on moving regions
                # Dilate mask to include hand regions
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                fg_mask_dilated = cv2.dilate(fg_mask, kernel, iterations=2)
                
                # Apply mask to original frame
                enhanced_frame = frame.copy()
                enhanced_frame[fg_mask_dilated == 0] = enhanced_frame[fg_mask_dilated == 0] * 0.3
                
                return enhanced_frame, True
            else:
                return frame, False
                
        except Exception as e:
            logger.warning(f"Background suppression failed: {e}")
            return frame, False
    
    def _apply_skin_masking(self, frame: np.ndarray) -> np.ndarray:
        """Apply skin-tone based masking as fallback"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create skin mask
            skin_mask = cv2.inRange(hsv, self.skin_lower, self.skin_upper)
            
            # Morphological operations to clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            
            # Apply Gaussian blur to soften edges
            skin_mask = cv2.GaussianBlur(skin_mask, (3, 3), 0)
            
            # Create 3-channel mask
            skin_mask_3ch = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2BGR) / 255.0
            
            # Blend with original frame
            enhanced_frame = frame * skin_mask_3ch + frame * 0.3 * (1 - skin_mask_3ch)
            
            return enhanced_frame.astype(np.uint8)
            
        except Exception as e:
            logger.warning(f"Skin masking failed: {e}")
            return frame
    
    def enhance_roi(self, roi: np.ndarray) -> np.ndarray:
        """Apply targeted enhancement to hand ROI"""
        if roi is None or roi.size == 0:
            return roi
        
        try:
            enhanced_roi = roi.copy()
            
            # Noise reduction
            enhanced_roi = cv2.bilateralFilter(enhanced_roi, 9, 75, 75)
            
            # Sharpening kernel
            sharpening_kernel = np.array([[-1, -1, -1],
                                        [-1,  9, -1],
                                        [-1, -1, -1]])
            enhanced_roi = cv2.filter2D(enhanced_roi, -1, sharpening_kernel)
            
            # Gamma correction for better contrast
            gamma = 1.2
            enhanced_roi = np.power(enhanced_roi / 255.0, gamma) * 255.0
            enhanced_roi = enhanced_roi.astype(np.uint8)
            
            return enhanced_roi
            
        except Exception as e:
            logger.warning(f"ROI enhancement failed: {e}")
            return roi
    
    def detect_lighting_conditions(self, frame: np.ndarray) -> dict:
        """Analyze lighting conditions for adaptive processing"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate statistics
            mean_brightness = np.mean(gray)
            brightness_std = np.std(gray)
            
            # Histogram analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_normalized = hist.flatten() / hist.sum()
            
            # Detect conditions
            is_low_light = mean_brightness < 80
            is_high_contrast = brightness_std > 60
            is_backlit = hist_normalized[:50].sum() > 0.3 and hist_normalized[200:].sum() > 0.2
            
            return {
                'mean_brightness': float(mean_brightness),
                'brightness_std': float(brightness_std),
                'is_low_light': is_low_light,
                'is_high_contrast': is_high_contrast,
                'is_backlit': is_backlit,
                'lighting_quality': self._assess_lighting_quality(mean_brightness, brightness_std)
            }
            
        except Exception as e:
            logger.warning(f"Lighting analysis failed: {e}")
            return {}
    
    def _assess_lighting_quality(self, brightness: float, contrast: float) -> str:
        """Assess overall lighting quality"""
        if brightness < 50:
            return "poor_low_light"
        elif brightness > 200:
            return "poor_overexposed"
        elif contrast < 20:
            return "poor_low_contrast"
        elif contrast > 80:
            return "poor_high_contrast"
        elif 80 <= brightness <= 180 and 30 <= contrast <= 60:
            return "excellent"
        else:
            return "good"
    
    def adapt_processing_parameters(self, lighting_conditions: dict):
        """Adapt processing parameters based on lighting conditions"""
        if not lighting_conditions:
            return
        
        # Adjust CLAHE parameters
        if lighting_conditions.get('is_low_light', False):
            self.clahe.setClipLimit(4.0)  # More aggressive enhancement
        elif lighting_conditions.get('is_high_contrast', False):
            self.clahe.setClipLimit(2.0)  # Gentler enhancement
        else:
            self.clahe.setClipLimit(3.0)  # Default
        
        # Adjust background subtraction sensitivity
        if lighting_conditions.get('lighting_quality') == 'poor_low_light':
            self.background_subtractor.setVarThreshold(30)  # More sensitive
        else:
            self.background_subtractor.setVarThreshold(50)  # Default
    
    def reset_background_model(self):
        """Reset background subtraction model"""
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True, varThreshold=50
        )
        logger.info("Background model reset")