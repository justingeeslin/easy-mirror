#!/usr/bin/env python3
"""
Test script to analyze clothing in provided images using the ClothingAnalyzer.
"""

import cv2
import numpy as np
import json
import sys
import os
from PIL import Image
import requests
from io import BytesIO

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from clothing_analysis import ClothingAnalyzer
    CLOTHING_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing ClothingAnalyzer: {e}")
    CLOTHING_ANALYSIS_AVAILABLE = False
    sys.exit(1)

def download_image_from_data_url(data_url, filename):
    """Download image from data URL and save it."""
    try:
        # For now, we'll create placeholder images since we can't directly access the data URLs
        # In a real scenario, you would decode the base64 data from the data URL
        print(f"Note: Creating placeholder for {filename}")
        return None
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return None

def create_test_images():
    """Create test images that simulate the provided images."""
    
    # Image 1: Man in purple/pink t-shirt and blue jeans
    print("Creating test image 1: Man in purple t-shirt and blue jeans")
    img1 = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Background (gray/black)
    img1[:, :] = [40, 40, 40]
    
    # Person silhouette
    # Head
    cv2.circle(img1, (320, 100), 35, (200, 180, 160), -1)
    
    # Torso (purple/pink t-shirt)
    cv2.rectangle(img1, (280, 135), (360, 280), (180, 120, 200), -1)  # Purple-ish shirt
    
    # Arms (shirt sleeves)
    cv2.rectangle(img1, (240, 150), (280, 220), (180, 120, 200), -1)  # Left arm
    cv2.rectangle(img1, (360, 150), (400, 220), (180, 120, 200), -1)  # Right arm
    
    # Legs (blue jeans)
    cv2.rectangle(img1, (290, 280), (320, 450), (120, 80, 40), -1)   # Left leg (blue)
    cv2.rectangle(img1, (320, 280), (350, 450), (120, 80, 40), -1)   # Right leg (blue)
    
    cv2.imwrite('test_images/man_purple_shirt_jeans.jpg', img1)
    
    # Image 2: Woman in black top and gray skirt
    print("Creating test image 2: Woman in black top and gray skirt")
    img2 = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Background (white)
    img2[:, :] = [240, 240, 240]
    
    # Person silhouette
    # Head
    cv2.circle(img2, (320, 80), 30, (200, 180, 160), -1)
    
    # Torso (black top - sleeveless)
    cv2.rectangle(img2, (290, 110), (350, 220), (20, 20, 20), -1)  # Black top
    
    # Arms (bare arms)
    cv2.circle(img2, (270, 140), 12, (200, 180, 160), -1)  # Left arm
    cv2.circle(img2, (370, 140), 12, (200, 180, 160), -1)  # Right arm
    cv2.rectangle(img2, (258, 140), (282, 200), (200, 180, 160), -1)  # Left arm
    cv2.rectangle(img2, (358, 140), (382, 200), (200, 180, 160), -1)  # Right arm
    
    # Skirt (gray)
    cv2.rectangle(img2, (285, 220), (355, 320), (120, 120, 120), -1)  # Gray skirt
    
    # Legs (bare legs)
    cv2.rectangle(img2, (295, 320), (315, 420), (200, 180, 160), -1)   # Left leg
    cv2.rectangle(img2, (325, 320), (345, 420), (200, 180, 160), -1)   # Right leg
    
    # Shoes (black)
    cv2.rectangle(img2, (290, 420), (320, 440), (20, 20, 20), -1)   # Left shoe
    cv2.rectangle(img2, (320, 420), (350, 440), (20, 20, 20), -1)   # Right shoe
    
    cv2.imwrite('test_images/woman_black_top_gray_skirt.jpg', img2)
    
    return ['test_images/man_purple_shirt_jeans.jpg', 'test_images/woman_black_top_gray_skirt.jpg']

