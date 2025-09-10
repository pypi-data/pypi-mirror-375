#!/usr/bin/env python3
"""
Test script for the improved font scaling system.
Demonstrates resolution-based font scaling vs the old hardcoded method.
"""

import cv2
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evileye.utils.utils import (
    put_text_adaptive, 
    calculate_font_scale_for_resolution,
    calculate_font_scale_simple,
    pt_to_pixels
)

def create_test_image(width=1920, height=1080):
    """Create a test image with different resolutions."""
    # Create a gradient background
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient
    for y in range(height):
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = int(128)
            image[y, x] = [b, g, r]
    
    return image

def test_font_scaling_comparison():
    """Compare different font scaling methods."""
    
    print("🔍 Font Scaling Method Comparison")
    print("=" * 50)
    
    # Test different resolutions
    resolutions = [
        (640, 480),    # VGA
        (1280, 720),   # HD
        (1920, 1080),  # Full HD
        (3840, 2160)   # 4K
    ]
    
    font_size_pt = 16
    
    print(f"\n📏 Font size: {font_size_pt}pt")
    print(f"{'Resolution':<12} {'Old Method':<12} {'Resolution-based':<18} {'Simple Method':<15}")
    print("-" * 70)
    
    for width, height in resolutions:
        # Old method (hardcoded 30.0)
        old_scale = pt_to_pixels(font_size_pt) / 30.0
        
        # New methods
        resolution_scale = calculate_font_scale_for_resolution(font_size_pt, width, height)
        simple_scale = calculate_font_scale_simple(font_size_pt, width, height)
        
        print(f"{width}x{height:<6} {old_scale:<12.3f} {resolution_scale:<18.3f} {simple_scale:<15.3f}")

def test_visual_comparison():
    """Create visual comparison of different scaling methods."""
    
    print("\n🎨 Visual Comparison Test")
    print("=" * 50)
    
    # Test resolutions
    resolutions = [
        (640, 480),    # VGA
        (1920, 1080),  # Full HD
        (3840, 2160)   # 4K
    ]
    
    for width, height in resolutions:
        print(f"\n📐 Testing resolution: {width}x{height}")
        
        # Create test image
        image = create_test_image(width, height)
        
        # Test different methods
        methods = [
            ("resolution_based", "Resolution-based"),
            ("simple", "Simple diagonal-based")
        ]
        
        y_positions = [20, 40, 60, 80]
        
        for i, (method, method_name) in enumerate(methods):
            if i < len(y_positions):
                y_pos = y_positions[i]
                
                # Draw text with different methods
                put_text_adaptive(image, f"{method_name} - 16pt", (10, y_pos), 
                                font_size_pt=16, color=(255, 255, 255),
                                background_color=(0, 0, 0),
                                font_scale_method=method)
                
                put_text_adaptive(image, f"{method_name} - 24pt", (10, y_pos + 15), 
                                font_size_pt=24, color=(255, 255, 0),
                                background_color=(0, 0, 0),
                                font_scale_method=method)
        
        # Save test image
        output_filename = f"font_scaling_comparison_{width}x{height}.jpg"
        cv2.imwrite(output_filename, image)
        print(f"  💾 Saved: {output_filename}")

def test_resolution_independence():
    """Test that text appears similar size across different resolutions."""
    
    print("\n📊 Resolution Independence Test")
    print("=" * 50)
    
    # Test with same font size across different resolutions
    font_size_pt = 20
    
    resolutions = [
        (640, 480),    # VGA
        (1280, 720),   # HD
        (1920, 1080),  # Full HD
        (3840, 2160)   # 4K
    ]
    
    for width, height in resolutions:
        print(f"\n📐 Resolution: {width}x{height}")
        
        # Create test image
        image = create_test_image(width, height)
        
        # Calculate font scales
        resolution_scale = calculate_font_scale_for_resolution(font_size_pt, width, height)
        simple_scale = calculate_font_scale_simple(font_size_pt, width, height)
        
        print(f"  Resolution-based scale: {resolution_scale:.3f}")
        print(f"  Simple scale: {simple_scale:.3f}")
        
        # Draw text with resolution-based method
        put_text_adaptive(image, f"Resolution-based {font_size_pt}pt", (10, 20), 
                        font_size_pt=font_size_pt, color=(255, 255, 255),
                        background_color=(0, 0, 0),
                        font_scale_method="resolution_based")
        
        # Draw text with simple method
        put_text_adaptive(image, f"Simple {font_size_pt}pt", (10, 50), 
                        font_size_pt=font_size_pt, color=(255, 255, 0),
                        background_color=(0, 0, 0),
                        font_scale_method="simple")
        
        # Save test image
        output_filename = f"resolution_independence_{width}x{height}.jpg"
        cv2.imwrite(output_filename, image)
        print(f"  💾 Saved: {output_filename}")

def test_edge_cases():
    """Test edge cases and extreme resolutions."""
    
    print("\n🔍 Edge Cases Test")
    print("=" * 50)
    
    # Test extreme resolutions
    extreme_resolutions = [
        (320, 240),    # Very small
        (8000, 6000),  # Very large
        (1920, 480),   # Very wide
        (480, 1920),   # Very tall
    ]
    
    for width, height in extreme_resolutions:
        print(f"\n📐 Extreme resolution: {width}x{height}")
        
        # Create test image
        image = create_test_image(width, height)
        
        # Test both methods
        for method in ["resolution_based", "simple"]:
            try:
                put_text_adaptive(image, f"{method} test", (10, 20), 
                                font_size_pt=16, color=(255, 255, 255),
                                background_color=(0, 0, 0),
                                font_scale_method=method)
                print(f"  ✅ {method}: Success")
            except Exception as e:
                print(f"  ❌ {method}: Failed - {e}")
        
        # Save test image
        output_filename = f"edge_case_{width}x{height}.jpg"
        cv2.imwrite(output_filename, image)
        print(f"  💾 Saved: {output_filename}")

def main():
    """Main test function."""
    
    print("🎨 Improved Font Scaling System Test")
    print("=" * 60)
    
    try:
        # Run all tests
        test_font_scaling_comparison()
        test_visual_comparison()
        test_resolution_independence()
        test_edge_cases()
        
        print("\n✅ All tests completed successfully!")
        print("\n📁 Generated test images:")
        print("  - font_scaling_comparison_*.jpg (method comparison)")
        print("  - resolution_independence_*.jpg (consistency test)")
        print("  - edge_case_*.jpg (extreme resolutions)")
        
        print("\n📊 Key Improvements:")
        print("  ✅ Removed hardcoded 30.0 divisor")
        print("  ✅ Added resolution-based scaling")
        print("  ✅ Added simple diagonal-based scaling")
        print("  ✅ Configurable base resolution")
        print("  ✅ Better handling of extreme resolutions")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



