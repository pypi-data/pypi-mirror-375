#!/usr/bin/env python3
"""
Test script to analyze registry and PreprocessingPipeline registration.
"""

import sys
from pathlib import Path

def test_registry_before_imports():
    """Test registry before importing preprocessing module."""
    
    print("🔍 Testing Registry Before Imports")
    print("=" * 50)
    
    # Import base class
    from evileye.core.base_class import EvilEyeBase
    
    print(f"Registry contents before preprocessing import:")
    for name, cls in EvilEyeBase._registry.items():
        print(f"  {name}: {cls}")
    
    print(f"Total registered classes: {len(EvilEyeBase._registry)}")

def test_registry_after_imports():
    """Test registry after importing preprocessing module."""
    
    print("\n🔍 Testing Registry After Imports")
    print("=" * 50)
    
    # Import base class
    from evileye.core.base_class import EvilEyeBase
    
    # Import preprocessing module
    try:
        import evileye.preprocessing
        print("✅ Successfully imported evileye.preprocessing")
    except Exception as e:
        print(f"❌ Error importing evileye.preprocessing: {e}")
        return
    
    print(f"Registry contents after preprocessing import:")
    for name, cls in EvilEyeBase._registry.items():
        print(f"  {name}: {cls}")
    
    print(f"Total registered classes: {len(EvilEyeBase._registry)}")
    
    # Check specifically for PreprocessingPipeline
    if "PreprocessingPipeline" in EvilEyeBase._registry:
        print("✅ PreprocessingPipeline is registered")
    else:
        print("❌ PreprocessingPipeline is NOT registered")

def test_direct_import():
    """Test direct import of PreprocessingPipeline."""
    
    print("\n🔍 Testing Direct Import")
    print("=" * 50)
    
    try:
        from evileye.preprocessing.preprocessing_pipeline import PreprocessingPipeline
        print("✅ Successfully imported PreprocessingPipeline directly")
        
        # Check if it's in registry now
        from evileye.core.base_class import EvilEyeBase
        if "PreprocessingPipeline" in EvilEyeBase._registry:
            print("✅ PreprocessingPipeline is now in registry")
        else:
            print("❌ PreprocessingPipeline is still NOT in registry")
            
    except Exception as e:
        print(f"❌ Error importing PreprocessingPipeline directly: {e}")

def test_import_order():
    """Test different import orders."""
    
    print("\n🔍 Testing Import Order")
    print("=" * 50)
    
    # Clear registry (simulate fresh start)
    from evileye.core.base_class import EvilEyeBase
    EvilEyeBase._registry.clear()
    
    print("Registry cleared")
    
    # Import in different order
    try:
        # First import preprocessing
        import evileye.preprocessing
        print("✅ Imported preprocessing first")
        
        # Then check registry
        if "PreprocessingPipeline" in EvilEyeBase._registry:
            print("✅ PreprocessingPipeline is registered after preprocessing import")
        else:
            print("❌ PreprocessingPipeline is NOT registered after preprocessing import")
            
    except Exception as e:
        print(f"❌ Error in import order test: {e}")

def test_controller_imports():
    """Test what controller imports."""
    
    print("\n🔍 Testing Controller Imports")
    print("=" * 50)
    
    try:
        # Import controller
        from evileye.controller import controller
        print("✅ Successfully imported controller")
        
        # Check registry
        from evileye.core.base_class import EvilEyeBase
        if "PreprocessingPipeline" in EvilEyeBase._registry:
            print("✅ PreprocessingPipeline is registered after controller import")
        else:
            print("❌ PreprocessingPipeline is NOT registered after controller import")
            
    except Exception as e:
        print(f"❌ Error importing controller: {e}")

def main():
    """Main test function."""
    
    print("🔍 Registry Analysis for PreprocessingPipeline")
    print("=" * 60)
    
    # Test registry before imports
    test_registry_before_imports()
    
    # Test registry after imports
    test_registry_after_imports()
    
    # Test direct import
    test_direct_import()
    
    # Test import order
    test_import_order()
    
    # Test controller imports
    test_controller_imports()
    
    print("\n📋 Summary:")
    print("  • Registry is populated when modules are imported")
    print("  • PreprocessingPipeline should be registered when preprocessing module is imported")
    print("  • If not registered, there might be an import issue")

if __name__ == "__main__":
    main()
