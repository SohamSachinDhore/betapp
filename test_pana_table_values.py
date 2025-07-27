#!/usr/bin/env python3
"""Test to check individual pana table values for TYPE entries"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.calculation_engine import CalculationEngine, CalculationContext
from src.parsing.type_table_parser import TypeTableLoader, TypeTableEntry
from src.database.models import UniversalLogEntry, EntryType
from datetime import date

def test_pana_table_values():
    """Test individual pana table values"""
    
    print("=" * 80)
    print("TESTING PANA TABLE VALUES FOR 4SP=100")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    test_date = '2025-01-27'
    test_bazar = 'TEST'
    
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    # Load type tables
    type_loader = TypeTableLoader(db_manager)
    sp_table, dp_table, cp_table = type_loader.load_all_tables()
    
    # Get SP column 4 numbers
    sp4_numbers = sorted(sp_table.get(4, set()))
    print(f"1. SP COLUMN 4 has {len(sp4_numbers)} numbers")
    print(f"   Numbers: {sp4_numbers[:5]}... (showing first 5)")
    
    # Manually insert universal_log entries for 4SP=100
    print(f"\n2. INSERTING UNIVERSAL_LOG ENTRIES FOR 4SP=100")
    print(f"   Each number should get value = 100")
    
    for number in sp4_numbers:
        db_manager.execute_query("""
            INSERT INTO universal_log 
            (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
            VALUES (1, 'test', ?, ?, ?, 100, 'TYPE', '4SP=100')
        """, (test_date, test_bazar, number))
    
    print(f"   Inserted {len(sp4_numbers)} entries with value=100 each")
    
    # Check what's in pana_table
    print(f"\n3. CHECKING PANA_TABLE VALUES")
    pana_entries = db_manager.execute_query("""
        SELECT number, value FROM pana_table 
        WHERE bazar = ? AND entry_date = ?
        ORDER BY number
    """, (test_bazar, test_date))
    
    print(f"   Found {len(pana_entries)} entries in pana_table")
    
    # Show individual values
    print(f"\n4. INDIVIDUAL PANA TABLE VALUES:")
    all_correct = True
    for i, entry in enumerate(pana_entries):
        if i < 5:  # Show first 5
            status = "✅" if entry['value'] == 100 else "❌"
            print(f"   {status} Number {entry['number']}: ₹{entry['value']}")
        
        if entry['value'] != 100:
            all_correct = False
            if entry['value'] == 1300:
                print(f"   ❌ FOUND 1300 BUG: Number {entry['number']} has ₹1300 instead of ₹100")
    
    # Calculate totals
    total_pana = sum(e['value'] for e in pana_entries)
    expected_total = len(sp4_numbers) * 100
    
    print(f"\n5. TOTALS:")
    print(f"   Expected total: {len(sp4_numbers)} × ₹100 = ₹{expected_total}")
    print(f"   Actual total in pana_table: ₹{total_pana}")
    
    if not all_correct:
        print(f"\n   ❌ BUG CONFIRMED: Individual values are wrong!")
        avg_value = total_pana / len(pana_entries) if pana_entries else 0
        print(f"   Average value per entry: ₹{avg_value:.0f}")
    else:
        print(f"\n   ✅ All values are correct (₹100 each)")
    
    # Let's also check a specific number
    if sp4_numbers:
        test_number = sp4_numbers[0]
        print(f"\n6. DETAILED CHECK FOR NUMBER {test_number}:")
        
        # Check universal_log
        ul_entries = db_manager.execute_query("""
            SELECT value, source_line FROM universal_log 
            WHERE bazar = ? AND entry_date = ? AND number = ?
        """, (test_bazar, test_date, test_number))
        
        print(f"   Universal_log entries: {len(ul_entries)}")
        for entry in ul_entries:
            print(f"     - Value: ₹{entry['value']}, Source: {entry['source_line']}")
        
        # Check pana_table
        pana_entry = db_manager.execute_query("""
            SELECT value FROM pana_table 
            WHERE bazar = ? AND entry_date = ? AND number = ?
        """, (test_bazar, test_date, test_number))
        
        if pana_entry:
            print(f"   Pana_table value: ₹{pana_entry[0]['value']}")

if __name__ == "__main__":
    test_pana_table_values()