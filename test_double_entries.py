#!/usr/bin/env python3
"""Test to investigate double entries in pivot table"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.data_processor import DataProcessor, ProcessingContext
from datetime import date

def test_double_entries():
    """Test double entries for PANA and DIRECT entries"""
    
    print("=" * 80)
    print("INVESTIGATING DOUBLE ENTRIES IN PIVOT TABLE")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Test cases
    test_cases = [
        {
            'name': 'PANA Entry',
            'input': '138+347+230+349+269=RS,,400',
            'expected_type': 'PANA'
        },
        {
            'name': 'DIRECT Entries',
            'input': '239=150\n456=150\n279=150\n170=150',
            'expected_type': 'DIRECT'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. TESTING {test_case['name']}:")
        print(f"   Input: {repr(test_case['input'])}")
        
        # Clear test data
        test_date = date.today().isoformat()
        test_bazar = 'T.O'
        customer_name = f'TestDouble{i}'
        
        db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ? AND customer_name = ?", 
                                (test_bazar, test_date, customer_name))
        db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", 
                                (test_bazar, test_date))
        
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
        
        if not result.success:
            print(f"   ❌ Processing failed: {result.error_message}")
            continue
        
        print(f"   ✅ Processing successful")
        
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
        
        # Check pana_table entries
        pana_entries = db_manager.execute_query("""
            SELECT number, value 
            FROM pana_table 
            WHERE bazar = ? AND entry_date = ?
            ORDER BY number
        """, (test_bazar, test_date))
        
        print(f"   Pana_table entries: {len(pana_entries)}")
        
        # Check for duplicates in pana_table
        number_counts = {}
        for entry in pana_entries:
            num = entry['number']
            if num not in number_counts:
                number_counts[num] = {'count': 0, 'total_value': 0}
            number_counts[num]['count'] += 1
            number_counts[num]['total_value'] += entry['value']
        
        duplicates = [(num, data) for num, data in number_counts.items() if data['count'] > 1]
        
        if duplicates:
            print(f"   ❌ DUPLICATE ENTRIES FOUND:")
            for num, data in duplicates:
                print(f"     Number {num}: appears {data['count']} times, total value ₹{data['total_value']}")
        else:
            print(f"   ✅ No duplicate entries in pana_table")
        
        # Show sample pana entries
        sample_pana = pana_entries[:5] if len(pana_entries) > 5 else pana_entries
        print(f"   Sample pana values: {[(p['number'], p['value']) for p in sample_pana]}")

def test_trigger_behavior():
    """Test if the database trigger is causing duplicates"""
    
    print(f"\n" + "=" * 80)
    print("TESTING DATABASE TRIGGER BEHAVIOR")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    test_date = '2025-01-28'
    test_bazar = 'T.O'
    test_number = 138
    
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    print(f"1. TESTING PANA ENTRY TRIGGER:")
    print(f"   Number: {test_number}, Value: ₹400")
    
    # Insert a PANA entry
    db_manager.execute_query("""
        INSERT INTO universal_log 
        (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
        VALUES (1, 'test_trigger', ?, ?, ?, 400, 'PANA', '138+347=RS,,400')
    """, (test_date, test_bazar, test_number))
    
    # Check pana_table
    pana_result = db_manager.execute_query("""
        SELECT number, value FROM pana_table 
        WHERE bazar = ? AND entry_date = ? AND number = ?
    """, (test_bazar, test_date, test_number))
    
    print(f"   After trigger: {len(pana_result)} entries")
    for entry in pana_result:
        print(f"     Number {entry['number']}: ₹{entry['value']}")
    
    print(f"\n2. TESTING DIRECT ENTRY TRIGGER:")
    
    # Clear and test DIRECT entry
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    test_number = 239
    print(f"   Number: {test_number}, Value: ₹150")
    
    # Insert a DIRECT entry
    db_manager.execute_query("""
        INSERT INTO universal_log 
        (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
        VALUES (1, 'test_trigger', ?, ?, ?, 150, 'DIRECT', '239=150')
    """, (test_date, test_bazar, test_number))
    
    # Check pana_table
    pana_result = db_manager.execute_query("""
        SELECT number, value FROM pana_table 
        WHERE bazar = ? AND entry_date = ? AND number = ?
    """, (test_bazar, test_date, test_number))
    
    print(f"   After trigger: {len(pana_result)} entries")
    for entry in pana_result:
        print(f"     Number {entry['number']}: ₹{entry['value']}")
    
    # Check the trigger condition
    trigger_sql = db_manager.execute_query("""
        SELECT sql FROM sqlite_master WHERE name='tr_update_pana_table'
    """)[0]['sql']
    
    print(f"\n3. TRIGGER ANALYSIS:")
    print(f"   Trigger condition includes PANA: {'PANA' in trigger_sql}")
    print(f"   Trigger condition includes DIRECT: {'DIRECT' in trigger_sql}")
    print(f"   Trigger uses ON CONFLICT: {'ON CONFLICT' in trigger_sql}")

if __name__ == "__main__":
    test_double_entries()
    test_trigger_behavior()