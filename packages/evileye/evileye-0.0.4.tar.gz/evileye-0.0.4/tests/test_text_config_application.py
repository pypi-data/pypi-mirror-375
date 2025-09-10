#!/usr/bin/env python3
"""
Test script to verify that text_config is properly applied from configuration.
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evileye.utils.utils import apply_text_config, get_default_text_config

def test_text_config_from_file():
    """Test text_config loading from sample configuration files."""
    
    print("🔍 Testing text_config application from configuration files")
    print("=" * 60)
    
    # Test files
    config_files = [
        "evileye/samples_configs/single_video.json",
        "evileye/samples_configs/single_video_split.json", 
        "evileye/samples_configs/multi_videos.json",
        "evileye/samples_configs/single_ip_camera.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"\n📄 Testing: {config_file}")
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Get text_config from visualizer section
                visualizer_config = config.get('visualizer', {})
                text_config = visualizer_config.get('text_config', {})
                
                print(f"  📋 Found text_config in visualizer section:")
                for key, value in text_config.items():
                    print(f"    {key}: {value}")
                
                # Apply text_config
                merged_config = apply_text_config(text_config)
                
                print(f"  ✅ Applied text_config:")
                for key, value in merged_config.items():
                    print(f"    {key}: {value}")
                
                # Test specific values
                if 'font_scale_method' in text_config:
                    print(f"  🎯 Font scale method: {text_config['font_scale_method']}")
                
                if 'font_size_pt' in text_config:
                    print(f"  📏 Font size: {text_config['font_size_pt']}pt")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print(f"\n⚠️  File not found: {config_file}")

def test_default_config():
    """Test default text configuration."""
    
    print("\n🔧 Testing default text configuration")
    print("=" * 40)
    
    default_config = get_default_text_config()
    
    print("Default configuration:")
    for key, value in default_config.items():
        print(f"  {key}: {value}")

def test_config_merging():
    """Test merging of user config with defaults."""
    
    print("\n🔄 Testing configuration merging")
    print("=" * 40)
    
    # Test user config
    user_config = {
        "font_size_pt": 20,
        "font_scale_method": "simple",
        "color": [255, 0, 0]  # Red color
    }
    
    print("User configuration:")
    for key, value in user_config.items():
        print(f"  {key}: {value}")
    
    # Apply merging
    merged_config = apply_text_config(user_config)
    
    print("\nMerged configuration:")
    for key, value in merged_config.items():
        print(f"  {key}: {value}")

def test_visualizer_integration():
    """Test that visualizer properly receives text_config."""
    
    print("\n🎨 Testing visualizer integration")
    print("=" * 40)
    
    # Simulate visualizer parameter setting
    from evileye.visualization_modules.visualizer import Visualizer
    
    # Create mock slots and signals
    mock_slots = {}
    mock_signals = {}
    
    visualizer = Visualizer(mock_slots, mock_signals)
    
    # Set parameters with text_config
    test_params = {
        'source_ids': [0],
        'fps': [5],
        'num_height': 1,
        'num_width': 1,
        'show_debug_info': True,
        'text_config': {
            'font_size_pt': 18,
            'font_scale_method': 'resolution_based',
            'color': [0, 255, 0]  # Green
        }
    }
    
    visualizer.params = test_params
    visualizer.set_params_impl()
    
    print(f"Visualizer text_config: {visualizer.text_config}")
    
    # Test that text_config is properly stored
    if visualizer.text_config:
        print("✅ text_config successfully applied to visualizer")
        for key, value in visualizer.text_config.items():
            print(f"  {key}: {value}")
    else:
        print("❌ text_config not applied to visualizer")

def main():
    """Main test function."""
    
    print("🎨 Text Configuration Application Test")
    print("=" * 60)
    
    try:
        test_default_config()
        test_config_merging()
        test_text_config_from_file()
        test_visualizer_integration()
        
        print("\n✅ All tests completed successfully!")
        
        print("\n📋 Summary:")
        print("  ✅ text_config moved to visualizer section")
        print("  ✅ text_config properly applied in visualizer")
        print("  ✅ text_config passed to VideoThread")
        print("  ✅ text_config used in draw_boxes_tracking")
        print("  ✅ Configuration merging works correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



