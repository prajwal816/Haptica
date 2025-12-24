"""
Preprocessing Module - Transforms ROI for model input
"""
import cv2
import numpy as np
from typing import Tuple, Optional
from loguru import logger


class ImageTransforms:
    """Image preprocessing pipeline for gesture recognition model"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224), normalize: bool = True):
        self.target_size = target_size
        self.normalize = normalize
        logger.info(f"Transforms initialized: size={target_size}, normalize={normalize}")
    
    def preprocess_roi(self, roi: np.ndarray) -> Optional[np.ndarray]:
        """
        Complete preprocessing pipeline for ROI
        
        Args:
            roi: Hand region of interest
            
        Returns:
            Model-ready tensor or None if preprocessing fails
        """
        if roi is None or roi.size == 0:
            return None
            
        try:
            # Resize to target dimensions
            processed = cv2.resize(roi, self.target_size, interpolation=cv2.INTER_AREA)
            
            # Convert to RGB if needed (model expects RGB)
            if len(processed.shape) == 3 and processed.shape[2] == 3:
                processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values
            if self.normalize:
                processed = processed.astype(np.float32) / 255.0
            
            # Add batch dimension
            processed = np.expand_dims(processed, axis=0)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            return None
    
    def augment_for_training(self, roi: np.ndarray) -> np.ndarray:
        """
        Apply data augmentation (for training pipeline)
        """
        try:
            # Random brightness adjustment
            if np.random.random() > 0.5:
                brightness = np.random.uniform(0.8, 1.2)
                roi = cv2.convertScaleAbs(roi, alpha=brightness, beta=0)
            
            # Random rotation
            if np.random.random() > 0.5:
                angle = np.random.uniform(-15, 15)
                center = (roi.shape[1] // 2, roi.shape[0] // 2)
                matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                roi = cv2.warpAffine(roi, matrix, (roi.shape[1], roi.shape[0]))
            
            # Random horizontal flip
            if np.random.random() > 0.5:
                roi = cv2.flip(roi, 1)
                
            return roi
            
        except Exception as e:
            logger.error(f"Error in augmentation: {e}")
            return roi
    
    def validate_input(self, tensor: np.ndarray) -> bool:
        """Validate preprocessed tensor"""
        try:
            # Check shape
            expected_shape = (1, self.target_size[0], self.target_size[1], 3)
            if tensor.shape != expected_shape:
                logger.warning(f"Unexpected tensor shape: {tensor.shape}, expected: {expected_shape}")
                return False
            
            # Check value range
            if self.normalize:
                if tensor.min() < 0 or tensor.max() > 1:
                    logger.warning(f"Values out of range [0,1]: min={tensor.min()}, max={tensor.max()}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return False