#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_data_flow():
    """Test data flow in the system"""
    
    print("=== Test Data Flow ===")
    
    try:
        # Check if objects_handler is being called
        print("🔍 Checking if objects_handler is being called...")
        
        # Check if there are any active objects in the system
        from evileye.objects_handler.objects_handler import ObjectsHandler
        
        # Create a simple objects handler
        handler = ObjectsHandler(db_controller=None, db_adapter=None)
        
        print(f"✅ ObjectsHandler created")
        print(f"📊 Active objects: {len(handler.active_objs.objects)}")
        print(f"📊 Lost objects: {len(handler.lost_objs.objects)}")
        
        # Check if labeling manager is initialized
        if hasattr(handler, 'labeling_manager'):
            print(f"✅ Labeling manager initialized")
            print(f"📊 Found buffer size: {len(handler.labeling_manager.found_buffer)}")
            print(f"📊 Lost buffer size: {len(handler.labeling_manager.lost_buffer)}")
        else:
            print("❌ Labeling manager not initialized")
            
        # Check if there are any recent files
        import glob
        recent_files = glob.glob("EvilEyeData/images/2025_09_01/detected_frames/*.jpeg")
        print(f"📁 Recent detected frames: {len(recent_files)}")
        
        if recent_files:
            print("📋 Recent files:")
            for f in recent_files[-3:]:  # Show last 3 files
                print(f"  {os.path.basename(f)}")
        
        # Check if objects are being detected but not saved
        print("\n🔍 Checking detection results...")
        
        # Try to read the current JSON files
        found_file = "EvilEyeData/images/2025_09_01/objects_found.json"
        lost_file = "EvilEyeData/images/2025_09_01/objects_lost.json"
        
        if os.path.exists(found_file):
            import json
            with open(found_file, 'r') as f:
                found_data = json.load(f)
            print(f"📊 Found objects in JSON: {found_data['metadata']['total_objects']}")
        else:
            print("❌ Found objects JSON file not found")
            
        if os.path.exists(lost_file):
            import json
            with open(lost_file, 'r') as f:
                lost_data = json.load(f)
            print(f"📊 Lost objects in JSON: {lost_data['metadata']['total_objects']}")
        else:
            print("❌ Lost objects JSON file not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_flow()
