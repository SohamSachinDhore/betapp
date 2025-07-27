#!/usr/bin/env python3
"""Check the current database constraint for entry_type"""

import sqlite3
import os

def check_database_constraint():
    """Check the current database constraint"""
    
    db_path = "data/rickey_mama.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found at data/rickey_mama.db")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='universal_log'")
        result = cursor.fetchone()
        
        if result:
            schema = result[0]
            print("Current universal_log table schema:")
            print("=" * 50)
            print(schema)
            print("=" * 50)
            
            # Look for the constraint specifically
            if "universal_log_entry_type_valid" in schema:
                print("\n✅ Found entry_type constraint in schema")
                
                # Extract the constraint part
                constraint_start = schema.find("universal_log_entry_type_valid CHECK")
                if constraint_start != -1:
                    constraint_end = schema.find(")", constraint_start)
                    if constraint_end != -1:
                        constraint_text = schema[constraint_start:constraint_end+1]
                        print(f"Constraint: {constraint_text}")
            else:
                print("\n❌ Entry type constraint not found in schema")
        else:
            print("❌ universal_log table not found")
        
        # Test insertion with JODI
        print("\n🧪 Testing JODI insertion...")
        try:
            cursor.execute("""
                INSERT INTO universal_log 
                (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
                VALUES (1, 'Test', '2025-07-27', 'T.O', 22, 500, 'JODI', 'test')
            """)
            conn.commit()
            print("✅ JODI insertion successful")
            
            # Clean up
            cursor.execute("DELETE FROM universal_log WHERE entry_type = 'JODI' AND customer_name = 'Test'")
            conn.commit()
            
        except Exception as e:
            print(f"❌ JODI insertion failed: {e}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database_constraint()