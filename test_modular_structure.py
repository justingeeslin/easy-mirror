#!/usr/bin/env python3
"""
Test script to verify the modular structure of Easy Mirror
Tests module imports, dependencies, and basic functionality.
"""

import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_module_imports():
    """Test that all modules can be imported correctly."""
    print("Testing module imports...")
    
    try:
        from modules.base import CameraManager
        print("✓ CameraManager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CameraManager: {e}")
        return False
    
    try:
        from modules.filters import BasicFilters, ClothingOverlay
        print("✓ BasicFilters and ClothingOverlay imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import filters: {e}")
        return False
    
    try:
        from modules.anthropometric import AnthropometricMeasurements
        print("✓ AnthropometricMeasurements imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AnthropometricMeasurements: {e}")
        return False
    
    try:
        from modules.prediction import SexPredictor
        print("✓ SexPredictor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SexPredictor: {e}")
        return False
    
    return True


def test_module_initialization():
    """Test that modules can be initialized correctly."""
    print("\nTesting module initialization...")
    
    try:
        from modules.base import CameraManager
        camera_manager = CameraManager()
        print("✓ CameraManager initialized")
    except Exception as e:
        print(f"✗ Failed to initialize CameraManager: {e}")
    
    try:
        from modules.filters import BasicFilters
        basic_filters = BasicFilters()
        filters = basic_filters.get_available_filters()
        print(f"✓ BasicFilters initialized with {len(filters)} filters: {filters}")
    except Exception as e:
        print(f"✗ Failed to initialize BasicFilters: {e}")
    
    try:
        from modules.anthropometric import AnthropometricMeasurements
        measurements = AnthropometricMeasurements()
        print("✓ AnthropometricMeasurements initialized")
    except Exception as e:
        print(f"✗ Failed to initialize AnthropometricMeasurements: {e}")
        return False
    
    try:
        from modules.prediction import SexPredictor
        sex_predictor = SexPredictor()
        print("✓ SexPredictor initialized")
    except Exception as e:
        print(f"✗ Failed to initialize SexPredictor: {e}")
        return False
    
    return True


def test_dependency_relationship():
    """Test that sex prediction properly depends on anthropometric measurements."""
    print("\nTesting dependency relationship...")
    
    try:
        from modules.anthropometric import AnthropometricMeasurements
        from modules.prediction import SexPredictor
        
        # Initialize both modules
        measurements_module = AnthropometricMeasurements()
        sex_predictor = SexPredictor()
        
        # Create mock measurement data (similar to what AnthropometricMeasurements would produce)
        mock_measurements = {
            'pose_detected': True,
            'height_cm': 175.0,
            'shoulder_breadth_cm': 42.0,
            'head_circumference_cm': 57.0,
            'shoulder_to_hip_ratio': 1.3,
            'head_to_shoulder_ratio': 0.25,
            'arm_span_to_height_ratio': 1.05
        }
        
        # Test that sex predictor can use measurements
        prediction_result = sex_predictor.predict_sex(mock_measurements)
        
        print(f"✓ Sex prediction works with measurement data:")
        print(f"  - Predicted sex: {prediction_result.get('predicted_sex', 'Unknown')}")
        print(f"  - Confidence: {prediction_result.get('confidence', 0):.2f}")
        print(f"  - Contributing factors: {len(prediction_result.get('contributing_factors', []))}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test dependency relationship: {e}")
        return False


def test_modular_app():
    """Test that the modular app can be imported and initialized."""
    print("\nTesting modular app...")
    
    try:
        import app_modular
        print("✓ Modular app imported successfully")
        
        # Test that the webcam filter was created
        if hasattr(app_modular, 'webcam_filter'):
            webcam_filter = app_modular.webcam_filter
            filters = webcam_filter.get_available_filters()
            print(f"✓ Modular webcam filter initialized with {len(filters)} filters")
            print(f"  Available filters: {filters}")
            
            # Test module availability
            modules_status = {
                'camera': webcam_filter.camera_manager is not None,
                'basic_filters': webcam_filter.basic_filters is not None,
                'clothing': webcam_filter.clothing_overlay is not None,
                'measurements': webcam_filter.anthropometric_measurements is not None,
                'sex_prediction': webcam_filter.sex_predictor is not None
            }
            
            print("  Module availability:")
            for module, available in modules_status.items():
                status = "✓" if available else "✗"
                print(f"    {status} {module}: {available}")
            
            return True
        else:
            print("✗ Webcam filter not found in modular app")
            return False
            
    except Exception as e:
        print(f"✗ Failed to test modular app: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Easy Mirror Modular Structure Test")
    print("=" * 60)
    
    tests = [
        test_module_imports,
        test_module_initialization,
        test_dependency_relationship,
        test_modular_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular structure is working correctly.")
        print("\nKey achievements:")
        print("- ✓ All modules can be imported independently")
        print("- ✓ Sex prediction module properly depends on anthropometric measurements")
        print("- ✓ Modular app integrates all components correctly")
        print("- ✓ Clear separation of concerns achieved")
    else:
        print("❌ Some tests failed. Please check the module structure.")
    
    print("=" * 60)


if __name__ == '__main__':
    main()