"""
Asynchronous Processing Pipeline
Producer-consumer architecture for high-performance gesture recognition
"""
import asyncio
import threading
import queue
import time
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
import numpy as np


@dataclass
class PipelineFrame:
    """Frame data structure for pipeline processing"""
    frame_id: int
    timestamp: float
    raw_frame: np.ndarray
    processed_frame: Optional[np.ndarray] = None
    hand_info: Optional[Dict] = None
    prediction: Optional[Dict] = None
    action_result: Optional[Dict] = None


class AsyncGesturePipeline:
    """
    High-performance asynchronous gesture recognition pipeline
    Implements producer-consumer pattern with separate threads for:
    - Camera capture
    - ML inference  
    - Action execution
    """
    
    def __init__(self, 
                 max_queue_size: int = 10,
                 max_workers: int = 3,
                 target_fps: float = 30.0):
        
        self.max_queue_size = max_queue_size
        self.max_workers = max_workers
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        
        # Processing queues
        self.capture_queue = queue.Queue(maxsize=max_queue_size)
        self.inference_queue = queue.Queue(maxsize=max_queue_size)
        self.action_queue = queue.Queue(maxsize=max_queue_size)
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Pipeline components (to be injected)
        self.camera_source = None
        self.hand_detector = None
        self.gesture_predictor = None
        self.action_mapper = None
        self.state_machine = None
        
        # Pipeline control
        self.running = False
        self.threads = []
        
        # Performance metrics
        self.metrics = {
            'frames_captured': 0,
            'frames_processed': 0,
            'frames_dropped': 0,
            'inference_time_ms': [],
            'total_latency_ms': [],
            'fps_actual': 0.0
        }
        
        # Frame tracking
        self.frame_counter = 0
        self.last_fps_time = time.time()
        self.fps_frame_count = 0
        
        logger.info(f"Async pipeline initialized: queue_size={max_queue_size}, "
                   f"workers={max_workers}, target_fps={target_fps}")
    
    def inject_components(self, 
                         camera_source,
                         hand_detector, 
                         gesture_predictor,
                         action_mapper,
                         state_machine):
        """Inject pipeline components"""
        self.camera_source = camera_source
        self.hand_detector = hand_detector
        self.gesture_predictor = gesture_predictor
        self.action_mapper = action_mapper
        self.state_machine = state_machine
        logger.info("Pipeline components injected")
    
    def start(self):
        """Start the asynchronous pipeline"""
        if self.running:
            logger.warning("Pipeline already running")
            return
        
        if not all([self.camera_source, self.hand_detector, 
                   self.gesture_predictor, self.action_mapper]):
            raise ValueError("Pipeline components not properly injected")
        
        self.running = True
        
        # Start pipeline threads
        self.threads = [
            threading.Thread(target=self._camera_capture_thread, daemon=True),
            threading.Thread(target=self._inference_thread, daemon=True),
            threading.Thread(target=self._action_execution_thread, daemon=True),
            threading.Thread(target=self._metrics_thread, daemon=True)
        ]
        
        for thread in self.threads:
            thread.start()
        
        logger.info("Async pipeline started")
    
    def stop(self):
        """Stop the pipeline"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2.0)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Async pipeline stopped")
    
    def _camera_capture_thread(self):
        """Camera capture producer thread"""
        logger.info("Camera capture thread started")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Capture frame
                frame = self.camera_source.get_frame()
                if frame is None:
                    time.sleep(0.001)  # Brief pause if no frame
                    continue
                
                # Create pipeline frame
                pipeline_frame = PipelineFrame(
                    frame_id=self.frame_counter,
                    timestamp=start_time,
                    raw_frame=frame
                )
                
                # Try to add to queue (non-blocking)
                try:
                    self.capture_queue.put_nowait(pipeline_frame)
                    self.metrics['frames_captured'] += 1
                    self.frame_counter += 1
                except queue.Full:
                    # Drop frame if queue is full
                    self.metrics['frames_dropped'] += 1
                    logger.debug("Dropped frame - capture queue full")
                
                # Frame rate control
                elapsed = time.time() - start_time
                sleep_time = max(0, self.frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Camera capture error: {e}")
                time.sleep(0.1)
    
    def _inference_thread(self):
        """ML inference consumer/producer thread"""
        logger.info("Inference thread started")
        
        while self.running:
            try:
                # Get frame from capture queue
                try:
                    pipeline_frame = self.capture_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                inference_start = time.time()
                
                # Hand detection
                hands_info, annotated_frame = self.hand_detector.detect_hands(
                    pipeline_frame.raw_frame
                )
                pipeline_frame.processed_frame = annotated_frame
                pipeline_frame.hand_info = hands_info
                
                # Gesture prediction if hand detected
                if hands_info:
                    hand_info = hands_info[0]  # Use first hand
                    roi = hand_info.get('roi')
                    
                    if roi is not None:
                        # This would be done by preprocessor and predictor
                        # For now, simulate prediction
                        prediction = {
                            'gesture': 'palm',  # Placeholder
                            'confidence': 0.8,
                            'is_confident': True,
                            'is_stable': True
                        }
                        pipeline_frame.prediction = prediction
                
                # Record inference time
                inference_time = (time.time() - inference_start) * 1000
                self.metrics['inference_time_ms'].append(inference_time)
                
                # Keep only recent metrics (sliding window)
                if len(self.metrics['inference_time_ms']) > 100:
                    self.metrics['inference_time_ms'] = self.metrics['inference_time_ms'][-100:]
                
                # Add to action queue
                try:
                    self.inference_queue.put_nowait(pipeline_frame)
                except queue.Full:
                    logger.debug("Dropped frame - inference queue full")
                
                self.metrics['frames_processed'] += 1
                
            except Exception as e:
                logger.error(f"Inference error: {e}")
    
    def _action_execution_thread(self):
        """Action execution consumer thread"""
        logger.info("Action execution thread started")
        
        while self.running:
            try:
                # Get processed frame
                try:
                    pipeline_frame = self.inference_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Process through state machine if prediction available
                if pipeline_frame.prediction and self.state_machine:
                    from core.state_machine import GestureEvent
                    
                    gesture_event = GestureEvent(
                        gesture=pipeline_frame.prediction['gesture'],
                        confidence=pipeline_frame.prediction['confidence'],
                        timestamp=pipeline_frame.timestamp,
                        is_stable=pipeline_frame.prediction.get('is_stable', False)
                    )
                    
                    # Process through state machine
                    state_result = self.state_machine.process_gesture(gesture_event)
                    
                    # Execute action if required
                    if state_result.get('action'):
                        action_result = self.action_mapper.execute_action(
                            state_result['gesture'],
                            state_result['confidence']
                        )
                        pipeline_frame.action_result = action_result
                
                # Calculate total latency
                total_latency = (time.time() - pipeline_frame.timestamp) * 1000
                self.metrics['total_latency_ms'].append(total_latency)
                
                # Keep sliding window
                if len(self.metrics['total_latency_ms']) > 100:
                    self.metrics['total_latency_ms'] = self.metrics['total_latency_ms'][-100:]
                
                # Add to action queue for UI consumption
                try:
                    self.action_queue.put_nowait(pipeline_frame)
                except queue.Full:
                    # Remove oldest frame and add new one
                    try:
                        self.action_queue.get_nowait()
                        self.action_queue.put_nowait(pipeline_frame)
                    except queue.Empty:
                        pass
                
            except Exception as e:
                logger.error(f"Action execution error: {e}")
    
    def _metrics_thread(self):
        """Performance metrics calculation thread"""
        logger.info("Metrics thread started")
        
        while self.running:
            try:
                time.sleep(1.0)  # Update metrics every second
                
                current_time = time.time()
                time_elapsed = current_time - self.last_fps_time
                
                if time_elapsed >= 1.0:
                    # Calculate actual FPS
                    frames_in_period = self.metrics['frames_processed'] - self.fps_frame_count
                    self.metrics['fps_actual'] = frames_in_period / time_elapsed
                    
                    self.fps_frame_count = self.metrics['frames_processed']
                    self.last_fps_time = current_time
                
            except Exception as e:
                logger.error(f"Metrics calculation error: {e}")
    
    def get_latest_frame(self) -> Optional[PipelineFrame]:
        """Get latest processed frame for UI display"""
        try:
            return self.action_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_performance_metrics(self) -> dict:
        """Get current performance metrics"""
        inference_times = self.metrics['inference_time_ms']
        latency_times = self.metrics['total_latency_ms']
        
        return {
            'fps_actual': self.metrics['fps_actual'],
            'fps_target': self.target_fps,
            'frames_captured': self.metrics['frames_captured'],
            'frames_processed': self.metrics['frames_processed'],
            'frames_dropped': self.metrics['frames_dropped'],
            'drop_rate': (
                self.metrics['frames_dropped'] / 
                max(1, self.metrics['frames_captured'])
            ),
            'avg_inference_ms': np.mean(inference_times) if inference_times else 0,
            'avg_latency_ms': np.mean(latency_times) if latency_times else 0,
            'queue_sizes': {
                'capture': self.capture_queue.qsize(),
                'inference': self.inference_queue.qsize(),
                'action': self.action_queue.qsize()
            }
        }
    
    def adjust_target_fps(self, new_fps: float):
        """Dynamically adjust target FPS"""
        self.target_fps = max(1.0, min(60.0, new_fps))
        self.frame_interval = 1.0 / self.target_fps
        logger.info(f"Target FPS adjusted to: {self.target_fps}")
    
    def clear_queues(self):
        """Clear all processing queues"""
        queues = [self.capture_queue, self.inference_queue, self.action_queue]
        
        for q in queues:
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
        
        logger.info("Pipeline queues cleared")