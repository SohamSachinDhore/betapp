#!/usr/bin/env python3
"""Reinitialize database with updated schema"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager

def main():
    print("🔄 Reinitializing database with updated schema...")
    
    # Initialize database with updated schema
    db_manager = DatabaseManager("./data/rickymama.db")
    db_manager.initialize_database()
    
    print("✅ Database reinitialized successfully!")
    
    # Verify the constraint is correct
    constraint_query = "SELECT sql FROM sqlite_master WHERE name='universal_log'"
    result = db_manager.execute_query(constraint_query)
    
    if result:
        schema = result[0]['sql']
        if 'DIRECT' in schema:
            print("✅ DIRECT entry type is included in constraint")
        else:
            print("❌ DIRECT entry type is missing from constraint")
        
        print(f"Schema: {schema}")
    
    # Check triggers
    triggers = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='trigger'")
    print(f"✅ Created {len(triggers)} triggers")
    
    return True

if __name__ == "__main__":
    main()