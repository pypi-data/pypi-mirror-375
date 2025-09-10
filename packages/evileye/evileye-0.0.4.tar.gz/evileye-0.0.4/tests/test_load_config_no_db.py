#!/usr/bin/env python3
"""
Test loading configuration without database.
"""

import json

def test_load_config():
    """Test loading configuration file without database."""
    
    print("🔍 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        # Load configuration
        with open('test_config_no_database.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        print(f"use_database: {config['controller']['use_database']}")
        
        # Test controller initialization
        from evileye.controller import controller
        ctrl = controller.Controller()
        print("✅ Controller created")
        
        # Initialize with config
        ctrl.init(config)
        print("✅ Controller initialized with config")
        
        # Check results
        print(f"Controller use_database: {ctrl.use_database}")
        print(f"Database controller: {ctrl.db_controller}")
        print(f"Object handler: {ctrl.obj_handler is not None}")
        print(f"Events processor: {ctrl.events_processor is not None}")
        
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load_config()



