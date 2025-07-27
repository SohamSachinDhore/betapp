"""Test the full mixed input parsing including the improved PANA parser"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsing.mixed_input_parser import MixedInputParser
from src.business.calculation_engine import CalculationEngine
from src.database.db_manager import DatabaseManager

def test_full_mixed_parsing():
    """Test the complete mixed input parsing with PANA improvements"""
    
    print("🔧 TESTING FULL MIXED INPUT PARSING")
    print("=" * 60)
    
    # Full input from user's GUI screenshot 
    full_input = """1=150
2=150
3=150
4=150
5=150
6=150

38x100
43x100

138+347+230+349+269+
=RS,, 400

369+378+270+578+590+
128+380+129+670+580+
=150

668+677+488+299+

= RS,60"""
    
    print("📝 FULL TEST INPUT:")
    print("-" * 30)
    lines = full_input.strip().split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"{i:2d}. '{line}'")
        else:
            print(f"{i:2d}. (empty line)")
    
    print("\n🧪 MIXED PARSING TEST:")
    print("-" * 30)
    
    try:
        # Initialize database and processor (use DataProcessor for proper setup)
        from src.business.data_processor import DataProcessor
        
        db_manager = DatabaseManager("./data/rickymama.db")
        processor = DataProcessor(db_manager)
        
        # Parse the input using the properly configured processor
        result = processor.mixed_parser.parse(full_input)
        
        print(f"✅ Successfully parsed mixed input")
        print(f"� Total entries: {result.total_entries}")
        
        # Collect all entries for calculation
        all_entries = (result.pana_entries + result.type_entries + 
                      result.time_entries + result.multi_entries + result.direct_entries)
        
        # Group entries by type
        type_groups = {}
        for entry in all_entries:
            entry_type = type(entry).__name__
            if entry_type not in type_groups:
                type_groups[entry_type] = []
            type_groups[entry_type].append(entry)
        
        print(f"\n📊 PARSED BY TYPE:")
        print("-" * 30)
        
        for entry_type, entries in type_groups.items():
            print(f"{entry_type}: {len(entries)} entries")
            if entry_type == "DirectEntry":
                values = [e.value for e in entries]
                print(f"  Values: {values}")
            elif entry_type == "TimeEntry":
                details = [(e.columns, e.value) for e in entries]
                print(f"  Time entries: {details}")
            elif entry_type == "MultiEntry":
                details = [(e.number, e.value) for e in entries]
                print(f"  Multi entries: {details}")
            elif entry_type == "PanaEntry":
                values = {}
                for e in entries:
                    if e.value not in values:
                        values[e.value] = 0
                    values[e.value] += 1
        print(f"  PANA groups: {values}")

        # Calculate total using processor's calculation engine
        calc_result = processor.calculation_engine.calculate_total(result)
        
        print(f"\n💰 CALCULATION RESULTS:")
        print("-" * 30)
        print(f"Total amount: ₹{calc_result.grand_total:,}")
        
        # Break down by type
        if calc_result.pana_total > 0:
            print(f"  PANA: ₹{calc_result.pana_total:,}")
        if calc_result.type_total > 0:
            print(f"  TYPE: ₹{calc_result.type_total:,}")
        if calc_result.time_total > 0:
            print(f"  TIME: ₹{calc_result.time_total:,}")
        if calc_result.multi_total > 0:
            print(f"  MULTI: ₹{calc_result.multi_total:,}")
        
        # Expected breakdown
        expected_direct = 6 * 150  # 6 direct entries × ₹150 = ₹900
        expected_time = 2 * 100    # 2 time entries × ₹100 = ₹200  
        expected_pana = 3740       # From PANA calculation above
        expected_total = expected_direct + expected_time + expected_pana  # ₹4,840
        
        print(f"\n🎯 EXPECTED BREAKDOWN:")
        print("-" * 30)
        print(f"  DIRECT: ₹{expected_direct:,} (6 × ₹150)")
        print(f"  TIME: ₹{expected_time:,} (2 × ₹100)")
        print(f"  PANA: ₹{expected_pana:,} (complex PANA entries)")
        print(f"  TOTAL: ₹{expected_total:,}")
        
        if calc_result.grand_total == expected_total:
            print("✅ FULL PARSING SUCCESSFUL - All patterns parsed correctly!")
        else:
            print(f"❌ MISMATCH - Expected ₹{expected_total:,}, got ₹{calc_result.grand_total:,}")
            print("   This indicates some patterns were not parsed correctly")
            
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_mixed_parsing()
