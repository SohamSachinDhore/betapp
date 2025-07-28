#!/usr/bin/env python3
"""Test to reproduce the 4SP=100 bug where it adds 1300 instead of 100"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.data_processor import DataProcessor, ProcessingContext
from datetime import date

def test_4sp_bug():
    """Test the 4SP=100 bug"""
    
    print("=" * 80)
    print("TESTING 4SP=100 BUG")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    db_manager.execute_query("DELETE FROM universal_log WHERE customer_name = 'sp4_test'")
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = 'TEST' AND entry_date = '2025-01-27'")
    db_manager.execute_query("DELETE FROM customers WHERE name = 'sp4_test'")
    
    # Add test customer
    db_manager.execute_query("INSERT INTO customers (name) VALUES ('sp4_test')")
    
    # Get SP column 4 numbers
    sp4_numbers = db_manager.execute_query("""
        SELECT number FROM type_table_sp 
        WHERE column_number = 4 
        ORDER BY row_number
    """)
    sp4_list = [row['number'] for row in sp4_numbers]
    
    print(f"1. SP COLUMN 4 INFO:")
    print(f"   Numbers: {sp4_list}")
    print(f"   Count: {len(sp4_list)}")
    
    # Process the input "4SP=100"
    processor = DataProcessor(db_manager)
    context = ProcessingContext(
        customer_name='sp4_test',
        bazar='TEST',
        entry_date=date(2025, 1, 27),
        input_text='4SP=100',
        validate_references=True,
        auto_create_customer=False
    )
    
    print(f"\n2. PROCESSING '4SP=100'...")
    result = processor.process_mixed_input(context)
    
    print(f"\n3. PROCESSING RESULT:")
    print(f"   Success: {result.success}")
    print(f"   Total value: ₹{result.total_value}")
    print(f"   Type count: {result.type_count}")
    
    # Check universal_log
    universal_entries = db_manager.execute_query("""
        SELECT number, value FROM universal_log 
        WHERE customer_name = 'sp4_test' AND entry_type = 'TYPE'
        ORDER BY number
    """)
    
    print(f"\n4. UNIVERSAL_LOG ENTRIES:")
    print(f"   Total entries: {len(universal_entries)}")
    if universal_entries:
        print(f"   Sample entries:")
        for entry in universal_entries[:3]:
            print(f"     Number {entry['number']}: ₹{entry['value']}")
        total_universal = sum(e['value'] for e in universal_entries)
        print(f"   Total value in universal_log: ₹{total_universal}")
    
    # Check pana_table
    pana_entries = db_manager.execute_query("""
        SELECT number, value FROM pana_table 
        WHERE bazar = 'TEST' AND entry_date = '2025-01-27'
        ORDER BY number
    """)
    
    print(f"\n5. PANA_TABLE ENTRIES:")
    print(f"   Total entries: {len(pana_entries)}")
    if pana_entries:
        print(f"   Sample entries:")
        for entry in pana_entries[:3]:
            print(f"     Number {entry['number']}: ₹{entry['value']}")
        total_pana = sum(e['value'] for e in pana_entries)
        print(f"   Total value in pana_table: ₹{total_pana}")
    
    print(f"\n6. ANALYSIS:")
    expected_total = len(sp4_list) * 100
    print(f"   Expected: {len(sp4_list)} numbers × ₹100 = ₹{expected_total}")
    print(f"   Actual (from processing): ₹{result.total_value}")
    
    if result.total_value == 1300:
        print(f"   ❌ BUG CONFIRMED: Got ₹1300 instead of ₹{expected_total}")
        print(f"   Ratio: {1300 / expected_total} = {1300 / expected_total:.2f}x")
    elif result.total_value == expected_total:
        print(f"   ✅ Working correctly: ₹{result.total_value}")
    else:
        print(f"   ❓ Unexpected result: ₹{result.total_value}")

if __name__ == "__main__":
    test_4sp_bug()