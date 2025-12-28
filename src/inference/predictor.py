"""
Inference Engine - Handles model loading and prediction
"""
import tensorflow as tf
import numpy as np
from typing import Dict, Optional, Tuple
from pathlib import Path
from loguru import logger
import json


class GesturePredictor:
    """TensorFlow model inference engine"""
    
    def __init__(self, model_path: str, labels_path: str):
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        self.model = None
        self.labels = {}
        self.confidence_threshold = 0.7
        
        self._load_model()
        self._load_labels()
    
    def _load_model(self):
        """Load the trained gesture recognition model"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model = tf.keras.models.load_model(str(self.model_path))
            logger.info(f"Model loaded successfully: {self.model_path}")
            
            # Log model architecture
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_labels(self):
        """Load gesture labels and configuration"""
        try:
            with open(self.labels_path, 'r') as f:
                config = json.load(f)
            
            self.labels = config.get('gesture_classes', {})
            self.confidence_threshold = config.get('confidence_threshold', 0.7)
            
            logger.info(f"Labels loaded: {len(self.labels)} classes")
            logger.info(f"Confidence threshold: {self.confidence_threshold}")
            
        except Exception as e:
            logger.error(f"Failed to load labels: {e}")
            self.labels = {str(i): f"gesture_{i}" for i in range(10)}
    
    def predict(self, input_tensor: np.ndarray) -> Dict:
        """
        Make prediction on preprocessed input with horizontal flip fallback
        
        Args:
            input_tensor: Preprocessed image tensor
            
        Returns:
            Dictionary with prediction results
        """
        if self.model is None:
            logger.error("Model not loaded")
            return self._empty_prediction()
        
        try:
            # Make initial prediction
            predictions = self.model.predict(input_tensor, verbose=0)
            
            # Get class probabilities
            probabilities = predictions[0]
            predicted_class_idx = np.argmax(probabilities)
            confidence = float(probabilities[predicted_class_idx])
            
            # FIX 3: HORIZONTAL FLIP FALLBACK for orientation mismatch
            # If confidence is low, try horizontal flip
            if confidence < 0.8:
                # Create horizontally flipped version
                flipped_tensor = input_tensor.copy()
                flipped_tensor[0, :, :, 0] = np.fliplr(input_tensor[0, :, :, 0])
                
                # Make prediction on flipped image
                flipped_predictions = self.model.predict(flipped_tensor, verbose=0)
                flipped_probabilities = flipped_predictions[0]
                flipped_class_idx = np.argmax(flipped_probabilities)
                flipped_confidence = float(flipped_probabilities[flipped_class_idx])
                
                # Use flipped prediction if it's more confident
                if flipped_confidence > confidence:
                    probabilities = flipped_probabilities
                    predicted_class_idx = flipped_class_idx
                    confidence = flipped_confidence
                    logger.debug(f"Used flipped prediction: {confidence:.3f} > {float(predictions[0][np.argmax(predictions[0])]):.3f}")
            
            # Get gesture label
            gesture_label = self.labels.get(str(predicted_class_idx), f"unknown_{predicted_class_idx}")
            
            # Check confidence threshold
            is_confident = confidence >= self.confidence_threshold
            
            # DEBUG: Log raw predictions for debugging
            logger.debug(f"Raw prediction - Class: {predicted_class_idx}, Confidence: {confidence:.3f}, Label: {gesture_label}")
            logger.debug(f"Top 3 probabilities: {sorted(enumerate(probabilities), key=lambda x: x[1], reverse=True)[:3]}")
            
            result = {
                'gesture': gesture_label if is_confident else 'uncertain',
                'confidence': confidence,
                'class_index': int(predicted_class_idx),
                'probabilities': probabilities.tolist(),
                'is_confident': is_confident,
                'threshold': self.confidence_threshold
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._empty_prediction()
    
    def predict_batch(self, batch_tensor: np.ndarray) -> list:
        """Predict on batch of inputs"""
        try:
            predictions = self.model.predict(batch_tensor, verbose=0)
            results = []
            
            for i, probs in enumerate(predictions):
                predicted_class_idx = np.argmax(probs)
                confidence = float(probs[predicted_class_idx])
                gesture_label = self.labels.get(str(predicted_class_idx), f"unknown_{predicted_class_idx}")
                
                results.append({
                    'gesture': gesture_label if confidence >= self.confidence_threshold else 'uncertain',
                    'confidence': confidence,
                    'class_index': int(predicted_class_idx),
                    'is_confident': confidence >= self.confidence_threshold
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return [self._empty_prediction() for _ in range(len(batch_tensor))]
    
    def _empty_prediction(self) -> Dict:
        """Return empty prediction result"""
        return {
            'gesture': 'none',
            'confidence': 0.0,
            'class_index': -1,
            'probabilities': [],
            'is_confident': False,
            'threshold': self.confidence_threshold
        }
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        if self.model is None:
            return {}
        
        return {
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'num_classes': len(self.labels),
            'labels': self.labels,
            'confidence_threshold': self.confidence_threshold
        }