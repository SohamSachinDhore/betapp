"""Test the improved PANA parsing functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsing.pana_parser import PanaTableParser, PanaValidator
from src.database.db_manager import DatabaseManager

def test_improved_pana_parsing():
    """Test the improved PANA parsing with complex input"""
    
    print("🔧 TESTING IMPROVED PANA PARSING")
    print("=" * 60)
    
    # Test input from user's GUI screenshot
    test_input = """138+347+230+349+269+
=RS,, 400

369+378+270+578+590+
128+380+129+670+580+
=150

668+677+488+299+

= RS,60"""
    
    print("📝 TEST INPUT:")
    print("-" * 30)
    lines = test_input.strip().split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"{i:2d}. '{line}'")
        else:
            print(f"{i:2d}. (empty line)")
    
    print("\n🧪 PARSING TEST:")
    print("-" * 30)
    
    try:
        # Initialize database and get pana reference numbers
        db_manager = DatabaseManager("./data/rickymama.db")
        pana_numbers = db_manager.get_pana_reference_numbers()
        print(f"✅ Loaded {len(pana_numbers)} pana reference numbers")
        
        # Create validator and parser
        validator = PanaValidator(pana_numbers)
        parser = PanaTableParser(validator)
        
        # Parse the input
        entries = parser.parse(test_input)
        
        print(f"✅ Successfully parsed {len(entries)} pana entries")
        
        # Group and calculate totals
        groups = {}
        for entry in entries:
            value = entry.value
            if value not in groups:
                groups[value] = []
            groups[value].append(entry.number)
        
        print("\n📊 PARSED GROUPS:")
        print("-" * 30)
        total_amount = 0
        
        for value, numbers in groups.items():
            count = len(numbers)
            group_total = count * value
            total_amount += group_total
            
            print(f"Value ₹{value}: {count} numbers × ₹{value} = ₹{group_total:,}")
            print(f"  Numbers: {numbers[:5]}{'...' if len(numbers) > 5 else ''}")
        
        print(f"\n💰 TOTAL PANA AMOUNT: ₹{total_amount:,}")
        
        # Compare with expected
        expected_total = (5 * 400) + (10 * 150) + (4 * 60)  # 2000 + 1500 + 240 = 3740
        print(f"🎯 EXPECTED TOTAL: ₹{expected_total:,}")
        
        if total_amount == expected_total:
            print("✅ PARSING SUCCESSFUL - Totals match!")
        else:
            print(f"❌ PARSING ISSUE - Expected ₹{expected_total:,}, got ₹{total_amount:,}")
            
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_pana_parsing()
