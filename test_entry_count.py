#!/usr/bin/env python3
"""Test to check how many entries are created"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.data_processor import DataProcessor, ProcessingContext
from datetime import date

def test_entry_count():
    """Test entry counts in the processing flow"""
    
    print("=" * 80)
    print("TESTING ENTRY COUNTS FOR 4SP=100")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    test_date = date.today().isoformat()
    test_bazar = 'T.O'
    
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    # Process input
    processor = DataProcessor(db_manager)
    context = ProcessingContext(
        customer_name='TestCount',
        bazar=test_bazar,
        entry_date=date.today(),
        input_text='4SP=100',
        validate_references=True,
        auto_create_customer=True
    )
    
    print("1. PROCESSING '4SP=100'")
    result = processor.process_mixed_input(context)
    
    print(f"   Success: {result.success}")
    if not result.success:
        print(f"   Error: {result.error_message}")
        print(f"   Validation errors: {result.validation_errors}")
        return
    
    # Check universal_log
    ul_all = db_manager.execute_query("""
        SELECT entry_type, COUNT(*) as count, SUM(value) as total
        FROM universal_log 
        WHERE bazar = ? AND entry_date = ?
        GROUP BY entry_type
    """, (test_bazar, test_date))
    
    print("\n2. UNIVERSAL_LOG ENTRIES BY TYPE:")
    for entry in ul_all:
        print(f"   {entry['entry_type']}: {entry['count']} entries, total value ₹{entry['total']}")
    
    # Check TYPE entries specifically
    type_entries = db_manager.execute_query("""
        SELECT number, value, source_line
        FROM universal_log 
        WHERE bazar = ? AND entry_date = ? AND entry_type = 'TYPE'
        ORDER BY number
    """, (test_bazar, test_date))
    
    print(f"\n3. TYPE ENTRIES IN UNIVERSAL_LOG:")
    print(f"   Total TYPE entries: {len(type_entries)}")
    if type_entries:
        # Check for duplicates
        seen = {}
        for entry in type_entries:
            key = entry['number']
            if key not in seen:
                seen[key] = 0
            seen[key] += 1
        
        duplicates = [(k, v) for k, v in seen.items() if v > 1]
        if duplicates:
            print("   ❌ DUPLICATE TYPE ENTRIES FOUND:")
            for num, count in duplicates:
                print(f"      Number {num} appears {count} times")
        else:
            print("   ✅ No duplicate TYPE entries")
        
        # Show first few
        for i, entry in enumerate(type_entries[:3]):
            print(f"   Entry {i+1}: Number={entry['number']}, Value=₹{entry['value']}, Source={entry['source_line']}")
    
    # Check pana_table
    pana_entries = db_manager.execute_query("""
        SELECT number, value
        FROM pana_table 
        WHERE bazar = ? AND entry_date = ?
        ORDER BY number
    """, (test_bazar, test_date))
    
    print(f"\n4. PANA_TABLE ENTRIES:")
    print(f"   Total entries: {len(pana_entries)}")
    if pana_entries:
        total_pana = sum(e['value'] for e in pana_entries)
        print(f"   Total value: ₹{total_pana}")
        
        # Check individual values
        unique_values = set(e['value'] for e in pana_entries)
        print(f"   Unique values: {sorted(unique_values)}")
        
        if 1300 in unique_values:
            print(f"   ❌ FOUND 1300 VALUES!")
            count_1300 = sum(1 for e in pana_entries if e['value'] == 1300)
            print(f"   Numbers with ₹1300: {count_1300}")
    
    # Theory check
    print(f"\n5. THEORY CHECK:")
    print(f"   SP column 4 has 12 numbers")
    print(f"   If each number gets ₹100: Total = 12 × ₹100 = ₹1200")
    print(f"   If each number gets ₹1300: Total = 12 × ₹1300 = ₹15600")
    print(f"   ₹1300 = 13 × ₹100")
    print(f"   This suggests each number is being updated 13 times!")

if __name__ == "__main__":
    test_entry_count()