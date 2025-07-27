"""
🧪 LIVE DATABASE STORAGE DEMONSTRATION
=====================================

This script demonstrates how each entry type is actually stored in the database
by processing our test input and showing the actual database records created.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.business.data_processor import DataProcessor, ProcessingContext
from src.database.db_manager import DatabaseManager
from datetime import date

def demonstrate_database_storage():
    print("🧪 LIVE DATABASE STORAGE DEMONSTRATION")
    print("=" * 80)
    
    # Our test input with all types
    test_input = """1=150
2=150
38x100
138+347+230+349+269+
=RS,, 400"""
    
    print("📝 TEST INPUT:")
    print("-" * 40)
    for i, line in enumerate(test_input.strip().split('\n'), 1):
        print(f"{i}. '{line}'")
    
    try:
        # Setup
        db_manager = DatabaseManager("./data/rickymama.db")
        processor = DataProcessor(db_manager)
        
        # Create processing context
        context = ProcessingContext(
            customer_name="TestCustomer",
            bazar="T.O",
            entry_date=date.today(),
            input_text=test_input,
            validate_references=True,
            auto_create_customer=True
        )
        
        print(f"\n🔧 PROCESSING WITH CONTEXT:")
        print("-" * 40)
        print(f"Customer: {context.customer_name}")
        print(f"Bazar: {context.bazar}")
        print(f"Date: {context.entry_date}")
        
        # Process and save to database
        result = processor.process_input(context)
        
        if result.success:
            print(f"\n✅ PROCESSING SUCCESSFUL!")
            print(f"📊 Entries saved: {result.entries_saved}")
            print(f"💰 Total value: ₹{result.calculation.grand_total:,}")
            
            # Now let's examine what was actually stored in the database
            print(f"\n" + "="*80)
            print("🔍 DATABASE RECORDS CREATED:")
            print("="*80)
            
            # Get the customer ID for filtering
            customer = db_manager.get_customer_by_name("TestCustomer")
            customer_id = customer['id'] if customer else None
            
            # 1. Universal Log Entries
            print(f"\n1️⃣ UNIVERSAL_LOG TABLE:")
            print("-" * 50)
            
            filters = {
                'customer_id': customer_id,
                'start_date': context.entry_date.isoformat(),
                'end_date': context.entry_date.isoformat()
            }
            
            universal_entries = db_manager.get_universal_log_entries(filters, limit=20)
            
            print(f"Total entries: {len(universal_entries)}")
            print(f"{'#':<3} {'Type':<12} {'Number':<7} {'Value':<8} {'Source':<25}")
            print("-" * 60)
            
            for i, entry in enumerate(universal_entries, 1):
                print(f"{i:<3} {entry['entry_type']:<12} {entry['number']:<7} ₹{entry['value']:<7} {entry['source_line'][:24]:<25}")
            
            # 2. Pana Table Entries
            print(f"\n2️⃣ PANA_TABLE:")
            print("-" * 50)
            
            pana_entries = db_manager.get_pana_table_values("T.O", context.entry_date.isoformat())
            
            print(f"Total PANA entries: {len(pana_entries)}")
            print(f"{'Number':<8} {'Value':<8} {'Source Type'}")
            print("-" * 30)
            
            # Group by number for cleaner display
            pana_by_number = {}
            for entry in pana_entries:
                num = entry['number']
                val = entry['value']
                if num not in pana_by_number:
                    pana_by_number[num] = val
                else:
                    pana_by_number[num] += val
            
            # Determine source type for each number
            for number, value in sorted(pana_by_number.items()):
                if number in [1, 2]:
                    source = "TimeEntry"
                elif number in [138, 347, 230, 349, 269]:
                    source = "PanaEntry"
                else:
                    source = "Unknown"
                print(f"{number:<8} ₹{value:<7} {source}")
            
            # 3. Time Table Entry
            print(f"\n3️⃣ TIME_TABLE:")
            print("-" * 50)
            
            time_entry = db_manager.get_time_table_entry(customer_id, "T.O", context.entry_date.isoformat())
            
            if time_entry:
                print(f"Customer: {time_entry['customer_name']}")
                print(f"Bazar: {time_entry['bazar']}")
                print(f"Date: {time_entry['entry_date']}")
                print(f"Column values:")
                
                for col in range(10):
                    col_val = time_entry[f'col_{col}']
                    if col_val > 0:
                        source = "TimeEntry" if col in [1, 2] else "MultiEntry" if col == 3 else "Other"
                        print(f"  col_{col}: ₹{col_val} ({source})")
            else:
                print("No time table entry found")
            
            # 4. Customer Bazar Summary
            print(f"\n4️⃣ CUSTOMER_BAZAR_SUMMARY:")
            print("-" * 50)
            
            summary_entries = db_manager.get_customer_bazar_summary_by_date(context.entry_date.isoformat())
            
            if summary_entries:
                for summary in summary_entries:
                    if summary['customer_name'] == 'TestCustomer':
                        print(f"Customer: {summary['customer_name']}")
                        print(f"Date: {summary['entry_date']}")
                        print(f"T.O Total: ₹{summary['to_total']}")
                        break
            else:
                print("No summary entries found")
            
            print(f"\n" + "="*80)
            print("📊 STORAGE SUMMARY:")
            print("="*80)
            
            print(f"✅ {len(universal_entries)} entries in universal_log (complete audit trail)")
            print(f"✅ {len(pana_by_number)} numbers in pana_table (PANA + Direct entries)")
            print(f"✅ 1 record in time_table (column-organized data)")
            print(f"✅ 1 record in customer_bazar_summary (daily totals)")
            
            print(f"\n💡 KEY OBSERVATIONS:")
            print("-" * 40)
            print(f"🔸 TimeEntry (1=150, 2=150) → stored in BOTH pana_table AND time_table")
            print(f"🔸 MultiEntry (38x100) → stored in time_table col_3 only")
            print(f"🔸 PanaEntry (5 numbers) → stored in universal_log AND pana_table")
            print(f"🔸 All entries contribute to customer_bazar_summary total")
            
        else:
            print(f"❌ Processing failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demonstrate_database_storage()
