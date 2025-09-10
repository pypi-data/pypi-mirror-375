#!/usr/bin/env python3
"""
Simple test to verify basic controller functionality without database.
"""

def test_basic_controller():
    """Test basic controller creation and initialization."""
    
    print("🔍 Testing Basic Controller")
    print("=" * 50)
    
    try:
        from evileye.controller import controller
        print("✅ Successfully imported controller")
        
        # Create controller instance
        ctrl = controller.Controller()
        print("✅ Successfully created controller")
        
        # Check default value
        print(f"use_database default value: {ctrl.use_database}")
        
        # Test minimal initialization
        test_params = {
            'controller': {
                'use_database': False,
                'fps': 30
            },
            'sources': [],
            'pipeline': {
                'pipeline_class': 'PipelineSurveillance'
            }
        }
        
        print("Attempting to initialize controller...")
        ctrl.init(test_params)
        print("✅ Controller initialized successfully")
        
        print(f"use_database after init: {ctrl.use_database}")
        print(f"db_controller: {ctrl.db_controller}")
        print(f"obj_handler: {ctrl.obj_handler is not None}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_controller()



