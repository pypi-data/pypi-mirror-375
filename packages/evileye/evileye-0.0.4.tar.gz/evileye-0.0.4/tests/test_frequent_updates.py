#!/usr/bin/env python3

import sys
import os
import time
import json
import datetime
sys.path.append('.')

def test_frequent_updates():
    """Test frequent updates of JSON files"""
    
    print("=== Test Frequent Updates ===")
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        
        # Create test directory
        base_dir = 'EvilEyeData'
        today = datetime.date.today().strftime('%Y_%m_%d')
        test_dir = os.path.join(base_dir, 'images', today)
        os.makedirs(test_dir, exist_ok=True)
        
        # Create labeling manager
        labeling_manager = LabelingManager(base_dir=base_dir, cameras_params=[])
        
        print(f"✅ Created labeling manager")
        print(f"   Buffer size: {labeling_manager.buffer_size}")
        print(f"   Save interval: {labeling_manager.save_interval} seconds")
        
        # Test object data
        test_object = {
            "object_id": 999,
            "frame_id": 999,
            "timestamp": datetime.datetime.now().isoformat(),
            "image_filename": "detected_frames/test_frame.jpeg",
            "bounding_box": {
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 200
            },
            "confidence": 0.95,
            "class_id": 0,
            "class_name": "person",
            "source_id": 0,
            "source_name": "Cam1",
            "track_id": 999,
            "global_id": None
        }
        
        print("\n🧪 Testing Frequent Updates:")
        print("   - Adding objects to buffer")
        print("   - Checking if files update more frequently")
        
        # Add objects and monitor file changes
        for i in range(10):
            # Update object ID
            test_object["object_id"] = 1000 + i
            test_object["timestamp"] = datetime.datetime.now().isoformat()
            
            # Add to buffer
            labeling_manager.add_object_found(test_object)
            
            print(f"   ✅ Added object {1000 + i}")
            
            # Check if file was updated
            found_file = labeling_manager.found_labels_file
            if os.path.exists(found_file):
                stat = os.stat(found_file)
                print(f"      File last modified: {datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%H:%M:%S')}")
            
            # Wait a bit
            time.sleep(2)
        
        # Force save
        print("\n   🔄 Forcing buffer flush...")
        labeling_manager.flush_buffers()
        
        # Check final state
        stats = labeling_manager.get_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"   Found objects: {stats['found_objects']}")
        print(f"   Lost objects: {stats['lost_objects']}")
        print(f"   Total objects: {stats['total_objects']}")
        
        # Stop labeling manager
        labeling_manager.stop()
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frequent_updates()

