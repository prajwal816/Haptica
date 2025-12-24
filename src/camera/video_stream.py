"""
Video Stream Module - Handles camera input and frame acquisition
"""
import cv2
import threading
from typing import Optional, Tuple
from loguru import logger


class VideoStream:
    """Professional video stream handler with threading support"""
    
    def __init__(self, source: int = 0, resolution: Tuple[int, int] = (640, 480)):
        self.source = source
        self.resolution = resolution
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame = None
        self.running = False
        self.thread = None
        
    def start(self) -> bool:
        """Initialize and start video capture"""
        try:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera source: {self.source}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.running = True
            self.thread = threading.Thread(target=self._update_frame)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info(f"Video stream started: {self.resolution[0]}x{self.resolution[1]}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting video stream: {e}")
            return False
    
    def _update_frame(self):
        """Continuously update frame in background thread"""
        while self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.frame = cv2.flip(frame, 1)  # Mirror for natural interaction
            else:
                logger.warning("Failed to read frame")
                
    def get_frame(self):
        """Get current frame"""
        return self.frame
    
    def stop(self):
        """Stop video capture and cleanup"""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        logger.info("Video stream stopped")
    
    def is_running(self) -> bool:
        """Check if stream is active"""
        return self.running and self.cap and self.cap.isOpened()