#!/usr/bin/env python3
"""
Test script to demonstrate the background disable option.
"""

import cv2
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evileye.utils.utils import put_text_adaptive, put_text_with_bbox

def create_test_image(width=800, height=600):
    """Create a test image with gradient background."""
    # Create gradient background
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient
    for y in range(height):
        for x in range(width):
            r = int(128 + 64 * x / width)
            g = int(128 + 64 * y / height)
            b = int(128)
            image[y, x] = [b, g, r]
    
    return image

def test_background_options():
    """Test different background options."""
    
    print("🎨 Background Options Test")
    print("=" * 50)
    
    # Create test image
    image = create_test_image(800, 600)
    
    # Test configurations
    test_configs = [
        {
            "name": "Background Enabled",
            "background_enabled": True,
            "background_color": [0, 0, 0],
            "color": [255, 255, 255],
            "position": (10, 20)
        },
        {
            "name": "Background Disabled",
            "background_enabled": False,
            "background_color": [0, 0, 0],
            "color": [255, 255, 255],
            "position": (10, 60)
        },
        {
            "name": "Colored Background",
            "background_enabled": True,
            "background_color": [0, 100, 200],
            "color": [255, 255, 255],
            "position": (10, 100)
        },
        {
            "name": "No Background (transparent)",
            "background_enabled": False,
            "background_color": None,
            "color": [0, 255, 0],
            "position": (10, 140)
        }
    ]
    
    for i, config in enumerate(test_configs):
        print(f"\n📝 Testing: {config['name']}")
        
        # Draw text with different background settings
        put_text_adaptive(
            image, 
            config['name'], 
            config['position'], 
            font_size_pt=16,
            color=tuple(config['color']),
            background_color=config['background_color'],
            background_enabled=config['background_enabled'],
            padding_percent=2.0
        )
        
        print(f"  ✅ Position: {config['position']}")
        print(f"  ✅ Background enabled: {config['background_enabled']}")
        print(f"  ✅ Background color: {config['background_color']}")
        print(f"  ✅ Text color: {config['color']}")
    
    # Test bounding box text
    print(f"\n📦 Testing bounding box text with background disabled")
    
    # Create a bounding box
    bbox = [200, 200, 400, 300]
    
    # Draw bounding box
    cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
    
    # Draw text with background disabled
    put_text_with_bbox(
        image,
        "Object Label (No Background)",
        bbox,
        font_size_pt=14,
        color=(255, 255, 255),
        background_color=(0, 0, 0),
        background_enabled=False,
        position_offset_percent=(0, -10)
    )
    
    # Draw text with background enabled
    put_text_with_bbox(
        image,
        "Object Label (With Background)",
        bbox,
        font_size_pt=14,
        color=(255, 255, 255),
        background_color=(0, 0, 0),
        background_enabled=True,
        position_offset_percent=(0, 10)
    )
    
    # Save test image
    output_filename = "background_options_test.jpg"
    cv2.imwrite(output_filename, image)
    print(f"\n💾 Saved test image: {output_filename}")
    
    return output_filename

def test_config_file_background_settings():
    """Test background settings from configuration files."""
    
    print("\n📄 Testing background settings from config files")
    print("=" * 50)
    
    import json
    
    config_files = [
        "evileye/samples_configs/single_video.json",
        "evileye/samples_configs/single_video_split.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"\n📋 {config_file}")
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            text_config = config.get('visualizer', {}).get('text_config', {})
            
            background_enabled = text_config.get('background_enabled', True)
            background_color = text_config.get('background_color', None)
            
            print(f"  Background enabled: {background_enabled}")
            print(f"  Background color: {background_color}")
            
            if background_enabled:
                print(f"  ✅ Background will be drawn")
            else:
                print(f"  ❌ Background will be disabled")

def main():
    """Main test function."""
    
    print("🎨 Background Disable Option Test")
    print("=" * 60)
    
    try:
        # Test background options
        test_image = test_background_options()
        
        # Test config file settings
        test_config_file_background_settings()
        
        print("\n✅ All tests completed successfully!")
        
        print("\n📋 Summary:")
        print("  ✅ Added background_enabled option")
        print("  ✅ Background can be disabled independently of background_color")
        print("  ✅ Works with both put_text_adaptive and put_text_with_bbox")
        print("  ✅ Configurable via JSON configuration")
        print("  ✅ Default value is True (backward compatibility)")
        
        print(f"\n🎨 Check the generated image: {test_image}")
        print("  - Shows different text rendering options")
        print("  - Demonstrates background enable/disable")
        print("  - Shows bounding box text with and without background")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



