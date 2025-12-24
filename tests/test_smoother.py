"""
Unit tests for GestureSmoother
"""
import unittest
import time
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from logic.gesture_smoother import GestureSmoother


class TestGestureSmoother(unittest.TestCase):
    
    def setUp(self):
        """Set up test case"""
        self.smoother = GestureSmoother(window_size=3, debounce_time=0.1)
    
    def test_initialization(self):
        """Test smoother initialization"""
        self.assertEqual(self.smoother.window_size, 3)
        self.assertEqual(self.smoother.debounce_time, 0.1)
        self.assertIsNone(self.smoother.current_gesture)
    
    def test_single_prediction(self):
        """Test processing single prediction"""
        prediction = {
            'gesture': 'palm',
            'confidence': 0.8,
            'is_confident': True
        }
        
        result = self.smoother.process_prediction(prediction)
        
        self.assertIn('gesture', result)
        self.assertIn('is_stable', result)
        self.assertIn('raw_gesture', result)
    
    def test_temporal_smoothing(self):
        """Test temporal smoothing with consistent predictions"""
        predictions = [
            {'gesture': 'palm', 'confidence': 0.8, 'is_confident': True},
            {'gesture': 'palm', 'confidence': 0.9, 'is_confident': True},
            {'gesture': 'palm', 'confidence': 0.7, 'is_confident': True}
        ]
        
        results = []
        for pred in predictions:
            result = self.smoother.process_prediction(pred)
            results.append(result)
        
        # Last result should be stable
        self.assertTrue(results[-1]['is_stable'])
        self.assertEqual(results[-1]['gesture'], 'palm')
    
    def test_debouncing(self):
        """Test debouncing prevents rapid changes"""
        # First gesture
        pred1 = {'gesture': 'palm', 'confidence': 0.8, 'is_confident': True}
        result1 = self.smoother.process_prediction(pred1)
        
        # Immediate different gesture (should be debounced)
        pred2 = {'gesture': 'fist', 'confidence': 0.8, 'is_confident': True}
        result2 = self.smoother.process_prediction(pred2)
        
        # Should still return previous gesture due to debouncing
        self.assertNotEqual(result2['gesture'], 'fist')
    
    def test_uncertain_predictions(self):
        """Test handling of uncertain predictions"""
        prediction = {
            'gesture': 'uncertain',
            'confidence': 0.3,
            'is_confident': False
        }
        
        result = self.smoother.process_prediction(prediction)
        
        self.assertFalse(result['is_stable'])
    
    def test_reset(self):
        """Test smoother reset"""
        # Add some predictions
        pred = {'gesture': 'palm', 'confidence': 0.8, 'is_confident': True}
        self.smoother.process_prediction(pred)
        
        # Reset
        self.smoother.reset()
        
        self.assertEqual(len(self.smoother.prediction_window), 0)
        self.assertIsNone(self.smoother.current_gesture)
    
    def test_stats(self):
        """Test statistics retrieval"""
        pred = {'gesture': 'palm', 'confidence': 0.8, 'is_confident': True}
        self.smoother.process_prediction(pred)
        
        stats = self.smoother.get_stats()
        
        self.assertIn('window_size', stats)
        self.assertIn('current_gesture', stats)
        self.assertIn('gesture_duration', stats)


if __name__ == '__main__':
    unittest.main()