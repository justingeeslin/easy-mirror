#!/usr/bin/env python3
"""
Basic Image Filters for Easy Mirror
Provides various computer vision filters for real-time video processing.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BasicFilters:
    """Collection of basic image filters for real-time video processing."""
    
    def __init__(self):
        """Initialize the basic filters system."""
        self.filters = {
            'none': self.no_filter,
            'blur': self.blur_filter,
            'edge': self.edge_filter,
            'grayscale': self.grayscale_filter,
            'sepia': self.sepia_filter,
            'invert': self.invert_filter,
            'emboss': self.emboss_filter,
            'cartoon': self.cartoon_filter,
            'vintage': self.vintage_filter,
            'cool': self.cool_filter,
            'warm': self.warm_filter
        }
    
    def get_available_filters(self):
        """Get list of available basic filters."""
        return list(self.filters.keys())
    
    def apply_filter(self, frame, filter_name):
        """Apply a specific filter to the frame."""
        if filter_name in self.filters:
            try:
                return self.filters[filter_name](frame)
            except Exception as e:
                logger.error(f"Error applying filter {filter_name}: {e}")
                return self.no_filter(frame)
        else:
            logger.warning(f"Unknown filter: {filter_name}")
            return self.no_filter(frame)
    
    def no_filter(self, frame):
        """No filter applied."""
        return frame
    
    def blur_filter(self, frame):
        """Apply Gaussian blur."""
        return cv2.GaussianBlur(frame, (15, 15), 0)
    
    def edge_filter(self, frame):
        """Apply edge detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def grayscale_filter(self, frame):
        """Convert to grayscale."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    def sepia_filter(self, frame):
        """Apply sepia tone effect."""
        sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        return cv2.transform(frame, sepia_kernel)
    
    def invert_filter(self, frame):
        """Invert colors."""
        return cv2.bitwise_not(frame)
    
    def emboss_filter(self, frame):
        """Apply emboss effect."""
        kernel = np.array([[-2, -1, 0],
                          [-1, 1, 1],
                          [0, 1, 2]])
        return cv2.filter2D(frame, -1, kernel)
    
    def cartoon_filter(self, frame):
        """Apply cartoon effect."""
        # Reduce colors
        data = np.float32(frame).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(frame.shape)
        
        # Create edge mask
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine
        cartoon = cv2.bitwise_and(segmented_image, edges)
        return cartoon
    
    def vintage_filter(self, frame):
        """Apply vintage effect."""
        # Add noise
        noise = np.random.randint(0, 50, frame.shape, dtype=np.uint8)
        vintage = cv2.add(frame, noise)
        
        # Apply sepia-like color transformation
        vintage = cv2.addWeighted(vintage, 0.8, self.sepia_filter(vintage), 0.2, 0)
        
        # Reduce brightness slightly
        vintage = cv2.convertScaleAbs(vintage, alpha=0.9, beta=-10)
        
        return vintage
    
    def cool_filter(self, frame):
        """Apply cool color temperature."""
        # Increase blue channel, decrease red
        frame_cool = frame.copy()
        frame_cool[:, :, 0] = np.clip(frame_cool[:, :, 0] * 1.2, 0, 255)  # Blue
        frame_cool[:, :, 2] = np.clip(frame_cool[:, :, 2] * 0.8, 0, 255)  # Red
        return frame_cool
    
    def warm_filter(self, frame):
        """Apply warm color temperature."""
        # Increase red channel, decrease blue
        frame_warm = frame.copy()
        frame_warm[:, :, 0] = np.clip(frame_warm[:, :, 0] * 0.8, 0, 255)  # Blue
        frame_warm[:, :, 2] = np.clip(frame_warm[:, :, 2] * 1.2, 0, 255)  # Red
        return frame_warm