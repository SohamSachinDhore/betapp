#!/usr/bin/env python3
"""
Apply commission_type field update to existing database
"""

import sqlite3
import os
import sys

def apply_commission_update():
    """Apply the commission_type field to customers table"""
    
    # Database path
    db_path = "./data/rickymama.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run 'python setup_database.py' first.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if commission_type column already exists
        cursor.execute("PRAGMA table_info(customers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'commission_type' in columns:
            print("✅ commission_type column already exists in customers table")
            return True
        
        print("🔄 Adding commission_type column to customers table...")
        
        # Read and execute the SQL file
        sql_file = "./src/database/add_commission_field.sql"
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Execute the SQL commands
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e):
                            print(f"⚠️  Column already exists, skipping...")
                        else:
                            raise
            
            conn.commit()
            print("✅ Successfully added commission_type field!")
        else:
            # If SQL file doesn't exist, execute directly
            print("⚠️  SQL file not found, executing directly...")
            try:
                cursor.execute("""
                    ALTER TABLE customers 
                    ADD COLUMN commission_type TEXT 
                    DEFAULT 'commission' 
                    CHECK (commission_type IN ('commission', 'non_commission'))
                """)
                cursor.execute("""
                    UPDATE customers 
                    SET commission_type = 'commission' 
                    WHERE commission_type IS NULL
                """)
                conn.commit()
                print("✅ Successfully added commission_type field!")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("✅ commission_type column already exists")
                else:
                    raise
        
        # Verify the update
        cursor.execute("PRAGMA table_info(customers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'commission_type' in columns:
            print("✅ Verified: commission_type column is now in customers table")
            
            # Show current customers with their commission types
            cursor.execute("SELECT id, name, commission_type FROM customers")
            customers = cursor.fetchall()
            
            if customers:
                print("\n📋 Current customers:")
                for customer in customers:
                    print(f"   - {customer[1]}: {customer[2]}")
            
            return True
        else:
            print("❌ Failed to add commission_type column")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 RickyMama Commission Type Update")
    print("=" * 50)
    
    success = apply_commission_update()
    
    if success:
        print("\n✅ Database update complete!")
        print("You can now run the application with commission type support.")
        sys.exit(0)
    else:
        print("\n❌ Database update failed!")
        sys.exit(1)