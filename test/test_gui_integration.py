#!/usr/bin/env python3
"""
Test script to verify GUI integration with mixed input parsing
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_validation_function():
    """Test the validate_input function directly"""
    
    # Test input (same as before)
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

    print("🔍 TESTING GUI VALIDATION INTEGRATION")
    print("=" * 60)
    
    try:
        # Import the necessary components used by GUI
        from src.business.data_processor import DataProcessor, ProcessingContext
        from src.parsing.mixed_input_parser import MixedInputParser
        from datetime import date
        
        print("✅ Successfully imported GUI dependencies")
        
        # Simulate GUI validation process
        print("\n📋 Simulating GUI validate_input() process...")
        
        # Create processor (same as GUI does)
        db_manager = None  # GUI can handle None db_manager
        processor = DataProcessor(db_manager)
        
        print("✅ DataProcessor created successfully")
        
        # Create test context (same as GUI validation)
        test_context = ProcessingContext(
            customer_name="Test Customer",
            bazar="T.O",
            entry_date=date.today(),
            input_text=test_input,
            validate_references=True,
            auto_create_customer=False
        )
        
        print("✅ ProcessingContext created successfully")
        
        # Parse input to get preview (exactly as GUI does)
        mixed_parser = processor.mixed_parser
        parsed_result = mixed_parser.parse(test_input)
        
        print("✅ Mixed parser executed successfully")
        
        if not parsed_result.is_empty:
            # Calculate totals (same as GUI)
            calc_engine = processor.calculation_engine
            calc_result = calc_engine.calculate_total(parsed_result)
            
            total_entries = (len(parsed_result.pana_entries or []) + 
                           len(parsed_result.type_entries or []) + 
                           len(parsed_result.time_entries or []) + 
                           len(parsed_result.multi_entries or []) +
                           len(parsed_result.direct_entries or []))
            
            print(f"✅ Calculation engine executed successfully")
            print(f"📊 Total entries detected: {total_entries}")
            
            # Calculate total value (same logic as GUI)
            if hasattr(calc_result, 'grand_total'):
                total_value = calc_result.grand_total
            else:
                total_value = (getattr(calc_result, 'pana_total', 0) + 
                             getattr(calc_result, 'type_total', 0) + 
                             getattr(calc_result, 'time_total', 0) + 
                             getattr(calc_result, 'multi_total', 0) + 
                             getattr(calc_result, 'direct_total', 0))
            
            print(f"💰 Total value calculated: ₹{total_value:,}")
            
            # Generate preview (same detailed preview as GUI)
            preview_lines = []
            
            if parsed_result.pana_entries:
                preview_lines.append(f"[PANA] Entries ({len(parsed_result.pana_entries)}):")
                pana_by_value = {}
                for entry in parsed_result.pana_entries:
                    if entry.value not in pana_by_value:
                        pana_by_value[entry.value] = []
                    pana_by_value[entry.value].append(entry.number)
                
                for value, numbers in pana_by_value.items():
                    numbers_str = ", ".join(map(str, sorted(numbers)))
                    if len(numbers) <= 8:
                        preview_lines.append(f"   {numbers_str} = ₹{value:,}")
                    else:
                        first_eight = ", ".join(map(str, sorted(numbers)[:8]))
                        preview_lines.append(f"   {first_eight}... (+{len(numbers)-8}) = ₹{value:,}")
                
                if hasattr(calc_result, 'pana_total') and calc_result.pana_total > 0:
                    preview_lines.append(f"   → Subtotal: ₹{calc_result.pana_total:,}")
                preview_lines.append("")
            
            # Check for direct entries (exactly like GUI)
            if hasattr(parsed_result, 'direct_entries') and parsed_result.direct_entries:
                preview_lines.append(f"[DIRECT] Number Assignments ({len(parsed_result.direct_entries)}):")
                direct_by_value = {}
                for entry in parsed_result.direct_entries:
                    if entry.value not in direct_by_value:
                        direct_by_value[entry.value] = []
                    direct_by_value[entry.value].append(entry.number)
                
                for value, numbers in direct_by_value.items():
                    numbers_str = ", ".join(map(str, sorted(numbers)))
                    if len(numbers) <= 8:
                        preview_lines.append(f"   {numbers_str} = ₹{value:,}")
                    else:
                        first_eight = ", ".join(map(str, sorted(numbers)[:8]))
                        preview_lines.append(f"   {first_eight}... (+{len(numbers)-8}) = ₹{value:,}")
                
                if hasattr(calc_result, 'direct_total') and calc_result.direct_total > 0:
                    preview_lines.append(f"   → Subtotal: ₹{calc_result.direct_total:,}")
                preview_lines.append("")
            
            if parsed_result.time_entries:
                preview_lines.append(f"[TIME] Column Assignments ({len(parsed_result.time_entries)}):")
                for entry in parsed_result.time_entries:
                    columns_str = " ".join(map(str, sorted(entry.columns)))
                    preview_lines.append(f"   Columns {columns_str} = ₹{entry.value:,}")
                
                if hasattr(calc_result, 'time_total') and calc_result.time_total > 0:
                    preview_lines.append(f"   → Subtotal: ₹{calc_result.time_total:,}")
                preview_lines.append("")
            
            # Add grand total summary (exactly like GUI)
            preview_lines.append("=" * 40)
            preview_lines.append(f"GRAND TOTAL: ₹{total_value:,}")
            preview_lines.append(f"Total Entries: {total_entries}")
            
            preview_text = "\n".join(preview_lines)
            
            print("\n🎯 GUI PREVIEW OUTPUT:")
            print("-" * 40)
            print(preview_text)
            print("-" * 40)
            
            print("\n✅ GUI VALIDATION TEST SUCCESSFUL!")
            print(f"Status that would be shown: '✓ {total_entries} entries detected'")
            print(f"Total that would be displayed: '₹{total_value:,}'")
            
        else:
            print("❌ No valid entries found - this would show 'No valid data format detected'")
            
    except ImportError as ie:
        print(f"❌ Import Error: {ie}")
        print("GUI would fall back to simple parsing mode")
        
        # Test fallback logic
        lines = [line.strip() for line in test_input.split('\n') if line.strip()]
        
        if lines:
            print(f"Fallback status: 'Status: {len(lines)} lines detected'")
            
            preview = f"Preview - {len(lines)} data entries:\n"
            for i, line in enumerate(lines[:5]):
                preview += f"{i+1}. {line[:60]}{'...' if len(line) > 60 else ''}\n"
            
            if len(lines) > 5:
                preview += f"... and {len(lines) - 5} more lines"
            
            print("\nFallback preview:")
            print(preview)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("GUI would show: f'Status: Error - {e}'")

def test_gui_submit_function():
    """Test the submit_data function logic"""
    
    test_input = """138+347+230+349+269+
