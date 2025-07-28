#!/usr/bin/env python3
"""Test TIME table entry storage logic"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.data_processor import DataProcessor, ProcessingContext
from datetime import date

def test_time_entries():
    """Test TIME table entries for both multiplication and special formats"""
    
    print("=" * 80)
    print("INVESTIGATING TIME TABLE ENTRY STORAGE")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Test cases for TIME entries
    test_cases = [
        {
            'name': 'Multiplication Type',
            'input': '38x700\n83x700\n96x500\n92x200\n29x200',
            'expected_type': 'TIME'
        },
        {
            'name': 'Special Format',
            'input': '6 8 9 0==3300',
            'expected_type': 'TIME'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. TESTING {test_case['name']}:")
        print(f"   Input: {repr(test_case['input'])}")
        
        # Clear test data
        test_date = date.today().isoformat()
        test_bazar = 'T.O'
        customer_name = f'TestTime{i}'
        
        db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ? AND customer_name = ?", 
                                (test_bazar, test_date, customer_name))
        db_manager.execute_query("DELETE FROM time_table WHERE bazar = ? AND entry_date = ? AND customer_name = ?", 
                                (test_bazar, test_date, customer_name))
        
        # Process the input
        processor = DataProcessor(db_manager)
        context = ProcessingContext(
            customer_name=customer_name,
            bazar=test_bazar,
            entry_date=date.today(),
            input_text=test_case['input'],
            validate_references=True,
            auto_create_customer=True
        )
        
        result = processor.process_mixed_input(context)
        
        print(f"   Processing result: {'Success' if result.success else 'Failed'}")
        if not result.success:
            print(f"   Error: {result.error_message}")
            if result.validation_errors:
                print(f"   Validation errors: {result.validation_errors}")
            continue
        
        # Check universal_log entries
        ul_entries = db_manager.execute_query("""
            SELECT entry_type, number, value, source_line 
            FROM universal_log 
            WHERE bazar = ? AND entry_date = ? AND customer_name = ?
            ORDER BY entry_type, number
        """, (test_bazar, test_date, customer_name))
        
        print(f"   Universal_log entries: {len(ul_entries)}")
        for entry in ul_entries:
            print(f"     {entry['entry_type']}: {entry['number']} = ₹{entry['value']} (source: {entry['source_line']})")
        
        # Check time_table entries
        time_entries = db_manager.execute_query("""
            SELECT customer_name, bazar, entry_date, col_0, col_1, col_2, col_3, col_4, 
                   col_5, col_6, col_7, col_8, col_9
            FROM time_table 
            WHERE bazar = ? AND entry_date = ? AND customer_name = ?
        """, (test_bazar, test_date, customer_name))
        
        print(f"   Time_table entries: {len(time_entries)}")
        
        if time_entries:
            for entry in time_entries:
                print(f"     Customer: {entry['customer_name']}")
                columns = []
                for col_num in range(10):
                    col_name = f'col_{col_num}'
                    value = entry[col_name]
                    if value and value > 0:
                        columns.append(f"Col{col_num}=₹{value}")
                print(f"     Columns: {', '.join(columns) if columns else 'No data'}")
        else:
            print(f"     ❌ No entries found in time_table")
        
        # Check if there are any TIME_DIRECT entries that should trigger time table updates
        time_direct_entries = [e for e in ul_entries if e['entry_type'] == 'TIME_DIRECT']
        if time_direct_entries:
            print(f"   TIME_DIRECT entries found: {len(time_direct_entries)}")
            for entry in time_direct_entries:
                print(f"     TIME_DIRECT: Col{entry['number']} = ₹{entry['value']}")

def check_time_table_triggers():
    """Check database triggers for time_table"""
    
    print(f"\n" + "=" * 80)
    print("CHECKING TIME TABLE TRIGGERS")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Check for time table triggers
    triggers = db_manager.execute_query("""
        SELECT name, sql FROM sqlite_master 
        WHERE type='trigger' AND (sql LIKE '%time_table%' OR name LIKE '%time%')
    """)
    
    print(f"Time-related triggers found: {len(triggers)}")
    for trigger in triggers:
        print(f"\nTrigger: {trigger['name']}")
        print(f"SQL: {trigger['sql']}")

if __name__ == "__main__":
    test_time_entries()
    check_time_table_triggers()