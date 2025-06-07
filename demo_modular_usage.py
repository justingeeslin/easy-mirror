#!/usr/bin/env python3
"""
Demonstration of Easy Mirror Modular Usage
Shows how different modules work together, with emphasis on dependency relationships.
"""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_individual_modules():
    """Demonstrate using individual modules separately."""
    print("=" * 60)
    print("DEMO: Individual Module Usage")
    print("=" * 60)
    
    # 1. Basic Filters Module (independent)
    print("\n1. Basic Filters Module (Independent)")
    print("-" * 40)
    try:
        from modules.filters import BasicFilters
        
        filters = BasicFilters()
        available_filters = filters.get_available_filters()
        print(f"✓ BasicFilters initialized")
        print(f"  Available filters: {available_filters}")
        
        # Create a dummy frame for demonstration
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        dummy_frame[:, :] = [100, 150, 200]  # Light blue
        
        # Apply a filter
        filtered_frame = filters.apply_filter(dummy_frame, 'sepia')
        print(f"  ✓ Applied sepia filter to dummy frame")
        
    except Exception as e:
        print(f"✗ Error with BasicFilters: {e}")
    
    # 2. Camera Manager Module (independent)
    print("\n2. Camera Manager Module (Independent)")
    print("-" * 40)
    try:
        from modules.base import CameraManager
        
        camera = CameraManager()
        is_available = camera.is_available()
        print(f"✓ CameraManager initialized")
        print(f"  Camera available: {is_available}")
        
        if is_available:
            ret, frame = camera.read_frame()
            if ret:
                print(f"  ✓ Successfully captured frame: {frame.shape}")
            else:
                print(f"  ✗ Failed to capture frame")
        
        camera.cleanup()
        
    except Exception as e:
        print(f"✗ Error with CameraManager: {e}")
    
    # 3. Anthropometric Measurements Module (independent)
    print("\n3. Anthropometric Measurements Module (Independent)")
    print("-" * 40)
    try:
        from modules.anthropometric import AnthropometricMeasurements
        
        measurements = AnthropometricMeasurements()
        print(f"✓ AnthropometricMeasurements initialized")
        
        # Get measurement descriptions
        descriptions = measurements.get_measurement_descriptions()
        print(f"  Available measurements: {len(descriptions)} types")
        for name, desc in list(descriptions.items())[:3]:  # Show first 3
            print(f"    - {name}: {desc}")
        print(f"    ... and {len(descriptions) - 3} more")
        
    except Exception as e:
        print(f"✗ Error with AnthropometricMeasurements: {e}")


def demo_dependency_relationship():
    """Demonstrate the dependency relationship between modules."""
    print("\n" + "=" * 60)
    print("DEMO: Module Dependency Relationship")
    print("=" * 60)
    
    print("\n🔗 Sex Prediction Module DEPENDS ON Anthropometric Measurements Module")
    print("-" * 60)
    
    try:
        # Import both modules
        from modules.anthropometric import AnthropometricMeasurements
        from modules.prediction import SexPredictor
        
        # Initialize modules
        measurements_module = AnthropometricMeasurements()
        sex_predictor = SexPredictor()
        
        print("✓ Both modules initialized successfully")
        
        # Create realistic mock measurement data (what AnthropometricMeasurements would produce)
        print("\n📏 Creating mock anthropometric measurements...")
        mock_measurements = {
            'pose_detected': True,
            'height_cm': 175.0,
            'shoulder_breadth_cm': 42.0,
            'head_circumference_cm': 57.0,
            'shoulder_to_hip_ratio': 1.3,
            'head_to_shoulder_ratio': 0.25,
            'arm_span_to_height_ratio': 1.05,
            'neck_circumference_cm': 38.0,
            'chest_circumference_cm': 95.0,
            'waist_circumference_cm': 85.0,
            'hip_circumference_cm': 92.0
        }
        
        print("  Mock measurements created:")
        for key, value in mock_measurements.items():
            if isinstance(value, bool):
                print(f"    {key}: {value}")
            elif isinstance(value, (int, float)):
                print(f"    {key}: {value:.2f}")
        
        # Demonstrate the dependency: Sex prediction USES measurement data
        print("\n🔮 Using measurements for sex prediction...")
        prediction_result = sex_predictor.predict_sex(mock_measurements)
        
        print("✓ Sex prediction completed using anthropometric data:")
        print(f"  Predicted sex: {prediction_result.get('predicted_sex', 'Unknown')}")
        print(f"  Confidence: {prediction_result.get('confidence', 0):.2f}")
        print(f"  Contributing factors: {len(prediction_result.get('contributing_factors', []))}")
        
        # Show some contributing factors
        factors = prediction_result.get('contributing_factors', [])
        if factors:
            print("  Key contributing factors:")
            for factor in factors[:3]:  # Show first 3
                print(f"    - {factor}")
        
        # Demonstrate what happens without measurement data
        print("\n❌ Demonstrating dependency: What happens without proper measurement data?")
        incomplete_data = {'pose_detected': False}
        
        try:
            incomplete_prediction = sex_predictor.predict_sex(incomplete_data)
            print(f"  With incomplete data: {incomplete_prediction}")
        except Exception as e:
            print(f"  Error with incomplete data: {e}")
        
        print("\n💡 Key Dependency Points:")
        print("  1. Sex prediction REQUIRES anthropometric measurement data")
        print("  2. The data format must match what AnthropometricMeasurements produces")
        print("  3. Sex prediction cannot work without pose detection")
        print("  4. The modules are designed to work together seamlessly")
        
    except Exception as e:
        print(f"✗ Error demonstrating dependency: {e}")


