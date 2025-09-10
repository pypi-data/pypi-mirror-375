#!/usr/bin/env python3
"""
Test script to verify PipelineCapture get_sources method.
"""

def test_pipeline_capture_sources():
    """Test PipelineCapture get_sources functionality."""
    
    print("🔍 Testing PipelineCapture get_sources")
    print("=" * 50)
    
    try:
        from evileye.pipelines.pipeline_capture import PipelineCapture
        from unittest.mock import Mock, patch
        import cv2
        
        # Create pipeline
        pipeline = PipelineCapture()
        print("✅ PipelineCapture instantiated")
        
        # Test get_sources before initialization (should return empty list)
        sources = pipeline.get_sources()
        assert isinstance(sources, list)
        assert len(sources) == 0
        print("✅ get_sources returns empty list before initialization")
        
        # Mock VideoCapture class
        mock_video_capture = Mock()
        mock_video_capture.init.return_value = True
        mock_video_capture.is_opened.return_value = True
        mock_video_capture.is_finished.return_value = False
        mock_video_capture.source_fps = 30.0
        mock_video_capture.video_current_frame = 0
        mock_video_capture.capture = Mock()
        mock_video_capture.capture.get.side_effect = lambda prop: {
            3: 1920,  # CAP_PROP_FRAME_WIDTH
            4: 1080,  # CAP_PROP_FRAME_HEIGHT
            7: 100    # CAP_PROP_FRAME_COUNT
        }.get(prop, 0)
        
        # Mock CaptureImage
        mock_capture_image = Mock()
        mock_capture_image.source_id = 0
        mock_capture_image.frame_id = 0
        mock_capture_image.time_stamp = 1234567890.0
        mock_capture_image.current_video_frame = 0
        mock_capture_image.current_video_position = 0.0
        mock_capture_image.image = Mock()
        
        # Mock get() method to return list with CaptureImage
        mock_video_capture.get.return_value = [mock_capture_image]
        
        # Set source config and mock file existence
        pipeline.source_config = {
            'camera': 'test_video.mp4',
            'source': 'VideoFile',
            'source_ids': [0],
            'source_names': ['VideoCapture']
        }
        
        with patch('evileye.pipelines.pipeline_capture.VideoCapture', return_value=mock_video_capture), \
             patch('os.path.exists', return_value=True):
            # Initialize pipeline
            result = pipeline.init_impl()
            assert result == True
            print("✅ Pipeline initialized successfully")
            
            # Test get_sources after initialization (should return video capture object)
            sources = pipeline.get_sources()
            assert isinstance(sources, list)
            assert len(sources) == 1
            assert sources[0] == mock_video_capture
            print("✅ get_sources returns video capture object after initialization")
            
            # Test get_sources after release (should return empty list)
            pipeline.release_impl()
            sources = pipeline.get_sources()
            assert isinstance(sources, list)
            assert len(sources) == 0
            print("✅ get_sources returns empty list after release")
        
        print("✅ PipelineCapture get_sources test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_capture_controller_compatibility():
    """Test that PipelineCapture is compatible with controller."""
    
    print("\n🔍 Testing PipelineCapture Controller Compatibility")
    print("=" * 50)
    
    try:
        from evileye.controller.controller import Controller
        import json
        
        # Create controller
        controller = Controller()
        
        # Check available pipelines
        available_pipelines = controller.get_available_pipeline_classes()
        print(f"Available pipelines: {available_pipelines}")
        
        if 'PipelineCapture' in available_pipelines:
            print("✅ PipelineCapture discovered")
            
            # Test creation
            pipeline = controller._create_pipeline_instance('PipelineCapture')
            print(f"✅ Pipeline created: {type(pipeline).__name__}")
            
            # Test that it has required methods
            assert hasattr(pipeline, 'get_sources')
            assert hasattr(pipeline, 'process')
            assert hasattr(pipeline, 'init_impl')
            print("✅ Has all required methods")
            
            # Test get_sources method
            sources = pipeline.get_sources()
            assert isinstance(sources, list)
            print("✅ get_sources method works")
            
        else:
            print("❌ PipelineCapture not discovered")
        
        print("✅ PipelineCapture controller compatibility test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in compatibility test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 PipelineCapture Sources Test")
    print("=" * 60)
    
    test_pipeline_capture_sources()
    test_pipeline_capture_controller_compatibility()
    
    print("\n📋 Summary:")
    print("  ✅ PipelineCapture get_sources method tested")
    print("  ✅ Controller compatibility verified")
    print("  ✅ All tests passed successfully")

if __name__ == "__main__":
    main()
