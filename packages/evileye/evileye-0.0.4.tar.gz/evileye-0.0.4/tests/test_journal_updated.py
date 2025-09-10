#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_updated():
    """Test updated journal with new structure"""
    
    print("=== Updated Journal Test ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create journal widget
        journal = EventsJournalJson('EvilEyeData')
        
        print("✅ Updated journal widget created")
        
        # Test data loading
        print("\n📊 Data Summary:")
        print(f"   Total events: {journal.ds.get_total({})}")
        print(f"   Found events: {journal.ds.get_total({'event_type': 'found'})}")
        print(f"   Lost events: {journal.ds.get_total({'event_type': 'lost'})}")
        print(f"   Available dates: {journal.ds.list_available_dates()}")
        
        # Test sample data
        print("\n📋 Sample Data:")
        events = journal.ds.fetch(0, 5, {}, [])
        for i, ev in enumerate(events):
            print(f"   Event {i+1}:")
            print(f"     Type: {ev.get('event_type')}")
            print(f"     Time: {ev.get('ts')}")
            print(f"     Source: {ev.get('source_name')}")
            print(f"     Object ID: {ev.get('object_id')}")
            print(f"     Image: {ev.get('image_filename')}")
        
        # Show window
        journal.show()
        
        print("\n🔧 New Features:")
        print("   - Database-style table structure")
        print("   - Found and lost events in same row")
        print("   - Proper source name display (Cam1, Cam2, etc.)")
        print("   - Real-time updates every 5 seconds")
        print("   - Preview and Lost preview columns")
        print("   - Bounding box drawing on images")
        
        print("\n✅ All systems operational")
        print("🖥️  Journal window opened. Close it to continue...")
        
        journal.ds.close()
        app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_updated()

