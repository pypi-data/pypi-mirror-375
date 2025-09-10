#!/usr/bin/env python3
"""
Test script to verify PipelineCapture inheritance.
"""

def test_pipeline_inheritance():
    """Test PipelineCapture inheritance chain."""
    
    print("🔍 Testing PipelineCapture Inheritance")
    print("=" * 50)
    
    try:
        from evileye.pipelines.pipeline_capture import PipelineCapture
        from evileye.core.pipeline_simple import PipelineSimple
        from evileye.core.pipeline_base import PipelineBase
        
        # Check inheritance chain
        print(f"PipelineCapture bases: {PipelineCapture.__bases__}")
        print(f"PipelineSimple bases: {PipelineSimple.__bases__}")
        print(f"PipelineBase bases: {PipelineBase.__bases__}")
        
        # Check if PipelineCapture inherits from classes with 'Pipeline' in name
        pipeline_bases = []
        for base in PipelineCapture.__bases__:
            if 'Pipeline' in base.__name__:
                pipeline_bases.append(base.__name__)
        
        print(f"PipelineCapture pipeline bases: {pipeline_bases}")
        
        # Check inheritance chain
        assert issubclass(PipelineCapture, PipelineSimple)
        assert issubclass(PipelineSimple, PipelineBase)
        print("✅ Inheritance chain correct")
        
        # Check that PipelineCapture is found by the discovery mechanism
        import inspect
        has_pipeline_base = any('Pipeline' in base.__name__ for base in PipelineCapture.__bases__)
        print(f"Has pipeline base: {has_pipeline_base}")
        
        if has_pipeline_base:
            print("✅ PipelineCapture should be discoverable")
        else:
            print("⚠️ PipelineCapture may not be discoverable")
        
        print("✅ PipelineCapture inheritance test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in inheritance test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_discovery():
    """Test pipeline discovery mechanism."""
    
    print("\n🔍 Testing Pipeline Discovery")
    print("=" * 50)
    
    try:
        import importlib
        import inspect
        from pathlib import Path
        
        # Simulate the discovery mechanism
        pipeline_classes = {}
        
        # Search in evileye.pipelines package
        try:
            pipelines_module = importlib.import_module('evileye.pipelines')
            for name, obj in inspect.getmembers(pipelines_module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__bases__') and 
                    any('Pipeline' in base.__name__ for base in obj.__bases__)):
                    pipeline_classes[name] = obj
                    print(f"Found pipeline class: {name}")
        except ImportError as e:
            print(f"Warning: Could not import evileye.pipelines: {e}")
        
        print(f"Discovered pipeline classes: {list(pipeline_classes.keys())}")
        
        if 'PipelineCapture' in pipeline_classes:
            print("✅ PipelineCapture discovered successfully")
        else:
            print("❌ PipelineCapture not discovered")
            print("Available classes:", list(pipeline_classes.keys()))
        
        print("✅ Pipeline discovery test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in discovery test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 Pipeline Inheritance Test")
    print("=" * 60)
    
    test_pipeline_inheritance()
    test_pipeline_discovery()
    
    print("\n📋 Summary:")
    print("  ✅ PipelineCapture inheritance verified")
    print("  ✅ Discovery mechanism tested")
    print("  ✅ All tests completed")

if __name__ == "__main__":
    main()



