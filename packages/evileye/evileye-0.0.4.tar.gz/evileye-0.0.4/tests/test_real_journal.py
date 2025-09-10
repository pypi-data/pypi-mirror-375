#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    pyqt_version = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    pyqt_version = 5

from evileye.visualization_modules.events_journal_json import EventsJournalJson

def test_real_journal():
    app = QApplication(sys.argv)
    
    print("Testing JSON journal with real data...")
    
    # Test with existing data
    journal = EventsJournalJson('EvilEyeData')
    journal.show()
    
    print("JSON Journal window opened.")
    print("Available dates:", journal.ds.list_available_dates())
    print("Total events:", journal.ds.get_total({}))
    
    # Test filtering
    found_events = journal.ds.get_total({'event_type': 'found'})
    lost_events = journal.ds.get_total({'event_type': 'lost'})
    print(f"Found events: {found_events}")
    print(f"Lost events: {lost_events}")
    
    # Test fetching
    events = journal.ds.fetch(0, 10, {}, [('ts', 'desc')])
    print(f"First 10 events: {len(events)}")
    for i, ev in enumerate(events[:3]):  # Show first 3
        print(f"  Event {i+1}: {ev.get('event_type')} - {ev.get('class_name')} - {ev.get('ts')}")
    
    print("\nClose the window to continue...")
    app.exec()

if __name__ == "__main__":
    test_real_journal()



