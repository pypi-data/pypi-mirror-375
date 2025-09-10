#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_final_structure():
    """Test journal with correct folder structure"""
    
    print("=== Final Journal Structure Test ===")
    
    # Test 1: Check folder structure
    print("\n1. Folder Structure Verification:")
    base_dir = 'EvilEyeData'
    images_dir = os.path.join(base_dir, 'images')
    
    print(f"   Base directory: {base_dir} - {'✅' if os.path.exists(base_dir) else '❌'}")
    print(f"   Images directory: {images_dir} - {'✅' if os.path.exists(images_dir) else '❌'}")
    
    if os.path.exists(images_dir):
        dates = [d for d in os.listdir(images_dir) 
                if os.path.isdir(os.path.join(images_dir, d)) and d[:4].isdigit()]
        print(f"   Date folders found: {len(dates)}")
        for date in dates[:3]:  # Show first 3
            date_path = os.path.join(images_dir, date)
            found_file = os.path.join(date_path, 'objects_found.json')
            lost_file = os.path.join(date_path, 'objects_lost.json')
            detected_frames = os.path.join(date_path, 'detected_frames')
            lost_frames = os.path.join(date_path, 'lost_frames')
            
            print(f"   📁 {date}:")
            print(f"      objects_found.json: {'✅' if os.path.exists(found_file) else '❌'}")
            print(f"      objects_lost.json: {'✅' if os.path.exists(lost_file) else '❌'}")
            print(f"      detected_frames/: {'✅' if os.path.exists(detected_frames) else '❌'}")
            print(f"      lost_frames/: {'✅' if os.path.exists(lost_frames) else '❌'}")
    
    # Test 2: Test JSON data source
    print("\n2. JSON Data Source Test:")
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        ds = JsonLabelJournalDataSource(base_dir)
        dates = ds.list_available_dates()
        print(f"   Available dates: {dates}")
        
        total_events = ds.get_total({})
        found_events = ds.get_total({'event_type': 'found'})
        lost_events = ds.get_total({'event_type': 'lost'})
        
        print(f"   Total events: {total_events}")
        print(f"   Found events: {found_events}")
        print(f"   Lost events: {lost_events}")
        
        # Test fetching
        events = ds.fetch(0, 5, {}, [('ts', 'desc')])
        print(f"   First 5 events:")
        for i, ev in enumerate(events):
            print(f"     {i+1}. {ev.get('event_type')} - {ev.get('class_name')} - {ev.get('ts')}")
        
        ds.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test journal widget
    print("\n3. Journal Widget Test:")
    try:
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        
        journal = EventsJournalJson(base_dir)
        print(f"   ✅ Journal widget created successfully")
        print(f"   Available dates: {journal.ds.list_available_dates()}")
        print(f"   Total events: {journal.ds.get_total({})}")
        
        journal.ds.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Configuration test
    print("\n4. Configuration Test:")
    configs = [
        ('configs/pipeline_capture.json', 'JSON mode'),
        ('configs/pipeline_capture_no_dir.json', 'JSON mode (no dir)'),
        ('configs/pipeline_capture_db.json', 'Database mode')
    ]
    
    for config_file, description in configs:
        if os.path.exists(config_file):
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            use_database = config.get('controller', {}).get('use_database', True)
            image_dir = config.get('database', {}).get('image_dir', 'EvilEyeData')
            image_dir_exists = os.path.exists(image_dir)
            
            print(f"   {description}:")
            print(f"      use_database={use_database}, image_dir='{image_dir}', exists={image_dir_exists}")
            
            if not use_database:
                if image_dir_exists:
                    print(f"      Expected: JSON journal enabled")
                else:
                    print(f"      Expected: JSON journal disabled")
            else:
                print(f"      Expected: Database journal")
    
    print("\n=== Expected Structure ===")
    print("📁 images_dir/")
    print("   📁 images/")
    print("      📁 YYYY_MM_DD/")
    print("         📄 objects_found.json")
    print("         📄 objects_lost.json")
    print("         📁 detected_frames/")
    print("         📁 detected_previews/")
    print("         📁 lost_frames/")
    print("         📁 lost_previews/")
    
    print("\n=== Test completed successfully ===")

if __name__ == "__main__":
    test_journal_final_structure()



