#!/usr/bin/env python3
"""Test calculation directly to understand the 1300 issue"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from src.business.calculation_engine import CalculationEngine, CalculationContext
from src.parsing.type_table_parser import TypeTableLoader, TypeTableEntry
from datetime import date

def test_direct_calculation():
    """Test calculation directly"""
    
    print("=" * 80)
    print("TESTING DIRECT CALCULATION FOR 4SP=100")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Load type tables
    type_loader = TypeTableLoader(db_manager)
    sp_table, dp_table, cp_table = type_loader.load_all_tables()
    
    # Check SP column 4
    sp4_numbers = sp_table.get(4, set())
    print(f"1. SP COLUMN 4:")
    print(f"   Numbers: {sorted(sp4_numbers)}")
    print(f"   Count: {len(sp4_numbers)}")
    
    # Create calculation engine
    calc_engine = CalculationEngine(sp_table, dp_table, cp_table)
    
    # Create TYPE entry for 4SP=100
    type_entry = TypeTableEntry(column=4, table_type='SP', value=100)
    
    # Create context
    context = CalculationContext(
        customer_id=1,
        customer_name='test',
        entry_date=date.today(),
        bazar='TEST',
        source_data='4SP=100'
    )
    
    # Calculate
    result = calc_engine._calculate_type_entries(context, [type_entry])
    
    print(f"\n2. CALCULATION RESULT:")
    print(f"   Total: ₹{result['total']}")
    print(f"   Universal entries: {len(result['universal_entries'])}")
    
    # Check individual entries
    print(f"\n3. UNIVERSAL ENTRIES:")
    total_check = 0
    for i, entry in enumerate(result['universal_entries']):
        if i < 3:  # Show first 3
            print(f"   Entry {i+1}: Number {entry.number}, Value ₹{entry.value}")
        total_check += entry.value
    
    print(f"   ...")
    print(f"   Total of all entries: ₹{total_check}")
    
    print(f"\n4. ANALYSIS:")
    expected = len(sp4_numbers) * 100
    print(f"   Expected: {len(sp4_numbers)} × ₹100 = ₹{expected}")
    print(f"   Actual: ₹{result['total']}")
    
    if result['total'] == 1300:
        print(f"   ❌ BUG CONFIRMED: ₹1300 instead of ₹{expected}")
        print(f"   Inflated by: {1300/expected:.2f}x")
    elif result['total'] == expected:
        print(f"   ✅ Calculation is correct")
    else:
        print(f"   ❓ Unexpected result")

if __name__ == "__main__":
    test_direct_calculation()