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
        self.pixel_to_cm_ratio = 0.33  # Default: 1 pixel = 0.1 cm (needs calibration)
        
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
    
    def generate_ui_html(self):
        """Generate HTML for anthropometric measurements UI controls."""
        return '''
        <div class="module-section" id="anthropometric-section">
            <h3>📏 Anthropometric Measurements</h3>
            <div class="measurements-controls">
                <button id="get-measurements-btn" class="action-btn">
                    <span class="btn-icon">📐</span>
                    Get Measurements
                </button>
                <button id="calibrate-btn" class="action-btn secondary">
                    <span class="btn-icon">⚙️</span>
                    Calibrate
                </button>
                <button id="show-descriptions-btn" class="action-btn secondary">
                    <span class="btn-icon">ℹ️</span>
                    Info
                </button>
            </div>
            
            <div id="calibration-panel" class="panel hidden">
                <h4>Calibration</h4>
                <p>Enter the pixel-to-cm ratio for accurate measurements:</p>
                <div class="input-group">
                    <input type="number" id="calibration-ratio" placeholder="0.1" step="0.01" min="0.01">
                    <label>pixels per cm</label>
                </div>
                <div class="panel-actions">
                    <button id="apply-calibration-btn" class="action-btn">Apply</button>
                    <button id="cancel-calibration-btn" class="action-btn secondary">Cancel</button>
                </div>
            </div>
            
            <div id="measurements-results" class="results-panel hidden">
                <h4>Measurement Results</h4>
                <div id="measurements-data"></div>
            </div>
            
            <div id="measurements-descriptions" class="descriptions-panel hidden">
                <h4>Measurement Descriptions</h4>
                <div id="descriptions-data"></div>
            </div>
        </div>
        '''
    
    def generate_ui_css(self):
        """Generate CSS for anthropometric measurements UI."""
        return '''
        .measurements-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .action-btn {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 8px 16px;
            border: 2px solid #28a745;
            border-radius: 6px;
            background: #28a745;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .action-btn:hover {
            background: #218838;
            transform: translateY(-1px);
        }
        
        .action-btn.secondary {
            background: white;
            color: #6c757d;
            border-color: #6c757d;
        }
        
        .action-btn.secondary:hover {
            background: #6c757d;
            color: white;
        }
        
        .panel {
            margin-top: 15px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .panel.hidden {
            display: none;
        }
        
        .input-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
        }
        
        .input-group input {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 120px;
        }
        
        .panel-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .results-panel {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .measurement-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        
        .measurement-item:last-child {
            border-bottom: none;
        }
        
        .measurement-name {
            font-weight: 500;
        }
        
        .measurement-value {
            color: #007bff;
            font-family: monospace;
        }
        
        .descriptions-panel {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .description-item {
            margin-bottom: 10px;
            padding: 8px;
            background: white;
            border-radius: 4px;
        }
        
        .description-title {
            font-weight: bold;
            color: #495057;
        }
        
        .description-text {
            font-size: 13px;
            color: #6c757d;
            margin-top: 3px;
        }
        '''
    
    def generate_ui_javascript(self):
        """Generate JavaScript for anthropometric measurements UI."""
        return '''
        // Anthropometric Measurements Module JavaScript
        function initAnthropometricModule() {
            const getMeasurementsBtn = document.getElementById('get-measurements-btn');
            const calibrateBtn = document.getElementById('calibrate-btn');
            const showDescriptionsBtn = document.getElementById('show-descriptions-btn');
            const calibrationPanel = document.getElementById('calibration-panel');
            const resultsPanel = document.getElementById('measurements-results');
            const descriptionsPanel = document.getElementById('measurements-descriptions');
            
            // Get measurements
            if (getMeasurementsBtn) {
                getMeasurementsBtn.addEventListener('click', async function() {
                    this.disabled = true;
                    this.innerHTML = '<span class="btn-icon">⏳</span> Getting...';
                    
                    try {
                        const response = await fetch('/api/measurements');
                        const data = await response.json();
                        
                        if (response.ok) {
                            displayMeasurements(data);
                            resultsPanel.classList.remove('hidden');
                        } else {
                            alert('Error: ' + data.error);
                        }
                    } catch (error) {
                        alert('Error getting measurements: ' + error.message);
                    } finally {
                        this.disabled = false;
                        this.innerHTML = '<span class="btn-icon">📐</span> Get Measurements';
                    }
                });
            }
            
            // Calibration
            if (calibrateBtn) {
                calibrateBtn.addEventListener('click', function() {
                    calibrationPanel.classList.toggle('hidden');
                    descriptionsPanel.classList.add('hidden');
                });
            }
            
            // Apply calibration
            const applyCalibrateBtn = document.getElementById('apply-calibration-btn');
            if (applyCalibrateBtn) {
                applyCalibrateBtn.addEventListener('click', async function() {
                    const ratio = document.getElementById('calibration-ratio').value;
                    if (!ratio || ratio <= 0) {
                        alert('Please enter a valid calibration ratio');
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/measurements/calibrate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({pixel_to_cm_ratio: parseFloat(ratio)})
                        });
                        
                        const data = await response.json();
                        if (response.ok) {
                            alert('Calibration applied successfully!');
                            calibrationPanel.classList.add('hidden');
                        } else {
                            alert('Error: ' + data.error);
                        }
                    } catch (error) {
                        alert('Error applying calibration: ' + error.message);
                    }
                });
            }
            
            // Cancel calibration
            const cancelCalibrateBtn = document.getElementById('cancel-calibration-btn');
            if (cancelCalibrateBtn) {
                cancelCalibrateBtn.addEventListener('click', function() {
                    calibrationPanel.classList.add('hidden');
                });
            }
            
            // Show descriptions
            if (showDescriptionsBtn) {
                showDescriptionsBtn.addEventListener('click', async function() {
                    if (descriptionsPanel.classList.contains('hidden')) {
                        try {
                            const response = await fetch('/api/measurements/descriptions');
                            const data = await response.json();
                            
                            if (response.ok) {
                                displayDescriptions(data);
                                descriptionsPanel.classList.remove('hidden');
                                calibrationPanel.classList.add('hidden');
                            } else {
                                alert('Error: ' + data.error);
                            }
                        } catch (error) {
                            alert('Error getting descriptions: ' + error.message);
                        }
                    } else {
                        descriptionsPanel.classList.add('hidden');
                    }
                });
            }
        }
        
        function displayMeasurements(data) {
            const container = document.getElementById('measurements-data');
            if (!container) return;
            
            let html = '';
            
            if (data.pose_detected) {
                // Display measurements
                Object.entries(data).forEach(([key, value]) => {
                    if (key !== 'pose_detected' && key !== 'timestamp') {
                        const displayName = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        const displayValue = typeof value === 'number' ? value.toFixed(2) + ' cm' : value;
                        
                        html += `
                            <div class="measurement-item">
                                <span class="measurement-name">${displayName}</span>
                                <span class="measurement-value">${displayValue}</span>
                            </div>
                        `;
                    }
                });
            } else {
                html = '<p style="color: #dc3545;">No pose detected in current frame. Please ensure you are visible in the camera.</p>';
            }
            
            container.innerHTML = html;
        }
        
        function displayDescriptions(data) {
            const container = document.getElementById('descriptions-data');
            if (!container) return;
            
            let html = '';
            Object.entries(data).forEach(([key, description]) => {
                const displayName = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                html += `
                    <div class="description-item">
                        <div class="description-title">${displayName}</div>
                        <div class="description-text">${description}</div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAnthropometricModule);
        } else {
            initAnthropometricModule();
        }
        '''

# Import time for timestamps
import time
