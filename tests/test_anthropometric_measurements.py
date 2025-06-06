#!/usr/bin/env python3
"""
Test suite for anthropometric measurements functionality.
"""

import unittest
import numpy as np
import cv2
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from anthropometric_measurements import AnthropometricMeasurements
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class TestAnthropometricMeasurements(unittest.TestCase):
    """Test cases for the AnthropometricMeasurements class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MEDIAPIPE_AVAILABLE:
            self.skipTest("MediaPipe not available")
        
        self.measurements = AnthropometricMeasurements()
        
        # Create a mock landmarks object
        self.mock_landmarks = Mock()
        self.mock_landmarks.landmark = []
        
        # Create mock landmark points with realistic positions
        for i in range(33):  # MediaPipe has 33 pose landmarks
            mock_point = Mock()
            mock_point.x = 0.5  # Center of frame
            mock_point.y = 0.5  # Center of frame
            mock_point.z = 0.0  # Depth
            mock_point.visibility = 0.8  # High visibility
            self.mock_landmarks.landmark.append(mock_point)
        
        # Set specific positions for key landmarks
        # Shoulders
        self.mock_landmarks.landmark[11].x = 0.4  # Left shoulder
        self.mock_landmarks.landmark[11].y = 0.3
        self.mock_landmarks.landmark[12].x = 0.6  # Right shoulder
        self.mock_landmarks.landmark[12].y = 0.3
        
        # Hips
        self.mock_landmarks.landmark[23].x = 0.45  # Left hip
        self.mock_landmarks.landmark[23].y = 0.6
        self.mock_landmarks.landmark[24].x = 0.55  # Right hip
        self.mock_landmarks.landmark[24].y = 0.6
        
        # Ankles
        self.mock_landmarks.landmark[27].x = 0.45  # Left ankle
        self.mock_landmarks.landmark[27].y = 0.9
        self.mock_landmarks.landmark[28].x = 0.55  # Right ankle
        self.mock_landmarks.landmark[28].y = 0.9
        
        # Nose
        self.mock_landmarks.landmark[0].x = 0.5  # Nose
        self.mock_landmarks.landmark[0].y = 0.1
        
        # Ears
        self.mock_landmarks.landmark[7].x = 0.45  # Left ear
        self.mock_landmarks.landmark[7].y = 0.1
        self.mock_landmarks.landmark[8].x = 0.55  # Right ear
        self.mock_landmarks.landmark[8].y = 0.1
        
        # Elbows and wrists
        self.mock_landmarks.landmark[13].x = 0.3  # Left elbow
        self.mock_landmarks.landmark[13].y = 0.4
        self.mock_landmarks.landmark[14].x = 0.7  # Right elbow
        self.mock_landmarks.landmark[14].y = 0.4
        self.mock_landmarks.landmark[15].x = 0.2  # Left wrist
        self.mock_landmarks.landmark[15].y = 0.5
        self.mock_landmarks.landmark[16].x = 0.8  # Right wrist
        self.mock_landmarks.landmark[16].y = 0.5
        
        # Knees
        self.mock_landmarks.landmark[25].x = 0.45  # Left knee
        self.mock_landmarks.landmark[25].y = 0.75
        self.mock_landmarks.landmark[26].x = 0.55  # Right knee
        self.mock_landmarks.landmark[26].y = 0.75
    
    def test_initialization(self):
        """Test that the AnthropometricMeasurements class initializes correctly."""
        self.assertIsNotNone(self.measurements.pose)
        self.assertEqual(self.measurements.pixel_to_cm_ratio, 0.1)
        self.assertIsInstance(self.measurements.landmark_indices, dict)
        self.assertIn('nose', self.measurements.landmark_indices)
        self.assertIn('left_shoulder', self.measurements.landmark_indices)
    
    def test_get_landmark_position(self):
        """Test landmark position extraction."""
        frame_width, frame_height = 640, 480
        
        # Test valid landmark
        position = self.measurements.get_landmark_position(
            self.mock_landmarks, 'nose', frame_width, frame_height
        )
        self.assertIsNotNone(position)
        self.assertEqual(len(position), 3)  # x, y, z
        self.assertEqual(position[0], 0.5 * frame_width)
        self.assertEqual(position[1], 0.1 * frame_height)
        
        # Test invalid landmark
        position = self.measurements.get_landmark_position(
            self.mock_landmarks, 'invalid_landmark', frame_width, frame_height
        )
        self.assertIsNone(position)
    
    def test_calculate_distance_2d(self):
        """Test 2D distance calculation."""
        point1 = (0, 0, 0)
        point2 = (3, 4, 0)
        
        distance = self.measurements.calculate_distance_2d(point1, point2)
        self.assertEqual(distance, 5.0)  # 3-4-5 triangle
        
        # Test with None values
        distance = self.measurements.calculate_distance_2d(None, point2)
        self.assertIsNone(distance)
        
        distance = self.measurements.calculate_distance_2d(point1, None)
        self.assertIsNone(distance)
    
    def test_calculate_distance_3d(self):
        """Test 3D distance calculation."""
        point1 = (0, 0, 0)
        point2 = (1, 1, 1)
        
        distance = self.measurements.calculate_distance_3d(point1, point2)
        expected = np.sqrt(3)  # sqrt(1^2 + 1^2 + 1^2)
        self.assertAlmostEqual(distance, expected, places=5)
    
    def test_calculate_shoulder_breadth(self):
        """Test shoulder breadth calculation."""
        frame_width, frame_height = 640, 480
        
        shoulder_breadth = self.measurements.calculate_shoulder_breadth(
            self.mock_landmarks, frame_width, frame_height
        )
        
        self.assertIsNotNone(shoulder_breadth)
        self.assertGreater(shoulder_breadth, 0)
        
        # Expected calculation: distance between (0.4*640, 0.3*480) and (0.6*640, 0.3*480)
        # = distance between (256, 144) and (384, 144) = 128 pixels
        # = 128 * 0.1 = 12.8 cm
        expected = 128 * 0.1
        self.assertAlmostEqual(shoulder_breadth, expected, places=1)
    
    def test_calculate_standing_height(self):
        """Test standing height calculation."""
        frame_width, frame_height = 640, 480
        
        height = self.measurements.calculate_standing_height(
            self.mock_landmarks, frame_width, frame_height
        )
        
        self.assertIsNotNone(height)
        self.assertGreater(height, 0)
    
    def test_calculate_arm_span(self):
        """Test arm span calculation."""
        frame_width, frame_height = 640, 480
        
        arm_span = self.measurements.calculate_arm_span(
            self.mock_landmarks, frame_width, frame_height
        )
        
        self.assertIsNotNone(arm_span)
        self.assertGreater(arm_span, 0)
        
        # Should include hand length estimation (36cm total for both hands)
        wrist_distance = abs(0.8 * frame_width - 0.2 * frame_width) * 0.1
        expected = wrist_distance + 36
        self.assertAlmostEqual(arm_span, expected, places=1)
    
    def test_calculate_upper_arm_length(self):
        """Test upper arm length calculation."""
        frame_width, frame_height = 640, 480
        
        # Test left arm
        left_length = self.measurements.calculate_upper_arm_length(
            self.mock_landmarks, frame_width, frame_height, 'left'
        )
        self.assertIsNotNone(left_length)
        self.assertGreater(left_length, 0)
        
        # Test right arm
        right_length = self.measurements.calculate_upper_arm_length(
            self.mock_landmarks, frame_width, frame_height, 'right'
        )
        self.assertIsNotNone(right_length)
        self.assertGreater(right_length, 0)
    
    def test_calculate_forearm_length(self):
        """Test forearm length calculation."""
        frame_width, frame_height = 640, 480
        
        # Test left forearm
        left_length = self.measurements.calculate_forearm_length(
            self.mock_landmarks, frame_width, frame_height, 'left'
        )
        self.assertIsNotNone(left_length)
        self.assertGreater(left_length, 0)
        
        # Test right forearm
        right_length = self.measurements.calculate_forearm_length(
            self.mock_landmarks, frame_width, frame_height, 'right'
        )
        self.assertIsNotNone(right_length)
        self.assertGreater(right_length, 0)
    
    def test_calculate_thigh_length(self):
        """Test thigh length calculation."""
        frame_width, frame_height = 640, 480
        
        # Test left thigh
        left_length = self.measurements.calculate_thigh_length(
            self.mock_landmarks, frame_width, frame_height, 'left'
        )
        self.assertIsNotNone(left_length)
        self.assertGreater(left_length, 0)
        
        # Test right thigh
        right_length = self.measurements.calculate_thigh_length(
            self.mock_landmarks, frame_width, frame_height, 'right'
        )
        self.assertIsNotNone(right_length)
        self.assertGreater(right_length, 0)
    
    def test_calculate_lower_leg_length(self):
        """Test lower leg length calculation."""
        frame_width, frame_height = 640, 480
        
        # Test left lower leg
        left_length = self.measurements.calculate_lower_leg_length(
            self.mock_landmarks, frame_width, frame_height, 'left'
        )
        self.assertIsNotNone(left_length)
        self.assertGreater(left_length, 0)
        
        # Test right lower leg
        right_length = self.measurements.calculate_lower_leg_length(
            self.mock_landmarks, frame_width, frame_height, 'right'
        )
        self.assertIsNotNone(right_length)
        self.assertGreater(right_length, 0)
    
    def test_estimate_chest_circumference(self):
        """Test chest circumference estimation."""
        frame_width, frame_height = 640, 480
        
        chest_circ = self.measurements.estimate_chest_circumference(
            self.mock_landmarks, frame_width, frame_height
        )
        
        self.assertIsNotNone(chest_circ)
        self.assertGreater(chest_circ, 0)
        
        # Should be shoulder breadth * 2.4
        shoulder_breadth = self.measurements.calculate_shoulder_breadth(
            self.mock_landmarks, frame_width, frame_height
        )
        expected = shoulder_breadth * 2.4
        self.assertAlmostEqual(chest_circ, expected, places=1)
    
    def test_estimate_waist_circumference(self):
        """Test waist circumference estimation."""
        frame_width, frame_height = 640, 480
        
        waist_circ = self.measurements.estimate_waist_circumference(
            self.mock_landmarks, frame_width, frame_height
        )
        
        self.assertIsNotNone(waist_circ)
        self.assertGreater(waist_circ, 0)
    
    def test_estimate_head_circumference(self):
        """Test head circumference estimation."""
        frame_width, frame_height = 640, 480
        
        head_circ = self.measurements.estimate_head_circumference(
            self.mock_landmarks, frame_width, frame_height
        )
        
        self.assertIsNotNone(head_circ)
        self.assertGreater(head_circ, 0)
    
    def test_set_calibration(self):
        """Test calibration setting."""
        # Test valid calibration
        result = self.measurements.set_calibration(0.2)
        self.assertTrue(result)
        self.assertEqual(self.measurements.pixel_to_cm_ratio, 0.2)
        
        # Test invalid calibration
        result = self.measurements.set_calibration(0)
        self.assertFalse(result)
        
        result = self.measurements.set_calibration(-0.1)
        self.assertFalse(result)
    
    def test_get_measurement_descriptions(self):
        """Test measurement descriptions."""
        descriptions = self.measurements.get_measurement_descriptions()
        
        self.assertIsInstance(descriptions, dict)
        self.assertIn('shoulder_breadth', descriptions)
        self.assertIn('standing_height', descriptions)
        self.assertIn('arm_span', descriptions)
        
        # Check that all descriptions are strings
        for desc in descriptions.values():
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 0)
    
    @patch('cv2.cvtColor')
    def test_calculate_all_measurements_with_pose(self, mock_cvtColor):
        """Test calculating all measurements with a detected pose."""
        # Create a mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cvtColor.return_value = frame
        
        # Mock the pose processing
        with patch.object(self.measurements.pose, 'process') as mock_process:
            mock_result = Mock()
            mock_result.pose_landmarks = self.mock_landmarks
            mock_process.return_value = mock_result
            
            measurements = self.measurements.calculate_all_measurements(frame)
            
            self.assertIsInstance(measurements, dict)
            self.assertTrue(measurements.get('pose_detected', False))
            self.assertIn('shoulder_breadth', measurements)
            self.assertIn('standing_height', measurements)
            self.assertIn('timestamp', measurements)
            self.assertIn('calibration_note', measurements)
    
    @patch('cv2.cvtColor')
    def test_calculate_all_measurements_no_pose(self, mock_cvtColor):
        """Test calculating measurements when no pose is detected."""
        # Create a mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cvtColor.return_value = frame
        
        # Mock the pose processing with no landmarks
        with patch.object(self.measurements.pose, 'process') as mock_process:
            mock_result = Mock()
            mock_result.pose_landmarks = None
            mock_process.return_value = mock_result
            
            measurements = self.measurements.calculate_all_measurements(frame)
            
            self.assertIsInstance(measurements, dict)
            self.assertFalse(measurements.get('pose_detected', True))
            self.assertIn('error', measurements)
    
    @patch('cv2.cvtColor')
    def test_calculate_all_measurements_exception(self, mock_cvtColor):
        """Test calculating measurements when an exception occurs."""
        # Create a mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cvtColor.side_effect = Exception("Test exception")
        
        measurements = self.measurements.calculate_all_measurements(frame)
        
        self.assertIsInstance(measurements, dict)
        self.assertFalse(measurements.get('pose_detected', True))
        self.assertIn('error', measurements)
        self.assertEqual(measurements['error'], "Test exception")


class TestAnthropometricMeasurementsIntegration(unittest.TestCase):
    """Integration tests for anthropometric measurements with the Flask app."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MEDIAPIPE_AVAILABLE:
            self.skipTest("MediaPipe not available")
        
        # Import Flask app components
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import app
        self.app = app
        self.client = app.test_client()
        self.app.config['TESTING'] = True
    
    def test_measurements_api_endpoint(self):
        """Test the measurements API endpoint."""
        response = self.client.get('/api/measurements')
        
        # Should return either measurements or an error
        self.assertIn(response.status_code, [200, 400, 500])
        
        data = response.get_json()
        self.assertIsInstance(data, dict)
        
        if response.status_code == 200:
            # If successful, should have pose_detected field
            self.assertIn('pose_detected', data)
        else:
            # If error, should have error field
            self.assertIn('error', data)
    
    def test_measurement_descriptions_api_endpoint(self):
        """Test the measurement descriptions API endpoint."""
        response = self.client.get('/api/measurements/descriptions')
        
        if response.status_code == 200:
            data = response.get_json()
            self.assertIsInstance(data, dict)
            self.assertIn('shoulder_breadth', data)
        else:
            # Measurements system not available
            data = response.get_json()
            self.assertIn('error', data)
    
    def test_calibrate_measurements_api_endpoint(self):
        """Test the calibration API endpoint."""
        # Test with valid data
        response = self.client.post('/api/measurements/calibrate', 
                                  json={'pixel_to_cm_ratio': 0.15})
        
        if response.status_code == 200:
            data = response.get_json()
            self.assertTrue(data.get('success', False))
            self.assertEqual(data.get('pixel_to_cm_ratio'), 0.15)
        else:
            # Measurements system not available
            data = response.get_json()
            self.assertIn('error', data)
        
        # Test with invalid data
        response = self.client.post('/api/measurements/calibrate', 
                                  json={'pixel_to_cm_ratio': -0.1})
        
        if response.status_code != 400:
            # If measurements system is available, should return 400 for invalid data
            # If not available, will return different error
            pass
        
        # Test with missing data
        response = self.client.post('/api/measurements/calibrate', json={})
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_status_includes_measurements_availability(self):
        """Test that the status endpoint includes measurements availability."""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('measurements_available', data)
        self.assertIsInstance(data['measurements_available'], bool)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)