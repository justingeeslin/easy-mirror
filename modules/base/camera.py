#!/usr/bin/env python3
"""
Camera Management for Easy Mirror
Handles camera initialization, frame capture, and demo mode.
"""

import cv2
import os
import logging

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages camera initialization and frame capture with fallback options."""
    
    def __init__(self):
        """Initialize the camera manager."""
        self.camera = None
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize the camera with fallback options for different systems."""
        # Check if demo mode is requested
        if os.environ.get('DEMO_MODE', '').lower() in ['true', '1', 'yes']:
            try:
                from demo_mode import DemoCamera
                self.camera = DemoCamera()
                logger.info("Demo mode activated - using simulated camera")
                return
            except ImportError:
                logger.warning("Demo mode requested but demo_mode.py not available")
        
        camera_indices = [0, 1, 2, -1]  # Try different camera indices
        
        for idx in camera_indices:
            try:
                self.camera = cv2.VideoCapture(idx)
                if self.camera.isOpened():
                    # Set camera properties for better performance
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.camera.set(cv2.CAP_PROP_FPS, 30)
                    
                    # Test if we can read a frame
                    ret, frame = self.camera.read()
                    if ret:
                        logger.info(f"Camera initialized successfully on index {idx}")
                        return
                    else:
                        self.camera.release()
            except Exception as e:
                logger.warning(f"Failed to initialize camera on index {idx}: {e}")
                continue
        
        # If no real camera found, try demo mode as fallback
        try:
            from demo_mode import DemoCamera
            logger.info("No real camera found, falling back to demo mode")
            self.camera = DemoCamera()
            return
        except ImportError:
            pass
        
        logger.error("Could not initialize any camera and demo mode not available")
        self.camera = None
    
    def is_available(self):
        """Check if camera is available."""
        return self.camera is not None and self.camera.isOpened()
    
    def read_frame(self):
        """Read a frame from the camera."""
        if not self.is_available():
            return False, None
        
        return self.camera.read()
    
    def cleanup(self):
        """Clean up camera resources."""
        if self.camera:
            self.camera.release()
            self.camera = None