#!/usr/bin/env python3
"""Fix database constraint to include JODI entry type"""

import sqlite3
import os

def fix_database_constraint():
    """Update the database constraint to include JODI"""
    
    db_path = "data/rickymama.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found at data/rickey_mama.db")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Updating database constraint to include JODI...")
        
        # SQLite doesn't support ALTER TABLE to modify constraints directly
        # We need to recreate the table with the new constraint
        
        # Step 1: Create backup of existing data
        print("📦 Creating backup of existing data...")
        cursor.execute("CREATE TEMPORARY TABLE universal_log_backup AS SELECT * FROM universal_log")
        
        # Step 2: Drop the existing table
        print("🗑️ Dropping existing table...")
        cursor.execute("DROP TABLE universal_log")
        
        # Step 3: Recreate table with updated constraint
        print("🛠️ Creating new table with JODI support...")
        cursor.execute("""
        CREATE TABLE universal_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            entry_date DATE NOT NULL,
            bazar TEXT NOT NULL,
            number INTEGER NOT NULL,
            value INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            source_line TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Foreign Keys
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            
            -- Constraints
            CONSTRAINT universal_log_number_range CHECK (number >= 0 AND number <= 999),
            CONSTRAINT universal_log_value_positive CHECK (value >= 0),
            CONSTRAINT universal_log_entry_type_valid CHECK (
                entry_type IN ('PANA', 'TYPE', 'TIME_DIRECT', 'TIME_MULTI', 'DIRECT', 'JODI')
            )
        )
        """)
        
        # Step 4: Restore data
        print("📥 Restoring existing data...")
        cursor.execute("""
        INSERT INTO universal_log 
        (id, customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line, created_at)
        SELECT id, customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line, created_at
        FROM universal_log_backup
        """)
        
        # Step 5: Recreate indexes
        print("🔍 Recreating indexes...")
        cursor.execute("CREATE INDEX idx_universal_log_customer_date ON universal_log(customer_id, entry_date)")
        cursor.execute("CREATE INDEX idx_universal_log_bazar_date ON universal_log(bazar, entry_date)")
        cursor.execute("CREATE INDEX idx_universal_log_number ON universal_log(number)")
        cursor.execute("CREATE INDEX idx_universal_log_created_at ON universal_log(created_at)")
        cursor.execute("CREATE INDEX idx_universal_log_composite ON universal_log(customer_id, bazar, entry_date)")
        
        # Step 6: Drop backup table
        print("🧹 Cleaning up backup...")
        cursor.execute("DROP TABLE universal_log_backup")
        
        # Step 7: Test JODI insertion
        print("🧪 Testing JODI insertion...")
        cursor.execute("""
            INSERT INTO universal_log 
            (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
            VALUES (1, 'Test', '2025-07-27', 'T.O', 22, 500, 'JODI', 'test')
        """)
        
        # Clean up test entry
        cursor.execute("DELETE FROM universal_log WHERE entry_type = 'JODI' AND customer_name = 'Test'")
        
        conn.commit()
        print("✅ Database constraint updated successfully!")
        print("✅ JODI entry type now supported!")
        
    except Exception as e:
        print(f"❌ Database update failed: {e}")
        if conn:
            conn.rollback()
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_database_constraint()