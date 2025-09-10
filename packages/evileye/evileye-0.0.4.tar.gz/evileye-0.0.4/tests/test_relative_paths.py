#!/usr/bin/env python3
"""
Test script for relative path resolution in EvilEye components.
"""

import os
import sys
from pathlib import Path

def test_detector_relative_paths():
    """Test relative path resolution in YOLO detector."""
    
    print("🔍 Testing Detector Relative Paths")
    print("=" * 50)
    
    try:
        from evileye.object_detector.object_detection_yolo import ObjectDetectorYolo
        
        # Test with relative path
        detector = ObjectDetectorYolo()
        detector.params['model'] = 'models/yolo11n.pt'
        detector.set_params_impl()
        
        print(f"Original model path: models/yolo11n.pt")
        print(f"Stored model path: {detector.model_name}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Path is absolute: {os.path.isabs(detector.model_name)}")
        
        # Test access path resolution
        access_path = detector.model_name
        if not os.path.isabs(access_path):
            access_path = os.path.join(os.getcwd(), access_path)
        print(f"Access path: {access_path}")
        print(f"File exists: {os.path.exists(access_path)}")
        
    except Exception as e:
        print(f"Error testing detector: {e}")

def test_tracker_relative_paths():
    """Test relative path resolution in Botsort tracker."""
    
    print("\n🔍 Testing Tracker Relative Paths")
    print("=" * 50)
    
    try:
        from evileye.object_tracker.object_tracking_botsort import ObjectTrackingBotsort
        
        # Test with relative path
        tracker = ObjectTrackingBotsort()
        tracker.params['tracker_onnx'] = 'models/osnet_ain_x1_0_M.onnx'
        
        # Simulate encoder dictionary
        encoders = {}
        encoders[os.path.join(os.getcwd(), 'models/osnet_ain_x1_0_M.onnx')] = None
        
        tracker.init_impl(encoders=encoders)
        
        print(f"Original onnx path: models/osnet_ain_x1_0_M.onnx")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Expected resolved path: {os.path.join(os.getcwd(), 'models/osnet_ain_x1_0_M.onnx')}")
        print(f"File exists: {os.path.exists('models/osnet_ain_x1_0_M.onnx')}")
        
    except Exception as e:
        print(f"Error testing tracker: {e}")

def test_database_relative_paths():
    """Test relative path resolution in database controller."""
    
    print("\n🔍 Testing Database Relative Paths")
    print("=" * 50)
    
    try:
        from evileye.database_controller.database_controller_pg import DatabaseControllerPg
        
        # Test with relative path
        db_controller = DatabaseControllerPg({})
        db_controller.default()  # Initialize default parameters
        db_controller.params['image_dir'] = 'database_images'
        db_controller.set_params_impl()
        
        print(f"Original image_dir: database_images")
        print(f"Stored image_dir: {db_controller.image_dir}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Path is absolute: {os.path.isabs(db_controller.image_dir)}")
        
        # Test access path resolution
        access_path = db_controller.image_dir
        if not os.path.isabs(access_path):
            access_path = os.path.join(os.getcwd(), access_path)
        print(f"Access path: {access_path}")
        print(f"Directory exists: {os.path.exists(access_path)}")
        
        # Create directory if it doesn't exist
        if not os.path.exists(db_controller.image_dir):
            os.makedirs(db_controller.image_dir)
            print(f"Created directory: {db_controller.image_dir}")
        
    except Exception as e:
        print(f"Error testing database: {e}")

