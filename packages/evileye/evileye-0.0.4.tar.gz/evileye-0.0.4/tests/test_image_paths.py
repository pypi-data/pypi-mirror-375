#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_image_paths():
    """Test image paths in journal"""
    
    print("=== Test Image Paths ===")
    
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        ds = JsonLabelJournalDataSource('EvilEyeData')
        
        # Get sample data
        events = ds.fetch(0, 5, {}, [])
        
        print(f"\n📊 Image Paths Test:")
        for i, ev in enumerate(events):
            print(f"   Event {i+1}:")
            print(f"     Type: {ev.get('event_type')}")
            print(f"     Object ID: {ev.get('object_id')}")
            print(f"     Image filename: {ev.get('image_filename')}")
            print(f"     Date folder: {ev.get('date_folder')}")
            
            # Test full path
            if ev.get('image_filename') and ev.get('date_folder'):
                full_path = os.path.join('EvilEyeData', 'images', ev.get('date_folder'), ev.get('image_filename'))
                exists = os.path.exists(full_path)
                print(f"     Full path: {full_path}")
                print(f"     Exists: {exists}")
                
                # Check if directory exists
                dir_path = os.path.join('EvilEyeData', 'images', ev.get('date_folder'))
                dir_exists = os.path.exists(dir_path)
                print(f"     Directory exists: {dir_exists}")
                
                if dir_exists:
                    # List files in directory
                    try:
                        files = os.listdir(dir_path)
                        print(f"     Files in directory: {len(files)}")
                        if len(files) > 0:
                            print(f"     Sample files: {files[:3]}")
                    except Exception as e:
                        print(f"     Error listing directory: {e}")
        
        ds.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_paths()

