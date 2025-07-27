#!/usr/bin/env python3
"""Test to understand the 1300 issue with triggers"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from datetime import date

def test_trigger_issue():
    """Test trigger behavior"""
    
    print("=" * 80)
    print("TESTING TRIGGER BEHAVIOR")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    test_date = '2025-01-28'
    test_bazar = 'TEST'
    test_number = 130  # First number in SP column 4
    
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    print(f"1. INITIAL STATE - Pana table for number {test_number}:")
    check_pana_value(db_manager, test_bazar, test_date, test_number)
    
    # Insert ONE universal_log entry
    print(f"\n2. INSERTING ONE UNIVERSAL_LOG ENTRY (TYPE, value=100):")
    db_manager.execute_query("""
        INSERT INTO universal_log 
        (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
        VALUES (1, 'test', ?, ?, ?, 100, 'TYPE', '4SP=100')
    """, (test_date, test_bazar, test_number))
    
    print(f"   After trigger:")
    check_pana_value(db_manager, test_bazar, test_date, test_number)
    
    # Manually update pana_table (like the code does)
    print(f"\n3. MANUALLY UPDATING PANA_TABLE (value=100):")
    db_manager.update_pana_table_entry(test_bazar, test_date, test_number, 100)
    
    print(f"   After manual update:")
    check_pana_value(db_manager, test_bazar, test_date, test_number)
    
    # Let's check the entire flow for all SP4 numbers
    print(f"\n4. CHECKING FULL SP4 FLOW:")
    
    # Get SP4 numbers
    sp4_numbers = db_manager.execute_query("""
        SELECT number FROM type_table_sp WHERE column_number = 4 ORDER BY row_number
    """)
    sp4_list = [row['number'] for row in sp4_numbers]
    
    print(f"   SP4 has {len(sp4_list)} numbers")
    
    # Clear and test full flow
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    # Insert all universal_log entries
    for num in sp4_list:
        db_manager.execute_query("""
            INSERT INTO universal_log 
            (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
            VALUES (1, 'test', ?, ?, ?, 100, 'TYPE', '4SP=100')
        """, (test_date, test_bazar, num))
    
    # Check pana table after triggers
    pana_total = db_manager.execute_query("""
        SELECT SUM(value) as total FROM pana_table WHERE bazar = ? AND entry_date = ?
    """, (test_bazar, test_date))[0]['total']
    
    print(f"   After triggers only: Total = ₹{pana_total} (expected ₹{len(sp4_list) * 100})")
    
    # Now do manual updates (like the buggy code)
    for num in sp4_list:
        db_manager.update_pana_table_entry(test_bazar, test_date, num, 100)
    
    pana_total2 = db_manager.execute_query("""
        SELECT SUM(value) as total FROM pana_table WHERE bazar = ? AND entry_date = ?
    """, (test_bazar, test_date))[0]['total']
    
    print(f"   After manual updates: Total = ₹{pana_total2}")
    
    # Check individual values
    sample_values = db_manager.execute_query("""
        SELECT number, value FROM pana_table 
        WHERE bazar = ? AND entry_date = ? 
        ORDER BY number LIMIT 3
    """, (test_bazar, test_date))
    
    print(f"\n   Sample individual values:")
    for entry in sample_values:
        print(f"     Number {entry['number']}: ₹{entry['value']}")
    
    if pana_total2 == 15600:  # 12 * 1300
        print(f"\n   ❌ CONFIRMED: Each number has ₹1300")
        print(f"   This suggests 13 updates per number!")

def check_pana_value(db_manager, bazar, date, number):
    """Check pana table value for a specific number"""
    result = db_manager.execute_query("""
        SELECT value FROM pana_table WHERE bazar = ? AND entry_date = ? AND number = ?
    """, (bazar, date, number))
    
    if result:
        print(f"     Pana table: Number {number} = ₹{result[0]['value']}")
    else:
        print(f"     Pana table: Number {number} = Not found")

if __name__ == "__main__":
    test_trigger_issue()