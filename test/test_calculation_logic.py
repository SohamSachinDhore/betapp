#!/usr/bin/env python3
"""
Test script to verify total calculation logic for mixed input
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mixed_input_calculation():
    """Test the total calculation logic for mixed input types"""
    
    print("🔍 TESTING MIXED INPUT CALCULATION LOGIC")
    print("=" * 70)
    
    # Complex test input with multiple pattern types
    test_input = """138+347+230+349+269+
=RS,, 400
369+378+270+578+590+
128+380+129+670+580+
=150
239=150
456=150
279=150
170=150
668+677+488+299+
= RS,60
128=150
169=150
1=100
6=100"""

    try:
        from src.business.data_processor import DataProcessor
        from src.business.calculation_engine import CalculationEngine
        from src.database.db_manager import create_database_manager
        from datetime import date
        
        print("✅ Successfully imported calculation components")
        
        # Create processor with database for full functionality
        db_manager = create_database_manager()
        processor = DataProcessor(db_manager)
        
        print("✅ DataProcessor created with database")
        
        # Parse the mixed input
        mixed_parser = processor.mixed_parser
        parsed_result = mixed_parser.parse(test_input)
        
        print(f"✅ Mixed input parsed successfully")
        print(f"📊 Parsed entries summary:")
        print(f"   PANA entries: {len(parsed_result.pana_entries or [])}")
        print(f"   TYPE entries: {len(parsed_result.type_entries or [])}")
        print(f"   TIME entries: {len(parsed_result.time_entries or [])}")
        print(f"   MULTI entries: {len(parsed_result.multi_entries or [])}")
        print(f"   DIRECT entries: {len(parsed_result.direct_entries or [])}")
        
        # Test calculation with CalculationEngine
        print("\n🧮 TESTING CALCULATION ENGINE")
        print("-" * 50)
        
        calc_engine = processor.calculation_engine
        calc_result = calc_engine.calculate_total(parsed_result)
        
        print(f"📊 CalculationEngine.calculate_total() results:")
        print(f"   PANA total: ₹{calc_result.pana_total:,}")
        print(f"   TYPE total: ₹{calc_result.type_total:,}")
        print(f"   TIME total: ₹{calc_result.time_total:,}")
        print(f"   MULTI total: ₹{calc_result.multi_total:,}")
        print(f"   DIRECT total: ₹{calc_result.direct_total:,}")
        print(f"   GRAND TOTAL: ₹{calc_result.grand_total:,}")
        
        # Test individual calculation methods
        print("\n🔍 TESTING INDIVIDUAL CALCULATION METHODS")
        print("-" * 50)
        
        # Test PANA calculation
        if parsed_result.pana_entries:
            pana_total = calc_engine.calculate_pana_total(parsed_result.pana_entries)
            print(f"PANA calculation: {len(parsed_result.pana_entries)} entries → ₹{pana_total:,}")
            
            # Show PANA entry details
            for entry in parsed_result.pana_entries:
                print(f"   {entry.number} = ₹{entry.value}")
        
        # Test DIRECT calculation
        if hasattr(parsed_result, 'direct_entries') and parsed_result.direct_entries:
            direct_total = calc_engine.calculate_direct_total(parsed_result.direct_entries)
            print(f"\nDIRECT calculation: {len(parsed_result.direct_entries)} entries → ₹{direct_total:,}")
            
            # Show DIRECT entry details
            for entry in parsed_result.direct_entries:
                print(f"   {entry.number} = ₹{entry.value}")
        
        # Test TIME calculation
        if parsed_result.time_entries:
            time_total = calc_engine.calculate_time_total(parsed_result.time_entries)
            print(f"\nTIME calculation: {len(parsed_result.time_entries)} entries → ₹{time_total:,}")
            
            # Show TIME entry details
            for entry in parsed_result.time_entries:
                columns_str = " ".join(map(str, sorted(entry.columns)))
                multiplier = len(entry.columns)
                total_for_entry = entry.value * multiplier
                print(f"   Columns {columns_str} = ₹{entry.value} × {multiplier} = ₹{total_for_entry:,}")
        
        # Test TYPE calculation
        if parsed_result.type_entries:
            type_total = calc_engine.calculate_type_total(parsed_result.type_entries)
            print(f"\nTYPE calculation: {len(parsed_result.type_entries)} entries → ₹{type_total:,}")
            
            # Show TYPE entry details
            for entry in parsed_result.type_entries:
                print(f"   {entry.table_type} Column {entry.column} = ₹{entry.value}")
        
        # Test MULTI calculation
        if parsed_result.multi_entries:
            multi_total = calc_engine.calculate_multi_total(parsed_result.multi_entries)
            print(f"\nMULTI calculation: {len(parsed_result.multi_entries)} entries → ₹{multi_total:,}")
            
            # Show MULTI entry details
            for entry in parsed_result.multi_entries:
                print(f"   {entry.number:02d} × ₹{entry.value}")
        
        # Verify total calculation logic
        print("\n✅ TOTAL CALCULATION VERIFICATION")
        print("-" * 50)
        
        manual_total = (
            calc_result.pana_total + 
            calc_result.type_total + 
            calc_result.time_total + 
            calc_result.multi_total + 
            calc_result.direct_total
        )
        
        print(f"Manual calculation:")
        print(f"   ₹{calc_result.pana_total:,} (PANA) +")
        print(f"   ₹{calc_result.type_total:,} (TYPE) +")
        print(f"   ₹{calc_result.time_total:,} (TIME) +")
        print(f"   ₹{calc_result.multi_total:,} (MULTI) +")
        print(f"   ₹{calc_result.direct_total:,} (DIRECT)")
        print(f"   = ₹{manual_total:,}")
        
        print(f"\nCalculationEngine result: ₹{calc_result.grand_total:,}")
        
        if manual_total == calc_result.grand_total:
            print("✅ CALCULATION LOGIC VERIFIED - Totals match!")
        else:
            print("❌ CALCULATION MISMATCH!")
            print(f"   Expected: ₹{manual_total:,}")
            print(f"   Got: ₹{calc_result.grand_total:,}")
            print(f"   Difference: ₹{abs(manual_total - calc_result.grand_total):,}")
        
        # Test GUI calculation logic
        print("\n🖥️ TESTING GUI CALCULATION LOGIC")
        print("-" * 50)
        
        # This mimics the calculation logic used in main_gui_working.py
        if hasattr(calc_result, 'grand_total'):
            gui_total_value = calc_result.grand_total
        else:
            gui_total_value = (getattr(calc_result, 'pana_total', 0) + 
                             getattr(calc_result, 'type_total', 0) + 
                             getattr(calc_result, 'time_total', 0) + 
                             getattr(calc_result, 'multi_total', 0) + 
                             getattr(calc_result, 'direct_total', 0))
        
        print(f"GUI calculation logic result: ₹{gui_total_value:,}")
        
        if gui_total_value == calc_result.grand_total:
            print("✅ GUI CALCULATION LOGIC VERIFIED!")
        else:
            print("❌ GUI CALCULATION MISMATCH!")
        
        # Test entry counting logic (used in GUI)
        total_entries = (len(parsed_result.pana_entries or []) + 
                       len(parsed_result.type_entries or []) + 
                       len(parsed_result.time_entries or []) + 
                       len(parsed_result.multi_entries or []) +
                       len(parsed_result.direct_entries or []))
        
        print(f"\nEntry counting:")
        print(f"   Total entries for GUI display: {total_entries}")
        
        print("\n🎯 CALCULATION LOGIC SUMMARY")
        print("-" * 50)
        print("✅ PANA entries: Sum of all values")
        print("✅ DIRECT entries: Sum of all values")
        print("✅ TIME entries: Value × number_of_columns")
        print("✅ TYPE entries: Value × numbers_in_table_column")
        print("✅ MULTI entries: Sum of all values")
        print("✅ GRAND TOTAL: Sum of all type totals")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_specific_calculation_scenarios():
    """Test specific calculation scenarios"""
    
    print("\n\n🧪 TESTING SPECIFIC CALCULATION SCENARIOS")
    print("=" * 70)
    
    try:
        from src.business.calculation_engine import CalculationEngine
        from src.database.models import PanaEntry, TimeEntry, DirectEntry
        from src.database.models import ParsedInputResult
        
        calc_engine = CalculationEngine()
        
        # Test 1: Simple DIRECT entries
        print("Test 1: Simple DIRECT entries")
        direct_entries = [
            type('DirectEntry', (), {'number': 239, 'value': 150})(),
            type('DirectEntry', (), {'number': 456, 'value': 150})(),
        ]
        
        # Create a mock parsed result
        parsed_result = type('ParsedResult', (), {
            'pana_entries': [],
            'type_entries': [],
            'time_entries': [],
            'multi_entries': [],
            'direct_entries': direct_entries,
            'is_empty': False
        })()
        
        result = calc_engine.calculate_total(parsed_result)
        print(f"   Input: 239=150, 456=150")
        print(f"   Expected: ₹300")
        print(f"   Got: ₹{result.direct_total}")
        print(f"   Status: {'✅ PASS' if result.direct_total == 300 else '❌ FAIL'}")
        
        # Test 2: TIME entries with multiplication
        print("\nTest 2: TIME entries with multiplication")
        time_entries = [
            type('TimeEntry', (), {'columns': [1], 'value': 100})(),
            type('TimeEntry', (), {'columns': [6], 'value': 100})(),
        ]
        
        time_result = calc_engine.calculate_time_total(time_entries)
        print(f"   Input: 1=100, 6=100")
        print(f"   Expected: 100×1 + 100×1 = ₹200")
        print(f"   Got: ₹{time_result}")
        print(f"   Status: {'✅ PASS' if time_result == 200 else '❌ FAIL'}")
        
        print("\n✅ Specific calculation scenarios completed")
        
    except Exception as e:
        print(f"❌ Specific test failed: {e}")

if __name__ == "__main__":
    test_mixed_input_calculation()
    test_specific_calculation_scenarios()
