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

def test_journal_images():
    app = QApplication(sys.argv)
    
    print("Testing JSON journal with image display...")
    
    # Test with existing data
    journal = EventsJournalJson('EvilEyeData')
    journal.show()
    
    print("JSON Journal window opened with image display.")
    print("Available dates:", journal.ds.list_available_dates())
    print("Total events:", journal.ds.get_total({}))
    
    # Test image paths
    events = journal.ds.fetch(0, 5, {}, [('ts', 'desc')])
    print(f"First 5 events with image paths:")
    for i, ev in enumerate(events):
        img_rel = ev.get('image_filename') or ''
        date_folder = ev.get('date_folder') or ''
        img_path = os.path.join('EvilEyeData', 'images', date_folder, img_rel)
        bbox = ev.get('bounding_box') or ''
        
        print(f"  Event {i+1}:")
        print(f"    Type: {ev.get('event_type')}")
        print(f"    Class: {ev.get('class_name')}")
        print(f"    Image path: {img_path}")
        print(f"    Image exists: {os.path.exists(img_path)}")
        print(f"    BBox: {bbox}")
    
    print("\nClose the window to continue...")
    app.exec()

if __name__ == "__main__":
    test_journal_images()



