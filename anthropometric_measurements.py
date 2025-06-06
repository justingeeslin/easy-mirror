#!/usr/bin/env python3
"""
Anthropometric Measurements System for Easy Mirror
Calculates body measurements using MediaPipe pose landmarks, similar to ANSUR measurements.
"""

import cv2
import numpy as np
import mediapipe as mp
import math
import logging

logger = logging.getLogger(__name__)

class AnthropometricMeasurements:
    def __init__(self):
        """Initialize the anthropometric measurement system."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # MediaPipe pose landmark indices
        self.landmark_indices = {
            'nose': 0,
            'left_eye_inner': 1,
            'left_eye': 2,
            'left_eye_outer': 3,
            'right_eye_inner': 4,
            'right_eye': 5,
            'right_eye_outer': 6,
            'left_ear': 7,
            'right_ear': 8,
            'mouth_left': 9,
            'mouth_right': 10,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_pinky': 17,
            'right_pinky': 18,
            'left_index': 19,
            'right_index': 20,
            'left_thumb': 21,
            'right_thumb': 22,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
            'left_heel': 29,
            'right_heel': 30,
            'left_foot_index': 31,
            'right_foot_index': 32
        }
        
        # Calibration factor for converting pixel measurements to real-world units
        # This would need to be calibrated based on camera distance and known reference
        self.pixel_to_cm_ratio = 0.1  # Default: 1 pixel = 0.1 cm (needs calibration)
        
    def get_landmark_position(self, landmarks, landmark_name, frame_width, frame_height):
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
    
    def calculate_distance_2d(self, point1, point2):
        """Calculate 2D Euclidean distance between two points."""
        if point1 is None or point2 is None:
            return None
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calculate_distance_3d(self, point1, point2):
        """Calculate 3D Euclidean distance between two points."""
        if point1 is None or point2 is None:
            return None
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)
    
    def calculate_shoulder_breadth(self, landmarks, frame_width, frame_height):
        """Calculate shoulder breadth (biacromial breadth)."""
        left_shoulder = self.get_landmark_position(landmarks, 'left_shoulder', frame_width, frame_height)
        right_shoulder = self.get_landmark_position(landmarks, 'right_shoulder', frame_width, frame_height)
        
        distance_pixels = self.calculate_distance_2d(left_shoulder, right_shoulder)
        if distance_pixels:
            return distance_pixels * self.pixel_to_cm_ratio
        return None
    
    def calculate_standing_height(self, landmarks, frame_width, frame_height):
        """Calculate approximate standing height."""
        # Use head top (estimated from nose) to ankle
        nose = self.get_landmark_position(landmarks, 'nose', frame_width, frame_height)
        left_ankle = self.get_landmark_position(landmarks, 'left_ankle', frame_width, frame_height)
        right_ankle = self.get_landmark_position(landmarks, 'right_ankle', frame_width, frame_height)
        
        if nose and (left_ankle or right_ankle):
            # Use the lower ankle for more accurate measurement
            ankle = left_ankle if left_ankle and right_ankle and left_ankle[1] > right_ankle[1] else (right_ankle or left_ankle)
            
            # Estimate head top by adding head height (nose to top of head ~10cm)
            head_top_y = nose[1] - (10 / self.pixel_to_cm_ratio)
            height_pixels = ankle[1] - head_top_y
            
            if height_pixels > 0:
                return height_pixels * self.pixel_to_cm_ratio
        return None
    
    def calculate_arm_span(self, landmarks, frame_width, frame_height):
        """Calculate arm span (fingertip to fingertip)."""
        left_wrist = self.get_landmark_position(landmarks, 'left_wrist', frame_width, frame_height)
        right_wrist = self.get_landmark_position(landmarks, 'right_wrist', frame_width, frame_height)
        
        # Use wrists as approximation for fingertips (add ~18cm for hand length)
        if left_wrist and right_wrist:
            wrist_distance = self.calculate_distance_2d(left_wrist, right_wrist)
            if wrist_distance:
                # Add estimated hand lengths (18cm each)
                return (wrist_distance * self.pixel_to_cm_ratio) + 36
        return None
    
    def calculate_upper_arm_length(self, landmarks, frame_width, frame_height, side='left'):
        """Calculate upper arm length (shoulder to elbow)."""
        shoulder_key = f'{side}_shoulder'
        elbow_key = f'{side}_elbow'
        
        shoulder = self.get_landmark_position(landmarks, shoulder_key, frame_width, frame_height)
        elbow = self.get_landmark_position(landmarks, elbow_key, frame_width, frame_height)
        
        distance_pixels = self.calculate_distance_2d(shoulder, elbow)
        if distance_pixels:
            return distance_pixels * self.pixel_to_cm_ratio
        return None
    
    def calculate_forearm_length(self, landmarks, frame_width, frame_height, side='left'):
        """Calculate forearm length (elbow to wrist)."""
        elbow_key = f'{side}_elbow'
        wrist_key = f'{side}_wrist'
        
        elbow = self.get_landmark_position(landmarks, elbow_key, frame_width, frame_height)
        wrist = self.get_landmark_position(landmarks, wrist_key, frame_width, frame_height)
        
        distance_pixels = self.calculate_distance_2d(elbow, wrist)
        if distance_pixels:
            return distance_pixels * self.pixel_to_cm_ratio
        return None
    
    def calculate_thigh_length(self, landmarks, frame_width, frame_height, side='left'):
        """Calculate thigh length (hip to knee)."""
        hip_key = f'{side}_hip'
        knee_key = f'{side}_knee'
        
        hip = self.get_landmark_position(landmarks, hip_key, frame_width, frame_height)
        knee = self.get_landmark_position(landmarks, knee_key, frame_width, frame_height)
        
        distance_pixels = self.calculate_distance_2d(hip, knee)
        if distance_pixels:
            return distance_pixels * self.pixel_to_cm_ratio
        return None
    
    def calculate_lower_leg_length(self, landmarks, frame_width, frame_height, side='left'):
        """Calculate lower leg length (knee to ankle)."""
        knee_key = f'{side}_knee'
        ankle_key = f'{side}_ankle'
        
        knee = self.get_landmark_position(landmarks, knee_key, frame_width, frame_height)
        ankle = self.get_landmark_position(landmarks, ankle_key, frame_width, frame_height)
        
        distance_pixels = self.calculate_distance_2d(knee, ankle)
        if distance_pixels:
            return distance_pixels * self.pixel_to_cm_ratio
        return None
    
    def estimate_chest_circumference(self, landmarks, frame_width, frame_height):
        """Estimate chest circumference based on shoulder breadth."""
        shoulder_breadth = self.calculate_shoulder_breadth(landmarks, frame_width, frame_height)
        if shoulder_breadth:
            # Empirical relationship: chest circumference ≈ shoulder breadth × 2.4
            return shoulder_breadth * 2.4
        return None
    
    def estimate_waist_circumference(self, landmarks, frame_width, frame_height):
        """Estimate waist circumference based on hip width."""
        left_hip = self.get_landmark_position(landmarks, 'left_hip', frame_width, frame_height)
        right_hip = self.get_landmark_position(landmarks, 'right_hip', frame_width, frame_height)
        
        if left_hip and right_hip:
            hip_width = self.calculate_distance_2d(left_hip, right_hip)
            if hip_width:
                # Empirical relationship: waist circumference ≈ hip width × 2.8
                return (hip_width * self.pixel_to_cm_ratio) * 2.8
        return None
    
    def estimate_head_circumference(self, landmarks, frame_width, frame_height):
        """Estimate head circumference based on head width."""
        left_ear = self.get_landmark_position(landmarks, 'left_ear', frame_width, frame_height)
        right_ear = self.get_landmark_position(landmarks, 'right_ear', frame_width, frame_height)
        
        if left_ear and right_ear:
            head_width = self.calculate_distance_2d(left_ear, right_ear)
            if head_width:
                # Empirical relationship: head circumference ≈ head width × 3.14
                return (head_width * self.pixel_to_cm_ratio) * 3.14
        return None
    
    def calculate_all_measurements(self, frame):
        """Calculate all available anthropometric measurements from a frame."""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            measurements = {}
            
            if results.pose_landmarks:
                frame_height, frame_width = frame.shape[:2]
                landmarks = results.pose_landmarks
                
                # Linear measurements
                measurements['shoulder_breadth'] = self.calculate_shoulder_breadth(landmarks, frame_width, frame_height)
                measurements['standing_height'] = self.calculate_standing_height(landmarks, frame_width, frame_height)
                measurements['arm_span'] = self.calculate_arm_span(landmarks, frame_width, frame_height)
                
                # Bilateral measurements (left and right)
                measurements['left_upper_arm_length'] = self.calculate_upper_arm_length(landmarks, frame_width, frame_height, 'left')
                measurements['right_upper_arm_length'] = self.calculate_upper_arm_length(landmarks, frame_width, frame_height, 'right')
                measurements['left_forearm_length'] = self.calculate_forearm_length(landmarks, frame_width, frame_height, 'left')
                measurements['right_forearm_length'] = self.calculate_forearm_length(landmarks, frame_width, frame_height, 'right')
                measurements['left_thigh_length'] = self.calculate_thigh_length(landmarks, frame_width, frame_height, 'left')
                measurements['right_thigh_length'] = self.calculate_thigh_length(landmarks, frame_width, frame_height, 'right')
                measurements['left_lower_leg_length'] = self.calculate_lower_leg_length(landmarks, frame_width, frame_height, 'left')
                measurements['right_lower_leg_length'] = self.calculate_lower_leg_length(landmarks, frame_width, frame_height, 'right')
                
                # Circumference estimates
                measurements['chest_circumference'] = self.estimate_chest_circumference(landmarks, frame_width, frame_height)
                measurements['waist_circumference'] = self.estimate_waist_circumference(landmarks, frame_width, frame_height)
                measurements['head_circumference'] = self.estimate_head_circumference(landmarks, frame_width, frame_height)
                
                # Filter out None values and round to 1 decimal place
                measurements = {k: round(v, 1) for k, v in measurements.items() if v is not None}
                
                # Add metadata
                measurements['timestamp'] = time.time()
                measurements['pose_detected'] = True
                measurements['calibration_note'] = f"Measurements use pixel-to-cm ratio of {self.pixel_to_cm_ratio}. Calibration recommended for accuracy."
                
            else:
                measurements = {
                    'pose_detected': False,
                    'error': 'No pose detected in frame'
                }
            
            return measurements
            
        except Exception as e:
            logger.error(f"Error calculating anthropometric measurements: {e}")
            return {
                'pose_detected': False,
                'error': str(e)
            }
    
    def set_calibration(self, pixel_to_cm_ratio):
        """Set the pixel-to-cm calibration ratio."""
        if pixel_to_cm_ratio > 0:
            self.pixel_to_cm_ratio = pixel_to_cm_ratio
            logger.info(f"Calibration set to {pixel_to_cm_ratio} cm per pixel")
            return True
        return False
    
    def get_measurement_descriptions(self):
        """Get descriptions of all available measurements."""
        return {
            'shoulder_breadth': 'Distance between left and right shoulder landmarks (biacromial breadth)',
            'standing_height': 'Estimated height from head top to ankle',
            'arm_span': 'Distance from left fingertip to right fingertip (estimated)',
            'left_upper_arm_length': 'Distance from left shoulder to left elbow',
            'right_upper_arm_length': 'Distance from right shoulder to right elbow',
            'left_forearm_length': 'Distance from left elbow to left wrist',
            'right_forearm_length': 'Distance from right elbow to right wrist',
            'left_thigh_length': 'Distance from left hip to left knee',
            'right_thigh_length': 'Distance from right hip to right knee',
            'left_lower_leg_length': 'Distance from left knee to left ankle',
            'right_lower_leg_length': 'Distance from right knee to right ankle',
            'chest_circumference': 'Estimated chest circumference based on shoulder breadth',
            'waist_circumference': 'Estimated waist circumference based on hip width',
            'head_circumference': 'Estimated head circumference based on head width'
        }

# Import time for timestamps
import time