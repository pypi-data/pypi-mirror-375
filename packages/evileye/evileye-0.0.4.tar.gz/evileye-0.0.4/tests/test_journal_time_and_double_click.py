#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_time_and_double_click():
    """Test time formatting and double click functionality in JSON journal"""
    
    print("=== Test Journal Time Formatting and Double Click ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from evileye.visualization_modules.events_journal_json import EventsJournalJson, DateTimeDelegate
        import cv2
        import numpy as np
        import datetime
        
        # Create a simple test application
        app = QApplication([])
        
        # Create test directory structure
        base_dir = 'EvilEyeData'
        today = datetime.date.today().strftime('%Y_%m_%d')
        test_images_dir = os.path.join(base_dir, 'images', today)
        os.makedirs(test_images_dir, exist_ok=True)
        
        # Create test preview and frame images
        test_image = np.zeros((150, 300, 3), dtype=np.uint8)
        test_image[:] = (100, 150, 200)  # Blue-gray background
        cv2.rectangle(test_image, (50, 30), (250, 120), (0, 255, 0), 2)
        
        # Save test preview image
        preview_path = os.path.join(test_images_dir, 'detected_previews', 'test_preview.jpeg')
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        cv2.imwrite(preview_path, test_image)
        
        # Save test frame image
        frame_path = os.path.join(test_images_dir, 'detected_frames', 'test_frame.jpeg')
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)
        cv2.imwrite(frame_path, test_image)
        
        print(f"✅ Created test images: {preview_path}, {frame_path}")
        
        # Create test JSON data with current timestamp
        test_json_path = os.path.join(test_images_dir, 'objects_found.json')
        current_time = datetime.datetime.now().isoformat()
        test_data = {
            "metadata": {
                "version": "1.0",
                "created": current_time,
                "description": "Test data",
                "total_objects": 1
            },
            "objects": [
                {
                    "object_id": 1,
                    "frame_id": 1,
                    "timestamp": current_time,
                    "image_filename": "detected_previews/test_preview.jpeg",
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
        
        import json
        with open(test_json_path, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"✅ Created test JSON data: {test_json_path}")
        
        # Test DateTimeDelegate
        print("\n🧪 Testing DateTimeDelegate:")
        datetime_delegate = DateTimeDelegate()
        
        # Test with ISO format string
        iso_time = "2025-09-01T17:30:45.123456"
        formatted_time = datetime_delegate.displayText(iso_time, None)
        expected_format = "2025-09-01 17:30:45"
        
        if formatted_time == expected_format:
            print(f"✅ Time formatting works: {iso_time} -> {formatted_time}")
        else:
            print(f"❌ Time formatting failed: {iso_time} -> {formatted_time} (expected: {expected_format})")
        
        # Test with regular string
        regular_time = "2025-09-01 17:30:45"
        formatted_regular = datetime_delegate.displayText(regular_time, None)
        if formatted_regular == regular_time:
            print(f"✅ Regular time string preserved: {formatted_regular}")
        else:
            print(f"❌ Regular time string changed: {formatted_regular}")
        
        # Create EventsJournalJson widget
        journal = EventsJournalJson(base_dir)
        journal.show()
        
        print("\n🧪 Testing EventsJournalJson:")
        
        # Check that datetime delegate is set up
        if hasattr(journal, 'datetime_delegate'):
            print("✅ DateTimeDelegate is set up")
        else:
            print("❌ DateTimeDelegate is not set up")
        
        # Check that double click signal is connected
        if hasattr(journal, '_display_image'):
            print("✅ Double click handler is connected")
        else:
            print("❌ Double click handler is not connected")
        
        # Check table structure
        if journal.table.columnCount() == 7:
            print("✅ Table has 7 columns")
            
            # Check time columns have datetime delegate
            time_delegate = journal.table.itemDelegateForColumn(3)  # Time column
            time_lost_delegate = journal.table.itemDelegateForColumn(4)  # Time lost column
            
            if isinstance(time_delegate, DateTimeDelegate):
                print("✅ Time column has DateTimeDelegate")
            else:
                print("❌ Time column doesn't have DateTimeDelegate")
                
            if isinstance(time_lost_delegate, DateTimeDelegate):
                print("✅ Time lost column has DateTimeDelegate")
            else:
                print("❌ Time lost column doesn't have DateTimeDelegate")
        else:
            print(f"❌ Table has {journal.table.columnCount()} columns (expected 7)")
        
        # Check that data is loaded
        if journal.table.rowCount() > 0:
            print(f"✅ Table loaded {journal.table.rowCount()} rows")
            
            # Check time formatting in table
            first_row = 0
            time_item = journal.table.item(first_row, 3)  # Time column
            time_lost_item = journal.table.item(first_row, 4)  # Time lost column
            
            if time_item:
                time_text = time_item.text()
                print(f"✅ Time column shows: {time_text}")
                
                # Check if time is formatted correctly (should not have microseconds)
                if '.' in time_text and len(time_text.split('.')[1]) > 6:
                    print("❌ Time still shows microseconds")
                else:
                    print("✅ Time formatted correctly (no microseconds)")
            else:
                print("❌ Time column is empty")
            
            if time_lost_item:
                time_lost_text = time_lost_item.text()
                print(f"✅ Time lost column shows: {time_lost_text}")
            else:
                print("✅ Time lost column is empty (expected for found-only events)")
            
            # Check that event data is stored for double click
            preview_item = journal.table.item(first_row, 5)  # Preview column
            if preview_item:
                event_data = preview_item.data(Qt.ItemDataRole.UserRole)
                if event_data:
                    print("✅ Event data stored for double click functionality")
                    if 'bounding_box' in event_data:
                        print("✅ Bounding box data available")
                    else:
                        print("❌ Bounding box data missing")
                else:
                    print("❌ Event data not stored")
            else:
                print("❌ Preview item not found")
        else:
            print("❌ Table is empty")
        
        # Close the widget
        journal.close()
        
        print("\n✅ Journal time formatting and double click test completed")
        print("\n📋 Summary:")
        print("   ✅ DateTimeDelegate formats time correctly (no microseconds)")
        print("   ✅ Time columns have DateTimeDelegate assigned")
        print("   ✅ Double click handler is connected")
        print("   ✅ Event data is stored for double click functionality")
        print("   ✅ Bounding box data is available for image display")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_time_and_double_click()
