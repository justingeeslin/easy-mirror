#!/usr/bin/env python3
"""
Tests for the clothing analysis functionality.
"""

import unittest
import numpy as np
import cv2
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from clothing_analysis import ClothingAnalyzer
    CLOTHING_ANALYSIS_AVAILABLE = True
except ImportError:
    CLOTHING_ANALYSIS_AVAILABLE = False

class TestClothingAnalysis(unittest.TestCase):
    """Test cases for clothing analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not CLOTHING_ANALYSIS_AVAILABLE:
            self.skipTest("Clothing analysis not available - MediaPipe not installed")
        
        self.analyzer = ClothingAnalyzer()
        
        # Create test images
        self.test_frame = self.create_test_frame()
        self.test_frame_with_person = self.create_test_frame_with_person()
    
    def create_test_frame(self):
        """Create a simple test frame."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some color variation
        frame[:, :, 0] = 100  # Blue channel
        frame[:, :, 1] = 150  # Green channel
        frame[:, :, 2] = 200  # Red channel
        return frame
    
    def create_test_frame_with_person(self):
        """Create a test frame with a simple person-like shape."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Draw a simple person silhouette
        # Head (circle)
        cv2.circle(frame, (320, 100), 40, (100, 150, 200), -1)
        
        # Body (rectangle)
        cv2.rectangle(frame, (280, 140), (360, 300), (50, 100, 150), -1)
        
        # Arms
        cv2.rectangle(frame, (240, 160), (280, 250), (50, 100, 150), -1)  # Left arm
        cv2.rectangle(frame, (360, 160), (400, 250), (50, 100, 150), -1)  # Right arm
        
        # Legs
        cv2.rectangle(frame, (290, 300), (320, 450), (30, 60, 90), -1)   # Left leg
        cv2.rectangle(frame, (320, 300), (350, 450), (30, 60, 90), -1)   # Right leg
        
        return frame
    
    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.mp_selfie_segmentation)
        self.assertIsNotNone(self.analyzer.segmentation)
        self.assertIsNotNone(self.analyzer.mp_pose)
        self.assertIsNotNone(self.analyzer.pose)
    
    def test_color_ranges_defined(self):
        """Test that color ranges are properly defined."""
        self.assertIn('red', self.analyzer.color_ranges)
        self.assertIn('blue', self.analyzer.color_ranges)
        self.assertIn('green', self.analyzer.color_ranges)
        self.assertIn('black', self.analyzer.color_ranges)
        self.assertIn('white', self.analyzer.color_ranges)
        
        # Check that each color range has proper format
        for color, ranges in self.analyzer.color_ranges.items():
            if len(ranges) == 4:  # Red has two ranges
                self.assertEqual(len(ranges[0]), 3)  # HSV tuple
                self.assertEqual(len(ranges[1]), 3)
                self.assertEqual(len(ranges[2]), 3)
                self.assertEqual(len(ranges[3]), 3)
            else:
                self.assertEqual(len(ranges), 2)  # Min and max HSV
                self.assertEqual(len(ranges[0]), 3)
                self.assertEqual(len(ranges[1]), 3)
    
    def test_garment_patterns_defined(self):
        """Test that garment patterns are properly defined."""
        expected_garments = ['shirt', 'tank_top', 'long_sleeve', 'dress', 'blouse', 'jacket', 'pants', 'shorts', 'skirt']
        
        for garment in expected_garments:
            self.assertIn(garment, self.analyzer.garment_patterns)
            pattern = self.analyzer.garment_patterns[garment]
            self.assertIsInstance(pattern, dict)
    
    def test_material_indicators_defined(self):
        """Test that material indicators are properly defined."""
        expected_materials = ['denim', 'cotton', 'silk', 'wool', 'leather', 'polyester']
        
        for material in expected_materials:
            self.assertIn(material, self.analyzer.material_indicators)
            indicators = self.analyzer.material_indicators[material]
            self.assertIn('texture_variance', indicators)
            self.assertIn('color_consistency', indicators)
    
    def test_segment_person_empty_frame(self):
        """Test person segmentation with empty frame."""
        result = self.analyzer.segment_person(self.test_frame)
        # Should return a mask (might be all zeros for empty frame)
        if result is not None:
            self.assertEqual(result.dtype, np.uint8)
            self.assertEqual(result.shape, (480, 640))
    
    def test_analyze_color_basic(self):
        """Test basic color analysis."""
        # Create a red region
        red_region = np.zeros((100, 100, 3), dtype=np.uint8)
        red_region[:, :, 2] = 255  # Red channel
        
        color = self.analyzer.analyze_color(red_region)
        # Should detect some color (might not be perfect due to HSV conversion)
        self.assertIsInstance(color, str)
        self.assertNotEqual(color, '')
    
    def test_analyze_color_empty_region(self):
        """Test color analysis with empty region."""
        empty_region = np.zeros((0, 0, 3), dtype=np.uint8)
        color = self.analyzer.analyze_color(empty_region)
        self.assertEqual(color, 'unknown')
    
    def test_analyze_texture_basic(self):
        """Test basic texture analysis."""
        # Create a textured region
        textured_region = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        material = self.analyzer.analyze_texture(textured_region)
        self.assertIsInstance(material, str)
        self.assertIn(material, self.analyzer.material_indicators.keys() | {'cotton'})  # cotton is default
    
    def test_analyze_texture_empty_region(self):
        """Test texture analysis with empty region."""
        empty_region = np.zeros((0, 0, 3), dtype=np.uint8)
        material = self.analyzer.analyze_texture(empty_region)
        self.assertEqual(material, 'unknown')
    
    def test_classify_garment_no_regions(self):
        """Test garment classification with no regions."""
        empty_mask = np.zeros((480, 640), dtype=np.uint8)
        garment_type = self.analyzer.classify_garment({}, empty_mask, self.test_frame)
        self.assertEqual(garment_type, 'unknown')
    
    def test_detect_garment_features_no_regions(self):
        """Test garment feature detection with no regions."""
        features = self.analyzer.detect_garment_features({}, self.test_frame, 'shirt')
        self.assertIsInstance(features, dict)
    
    def test_detect_embellishments_no_regions(self):
        """Test embellishment detection with no regions."""
        embellishments = self.analyzer.detect_embellishments({}, self.test_frame)
        self.assertIsInstance(embellishments, list)
    
    def test_analyze_clothing_no_person(self):
        """Test clothing analysis with no person in frame."""
        analysis = self.analyzer.analyze_clothing(self.test_frame)
        # Should return None or handle gracefully
        if analysis is not None:
            self.assertIsInstance(analysis, dict)
    
    def test_analyze_clothing_with_person_shape(self):
        """Test clothing analysis with person-like shape."""
        analysis = self.analyzer.analyze_clothing(self.test_frame_with_person)
        
        if analysis is not None:
            # Check that analysis has expected structure
            self.assertIn('garment_type', analysis)
            self.assertIn('colors', analysis)
            self.assertIn('materials', analysis)
            self.assertIn('features', analysis)
            self.assertIn('embellishments', analysis)
            self.assertIn('confidence', analysis)
            
            # Check data types
            self.assertIsInstance(analysis['garment_type'], str)
            self.assertIsInstance(analysis['colors'], dict)
            self.assertIsInstance(analysis['materials'], dict)
            self.assertIsInstance(analysis['features'], dict)
            self.assertIsInstance(analysis['embellishments'], list)
            self.assertIsInstance(analysis['confidence'], (int, float))
            
            # Check confidence is in valid range
            self.assertGreaterEqual(analysis['confidence'], 0.0)
            self.assertLessEqual(analysis['confidence'], 1.0)
    
    def test_get_last_analysis_initially_none(self):
        """Test that last analysis is initially None."""
        fresh_analyzer = ClothingAnalyzer()
        self.assertIsNone(fresh_analyzer.get_last_analysis())
    
    def test_get_last_analysis_after_analysis(self):
        """Test that last analysis is stored after running analysis."""
        # Run analysis first
        self.analyzer.analyze_clothing(self.test_frame_with_person)
        
        # Get last analysis
        last_analysis = self.analyzer.get_last_analysis()
        
        if last_analysis is not None:
            self.assertIsInstance(last_analysis, dict)
    
    def test_get_body_regions_no_landmarks(self):
        """Test body region detection with no landmarks."""
        regions = self.analyzer.get_body_regions(self.test_frame, None)
        self.assertEqual(regions, {})
    
    def test_error_handling_invalid_frame(self):
        """Test error handling with invalid frame."""
        # Test with None frame
        analysis = self.analyzer.analyze_clothing(None)
        self.assertIsNone(analysis)
        
        # Test with invalid frame shape
        invalid_frame = np.zeros((10, 10), dtype=np.uint8)  # Missing color channels
        analysis = self.analyzer.analyze_clothing(invalid_frame)
        # Should handle gracefully (return None or valid analysis)
        if analysis is not None:
            self.assertIsInstance(analysis, dict)


class TestClothingAnalysisIntegration(unittest.TestCase):
    """Integration tests for clothing analysis with the main application."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not CLOTHING_ANALYSIS_AVAILABLE:
            self.skipTest("Clothing analysis not available - MediaPipe not installed")
    
    def test_import_clothing_analysis(self):
        """Test that clothing analysis module can be imported."""
        from clothing_analysis import ClothingAnalyzer
        analyzer = ClothingAnalyzer()
        self.assertIsNotNone(analyzer)
    
    def test_clothing_analysis_api_structure(self):
        """Test that the ClothingAnalyzer has the expected API."""
        from clothing_analysis import ClothingAnalyzer
        analyzer = ClothingAnalyzer()
        
        # Check that required methods exist
        self.assertTrue(hasattr(analyzer, 'analyze_clothing'))
        self.assertTrue(hasattr(analyzer, 'get_last_analysis'))
        self.assertTrue(hasattr(analyzer, 'segment_person'))
        self.assertTrue(hasattr(analyzer, 'analyze_color'))
        self.assertTrue(hasattr(analyzer, 'analyze_texture'))
        self.assertTrue(hasattr(analyzer, 'classify_garment'))
        self.assertTrue(hasattr(analyzer, 'detect_garment_features'))
        self.assertTrue(hasattr(analyzer, 'detect_embellishments'))
        
        # Check that methods are callable
        self.assertTrue(callable(analyzer.analyze_clothing))
        self.assertTrue(callable(analyzer.get_last_analysis))


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)