#!/usr/bin/env python3
"""
Body Slimming System for Easy Mirror
Applies slimming effects to specific body regions using MediaPipe pose landmarks and image warping.
"""

import cv2
import numpy as np
import mediapipe as mp
import math
import logging
from typing import Tuple, Optional, List, Dict

logger = logging.getLogger(__name__)

class BodySlimming:
    def __init__(self):
        """Initialize the body slimming system."""
        self.mp_pose = mp.solutions.pose
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        
        # Initialize pose detection
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=True,  # Enable segmentation for better body isolation
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Initialize selfie segmentation for better person isolation
        self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1  # Use general model for better accuracy
        )
        
        # MediaPipe pose landmark indices
        self.landmark_indices = {
            'nose': 0,
            'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
            'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
            'left_ear': 7, 'right_ear': 8,
            'mouth_left': 9, 'mouth_right': 10,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_pinky': 17, 'right_pinky': 18,
            'left_index': 19, 'right_index': 20,
            'left_thumb': 21, 'right_thumb': 22,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28,
            'left_heel': 29, 'right_heel': 30,
            'left_foot_index': 31, 'right_foot_index': 32
        }
        
        # Default slimming parameters
        self.slimming_intensity = 0.0  # 0.0 to 1.0
        self.start_landmark = 'left_shoulder'
        self.end_landmark = 'left_hip'
        self.enabled = False
        
        # Predefined landmark pairs for common slimming regions
        self.slimming_regions = {
            'waist': ('left_shoulder', 'left_hip'),
            'torso': ('left_shoulder', 'left_knee'),
            'upper_body': ('left_ear', 'left_elbow'),
            'lower_body': ('left_hip', 'left_ankle'),
            'full_body': ('nose', 'left_ankle'),
            'arms': ('left_shoulder', 'left_wrist'),
            'legs': ('left_hip', 'left_ankle')
        }
    
    def get_landmark_position(self, landmarks, landmark_name: str, frame_width: int, frame_height: int) -> Optional[Tuple[float, float, float]]:
        """Get the pixel position of a landmark."""
        if landmark_name not in self.landmark_indices:
            return None
        
        landmark_idx = self.landmark_indices[landmark_name]
        if landmark_idx < len(landmarks.landmark):
            landmark = landmarks.landmark[landmark_idx]
            if landmark.visibility > 0.5:  # Only use visible landmarks
                x = landmark.x * frame_width
                y = landmark.y * frame_height
                z = landmark.z  # Relative depth
                return (x, y, z)
        return None
    
    def get_corresponding_landmark(self, landmark_name: str) -> str:
        """Get the corresponding landmark on the opposite side of the body."""
        if landmark_name.startswith('left_'):
            return landmark_name.replace('left_', 'right_')
        elif landmark_name.startswith('right_'):
            return landmark_name.replace('right_', 'left_')
        return landmark_name
    
    def create_slimming_mask(self, frame: np.ndarray, landmarks, start_landmark: str, end_landmark: str) -> np.ndarray:
        """Create a mask for the slimming region between two landmarks."""
        frame_height, frame_width = frame.shape[:2]
        mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        
        # Get landmark positions
        start_left = self.get_landmark_position(landmarks, start_landmark, frame_width, frame_height)
        end_left = self.get_landmark_position(landmarks, end_landmark, frame_width, frame_height)
        start_right = self.get_landmark_position(landmarks, self.get_corresponding_landmark(start_landmark), frame_width, frame_height)
        end_right = self.get_landmark_position(landmarks, self.get_corresponding_landmark(end_landmark), frame_width, frame_height)
        
        if not all([start_left, end_left, start_right, end_right]):
            return mask
        
        # Create a polygon mask for the slimming region
        points = np.array([
            [start_left[0], start_left[1]],
            [start_right[0], start_right[1]],
            [end_right[0], end_right[1]],
            [end_left[0], end_left[1]]
        ], dtype=np.int32)
        
        cv2.fillPoly(mask, [points], 255)
        
        # Apply Gaussian blur to create smooth transitions
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        
        return mask
    
    def apply_radial_slimming(self, frame: np.ndarray, center: Tuple[float, float], radius: float, intensity: float) -> np.ndarray:
        """Apply radial slimming effect around a center point."""
        if intensity <= 0:
            return frame
        
        frame_height, frame_width = frame.shape[:2]
        result = frame.copy()
        
        # Create coordinate grids
        y_coords, x_coords = np.ogrid[:frame_height, :frame_width]
        
        # Calculate distance from center
        dx = x_coords - center[0]
        dy = y_coords - center[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        # Create mask for affected area
        mask = distance < radius
        
        # Apply slimming transformation
        # Use a smooth falloff function
        factor = np.where(mask, 1.0 - intensity * (1.0 - distance[mask] / radius), 1.0)
        
        # Calculate new coordinates
        new_x = center[0] + dx[mask] * factor
        new_y = center[1] + dy[mask] * factor
        
        # Ensure coordinates are within bounds
        new_x = np.clip(new_x, 0, frame_width - 1)
        new_y = np.clip(new_y, 0, frame_height - 1)
        
        # Apply bilinear interpolation for smooth results
        x_floor = np.floor(new_x).astype(int)
        y_floor = np.floor(new_y).astype(int)
        x_ceil = np.minimum(x_floor + 1, frame_width - 1)
        y_ceil = np.minimum(y_floor + 1, frame_height - 1)
        
        # Calculate interpolation weights
        wx = new_x - x_floor
        wy = new_y - y_floor
        
        # Get pixel values at four corners
        tl = frame[y_floor, x_floor]  # top-left
        tr = frame[y_floor, x_ceil]   # top-right
        bl = frame[y_ceil, x_floor]   # bottom-left
        br = frame[y_ceil, x_ceil]    # bottom-right
        
        # Bilinear interpolation
        top = tl * (1 - wx)[:, np.newaxis] + tr * wx[:, np.newaxis]
        bottom = bl * (1 - wx)[:, np.newaxis] + br * wx[:, np.newaxis]
        interpolated = top * (1 - wy)[:, np.newaxis] + bottom * wy[:, np.newaxis]
        
        # Apply the slimmed pixels back to the result
        y_indices, x_indices = np.where(mask)
        result[y_indices, x_indices] = interpolated.astype(np.uint8)
        
        return result
    
    def apply_directional_slimming(self, frame: np.ndarray, landmarks, start_landmark: str, end_landmark: str, intensity: float) -> np.ndarray:
        """Apply directional slimming between two landmarks."""
        if intensity <= 0:
            return frame
        
        frame_height, frame_width = frame.shape[:2]
        
        # Get landmark positions
        start_left = self.get_landmark_position(landmarks, start_landmark, frame_width, frame_height)
        end_left = self.get_landmark_position(landmarks, end_landmark, frame_width, frame_height)
        start_right = self.get_landmark_position(landmarks, self.get_corresponding_landmark(start_landmark), frame_width, frame_height)
        end_right = self.get_landmark_position(landmarks, self.get_corresponding_landmark(end_landmark), frame_width, frame_height)
        
        if not all([start_left, end_left, start_right, end_right]):
            return frame
        
        # Calculate center line and width at different heights
        result = frame.copy()
        
        # Define the slimming region
        top_y = min(start_left[1], start_right[1])
        bottom_y = max(end_left[1], end_right[1])
        
        if bottom_y <= top_y:
            return frame
        
        # Apply slimming line by line
        for y in range(int(top_y), int(bottom_y)):
            # Interpolate positions along the body
            t = (y - top_y) / (bottom_y - top_y)
            
            left_x = start_left[0] + t * (end_left[0] - start_left[0])
            right_x = start_right[0] + t * (end_right[0] - start_right[0])
            
            center_x = (left_x + right_x) / 2
            width = abs(right_x - left_x)
            
            if width > 0:
                # Apply horizontal compression
                slim_width = width * (1.0 - intensity * 0.3)  # Max 30% slimming
                compression_ratio = slim_width / width
                
                # Apply the transformation to this row
                for x in range(int(left_x), int(right_x)):
                    if 0 <= x < frame_width and 0 <= y < frame_height:
                        # Calculate new x position
                        offset_from_center = x - center_x
                        new_x = center_x + offset_from_center * compression_ratio
                        
                        if 0 <= new_x < frame_width:
                            # Bilinear interpolation
                            x_floor = int(new_x)
                            x_ceil = min(x_floor + 1, frame_width - 1)
                            wx = new_x - x_floor
                            
                            pixel = frame[y, x_floor] * (1 - wx) + frame[y, x_ceil] * wx
                            result[y, x] = pixel.astype(np.uint8)
        
        return result
    
    def apply_slimming_filter(self, frame: np.ndarray) -> np.ndarray:
        """Apply the slimming filter to a frame."""
        if not self.enabled or self.slimming_intensity <= 0:
            return frame
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process pose landmarks
            pose_results = self.pose.process(rgb_frame)
            
            if not pose_results.pose_landmarks:
                return frame
            
            # Get person segmentation mask
            segmentation_results = self.selfie_segmentation.process(rgb_frame)
            
            if segmentation_results.segmentation_mask is not None:
                # Create binary mask for person
                person_mask = (segmentation_results.segmentation_mask > 0.5).astype(np.uint8)
                person_mask = cv2.GaussianBlur(person_mask, (5, 5), 0)
            else:
                # Fallback: use full frame
                person_mask = np.ones((frame.shape[0], frame.shape[1]), dtype=np.uint8)
            
            # Apply directional slimming
            slimmed_frame = self.apply_directional_slimming(
                frame, 
                pose_results.pose_landmarks, 
                self.start_landmark, 
                self.end_landmark, 
                self.slimming_intensity
            )
            
            # Blend with original frame using person mask
            result = frame.copy()
            for c in range(3):  # For each color channel
                result[:, :, c] = (
                    slimmed_frame[:, :, c] * person_mask + 
                    frame[:, :, c] * (1 - person_mask)
                ).astype(np.uint8)
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying slimming filter: {e}")
            return frame
    
    def set_slimming_parameters(self, intensity: float, start_landmark: str = None, end_landmark: str = None, enabled: bool = None):
        """Set slimming parameters."""
        if intensity is not None:
            self.slimming_intensity = max(0.0, min(1.0, intensity))
        
        if start_landmark and start_landmark in self.landmark_indices:
            self.start_landmark = start_landmark
        
        if end_landmark and end_landmark in self.landmark_indices:
            self.end_landmark = end_landmark
        
        if enabled is not None:
            self.enabled = enabled
        
        logger.info(f"Slimming parameters updated: intensity={self.slimming_intensity}, "
                   f"landmarks={self.start_landmark} to {self.end_landmark}, enabled={self.enabled}")
    
    def set_slimming_region(self, region_name: str):
        """Set slimming region using predefined regions."""
        if region_name in self.slimming_regions:
            start, end = self.slimming_regions[region_name]
            self.start_landmark = start
            self.end_landmark = end
            logger.info(f"Slimming region set to: {region_name} ({start} to {end})")
            return True
        return False
    
    def get_available_landmarks(self) -> List[str]:
        """Get list of available landmarks for slimming."""
        return list(self.landmark_indices.keys())
    
    def get_available_regions(self) -> Dict[str, Tuple[str, str]]:
        """Get available predefined slimming regions."""
        return self.slimming_regions.copy()
    
    def get_current_parameters(self) -> Dict:
        """Get current slimming parameters."""
        return {
            'intensity': self.slimming_intensity,
            'start_landmark': self.start_landmark,
            'end_landmark': self.end_landmark,
            'enabled': self.enabled,
            'available_landmarks': self.get_available_landmarks(),
            'available_regions': self.get_available_regions()
        }