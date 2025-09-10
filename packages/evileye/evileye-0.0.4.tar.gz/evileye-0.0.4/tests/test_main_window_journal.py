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

from evileye.visualization_modules.main_window import MainWindow
from evileye.controller.controller import Controller

def test_main_window_journal():
    app = QApplication(sys.argv)
    
    # Create a mock controller with use_database=False
    class MockController:
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
    
    controller = MockController()
    
    # Test config
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
    
    # Create main window
    main_window = MainWindow(controller, 'test_config.json', config, 800, 600)
    main_window.show()
    
    print("Main window with JSON journal opened. Close it to continue.")
    
    # Run the application
    app.exec()

if __name__ == "__main__":
    test_main_window_journal()
