#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_journal_button_logic():
    """Test the journal button configuration logic without creating full windows"""
    
    # Test 1: use_database = True
    print("=== Test 1: use_database = True ===")
    use_database = True
    db_journal_win = "DatabaseJournalWindow"  # Mock
    
    if use_database:
        button_enabled = True
        button_text = "&DB journal"
        button_tooltip = "Open database events journal"
    else:
        if db_journal_win is not None:
            button_enabled = True
            button_text = "&Journal"
            button_tooltip = "Open events journal (JSON mode)"
        else:
            button_enabled = False
            button_text = "&Journal"
            button_tooltip = "Journal is not available (database disabled)"
    
    print(f"DB mode - Button enabled: {button_enabled}")
    print(f"DB mode - Button text: {button_text}")
    print(f"DB mode - Button tooltip: {button_tooltip}")
    
    # Test 2: use_database = False, journal created successfully
    print("\n=== Test 2: use_database = False, journal created ===")
    use_database = False
    db_journal_win = "EventsJournalJson"  # Mock
    
    if use_database:
        button_enabled = True
        button_text = "&DB journal"
        button_tooltip = "Open database events journal"
    else:
        if db_journal_win is not None:
            button_enabled = True
            button_text = "&Journal"
            button_tooltip = "Open events journal (JSON mode)"
        else:
            button_enabled = False
            button_text = "&Journal"
            button_tooltip = "Journal is not available (database disabled)"
    
    print(f"JSON mode - Button enabled: {button_enabled}")
    print(f"JSON mode - Button text: {button_text}")
    print(f"JSON mode - Button tooltip: {button_tooltip}")
    
    # Test 3: use_database = False, journal creation failed
    print("\n=== Test 3: use_database = False, journal creation failed ===")
    use_database = False
    db_journal_win = None  # Mock
    
    if use_database:
        button_enabled = True
        button_text = "&DB journal"
        button_tooltip = "Open database events journal"
    else:
        if db_journal_win is not None:
            button_enabled = True
            button_text = "&Journal"
            button_tooltip = "Open events journal (JSON mode)"
        else:
            button_enabled = False
            button_text = "&Journal"
            button_tooltip = "Journal is not available (database disabled)"
    
    print(f"Failed mode - Button enabled: {button_enabled}")
    print(f"Failed mode - Button text: {button_text}")
    print(f"Failed mode - Button tooltip: {button_tooltip}")
    
    print("\n=== Expected behavior ===")
    print("1. use_database=True: Button enabled, text='&DB journal'")
    print("2. use_database=False + journal exists: Button enabled, text='&Journal'")
    print("3. use_database=False + no journal: Button disabled, text='&Journal'")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_journal_button_logic()



