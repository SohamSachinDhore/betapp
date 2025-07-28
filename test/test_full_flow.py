#!/usr/bin/env python3
"""Test full flow from GUI input to pana table"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.data_processor import DataProcessor, ProcessingContext
from datetime import date

def test_full_flow():
    """Test the complete flow as it happens in GUI"""
    
    print("=" * 80)
    print("TESTING FULL FLOW FOR 4SP=100")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear ALL test data for a clean test
    test_date = date.today().isoformat()
    test_bazar = 'T.O'  # Using actual bazar like in GUI
    
    print(f"1. CLEARING ALL DATA FOR BAZAR '{test_bazar}' ON DATE '{test_date}'")
    db_manager.execute_query("DELETE FROM universal_log WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    db_manager.execute_query("DELETE FROM pana_table WHERE bazar = ? AND entry_date = ?", (test_bazar, test_date))
    
    # Check initial state
    initial_pana = db_manager.execute_query("""
        SELECT COUNT(*) as count, COALESCE(SUM(value), 0) as total 
        FROM pana_table 
        WHERE bazar = ? AND entry_date = ?
    """, (test_bazar, test_date))[0]
    
    print(f"\n2. INITIAL STATE:")
    print(f"   Pana table entries: {initial_pana['count']}")
    print(f"   Total value: ₹{initial_pana['total']}")
    
    # Process input using DataProcessor (like GUI does)
    processor = DataProcessor(db_manager)
    
    context = ProcessingContext(
        customer_name='TestCustomer',
        bazar=test_bazar,
        entry_date=date.today(),
        input_text='4SP=100',
        validate_references=True,
        auto_create_customer=True
    )
    
    print(f"\n3. PROCESSING '4SP=100' THROUGH DATA PROCESSOR")
    result = processor.process_mixed_input(context)
    
    print(f"   Success: {result.success}")
    print(f"   Type count: {result.type_count}")
    print(f"   Total value: ₹{result.total_value}")
    print(f"   Entries saved: {result.entries_saved}")
    
    if not result.success:
        print(f"   Error: {result.error_message}")
        return
    
    # Check universal_log
    print(f"\n4. CHECKING UNIVERSAL_LOG:")
    ul_entries = db_manager.execute_query("""
        SELECT number, value 
        FROM universal_log 
        WHERE bazar = ? AND entry_date = ? AND entry_type = 'TYPE'
        ORDER BY number
    """, (test_bazar, test_date))
    
    print(f"   Found {len(ul_entries)} TYPE entries")
    if ul_entries:
        # Show first few and check values
        for i, entry in enumerate(ul_entries[:5]):
            print(f"   Entry {i+1}: Number {entry['number']}, Value ₹{entry['value']}")
        if len(ul_entries) > 5:
            print(f"   ... and {len(ul_entries) - 5} more")
        
        # Check if all have value 100
        wrong_values = [e for e in ul_entries if e['value'] != 100]
        if wrong_values:
            print(f"   ❌ FOUND WRONG VALUES IN UNIVERSAL_LOG:")
            for e in wrong_values[:3]:
                print(f"      Number {e['number']} has ₹{e['value']} instead of ₹100")
    
    # Check pana_table
    print(f"\n5. CHECKING PANA_TABLE:")
    pana_entries = db_manager.execute_query("""
        SELECT number, value 
        FROM pana_table 
        WHERE bazar = ? AND entry_date = ?
        ORDER BY number
    """, (test_bazar, test_date))
    
    print(f"   Found {len(pana_entries)} entries")
    
    # Check individual values
    if pana_entries:
        print(f"\n   INDIVIDUAL VALUES:")
        wrong_count = 0
        for i, entry in enumerate(pana_entries):
            if entry['value'] != 100:
                wrong_count += 1
                if wrong_count <= 5:  # Show first 5 wrong values
                    print(f"   ❌ Number {entry['number']}: ₹{entry['value']} (should be ₹100)")
                    if entry['value'] == 1300:
                        print(f"      ^ THIS IS THE 1300 BUG!")
            elif i < 3:  # Show first 3 correct values
                print(f"   ✅ Number {entry['number']}: ₹{entry['value']}")
        
        if wrong_count > 5:
            print(f"   ... and {wrong_count - 5} more wrong values")
        
        # Summary
        total_pana = sum(e['value'] for e in pana_entries)
        expected_total = len(pana_entries) * 100
        
        print(f"\n   SUMMARY:")
        print(f"   Total entries: {len(pana_entries)}")
        print(f"   Expected total: {len(pana_entries)} × ₹100 = ₹{expected_total}")
        print(f"   Actual total: ₹{total_pana}")
        
        if wrong_count > 0:
            avg_value = total_pana / len(pana_entries)
            print(f"   Average value per entry: ₹{avg_value:.0f}")
            
            # Check if it's exactly 1300 per entry
            if all(e['value'] == 1300 for e in pana_entries):
                print(f"\n   ❌ ALL ENTRIES HAVE ₹1300!")
                print(f"   This is 13× the expected value")

if __name__ == "__main__":
    test_full_flow()