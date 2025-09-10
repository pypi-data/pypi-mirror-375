#!/usr/bin/env python3
"""
Test script for the new text rendering system.
Demonstrates adaptive text positioning and sizing.
"""

import cv2
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evileye.utils.utils import (
    put_text_adaptive, 
    put_text_with_bbox, 
    get_default_text_config,
    apply_text_config,
    pt_to_pixels,
    percent_to_pixels
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

def test_text_rendering():
    """Test different text rendering scenarios."""
    
    print("🎨 Testing Text Rendering System")
    print("=" * 50)
    
    # Test different image resolutions
    resolutions = [
        (640, 480),    # VGA
        (1280, 720),   # HD
        (1920, 1080),  # Full HD
        (3840, 2160)   # 4K
    ]
    
    for width, height in resolutions:
        print(f"\n📐 Testing resolution: {width}x{height}")
        
        # Create test image
        image = create_test_image(width, height)
        
        # Test 1: Adaptive text positioning
        print("  ✓ Testing adaptive text positioning...")
        
        # Top-left corner (10%, 10%)
        put_text_adaptive(image, f"Top-Left ({width}x{height})", (10, 10), 
                         font_size_pt=16, color=(255, 255, 255), 
                         background_color=(0, 0, 0))
        
        # Top-right corner (90%, 10%)
        put_text_adaptive(image, "Top-Right", (90, 10), 
                         font_size_pt=14, color=(255, 255, 255), 
                         background_color=(0, 0, 0))
        
        # Bottom-left corner (10%, 90%)
        put_text_adaptive(image, "Bottom-Left", (10, 90), 
                         font_size_pt=12, color=(255, 255, 255), 
                         background_color=(0, 0, 0))
        
        # Bottom-right corner (90%, 90%)
        put_text_adaptive(image, "Bottom-Right", (90, 90), 
                         font_size_pt=10, color=(255, 255, 255), 
                         background_color=(0, 0, 0))
        
        # Center (50%, 50%)
        put_text_adaptive(image, "Center", (50, 50), 
                         font_size_pt=18, color=(0, 0, 0), 
                         background_color=(255, 255, 255))
        
        # Test 2: Bounding box text
        print("  ✓ Testing bounding box text...")
        
        # Create some test bounding boxes
        bboxes = [
            (width//4, height//4, width//4 + 200, height//4 + 100),  # Top-left area
            (width//2, height//2, width//2 + 200, height//2 + 100),  # Center area
            (3*width//4, 3*height//4, 3*width//4 + 200, 3*height//4 + 100)  # Bottom-right area
        ]
        
        for i, bbox in enumerate(bboxes):
            # Draw bounding box
            cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            
            # Draw text with bbox
            put_text_with_bbox(image, f"Object {i+1}", bbox, 
                              font_size_pt=12, color=(255, 255, 255), 
                              background_color=(0, 0, 0))
        
        # Test 3: Different font sizes
        print("  ✓ Testing different font sizes...")
        
        font_sizes = [8, 12, 16, 20, 24]
        y_positions = [15, 25, 35, 45, 55]
        
        for size, y_pos in zip(font_sizes, y_positions):
            put_text_adaptive(image, f"Size {size}pt", (5, y_pos), 
                             font_size_pt=size, color=(255, 255, 255), 
                             background_color=(0, 0, 0))
        
        # Save test image
        output_filename = f"test_text_rendering_{width}x{height}.jpg"
        cv2.imwrite(output_filename, image)
        print(f"  💾 Saved: {output_filename}")

def test_text_config():
    """Test text configuration system."""
    
    print("\n⚙️  Testing Text Configuration System")
    print("=" * 50)
    
    # Test default configuration
    default_config = get_default_text_config()
    print(f"Default config: {default_config}")
    
    # Test custom configuration
    custom_config = {
        "font_size_pt": 20,
        "color": (0, 255, 0),  # Green
        "background_color": (0, 0, 255),  # Blue background
        "padding_percent": 3.0
    }
    
    merged_config = apply_text_config(custom_config)
    print(f"Custom config: {custom_config}")
    print(f"Merged config: {merged_config}")
    
    # Test point to pixel conversion
    print(f"\n📏 Point to Pixel Conversion:")
    for pt_size in [8, 12, 16, 20, 24]:
        pixels = pt_to_pixels(pt_size)
        print(f"  {pt_size}pt = {pixels}px")
    
    # Test percentage to pixel conversion
    print(f"\n📊 Percentage to Pixel Conversion (1920x1080):")
    for percent in [5, 10, 25, 50, 75, 90, 95]:
        x_px = percent_to_pixels(percent, 1920)
        y_px = percent_to_pixels(percent, 1080)
        print(f"  {percent}% = ({x_px}, {y_px}) pixels")

def test_edge_cases():
    """Test edge cases and error handling."""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 50)
    
    # Test very small image
    small_image = create_test_image(320, 240)
    put_text_adaptive(small_image, "Small Image Test", (50, 50), 
                     font_size_pt=8, color=(255, 255, 255))
    cv2.imwrite("test_small_image.jpg", small_image)
    print("  ✓ Small image test completed")
    
    # Test very large text
    large_image = create_test_image(1920, 1080)
    put_text_adaptive(large_image, "Large Text", (50, 50), 
                     font_size_pt=48, color=(255, 255, 255), 
                     background_color=(0, 0, 0))
    cv2.imwrite("test_large_text.jpg", large_image)
    print("  ✓ Large text test completed")
    
    # Test text that would overflow
    overflow_image = create_test_image(640, 480)
    put_text_adaptive(overflow_image, "This is a very long text that should be handled properly", (90, 10), 
                     font_size_pt=16, color=(255, 255, 255), 
                     background_color=(0, 0, 0))
    cv2.imwrite("test_text_overflow.jpg", overflow_image)
    print("  ✓ Text overflow test completed")

def main():
    """Main test function."""
    
    print("🎨 EvilEye Text Rendering System Test")
    print("=" * 60)
    
    try:
        # Run all tests
        test_text_rendering()
        test_text_config()
        test_edge_cases()
        
        print("\n✅ All tests completed successfully!")
        print("\n📁 Generated test images:")
        print("  - test_text_rendering_*.jpg (different resolutions)")
        print("  - test_small_image.jpg")
        print("  - test_large_text.jpg")
        print("  - test_text_overflow.jpg")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



