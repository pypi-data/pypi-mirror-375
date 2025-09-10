#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_complete():
    """Complete journal test"""
    
    print("=== Complete Journal Test ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create journal widget
        journal = EventsJournalJson('EvilEyeData')
        
        print("✅ Journal widget created")
        
        # Test data loading
        print("\n📊 Data Summary:")
        print(f"   Total events: {journal.ds.get_total({})}")
        print(f"   Found events: {journal.ds.get_total({'event_type': 'found'})}")
        print(f"   Lost events: {journal.ds.get_total({'event_type': 'lost'})}")
        print(f"   Available dates: {journal.ds.list_available_dates()}")
        
        # Test sample data
        print("\n📋 Sample Data:")
        events = journal.ds.fetch(0, 3, {}, [])
        for i, ev in enumerate(events):
            print(f"   Event {i+1}:")
            print(f"     Type: {ev.get('event_type')}")
            print(f"     Time: {ev.get('ts')}")
            print(f"     Source: {ev.get('source_name')}")
            print(f"     Class: {ev.get('class_name')}")
            print(f"     Image: {ev.get('image_filename')}")
            print(f"     BBox: {ev.get('bounding_box')}")
        
        # Show window
        journal.show()
        
        print("\n🔧 Features to test:")
        print("   - Event type filtering (found/lost)")
        print("   - Date selection")
        print("   - Image display (if files exist)")
        print("   - Bounding box drawing")
        print("   - Data accuracy in table")
        
        print("\n✅ All systems operational")
        print("🖥️  Journal window opened. Close it to continue...")
        
        journal.ds.close()
        app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_complete()

