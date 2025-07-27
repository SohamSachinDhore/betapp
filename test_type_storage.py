#!/usr/bin/env python3
"""
Simple demonstration of TYPE entry storage in pana_table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager
from datetime import date

def demonstrate_type_storage():
    """Show how TYPE entries are stored in database tables"""
    
    print("=" * 80)
    print("TYPE ENTRY DATABASE STORAGE DEMONSTRATION")
    print("=" * 80)
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Clear existing data
    db_manager.execute_query("DELETE FROM universal_log")
    db_manager.execute_query("DELETE FROM pana_table")
    db_manager.execute_query("DELETE FROM customers")
    
    # Insert test customer
    db_manager.execute_query("INSERT INTO customers (name) VALUES ('test_customer')")
    customer_id = db_manager.execute_query("SELECT last_insert_rowid() as id")[0]['id']
    
    print(f"1. SETUP:")
    print(f"   Created test customer with ID: {customer_id}")
    
    # Simulate TYPE entry processing by inserting to universal_log
    # The triggers will automatically update pana_table
    
    print(f"\n2. SIMULATING TYPE ENTRY: '1SP=50'")
    print(f"   This should create entries for all SP Column 1 numbers")
    
    # Get SP Column 1 numbers
    sp_numbers = db_manager.execute_query(
        "SELECT number FROM type_table_sp WHERE column_number = 1 ORDER BY row_number"
    )
    sp_numbers_list = [row['number'] for row in sp_numbers]
    
    print(f"   SP Column 1 contains {len(sp_numbers_list)} numbers: {sp_numbers_list}")
    
    # Insert universal_log entries (simulating what DataProcessor would do)
    for number in sp_numbers_list:
        db_manager.execute_query("""
            INSERT INTO universal_log 
            (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
            VALUES (?, 'test_customer', '2025-07-27', 'T.O', ?, 50, 'TYPE', '1SP=50')
        """, [customer_id, number])
    
    print(f"   Inserted {len(sp_numbers_list)} records into universal_log")
    
    # Check universal_log
    log_count = db_manager.execute_query("SELECT COUNT(*) as count FROM universal_log")[0]['count']
    print(f"\n3. UNIVERSAL_LOG TABLE:")
    print(f"   Total records: {log_count}")
    
    # Show sample records
    sample_logs = db_manager.execute_query("""
        SELECT number, value, entry_type, source_line 
        FROM universal_log 
        ORDER BY number 
        LIMIT 5
    """)
    
    print(f"   Sample records:")
    for log in sample_logs:
        print(f"     - Number: {log['number']}, Value: ₹{log['value']}, Type: {log['entry_type']}, Source: {log['source_line']}")
    
    # Check pana_table (should be auto-populated by trigger)
    pana_count = db_manager.execute_query("SELECT COUNT(*) as count FROM pana_table")[0]['count']
    print(f"\n4. PANA_TABLE (AUTO-POPULATED BY TRIGGER):")
    print(f"   Total records: {pana_count}")
    
    # Show sample pana records
    sample_panas = db_manager.execute_query("""
        SELECT bazar, number, value 
        FROM pana_table 
        ORDER BY number 
        LIMIT 5
    """)
    
    print(f"   Sample records:")
    for pana in sample_panas:
        print(f"     - Bazar: {pana['bazar']}, Number: {pana['number']}, Value: ₹{pana['value']}")
    
    # Show total value
    total_value = db_manager.execute_query("SELECT SUM(value) as total FROM pana_table")[0]['total']
    print(f"   Total value in pana_table: ₹{total_value}")
    
    print(f"\n5. VERIFICATION:")
    print(f"   Original TYPE entry: 1SP=50")
    print(f"   SP Column 1 has {len(sp_numbers_list)} numbers")
    print(f"   Expected total value: {len(sp_numbers_list)} × 50 = ₹{len(sp_numbers_list) * 50}")
    print(f"   Actual total value: ₹{total_value}")
    print(f"   ✅ {'CORRECT' if total_value == len(sp_numbers_list) * 50 else 'INCORRECT'}")

def show_type_to_pana_mapping():
    """Show mapping from TYPE tables to actual PANA numbers"""
    
    print(f"\n{'-' * 80}")
    print("TYPE TABLE TO PANA NUMBER MAPPING")
    print(f"{'-' * 80}")
    
    db_manager = DatabaseManager("data/rickymama.db")
    
    # Show examples from each table type
    examples = [
        ("SP", 1, "Single Patti"),
        ("DP", 1, "Double Patti"), 
        ("CP", 15, "Close Patti")
    ]
    
    for table_type, column, description in examples:
        print(f"\n{table_type} TABLE - {description} Column {column}:")
        
        query = f"SELECT number FROM type_table_{table_type.lower()} WHERE column_number = ? ORDER BY row_number"
        numbers = db_manager.execute_query(query, [column])
        numbers_list = [row['number'] for row in numbers]
        
        print(f"   Numbers: {numbers_list}")
        print(f"   Count: {len(numbers_list)}")
        print(f"   Example: If user enters '{column}{table_type}=100', then:")
        print(f"            Each of these {len(numbers_list)} numbers gets ₹100")
        print(f"            Total value distributed: ₹{len(numbers_list) * 100}")

if __name__ == "__main__":
    demonstrate_type_storage()
    show_type_to_pana_mapping()
    
    print(f"\n{'=' * 80}")
    print("KEY INSIGHTS:")
    print(f"{'=' * 80}")
    print("1. TYPE entries (1SP=50) are EXPANDED into multiple PANA numbers")
    print("2. Each number in the TYPE table column gets the same value")
    print("3. Universal_log stores one record per expanded number")
    print("4. Pana_table aggregates by bazar/date/number via database triggers")
    print("5. This allows TYPE entries to seamlessly integrate with PANA entries")
