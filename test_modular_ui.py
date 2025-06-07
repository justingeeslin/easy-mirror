#!/usr/bin/env python3
"""
Test script for the modular UI system.
Demonstrates how each module contributes its own HTML controls.
"""

import sys
import os
sys.path.append('.')

from modules.ui_manager import UIManager
from modules.filters.basic_filters import BasicFilters
from modules.filters.clothing_overlay import ClothingOverlay
from modules.anthropometric.measurements import AnthropometricMeasurements
from modules.prediction.sex_prediction import SexPredictor


def test_modular_ui():
    """Test the modular UI system."""
    print("🧪 Testing Modular UI System")
    print("=" * 50)
    
    # Initialize UI manager
    ui_manager = UIManager()
    
    # Initialize modules
    print("📦 Initializing modules...")
    
    try:
        basic_filters = BasicFilters()
        ui_manager.register_module('basic_filters', basic_filters)
        print("✅ Basic Filters module registered")
    except Exception as e:
        print(f"❌ Basic Filters failed: {e}")
    
    try:
        clothing_overlay = ClothingOverlay()
        ui_manager.register_module('clothing', clothing_overlay)
        print("✅ Clothing Overlay module registered")
    except Exception as e:
        print(f"❌ Clothing Overlay failed: {e}")
    
    try:
        measurements = AnthropometricMeasurements()
        ui_manager.register_module('anthropometric', measurements)
        print("✅ Anthropometric Measurements module registered")
    except Exception as e:
        print(f"❌ Anthropometric Measurements failed: {e}")
    
    try:
        sex_predictor = SexPredictor()
        ui_manager.register_module('sex_prediction', sex_predictor, dependencies=['anthropometric'])
        print("✅ Sex Prediction module registered (depends on anthropometric)")
    except Exception as e:
        print(f"❌ Sex Prediction failed: {e}")
    
    print(f"\n📊 Total modules registered: {len(ui_manager.get_available_modules())}")
    
    # Test module info
    print("\n🔍 Module Information:")
    module_info = ui_manager.get_module_info()
    for name, info in module_info.items():
        status = "✅" if info['dependencies_met'] else "⚠️"
        deps = ", ".join(info['dependencies']) if info['dependencies'] else "None"
        print(f"  {status} {name} ({info['class']}) - Dependencies: {deps}")
    
    # Test UI generation
    print("\n🎨 Testing UI Generation:")
    
    try:
        html = ui_manager.generate_combined_html()
        print(f"✅ HTML generated ({len(html)} characters)")
        
        # Count module sections
        module_sections = html.count('class="module-section"')
        print(f"   📄 Found {module_sections} module sections")
        
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
    
    try:
        css = ui_manager.generate_combined_css()
        print(f"✅ CSS generated ({len(css)} characters)")
        
        # Count CSS rules
        css_rules = css.count('{')
        print(f"   🎨 Found ~{css_rules} CSS rules")
        
    except Exception as e:
        print(f"❌ CSS generation failed: {e}")
    
    try:
        js = ui_manager.generate_combined_javascript()
        print(f"✅ JavaScript generated ({len(js)} characters)")
        
        # Count functions
        js_functions = js.count('function ')
        print(f"   ⚙️ Found ~{js_functions} JavaScript functions")
        
    except Exception as e:
        print(f"❌ JavaScript generation failed: {e}")
    
    # Test dependency checking
    print("\n🔗 Testing Dependency System:")
    for module_name in ui_manager.get_available_modules():
        deps_met = ui_manager.check_dependencies(module_name)
        status = "✅" if deps_met else "❌"
        print(f"  {status} {module_name} dependencies satisfied: {deps_met}")
    
    # Generate sample output files for inspection
    print("\n📁 Generating sample output files:")
    
    try:
        with open('/tmp/modular_ui_sample.html', 'w') as f:
            f.write(f'''<!DOCTYPE html>
<html>
<head>
    <title>Modular UI Sample</title>
    <style>
{ui_manager.generate_combined_css()}
    </style>
</head>
<body>
{ui_manager.generate_combined_html()}
    <script>
{ui_manager.generate_combined_javascript()}
    </script>
</body>
</html>''')
        print("✅ Sample HTML file: /tmp/modular_ui_sample.html")
    except Exception as e:
        print(f"❌ Failed to create sample file: {e}")
    
    print("\n🎉 Modular UI Test Complete!")
    print("\nKey Features Demonstrated:")
    print("  🎨 Each module contributes its own UI controls")
    print("  🔗 Dependency system ensures proper module relationships")
    print("  📦 UI Manager combines all components seamlessly")
    print("  🧬 Sex prediction UI shows dependency warning when needed")
    print("  🎛️ Filters, measurements, and clothing all have dedicated interfaces")
    
    return ui_manager


if __name__ == "__main__":
    test_modular_ui()