#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
    from PyQt6.QtCore import Qt
    pyqt_version = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    pyqt_version = 5

from evileye.visualization_modules.main_window import MainWindow

def test_journal_button_behavior():
    app = QApplication(sys.argv)
    
    # Test 1: use_database = True
    print("=== Test 1: use_database = True ===")
    class MockControllerDB:
        def __init__(self):
            self.use_database = True
            self.database_config = {
                'database': {
                    'image_dir': 'EvilEyeData',
                    'database_name': 'test_db',
                    'host_name': 'localhost',
                    'port': 5432,
                    'user_name': 'test_user',
                    'password': 'test_pass'
                },
                'database_adapters': {
                    'objects': {
                        'table_name': 'objects'
                    }
                },
                'tables': {
                    'objects': 'objects'
                }
            }
            self.enable_close_from_gui = True
            self.show_main_gui = True
            self.show_journal = False
            
        def is_running(self):
            return True
            
        def set_current_main_widget_size(self, width, height):
            pass
    
    controller_db = MockControllerDB()
    
    config = {
        'visualizer': {
            'num_height': 1,
            'num_width': 1
        },
        'pipeline': {
            'sources': [
                {
                    'source_ids': [0]
                }
            ]
        },
        'events_detectors': {
            'ZoneEventsDetector': {
                'sources': {}
            }
        }
    }
    
    main_window_db = MainWindow(controller_db, 'test_config.json', config, 800, 600)
    print(f"DB mode - Button enabled: {main_window_db.db_journal.isEnabled()}")
    print(f"DB mode - Button text: {main_window_db.db_journal.text()}")
    print(f"DB mode - Button tooltip: {main_window_db.db_journal.toolTip()}")
    main_window_db.close()
    
    # Test 2: use_database = False, journal created successfully
    print("\n=== Test 2: use_database = False, journal created ===")
    class MockControllerJSON:
        def __init__(self):
            self.use_database = False
            self.database_config = {
                'database': {
                    'image_dir': 'EvilEyeData'
                }
            }
            self.enable_close_from_gui = True
            self.show_main_gui = True
            self.show_journal = False
            
        def is_running(self):
            return True
            
        def set_current_main_widget_size(self, width, height):
            pass
    
    controller_json = MockControllerJSON()
    
    main_window_json = MainWindow(controller_json, 'test_config.json', config, 800, 600)
    print(f"JSON mode - Button enabled: {main_window_json.db_journal.isEnabled()}")
    print(f"JSON mode - Button text: {main_window_json.db_journal.text()}")
    print(f"JSON mode - Button tooltip: {main_window_json.db_journal.toolTip()}")
    main_window_json.close()
    
    # Test 3: use_database = False, journal creation failed
    print("\n=== Test 3: use_database = False, journal creation failed ===")
    class MockControllerFailed:
        def __init__(self):
            self.use_database = False
            self.database_config = {
                'database': {
                    'image_dir': '/invalid/path/that/will/fail'
                }
            }
            self.enable_close_from_gui = True
            self.show_main_gui = True
            self.show_journal = False
            
        def is_running(self):
            return True
            
        def set_current_main_widget_size(self, width, height):
            pass
    
    controller_failed = MockControllerFailed()
    
    main_window_failed = MainWindow(controller_failed, 'test_config.json', config, 800, 600)
    print(f"Failed mode - Button enabled: {main_window_failed.db_journal.isEnabled()}")
    print(f"Failed mode - Button text: {main_window_failed.db_journal.text()}")
    print(f"Failed mode - Button tooltip: {main_window_failed.db_journal.toolTip()}")
    main_window_failed.close()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_journal_button_behavior()
