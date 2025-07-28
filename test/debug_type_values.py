#!/usr/bin/env python3
"""
Test to identify and fix the TYPE value storage issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from datetime import date

def test_type_value_issue():
    """Test to see how TYPE values are being stored"""
    
    print("=" * 80)
    print("TESTING TYPE VALUE STORAGE ISSUE")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear test data
    db_manager.execute_query("DELETE FROM universal_log WHERE customer_name = 'type_test'")
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = 'TEST' AND entry_date = '2025-07-27'")
    db_manager.execute_query("DELETE FROM customers WHERE name = 'type_test'")
    
    # Add test customer
    db_manager.execute_query("INSERT INTO customers (name) VALUES ('type_test')")
    customer_id = db_manager.execute_query("SELECT last_insert_rowid() as id")[0]['id']
    
    print(f"1. SETUP COMPLETE:")
    print(f"   Test customer ID: {customer_id}")
    
    # Get SP Column 1 numbers for reference
    sp_numbers = db_manager.execute_query("""
        SELECT number FROM type_table_sp 
        WHERE column_number = 1 
        ORDER BY row_number
    """)
    sp_numbers_list = [row['number'] for row in sp_numbers]
    print(f"   SP Column 1 has {len(sp_numbers_list)} numbers: {sp_numbers_list[:5]}...")
    
    print(f"\n2. SIMULATING TYPE ENTRY: '1SP=50'")
    print(f"   Expected behavior: Each number gets ₹50")
    print(f"   Expected total in pana_table: {len(sp_numbers_list)} × ₹50 = ₹{len(sp_numbers_list) * 50}")
    
    # Manually insert what the calculation engine should create
    print(f"\n3. INSERTING UNIVERSAL_LOG ENTRIES:")
    for i, number in enumerate(sp_numbers_list):
        db_manager.execute_query("""
            INSERT INTO universal_log 
            (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
            VALUES (?, 'type_test', '2025-07-27', 'TEST', ?, 50, 'TYPE', '1SP=50')
        """, [customer_id, number])
        if i < 3:  # Show first 3 only
            print(f"   Inserted: number={number}, value=50")
        elif i == 3:
            print(f"   ... and {len(sp_numbers_list)-3} more")
    
    print(f"   Total insertions: {len(sp_numbers_list)}")
    
    # Check what was stored in universal_log
    universal_entries = db_manager.execute_query("""
        SELECT number, value FROM universal_log 
        WHERE customer_name = 'type_test' AND entry_type = 'TYPE'
        ORDER BY number
    """)
    
    print(f"\n4. UNIVERSAL_LOG VERIFICATION:")
    print(f"   Records created: {len(universal_entries)}")
    if universal_entries:
        print(f"   Sample values: {[(e['number'], e['value']) for e in universal_entries[:3]]}")
        total_universal_value = sum(e['value'] for e in universal_entries)
        print(f"   Total value in universal_log: ₹{total_universal_value}")
    
    # Check what was stored in pana_table (via trigger)
    pana_entries = db_manager.execute_query("""
        SELECT number, value FROM pana_table 
        WHERE bazar = 'TEST' AND entry_date = '2025-07-27'
        ORDER BY number
    """)
    
    print(f"\n5. PANA_TABLE VERIFICATION:")
    print(f"   Records created: {len(pana_entries)}")
    if pana_entries:
        print(f"   Sample values: {[(e['number'], e['value']) for e in pana_entries[:3]]}")
        total_pana_value = sum(e['value'] for e in pana_entries)
        print(f"   Total value in pana_table: ₹{total_pana_value}")
        
        # Check if any values are incorrect
        incorrect_values = [e for e in pana_entries if e['value'] != 50]
        if incorrect_values:
            print(f"   ❌ INCORRECT VALUES FOUND: {incorrect_values[:5]}")
        else:
            print(f"   ✅ All values are correct (₹50 each)")
    
    # Check the database trigger
    trigger_sql = db_manager.execute_query("""
        SELECT sql FROM sqlite_master WHERE name='tr_update_pana_table'
    """)[0]['sql']
    
    print(f"\n6. DATABASE TRIGGER ANALYSIS:")
    print(f"   Trigger condition: {'TYPE' in trigger_sql}")
    print(f"   Trigger uses NEW.value directly: {'NEW.value' in trigger_sql}")
    
    print(f"\n7. CONCLUSION:")
    expected_total = len(sp_numbers_list) * 50
    actual_universal = sum(e['value'] for e in universal_entries) if universal_entries else 0
    actual_pana = sum(e['value'] for e in pana_entries) if pana_entries else 0
    
    print(f"   Expected total: ₹{expected_total}")
    print(f"   Universal_log total: ₹{actual_universal}")
    print(f"   Pana_table total: ₹{actual_pana}")
    
    if actual_universal == expected_total and actual_pana == expected_total:
        print(f"   ✅ VALUES ARE CORRECT")
    else:
        print(f"   ❌ VALUES ARE INCORRECT")
        
        if actual_universal != expected_total:
            print(f"      - Universal_log issue: expected ₹{expected_total}, got ₹{actual_universal}")
        if actual_pana != expected_total:
            print(f"      - Pana_table issue: expected ₹{expected_total}, got ₹{actual_pana}")

def test_calculation_engine_directly():
    """Test the calculation engine TYPE logic directly"""
    
    print(f"\n{'=' * 80}")
    print("TESTING CALCULATION ENGINE TYPE LOGIC")
    print(f"{'=' * 80}")
    
    try:
        from src.business.calculation_engine import CalculationEngine, CalculationContext
        from src.parsing.type_table_parser import TypeTableLoader
        from src.database.models import TypeTableEntry
        from datetime import date
        
        db_manager = DatabaseManager("data/rickymama.db")
        
        # Load type tables
        type_loader = TypeTableLoader(db_manager)
        sp_table, dp_table, cp_table = type_loader.load_all_tables()
        
        # Create calculation engine
        calc_engine = CalculationEngine(sp_table, dp_table, cp_table)
        
        # Create test TYPE entry
        type_entry = TypeTableEntry(column=1, table_type='SP', value=50)
        
        # Create calculation context
        context = CalculationContext(
            customer_id=1,
            customer_name='test_user',
            entry_date=date.today(),
            bazar='TEST',
            source_data='1SP=50'  # Add the missing source_data parameter
        )
        
        # Test the calculation
        result = calc_engine._calculate_type_entries(context, [type_entry])
        
        print(f"1. CALCULATION ENGINE TEST:")
        print(f"   Input: 1SP=50")
        print(f"   SP Column 1 numbers: {len(sp_table.get(1, set()))}")
        print(f"   Result total: ₹{result['total']}")
        print(f"   Universal entries created: {len(result['universal_entries'])}")
        
        # Check individual universal entries
        if result['universal_entries']:
            sample_entries = result['universal_entries'][:3]
            print(f"   Sample universal entries:")
            for entry in sample_entries:
                print(f"     - number={entry.number}, value={entry.value}")
        
        # Calculate expected vs actual
        expected_count = len(sp_table.get(1, set()))
        expected_total = expected_count * 50
        actual_total = result['total']
        actual_count = len(result['universal_entries'])
        
        print(f"\n2. ANALYSIS:")
        print(f"   Expected: {expected_count} entries × ₹50 = ₹{expected_total}")
        print(f"   Actual: {actual_count} entries, total = ₹{actual_total}")
        
        if actual_total == expected_total:
            print(f"   ✅ CALCULATION ENGINE IS CORRECT")
        else:
            print(f"   ❌ CALCULATION ENGINE HAS ISSUE")
            ratio = actual_total / expected_total if expected_total > 0 else 0
            print(f"   Ratio (actual/expected): {ratio:.2f}")
            
            if ratio > 1:
                print(f"   Issue: Total is being inflated (each number counted multiple times)")
            elif ratio < 1:
                print(f"   Issue: Total is being deflated")
        
    except Exception as e:
        print(f"   Error testing calculation engine: {e}")

if __name__ == "__main__":
    test_type_value_issue()
    test_calculation_engine_directly()
