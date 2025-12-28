#!/usr/bin/env python3
"""
Debug Model Predictions - Verify Class Index Order
Tests static images from LeapGestRecog to determine actual model class mapping
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
from loguru import logger
import json

# Import HAPTICA modules
from preprocessing.transforms import ImageTransforms
from inference.predictor import GesturePredictor

def test_static_image_predictions():
    """Test model predictions on static LeapGestRecog images"""
    logger.info("=== DEBUGGING MODEL CLASS INDEX ORDER ===")
    
    # Initialize components
    transforms = ImageTransforms(target_size=(50, 50))
    predictor = GesturePredictor("models/hand_recognition_model.h5", "config/labels.json")
    
    # LeapGestRecog class order (based on directory structure)
    leapgest_classes = {
        0: "01_palm",
        1: "02_l", 
        2: "03_fist",
        3: "04_fist_moved",
        4: "05_thumb",
        5: "06_index", 
        6: "07_ok",
        7: "08_palm_moved",
        8: "09_c",
        9: "10_down"
    }
    
    # Test images from each class
    test_results = {}
    
    for class_idx, class_name in leapgest_classes.items():
        logger.info(f"\n--- Testing {class_name} (Expected Index: {class_idx}) ---")
        
        # Find test image
        test_image_path = None
        for subject in range(10):  # Try subjects 00-09
            subject_dir = Path(f"leapgestrecog/{subject:02d}/{class_name}")
            if subject_dir.exists():
                # Get first image from this class
                image_files = list(subject_dir.glob("*.png"))
                if image_files:
                    test_image_path = image_files[0]
                    break
        
        if test_image_path is None:
            logger.warning(f"No test image found for {class_name}")
            continue
            
        # Load and preprocess image
        try:
            image = cv2.imread(str(test_image_path))
            if image is None:
                logger.warning(f"Could not load image: {test_image_path}")
                continue
                
            # Preprocess exactly like runtime
            processed_tensor = transforms.preprocess_roi(image)
            
            if processed_tensor is None:
                logger.warning(f"Preprocessing failed for {test_image_path}")
                continue
            
            # Get raw prediction
            prediction = predictor.predict(processed_tensor)
            
            # Log detailed results
            logger.info(f"Image: {test_image_path.name}")
            logger.info(f"Predicted Class Index: {prediction['class_index']}")
            logger.info(f"Predicted Label: {prediction['gesture']}")
            logger.info(f"Confidence: {prediction['confidence']:.3f}")
            logger.info(f"Raw Probabilities: {[f'{p:.3f}' for p in prediction['probabilities']]}")
            
            # Store results
            test_results[class_name] = {
                'expected_index': class_idx,
                'predicted_index': prediction['class_index'],
                'predicted_label': prediction['gesture'],
                'confidence': prediction['confidence'],
                'probabilities': prediction['probabilities']
            }
            
        except Exception as e:
            logger.error(f"Error processing {class_name}: {e}")
    
    # Analyze results and determine correct mapping
    logger.info("\n=== ANALYSIS: CORRECT CLASS INDEX MAPPING ===")
    
    correct_mapping = {}
    for class_name, result in test_results.items():
        predicted_idx = result['predicted_index']
        confidence = result['confidence']
        
        if confidence > 0.5:  # Only consider confident predictions
            if predicted_idx not in correct_mapping:
                correct_mapping[predicted_idx] = []
            correct_mapping[predicted_idx].append({
                'class_name': class_name,
                'confidence': confidence
            })
    
    # Generate corrected labels.json
    logger.info("\n=== CORRECTED LABELS.JSON ===")
    corrected_labels = {}
    
    for idx in range(10):
        if idx in correct_mapping:
            # Find the most confident prediction for this index
            best_match = max(correct_mapping[idx], key=lambda x: x['confidence'])
            class_name = best_match['class_name']
            
            # Convert to our label format
            if class_name == "01_palm":
                corrected_labels[str(idx)] = "palm"
            elif class_name == "02_l":
                corrected_labels[str(idx)] = "l_shape"
            elif class_name == "03_fist":
                corrected_labels[str(idx)] = "fist"
            elif class_name == "04_fist_moved":
                corrected_labels[str(idx)] = "fist_moved"
            elif class_name == "05_thumb":
                corrected_labels[str(idx)] = "thumb"
            elif class_name == "06_index":
                corrected_labels[str(idx)] = "index"
            elif class_name == "07_ok":
                corrected_labels[str(idx)] = "ok"
            elif class_name == "08_palm_moved":
                corrected_labels[str(idx)] = "palm_moved"
            elif class_name == "09_c":
                corrected_labels[str(idx)] = "c_shape"
            elif class_name == "10_down":
                corrected_labels[str(idx)] = "down"
            
            logger.info(f"Index {idx}: {corrected_labels[str(idx)]} (confidence: {best_match['confidence']:.3f})")
        else:
            corrected_labels[str(idx)] = f"unknown_{idx}"
            logger.info(f"Index {idx}: unknown_{idx} (no confident predictions)")
    
    # Save corrected labels
    corrected_config = {
        "gesture_classes": corrected_labels,
        "confidence_threshold": 0.7,
        "smoothing_window": 5,
        "debounce_frames": 10
    }
    
    with open("config/labels_corrected.json", 'w') as f:
        json.dump(corrected_config, f, indent=2)
    
    logger.info(f"\nCorrected labels saved to: config/labels_corrected.json")
    
    return test_results, corrected_labels

def test_preprocessing_shape():
    """Test preprocessing output shape"""
    logger.info("\n=== TESTING PREPROCESSING SHAPE ===")
    
    transforms = ImageTransforms(target_size=(50, 50))
    
    # Create test image
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Test preprocessing
    processed = transforms.preprocess_roi(test_image)
    
    logger.info(f"Input shape: {test_image.shape}")
    logger.info(f"Output shape: {processed.shape}")
    logger.info(f"Output dtype: {processed.dtype}")
    logger.info(f"Output range: [{processed.min():.3f}, {processed.max():.3f}]")
    
    # Verify expected shape
    expected_shape = (1, 50, 50, 1)
    if processed.shape == expected_shape:
        logger.info(f"✅ Shape is correct: {expected_shape}")
    else:
        logger.error(f"❌ Shape is wrong! Expected: {expected_shape}, Got: {processed.shape}")
    
    return processed.shape == expected_shape

def main():
    """Main debug function"""
    logger.info("Starting model prediction debugging...")
    
    # Test 1: Preprocessing shape
    shape_correct = test_preprocessing_shape()
    
    # Test 2: Static image predictions
    test_results, corrected_labels = test_static_image_predictions()
    
    # Summary
    logger.info("\n=== DEBUGGING SUMMARY ===")
    logger.info(f"Preprocessing shape correct: {shape_correct}")
    logger.info(f"Tested {len(test_results)} gesture classes")
    logger.info("Corrected labels generated in config/labels_corrected.json")
    logger.info("\nNext steps:")
    logger.info("1. Review the corrected labels")
    logger.info("2. Replace config/labels.json with corrected version")
    logger.info("3. Test real-time predictions")

if __name__ == "__main__":
    main()