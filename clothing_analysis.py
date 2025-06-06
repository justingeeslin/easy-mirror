#!/usr/bin/env python3
"""
Clothing Analysis System for Easy Mirror
Uses MediaPipe Image Segmentation to detect and analyze real clothing.
"""

import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import logging
from collections import Counter
import colorsys

logger = logging.getLogger(__name__)

class ClothingAnalyzer:
    def __init__(self):
        """Initialize the clothing analysis system."""
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        
        # Initialize pose detection for body part identification
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Color definitions for clothing color detection
        self.color_ranges = {
            'red': [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
            'orange': [(10, 50, 50), (25, 255, 255)],
            'yellow': [(25, 50, 50), (35, 255, 255)],
            'green': [(35, 50, 50), (85, 255, 255)],
            'blue': [(85, 50, 50), (125, 255, 255)],
            'purple': [(125, 50, 50), (155, 255, 255)],
            'pink': [(155, 50, 50), (170, 255, 255)],
            'white': [(0, 0, 200), (180, 30, 255)],
            'black': [(0, 0, 0), (180, 255, 50)],
            'gray': [(0, 0, 50), (180, 30, 200)],
            'brown': [(8, 50, 20), (20, 255, 200)]
        }
        
        # Garment type patterns based on coverage areas
        self.garment_patterns = {
            'shirt': {'torso_coverage': (0.3, 0.8), 'arm_coverage': (0.1, 0.7)},
            'tank_top': {'torso_coverage': (0.3, 0.8), 'arm_coverage': (0.0, 0.2)},
            'long_sleeve': {'torso_coverage': (0.3, 0.8), 'arm_coverage': (0.6, 1.0)},
            'dress': {'torso_coverage': (0.5, 1.0), 'leg_coverage': (0.3, 1.0)},
            'blouse': {'torso_coverage': (0.3, 0.7), 'arm_coverage': (0.2, 0.8)},
            'jacket': {'torso_coverage': (0.4, 0.9), 'arm_coverage': (0.5, 1.0)},
            'pants': {'leg_coverage': (0.5, 1.0), 'torso_coverage': (0.0, 0.3)},
            'shorts': {'leg_coverage': (0.1, 0.5), 'torso_coverage': (0.0, 0.3)},
            'skirt': {'leg_coverage': (0.2, 0.7), 'torso_coverage': (0.0, 0.3)}
        }
        
        # Texture/material patterns (simplified)
        self.material_indicators = {
            'denim': {'texture_variance': 'high', 'color_consistency': 'medium'},
            'cotton': {'texture_variance': 'low', 'color_consistency': 'high'},
            'silk': {'texture_variance': 'very_low', 'color_consistency': 'high'},
            'wool': {'texture_variance': 'medium', 'color_consistency': 'medium'},
            'leather': {'texture_variance': 'medium', 'color_consistency': 'low'},
            'polyester': {'texture_variance': 'low', 'color_consistency': 'high'}
        }
        
        self.last_analysis = None
    
    def segment_person(self, frame):
        """Segment the person from the background using MediaPipe."""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.segmentation.process(rgb_frame)
            
            if results.segmentation_mask is not None:
                # Create binary mask
                mask = results.segmentation_mask > 0.5
                return mask.astype(np.uint8)
            return None
        except Exception as e:
            logger.error(f"Error in person segmentation: {e}")
            return None
    
    def get_body_regions(self, frame, pose_landmarks):
        """Define body regions based on pose landmarks."""
        if not pose_landmarks:
            return {}
        
        height, width = frame.shape[:2]
        regions = {}
        
        # Get landmark positions
        landmarks = {}
        for idx, landmark in enumerate(pose_landmarks.landmark):
            if landmark.visibility > 0.5:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmarks[idx] = (x, y)
        
        # Define regions based on landmarks
        if 11 in landmarks and 12 in landmarks:  # shoulders
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            
            # Torso region
            if 23 in landmarks and 24 in landmarks:  # hips
                left_hip = landmarks[23]
                right_hip = landmarks[24]
                
                torso_top = min(left_shoulder[1], right_shoulder[1])
                torso_bottom = max(left_hip[1], right_hip[1])
                torso_left = min(left_shoulder[0], left_hip[0]) - 20
                torso_right = max(right_shoulder[0], right_hip[0]) + 20
                
                regions['torso'] = {
                    'bbox': (max(0, torso_left), max(0, torso_top), 
                            min(width, torso_right), min(height, torso_bottom))
                }
        
        # Arm regions
        if 11 in landmarks and 15 in landmarks:  # left shoulder to wrist
            left_arm_top = landmarks[11][1]
            left_arm_bottom = landmarks[15][1] if 15 in landmarks else landmarks[11][1] + 100
            left_arm_left = landmarks[15][0] if 15 in landmarks else landmarks[11][0] - 50
            left_arm_right = landmarks[11][0]
            
            regions['left_arm'] = {
                'bbox': (max(0, left_arm_left), max(0, left_arm_top),
                        min(width, left_arm_right), min(height, left_arm_bottom))
            }
        
        if 12 in landmarks and 16 in landmarks:  # right shoulder to wrist
            right_arm_top = landmarks[12][1]
            right_arm_bottom = landmarks[16][1] if 16 in landmarks else landmarks[12][1] + 100
            right_arm_left = landmarks[12][0]
            right_arm_right = landmarks[16][0] if 16 in landmarks else landmarks[12][0] + 50
            
            regions['right_arm'] = {
                'bbox': (max(0, right_arm_left), max(0, right_arm_top),
                        min(width, right_arm_right), min(height, right_arm_bottom))
            }
        
        # Leg regions
        if 23 in landmarks and 24 in landmarks:  # hips
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            # Estimate leg regions
            leg_top = max(left_hip[1], right_hip[1])
            leg_bottom = height
            
            regions['left_leg'] = {
                'bbox': (max(0, left_hip[0] - 30), leg_top,
                        min(width, left_hip[0] + 30), leg_bottom)
            }
            
            regions['right_leg'] = {
                'bbox': (max(0, right_hip[0] - 30), leg_top,
                        min(width, right_hip[0] + 30), leg_bottom)
            }
        
        return regions
    
    def analyze_color(self, image_region):
        """Analyze the dominant color in an image region."""
        if image_region.size == 0:
            return 'unknown'
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image_region, cv2.COLOR_BGR2HSV)
        
        # Find dominant color
        color_counts = {}
        for color_name, ranges in self.color_ranges.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            if len(ranges) == 4:  # Red has two ranges
                mask1 = cv2.inRange(hsv, ranges[0], ranges[1])
                mask2 = cv2.inRange(hsv, ranges[2], ranges[3])
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                mask = cv2.inRange(hsv, ranges[0], ranges[1])
            
            color_counts[color_name] = cv2.countNonZero(mask)
        
        # Return the color with the highest count
        dominant_color = max(color_counts, key=color_counts.get)
        if color_counts[dominant_color] > hsv.shape[0] * hsv.shape[1] * 0.1:  # At least 10% coverage
            return dominant_color
        return 'unknown'
    
    def analyze_texture(self, image_region):
        """Analyze texture to estimate material type."""
        if image_region.size == 0:
            return 'unknown'
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture variance using Laplacian
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate color consistency
        color_std = np.std(image_region)
        
        # Simple material classification based on texture properties
        if laplacian_var > 500:
            texture_variance = 'high'
        elif laplacian_var > 200:
            texture_variance = 'medium'
        elif laplacian_var > 50:
            texture_variance = 'low'
        else:
            texture_variance = 'very_low'
        
        if color_std > 40:
            color_consistency = 'low'
        elif color_std > 20:
            color_consistency = 'medium'
        else:
            color_consistency = 'high'
        
        # Match against material patterns
        for material, indicators in self.material_indicators.items():
            if (indicators['texture_variance'] == texture_variance and 
                indicators['color_consistency'] == color_consistency):
                return material
        
        return 'cotton'  # Default fallback
    
    def classify_garment(self, regions, person_mask, frame):
        """Classify the type of garment based on coverage patterns."""
        height, width = frame.shape[:2]
        total_person_pixels = np.sum(person_mask)
        
        if total_person_pixels == 0:
            return 'unknown'
        
        # Calculate coverage for each region
        coverage = {}
        for region_name, region_info in regions.items():
            bbox = region_info['bbox']
            x1, y1, x2, y2 = bbox
            
            region_mask = person_mask[y1:y2, x1:x2]
            region_pixels = np.sum(region_mask)
            region_total = (x2 - x1) * (y2 - y1)
            
            if region_total > 0:
                coverage[region_name] = region_pixels / region_total
            else:
                coverage[region_name] = 0
        
        # Classify based on coverage patterns
        torso_coverage = coverage.get('torso', 0)
        arm_coverage = (coverage.get('left_arm', 0) + coverage.get('right_arm', 0)) / 2
        leg_coverage = (coverage.get('left_leg', 0) + coverage.get('right_leg', 0)) / 2
        
        best_match = 'unknown'
        best_score = 0
        
        for garment_type, pattern in self.garment_patterns.items():
            score = 0
            matches = 0
            
            if 'torso_coverage' in pattern:
                min_torso, max_torso = pattern['torso_coverage']
                if min_torso <= torso_coverage <= max_torso:
                    score += 1
                matches += 1
            
            if 'arm_coverage' in pattern:
                min_arm, max_arm = pattern['arm_coverage']
                if min_arm <= arm_coverage <= max_arm:
                    score += 1
                matches += 1
            
            if 'leg_coverage' in pattern:
                min_leg, max_leg = pattern['leg_coverage']
                if min_leg <= leg_coverage <= max_leg:
                    score += 1
                matches += 1
            
            if matches > 0:
                normalized_score = score / matches
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_match = garment_type
        
        return best_match if best_score > 0.5 else 'unknown'
    
    def detect_garment_features(self, regions, frame, garment_type):
        """Detect specific garment features like neckline, sleeve length, etc."""
        features = {}
        
        if 'torso' in regions:
            torso_bbox = regions['torso']['bbox']
            x1, y1, x2, y2 = torso_bbox
            torso_region = frame[y1:y2, x1:x2]
            
            # Analyze neckline (simplified)
            if garment_type in ['shirt', 'blouse', 'dress']:
                neckline_region = torso_region[:int(torso_region.shape[0] * 0.3), :]
                if neckline_region.size > 0:
                    # Simple neckline detection based on coverage pattern
                    gray_neck = cv2.cvtColor(neckline_region, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray_neck, 50, 150)
                    edge_density = np.sum(edges > 0) / edges.size
                    
                    if edge_density > 0.1:
                        features['neckline'] = 'v-neck'
                    elif edge_density > 0.05:
                        features['neckline'] = 'scoop'
                    else:
                        features['neckline'] = 'crew'
        
        # Analyze sleeve length
        if 'left_arm' in regions and 'right_arm' in regions:
            left_arm_bbox = regions['left_arm']['bbox']
            right_arm_bbox = regions['right_arm']['bbox']
            
            left_arm_length = left_arm_bbox[3] - left_arm_bbox[1]
            right_arm_length = right_arm_bbox[3] - right_arm_bbox[1]
            avg_arm_length = (left_arm_length + right_arm_length) / 2
            
            if avg_arm_length > 150:
                features['sleeve_length'] = 'long'
            elif avg_arm_length > 80:
                features['sleeve_length'] = 'short'
            else:
                features['sleeve_length'] = 'sleeveless'
        
        return features
    
    def detect_embellishments(self, regions, frame):
        """Detect embellishments like buttons, zippers, etc."""
        embellishments = []
        
        if 'torso' in regions:
            torso_bbox = regions['torso']['bbox']
            x1, y1, x2, y2 = torso_bbox
            torso_region = frame[y1:y2, x1:x2]
            
            if torso_region.size > 0:
                # Convert to grayscale for feature detection
                gray = cv2.cvtColor(torso_region, cv2.COLOR_BGR2GRAY)
                
                # Detect circular features (buttons)
                circles = cv2.HoughCircles(
                    gray, cv2.HOUGH_GRADIENT, 1, 20,
                    param1=50, param2=30, minRadius=3, maxRadius=15
                )
                
                if circles is not None and len(circles[0]) > 2:
                    embellishments.append('buttons')
                
                # Detect linear features (zippers)
                edges = cv2.Canny(gray, 50, 150)
                lines = cv2.HoughLinesP(
                    edges, 1, np.pi/180, threshold=50,
                    minLineLength=30, maxLineGap=10
                )
                
                if lines is not None:
                    # Look for vertical lines (potential zippers)
                    vertical_lines = 0
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                        if 80 <= angle <= 100:  # Nearly vertical
                            vertical_lines += 1
                    
                    if vertical_lines > 0:
                        embellishments.append('zipper')
        
        return embellishments
    
    def analyze_clothing(self, frame):
        """Perform comprehensive clothing analysis on a frame."""
        try:
            # Get person segmentation mask
            person_mask = self.segment_person(frame)
            if person_mask is None:
                return None
            
            # Get pose landmarks for body region detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pose_results = self.pose.process(rgb_frame)
            
            if not pose_results.pose_landmarks:
                return None
            
            # Get body regions
            regions = self.get_body_regions(frame, pose_results.pose_landmarks)
            if not regions:
                return None
            
            # Classify garment type
            garment_type = self.classify_garment(regions, person_mask, frame)
            
            # Analyze colors for each region
            colors = {}
            materials = {}
            for region_name, region_info in regions.items():
                bbox = region_info['bbox']
                x1, y1, x2, y2 = bbox
                region_frame = frame[y1:y2, x1:x2]
                region_mask = person_mask[y1:y2, x1:x2]
                
                # Apply mask to region
                if region_frame.size > 0 and region_mask.size > 0:
                    masked_region = cv2.bitwise_and(region_frame, region_frame, mask=region_mask)
                    if np.sum(region_mask) > 0:  # Only analyze if there's actual person pixels
                        colors[region_name] = self.analyze_color(masked_region)
                        materials[region_name] = self.analyze_texture(masked_region)
            
            # Detect garment features
            features = self.detect_garment_features(regions, frame, garment_type)
            
            # Detect embellishments
            embellishments = self.detect_embellishments(regions, frame)
            
            # Compile analysis results
            analysis = {
                'garment_type': garment_type,
                'colors': colors,
                'materials': materials,
                'features': features,
                'embellishments': embellishments,
                'confidence': 0.8 if garment_type != 'unknown' else 0.3
            }
            
            self.last_analysis = analysis
            return analysis
            
        except Exception as e:
            logger.error(f"Error in clothing analysis: {e}")
            return None
    
    def get_last_analysis(self):
        """Get the last clothing analysis result."""
        return self.last_analysis