#!/usr/bin/env python3
"""Test if parsing creates multiple entries"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.parsing.mixed_input_parser import MixedInputParser
from src.parsing.type_table_parser import TypeTableLoader, TypeTableValidator
from src.database.db_manager import DatabaseManager

def test_parsing():
    """Test if parser creates duplicate entries"""
    
    print("=" * 80)
    print("TESTING PARSER FOR 4SP=100")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Load type tables
    type_loader = TypeTableLoader(db_manager)
    sp_table, dp_table, cp_table = type_loader.load_all_tables()
    
    # Create validator
    type_validator = TypeTableValidator(sp_table, dp_table, cp_table)
    
    # Create parser
    parser = MixedInputParser(type_validator=type_validator)
    
    # Parse "4SP=100"
    print("1. PARSING '4SP=100':")
    try:
        result = parser.parse("4SP=100")
        
        print(f"   Parse successful: {not result.is_empty}")
        print(f"   Type entries: {len(result.type_entries) if result.type_entries else 0}")
        
        if result.type_entries:
            for i, entry in enumerate(result.type_entries):
                print(f"   Entry {i+1}: {entry.column}{entry.table_type}={entry.value}")
        
        # Check if there are duplicates
        if result.type_entries and len(result.type_entries) > 1:
            print(f"   ❌ MULTIPLE TYPE ENTRIES CREATED!")
        elif result.type_entries and len(result.type_entries) == 1:
            print(f"   ✅ Single TYPE entry created correctly")
            
    except Exception as e:
        print(f"   ❌ Parsing failed: {e}")
    
    # Test calculation engine directly
    print("\n2. TESTING CALCULATION ENGINE:")
    from src.business.calculation_engine import CalculationEngine, CalculationContext
    from datetime import date
    
    calc_engine = CalculationEngine(sp_table, dp_table, cp_table)
    
    # Create context
    context = CalculationContext(
        customer_id=1,
        customer_name='test',
        entry_date=date.today(),
        bazar='TEST',
        source_data='4SP=100'
    )
    
    # Test with single TYPE entry
    from src.database.models import TypeTableEntry
    type_entry = TypeTableEntry(column=4, table_type='SP', value=100)
    
    result = calc_engine._calculate_type_entries(context, [type_entry])
    
    print(f"   Total calculated: ₹{result['total']}")
    print(f"   Universal entries created: {len(result['universal_entries'])}")
    
    # Check if any number gets multiple entries
    number_counts = {}
    for entry in result['universal_entries']:
        if entry.number not in number_counts:
            number_counts[entry.number] = 0
        number_counts[entry.number] += 1
    
    duplicates = [(num, count) for num, count in number_counts.items() if count > 1]
    if duplicates:
        print(f"   ❌ DUPLICATE ENTRIES FOUND:")
        for num, count in duplicates:
            print(f"      Number {num} has {count} entries")
    else:
        print(f"   ✅ No duplicate entries created")
    
    # Check the actual SP4 expansion
    print(f"\n3. SP COLUMN 4 EXPANSION:")
    sp4_numbers = sp_table.get(4, set())
    print(f"   SP4 contains {len(sp4_numbers)} numbers: {sorted(sp4_numbers)}")
    
    # If we see 1300, maybe 13 numbers?
    if result['total'] == 1300:
        print(f"\n   ❌ FOUND THE BUG: Total is 1300!")
        print(f"   1300 / 100 = 13")
        print(f"   But SP4 only has {len(sp4_numbers)} numbers")
        print(f"   Looking for the extra entry...")

if __name__ == "__main__":
    test_parsing()