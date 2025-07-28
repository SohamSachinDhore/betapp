#!/usr/bin/env python3
"""
Analyze the specific input from the GUI screenshot to understand the ₹1,100 calculation
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_gui_input():
    """Analyze the exact input from the GUI screenshot"""
    
    print("🔍 ANALYZING GUI INPUT FROM SCREENSHOT")
    print("=" * 70)
    
    # Exact input from the screenshot
    gui_input = """138+347+230+349+269+
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

    print("📝 GUI INPUT:")
    print("-" * 30)
    for i, line in enumerate(gui_input.split('\n'), 1):
        if line.strip():
            print(f"{i:2d}. '{line}'")
        else:
            print(f"{i:2d}. (empty line)")
    
    try:
        from src.business.data_processor import DataProcessor
        from src.database.db_manager import create_database_manager
        
        print("\n🧮 PARSING AND CALCULATION:")
        print("-" * 50)
        
        # Create processor
        db_manager = create_database_manager()
        processor = DataProcessor(db_manager)
        
        # Parse the exact GUI input
        mixed_parser = processor.mixed_parser
        parsed_result = mixed_parser.parse(gui_input)
        
        print(f"✅ Parsing complete")
        print(f"📊 Entry breakdown:")
        print(f"   PANA entries: {len(parsed_result.pana_entries or [])}")
        print(f"   TYPE entries: {len(parsed_result.type_entries or [])}")
        print(f"   TIME entries: {len(parsed_result.time_entries or [])}")
        print(f"   MULTI entries: {len(parsed_result.multi_entries or [])}")
        print(f"   DIRECT entries: {len(parsed_result.direct_entries or [])}")
        
        # Calculate totals
        calc_engine = processor.calculation_engine
        calc_result = calc_engine.calculate_total(parsed_result)
        
        print(f"\n💰 CALCULATION RESULTS:")
        print(f"   PANA total: ₹{calc_result.pana_total:,}")
        print(f"   TYPE total: ₹{calc_result.type_total:,}")
        print(f"   TIME total: ₹{calc_result.time_total:,}")
        print(f"   MULTI total: ₹{calc_result.multi_total:,}")
        print(f"   DIRECT total: ₹{calc_result.direct_total:,}")
        print(f"   GRAND TOTAL: ₹{calc_result.grand_total:,}")
        
        # Show detailed breakdown
        print(f"\n🔍 DETAILED BREAKDOWN:")
        print("-" * 30)
        
        # DIRECT entries
        if hasattr(parsed_result, 'direct_entries') and parsed_result.direct_entries:
            print(f"DIRECT entries ({len(parsed_result.direct_entries)}):")
            direct_total = 0
            for entry in parsed_result.direct_entries:
                print(f"   {entry.number} = ₹{entry.value}")
                direct_total += entry.value
            print(f"   DIRECT subtotal: ₹{direct_total}")
        
        # TIME entries
        if parsed_result.time_entries:
            print(f"\nTIME entries ({len(parsed_result.time_entries)}):")
            time_total = 0
            for entry in parsed_result.time_entries:
                entry_total = entry.value * len(entry.columns)
                columns_str = " ".join(map(str, sorted(entry.columns)))
                print(f"   Columns {columns_str} = ₹{entry.value} × {len(entry.columns)} = ₹{entry_total}")
                time_total += entry_total
            print(f"   TIME subtotal: ₹{time_total}")
        
        # PANA entries (if any)
        if parsed_result.pana_entries:
            print(f"\nPANA entries ({len(parsed_result.pana_entries)}):")
            pana_total = 0
            for entry in parsed_result.pana_entries:
                print(f"   {entry.number} = ₹{entry.value}")
                pana_total += entry.value
            print(f"   PANA subtotal: ₹{pana_total}")
        
        # Manual verification
        manual_total = (
            calc_result.pana_total + 
            calc_result.direct_total + 
            calc_result.time_total + 
            calc_result.type_total + 
            calc_result.multi_total
        )
        
        print(f"\n✅ VERIFICATION:")
        print(f"   Manual calculation: ₹{manual_total:,}")
        print(f"   Engine calculation: ₹{calc_result.grand_total:,}")
        print(f"   GUI shows: ₹1,100")
        
        if calc_result.grand_total == 1100:
            print("✅ GUI calculation matches engine!")
        else:
            print(f"❌ MISMATCH!")
            print(f"   Expected GUI total: ₹{calc_result.grand_total:,}")
            print(f"   Actual GUI total: ₹1,100")
            print(f"   Difference: ₹{abs(calc_result.grand_total - 1100):,}")
        
        # Check why it might be 1100
        print(f"\n🤔 WHY ₹1,100?")
        print("-" * 20)
        
        # Count all possible entries
        if hasattr(parsed_result, 'direct_entries') and parsed_result.direct_entries:
            direct_sum = sum(e.value for e in parsed_result.direct_entries)
            print(f"DIRECT sum: 6 entries × ₹150 = ₹{direct_sum}")
        
        if parsed_result.time_entries:
            time_sum = sum(e.value * len(e.columns) for e in parsed_result.time_entries)
            print(f"TIME sum: 2 entries = ₹{time_sum}")
        
        total_sum = direct_sum + time_sum
        print(f"Total: ₹{direct_sum} + ₹{time_sum} = ₹{total_sum}")
        
        if total_sum == 1100:
            print("✅ This explains the ₹1,100 total!")
        
        # Show why PANA entries might not be parsed
        print(f"\n⚠️ PANA PARSING ANALYSIS:")
        print("-" * 30)
        
        pana_lines = [
            "138+347+230+349+269+",
            "=RS,, 400",
            "369+378+270+578+590+",
            "128+380+129+670+580+",
            "=150",
            "668+677+488+299+",
            "= RS,60"
        ]
        
        for line in pana_lines:
            print(f"   '{line}' - {'Result line' if line.startswith('=') else 'Number line'}")
        
        print(f"\n💡 EXPLANATION:")
        print("   The PANA parsing failed because:")
        print("   1. Complex multi-line PANA format requires specific validation")
        print("   2. Result lines (=RS,, 400) need proper parsing")
        print("   3. System correctly parsed simpler DIRECT and TIME patterns")
        print("   4. Total = 6×₹150 (DIRECT) + 2×₹100 (TIME) = ₹1,100")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_gui_input()
