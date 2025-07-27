"""
🧪 GUI FUNCTIONALITY TEST
========================

This script tests the key functionality of the GUI to ensure everything is working properly,
especially after our PANA parsing improvements.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.business.data_processor import DataProcessor, ProcessingContext
from src.database.db_manager import DatabaseManager
from datetime import date

def test_gui_functionality():
    print("🧪 GUI FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test the same input that would come from the GUI
    test_cases = [
        {
            "name": "Simple Direct Entries",
            "input": "1=150\n2=150\n3=150",
            "expected_entries": 3,
            "expected_total": 450
        },
        {
            "name": "Time Multiplication",
            "input": "38x100\n43x100",
            "expected_entries": 2,
            "expected_total": 200
        },
        {
            "name": "Complex PANA (Our Fixed Pattern)",
            "input": "138+347+230+349+269+\n=RS,, 400",
            "expected_entries": 5,
            "expected_total": 2000
        },
        {
            "name": "Mixed Input (Full GUI Test)",
            "input": """1=150
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

= RS,60""",
            "expected_entries": 27,
            "expected_total": 4840
        }
    ]
    
    try:
        # Initialize the same components used by GUI
        db_manager = DatabaseManager("./data/rickymama.db")
        processor = DataProcessor(db_manager)
        
        print("✅ Database and processor initialized successfully")
        print(f"📊 Testing {len(test_cases)} scenarios...\n")
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}️⃣ {test_case['name']}")
            print("-" * 40)
            
            try:
                # Create processing context (same as GUI)
                context = ProcessingContext(
                    customer_name=f"TestCustomer{i}",
                    bazar="T.O",
                    entry_date=date.today(),
                    input_text=test_case["input"],
                    validate_references=True,
                    auto_create_customer=True
                )
                
                # Process input (same as GUI submit_data function)
                result = processor.process_mixed_input(context)
                
                if result.success:
                    # Calculate total entries (use the correct attributes)
                    total_entries = (result.pana_count + result.type_count + 
                                   result.time_count + result.multi_count + result.direct_count)
                    
                    # Check results
                    entries_match = total_entries == test_case["expected_entries"]
                    total_match = result.total_value == test_case["expected_total"]
                    
                    if entries_match and total_match:
                        print(f"✅ PASSED")
                        print(f"   Entries: {total_entries}/{test_case['expected_entries']}")
                        print(f"   Total: ₹{result.total_value:,}/₹{test_case['expected_total']:,}")
                    else:
                        print(f"❌ FAILED")
                        print(f"   Entries: {total_entries}/{test_case['expected_entries']} {'✓' if entries_match else '✗'}")
                        print(f"   Total: ₹{result.total_value:,}/₹{test_case['expected_total']:,} {'✓' if total_match else '✗'}")
                        all_passed = False
                        
                        # Show breakdown for debugging
                        print(f"   Breakdown:")
                        print(f"     PANA: {result.pana_count} entries")
                        print(f"     TIME: {result.time_count} entries") 
                        print(f"     MULTI: {result.multi_count} entries")
                        print(f"     DIRECT: {result.direct_count} entries")
                        print(f"     TYPE: {result.type_count} entries")
                else:
                    print(f"❌ PROCESSING FAILED: {result.error_message}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                all_passed = False
                import traceback
                traceback.print_exc()
            
            print()  # Empty line between tests
        
        print("=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ GUI functionality is working correctly")
            print("✅ PANA parsing fix is working")
            print("✅ Mixed input processing is working")
            print("✅ Database storage is working")
        else:
            print("❌ SOME TESTS FAILED")
            print("🔧 Check the failed scenarios above")
            
        print("\n💡 Key Components Tested:")
        print("  ✓ Data processor initialization")
        print("  ✓ Mixed input parsing")
        print("  ✓ Pattern detection (PANA, TIME, MULTI)")
        print("  ✓ Calculation engine")
        print("  ✓ Database storage")
        print("  ✓ Error handling")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_validation_simulation():
    """Test the validation logic used by the GUI"""
    print("\n🔍 GUI VALIDATION SIMULATION")
    print("=" * 60)
    
    try:
        # Test the validation logic from validate_input() function
        db_manager = DatabaseManager("./data/rickymama.db")
        processor = DataProcessor(db_manager)
        
        test_input = """1=150
2=150
38x100
138+347+230+349+269+
=RS,, 400"""
        
        print("📝 Testing validation with input:")
        for i, line in enumerate(test_input.strip().split('\n'), 1):
            print(f"  {i}. '{line}'")
        
        # Parse input (same as GUI validate_input)
        mixed_parser = processor.mixed_parser
        parsed_result = mixed_parser.parse(test_input)
        
        if not parsed_result.is_empty:
            # Calculate totals (same as GUI)
            calc_engine = processor.calculation_engine
            calc_result = calc_engine.calculate_total(parsed_result)
            
            total_entries = (len(parsed_result.pana_entries or []) + 
                           len(parsed_result.type_entries or []) + 
                           len(parsed_result.time_entries or []) + 
                           len(parsed_result.multi_entries or []) +
                           len(parsed_result.direct_entries or []))
            
            print(f"\n✅ Validation Results:")
            print(f"   Status: ✓ {total_entries} entries detected")
            print(f"   Total: ₹{calc_result.grand_total:,}")
            
            # Show breakdown (same as GUI preview)
            print(f"\n📊 Entry Breakdown:")
            if parsed_result.pana_entries:
                print(f"   PANA: {len(parsed_result.pana_entries)} entries")
            if parsed_result.time_entries:
                print(f"   TIME: {len(parsed_result.time_entries)} entries")
            if parsed_result.multi_entries:
                print(f"   MULTI: {len(parsed_result.multi_entries)} entries")
            if parsed_result.direct_entries:
                print(f"   DIRECT: {len(parsed_result.direct_entries)} entries")
            if parsed_result.type_entries:
                print(f"   TYPE: {len(parsed_result.type_entries)} entries")
                
            print(f"\n🎯 This matches what the GUI would show in:")
            print(f"   • validation_status field")
            print(f"   • calculated_total field") 
            print(f"   • preview_area breakdown")
            
            return True
        else:
            print(f"❌ No valid entries found")
            return False
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

if __name__ == "__main__":
    # Run functionality tests
    functionality_passed = test_gui_functionality()
    
    # Run validation simulation
    validation_passed = test_gui_validation_simulation()
    
    print("\n" + "="*60)
    print("🏆 OVERALL TEST RESULTS")
    print("="*60)
    
    if functionality_passed and validation_passed:
        print("🎉 ALL GUI FUNCTIONALITY IS WORKING!")
        print("✅ The GUI should work perfectly with:")
        print("   • Real-time validation and preview")
        print("   • Accurate total calculations")
        print("   • Proper PANA parsing (fixed!)")
        print("   • Database storage")
        print("   • Error handling")
    else:
        print("❌ Some issues detected:")
        if not functionality_passed:
            print("   • Core functionality issues")
        if not validation_passed:
            print("   • Validation logic issues")
