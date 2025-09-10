#!/usr/bin/env python3
"""
Test script to check PreprocessingBase inheritance.
"""

def test_preprocessing_base():
    """Test PreprocessingBase inheritance."""
    
    print("🔍 Testing PreprocessingBase")
    print("=" * 50)
    
    try:
        from evileye.preprocessing.preprocessing_base import PreprocessingBase
        from evileye.core.base_class import EvilEyeBase
        
        print(f"PreprocessingBase: {PreprocessingBase}")
        print(f"EvilEyeBase: {EvilEyeBase}")
        print(f"PreprocessingBase.__bases__: {PreprocessingBase.__bases__}")
        
        # Check if PreprocessingBase inherits from EvilEyeBase
        if EvilEyeBase in PreprocessingBase.__bases__:
            print("✅ PreprocessingBase correctly inherits from EvilEyeBase")
        else:
            print("❌ PreprocessingBase does NOT inherit from EvilEyeBase")
            
    except Exception as e:
        print(f"❌ Error testing PreprocessingBase: {e}")
        import traceback
        traceback.print_exc()

def test_preprocessing_pipeline():
    """Test PreprocessingPipeline registration."""
    
    print("\n🔍 Testing PreprocessingPipeline")
    print("=" * 50)
    
    try:
        from evileye.preprocessing.preprocessing_pipeline import PreprocessingPipeline
        from evileye.core.base_class import EvilEyeBase
        
        print(f"PreprocessingPipeline: {PreprocessingPipeline}")
        print(f"PreprocessingPipeline.__bases__: {PreprocessingPipeline.__bases__}")
        
        # Check if PreprocessingPipeline is in registry
        if "PreprocessingPipeline" in EvilEyeBase._registry:
            print("✅ PreprocessingPipeline is in registry")
        else:
            print("❌ PreprocessingPipeline is NOT in registry")
            
        # Try to create instance
        try:
            instance = PreprocessingPipeline()
            print("✅ Successfully created PreprocessingPipeline instance")
        except Exception as e:
            print(f"❌ Error creating PreprocessingPipeline instance: {e}")
            
    except Exception as e:
        print(f"❌ Error testing PreprocessingPipeline: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🔍 PreprocessingBase and PreprocessingPipeline Test")
    print("=" * 60)
    
    test_preprocessing_base()
    test_preprocessing_pipeline()

if __name__ == "__main__":
    main()