def analyze_image(analyzer, image_path, description):
    """Analyze a single image and return results."""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {description}")
    print(f"Image: {image_path}")
    print(f"{'='*60}")
    
    try:
        # Load image
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not load image {image_path}")
            return None
        
        print(f"Image loaded successfully: {frame.shape}")
        
        # Analyze clothing
        analysis = analyzer.analyze_clothing(frame)
        
        if analysis is None:
            print("❌ Analysis failed - no person detected or analysis error")
            return None
        
        print("✅ Analysis completed successfully!")
        
        # Display results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"{'─'*40}")
        
        # Garment type
        garment_type = analysis.get('garment_type', 'unknown')
        print(f"👕 Garment Type: {garment_type.title()}")
        
        # Colors
        colors = analysis.get('colors', {})
        if colors:
            print(f"🎨 Colors:")
            for region, color in colors.items():
                if color != 'unknown':
                    print(f"   • {region}: {color}")
        
        # Materials
        materials = analysis.get('materials', {})
        if materials:
            print(f"🧵 Materials:")
            for region, material in materials.items():
                if material != 'unknown':
                    print(f"   • {region}: {material}")
        
        # Features
        features = analysis.get('features', {})
        if features:
            print(f"✨ Features:")
            for feature, value in features.items():
                print(f"   • {feature}: {value}")
        
        # Embellishments
        embellishments = analysis.get('embellishments', [])
        if embellishments:
            print(f"💎 Embellishments: {', '.join(embellishments)}")
        else:
            print(f"💎 Embellishments: None detected")
        
        # Confidence
        confidence = analysis.get('confidence', 0)
        confidence_percent = round(confidence * 100, 1)
        print(f"📈 Confidence: {confidence_percent}%")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_analyses(analysis1, analysis2, desc1, desc2):
    """Compare two analysis results."""
    print(f"\n{'='*60}")
    print(f"COMPARISON: {desc1} vs {desc2}")
    print(f"{'='*60}")
    
    if not analysis1 or not analysis2:
        print("❌ Cannot compare - one or both analyses failed")
        return
    
    # Compare garment types
    garment1 = analysis1.get('garment_type', 'unknown')
    garment2 = analysis2.get('garment_type', 'unknown')
    print(f"👕 Garment Types:")
    print(f"   • {desc1}: {garment1}")
    print(f"   • {desc2}: {garment2}")
    
    # Compare dominant colors
    colors1 = analysis1.get('colors', {})
    colors2 = analysis2.get('colors', {})
    print(f"\n🎨 Dominant Colors:")
    
    all_regions = set(colors1.keys()) | set(colors2.keys())
    for region in sorted(all_regions):
        color1 = colors1.get(region, 'not detected')
        color2 = colors2.get(region, 'not detected')
        print(f"   • {region}:")
        print(f"     - {desc1}: {color1}")
        print(f"     - {desc2}: {color2}")
    
    # Compare features
    features1 = analysis1.get('features', {})
    features2 = analysis2.get('features', {})
    print(f"\n✨ Features:")
    
    all_features = set(features1.keys()) | set(features2.keys())
    if all_features:
        for feature in sorted(all_features):
            feat1 = features1.get(feature, 'not detected')
            feat2 = features2.get(feature, 'not detected')
            print(f"   • {feature}:")
            print(f"     - {desc1}: {feat1}")
            print(f"     - {desc2}: {feat2}")
    else:
        print("   • No features detected in either image")
    
    # Compare confidence
    conf1 = analysis1.get('confidence', 0) * 100
    conf2 = analysis2.get('confidence', 0) * 100
    print(f"\n📈 Confidence Scores:")
    print(f"   • {desc1}: {conf1:.1f}%")
    print(f"   • {desc2}: {conf2:.1f}%")

def main():
    """Main test function."""
    print("🔍 CLOTHING ANALYZER TEST")
    print("Testing with simulated images based on provided examples")
    print("="*60)
    
    if not CLOTHING_ANALYSIS_AVAILABLE:
        print("❌ ClothingAnalyzer not available")
        return
    
    # Initialize analyzer
    print("🚀 Initializing ClothingAnalyzer...")
    try:
        analyzer = ClothingAnalyzer()
        print("✅ ClothingAnalyzer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize ClothingAnalyzer: {e}")
        return
    
    # Create test images
    print("\n📸 Creating test images...")
    try:
        image_paths = create_test_images()
        print("✅ Test images created successfully")
    except Exception as e:
        print(f"❌ Failed to create test images: {e}")
        return
    
    # Analyze images
    descriptions = [
        "Man in purple t-shirt and blue jeans",
        "Woman in black sleeveless top and gray skirt"
    ]
    
    analyses = []
    for i, (image_path, description) in enumerate(zip(image_paths, descriptions)):
        analysis = analyze_image(analyzer, image_path, description)
        analyses.append(analysis)
    
    # Compare results
    if len(analyses) >= 2:
        compare_analyses(analyses[0], analyses[1], descriptions[0], descriptions[1])
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_analyses = sum(1 for a in analyses if a is not None)
    total_analyses = len(analyses)
    
    print(f"✅ Successful analyses: {successful_analyses}/{total_analyses}")
    
    if successful_analyses > 0:
        print("\n🎯 Key Findings:")
        for i, (analysis, desc) in enumerate(zip(analyses, descriptions)):
            if analysis:
                garment = analysis.get('garment_type', 'unknown')
                confidence = analysis.get('confidence', 0) * 100
                print(f"   • {desc}: {garment} ({confidence:.1f}% confidence)")
    
    print(f"\n📁 Test images saved in: test_images/")
    print("🔬 You can manually inspect the generated images and analysis results")

if __name__ == "__main__":
    main()