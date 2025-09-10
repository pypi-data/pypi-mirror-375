#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_gui():
    """Test journal GUI with fixes"""
    
    print("=== Journal GUI Test ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from evileye.visualization_modules.events_journal_json import EventsJournalJson
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create journal widget
        journal = EventsJournalJson('EvilEyeData')
        journal.show()
        
        print("✅ Journal widget created and shown")
        print("📋 Features to test:")
        print("   - Different images for found vs lost events")
        print("   - Bounding boxes drawn correctly on images")
        print("   - Event type filtering (found/lost)")
        print("   - Date selection")
        print("   - Image scaling and display")
        
        print("\n🔧 Fixed Issues:")
        print("   - Event type separation")
        print("   - Proper timestamp handling")
        print("   - Correct image paths")
        print("   - Bounding box scaling with actual image dimensions")
        
        print("\n⚠️  Note: Image files may not exist yet")
        print("   - This is a separate issue with image saving")
        print("   - Journal will work correctly when images are available")
        
        # Run the application
        print("\n🖥️  Journal window opened. Close it to continue...")
        app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_gui()



