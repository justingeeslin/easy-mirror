#!/usr/bin/env python3
"""
Test script to verify the sex prediction API integration.
"""

import json
import requests
import time
from threading import Thread
from app import app

def start_test_server():
    """Start the Flask app in test mode."""
    app.config['TESTING'] = True
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def test_sex_prediction_api():
    """Test the sex prediction API endpoints."""
    base_url = "http://localhost:5000"
    
    # Wait for server to start
    time.sleep(2)
    
    print("Testing Sex Prediction API Integration...")
    print("=" * 50)
    
    # Test 1: Predict from measurements endpoint
    print("\n1. Testing /api/sex-prediction/from-measurements")
    
    sample_measurements = {
        'shoulder_breadth': 42.0,
        'standing_height': 175.0,
        'arm_span': 178.0,
        'head_circumference': 58.0,
        'waist_circumference': 85.0,
        'left_upper_arm_length': 32.0,
        'left_forearm_length': 22.0,
        'pose_detected': True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sex-prediction/from-measurements",
            json=sample_measurements,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success! Prediction: {result['prediction']}")
            print(f"  Confidence: {result['confidence']:.1%}")
            print(f"  Indicators used: {result['indicators_used']}/{result['total_possible_indicators']}")
            
            # Test 2: Get explanation
            print("\n2. Testing /api/sex-prediction/explanation")
            
            explanation_response = requests.post(
                f"{base_url}/api/sex-prediction/explanation",
                json=result,
                timeout=10
            )
            
            if explanation_response.status_code == 200:
                explanation_data = explanation_response.json()
                print("✓ Explanation generated successfully")
                print("First few lines of explanation:")
                explanation_lines = explanation_data['explanation'].split('\n')[:5]
                for line in explanation_lines:
                    print(f"  {line}")
            else:
                print(f"✗ Explanation failed: {explanation_response.status_code}")
                
        else:
            print(f"✗ Prediction failed: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
    
    # Test 3: Test with minimal data
    print("\n3. Testing with minimal measurements")
    
    minimal_measurements = {
        'shoulder_breadth': 35.0,
        'pose_detected': True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/sex-prediction/from-measurements",
            json=minimal_measurements,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Minimal data prediction: {result['prediction']}")
            print(f"  Indicators used: {result['indicators_used']}")
        else:
            print(f"✗ Minimal data test failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Minimal data request failed: {e}")
    
    # Test 4: Test with no data
    print("\n4. Testing with insufficient data")
    
    try:
        response = requests.post(
            f"{base_url}/api/sex-prediction/from-measurements",
            json={'pose_detected': True},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['prediction'] == 'insufficient_data':
                print("✓ Correctly identified insufficient data")
            else:
                print(f"✗ Unexpected result: {result['prediction']}")
        else:
            print(f"✗ Insufficient data test failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Insufficient data request failed: {e}")
    
    print("\n" + "=" * 50)
    print("API Integration Test Complete!")

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    server_thread = Thread(target=start_test_server, daemon=True)
    server_thread.start()
    
    # Run the tests
    test_sex_prediction_api()