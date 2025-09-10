#!/usr/bin/env python3
"""
Minimal test for controller without database.
"""

def test_minimal_init():
    """Test minimal controller initialization without database."""
    
    print("🔍 Testing Minimal Controller Init")
    print("=" * 50)
    
    try:
        from evileye.controller import controller
        
        # Create controller
        ctrl = controller.Controller()
        print("✅ Controller created")
        
        # Set minimal parameters
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
        
        # Initialize
        print("Initializing controller...")
        ctrl.init(test_params)
        print("✅ Controller initialized")
        
        # Check results
        print(f"use_database: {ctrl.use_database}")
        print(f"db_controller: {ctrl.db_controller}")
        print(f"obj_handler: {ctrl.obj_handler is not None}")
        print(f"events_processor: {ctrl.events_processor is not None}")
        
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal_init()