=RS,, 400
239=150
456=150
1=100
6=100"""

    print("\n\n🔍 TESTING GUI SUBMIT INTEGRATION")
    print("=" * 60)
    
    try:
        from src.business.data_processor import DataProcessor, ProcessingContext
        from datetime import date
        
        # Simulate GUI submit process
        print("📋 Simulating GUI submit_data() process...")
        
        # Create processor (same as GUI does)
        db_manager = None  # GUI can handle None db_manager
        processor = DataProcessor(db_manager)
        
        # Create processing context (same as GUI submit)
        context = ProcessingContext(
            customer_name="Test Customer",
            bazar="T.O",
            entry_date=date.today(),
            input_text=test_input,
            validate_references=True,
            auto_create_customer=True
        )
        
        # Process the input (same as GUI)
        result = processor.process_mixed_input(context)
        
        if result.success:
            total_entries = result.pana_count + result.type_count + result.time_count + result.multi_count + result.direct_count
            total_value = result.total_value or 0
            
            print(f"✅ SUCCESS: {total_entries} entries processed!")
            print(f"💰 Total value: ₹{total_value:.2f}")
            print(f"GUI would show: '✅ Success: {total_entries} entries saved! Total: ₹{total_value:.2f}'")
            
            # Show breakdown
            print(f"\n📊 Entry breakdown:")
            print(f"   PANA entries: {result.pana_count}")
            print(f"   TYPE entries: {result.type_count}")
            print(f"   TIME entries: {result.time_count}")
            print(f"   MULTI entries: {result.multi_count}")
            print(f"   DIRECT entries: {result.direct_count}")
            
        else:
            error_message = f"❌ Processing failed: {result.error_message}"
            if result.validation_errors:
                error_message += f"\nValidation errors: {', '.join(result.validation_errors)}"
            print(error_message)
            print(f"GUI would show: '{error_message}'")
            
    except Exception as e:
        print(f"❌ Submit Error: {e}")
        print(f"GUI would show: 'Submit error: {e}'")

if __name__ == "__main__":
    test_gui_validation_function()
    test_gui_submit_function()
