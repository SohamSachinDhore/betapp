#!/usr/bin/env python3
"""Test to confirm the double processing issue"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from datetime import date

def test_double_processing():
    """Test if TYPE entries are being processed twice"""
    
    print("=" * 80)
    print("TESTING DOUBLE PROCESSING THEORY")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    test_date = '2025-01-28'
    test_bazar = 'T.O'
    test_number = 130  # First number in SP column 4
    
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    print("1. STEP-BY-STEP SIMULATION:")
    print(f"   Testing with SP4 number {test_number}, value ₹100")
    
    # Step 1: Insert ONE universal_log entry (like the calculation engine does)
    print(f"\n2. INSERTING UNIVERSAL_LOG ENTRY:")
    db_manager.execute_query("""
        INSERT INTO universal_log 
        (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
        VALUES (1, 'test', ?, ?, ?, 100, 'TYPE', '4SP=100')
    """, (test_date, test_bazar, test_number))
    
    # Check pana_table after trigger
    pana_result = db_manager.execute_query("""
        SELECT value FROM pana_table WHERE bazar = ? AND entry_date = ? AND number = ?
    """, (test_bazar, test_date, test_number))
    
    trigger_value = pana_result[0]['value'] if pana_result else 0
    print(f"   After trigger: ₹{trigger_value}")
    
    # Step 2: Manual expansion (like data_processor.py does)
    print(f"\n3. MANUAL EXPANSION (what data_processor.py does):")
    
    # Get SP4 numbers (what _expand_type_entry would return)
    sp4_numbers = db_manager.execute_query("""
        SELECT number FROM type_table_sp WHERE column_number = 4 ORDER BY row_number
    """)
    sp4_list = [row['number'] for row in sp4_numbers]
    
    print(f"   _expand_type_entry would return {len(sp4_list)} numbers for SP4")
    print(f"   Each would be updated with ₹100")
    
    # Simulate what the manual expansion does for our test number
    manual_updates = 0
    for num in sp4_list:
        if num == test_number:
            db_manager.update_pana_table_entry(test_bazar, test_date, num, 100)
            manual_updates += 1
    
    print(f"   Manual updates for number {test_number}: {manual_updates}")
    
    # Check final value
    final_result = db_manager.execute_query("""
        SELECT value FROM pana_table WHERE bazar = ? AND entry_date = ? AND number = ?
    """, (test_bazar, test_date, test_number))
    
    final_value = final_result[0]['value'] if final_result else 0
    print(f"   Final value: ₹{final_value}")
    
    print(f"\n4. ANALYSIS:")
    print(f"   Trigger added: ₹{trigger_value}")
    print(f"   Manual updates: {manual_updates} × ₹100 = ₹{manual_updates * 100}")
    print(f"   Expected total: ₹{trigger_value + (manual_updates * 100)}")
    print(f"   Actual total: ₹{final_value}")
    
    if final_value == trigger_value + (manual_updates * 100):
        print(f"   ✅ THEORY CONFIRMED: Double processing!")
    else:
        print(f"   ❌ Theory doesn't fully explain the issue")
    
    # Step 3: Test with all SP4 numbers like the real scenario
    print(f"\n5. FULL SP4 TEST:")
    
    # Clear again
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    # Insert all 12 universal_log entries (like calculation engine does)
    for num in sp4_list:
        db_manager.execute_query("""
            INSERT INTO universal_log 
            (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
            VALUES (1, 'test', ?, ?, ?, 100, 'TYPE', '4SP=100')
        """, (test_date, test_bazar, num))
    
    # Check after triggers
    trigger_total = db_manager.execute_query("""
        SELECT SUM(value) as total FROM pana_table WHERE bazar = ? AND entry_date = ?
    """, (test_bazar, test_date))[0]['total']
    
    print(f"   After triggers: ₹{trigger_total} (expected ₹{len(sp4_list) * 100})")
    
    # Now do manual expansion for each of the 12 universal_log entries
    manual_total = 0
    ul_entries = db_manager.execute_query("""
        SELECT number, source_line FROM universal_log 
        WHERE bazar = ? AND entry_date = ? AND entry_type = 'TYPE'
    """, (test_bazar, test_date))
    
    print(f"   Found {len(ul_entries)} TYPE entries in universal_log")
    
    for entry in ul_entries:
        # Each entry would cause _expand_type_entry to return all 12 SP4 numbers
        for num in sp4_list:
            db_manager.update_pana_table_entry(test_bazar, test_date, num, 100)
            manual_total += 100
    
    print(f"   Manual expansion: {len(ul_entries)} entries × {len(sp4_list)} numbers × ₹100 = ₹{manual_total}")
    
    # Check final
    final_total = db_manager.execute_query("""
        SELECT SUM(value) as total FROM pana_table WHERE bazar = ? AND entry_date = ?
    """, (test_bazar, test_date))[0]['total']
    
    print(f"   Final total: ₹{final_total}")
    print(f"   Expected: ₹{trigger_total + manual_total}")
    
    if final_total == trigger_total + manual_total:
        print(f"   ✅ DOUBLE PROCESSING CONFIRMED!")
        print(f"   Each number gets: Trigger(₹100) + Manual(12×₹100) = ₹1300")

if __name__ == "__main__":
    test_double_processing()