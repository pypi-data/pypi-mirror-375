#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_mapping():
    """Test journal data mapping"""
    
    print("=== Journal Mapping Test ===")
    
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        ds = JsonLabelJournalDataSource('EvilEyeData')
        
        # Test raw data loading
        print("\n1. Raw Data Loading:")
        ds._load_cache()
        print(f"   Cache size: {len(ds._cache)}")
        
        # Check for None values in ts field
        none_ts_count = 0
        for ev in ds._cache:
            if ev.get('ts') is None:
                none_ts_count += 1
                print(f"   Found None ts in event: {ev.get('event_id')}")
        
        print(f"   Events with None ts: {none_ts_count}")
        
        # Test mapping with sample data
        print("\n2. Sample Data Mapping:")
        
        # Sample found event
        found_item = {
            "object_id": 1,
            "frame_id": 95,
            "timestamp": "2025-09-01T15:14:56.790676",
            "image_filename": "detected_frames/test_found.jpeg",
            "bounding_box": {"x": 298, "y": 1, "width": 234, "height": 509},
            "source_id": 4,
            "source_name": "Cam5",
            "class_id": 0,
            "class_name": "person"
        }
        
        mapped_found = ds._map_item(found_item, 'found', '2025_09_01', 0)
        print(f"   Found event mapping:")
        print(f"     ts: {mapped_found.get('ts')}")
        print(f"     event_type: {mapped_found.get('event_type')}")
        print(f"     image_filename: {mapped_found.get('image_filename')}")
        
        # Sample lost event
        lost_item = {
            "object_id": 1,
            "frame_id": 93,
            "detected_timestamp": "2025-09-01T15:14:56.790676",
            "lost_timestamp": "2025-09-01T15:14:58.555991",
            "image_filename": "lost_frames/test_lost.jpeg",
            "bounding_box": {"x": 319, "y": 1, "width": 234, "height": 407},
            "source_id": 4,
            "source_name": "Cam5",
            "class_id": 0,
            "class_name": "person"
        }
        
        mapped_lost = ds._map_item(lost_item, 'lost', '2025_09_01', 0)
        print(f"   Lost event mapping:")
        print(f"     ts: {mapped_lost.get('ts')}")
        print(f"     event_type: {mapped_lost.get('event_type')}")
        print(f"     image_filename: {mapped_lost.get('image_filename')}")
        
        # Test sorting
        print("\n3. Sorting Test:")
        test_items = [
            {'ts': '2025-09-01T15:24:30.977061', 'event_type': 'found'},
            {'ts': None, 'event_type': 'lost'},
            {'ts': '2025-09-01T15:24:29.807639', 'event_type': 'found'},
        ]
        
        sorted_items = ds._apply_sort(test_items, [('ts', 'desc')])
        print(f"   Sorted items:")
        for i, item in enumerate(sorted_items):
            print(f"     {i+1}. ts={item.get('ts')}, type={item.get('event_type')}")
        
        ds.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_mapping()



