#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_filters():
    """Test journal filtering"""
    
    print("=== Journal Filtering Test ===")
    
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        ds = JsonLabelJournalDataSource('EvilEyeData')
        
        # Test different filters
        print("\n1. All Events:")
        all_events = ds.fetch(0, 5, {}, [])
        print(f"   Total: {len(all_events)}")
        for ev in all_events:
            print(f"     {ev.get('event_type')} - {ev.get('ts')} - {ev.get('source_name')}")
        
        print("\n2. Found Events Only:")
        found_events = ds.fetch(0, 5, {'event_type': 'found'}, [])
        print(f"   Total: {len(found_events)}")
        for ev in found_events:
            print(f"     {ev.get('event_type')} - {ev.get('ts')} - {ev.get('source_name')}")
        
        print("\n3. Lost Events Only:")
        lost_events = ds.fetch(0, 5, {'event_type': 'lost'}, [])
        print(f"   Total: {len(lost_events)}")
        for ev in lost_events:
            print(f"     {ev.get('event_type')} - {ev.get('ts')} - {ev.get('source_name')}")
        
        print("\n4. Source Filter:")
        source_events = ds.fetch(0, 5, {'source_name': 'Cam5'}, [])
        print(f"   Total: {len(source_events)}")
        for ev in source_events:
            print(f"     {ev.get('event_type')} - {ev.get('ts')} - {ev.get('source_name')}")
        
        print("\n5. Combined Filter:")
        combined_events = ds.fetch(0, 5, {'event_type': 'found', 'source_name': 'Cam5'}, [])
        print(f"   Total: {len(combined_events)}")
        for ev in combined_events:
            print(f"     {ev.get('event_type')} - {ev.get('ts')} - {ev.get('source_name')}")
        
        ds.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_filters()

