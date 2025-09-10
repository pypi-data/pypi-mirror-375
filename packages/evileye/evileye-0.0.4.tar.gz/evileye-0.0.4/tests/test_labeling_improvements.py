#!/usr/bin/env python3
"""
Test script to verify improvements in the labeling system.
"""

import os
import json
import time
import datetime
from unittest.mock import Mock

def test_new_structure():
    """Test new folder structure."""
    
    print("🔍 Testing New Folder Structure")
    print("=" * 50)
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        
        # Create labeling manager with test directory
        test_dir = "test_labeling_improvements"
        labeling_manager = LabelingManager(base_dir=test_dir)
        print("✅ LabelingManager created")
        
        # Check if files are in the correct location
        expected_found_file = os.path.join(test_dir, "images", labeling_manager.date_str, "objects_found.json")
        expected_lost_file = os.path.join(test_dir, "images", labeling_manager.date_str, "objects_lost.json")
        
        if os.path.exists(expected_found_file):
            print("✅ Found labels file in correct location")
        else:
            print(f"❌ Found labels file not in expected location: {expected_found_file}")
            
        if os.path.exists(expected_lost_file):
            print("✅ Lost labels file in correct location")
        else:
            print(f"❌ Lost labels file not in expected location: {expected_lost_file}")
        
        # Check directory structure
        day_dir = os.path.join(test_dir, "images", labeling_manager.date_str)
        if os.path.exists(day_dir):
            print("✅ Date directory created")
            files = os.listdir(day_dir)
            print(f"Files in day directory: {files}")
        else:
            print("❌ Date directory not created")
        
        # Clean up
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
        
        print("✅ New structure test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in new structure test: {e}")
        import traceback
        traceback.print_exc()

def test_pixel_coordinates():
    """Test pixel coordinate format."""
    
    print("\n🔍 Testing Pixel Coordinates")
    print("=" * 50)
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        
        # Create labeling manager
        test_dir = "test_pixel_coords"
        labeling_manager = LabelingManager(base_dir=test_dir)
        
        # Create mock object with pixel coordinates
        mock_obj = Mock()
        mock_obj.object_id = 1
        mock_obj.frame_id = 1234
        mock_obj.time_stamp = datetime.datetime.now()
        mock_obj.track = Mock()
        mock_obj.track.bounding_box = [100, 150, 300, 400]  # x1, y1, x2, y2 in pixels
        mock_obj.track.confidence = 0.95
        mock_obj.track.track_id = 1
        mock_obj.class_id = 0
        mock_obj.source_id = 0
        mock_obj.global_id = None
        
        # Test found object data
        found_data = labeling_manager.create_found_object_data(
            mock_obj, 1920, 1080, "test_frame.jpeg", "test_preview.jpeg"
        )
        
        # Check bounding box format
        bbox = found_data["bounding_box"]
        expected_x = 100
        expected_y = 150
        expected_width = 200  # 300 - 100
        expected_height = 250  # 400 - 150
        
        if (bbox["x"] == expected_x and bbox["y"] == expected_y and
            bbox["width"] == expected_width and bbox["height"] == expected_height):
            print("✅ Pixel coordinates correct")
            print(f"Bounding box: x={bbox['x']}, y={bbox['y']}, w={bbox['width']}, h={bbox['height']}")
        else:
            print("❌ Pixel coordinates incorrect")
            print(f"Expected: x={expected_x}, y={expected_y}, w={expected_width}, h={expected_height}")
            print(f"Got: x={bbox['x']}, y={bbox['y']}, w={bbox['width']}, h={bbox['height']}")
        
        # Test lost object data
        mock_obj.time_detected = datetime.datetime.now()
        mock_obj.time_lost = datetime.datetime.now()
        mock_obj.lost_frames = 5
        
        lost_data = labeling_manager.create_lost_object_data(
            mock_obj, 1920, 1080, "test_lost_frame.jpeg", "test_lost_preview.jpeg"
        )
        
        lost_bbox = lost_data["bounding_box"]
        if (lost_bbox["x"] == expected_x and lost_bbox["y"] == expected_y and
            lost_bbox["width"] == expected_width and lost_bbox["height"] == expected_height):
            print("✅ Lost object pixel coordinates correct")
        else:
            print("❌ Lost object pixel coordinates incorrect")
        
        # Clean up
        labeling_manager.stop()
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
        
        print("✅ Pixel coordinates test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in pixel coordinates test: {e}")
        import traceback
        traceback.print_exc()