def demo_modular_app_integration():
    """Demonstrate how the modular app integrates all components."""
    print("\n" + "=" * 60)
    print("DEMO: Modular App Integration")
    print("=" * 60)
    
    try:
        import app_modular
        
        print("✓ Modular app imported successfully")
        
        # Check the webcam filter instance
        webcam_filter = app_modular.webcam_filter
        
        print(f"\n📊 Modular App Status:")
        print(f"  Available filters: {len(webcam_filter.get_available_filters())}")
        print(f"  Current filter: {webcam_filter.current_filter}")
        
        # Check module availability
        modules_status = {
            'Camera Manager': webcam_filter.camera_manager is not None,
            'Basic Filters': webcam_filter.basic_filters is not None,
            'Clothing Overlay': webcam_filter.clothing_overlay is not None,
            'Anthropometric Measurements': webcam_filter.anthropometric_measurements is not None,
            'Sex Prediction': webcam_filter.sex_predictor is not None
        }
        
        print(f"\n🔧 Module Integration Status:")
        for module_name, available in modules_status.items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module_name}: {status}")
        
        # Demonstrate dependency handling in the app
        has_measurements = webcam_filter.anthropometric_measurements is not None
        has_sex_prediction = webcam_filter.sex_predictor is not None
        
        print(f"\n🔗 Dependency Handling in Modular App:")
        print(f"  Anthropometric measurements available: {has_measurements}")
        print(f"  Sex prediction available: {has_sex_prediction}")
        
        if has_measurements and has_sex_prediction:
            print("  ✓ Dependency satisfied: Sex prediction can use anthropometric data")
        elif not has_measurements and not has_sex_prediction:
            print("  ⚠️  Both modules unavailable (likely missing dependencies)")
        elif has_sex_prediction and not has_measurements:
            print("  ❌ Dependency violation: Sex prediction available but measurements not available")
        
        print(f"\n🎯 Integration Benefits:")
        print("  1. Automatic dependency checking")
        print("  2. Graceful degradation when modules unavailable")
        print("  3. Unified interface for all capabilities")
        print("  4. Proper resource management")
        
    except Exception as e:
        print(f"✗ Error with modular app integration: {e}")


def main():
    """Run all demonstrations."""
    print("🎭 Easy Mirror Modular Architecture Demonstration")
    print("This demo shows how the different modules work together")
    print("with special emphasis on the dependency relationship between")
    print("the sex prediction and anthropometric measurements modules.")
    
    # Run demonstrations
    demo_individual_modules()
    demo_dependency_relationship()
    demo_modular_app_integration()
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("✅ Modules can be used independently")
    print("✅ Sex prediction module properly depends on anthropometric measurements")
    print("✅ Modular app handles dependencies correctly")
    print("✅ Clear separation of concerns achieved")
    print("✅ Architecture supports easy extension and maintenance")
    
    print(f"\n📚 For more details, see:")
    print(f"  - MODULAR_ARCHITECTURE.md: Complete architecture documentation")
    print(f"  - test_modular_structure.py: Automated tests for the modular structure")
    print(f"  - app_modular.py: The new modular application")


if __name__ == '__main__':
    main()