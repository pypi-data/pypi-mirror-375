#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_data_source():
    """Test data source functionality"""
    
    print("=== Test Data Source ===")
    
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        # Create data source
        base_dir = "EvilEyeData"
        ds = JsonLabelJournalDataSource(base_dir)
        
        print(f"✅ Data source created with base_dir: {base_dir}")
        
        # Test available dates
        dates = ds.list_available_dates()
        print(f"📅 Available dates: {dates}")
        
        # Test fetching data
        if dates:
            # Use first available date
            test_date = dates[0]
            print(f"📊 Testing with date: {test_date}")
            
            ds.set_date(test_date)
            data = ds.fetch(0, 10, {}, [])
            print(f"📈 Fetched {len(data)} records")
            
            if data:
                print("📋 Sample data:")
                for i, record in enumerate(data[:3]):
                    print(f"  Record {i+1}: {record}")
            else:
                print("❌ No data found")
        else:
            print("❌ No dates available")
            
        # Test without date filter
        print("\n--- Testing without date filter ---")
        ds.set_date(None)
        data = ds.fetch(0, 10, {}, [])
        print(f"📈 Fetched {len(data)} records (no date filter)")
        
        if data:
            print("📋 Sample data:")
            for i, record in enumerate(data[:3]):
                print(f"  Record {i+1}: {record}")
        else:
            print("❌ No data found without date filter")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_source()
