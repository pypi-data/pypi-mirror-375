#!/usr/bin/env python3
"""
Debug script to analyze PreprocessingPipeline registration issue.
"""

import sys
from pathlib import Path

def test_registry_debug():
    """Debug registry registration."""
    
    print("🔍 Debug Registry Registration")
    print("=" * 50)
    
    # Clear registry
    from evileye.core.base_class import EvilEyeBase
    EvilEyeBase._registry.clear()
    print("Registry cleared")
    
    # Check registry before any imports
    print(f"Registry before imports: {len(EvilEyeBase._registry)} items")
    
    # Import preprocessing step by step
    try:
        print("1. Importing preprocessing_base...")
        import evileye.preprocessing.preprocessing_base
        print(f"   Registry after preprocessing_base: {len(EvilEyeBase._registry)} items")
        
        print("2. Importing preprocessing_factory...")
        import evileye.preprocessing.preprocessing_factory
        print(f"   Registry after preprocessing_factory: {len(EvilEyeBase._registry)} items")
        
        print("3. Importing preprocessing_vehicle...")
        import evileye.preprocessing.preprocessing_vehicle
        print(f"   Registry after preprocessing_vehicle: {len(EvilEyeBase._registry)} items")
        
        # Check if PreprocessingPipeline is registered
        if "PreprocessingPipeline" in EvilEyeBase._registry:
            print("✅ PreprocessingPipeline is registered!")
        else:
            print("❌ PreprocessingPipeline is NOT registered!")
            
        # Show all registered classes
        print("\nRegistered classes:")
        for name, cls in EvilEyeBase._registry.items():
            print(f"  {name}: {cls}")
            
    except Exception as e:
        print(f"❌ Error during step-by-step import: {e}")
        import traceback
        traceback.print_exc()

def test_import_evileye_preprocessing():
    """Test importing evileye.preprocessing directly."""
    
    print("\n🔍 Test Import evileye.preprocessing")
    print("=" * 50)
    
    # Clear registry
    from evileye.core.base_class import EvilEyeBase
    EvilEyeBase._registry.clear()
    print("Registry cleared")
    
    try:
        print("Importing evileye.preprocessing...")
        import evileye.preprocessing
        print(f"Registry after import: {len(EvilEyeBase._registry)} items")
        
        if "PreprocessingPipeline" in EvilEyeBase._registry:
            print("✅ PreprocessingPipeline is registered!")
        else:
            print("❌ PreprocessingPipeline is NOT registered!")
            
    except Exception as e:
        print(f"❌ Error importing evileye.preprocessing: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function."""
    
    print("🔍 PreprocessingPipeline Registration Debug")
    print("=" * 60)
    
    test_registry_debug()
    test_import_evileye_preprocessing()

if __name__ == "__main__":
    main()
