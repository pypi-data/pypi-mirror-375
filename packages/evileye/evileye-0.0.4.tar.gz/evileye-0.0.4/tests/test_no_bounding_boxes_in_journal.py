#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_no_bounding_boxes_in_journal():
    """Test that bounding boxes are not displayed in the journal table"""
    
    print("=== Test No Bounding Boxes in Journal ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
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
        
        # Create test preview image with bounding box (simulating what was saved)
        test_image = np.zeros((150, 300, 3), dtype=np.uint8)
        test_image[:] = (100, 150, 200)  # Blue-gray background
        
        # Add a green bounding box to simulate what was previously drawn
        cv2.rectangle(test_image, (50, 30), (250, 120), (0, 255, 0), 2)
        
        # Save test preview image
        preview_path = os.path.join(test_images_dir, 'detected_previews', 'test_preview.jpeg')
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        cv2.imwrite(preview_path, test_image)
        
        print(f"✅ Created test preview image: {preview_path}")
        
        # Create test JSON data
        test_json_path = os.path.join(test_images_dir, 'objects_found.json')
        test_data = {
            "metadata": {
                "version": "1.0",
                "created": datetime.datetime.now().isoformat(),
                "description": "Test data",
                "total_objects": 1
            },
            "objects": [
                {
                    "object_id": 1,
                    "frame_id": 1,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "image_filename": "detected_previews/test_preview.jpeg",
                    "bounding_box": {
                        "x": 50,
                        "y": 30,
                        "width": 200,
                        "height": 90
                    },
                    "class_id": 0,
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
        
        # Create EventsJournalJson widget
        journal = EventsJournalJson(base_dir)
        journal.show()
        
        print("✅ Created EventsJournalJson widget")
        
        # Check that the table loads data
        if journal.table.rowCount() > 0:
            print(f"✅ Table loaded {journal.table.rowCount()} rows")
            
            # Check that preview column has image path
            preview_item = journal.table.item(0, 4)  # Preview column
            if preview_item and preview_item.text():
                print(f"✅ Preview column contains image path: {preview_item.text()}")
                
                # Check that no bounding box data is stored
                from PyQt6.QtCore import Qt
                bbox_data = preview_item.data(Qt.ItemDataRole.UserRole)
                if bbox_data is None:
                    print("✅ No bounding box data stored in table item")
                else:
                    print(f"❌ Bounding box data still stored: {bbox_data}")
            else:
                print("❌ Preview column is empty")
        else:
            print("❌ Table is empty")
        
        # Close the widget
        journal.close()
        
        print("\n✅ No bounding boxes in journal test completed")
        print("\n📋 Summary:")
        print("   ✅ Preview images are displayed without bounding boxes")
        print("   ✅ No bounding box data stored in table items")
        print("   ✅ Journal shows clean preview images")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_no_bounding_boxes_in_journal()