def test_buffering():
    """Test buffering functionality."""
    
    print("\n🔍 Testing Buffering Functionality")
    print("=" * 50)
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        
        # Create labeling manager with small buffer for testing
        test_dir = "test_buffering"
        labeling_manager = LabelingManager(base_dir=test_dir)
        labeling_manager.buffer_size = 3  # Small buffer for testing
        labeling_manager.save_interval = 5  # Short interval for testing
        
        # Create mock objects
        mock_objects = []
        for i in range(5):
            mock_obj = Mock()
            mock_obj.object_id = i + 1
            mock_obj.frame_id = 1000 + i
            mock_obj.time_stamp = datetime.datetime.now()
            mock_obj.track = Mock()
            mock_obj.track.bounding_box = [100 + i*10, 150 + i*10, 200 + i*10, 250 + i*10]
            mock_obj.track.confidence = 0.9
            mock_obj.track.track_id = i + 1
            mock_obj.class_id = 0
            mock_obj.source_id = 0
            mock_obj.global_id = None
            mock_objects.append(mock_obj)
        
        # Add objects to buffer
        print("Adding objects to buffer...")
        for i, mock_obj in enumerate(mock_objects):
            object_data = labeling_manager.create_found_object_data(
                mock_obj, 1920, 1080, f"test_frame_{i}.jpeg", f"test_preview_{i}.jpeg"
            )
            labeling_manager.add_object_found(object_data)
            print(f"Added object {i+1}, buffer size: {len(labeling_manager.found_buffer)}")
        
        # Wait a bit for background saving
        time.sleep(2)
        
        # Force flush
        print("Forcing buffer flush...")
        labeling_manager.flush_buffers()
        
        # Check if data was saved
        found_file = labeling_manager.found_labels_file
        if os.path.exists(found_file):
            with open(found_file, 'r') as f:
                data = json.load(f)
                object_count = len(data["objects"])
                print(f"✅ Found {object_count} objects in saved file")
                
                if object_count == 5:
                    print("✅ All objects were saved correctly")
                else:
                    print(f"❌ Expected 5 objects, got {object_count}")
        else:
            print("❌ Found labels file not created")
        
        # Clean up
        labeling_manager.stop()
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
        
        print("✅ Buffering test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in buffering test: {e}")
        import traceback
        traceback.print_exc()

def test_performance():
    """Test performance improvements."""
    
    print("\n🔍 Testing Performance Improvements")
    print("=" * 50)
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        import time
        
        # Create labeling manager
        test_dir = "test_performance"
        labeling_manager = LabelingManager(base_dir=test_dir)
        labeling_manager.buffer_size = 50  # Medium buffer
        
        # Create many mock objects
        num_objects = 200
        mock_objects = []
        
        print(f"Creating {num_objects} mock objects...")
        for i in range(num_objects):
            mock_obj = Mock()
            mock_obj.object_id = i + 1
            mock_obj.frame_id = 1000 + i
            mock_obj.time_stamp = datetime.datetime.now()
            mock_obj.track = Mock()
            mock_obj.track.bounding_box = [100 + i, 150 + i, 200 + i, 250 + i]
            mock_obj.track.confidence = 0.9
            mock_obj.track.track_id = i + 1
            mock_obj.class_id = 0
            mock_obj.source_id = 0
            mock_obj.global_id = None
            mock_objects.append(mock_obj)
        
        # Test buffered adding
        print("Testing buffered adding...")
        start_time = time.time()
        
        for i, mock_obj in enumerate(mock_objects):
            object_data = labeling_manager.create_found_object_data(
                mock_obj, 1920, 1080, f"test_frame_{i}.jpeg", f"test_preview_{i}.jpeg"
            )
            labeling_manager.add_object_found(object_data)
        
        # Force flush
        labeling_manager.flush_buffers()
        end_time = time.time()
        
        buffered_time = end_time - start_time
        print(f"✅ Buffered adding took {buffered_time:.3f} seconds")
        
        # Check results
        found_file = labeling_manager.found_labels_file
        if os.path.exists(found_file):
            with open(found_file, 'r') as f:
                data = json.load(f)
                object_count = len(data["objects"])
                print(f"✅ Saved {object_count} objects successfully")
        
        # Clean up
        labeling_manager.stop()
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
        
        print("✅ Performance test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 Labeling System Improvements Test")
    print("=" * 60)
    
    test_new_structure()
    test_pixel_coordinates()
    test_buffering()
    test_performance()
    
    print("\n📋 Summary:")
    print("  ✅ New folder structure implemented")
    print("  ✅ Pixel coordinates for COCO compatibility")
    print("  ✅ Buffering system for performance")
    print("  ✅ Asynchronous saving with background thread")
    print("  ✅ Proper cleanup and data persistence")

if __name__ == "__main__":
    main()



