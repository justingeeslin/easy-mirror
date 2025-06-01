#!/usr/bin/env python3
"""
Demo mode for Easy Mirror - Creates a simulated video feed for testing
"""

import cv2
import numpy as np
import time
import math

class DemoCamera:
    """Simulates a camera for demo purposes."""
    
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.frame_count = 0
        self.start_time = time.time()
    
    def isOpened(self):
        return True
    
    def set(self, prop, value):
        # Simulate setting camera properties
        pass
    
    def read(self):
        """Generate a demo frame with moving patterns."""
        # Create a colorful animated background
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Current time for animation
        t = time.time() - self.start_time
        
        # Create animated gradient background
        for y in range(self.height):
            for x in range(self.width):
                # Create moving wave patterns
                wave1 = math.sin((x + t * 50) * 0.02) * 127 + 128
                wave2 = math.sin((y + t * 30) * 0.03) * 127 + 128
                wave3 = math.sin((x + y + t * 40) * 0.01) * 127 + 128
                
                frame[y, x] = [
                    int(wave1) % 256,  # Red channel
                    int(wave2) % 256,  # Green channel
                    int(wave3) % 256   # Blue channel
                ]
        
        # Add some moving shapes
        center_x = int(self.width // 2 + math.sin(t) * 100)
        center_y = int(self.height // 2 + math.cos(t * 0.7) * 80)
        
        # Draw a moving circle
        cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)
        cv2.circle(frame, (center_x, center_y), 40, (0, 0, 0), -1)
        
        # Add text overlay
        text = f"DEMO MODE - Frame {self.frame_count}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = f"Time: {t:.1f}s"
        cv2.putText(frame, timestamp, (10, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add filter test pattern
        # Create a checkerboard pattern in corner
        checker_size = 20
        for i in range(0, 100, checker_size):
            for j in range(0, 100, checker_size):
                if (i // checker_size + j // checker_size) % 2:
                    cv2.rectangle(frame, 
                                (self.width - 100 + i, j), 
                                (self.width - 100 + i + checker_size, j + checker_size), 
                                (255, 255, 255), -1)
        
        self.frame_count += 1
        return True, frame
    
    def release(self):
        pass