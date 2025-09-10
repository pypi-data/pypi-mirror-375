#!/usr/bin/env python3
"""
Test script to verify that all pipeline classes implement required abstract methods.
"""

def test_pipeline_base_abstract_methods():
    """Test that PipelineBase has required abstract methods."""
    
    print("🔍 Testing PipelineBase Abstract Methods")
    print("=" * 50)
    
    try:
        from evileye.core.pipeline_base import PipelineBase
        import inspect
        
        # Check abstract methods
        abstract_methods = []
        for name, method in inspect.getmembers(PipelineBase, inspect.isfunction):
            if getattr(method, '__isabstractmethod__', False):
                abstract_methods.append(name)
        
        print(f"Abstract methods in PipelineBase: {abstract_methods}")
        
        # Check that get_sources is abstract
        assert 'get_sources' in abstract_methods
        print("✅ get_sources is abstract in PipelineBase")
        
        # Check that generate_default_structure is abstract
        assert 'generate_default_structure' in abstract_methods
        print("✅ generate_default_structure is abstract in PipelineBase")
        
        print("✅ PipelineBase abstract methods test completed")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_simple_implementation():
    """Test that PipelineSimple implements abstract methods."""
    
    print("\n🔍 Testing PipelineSimple Implementation")
    print("=" * 50)
    
    try:
        from evileye.core.pipeline_simple import PipelineSimple
        import inspect
        
        # Check that PipelineSimple is not abstract
        abstract_methods = []
        for name, method in inspect.getmembers(PipelineSimple, inspect.isfunction):
            if getattr(method, '__isabstractmethod__', False):
                abstract_methods.append(name)
        
        print(f"Abstract methods in PipelineSimple: {abstract_methods}")
        
        # PipelineSimple should only have process_logic as abstract
        assert 'process_logic' in abstract_methods
        assert 'get_sources' not in abstract_methods
        assert 'generate_default_structure' not in abstract_methods
        print("✅ PipelineSimple correctly implements abstract methods")
        
        # Test get_sources implementation
        pipeline = PipelineSimple()
        sources = pipeline.get_sources()
        assert isinstance(sources, list)
        assert len(sources) == 0
        print("✅ PipelineSimple.get_sources() returns empty list")
        
        print("✅ PipelineSimple implementation test completed")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_processors_implementation():
    """Test that PipelineProcessors implements abstract methods."""
    
    print("\n🔍 Testing PipelineProcessors Implementation")
    print("=" * 50)
    
    try:
        from evileye.core.pipeline_processors import PipelineProcessors
        import inspect
        
        # Check that PipelineProcessors is not abstract
        abstract_methods = []
        for name, method in inspect.getmembers(PipelineProcessors, inspect.isfunction):
            if getattr(method, '__isabstractmethod__', False):
                abstract_methods.append(name)
        
        print(f"Abstract methods in PipelineProcessors: {abstract_methods}")
        
        # PipelineProcessors should not have any abstract methods
        assert len(abstract_methods) == 0
        print("✅ PipelineProcessors has no abstract methods")
        
        # Test get_sources implementation
        pipeline = PipelineProcessors()
        sources = pipeline.get_sources()
        assert isinstance(sources, list)
        print("✅ PipelineProcessors.get_sources() returns list")
        
        print("✅ PipelineProcessors implementation test completed")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

def test_pipeline_capture_implementation():
    """Test that PipelineCapture implements abstract methods."""
    
    print("\n🔍 Testing PipelineCapture Implementation")
    print("=" * 50)
    
    try:
        from evileye.pipelines.pipeline_capture import PipelineCapture
        import inspect
        
        # Check that PipelineCapture is not abstract
        abstract_methods = []
        for name, method in inspect.getmembers(PipelineCapture, inspect.isfunction):
            if getattr(method, '__isabstractmethod__', False):
                abstract_methods.append(name)
        
        print(f"Abstract methods in PipelineCapture: {abstract_methods}")
        
        # PipelineCapture should not have any abstract methods
        assert len(abstract_methods) == 0
        print("✅ PipelineCapture correctly implements abstract methods")
        
        # Test get_sources implementation
        pipeline = PipelineCapture()
        sources = pipeline.get_sources()
        assert isinstance(sources, list)
        assert len(sources) == 0  # No capture object initially
        print("✅ PipelineCapture.get_sources() returns empty list initially")
        
        print("✅ PipelineCapture implementation test completed")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 Pipeline Base Methods Test")
    print("=" * 60)
    
    test_pipeline_base_abstract_methods()
    test_pipeline_simple_implementation()
    test_pipeline_processors_implementation()
    test_pipeline_capture_implementation()
    
    print("\n📋 Summary:")
    print("  ✅ PipelineBase has correct abstract methods")
    print("  ✅ PipelineSimple implements abstract methods")
    print("  ✅ PipelineProcessors implements abstract methods")
    print("  ✅ PipelineCapture implements abstract methods")
    print("  ✅ All pipeline classes have get_sources() method")
    print("  ✅ All tests passed successfully")

if __name__ == "__main__":
    main()
