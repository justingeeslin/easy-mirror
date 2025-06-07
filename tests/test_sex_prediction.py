#!/usr/bin/env python3
"""
Test suite for sex prediction functionality.
"""

import unittest
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sex_prediction import SexPredictor


class TestSexPredictor(unittest.TestCase):
    """Test cases for the SexPredictor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predictor = SexPredictor()
        
        # Sample measurements representing typical male characteristics
        self.male_measurements = {
            'shoulder_breadth': 42.5,
            'standing_height': 175.0,
            'arm_span': 180.0,
            'head_circumference': 58.0,
            'waist_circumference': 85.0,
            'left_upper_arm_length': 32.0,
            'left_forearm_length': 22.0,
            'pose_detected': True
        }
        
        # Sample measurements representing typical female characteristics
        self.female_measurements = {
            'shoulder_breadth': 34.0,
            'standing_height': 162.0,
            'arm_span': 162.0,
            'head_circumference': 54.0,
            'waist_circumference': 70.0,
            'left_upper_arm_length': 28.0,
            'left_forearm_length': 20.5,
            'pose_detected': True
        }
        
        # Ambiguous measurements (in overlap zones)
        self.ambiguous_measurements = {
            'shoulder_breadth': 37.0,  # In overlap zone
            'standing_height': 167.0,  # In overlap zone
            'arm_span': 167.0,
            'head_circumference': 55.5,  # In overlap zone
            'waist_circumference': 77.0,
            'pose_detected': True
        }
        
        # Minimal measurements
        self.minimal_measurements = {
            'shoulder_breadth': 40.0,
            'pose_detected': True
        }
    
    def test_initialization(self):
        """Test that the SexPredictor class initializes correctly."""
        self.assertIsInstance(self.predictor.shoulder_breadth_thresholds, dict)
        self.assertIsInstance(self.predictor.height_thresholds, dict)
        self.assertIsInstance(self.predictor.ratio_thresholds, dict)
        self.assertIsInstance(self.predictor.indicator_weights, dict)
        
        # Check that weights sum to approximately 1.0
        total_weight = sum(self.predictor.indicator_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)
    
    def test_calculate_hip_width_estimate(self):
        """Test hip width estimation from waist circumference."""
        measurements = {'waist_circumference': 70.0}
        hip_width = self.predictor.calculate_hip_width_estimate(measurements)
        
        self.assertIsNotNone(hip_width)
        self.assertGreater(hip_width, 0)
        self.assertAlmostEqual(hip_width, 70.0 / 3.5, places=2)
        
        # Test with no waist measurement
        empty_measurements = {}
        hip_width = self.predictor.calculate_hip_width_estimate(empty_measurements)
        self.assertIsNone(hip_width)
    
    def test_calculate_ratios(self):
        """Test ratio calculations."""
        ratios = self.predictor.calculate_ratios(self.male_measurements)
        
        self.assertIsInstance(ratios, dict)
        
        # Test shoulder to hip ratio
        if ratios['shoulder_hip_ratio'] is not None:
            self.assertGreater(ratios['shoulder_hip_ratio'], 0)
        
        # Test arm span to height ratio
        if ratios['armspan_height_ratio'] is not None:
            expected_ratio = self.male_measurements['arm_span'] / self.male_measurements['standing_height']
            self.assertAlmostEqual(ratios['armspan_height_ratio'], expected_ratio, places=3)
        
        # Test head to height ratio
        if ratios['head_height_ratio'] is not None:
            expected_ratio = self.male_measurements['head_circumference'] / self.male_measurements['standing_height']
            self.assertAlmostEqual(ratios['head_height_ratio'], expected_ratio, places=3)
        
        # Test upper arm to forearm ratio
        if ratios['upperarm_forearm_ratio'] is not None:
            expected_ratio = self.male_measurements['left_upper_arm_length'] / self.male_measurements['left_forearm_length']
            self.assertAlmostEqual(ratios['upperarm_forearm_ratio'], expected_ratio, places=3)
    
    def test_evaluate_indicator_shoulder_breadth(self):
        """Test shoulder breadth indicator evaluation."""
        # Test male-typical value
        prediction, confidence = self.predictor.evaluate_indicator(42.0, 'shoulder_breadth')
        self.assertEqual(prediction, 'male')
        self.assertGreater(confidence, 0.5)
        
        # Test female-typical value
        prediction, confidence = self.predictor.evaluate_indicator(34.0, 'shoulder_breadth')
        self.assertEqual(prediction, 'female')
        self.assertGreater(confidence, 0.5)
        
        # Test ambiguous value
        prediction, confidence = self.predictor.evaluate_indicator(37.0, 'shoulder_breadth')
        self.assertEqual(prediction, 'uncertain')
    
    def test_evaluate_indicator_height(self):
        """Test height indicator evaluation."""
        # Test male-typical value
        prediction, confidence = self.predictor.evaluate_indicator(175.0, 'standing_height')
        self.assertEqual(prediction, 'male')
        self.assertGreater(confidence, 0.5)
        
        # Test female-typical value
        prediction, confidence = self.predictor.evaluate_indicator(160.0, 'standing_height')
        self.assertEqual(prediction, 'female')
        self.assertGreater(confidence, 0.5)
    
    def test_evaluate_indicator_ratios(self):
        """Test ratio indicator evaluation."""
        # Test shoulder-hip ratio
        prediction, confidence = self.predictor.evaluate_indicator(1.4, 'shoulder_hip_ratio')
        self.assertEqual(prediction, 'male')
        self.assertGreater(confidence, 0.5)
        
        prediction, confidence = self.predictor.evaluate_indicator(1.2, 'shoulder_hip_ratio')
        self.assertEqual(prediction, 'female')
        self.assertGreater(confidence, 0.5)
        
        # Test arm span to height ratio
        prediction, confidence = self.predictor.evaluate_indicator(1.05, 'armspan_height_ratio')
        self.assertEqual(prediction, 'male')
        
        prediction, confidence = self.predictor.evaluate_indicator(0.98, 'armspan_height_ratio')
        self.assertEqual(prediction, 'female')
    
    def test_predict_sex_male_typical(self):
        """Test sex prediction with typical male measurements."""
        result = self.predictor.predict_sex(self.male_measurements)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['prediction'], 'male')
        self.assertGreater(result['confidence'], 0.5)
        self.assertGreater(result['certainty'], 0.5)
        self.assertIn('scores', result)
        self.assertIn('indicator_details', result)
        self.assertGreater(result['indicators_used'], 0)
    
    def test_predict_sex_female_typical(self):
        """Test sex prediction with typical female measurements."""
        result = self.predictor.predict_sex(self.female_measurements)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['prediction'], 'female')
        self.assertGreater(result['confidence'], 0.5)
        self.assertGreater(result['certainty'], 0.5)
        self.assertIn('scores', result)
        self.assertIn('indicator_details', result)
        self.assertGreater(result['indicators_used'], 0)
    
    def test_predict_sex_ambiguous(self):
        """Test sex prediction with ambiguous measurements."""
        result = self.predictor.predict_sex(self.ambiguous_measurements)
        
        self.assertIsInstance(result, dict)
        self.assertIn(result['prediction'], ['male', 'female', 'uncertain'])
        # Confidence should be lower for ambiguous cases
        self.assertLessEqual(result['confidence'], 0.8)
        self.assertIn('scores', result)
        self.assertIn('indicator_details', result)
    
    def test_predict_sex_minimal_data(self):
        """Test sex prediction with minimal measurements."""
        result = self.predictor.predict_sex(self.minimal_measurements)
        
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertGreater(result['indicators_used'], 0)
        self.assertLess(result['indicators_used'], result['total_possible_indicators'])
    
    def test_predict_sex_no_data(self):
        """Test sex prediction with no useful measurements."""
        empty_measurements = {'pose_detected': True}
        result = self.predictor.predict_sex(empty_measurements)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['prediction'], 'insufficient_data')
        self.assertEqual(result['confidence'], 0.0)
        self.assertEqual(result['indicators_used'], 0)
    
    def test_get_prediction_explanation(self):
        """Test prediction explanation generation."""
        result = self.predictor.predict_sex(self.male_measurements)
        explanation = self.predictor.get_prediction_explanation(result)
        
        self.assertIsInstance(explanation, str)
        self.assertIn('Prediction:', explanation)
        self.assertIn('Confidence:', explanation)
        self.assertIn('Key indicators:', explanation)
        self.assertGreater(len(explanation), 100)  # Should be a substantial explanation
    
    def test_get_prediction_explanation_error(self):
        """Test prediction explanation for error cases."""
        error_result = {'prediction': 'error', 'error': 'Test error'}
        explanation = self.predictor.get_prediction_explanation(error_result)
        
        self.assertIsInstance(explanation, str)
        self.assertIn('Error in prediction:', explanation)
        self.assertIn('Test error', explanation)
    
    def test_get_prediction_explanation_insufficient_data(self):
        """Test prediction explanation for insufficient data."""
        insufficient_result = {'prediction': 'insufficient_data'}
        explanation = self.predictor.get_prediction_explanation(insufficient_result)
        
        self.assertIsInstance(explanation, str)
        self.assertIn('Insufficient anthropometric data', explanation)
    
    def test_score_consistency(self):
        """Test that male and female scores are consistent."""
        result = self.predictor.predict_sex(self.male_measurements)
        
        # Male score should be higher for male-typical measurements
        self.assertGreater(result['scores']['male'], result['scores']['female'])
        
        result = self.predictor.predict_sex(self.female_measurements)
        
        # Female score should be higher for female-typical measurements
        self.assertGreater(result['scores']['female'], result['scores']['male'])
    
    def test_confidence_bounds(self):
        """Test that confidence values are within valid bounds."""
        test_cases = [self.male_measurements, self.female_measurements, self.ambiguous_measurements]
        
        for measurements in test_cases:
            result = self.predictor.predict_sex(measurements)
            
            # Confidence should be between 0 and 1
            self.assertGreaterEqual(result['confidence'], 0.0)
            self.assertLessEqual(result['confidence'], 1.0)
            
            # Certainty should be between 0 and 1
            self.assertGreaterEqual(result['certainty'], 0.0)
            self.assertLessEqual(result['certainty'], 1.0)
            
            # Scores should be between 0 and 1
            self.assertGreaterEqual(result['scores']['male'], 0.0)
            self.assertLessEqual(result['scores']['male'], 1.0)
            self.assertGreaterEqual(result['scores']['female'], 0.0)
            self.assertLessEqual(result['scores']['female'], 1.0)


class TestSexPredictionIntegration(unittest.TestCase):
    """Integration tests for sex prediction with anthropometric measurements."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predictor = SexPredictor()
    
    def test_integration_with_anthropometric_measurements(self):
        """Test integration with the anthropometric measurements system."""
        # This test would require the anthropometric measurements system
        # For now, we'll test with simulated measurement output
        
        simulated_measurements = {
            'shoulder_breadth': 40.2,
            'standing_height': 172.5,
            'arm_span': 175.8,
            'left_upper_arm_length': 30.5,
            'right_upper_arm_length': 30.8,
            'left_forearm_length': 21.2,
            'right_forearm_length': 21.0,
            'left_thigh_length': 42.0,
            'right_thigh_length': 41.8,
            'left_lower_leg_length': 38.5,
            'right_lower_leg_length': 38.2,
            'chest_circumference': 96.0,
            'waist_circumference': 82.0,
            'head_circumference': 57.2,
            'timestamp': 1234567890.0,
            'pose_detected': True,
            'calibration_note': 'Test calibration'
        }
        
        result = self.predictor.predict_sex(simulated_measurements)
        
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('indicator_details', result)
        self.assertGreater(result['indicators_used'], 3)  # Should use multiple indicators


if __name__ == '__main__':
    unittest.main()