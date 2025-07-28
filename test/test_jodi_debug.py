#!/usr/bin/env python3
"""Test script to debug Jodi input processing"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from src.business.data_processor import DataProcessor, ProcessingContext
from src.database.db_manager import DatabaseManager

def test_jodi_processing():
    """Test Jodi input processing step by step"""
    
    # Initialize database and processor
    db_manager = DatabaseManager()
    processor = DataProcessor(db_manager)
    
    # Test input
    jodi_input = """22-24-26-28-20
42-44-46-48-40
66-68-60-62-64
88-80-82-84-86
00-02-04-06-08=500"""
    
    print("🔍 Testing Jodi input processing...")
    print(f"Input:\n{jodi_input}")
    print("=" * 50)
    
    # Step 1: Test parsing
    print("Step 1: Parse input")
    try:
        parsed_result = processor.mixed_parser.parse(jodi_input)
        print(f"✅ Parsing successful")
        print(f"  - Jodi entries: {len(getattr(parsed_result, 'jodi_entries', []))}")
        if hasattr(parsed_result, 'jodi_entries') and parsed_result.jodi_entries:
            for entry in parsed_result.jodi_entries:
                print(f"    • Jodi numbers: {entry.jodi_numbers}")
                print(f"    • Value: {entry.value}")
        print()
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return
    
    # Step 2: Test calculation
    print("Step 2: Test calculation")
    try:
        calculation_result = processor.calculation_engine.calculate_total(parsed_result)
        print(f"✅ Calculation successful")
        print(f"  - Jodi total: {calculation_result.jodi_total}")
        print(f"  - Grand total: {calculation_result.grand_total}")
        print()
    except Exception as e:
        print(f"❌ Calculation failed: {e}")
        return
    
    # Step 3: Debug universal log entry creation
    print("Step 3: Debug universal log entry creation")
    try:
        from src.business.calculation_engine import CalculationContext
        context = CalculationContext(
            customer_id=1,
            customer_name="Test Customer",
            entry_date=date.today(),
            bazar="T.O",
            source_data=parsed_result
        )
        
        calculation = processor.calculation_engine.calculate(context)
        print(f"✅ Calculation successful")
        print(f"  - Universal entries: {len(calculation.universal_entries)}")
        
        # Debug the first few entries
        for i, entry in enumerate(calculation.universal_entries[:3]):
            print(f"  Entry {i+1}:")
            print(f"    - number: {entry.number}")
            print(f"    - value: {entry.value}")
            print(f"    - entry_type: {entry.entry_type} (type: {type(entry.entry_type)})")
            print(f"    - entry_type.value: {entry.entry_type.value if hasattr(entry.entry_type, 'value') else 'N/A'}")
        print()
    except Exception as e:
        print(f"❌ Calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Test database save with manual entry dict creation
    print("Step 4: Test database save (manual)")
    try:
        # Create entry dict manually to debug
        test_entry = calculation.universal_entries[0]
        entry_dict = {
            'customer_id': test_entry.customer_id,
            'customer_name': test_entry.customer_name,
            'entry_date': test_entry.entry_date.isoformat() if isinstance(test_entry.entry_date, date) else test_entry.entry_date,
            'bazar': test_entry.bazar,
            'number': test_entry.number,
            'value': test_entry.value,
            'entry_type': test_entry.entry_type.value if hasattr(test_entry.entry_type, 'value') else str(test_entry.entry_type),
            'source_line': test_entry.source_line
        }
        
        print(f"Debug entry dict: {entry_dict}")
        print(f"Entry type value: '{entry_dict['entry_type']}'")
        
        # Try to save just one entry
        db_manager.add_universal_log_entries([entry_dict])
        print(f"✅ Single entry saved successfully")
        
    except Exception as e:
        print(f"❌ Single entry save failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Test full processing (this should fail)
    print("Step 5: Test full processing")
    try:
        context = ProcessingContext(
            customer_name="Test Customer 2",
            bazar="T.O",
            entry_date=date.today(),
            input_text=jodi_input
        )
        
        result = processor.process_input(context)
        
        if result.success:
            print(f"✅ Processing successful")
            print(f"  - Entries saved: {result.entries_saved}")
            print(f"  - Customer: {result.customer_name}")
            print(f"  - Total: {result.calculation.grand_total if result.calculation else 'N/A'}")
        else:
            print(f"❌ Processing failed: {result.error_message}")
    except Exception as e:
        print(f"❌ Processing failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jodi_processing()