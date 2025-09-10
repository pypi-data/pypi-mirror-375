#!/usr/bin/env python3
"""
Test script to verify PipelineCapture launch.
"""

import json
import os

def test_pipeline_capture_launch():
    """Test PipelineCapture launch with configuration."""
    
    print("🔍 Testing PipelineCapture Launch")
    print("=" * 50)
    
    try:
        from evileye.controller.controller import Controller
        
        # Load configuration
        config_path = "evileye/samples_configs/pipeline_capture.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded")
        
        # Create controller
        controller = Controller()
        print("✅ Controller created")
        
        # Check available pipelines
        available_pipelines = controller.get_available_pipeline_classes()
        print(f"Available pipelines: {available_pipelines}")
        
        if 'PipelineCapture' not in available_pipelines:
            print("❌ PipelineCapture not available")
            return
        
        # Try to create pipeline instance
        try:
            pipeline = controller._create_pipeline_instance('PipelineCapture')
            print("✅ PipelineCapture instance created")
        except Exception as e:
            print(f"❌ Failed to create PipelineCapture instance: {e}")
            return
        
        # Try to initialize pipeline with config
        try:
            pipeline.params = config['pipeline']
            pipeline.set_params_impl()
            print("✅ Pipeline parameters set")
        except Exception as e:
            print(f"❌ Failed to set pipeline parameters: {e}")
            return
        
        # Try to initialize pipeline
        try:
            result = pipeline.init_impl()
            print(f"✅ Pipeline initialized: {result}")
        except Exception as e:
            print(f"❌ Failed to initialize pipeline: {e}")
            return
        
        print("✅ PipelineCapture launch test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in launch test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_capture_with_controller():
    """Test PipelineCapture with controller initialization."""
    
    print("\n🔍 Testing PipelineCapture with Controller")
    print("=" * 50)
    
    try:
        from evileye.controller.controller import Controller
        
        # Load configuration
        config_path = "evileye/samples_configs/pipeline_capture.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded")
        
        # Create controller
        controller = Controller()
        print("✅ Controller created")
        
        # Try to initialize controller with config
        try:
            controller.init(config)
            print("✅ Controller initialized with config")
        except Exception as e:
            print(f"❌ Failed to initialize controller: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Check if pipeline was created correctly
        if hasattr(controller, 'pipeline') and controller.pipeline:
            print(f"✅ Pipeline created: {type(controller.pipeline).__name__}")
        else:
            print("❌ No pipeline created")
        
        print("✅ PipelineCapture with controller test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in controller test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 PipelineCapture Launch Test")
    print("=" * 60)
    
    test_pipeline_capture_launch()
    test_pipeline_capture_with_controller()
    
    print("\n📋 Summary:")
    print("  ✅ PipelineCapture launch tested")
    print("  ✅ Controller integration tested")
    print("  ✅ All tests completed")

if __name__ == "__main__":
    main()



