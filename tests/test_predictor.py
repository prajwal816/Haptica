"""
Unit tests for GesturePredictor
"""
import unittest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from inference.predictor import GesturePredictor


class TestGesturePredictor(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.model_path = "models/hand_recognition_model.h5"
        cls.labels_path = "config/labels.json"
        
        # Skip tests if model doesn't exist
        if not Path(cls.model_path).exists():
            cls.skipTest("Model file not found")
    
    def setUp(self):
        """Set up test case"""
        self.predictor = GesturePredictor(self.model_path, self.labels_path)
    
    def test_model_loading(self):
        """Test model loads successfully"""
        self.assertIsNotNone(self.predictor.model)
        self.assertIsInstance(self.predictor.labels, dict)
    
    def test_prediction_shape(self):
        """Test prediction with correct input shape"""
        # Create dummy input
        dummy_input = np.random.random((1, 224, 224, 3)).astype(np.float32)
        
        result = self.predictor.predict(dummy_input)
        
        self.assertIsInstance(result, dict)
        self.assertIn('gesture', result)
        self.assertIn('confidence', result)
        self.assertIn('is_confident', result)
    
    def test_invalid_input(self):
        """Test prediction with invalid input"""
        # Wrong shape
        invalid_input = np.random.random((224, 224, 3)).astype(np.float32)
        
        # Should handle gracefully
        result = self.predictor.predict(invalid_input)
        self.assertEqual(result['gesture'], 'none')
    
    def test_batch_prediction(self):
        """Test batch prediction"""
        batch_input = np.random.random((3, 224, 224, 3)).astype(np.float32)
        
        results = self.predictor.predict_batch(batch_input)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('gesture', result)
            self.assertIn('confidence', result)
    
    def test_model_info(self):
        """Test model info retrieval"""
        info = self.predictor.get_model_info()
        
        self.assertIn('input_shape', info)
        self.assertIn('output_shape', info)
        self.assertIn('num_classes', info)


if __name__ == '__main__':
    unittest.main()