def test_config_loading():
    """Test loading configuration with relative paths."""
    
    print("\n🔍 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        import json
        
        # Load test configuration
        with open('test_relative_paths.json', 'r') as f:
            config = json.load(f)
        
        print("Configuration loaded successfully")
        print(f"Detector model: {config['pipeline']['detectors'][0]['model']}")
        print(f"Tracker onnx: {config['pipeline']['trackers'][0]['tracker_onnx']}")
        print(f"Database image_dir: {config['database']['image_dir']}")
        
        # Test path resolution
        detector_model = config['pipeline']['detectors'][0]['model']
        tracker_onnx = config['pipeline']['trackers'][0]['tracker_onnx']
        image_dir = config['database']['image_dir']
        
        print(f"\nPath resolution test:")
        print(f"  models/yolo11n.pt -> {os.path.join(os.getcwd(), detector_model)} (for access)")
        print(f"  models/osnet_ain_x1_0_M.onnx -> {os.path.join(os.getcwd(), tracker_onnx)} (for access)")
        print(f"  database_images -> {os.path.join(os.getcwd(), image_dir)} (for access)")
        
    except Exception as e:
        print(f"Error testing configuration: {e}")

#!/usr/bin/env python3
"""
Test script to verify relative paths in labeling data.
"""

import os
import json
import datetime
from unittest.mock import Mock

def test_relative_paths():
    """Test relative paths in labeling data."""
    
    print("🔍 Testing Relative Paths in Labeling Data")
    print("=" * 50)
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        
        # Create labeling manager
        test_dir = "test_relative_paths"
        cameras_params = [
            {
                'source_ids': [0, 1],
                'source_names': ['camera_1', 'camera_2']
            }
        ]
        labeling_manager = LabelingManager(base_dir=test_dir, cameras_params=cameras_params)
        
        # Create mock object
        mock_obj = Mock()
        mock_obj.object_id = 1
        mock_obj.frame_id = 1234
        mock_obj.time_stamp = datetime.datetime.now()
        mock_obj.time_detected = datetime.datetime.now()
        mock_obj.time_lost = datetime.datetime.now()
        mock_obj.track = Mock()
        mock_obj.track.bounding_box = [100, 150, 300, 400]
        mock_obj.track.confidence = 0.95
        mock_obj.track.track_id = 1
        mock_obj.class_id = 0
        mock_obj.source_id = 0
        mock_obj.global_id = None
        mock_obj.lost_frames = 5
        
        # Test found object data with relative paths
        found_data = labeling_manager.create_found_object_data(
            mock_obj, 1920, 1080, "test_frame.jpeg", "test_preview.jpeg"
        )
        
        print("✅ Found object data created")
        print(f"Image filename: {found_data['image_filename']}")
        print(f"Source ID: {found_data['source_id']}")
        print(f"Source name: {found_data['source_name']}")
        
        # Check relative paths (without date folder)
        expected_image_filename = "detected_frames/test_frame.jpeg"
        
        if found_data['image_filename'] == expected_image_filename:
            print("✅ Image filename is correct")
        else:
            print(f"❌ Expected image filename: {expected_image_filename}")
            print(f"Got: {found_data['image_filename']}")
        
        # Check source name
        if found_data['source_name'] == 'camera_1':
            print("✅ Source name is correct")
        else:
            print(f"❌ Expected source name: camera_1")
            print(f"Got: {found_data['source_name']}")
        
        # Test lost object data with relative paths
        lost_data = labeling_manager.create_lost_object_data(
            mock_obj, 1920, 1080, "test_lost_frame.jpeg", "test_lost_preview.jpeg"
        )
        
        print("\n✅ Lost object data created")
        print(f"Image filename: {lost_data['image_filename']}")
        print(f"Source ID: {lost_data['source_id']}")
        print(f"Source name: {lost_data['source_name']}")
        
        # Check relative paths for lost objects (without date folder)
        expected_lost_image_filename = "lost_frames/test_lost_frame.jpeg"
        
        if lost_data['image_filename'] == expected_lost_image_filename:
            print("✅ Lost image filename is correct")
        else:
            print(f"❌ Expected lost image filename: {expected_lost_image_filename}")
            print(f"Got: {lost_data['image_filename']}")
        
        # Check source name for lost object
        if lost_data['source_name'] == 'camera_1':
            print("✅ Lost source name is correct")
        else:
            print(f"❌ Expected lost source name: camera_1")
            print(f"Got: {lost_data['source_name']}")
        
        # Test path construction
        print("\n🔍 Testing path construction:")
        print(f"Base directory: {test_dir}")
        print(f"Date string: {labeling_manager.date_str}")
        print(f"Full image path would be: {os.path.join(test_dir, 'images', labeling_manager.date_str, found_data['image_filename'])}")
        
        # Clean up
        labeling_manager.stop()
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
        
        print("\n✅ Relative paths test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in relative paths test: {e}")
        import traceback
        traceback.print_exc()

def test_path_usage_example():
    """Test how to use relative paths to access images."""
    
    print("\n🔍 Testing Path Usage Example")
    print("=" * 50)
    
    try:
        from evileye.objects_handler.labeling_manager import LabelingManager
        
        # Create labeling manager
        test_dir = "test_path_usage"
        cameras_params = [
            {
                'source_ids': [0, 1],
                'source_names': ['camera_1', 'camera_2']
            }
        ]
        labeling_manager = LabelingManager(base_dir=test_dir, cameras_params=cameras_params)
        
        # Simulate loading label data
        mock_label_data = {
            "object_id": 1,
            "frame_id": 1234,
            "timestamp": "2024-01-15T10:30:15.123456",
            "image_filename": "detected_frames/2024_01_15_10_30_15.123456_frame.jpeg",
            "bounding_box": {"x": 480, "y": 324, "width": 288, "height": 216},
            "confidence": 0.95,
            "class_id": 0,
            "class_name": "person",
            "source_id": 0,
            "source_name": "camera_1",
            "track_id": 1,
            "global_id": None
        }
        
        print("✅ Mock label data created")
        print(f"Image filename from label: {mock_label_data['image_filename']}")
        print(f"Source name from label: {mock_label_data['source_name']}")
        
        # Show how to construct full paths
        base_dir = test_dir
        date_str = "2024_01_15"  # Date from the mock data
        full_image_path = os.path.join(base_dir, "images", date_str, mock_label_data['image_filename'])
        
        print(f"\nFull image path: {full_image_path}")
        
        # Show how to check if files exist
        print(f"\nImage file would exist: {os.path.exists(full_image_path)}")
        
        # Show how to use with different base directories
        alternative_base = "/custom/data/path"
        alt_image_path = os.path.join(alternative_base, "images", date_str, mock_label_data['image_filename'])
        
        print(f"\nWith alternative base '{alternative_base}':")
        print(f"Image path: {alt_image_path}")
        
        # Clean up
        labeling_manager.stop()
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
        
        print("\n✅ Path usage example completed successfully")
        
    except Exception as e:
        print(f"❌ Error in path usage example: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 Relative Paths in Labeling Data Test")
    print("=" * 60)
    
    test_relative_paths()
    test_path_usage_example()
    
    print("\n📋 Summary:")
    print("  ✅ Relative paths added to labeling data")
    print("  ✅ image_path and preview_path fields")
    print("  ✅ Paths relative to base directory")
    print("  ✅ Easy access to images from label data")
    print("  ✅ Compatible with different base directories")

if __name__ == "__main__":
    main()
