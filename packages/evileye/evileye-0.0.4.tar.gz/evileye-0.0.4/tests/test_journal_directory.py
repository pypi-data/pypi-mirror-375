#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_directory_behavior():
    """Test journal behavior with different directory scenarios"""
    
    print("=== Testing Journal Directory Behavior ===")
    
    # Test 1: Directory exists
    print("\n1. Directory exists (EvilEyeData):")
    if os.path.exists('EvilEyeData'):
        print("   ✅ EvilEyeData directory exists")
        print("   ✅ Journal should be created")
        print("   ✅ Button should be enabled")
    else:
        print("   ❌ EvilEyeData directory does not exist")
        print("   ❌ Journal should not be created")
        print("   ❌ Button should be disabled")
    
    # Test 2: Non-existent directory
    test_dir = '/non/existent/path'
    print(f"\n2. Non-existent directory ({test_dir}):")
    if os.path.exists(test_dir):
        print("   ❌ Directory exists (unexpected)")
    else:
        print("   ✅ Directory does not exist")
        print("   ✅ Journal should not be created")
        print("   ✅ Button should be disabled")
    
    # Test 3: Check current config
    print("\n3. Current config analysis:")
    try:
        import json
        with open('configs/pipeline_capture.json', 'r') as f:
            config = json.load(f)
        
        use_database = config.get('controller', {}).get('use_database', True)
        image_dir = config.get('database', {}).get('image_dir', 'EvilEyeData')
        
        print(f"   use_database: {use_database}")
        print(f"   image_dir: {image_dir}")
        print(f"   image_dir exists: {os.path.exists(image_dir)}")
        
        if not use_database:
            if os.path.exists(image_dir):
                print("   ✅ JSON journal should work")
            else:
                print("   ❌ JSON journal should be disabled")
        else:
            print("   ℹ️  Database journal should be used")
            
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
    
    print("\n=== Expected behavior ===")
    print("1. use_database=true: Always try to create DB journal")
    print("2. use_database=false + directory exists: Create JSON journal")
    print("3. use_database=false + directory missing: Disable journal button")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_journal_directory_behavior()



