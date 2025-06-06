#!/usr/bin/env python3
"""
Tests for the clothing analysis API endpoints.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock
import numpy as np
import cv2

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app, webcam_filter, CLOTHING_ANALYSIS_AVAILABLE
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False


class TestClothingAnalysisAPI(unittest.TestCase):
    """Test cases for clothing analysis API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not APP_AVAILABLE:
            self.skipTest("App not available for testing")
        
        self.app = app.test_client()
        self.app.testing = True
    
    def test_status_endpoint_includes_clothing_analysis(self):
        """Test that status endpoint includes clothing analysis availability."""
        response = self.app.get('/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('clothing_analysis_available', data)
        self.assertIsInstance(data['clothing_analysis_available'], bool)
    
    @unittest.skipUnless(CLOTHING_ANALYSIS_AVAILABLE, "Clothing analysis not available")
    def test_analyze_clothing_endpoint_no_frame(self):
        """Test clothing analysis endpoint when no frame is available."""
        with patch.object(webcam_filter, 'get_frame', return_value=None):
            response = self.app.post('/api/clothing/analyze')
            self.assertEqual(response.status_code, 400)
            
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('No frame available', data['error'])
    
    @unittest.skipUnless(CLOTHING_ANALYSIS_AVAILABLE, "Clothing analysis not available")
    def test_analyze_clothing_endpoint_with_mock_frame(self):
        """Test clothing analysis endpoint with a mock frame."""
        # Create a mock JPEG frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:, :] = [100, 150, 200]  # Some color
        
        # Encode as JPEG
        ret, buffer = cv2.imencode('.jpg', test_frame)
        mock_frame_bytes = buffer.tobytes()
        
        # Mock the analyzer to return a valid analysis
        mock_analysis = {
            'garment_type': 'shirt',
            'colors': {'torso': 'blue'},
            'materials': {'torso': 'cotton'},
            'features': {'neckline': 'crew', 'sleeve_length': 'short'},
            'embellishments': [],
            'confidence': 0.8
        }
        
        with patch.object(webcam_filter, 'get_frame', return_value=mock_frame_bytes):
            with patch.object(webcam_filter.clothing_analyzer, 'analyze_clothing', return_value=mock_analysis):
                response = self.app.post('/api/clothing/analyze')
                self.assertEqual(response.status_code, 200)
                
                data = json.loads(response.data)
                self.assertIn('success', data)
                self.assertTrue(data['success'])
                self.assertIn('analysis', data)
                
                analysis = data['analysis']
                self.assertEqual(analysis['garment_type'], 'shirt')
                self.assertIn('colors', analysis)
                self.assertIn('materials', analysis)
                self.assertIn('features', analysis)
                self.assertIn('embellishments', analysis)
                self.assertIn('confidence', analysis)
    
    @unittest.skipUnless(CLOTHING_ANALYSIS_AVAILABLE, "Clothing analysis not available")
    def test_analyze_clothing_endpoint_analysis_failure(self):
        """Test clothing analysis endpoint when analysis fails."""
        # Create a mock JPEG frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ret, buffer = cv2.imencode('.jpg', test_frame)
        mock_frame_bytes = buffer.tobytes()
        
        with patch.object(webcam_filter, 'get_frame', return_value=mock_frame_bytes):
            with patch.object(webcam_filter.clothing_analyzer, 'analyze_clothing', return_value=None):
                response = self.app.post('/api/clothing/analyze')
                self.assertEqual(response.status_code, 400)
                
                data = json.loads(response.data)
                self.assertIn('error', data)
                self.assertIn('Failed to analyze clothing', data['error'])
    
    @unittest.skipUnless(CLOTHING_ANALYSIS_AVAILABLE, "Clothing analysis not available")
    def test_get_clothing_analysis_endpoint_no_analysis(self):
        """Test get clothing analysis endpoint when no analysis is available."""
        with patch.object(webcam_filter.clothing_analyzer, 'get_last_analysis', return_value=None):
            response = self.app.get('/api/clothing/analysis')
            self.assertEqual(response.status_code, 400)
            
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('No analysis available', data['error'])
    
    @unittest.skipUnless(CLOTHING_ANALYSIS_AVAILABLE, "Clothing analysis not available")
    def test_get_clothing_analysis_endpoint_with_analysis(self):
        """Test get clothing analysis endpoint with available analysis."""
        mock_analysis = {
            'garment_type': 'dress',
            'colors': {'torso': 'red', 'left_leg': 'red'},
            'materials': {'torso': 'silk'},
            'features': {'neckline': 'v-neck', 'sleeve_length': 'sleeveless'},
            'embellishments': ['buttons'],
            'confidence': 0.9
        }
        
        with patch.object(webcam_filter.clothing_analyzer, 'get_last_analysis', return_value=mock_analysis):
            response = self.app.get('/api/clothing/analysis')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('analysis', data)
            
            analysis = data['analysis']
            self.assertEqual(analysis['garment_type'], 'dress')
            self.assertIn('red', analysis['colors']['torso'])
            self.assertIn('buttons', analysis['embellishments'])
    
    def test_analyze_clothing_endpoint_not_available(self):
        """Test clothing analysis endpoint when analyzer is not available."""
        with patch.object(webcam_filter, 'clothing_analyzer', None):
            response = self.app.post('/api/clothing/analyze')
            self.assertEqual(response.status_code, 400)
            
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Clothing analysis system not available', data['error'])
    
    def test_get_clothing_analysis_endpoint_not_available(self):
        """Test get clothing analysis endpoint when analyzer is not available."""
        with patch.object(webcam_filter, 'clothing_analyzer', None):
            response = self.app.get('/api/clothing/analysis')
            self.assertEqual(response.status_code, 400)
            
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Clothing analysis system not available', data['error'])
    
    def test_analyze_clothing_endpoint_invalid_frame(self):
        """Test clothing analysis endpoint with invalid frame data."""
        if not CLOTHING_ANALYSIS_AVAILABLE:
            self.skipTest("Clothing analysis not available")
        
        # Mock invalid frame data
        invalid_frame_bytes = b'invalid_jpeg_data'
        
        with patch.object(webcam_filter, 'get_frame', return_value=invalid_frame_bytes):
            response = self.app.post('/api/clothing/analyze')
            self.assertEqual(response.status_code, 400)
            
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Failed to decode frame', data['error'])


class TestClothingAnalysisAPIIntegration(unittest.TestCase):
    """Integration tests for clothing analysis API."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not APP_AVAILABLE:
            self.skipTest("App not available for testing")
        
        self.app = app.test_client()
        self.app.testing = True
    
    def test_api_endpoints_exist(self):
        """Test that the new API endpoints exist and return appropriate responses."""
        # Test analyze endpoint
        response = self.app.post('/api/clothing/analyze')
        self.assertIn(response.status_code, [200, 400])  # Should not be 404
        
        # Test get analysis endpoint
        response = self.app.get('/api/clothing/analysis')
        self.assertIn(response.status_code, [200, 400])  # Should not be 404
    
    def test_api_response_format(self):
        """Test that API responses have the correct format."""
        # Test analyze endpoint response format
        response = self.app.post('/api/clothing/analyze')
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        
        # Should have either success or error
        self.assertTrue('success' in data or 'error' in data)
        
        # Test get analysis endpoint response format
        response = self.app.get('/api/clothing/analysis')
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertTrue('success' in data or 'error' in data)
    
    @unittest.skipUnless(CLOTHING_ANALYSIS_AVAILABLE, "Clothing analysis not available")
    def test_full_analysis_workflow(self):
        """Test the full workflow of analyzing clothing and retrieving results."""
        # Create a mock frame and analysis
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:, :] = [50, 100, 150]
        ret, buffer = cv2.imencode('.jpg', test_frame)
        mock_frame_bytes = buffer.tobytes()
        
        mock_analysis = {
            'garment_type': 'blouse',
            'colors': {'torso': 'blue'},
            'materials': {'torso': 'cotton'},
            'features': {'neckline': 'scoop', 'sleeve_length': 'long'},
            'embellishments': ['zipper'],
            'confidence': 0.7
        }
        
        with patch.object(webcam_filter, 'get_frame', return_value=mock_frame_bytes):
            with patch.object(webcam_filter.clothing_analyzer, 'analyze_clothing', return_value=mock_analysis):
                with patch.object(webcam_filter.clothing_analyzer, 'get_last_analysis', return_value=mock_analysis):
                    # Step 1: Analyze clothing
                    response = self.app.post('/api/clothing/analyze')
                    self.assertEqual(response.status_code, 200)
                    
                    analyze_data = json.loads(response.data)
                    self.assertTrue(analyze_data['success'])
                    self.assertIn('analysis', analyze_data)
                    
                    # Step 2: Get the analysis result
                    response = self.app.get('/api/clothing/analysis')
                    self.assertEqual(response.status_code, 200)
                    
                    get_data = json.loads(response.data)
                    self.assertTrue(get_data['success'])
                    self.assertIn('analysis', get_data)
                    
                    # Verify the analysis data is consistent
                    analysis1 = analyze_data['analysis']
                    analysis2 = get_data['analysis']
                    self.assertEqual(analysis1['garment_type'], analysis2['garment_type'])
                    self.assertEqual(analysis1['confidence'], analysis2['confidence'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)