#!/usr/bin/env python3

import sys
import os
import time
import json
import datetime
import threading
sys.path.append('.')

def test_journal_updates_when_open():
    """Test journal updates when window is open"""
    
    print("=== Test Journal Updates When Open ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        import cv2
        import numpy as np
        
        # Create a simple test application
        app = QApplication([])
        
        # Create test directory structure
        base_dir = 'EvilEyeData'
        today = datetime.date.today().strftime('%Y_%m_%d')
        test_images_dir = os.path.join(base_dir, 'images', today)
        os.makedirs(test_images_dir, exist_ok=True)
        
        # Create test JSON data
        test_json_path = os.path.join(test_images_dir, 'objects_found.json')
        
        def create_test_data(object_id, timestamp):
            """Create test data with given object_id and timestamp"""
            return {
                "metadata": {
                    "version": "1.0",
                    "created": timestamp,
                    "description": "Test data",
                    "total_objects": 1
                },
                "objects": [
                    {
                        "object_id": object_id,
                        "frame_id": object_id,
                        "timestamp": timestamp,
                        "image_filename": f"detected_previews/test_preview_{object_id}.jpeg",
                        "bounding_box": {
                            "x": 50,
                            "y": 30,
                            "width": 200,
                            "height": 90
                        },
                        "class_id": 0,
                        "class_name": "person",
                        "confidence": 0.85,
                        "source_id": 0,
                        "source_name": "Cam1",
                        "date_folder": today
                    }
                ]
            }
        
        # Create initial test data
        initial_data = create_test_data(1, datetime.datetime.now().isoformat())
        with open(test_json_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        print(f"✅ Created initial test data: {test_json_path}")
        
        # Create EventsJournalJson widget
        journal = EventsJournalJson(base_dir)
        journal.show()
        
        print("\n🧪 Testing Journal Updates When Open:")
        print("   - Journal window should be visible")
        print("   - Timer should be active")
        print("   - New objects will be added every 3 seconds")
        print("   - Journal should update automatically")
        print("   - Press Ctrl+C to exit this test")
        
        # Function to add new objects
        def add_new_object():
            object_id = 100
            while True:
                try:
                    time.sleep(3)  # Wait 3 seconds
                    
                    # Create new object data
                    new_data = create_test_data(object_id, datetime.datetime.now().isoformat())
                    
                    # Read existing data
                    try:
                        with open(test_json_path, 'r') as f:
                            existing_data = json.load(f)
                    except FileNotFoundError:
                        existing_data = {"metadata": {}, "objects": []}
                    
                    # Add new object to existing data
                    existing_data["objects"].extend(new_data["objects"])
                    existing_data["metadata"]["total_objects"] = len(existing_data["objects"])
                    existing_data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
                    
                    # Write updated data
                    with open(test_json_path, 'w') as f:
                        json.dump(existing_data, f, indent=2)
                    
                    print(f"✅ Added new object {object_id} at {datetime.datetime.now().strftime('%H:%M:%S')}")
                    object_id += 1
                    
                except Exception as e:
                    print(f"❌ Error adding new object: {e}")
                    break
        
        # Start background thread to add objects
        update_thread = threading.Thread(target=add_new_object, daemon=True)
        update_thread.start()
        
        # Set up a timer to check if updates are working
        def check_updates():
            row_count = journal.table.rowCount()
            print(f"📊 Current table rows: {row_count}")
            
            # Check if timer is running
            if hasattr(journal, 'update_timer') and journal.update_timer.isActive():
                print("✅ Update timer is active")
            else:
                print("❌ Update timer is not active")
        
        timer = QTimer()
        timer.timeout.connect(check_updates)
        timer.start(6000)  # Check every 6 seconds
        
        # Run the application
        app.exec()
        
    except KeyboardInterrupt:
        print("\n✅ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_updates_when_open()

